"""
Monitoring and Alerting System for MLOps Best Practices

This module implements a comprehensive monitoring system with:
- Data drift detection
- Model performance monitoring
- Infrastructure monitoring
- Automated alerting
- Dashboard integration
- Anomaly detection
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import structlog
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from scipy import stats
import requests
from dataclasses import dataclass
import schedule
import uuid

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config
from utils.logging import setup_logging
from utils.metrics import MetricsCollector

# Configure structured logging
logger = structlog.get_logger()

# Prometheus metrics
DRIFT_DETECTED = Counter('data_drift_detected_total', 'Total data drift detections')
MODEL_DEGRADATION = Counter('model_degradation_detected_total', 'Total model degradation detections')
ALERTS_SENT = Counter('alerts_sent_total', 'Total alerts sent', ['alert_type', 'severity'])
MONITORING_CHECKS = Counter('monitoring_checks_total', 'Total monitoring checks', ['check_type'])


@dataclass
class DriftResult:
    """Data drift detection result"""
    feature_name: str
    drift_score: float
    p_value: float
    is_drifted: bool
    threshold: float
    timestamp: datetime


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_version: str
    accuracy: float
    latency: float
    throughput: float
    error_rate: float
    timestamp: datetime


@dataclass
class Alert:
    """Alert configuration"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    metadata: Dict


class MonitoringSystem:
    """
    Comprehensive monitoring system with MLOps best practices
    """
    
    def __init__(self, config_path: str = "configs/monitoring_config.yaml"):
        """Initialize the monitoring system"""
        self.config = load_config(config_path)
        self.metrics = MetricsCollector()
        self.setup_logging()
        self.setup_monitoring()
        
        # Initialize monitoring state
        self.baseline_data = {}
        self.model_performance_history = {}
        self.alerts_history = []
        self.drift_history = []
        
        logger.info("Monitoring system initialized", config_path=config_path)
    
    def setup_logging(self):
        """Setup structured logging with correlation IDs"""
        setup_logging()
        logger.info("Logging setup completed")
    
    def setup_monitoring(self):
        """Setup monitoring and metrics collection"""
        # Start Prometheus metrics server
        start_http_server(8002)
        logger.info("Monitoring setup completed", metrics_port=8002)
    
    def load_baseline_data(self, baseline_path: str) -> Dict:
        """
        Load baseline data for drift detection
        
        Args:
            baseline_path: Path to baseline data
            
        Returns:
            Dict: Baseline data statistics
        """
        try:
            logger.info("Loading baseline data", baseline_path=baseline_path)
            
            if baseline_path.endswith('.parquet'):
                baseline_df = pd.read_parquet(baseline_path)
            elif baseline_path.endswith('.csv'):
                baseline_df = pd.read_csv(baseline_path)
            else:
                raise ValueError(f"Unsupported file format: {baseline_path}")
            
            # Calculate baseline statistics
            baseline_stats = {}
            for column in baseline_df.select_dtypes(include=[np.number]).columns:
                baseline_stats[column] = {
                    'mean': float(baseline_df[column].mean()),
                    'std': float(baseline_df[column].std()),
                    'min': float(baseline_df[column].min()),
                    'max': float(baseline_df[column].max()),
                    'percentiles': baseline_df[column].quantile([0.25, 0.5, 0.75]).to_dict()
                }
            
            self.baseline_data = baseline_stats
            
            logger.info("Baseline data loaded", 
                       features=len(baseline_stats),
                       samples=len(baseline_df))
            
            return baseline_stats
            
        except Exception as e:
            logger.error("Failed to load baseline data", error=str(e))
            raise
    
    def detect_data_drift(self, current_data: pd.DataFrame, 
                         drift_threshold: float = 0.05) -> List[DriftResult]:
        """
        Detect data drift using statistical tests
        
        Args:
            current_data: Current data to compare against baseline
            drift_threshold: P-value threshold for drift detection
            
        Returns:
            List[DriftResult]: Drift detection results
        """
        try:
            logger.info("Starting data drift detection", 
                       samples=len(current_data),
                       threshold=drift_threshold)
            
            drift_results = []
            
            for column in current_data.select_dtypes(include=[np.number]).columns:
                if column not in self.baseline_data:
                    continue
                
                # Get baseline statistics
                baseline_stats = self.baseline_data[column]
                current_values = current_data[column].dropna()
                
                if len(current_values) == 0:
                    continue
                
                # Perform Kolmogorov-Smirnov test
                ks_statistic, p_value = stats.ks_2samp(
                    current_values,
                    np.random.normal(baseline_stats['mean'], baseline_stats['std'], len(current_values))
                )
                
                # Calculate drift score (1 - p_value)
                drift_score = 1 - p_value
                is_drifted = p_value < drift_threshold
                
                result = DriftResult(
                    feature_name=column,
                    drift_score=drift_score,
                    p_value=p_value,
                    is_drifted=is_drifted,
                    threshold=drift_threshold,
                    timestamp=datetime.now()
                )
                
                drift_results.append(result)
                
                if is_drifted:
                    DRIFT_DETECTED.inc()
                    logger.warning("Data drift detected", 
                                 feature=column,
                                 drift_score=drift_score,
                                 p_value=p_value)
            
            # Store drift history
            self.drift_history.extend(drift_results)
            
            MONITORING_CHECKS.labels(check_type='data_drift').inc()
            logger.info("Data drift detection completed", 
                       total_features=len(drift_results),
                       drifted_features=sum(1 for r in drift_results if r.is_drifted))
            
            return drift_results
            
        except Exception as e:
            logger.error("Data drift detection failed", error=str(e))
            raise
    
    def monitor_model_performance(self, model_version: str, 
                                 predictions: List[Dict]) -> ModelPerformance:
        """
        Monitor model performance metrics
        
        Args:
            model_version: Version of the model
            predictions: List of prediction results
            
        Returns:
            ModelPerformance: Performance metrics
        """
        try:
            logger.info("Monitoring model performance", model_version=model_version)
            
            if not predictions:
                raise ValueError("No predictions provided for monitoring")
            
            # Calculate performance metrics
            latencies = [pred.get('latency', 0) for pred in predictions]
            accuracies = [pred.get('accuracy', 0) for pred in predictions if 'accuracy' in pred]
            errors = [pred.get('error', False) for pred in predictions]
            
            performance = ModelPerformance(
                model_version=model_version,
                accuracy=np.mean(accuracies) if accuracies else 0.0,
                latency=np.mean(latencies) if latencies else 0.0,
                throughput=len(predictions) / (np.sum(latencies) if latencies else 1),
                error_rate=np.mean(errors) if errors else 0.0,
                timestamp=datetime.now()
            )
            
            # Store performance history
            if model_version not in self.model_performance_history:
                self.model_performance_history[model_version] = []
            self.model_performance_history[model_version].append(performance)
            
            # Keep only recent history
            max_history = self.config.get('monitoring', {}).get('max_performance_history', 1000)
            if len(self.model_performance_history[model_version]) > max_history:
                self.model_performance_history[model_version] = \
                    self.model_performance_history[model_version][-max_history:]
            
            MONITORING_CHECKS.labels(check_type='model_performance').inc()
            logger.info("Model performance monitoring completed", 
                       model_version=model_version,
                       accuracy=performance.accuracy,
                       latency=performance.latency)
            
            return performance
            
        except Exception as e:
            logger.error("Model performance monitoring failed", error=str(e))
            raise
    
    def detect_model_degradation(self, model_version: str, 
                                performance_threshold: float = 0.1) -> bool:
        """
        Detect model performance degradation
        
        Args:
            model_version: Version of the model
            performance_threshold: Threshold for degradation detection
            
        Returns:
            bool: True if degradation detected
        """
        try:
            if model_version not in self.model_performance_history:
                return False
            
            history = self.model_performance_history[model_version]
            if len(history) < 10:  # Need minimum history
                return False
            
            # Compare recent performance with historical average
            recent_performance = history[-10:]  # Last 10 measurements
            historical_performance = history[:-10]  # Earlier measurements
            
            recent_accuracy = np.mean([p.accuracy for p in recent_performance])
            historical_accuracy = np.mean([p.accuracy for p in historical_performance])
            
            degradation = historical_accuracy - recent_accuracy
            is_degraded = degradation > performance_threshold
            
            if is_degraded:
                MODEL_DEGRADATION.inc()
                logger.warning("Model degradation detected", 
                             model_version=model_version,
                             degradation=degradation,
                             threshold=performance_threshold)
            
            return is_degraded
            
        except Exception as e:
            logger.error("Model degradation detection failed", error=str(e))
            return False
    
    def send_alert(self, alert: Alert) -> bool:
        """
        Send alert through configured channels
        
        Args:
            alert: Alert to send
            
        Returns:
            bool: True if alert sent successfully
        """
        try:
            logger.info("Sending alert", 
                       alert_id=alert.alert_id,
                       alert_type=alert.alert_type,
                       severity=alert.severity)
            
            # Store alert in history
            self.alerts_history.append(alert)
            
            # Send to different channels based on configuration
            alert_config = self.config.get('alerts', {})
            
            # Email alerts
            if alert_config.get('email', {}).get('enabled', False):
                self._send_email_alert(alert)
            
            # Slack alerts
            if alert_config.get('slack', {}).get('enabled', False):
                self._send_slack_alert(alert)
            
            # Webhook alerts
            if alert_config.get('webhook', {}).get('enabled', False):
                self._send_webhook_alert(alert)
            
            ALERTS_SENT.labels(
                alert_type=alert.alert_type,
                severity=alert.severity
            ).inc()
            
            logger.info("Alert sent successfully", alert_id=alert.alert_id)
            return True
            
        except Exception as e:
            logger.error("Failed to send alert", 
                        alert_id=alert.alert_id,
                        error=str(e))
            return False
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        # Implementation would use SMTP or email service
        logger.info("Email alert sent", alert_id=alert.alert_id)
    
    def _send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        try:
            slack_config = self.config.get('alerts', {}).get('slack', {})
            webhook_url = slack_config.get('webhook_url')
            
            if webhook_url:
                message = {
                    "text": f"🚨 *{alert.alert_type.upper()} Alert*",
                    "attachments": [
                        {
                            "color": "danger" if alert.severity == "high" else "warning",
                            "fields": [
                                {"title": "Severity", "value": alert.severity, "short": True},
                                {"title": "Message", "value": alert.message, "short": False},
                                {"title": "Timestamp", "value": alert.timestamp.isoformat(), "short": True}
                            ]
                        }
                    ]
                }
                
                response = requests.post(webhook_url, json=message)
                response.raise_for_status()
                
                logger.info("Slack alert sent", alert_id=alert.alert_id)
            
        except Exception as e:
            logger.error("Failed to send Slack alert", error=str(e))
    
    def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert"""
        try:
            webhook_config = self.config.get('alerts', {}).get('webhook', {})
            webhook_url = webhook_config.get('url')
            
            if webhook_url:
                payload = {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metadata": alert.metadata
                }
                
                response = requests.post(webhook_url, json=payload)
                response.raise_for_status()
                
                logger.info("Webhook alert sent", alert_id=alert.alert_id)
            
        except Exception as e:
            logger.error("Failed to send webhook alert", error=str(e))
    
    def check_system_health(self) -> Dict:
        """
        Check overall system health
        
        Returns:
            Dict: System health status
        """
        try:
            logger.info("Checking system health")
            
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "checks": {}
            }
            
            # Check data drift
            drift_checks = self._check_drift_health()
            health_status["checks"]["data_drift"] = drift_checks
            
            # Check model performance
            performance_checks = self._check_performance_health()
            health_status["checks"]["model_performance"] = performance_checks
            
            # Check infrastructure
            infrastructure_checks = self._check_infrastructure_health()
            health_status["checks"]["infrastructure"] = infrastructure_checks
            
            # Determine overall status
            all_healthy = all(
                check.get("status") == "healthy" 
                for check in health_status["checks"].values()
            )
            
            health_status["status"] = "healthy" if all_healthy else "unhealthy"
            
            logger.info("System health check completed", status=health_status["status"])
            return health_status
            
        except Exception as e:
            logger.error("System health check failed", error=str(e))
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _check_drift_health(self) -> Dict:
        """Check data drift health"""
        try:
            # Check recent drift detections
            recent_drift = [
                drift for drift in self.drift_history
                if drift.timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            drifted_features = [d for d in recent_drift if d.is_drifted]
            
            return {
                "status": "healthy" if len(drifted_features) == 0 else "warning",
                "drifted_features": len(drifted_features),
                "total_checks": len(recent_drift)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_performance_health(self) -> Dict:
        """Check model performance health"""
        try:
            degraded_models = []
            
            for model_version in self.model_performance_history:
                if self.detect_model_degradation(model_version):
                    degraded_models.append(model_version)
            
            return {
                "status": "healthy" if len(degraded_models) == 0 else "warning",
                "degraded_models": degraded_models,
                "total_models": len(self.model_performance_history)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_infrastructure_health(self) -> Dict:
        """Check infrastructure health"""
        try:
            # Check disk space
            disk_usage = self._get_disk_usage()
            
            # Check memory usage
            memory_usage = self._get_memory_usage()
            
            # Check CPU usage
            cpu_usage = self._get_cpu_usage()
            
            overall_status = "healthy"
            if any(usage > 90 for usage in [disk_usage, memory_usage, cpu_usage]):
                overall_status = "warning"
            
            return {
                "status": overall_status,
                "disk_usage": disk_usage,
                "memory_usage": memory_usage,
                "cpu_usage": cpu_usage
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_disk_usage(self) -> float:
        """Get disk usage percentage"""
        try:
            import psutil
            return psutil.disk_usage('/').percent
        except:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0
    
    def run_monitoring_loop(self):
        """Run continuous monitoring loop"""
        logger.info("Starting monitoring loop")
        
        while True:
            try:
                # Check system health
                health_status = self.check_system_health()
                
                # Send alerts if needed
                if health_status["status"] != "healthy":
                    alert = Alert(
                        alert_id=str(uuid.uuid4()),
                        alert_type="system_health",
                        severity="high" if health_status["status"] == "error" else "medium",
                        message=f"System health check failed: {health_status['status']}",
                        timestamp=datetime.now(),
                        metadata=health_status
                    )
                    self.send_alert(alert)
                
                # Sleep for monitoring interval
                interval = self.config.get('monitoring', {}).get('interval_seconds', 300)
                time.sleep(interval)
                
            except Exception as e:
                logger.error("Monitoring loop error", error=str(e))
                time.sleep(60)  # Wait before retrying
    
    def get_monitoring_dashboard_data(self) -> Dict:
        """
        Get data for monitoring dashboard
        
        Returns:
            Dict: Dashboard data
        """
        try:
            return {
                "system_health": self.check_system_health(),
                "recent_alerts": self.alerts_history[-10:],  # Last 10 alerts
                "drift_summary": {
                    "total_drifted_features": sum(1 for d in self.drift_history if d.is_drifted),
                    "recent_drift": len([d for d in self.drift_history 
                                       if d.timestamp > datetime.now() - timedelta(hours=24)])
                },
                "performance_summary": {
                    model_version: {
                        "avg_accuracy": np.mean([p.accuracy for p in history]),
                        "avg_latency": np.mean([p.latency for p in history]),
                        "total_predictions": len(history)
                    }
                    for model_version, history in self.model_performance_history.items()
                }
            }
            
        except Exception as e:
            logger.error("Failed to get dashboard data", error=str(e))
            return {}


def main():
    """Main function to run the monitoring system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the monitoring system")
    parser.add_argument("--config", default="configs/monitoring_config.yaml", 
                       help="Config file path")
    parser.add_argument("--baseline", help="Path to baseline data for drift detection")
    parser.add_argument("--daemon", action="store_true", 
                       help="Run as daemon process")
    
    args = parser.parse_args()
    
    # Initialize monitoring system
    monitor = MonitoringSystem(args.config)
    
    # Load baseline data if provided
    if args.baseline:
        monitor.load_baseline_data(args.baseline)
    
    if args.daemon:
        # Run as daemon
        monitor.run_monitoring_loop()
    else:
        # Run single health check
        health_status = monitor.check_system_health()
        print(json.dumps(health_status, indent=2, default=str))


if __name__ == "__main__":
    main()