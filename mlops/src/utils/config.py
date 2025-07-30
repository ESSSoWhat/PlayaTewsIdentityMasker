"""
Configuration Management for MLOps Best Practices

This module provides configuration management utilities with:
- YAML configuration loading
- Environment variable substitution
- Configuration validation
- Default value handling
- Configuration hot-reloading
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from pydantic import BaseModel, ValidationError
import structlog

logger = structlog.get_logger()


class ConfigValidator(BaseModel):
    """Base configuration validator"""
    class Config:
        extra = "allow"


def load_config(config_path: str, validate: bool = True) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution
    
    Args:
        config_path: Path to configuration file
        validate: Whether to validate configuration
        
    Returns:
        Dict: Configuration dictionary
    """
    try:
        # Resolve path
        config_path = Path(config_path).resolve()
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        logger.info("Loading configuration", config_path=str(config_path))
        
        # Read YAML file
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Substitute environment variables
        config_content = substitute_env_vars(config_content)
        
        # Parse YAML
        config = yaml.safe_load(config_content)
        
        if config is None:
            raise ValueError("Configuration file is empty or invalid")
        
        # Validate configuration if requested
        if validate:
            config = validate_config(config, config_path.name)
        
        logger.info("Configuration loaded successfully", 
                   config_path=str(config_path),
                   config_keys=list(config.keys()))
        
        return config
        
    except Exception as e:
        logger.error("Failed to load configuration", 
                    config_path=config_path,
                    error=str(e))
        raise


def substitute_env_vars(content: str) -> str:
    """
    Substitute environment variables in configuration content
    
    Args:
        content: Configuration content string
        
    Returns:
        str: Content with environment variables substituted
    """
    try:
        # Simple environment variable substitution
        # Format: ${VAR_NAME} or $VAR_NAME
        import re
        
        def replace_env_var(match):
            var_name = match.group(1) or match.group(2)
            if var_name in os.environ:
                return os.environ[var_name]
            else:
                logger.warning("Environment variable not found", variable=var_name)
                return match.group(0)  # Keep original if not found
        
        # Replace ${VAR_NAME} and $VAR_NAME patterns
        content = re.sub(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)', replace_env_var, content)
        
        return content
        
    except Exception as e:
        logger.error("Failed to substitute environment variables", error=str(e))
        return content


def validate_config(config: Dict[str, Any], config_type: str) -> Dict[str, Any]:
    """
    Validate configuration based on type
    
    Args:
        config: Configuration dictionary
        config_type: Type of configuration file
        
    Returns:
        Dict: Validated configuration
    """
    try:
        if config_type == "data_config.yaml":
            return validate_data_config(config)
        elif config_type == "model_config.yaml":
            return validate_model_config(config)
        elif config_type == "serving_config.yaml":
            return validate_serving_config(config)
        elif config_type == "monitoring_config.yaml":
            return validate_monitoring_config(config)
        else:
            logger.warning("Unknown configuration type, skipping validation", config_type=config_type)
            return config
            
    except Exception as e:
        logger.error("Configuration validation failed", 
                    config_type=config_type,
                    error=str(e))
        raise


def validate_data_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate data pipeline configuration"""
    required_keys = ["transformations"]
    
    for key in required_keys:
        if key not in config:
            config[key] = {}
    
    # Set defaults
    if "transformations" not in config:
        config["transformations"] = {
            "missing_values": {"strategy": "drop"},
            "dtype_conversions": {},
            "feature_engineering": {}
        }
    
    return config


def validate_model_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model training configuration"""
    required_keys = ["target_column", "mlflow", "default_params"]
    
    for key in required_keys:
        if key not in config:
            config[key] = {}
    
    # Set defaults
    if "target_column" not in config:
        config["target_column"] = "target"
    
    if "mlflow" not in config:
        config["mlflow"] = {
            "tracking_uri": "sqlite:///mlflow.db",
            "experiment_name": "mlops-experiment"
        }
    
    if "default_params" not in config:
        config["default_params"] = {
            "random_forest_classifier": {
                "n_estimators": 100,
                "random_state": 42
            },
            "logistic_regression": {
                "random_state": 42
            }
        }
    
    return config


def validate_serving_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model serving configuration"""
    required_keys = ["models_dir", "redis", "cors", "cache", "ab_tests"]
    
    for key in required_keys:
        if key not in config:
            config[key] = {}
    
    # Set defaults
    if "models_dir" not in config:
        config["models_dir"] = "models"
    
    if "redis" not in config:
        config["redis"] = {
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    
    if "cors" not in config:
        config["cors"] = {
            "allow_origins": ["*"]
        }
    
    if "cache" not in config:
        config["cache"] = {
            "ttl": 3600
        }
    
    if "ab_tests" not in config:
        config["ab_tests"] = {}
    
    return config


def validate_monitoring_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate monitoring configuration"""
    required_keys = ["monitoring", "alerts"]
    
    for key in required_keys:
        if key not in config:
            config[key] = {}
    
    # Set defaults
    if "monitoring" not in config:
        config["monitoring"] = {
            "interval_seconds": 300,
            "max_performance_history": 1000
        }
    
    if "alerts" not in config:
        config["alerts"] = {
            "email": {"enabled": False},
            "slack": {"enabled": False},
            "webhook": {"enabled": False}
        }
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path (e.g., "database.host")
        default: Default value if key not found
        
    Returns:
        Any: Configuration value
    """
    try:
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
        
    except Exception as e:
        logger.warning("Failed to get config value", 
                      key_path=key_path,
                      error=str(e))
        return default


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set configuration value using dot notation
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path
        value: Value to set
    """
    try:
        keys = key_path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
    except Exception as e:
        logger.error("Failed to set config value", 
                    key_path=key_path,
                    error=str(e))
        raise


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to YAML file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    try:
        config_path = Path(config_path).resolve()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        logger.info("Configuration saved", config_path=str(config_path))
        
    except Exception as e:
        logger.error("Failed to save configuration", 
                    config_path=config_path,
                    error=str(e))
        raise


def create_default_configs():
    """Create default configuration files"""
    configs = {
        "configs/data_config.yaml": {
            "transformations": {
                "missing_values": {
                    "strategy": "drop"
                },
                "dtype_conversions": {},
                "feature_engineering": {
                    "date_features": [],
                    "categorical_encoding": [],
                    "numerical_aggregations": {}
                }
            }
        },
        "configs/model_config.yaml": {
            "target_column": "target",
            "mlflow": {
                "tracking_uri": "sqlite:///mlflow.db",
                "experiment_name": "mlops-experiment"
            },
            "default_params": {
                "random_forest_classifier": {
                    "n_estimators": 100,
                    "random_state": 42
                },
                "logistic_regression": {
                    "random_state": 42
                }
            }
        },
        "configs/serving_config.yaml": {
            "models_dir": "models",
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "cors": {
                "allow_origins": ["*"]
            },
            "cache": {
                "ttl": 3600
            },
            "ab_tests": {}
        },
        "configs/monitoring_config.yaml": {
            "monitoring": {
                "interval_seconds": 300,
                "max_performance_history": 1000
            },
            "alerts": {
                "email": {
                    "enabled": False
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": ""
                },
                "webhook": {
                    "enabled": False,
                    "url": ""
                }
            }
        }
    }
    
    for config_path, config_data in configs.items():
        try:
            save_config(config_data, config_path)
            logger.info("Default configuration created", config_path=config_path)
        except Exception as e:
            logger.error("Failed to create default configuration", 
                        config_path=config_path,
                        error=str(e))


if __name__ == "__main__":
    # Create default configurations if run directly
    create_default_configs()