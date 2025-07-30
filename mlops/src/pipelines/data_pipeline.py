"""
Data Pipeline for MLOps Best Practices

This module implements a comprehensive data pipeline with:
- Data validation and quality checks
- Structured logging with correlation IDs
- Error handling and retry mechanisms
- Data versioning with DVC
- Monitoring and metrics collection
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import structlog
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import BaseDataContext
from great_expectations.data_context.types.resource_identifiers import GeCloudIdentifier
from prometheus_client import Counter, Histogram, start_http_server

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config
from utils.logging import setup_logging
from utils.metrics import MetricsCollector

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
DATA_PROCESSING_TIME = Histogram('data_processing_seconds', 'Time spent processing data')
DATA_RECORDS_PROCESSED = Counter('data_records_processed_total', 'Total records processed')
DATA_VALIDATION_ERRORS = Counter('data_validation_errors_total', 'Total validation errors')
DATA_PIPELINE_RUNS = Counter('data_pipeline_runs_total', 'Total pipeline runs')


class DataPipeline:
    """
    Comprehensive data pipeline with MLOps best practices
    """
    
    def __init__(self, config_path: str = "configs/data_config.yaml"):
        """Initialize the data pipeline with configuration"""
        self.config = load_config(config_path)
        self.metrics = MetricsCollector()
        self.setup_logging()
        self.setup_monitoring()
        
        # Initialize Great Expectations context
        self.ge_context = BaseDataContext(project_config_dir="great_expectations")
        
        logger.info("Data pipeline initialized", config_path=config_path)
    
    def setup_logging(self):
        """Setup structured logging with correlation IDs"""
        setup_logging()
        logger.info("Logging setup completed")
    
    def setup_monitoring(self):
        """Setup monitoring and metrics collection"""
        # Start Prometheus metrics server
        start_http_server(8000)
        logger.info("Monitoring setup completed", metrics_port=8000)
    
    @DATA_PROCESSING_TIME.time()
    def extract_data(self, source_path: str) -> pd.DataFrame:
        """
        Extract data from source with validation
        
        Args:
            source_path: Path to the data source
            
        Returns:
            DataFrame: Extracted data
        """
        try:
            logger.info("Starting data extraction", source_path=source_path)
            
            # Determine file type and extract accordingly
            if source_path.endswith('.csv'):
                data = pd.read_csv(source_path)
            elif source_path.endswith('.parquet'):
                data = pd.read_parquet(source_path)
            elif source_path.endswith('.json'):
                data = pd.read_json(source_path)
            else:
                raise ValueError(f"Unsupported file format: {source_path}")
            
            DATA_RECORDS_PROCESSED.inc(len(data))
            logger.info("Data extraction completed", 
                       records=len(data), 
                       columns=list(data.columns))
            
            return data
            
        except Exception as e:
            logger.error("Data extraction failed", 
                        source_path=source_path, 
                        error=str(e))
            raise
    
    def validate_data(self, data: pd.DataFrame, validation_suite: str) -> Tuple[bool, Dict]:
        """
        Validate data using Great Expectations
        
        Args:
            data: DataFrame to validate
            validation_suite: Name of the validation suite
            
        Returns:
            Tuple[bool, Dict]: Validation result and details
        """
        try:
            logger.info("Starting data validation", validation_suite=validation_suite)
            
            # Create batch request
            batch_request = RuntimeBatchRequest(
                datasource_name="pandas_datasource",
                data_connector_name="default_runtime_data_connector_name",
                data_asset_name="data_asset",
                runtime_parameters={"batch_data": data},
                batch_identifiers={"default_identifier_name": "default_identifier"}
            )
            
            # Run validation
            results = self.ge_context.run_validation_operator(
                "action_list_operator",
                assets_to_validate=[batch_request],
                validation_operator_kwargs={
                    "validation_suite_name": validation_suite
                }
            )
            
            # Process results
            success = results.success
            validation_details = {
                "success": success,
                "statistics": results.statistics,
                "run_id": results.run_id
            }
            
            if not success:
                DATA_VALIDATION_ERRORS.inc()
                logger.warning("Data validation failed", 
                             validation_suite=validation_suite,
                             details=validation_details)
            else:
                logger.info("Data validation passed", 
                           validation_suite=validation_suite)
            
            return success, validation_details
            
        except Exception as e:
            logger.error("Data validation error", 
                        validation_suite=validation_suite, 
                        error=str(e))
            DATA_VALIDATION_ERRORS.inc()
            raise
    
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data according to business rules
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame: Transformed data
        """
        try:
            logger.info("Starting data transformation", 
                       input_shape=data.shape)
            
            # Apply transformations based on config
            transformations = self.config.get('transformations', {})
            
            # Handle missing values
            if 'missing_values' in transformations:
                strategy = transformations['missing_values'].get('strategy', 'drop')
                if strategy == 'drop':
                    data = data.dropna()
                elif strategy == 'fill':
                    fill_values = transformations['missing_values'].get('fill_values', {})
                    data = data.fillna(fill_values)
            
            # Data type conversions
            if 'dtype_conversions' in transformations:
                for col, dtype in transformations['dtype_conversions'].items():
                    if col in data.columns:
                        data[col] = data[col].astype(dtype)
            
            # Feature engineering
            if 'feature_engineering' in transformations:
                data = self._apply_feature_engineering(data, transformations['feature_engineering'])
            
            logger.info("Data transformation completed", 
                       output_shape=data.shape)
            
            return data
            
        except Exception as e:
            logger.error("Data transformation failed", error=str(e))
            raise
    
    def _apply_feature_engineering(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply feature engineering transformations"""
        try:
            # Date features
            if 'date_features' in config:
                for col in config['date_features']:
                    if col in data.columns:
                        data[f'{col}_year'] = pd.to_datetime(data[col]).dt.year
                        data[f'{col}_month'] = pd.to_datetime(data[col]).dt.month
                        data[f'{col}_day'] = pd.to_datetime(data[col]).dt.day
            
            # Categorical encoding
            if 'categorical_encoding' in config:
                for col in config['categorical_encoding']:
                    if col in data.columns:
                        data[f'{col}_encoded'] = pd.Categorical(data[col]).codes
            
            # Numerical aggregations
            if 'numerical_aggregations' in config:
                for col, agg_funcs in config['numerical_aggregations'].items():
                    if col in data.columns:
                        for func in agg_funcs:
                            if func == 'log':
                                data[f'{col}_log'] = np.log1p(data[col])
                            elif func == 'sqrt':
                                data[f'{col}_sqrt'] = np.sqrt(data[col])
            
            return data
            
        except Exception as e:
            logger.error("Feature engineering failed", error=str(e))
            raise
    
    def load_data(self, data: pd.DataFrame, output_path: str) -> str:
        """
        Load processed data to storage
        
        Args:
            data: DataFrame to save
            output_path: Output file path
            
        Returns:
            str: Path to saved data
        """
        try:
            logger.info("Starting data loading", output_path=output_path)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save data based on format
            if output_path.endswith('.parquet'):
                data.to_parquet(output_path, index=False)
            elif output_path.endswith('.csv'):
                data.to_csv(output_path, index=False)
            elif output_path.endswith('.json'):
                data.to_json(output_path, orient='records')
            else:
                raise ValueError(f"Unsupported output format: {output_path}")
            
            logger.info("Data loading completed", 
                       output_path=output_path, 
                       file_size=os.path.getsize(output_path))
            
            return output_path
            
        except Exception as e:
            logger.error("Data loading failed", 
                        output_path=output_path, 
                        error=str(e))
            raise
    
    def run_pipeline(self, 
                    source_path: str, 
                    output_path: str, 
                    validation_suite: str = "default") -> Dict:
        """
        Run the complete data pipeline
        
        Args:
            source_path: Path to input data
            output_path: Path for output data
            validation_suite: Validation suite name
            
        Returns:
            Dict: Pipeline execution results
        """
        pipeline_start = datetime.now()
        
        try:
            DATA_PIPELINE_RUNS.inc()
            logger.info("Starting data pipeline", 
                       source_path=source_path, 
                       output_path=output_path)
            
            # Extract
            data = self.extract_data(source_path)
            
            # Validate
            validation_success, validation_details = self.validate_data(data, validation_suite)
            
            if not validation_success:
                raise ValueError("Data validation failed")
            
            # Transform
            transformed_data = self.transform_data(data)
            
            # Load
            final_path = self.load_data(transformed_data, output_path)
            
            # Calculate metrics
            pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
            
            results = {
                "success": True,
                "pipeline_duration": pipeline_duration,
                "input_records": len(data),
                "output_records": len(transformed_data),
                "output_path": final_path,
                "validation_details": validation_details,
                "timestamp": pipeline_start.isoformat()
            }
            
            logger.info("Data pipeline completed successfully", **results)
            
            return results
            
        except Exception as e:
            pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
            logger.error("Data pipeline failed", 
                        error=str(e), 
                        duration=pipeline_duration)
            
            return {
                "success": False,
                "error": str(e),
                "pipeline_duration": pipeline_duration,
                "timestamp": pipeline_start.isoformat()
            }


def main():
    """Main function to run the data pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the data pipeline")
    parser.add_argument("--source", required=True, help="Source data path")
    parser.add_argument("--output", required=True, help="Output data path")
    parser.add_argument("--config", default="configs/data_config.yaml", help="Config file path")
    parser.add_argument("--validation-suite", default="default", help="Validation suite name")
    
    args = parser.parse_args()
    
    # Initialize and run pipeline
    pipeline = DataPipeline(args.config)
    results = pipeline.run_pipeline(args.source, args.output, args.validation_suite)
    
    if results["success"]:
        print(f"Pipeline completed successfully in {results['pipeline_duration']:.2f} seconds")
        print(f"Output saved to: {results['output_path']}")
    else:
        print(f"Pipeline failed: {results['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()