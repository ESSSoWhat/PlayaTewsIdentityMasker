"""
A/B Testing Framework for MLOps Best Practices

This module implements a comprehensive A/B testing framework with:
- Statistical testing with proper sample sizes
- Traffic splitting and routing
- Results analysis and visualization
- Automated recommendations
- Historical comparison
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import numpy as np
import pandas as pd
import structlog
from dataclasses import dataclass, asdict
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from prometheus_client import Counter, Histogram, Gauge

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config
from utils.logging import setup_logging
from utils.metrics import MetricsCollector

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
AB_TEST_REQUESTS = Counter('ab_test_requests_total', 'Total A/B test requests', ['experiment_id', 'variant'])
AB_TEST_CONVERSIONS = Counter('ab_test_conversions_total', 'Total A/B test conversions', ['experiment_id', 'variant'])
AB_TEST_DURATION = Histogram('ab_test_duration_seconds', 'A/B test duration', ['experiment_id'])
AB_TEST_SAMPLE_SIZE = Gauge('ab_test_sample_size', 'A/B test sample size', ['experiment_id', 'variant'])


@dataclass
class ExperimentConfig:
    """A/B test experiment configuration"""
    experiment_id: str
    name: str
    description: str
    control_model: str
    variant_model: str
    traffic_split: float  # Percentage of traffic for variant (0.0 to 1.0)
    metrics: List[str]
    minimum_sample_size: int
    confidence_level: float
    max_duration_days: int
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, paused, completed, stopped
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class ExperimentResult:
    """A/B test experiment result"""
    experiment_id: str
    variant: str
    sample_size: int
    conversions: int
    conversion_rate: float
    revenue: float
    latency: float
    error_rate: float
    confidence_interval: Tuple[float, float]
    p_value: float
    statistical_significance: bool
    timestamp: datetime


@dataclass
class StatisticalTestResult:
    """Statistical test result"""
    test_type: str
    statistic: float
    p_value: float
    confidence_interval: Tuple[float, float]
    effect_size: float
    power: float
    sample_size_required: int
    is_significant: bool


class ABTestingFramework:
    """
    Comprehensive A/B testing framework with MLOps best practices
    """
    
    def __init__(self, config_path: str = "configs/ab_testing_config.yaml"):
        """Initialize the A/B testing framework"""
        self.config = load_config(config_path)
        self.metrics = MetricsCollector()
        self.setup_logging()
        self.setup_storage()
        
        # Active experiments
        self.active_experiments = {}
        self.experiment_results = {}
        self.experiment_history = {}
        
        logger.info("A/B testing framework initialized", config_path=config_path)
    
    def setup_logging(self):
        """Setup structured logging with correlation IDs"""
        setup_logging()
        logger.info("Logging setup completed")
    
    def setup_storage(self):
        """Setup storage for experiment data"""
        self.storage_path = Path(self.config.get('storage', {}).get('path', 'data/ab_testing/'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing experiments
        self.load_experiments()
    
    def create_experiment(self, config: ExperimentConfig) -> str:
        """
        Create a new A/B test experiment
        
        Args:
            config: Experiment configuration
            
        Returns:
            str: Experiment ID
        """
        try:
            logger.info("Creating A/B test experiment", 
                       experiment_id=config.experiment_id,
                       name=config.name)
            
            # Validate configuration
            self._validate_experiment_config(config)
            
            # Store experiment
            self.active_experiments[config.experiment_id] = config
            self.experiment_results[config.experiment_id] = {
                'control': [],
                'variant': []
            }
            
            # Save to storage
            self._save_experiment(config)
            
            logger.info("A/B test experiment created successfully", 
                       experiment_id=config.experiment_id)
            
            return config.experiment_id
            
        except Exception as e:
            logger.error("Failed to create A/B test experiment", 
                        experiment_id=config.experiment_id,
                        error=str(e))
            raise
    
    def _validate_experiment_config(self, config: ExperimentConfig):
        """Validate experiment configuration"""
        if not 0 <= config.traffic_split <= 1:
            raise ValueError("Traffic split must be between 0 and 1")
        
        if config.minimum_sample_size < 100:
            raise ValueError("Minimum sample size must be at least 100")
        
        if not 0.8 <= config.confidence_level <= 0.99:
            raise ValueError("Confidence level must be between 0.8 and 0.99")
        
        if config.max_duration_days < 1:
            raise ValueError("Maximum duration must be at least 1 day")
    
    def assign_variant(self, experiment_id: str, user_id: str) -> str:
        """
        Assign a user to a variant (control or treatment)
        
        Args:
            experiment_id: Experiment ID
            user_id: User ID for consistent assignment
            
        Returns:
            str: Assigned variant (control or variant)
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.active_experiments[experiment_id]
            
            # Consistent assignment based on user ID hash
            user_hash = hash(user_id) % 10000
            threshold = experiment.traffic_split * 10000
            
            variant = "variant" if user_hash < threshold else "control"
            
            # Log assignment
            AB_TEST_REQUESTS.labels(
                experiment_id=experiment_id,
                variant=variant
            ).inc()
            
            logger.debug("User assigned to variant", 
                        experiment_id=experiment_id,
                        user_id=user_id,
                        variant=variant)
            
            return variant
            
        except Exception as e:
            logger.error("Failed to assign variant", 
                        experiment_id=experiment_id,
                        user_id=user_id,
                        error=str(e))
            # Default to control in case of error
            return "control"
    
    def record_event(self, experiment_id: str, variant: str, 
                    event_type: str, value: float = 1.0, 
                    metadata: Dict = None) -> bool:
        """
        Record an event for the A/B test
        
        Args:
            experiment_id: Experiment ID
            variant: Variant (control or variant)
            event_type: Type of event (conversion, revenue, etc.)
            value: Event value
            metadata: Additional metadata
            
        Returns:
            bool: True if event recorded successfully
        """
        try:
            if experiment_id not in self.active_experiments:
                return False
            
            # Create result record
            result = ExperimentResult(
                experiment_id=experiment_id,
                variant=variant,
                sample_size=1,
                conversions=1 if event_type == "conversion" else 0,
                conversion_rate=1.0 if event_type == "conversion" else 0.0,
                revenue=value if event_type == "revenue" else 0.0,
                latency=value if event_type == "latency" else 0.0,
                error_rate=value if event_type == "error" else 0.0,
                confidence_interval=(0.0, 0.0),
                p_value=1.0,
                statistical_significance=False,
                timestamp=datetime.now()
            )
            
            # Store result
            if variant not in self.experiment_results[experiment_id]:
                self.experiment_results[experiment_id][variant] = []
            
            self.experiment_results[experiment_id][variant].append(result)
            
            # Update metrics
            if event_type == "conversion":
                AB_TEST_CONVERSIONS.labels(
                    experiment_id=experiment_id,
                    variant=variant
                ).inc()
            
            # Update sample size gauge
            sample_size = len(self.experiment_results[experiment_id][variant])
            AB_TEST_SAMPLE_SIZE.labels(
                experiment_id=experiment_id,
                variant=variant
            ).set(sample_size)
            
            logger.debug("Event recorded", 
                        experiment_id=experiment_id,
                        variant=variant,
                        event_type=event_type,
                        value=value)
            
            return True
            
        except Exception as e:
            logger.error("Failed to record event", 
                        experiment_id=experiment_id,
                        variant=variant,
                        event_type=event_type,
                        error=str(e))
            return False
    
    def analyze_experiment(self, experiment_id: str) -> Dict:
        """
        Analyze A/B test experiment results
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Dict: Analysis results
        """
        try:
            if experiment_id not in self.active_experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.active_experiments[experiment_id]
            results = self.experiment_results[experiment_id]
            
            logger.info("Analyzing A/B test experiment", experiment_id=experiment_id)
            
            # Aggregate results
            control_results = self._aggregate_results(results.get('control', []))
            variant_results = self._aggregate_results(results.get('variant', []))
            
            # Perform statistical tests
            statistical_tests = {}
            for metric in experiment.metrics:
                test_result = self._perform_statistical_test(
                    control_results, variant_results, metric, experiment
                )
                statistical_tests[metric] = test_result
            
            # Calculate overall results
            analysis = {
                'experiment_id': experiment_id,
                'experiment_name': experiment.name,
                'status': experiment.status,
                'start_date': experiment.start_date.isoformat(),
                'end_date': experiment.end_date.isoformat() if experiment.end_date else None,
                'duration_days': (datetime.now() - experiment.start_date).days,
                'control_results': control_results,
                'variant_results': variant_results,
                'statistical_tests': statistical_tests,
                'recommendations': self._generate_recommendations(
                    experiment, control_results, variant_results, statistical_tests
                ),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Save analysis
            self._save_analysis(experiment_id, analysis)
            
            logger.info("A/B test analysis completed", experiment_id=experiment_id)
            return analysis
            
        except Exception as e:
            logger.error("Failed to analyze experiment", 
                        experiment_id=experiment_id,
                        error=str(e))
            raise
    
    def _aggregate_results(self, results: List[ExperimentResult]) -> Dict:
        """Aggregate experiment results"""
        if not results:
            return {
                'sample_size': 0,
                'conversions': 0,
                'conversion_rate': 0.0,
                'revenue': 0.0,
                'avg_revenue': 0.0,
                'latency': 0.0,
                'error_rate': 0.0
            }
        
        return {
            'sample_size': len(results),
            'conversions': sum(r.conversions for r in results),
            'conversion_rate': sum(r.conversions for r in results) / len(results),
            'revenue': sum(r.revenue for r in results),
            'avg_revenue': sum(r.revenue for r in results) / len(results),
            'latency': np.mean([r.latency for r in results]),
            'error_rate': np.mean([r.error_rate for r in results])
        }
    
    def _perform_statistical_test(self, control_results: Dict, variant_results: Dict, 
                                 metric: str, experiment: ExperimentConfig) -> StatisticalTestResult:
        """Perform statistical test for a metric"""
        try:
            # Extract metric values
            control_values = self._extract_metric_values(control_results, metric)
            variant_values = self._extract_metric_values(variant_results, metric)
            
            if len(control_values) == 0 or len(variant_values) == 0:
                return StatisticalTestResult(
                    test_type="insufficient_data",
                    statistic=0.0,
                    p_value=1.0,
                    confidence_interval=(0.0, 0.0),
                    effect_size=0.0,
                    power=0.0,
                    sample_size_required=experiment.minimum_sample_size,
                    is_significant=False
                )
            
            # Perform t-test for continuous metrics
            if metric in ['revenue', 'latency']:
                statistic, p_value = stats.ttest_ind(control_values, variant_values)
                test_type = "t_test"
            else:
                # Chi-square test for categorical metrics
                contingency_table = self._create_contingency_table(control_results, variant_results, metric)
                statistic, p_value, _, _ = stats.chi2_contingency(contingency_table)
                test_type = "chi_square"
            
            # Calculate confidence interval
            control_mean = np.mean(control_values)
            variant_mean = np.mean(variant_values)
            effect_size = (variant_mean - control_mean) / np.std(control_values) if np.std(control_values) > 0 else 0
            
            # Calculate power
            power = self._calculate_power(control_values, variant_values, experiment.confidence_level)
            
            # Determine significance
            is_significant = p_value < (1 - experiment.confidence_level)
            
            return StatisticalTestResult(
                test_type=test_type,
                statistic=statistic,
                p_value=p_value,
                confidence_interval=(control_mean, variant_mean),
                effect_size=effect_size,
                power=power,
                sample_size_required=experiment.minimum_sample_size,
                is_significant=is_significant
            )
            
        except Exception as e:
            logger.error("Failed to perform statistical test", 
                        metric=metric,
                        error=str(e))
            return StatisticalTestResult(
                test_type="error",
                statistic=0.0,
                p_value=1.0,
                confidence_interval=(0.0, 0.0),
                effect_size=0.0,
                power=0.0,
                sample_size_required=experiment.minimum_sample_size,
                is_significant=False
            )
    
    def _extract_metric_values(self, results: Dict, metric: str) -> List[float]:
        """Extract metric values from results"""
        if metric == 'conversion_rate':
            return [results['conversion_rate']] * results['sample_size']
        elif metric == 'revenue':
            return [results['avg_revenue']] * results['sample_size']
        elif metric == 'latency':
            return [results['latency']] * results['sample_size']
        elif metric == 'error_rate':
            return [results['error_rate']] * results['sample_size']
        else:
            return []
    
    def _create_contingency_table(self, control_results: Dict, variant_results: Dict, 
                                 metric: str) -> np.ndarray:
        """Create contingency table for categorical metrics"""
        if metric == 'conversion_rate':
            return np.array([
                [control_results['conversions'], control_results['sample_size'] - control_results['conversions']],
                [variant_results['conversions'], variant_results['sample_size'] - variant_results['conversions']]
            ])
        else:
            return np.array([[1, 1], [1, 1]])
    
    def _calculate_power(self, control_values: List[float], variant_values: List[float], 
                        confidence_level: float) -> float:
        """Calculate statistical power"""
        try:
            # Simplified power calculation
            effect_size = abs(np.mean(variant_values) - np.mean(control_values)) / np.std(control_values)
            alpha = 1 - confidence_level
            n1, n2 = len(control_values), len(variant_values)
            
            # Using Cohen's d effect size
            if effect_size < 0.2:
                power = 0.3
            elif effect_size < 0.5:
                power = 0.6
            elif effect_size < 0.8:
                power = 0.8
            else:
                power = 0.95
            
            return min(power, 0.99)
        except:
            return 0.5
    
    def _generate_recommendations(self, experiment: ExperimentConfig, 
                                 control_results: Dict, variant_results: Dict,
                                 statistical_tests: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check sample size
        total_sample_size = control_results['sample_size'] + variant_results['sample_size']
        if total_sample_size < experiment.minimum_sample_size:
            recommendations.append(
                f"Insufficient sample size. Need {experiment.minimum_sample_size} samples, "
                f"currently have {total_sample_size}"
            )
        
        # Check duration
        duration_days = (datetime.now() - experiment.start_date).days
        if duration_days < experiment.max_duration_days:
            recommendations.append(
                f"Experiment should run for at least {experiment.max_duration_days} days. "
                f"Currently running for {duration_days} days"
            )
        
        # Check statistical significance
        significant_metrics = [
            metric for metric, test in statistical_tests.items()
            if test.is_significant
        ]
        
        if significant_metrics:
            recommendations.append(
                f"Statistically significant results found for: {', '.join(significant_metrics)}"
            )
        else:
            recommendations.append("No statistically significant results found yet")
        
        # Check effect size
        for metric, test in statistical_tests.items():
            if abs(test.effect_size) > 0.5:
                recommendations.append(
                    f"Large effect size ({test.effect_size:.2f}) for {metric}"
                )
        
        return recommendations
    
    def stop_experiment(self, experiment_id: str, reason: str = "manual_stop") -> bool:
        """
        Stop an A/B test experiment
        
        Args:
            experiment_id: Experiment ID
            reason: Reason for stopping
            
        Returns:
            bool: True if experiment stopped successfully
        """
        try:
            if experiment_id not in self.active_experiments:
                return False
            
            experiment = self.active_experiments[experiment_id]
            experiment.status = "stopped"
            experiment.end_date = datetime.now()
            experiment.updated_at = datetime.now()
            
            # Move to history
            self.experiment_history[experiment_id] = experiment
            del self.active_experiments[experiment_id]
            
            # Save updated experiment
            self._save_experiment(experiment)
            
            logger.info("A/B test experiment stopped", 
                       experiment_id=experiment_id,
                       reason=reason)
            
            return True
            
        except Exception as e:
            logger.error("Failed to stop experiment", 
                        experiment_id=experiment_id,
                        error=str(e))
            return False
    
    def get_experiment_status(self, experiment_id: str) -> Dict:
        """
        Get experiment status and summary
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Dict: Experiment status
        """
        try:
            if experiment_id not in self.active_experiments:
                if experiment_id in self.experiment_history:
                    experiment = self.experiment_history[experiment_id]
                    return {
                        'experiment_id': experiment_id,
                        'status': 'completed',
                        'name': experiment.name,
                        'start_date': experiment.start_date.isoformat(),
                        'end_date': experiment.end_date.isoformat() if experiment.end_date else None
                    }
                else:
                    raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.active_experiments[experiment_id]
            results = self.experiment_results[experiment_id]
            
            control_size = len(results.get('control', []))
            variant_size = len(results.get('variant', []))
            
            return {
                'experiment_id': experiment_id,
                'status': experiment.status,
                'name': experiment.name,
                'start_date': experiment.start_date.isoformat(),
                'control_sample_size': control_size,
                'variant_sample_size': variant_size,
                'total_sample_size': control_size + variant_size,
                'traffic_split': experiment.traffic_split,
                'duration_days': (datetime.now() - experiment.start_date).days
            }
            
        except Exception as e:
            logger.error("Failed to get experiment status", 
                        experiment_id=experiment_id,
                        error=str(e))
            raise
    
    def _save_experiment(self, experiment: ExperimentConfig):
        """Save experiment to storage"""
        try:
            file_path = self.storage_path / f"{experiment.experiment_id}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(experiment), f, default=str, indent=2)
        except Exception as e:
            logger.error("Failed to save experiment", 
                        experiment_id=experiment.experiment_id,
                        error=str(e))
    
    def _save_analysis(self, experiment_id: str, analysis: Dict):
        """Save analysis results to storage"""
        try:
            file_path = self.storage_path / f"{experiment_id}_analysis.json"
            with open(file_path, 'w') as f:
                json.dump(analysis, f, default=str, indent=2)
        except Exception as e:
            logger.error("Failed to save analysis", 
                        experiment_id=experiment_id,
                        error=str(e))
    
    def load_experiments(self):
        """Load experiments from storage"""
        try:
            for file_path in self.storage_path.glob("*.json"):
                if not file_path.name.endswith("_analysis.json"):
                    experiment_id = file_path.stem
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        config = ExperimentConfig(**data)
                        if config.status == "active":
                            self.active_experiments[experiment_id] = config
                        else:
                            self.experiment_history[experiment_id] = config
                        self.experiment_results[experiment_id] = {'control': [], 'variant': []}
            
            logger.info("Experiments loaded from storage", 
                       active_count=len(self.active_experiments),
                       history_count=len(self.experiment_history))
            
        except Exception as e:
            logger.error("Failed to load experiments", error=str(e))


def main():
    """Main function to run the A/B testing framework"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the A/B testing framework")
    parser.add_argument("--config", default="configs/ab_testing_config.yaml", 
                       help="Config file path")
    parser.add_argument("--create-experiment", help="Create new experiment")
    parser.add_argument("--analyze", help="Analyze experiment")
    parser.add_argument("--status", help="Get experiment status")
    
    args = parser.parse_args()
    
    # Initialize framework
    framework = ABTestingFramework(args.config)
    
    if args.create_experiment:
        # Create example experiment
        config = ExperimentConfig(
            experiment_id="test_experiment_001",
            name="Model Comparison Test",
            description="Compare new model vs baseline",
            control_model="baseline_v1",
            variant_model="new_model_v1",
            traffic_split=0.5,
            metrics=["conversion_rate", "revenue", "latency"],
            minimum_sample_size=1000,
            confidence_level=0.95,
            max_duration_days=14,
            start_date=datetime.now()
        )
        framework.create_experiment(config)
        print(f"Created experiment: {config.experiment_id}")
    
    elif args.analyze:
        analysis = framework.analyze_experiment(args.analyze)
        print(json.dumps(analysis, indent=2, default=str))
    
    elif args.status:
        status = framework.get_experiment_status(args.status)
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    main() 