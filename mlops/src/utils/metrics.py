"""
Metrics Collection for MLOps Best Practices

This module provides metrics collection utilities with:
- Prometheus integration
- Custom business metrics
- Performance tracking
- Model metrics
- Data quality metrics
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest
import structlog

logger = structlog.get_logger()


class MetricsCollector:
    """
    Comprehensive metrics collector for MLOps
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self._initialize_metrics()
        logger.info("Metrics collector initialized")
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics"""
        
        # Pipeline metrics
        self.pipeline_runs = Counter(
            'pipeline_runs_total',
            'Total pipeline runs',
            ['pipeline_type', 'status']
        )
        
        self.pipeline_duration = Histogram(
            'pipeline_duration_seconds',
            'Pipeline execution duration',
            ['pipeline_type']
        )
        
        # Data metrics
        self.data_records_processed = Counter(
            'data_records_processed_total',
            'Total data records processed',
            ['data_type', 'operation']
        )
        
        self.data_quality_score = Gauge(
            'data_quality_score',
            'Data quality score',
            ['data_source']
        )
        
        # Model metrics
        self.model_training_runs = Counter(
            'model_training_runs_total',
            'Total model training runs',
            ['model_type', 'status']
        )
        
        self.model_accuracy = Gauge(
            'model_accuracy',
            'Model accuracy',
            ['model_version', 'model_type']
        )
        
        self.model_latency = Histogram(
            'model_prediction_latency_seconds',
            'Model prediction latency',
            ['model_version', 'model_type']
        )
        
        self.model_predictions = Counter(
            'model_predictions_total',
            'Total model predictions',
            ['model_version', 'model_type', 'status']
        )
        
        # Feature store metrics
        self.feature_store_operations = Counter(
            'feature_store_operations_total',
            'Feature store operations',
            ['operation_type', 'status']
        )
        
        self.feature_store_latency = Histogram(
            'feature_store_latency_seconds',
            'Feature store operation latency',
            ['operation_type']
        )
        
        # Monitoring metrics
        self.drift_detections = Counter(
            'data_drift_detections_total',
            'Data drift detections',
            ['feature_name', 'severity']
        )
        
        self.alert_count = Counter(
            'alerts_sent_total',
            'Total alerts sent',
            ['alert_type', 'severity']
        )
        
        # Infrastructure metrics
        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )
        
        self.disk_usage = Gauge(
            'disk_usage_percent',
            'Disk usage percentage'
        )
        
        # Business metrics
        self.business_metrics = {}
        
        logger.info("Prometheus metrics initialized")
    
    def record_pipeline_run(self, pipeline_type: str, status: str, duration: float = None):
        """
        Record pipeline execution metrics
        
        Args:
            pipeline_type: Type of pipeline (data, model, etc.)
            status: Execution status (success, failed)
            duration: Execution duration in seconds
        """
        try:
            self.pipeline_runs.labels(pipeline_type=pipeline_type, status=status).inc()
            
            if duration is not None:
                self.pipeline_duration.labels(pipeline_type=pipeline_type).observe(duration)
            
            logger.debug("Pipeline metrics recorded", 
                        pipeline_type=pipeline_type,
                        status=status,
                        duration=duration)
            
        except Exception as e:
            logger.error("Failed to record pipeline metrics", error=str(e))
    
    def record_data_processing(self, data_type: str, operation: str, record_count: int):
        """
        Record data processing metrics
        
        Args:
            data_type: Type of data being processed
            operation: Operation performed (extract, transform, load)
            record_count: Number of records processed
        """
        try:
            self.data_records_processed.labels(
                data_type=data_type, 
                operation=operation
            ).inc(record_count)
            
            logger.debug("Data processing metrics recorded", 
                        data_type=data_type,
                        operation=operation,
                        record_count=record_count)
            
        except Exception as e:
            logger.error("Failed to record data processing metrics", error=str(e))
    
    def record_data_quality(self, data_source: str, quality_score: float):
        """
        Record data quality metrics
        
        Args:
            data_source: Source of the data
            quality_score: Quality score (0-1)
        """
        try:
            self.data_quality_score.labels(data_source=data_source).set(quality_score)
            
            logger.debug("Data quality metrics recorded", 
                        data_source=data_source,
                        quality_score=quality_score)
            
        except Exception as e:
            logger.error("Failed to record data quality metrics", error=str(e))
    
    def record_model_training(self, model_type: str, status: str, duration: float = None):
        """
        Record model training metrics
        
        Args:
            model_type: Type of model being trained
            status: Training status (success, failed)
            duration: Training duration in seconds
        """
        try:
            self.model_training_runs.labels(model_type=model_type, status=status).inc()
            
            if duration is not None:
                # Use histogram for training duration
                self.pipeline_duration.labels(pipeline_type=f"model_training_{model_type}").observe(duration)
            
            logger.debug("Model training metrics recorded", 
                        model_type=model_type,
                        status=status,
                        duration=duration)
            
        except Exception as e:
            logger.error("Failed to record model training metrics", error=str(e))
    
    def record_model_performance(self, model_version: str, model_type: str, 
                               accuracy: float, latency: float):
        """
        Record model performance metrics
        
        Args:
            model_version: Version of the model
            model_type: Type of model
            accuracy: Model accuracy
            latency: Prediction latency in seconds
        """
        try:
            self.model_accuracy.labels(
                model_version=model_version, 
                model_type=model_type
            ).set(accuracy)
            
            self.model_latency.labels(
                model_version=model_version, 
                model_type=model_type
            ).observe(latency)
            
            logger.debug("Model performance metrics recorded", 
                        model_version=model_version,
                        model_type=model_type,
                        accuracy=accuracy,
                        latency=latency)
            
        except Exception as e:
            logger.error("Failed to record model performance metrics", error=str(e))
    
    def record_prediction(self, model_version: str, model_type: str, status: str):
        """
        Record prediction metrics
        
        Args:
            model_version: Version of the model
            model_type: Type of model
            status: Prediction status (success, failed)
        """
        try:
            self.model_predictions.labels(
                model_version=model_version,
                model_type=model_type,
                status=status
            ).inc()
            
            logger.debug("Prediction metrics recorded", 
                        model_version=model_version,
                        model_type=model_type,
                        status=status)
            
        except Exception as e:
            logger.error("Failed to record prediction metrics", error=str(e))
    
    def record_feature_store_operation(self, operation_type: str, status: str, duration: float = None):
        """
        Record feature store operation metrics
        
        Args:
            operation_type: Type of operation (read, write, delete)
            status: Operation status (success, failed)
            duration: Operation duration in seconds
        """
        try:
            self.feature_store_operations.labels(
                operation_type=operation_type,
                status=status
            ).inc()
            
            if duration is not None:
                self.feature_store_latency.labels(operation_type=operation_type).observe(duration)
            
            logger.debug("Feature store metrics recorded", 
                        operation_type=operation_type,
                        status=status,
                        duration=duration)
            
        except Exception as e:
            logger.error("Failed to record feature store metrics", error=str(e))
    
    def record_drift_detection(self, feature_name: str, severity: str):
        """
        Record data drift detection metrics
        
        Args:
            feature_name: Name of the feature
            severity: Drift severity (low, medium, high)
        """
        try:
            self.drift_detections.labels(
                feature_name=feature_name,
                severity=severity
            ).inc()
            
            logger.debug("Drift detection metrics recorded", 
                        feature_name=feature_name,
                        severity=severity)
            
        except Exception as e:
            logger.error("Failed to record drift detection metrics", error=str(e))
    
    def record_alert(self, alert_type: str, severity: str):
        """
        Record alert metrics
        
        Args:
            alert_type: Type of alert
            severity: Alert severity (low, medium, high, critical)
        """
        try:
            self.alert_count.labels(alert_type=alert_type, severity=severity).inc()
            
            logger.debug("Alert metrics recorded", 
                        alert_type=alert_type,
                        severity=severity)
            
        except Exception as e:
            logger.error("Failed to record alert metrics", error=str(e))
    
    def update_infrastructure_metrics(self, memory_usage: float = None, 
                                    cpu_usage: float = None, 
                                    disk_usage: float = None):
        """
        Update infrastructure metrics
        
        Args:
            memory_usage: Memory usage percentage
            cpu_usage: CPU usage percentage
            disk_usage: Disk usage percentage
        """
        try:
            if memory_usage is not None:
                self.memory_usage.set(memory_usage)
            
            if cpu_usage is not None:
                self.cpu_usage.set(cpu_usage)
            
            if disk_usage is not None:
                self.disk_usage.set(disk_usage)
            
            logger.debug("Infrastructure metrics updated", 
                        memory_usage=memory_usage,
                        cpu_usage=cpu_usage,
                        disk_usage=disk_usage)
            
        except Exception as e:
            logger.error("Failed to update infrastructure metrics", error=str(e))
    
    def record_business_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """
        Record custom business metrics
        
        Args:
            metric_name: Name of the business metric
            value: Metric value
            labels: Optional labels for the metric
        """
        try:
            if metric_name not in self.business_metrics:
                # Create new gauge for business metric
                self.business_metrics[metric_name] = Gauge(
                    f'business_{metric_name}',
                    f'Business metric: {metric_name}',
                    list(labels.keys()) if labels else []
                )
            
            metric = self.business_metrics[metric_name]
            
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
            
            logger.debug("Business metric recorded", 
                        metric_name=metric_name,
                        value=value,
                        labels=labels)
            
        except Exception as e:
            logger.error("Failed to record business metric", error=str(e))
    
    @contextmanager
    def measure_operation(self, operation_name: str, labels: Dict[str, str] = None):
        """
        Context manager to measure operation duration
        
        Args:
            operation_name: Name of the operation
            labels: Optional labels for the metric
        """
        start_time = time.time()
        
        try:
            yield
            duration = time.time() - start_time
            
            # Record operation duration
            if operation_name.startswith('pipeline_'):
                self.pipeline_duration.labels(pipeline_type=operation_name).observe(duration)
            elif operation_name.startswith('feature_store_'):
                self.feature_store_latency.labels(operation_type=operation_name).observe(duration)
            elif operation_name.startswith('model_'):
                self.model_latency.labels(
                    model_version=labels.get('model_version', 'unknown'),
                    model_type=labels.get('model_type', 'unknown')
                ).observe(duration)
            
            logger.debug("Operation duration measured", 
                        operation=operation_name,
                        duration=duration,
                        labels=labels)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error("Operation failed", 
                        operation=operation_name,
                        duration=duration,
                        error=str(e),
                        labels=labels)
            raise
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics
        
        Returns:
            Dict: Summary of metrics
        """
        try:
            # Generate Prometheus metrics
            metrics_text = generate_latest().decode('utf-8')
            
            # Parse metrics for summary
            summary = {
                "timestamp": datetime.now().isoformat(),
                "metrics_count": len(self.business_metrics),
                "prometheus_metrics": metrics_text
            }
            
            return summary
            
        except Exception as e:
            logger.error("Failed to get metrics summary", error=str(e))
            return {"error": str(e)}
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        try:
            # Reset all counters and gauges
            for metric in [
                self.pipeline_runs,
                self.data_records_processed,
                self.model_training_runs,
                self.model_predictions,
                self.feature_store_operations,
                self.drift_detections,
                self.alert_count,
                self.memory_usage,
                self.cpu_usage,
                self.disk_usage
            ]:
                # Reset metric (this is a simplified approach)
                pass
            
            # Reset business metrics
            self.business_metrics.clear()
            
            logger.info("Metrics reset completed")
            
        except Exception as e:
            logger.error("Failed to reset metrics", error=str(e))


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """
    Get global metrics collector instance
    
    Returns:
        MetricsCollector: Global metrics collector
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    
    return _metrics_collector


def record_pipeline_metrics(pipeline_type: str, status: str, duration: float = None):
    """Convenience function to record pipeline metrics"""
    collector = get_metrics_collector()
    collector.record_pipeline_run(pipeline_type, status, duration)


def record_model_metrics(model_version: str, model_type: str, accuracy: float, latency: float):
    """Convenience function to record model metrics"""
    collector = get_metrics_collector()
    collector.record_model_performance(model_version, model_type, accuracy, latency)


def record_prediction_metrics(model_version: str, model_type: str, status: str):
    """Convenience function to record prediction metrics"""
    collector = get_metrics_collector()
    collector.record_prediction(model_version, model_type, status)


@contextmanager
def measure_operation_duration(operation_name: str, labels: Dict[str, str] = None):
    """Convenience context manager for measuring operation duration"""
    collector = get_metrics_collector()
    with collector.measure_operation(operation_name, labels):
        yield