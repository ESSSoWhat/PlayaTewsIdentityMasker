#!/usr/bin/env python3
"""
MLOps Setup Script

This script sets up a complete MLOps environment with:
- Directory structure creation
- Configuration file generation
- Dependencies installation
- DVC initialization
- MLflow setup
- Docker environment preparation
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import yaml
import json

def run_command(command, description, check=True):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def create_directory_structure():
    """Create the MLOps directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        "data/raw",
        "data/processed",
        "data/features",
        "models",
        "logs",
        "notebooks",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        "tests/api",
        "tests/performance",
        "configs",
        "scripts",
        "scripts/ci",
        "monitoring",
        "monitoring/grafana/dashboards",
        "monitoring/grafana/datasources",
        "docker",
        "k8s/staging",
        "k8s/production",
        "docs",
        "dags",
        "plugins"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {directory}")

def create_config_files():
    """Create default configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Data configuration
    data_config = {
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
        },
        "validation": {
            "enabled": True,
            "suites": ["default"]
        }
    }
    
    # Model configuration
    model_config = {
        "target_column": "target",
        "mlflow": {
            "tracking_uri": "sqlite:///mlflow.db",
            "experiment_name": "mlops-experiment",
            "registry_uri": "sqlite:///mlflow.db"
        },
        "default_params": {
            "random_forest_classifier": {
                "n_estimators": 100,
                "random_state": 42
            },
            "logistic_regression": {
                "random_state": 42
            }
        },
        "hyperparameter_optimization": {
            "enabled": True,
            "n_trials": 100,
            "timeout": 3600
        }
    }
    
    # Serving configuration
    serving_config = {
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
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 100
        },
        "ab_tests": {}
    }
    
    # Monitoring configuration
    monitoring_config = {
        "monitoring": {
            "interval_seconds": 300,
            "max_performance_history": 1000,
            "drift_threshold": 0.05
        },
        "alerts": {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": ""
            },
            "slack": {
                "enabled": False,
                "webhook_url": ""
            },
            "webhook": {
                "enabled": False,
                "url": ""
            }
        },
        "prometheus": {
            "enabled": True,
            "port": 8002
        }
    }
    
    configs = {
        "configs/data_config.yaml": data_config,
        "configs/model_config.yaml": model_config,
        "configs/serving_config.yaml": serving_config,
        "configs/monitoring_config.yaml": monitoring_config
    }
    
    for config_path, config_data in configs.items():
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
        print(f"  ✅ Created {config_path}")

def create_prometheus_config():
    """Create Prometheus configuration"""
    print("📊 Creating Prometheus configuration...")
    
    prometheus_config = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s"
        },
        "rule_files": [],
        "scrape_configs": [
            {
                "job_name": "prometheus",
                "static_configs": [
                    {
                        "targets": ["localhost:9090"]
                    }
                ]
            },
            {
                "job_name": "model-server",
                "static_configs": [
                    {
                        "targets": ["model-server:8001"]
                    }
                ]
            },
            {
                "job_name": "monitoring",
                "static_configs": [
                    {
                        "targets": ["monitoring:8002"]
                    }
                ]
            }
        ]
    }
    
    with open("monitoring/prometheus.yml", 'w') as f:
        yaml.dump(prometheus_config, f, default_flow_style=False, indent=2)
    
    print("  ✅ Created monitoring/prometheus.yml")

def create_grafana_datasource():
    """Create Grafana datasource configuration"""
    print("📈 Creating Grafana datasource configuration...")
    
    datasource_config = {
        "apiVersion": 1,
        "datasources": [
            {
                "name": "Prometheus",
                "type": "prometheus",
                "url": "http://prometheus:9090",
                "access": "proxy",
                "isDefault": True
            }
        ]
    }
    
    with open("monitoring/grafana/datasources/prometheus.yml", 'w') as f:
        yaml.dump(datasource_config, f, default_flow_style=False, indent=2)
    
    print("  ✅ Created monitoring/grafana/datasources/prometheus.yml")

def create_sample_tests():
    """Create sample test files"""
    print("🧪 Creating sample test files...")
    
    # Unit test example
    unit_test_content = '''"""
Sample unit tests for MLOps components
"""
import pytest
import pandas as pd
import numpy as np

def test_data_pipeline():
    """Test data pipeline functionality"""
    # Create sample data
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [0.1, 0.2, 0.3, 0.4, 0.5],
        'target': [0, 1, 0, 1, 0]
    })
    
    assert len(data) == 5
    assert 'target' in data.columns

def test_model_training():
    """Test model training functionality"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Create sample data
    X = np.random.rand(100, 4)
    y = np.random.randint(0, 2, 100)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Make prediction
    prediction = model.predict(X_test)
    
    assert len(prediction) == len(y_test)
    assert all(pred in [0, 1] for pred in prediction)

def test_model_serving():
    """Test model serving functionality"""
    import requests
    import json
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
    except requests.exceptions.RequestException:
        pytest.skip("Model server not running")
    
    # Test prediction endpoint
    try:
        payload = {
            "features": [1.0, 2.0, 3.0, 4.0],
            "model_version": "latest"
        }
        response = requests.post(
            "http://localhost:8000/predict",
            json=payload,
            timeout=5
        )
        assert response.status_code in [200, 404]  # 404 if no models available
    except requests.exceptions.RequestException:
        pytest.skip("Model server not running")
'''
    
    with open("tests/unit/test_sample.py", 'w') as f:
        f.write(unit_test_content)
    
    print("  ✅ Created tests/unit/test_sample.py")

def create_sample_data():
    """Create sample data for testing"""
    print("📊 Creating sample data...")
    
    import pandas as pd
    import numpy as np
    
    # Create sample dataset
    np.random.seed(42)
    n_samples = 1000
    
    data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(0, 1, n_samples),
        'feature3': np.random.normal(0, 1, n_samples),
        'feature4': np.random.normal(0, 1, n_samples),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], n_samples),
        'date_feature': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
        'target': np.random.randint(0, 2, n_samples)
    })
    
    # Save to data directory
    data.to_csv("data/raw/sample_data.csv", index=False)
    data.to_parquet("data/raw/sample_data.parquet", index=False)
    
    print("  ✅ Created data/raw/sample_data.csv")
    print("  ✅ Created data/raw/sample_data.parquet")

def create_dvc_config():
    """Initialize DVC for data versioning"""
    print("📦 Initializing DVC...")
    
    # Initialize DVC
    run_command("dvc init", "Initializing DVC repository", check=False)
    
    # Create .dvcignore
    dvcignore_content = """# DVC ignore file
*.pyc
__pycache__/
*.log
.env
.venv/
venv/
.idea/
.vscode/
*.swp
*.swo
.DS_Store
"""
    
    with open(".dvcignore", 'w') as f:
        f.write(dvcignore_content)
    
    print("  ✅ Created .dvcignore")

def create_git_hooks():
    """Create Git hooks for pre-commit"""
    print("🔧 Setting up Git hooks...")
    
    # Create pre-commit configuration
    pre_commit_config = {
        "repos": [
            {
                "repo": "https://github.com/psf/black",
                "rev": "23.7.0",
                "hooks": [
                    {
                        "id": "black",
                        "language_version": "python3"
                    }
                ]
            },
            {
                "repo": "https://github.com/pycqa/isort",
                "rev": "5.12.0",
                "hooks": [
                    {
                        "id": "isort",
                        "args": ["--profile", "black"]
                    }
                ]
            },
            {
                "repo": "https://github.com/pycqa/flake8",
                "rev": "6.0.0",
                "hooks": [
                    {
                        "id": "flake8",
                        "args": ["--max-line-length=88", "--extend-ignore=E203,W503"]
                    }
                ]
            },
            {
                "repo": "local",
                "hooks": [
                    {
                        "id": "pytest",
                        "name": "pytest",
                        "entry": "pytest",
                        "language": "system",
                        "pass_filenames": False,
                        "always_run": True,
                        "args": ["tests/unit/", "-v"]
                    }
                ]
            }
        ]
    }
    
    with open(".pre-commit-config.yaml", 'w') as f:
        yaml.dump(pre_commit_config, f, default_flow_style=False, indent=2)
    
    print("  ✅ Created .pre-commit-config.yaml")

def create_docker_ignore():
    """Create .dockerignore file"""
    print("🐳 Creating .dockerignore...")
    
    dockerignore_content = """# Docker ignore file
.git
.gitignore
README.md
*.md
.env
.venv
venv
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
.idea
.vscode
*.swp
*.swo
"""
    
    with open(".dockerignore", 'w') as f:
        f.write(dockerignore_content)
    
    print("  ✅ Created .dockerignore")

def create_readme():
    """Create comprehensive README"""
    print("📖 Creating README...")
    
    readme_content = """# MLOps Best Practices Implementation

This repository demonstrates comprehensive MLOps best practices for production-ready machine learning systems.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd mlops

# Run setup script
python setup.py

# Start the MLOps environment
docker-compose up -d
```

### Access Services
- **Model Serving API**: http://localhost:8000
- **MLflow**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jupyter Lab**: http://localhost:8888
- **Airflow**: http://localhost:8080

## 📁 Project Structure

```
mlops/
├── data/                   # Data storage and versioning
├── models/                 # Model artifacts and versions
├── src/                    # Source code
│   ├── pipelines/         # Data and model pipelines
│   ├── features/          # Feature engineering
│   ├── models/            # Model training and evaluation
│   ├── serving/           # Model serving API
│   ├── monitoring/        # Monitoring and alerting
│   └── utils/             # Utility functions
├── tests/                 # Unit and integration tests
├── configs/               # Configuration files
├── notebooks/             # Jupyter notebooks for exploration
├── docker/                # Docker configurations
├── k8s/                   # Kubernetes manifests
├── monitoring/            # Monitoring dashboards
└── docs/                  # Documentation
```

## 🔧 Usage

### Data Pipeline
```bash
python src/pipelines/data_pipeline.py \
  --source data/raw/sample_data.csv \
  --output data/processed/processed_data.parquet
```

### Model Training
```bash
python src/models/train.py \
  --data data/processed/processed_data.parquet \
  --model-type random_forest_classifier \
  --task-type classification
```

### Model Serving
```bash
python src/serving/app.py
```

### Monitoring
```bash
python src/monitoring/monitor.py --daemon
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

## 📊 Monitoring

The monitoring system provides:
- Real-time model performance tracking
- Data drift detection
- Infrastructure monitoring
- Automated alerting

Access dashboards at:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## 🔄 CI/CD

The CI/CD pipeline includes:
- Automated testing
- Security scanning
- Docker image building
- Deployment to staging/production

## 📚 Documentation

- [Pipeline Design Guide](docs/pipeline-design.md)
- [Deployment Guide](docs/deployment.md)
- [Monitoring Guide](docs/monitoring.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
"""
    
    with open("README.md", 'w') as f:
        f.write(readme_content)
    
    print("  ✅ Created README.md")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup MLOps environment")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker setup")
    parser.add_argument("--skip-dvc", action="store_true", help="Skip DVC initialization")
    
    args = parser.parse_args()
    
    print("🚀 Setting up MLOps environment...")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    print()
    
    # Create configuration files
    create_config_files()
    print()
    
    # Create monitoring configurations
    create_prometheus_config()
    create_grafana_datasource()
    print()
    
    # Create sample tests
    create_sample_tests()
    print()
    
    # Create sample data
    create_sample_data()
    print()
    
    # Create DVC configuration
    if not args.skip_dvc:
        create_dvc_config()
        print()
    
    # Create Git hooks
    create_git_hooks()
    print()
    
    # Create Docker configuration
    if not args.skip_docker:
        create_docker_ignore()
        print()
    
    # Create README
    create_readme()
    print()
    
    # Install dependencies
    if not args.skip_deps:
        print("📦 Installing dependencies...")
        run_command("pip install -r requirements.txt", "Installing Python dependencies")
        run_command("pip install pre-commit", "Installing pre-commit")
        run_command("pre-commit install", "Installing pre-commit hooks")
        print()
    
    print("✅ MLOps environment setup completed!")
    print()
    print("🎉 Next steps:")
    print("1. Review and customize configuration files in configs/")
    print("2. Start the environment: docker-compose up -d")
    print("3. Access services at their respective URLs")
    print("4. Run tests: pytest tests/ -v")
    print("5. Start developing!")

if __name__ == "__main__":
    main()