# MLOps Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the MLOps infrastructure for the PlayaTews Identity Masker project. It covers all deployment strategies, environments, and best practices.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Staging Deployment](#staging-deployment)
5. [Production Deployment](#production-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Monitoring Setup](#monitoring-setup)
9. [Security Configuration](#security-configuration)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Python**: Version 3.9+
- **Git**: Version 2.30+
- **Kubectl**: Version 1.24+ (for Kubernetes deployment)
- **Helm**: Version 3.8+ (for Kubernetes deployment)

### Hardware Requirements

- **CPU**: 4+ cores
- **RAM**: 16GB+ (32GB recommended for production)
- **Storage**: 100GB+ available space
- **GPU**: NVIDIA GPU with CUDA support (optional, for model training)

### Software Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python dependencies
pip install -r requirements.txt
```

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd mlops
```

### 2. Environment Configuration

Create environment-specific configuration files:

```bash
# Copy example configuration
cp .env.example .env

# Edit environment variables
nano .env
```

**Example .env file:**

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mlops
POSTGRES_USER=mlops
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_REGISTRY_URI=http://localhost:5000

# Feature Store
HOPSWORKS_API_KEY=your_hopsworks_api_key
HOPSWORKS_PROJECT=your_project_name

# Monitoring
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Cloud Storage (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=mlops-data

# Alerting
SLACK_WEBHOOK_URL=your_slack_webhook_url
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 3. Initialize DVC (Data Version Control)

```bash
# Initialize DVC
dvc init

# Add remote storage
dvc remote add -d storage s3://your-bucket/mlops-data

# Configure DVC
dvc config core.analytics false
```

## Local Development

### 1. Start Development Environment

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access Services

- **Model API**: http://localhost:8000
- **MLflow UI**: http://localhost:5000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jupyter**: http://localhost:8888

### 3. Run Data Pipeline

```bash
# Run data pipeline
docker-compose run data-pipeline

# Check pipeline status
docker-compose logs data-pipeline
```

### 4. Train Models

```bash
# Run model training
docker-compose run model-training

# Monitor training in MLflow
open http://localhost:5000
```

### 5. Test Model Serving

```bash
# Test prediction endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [1.0, 2.0, 3.0, 4.0],
    "model_version": "latest"
  }'

# Test health endpoint
curl http://localhost:8000/health
```

## Staging Deployment

### 1. Prepare Staging Environment

```bash
# Create staging configuration
cp configs/serving_config.yaml configs/serving_config_staging.yaml

# Edit staging configuration
nano configs/serving_config_staging.yaml
```

### 2. Deploy to Staging

```bash
# Build staging image
docker build -t mlops:staging -f docker/Dockerfile .

# Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# Run staging tests
docker-compose -f docker-compose.staging.yml run testing
```

### 3. Staging Validation

```bash
# Run smoke tests
pytest tests/smoke/ -v

# Run performance tests
pytest tests/performance/ -v

# Check monitoring
curl http://staging-host:8000/health
```

## Production Deployment

### 1. Production Configuration

```bash
# Create production configuration
cp configs/serving_config.yaml configs/serving_config_production.yaml

# Edit production configuration
nano configs/serving_config_production.yaml
```

**Production Configuration Checklist:**

- [ ] Authentication enabled
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring enabled
- [ ] Logging configured
- [ ] Security headers set
- [ ] Backup strategy configured

### 2. Blue-Green Deployment

```bash
# Deploy new version (green)
docker-compose -f docker-compose.production.yml up -d

# Health check
curl http://production-host:8000/health

# Switch traffic (if using load balancer)
# Update DNS or load balancer configuration

# Monitor for issues
# Check metrics and logs

# Rollback if needed (blue)
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml.rollback up -d
```

### 3. Canary Deployment

```bash
# Deploy canary version
docker-compose -f docker-compose.production.yml -f docker-compose.canary.yml up -d

# Monitor canary performance
# Check metrics, error rates, latency

# Gradually increase traffic
# Update traffic split configuration

# Full rollout or rollback based on metrics
```

## Kubernetes Deployment

### 1. Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Configure kubectl for your cluster
kubectl config set-cluster your-cluster
kubectl config set-context your-context
kubectl config use-context your-context
```

### 2. Deploy Infrastructure

```bash
# Create namespace
kubectl create namespace mlops

# Deploy PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --namespace mlops \
  --set postgresqlPassword=secure_password

# Deploy Redis
helm install redis bitnami/redis \
  --namespace mlops \
  --set auth.enabled=false

# Deploy Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace mlops

# Deploy Grafana
helm install grafana bitnami/grafana \
  --namespace mlops \
  --set adminPassword=admin
```

### 3. Deploy Application

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Check deployment status
kubectl get pods -n mlops
kubectl get services -n mlops
kubectl get ingress -n mlops
```

### 4. Kubernetes Monitoring

```bash
# Check pod logs
kubectl logs -f deployment/mlops-model-server -n mlops

# Check resource usage
kubectl top pods -n mlops

# Check events
kubectl get events -n mlops --sort-by='.lastTimestamp'
```

## Cloud Deployment

### AWS Deployment

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure

# Deploy using AWS ECS
aws ecs create-cluster --cluster-name mlops-cluster
aws ecs register-task-definition --cli-input-json file://aws/task-definition.json
aws ecs create-service --cli-input-json file://aws/service-definition.json
```

### Azure Deployment

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name mlops-rg --location eastus

# Deploy using Azure Container Instances
az container create \
  --resource-group mlops-rg \
  --name mlops-container \
  --image mlops:latest \
  --ports 8000
```

### Google Cloud Deployment

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Deploy using Google Cloud Run
gcloud run deploy mlops \
  --image gcr.io/your-project/mlops:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Monitoring Setup

### 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mlops-model-server'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'mlops-monitoring'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: '/metrics'
```

### 2. Grafana Dashboards

```bash
# Import dashboards
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/mlops-overview.json

curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/dashboards/model-performance.json
```

### 3. Alerting Rules

```yaml
# alerting-rules.yml
groups:
  - name: mlops-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"

      - alert: ModelLatencyHigh
        expr: histogram_quantile(0.95, model_prediction_duration_seconds_bucket) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High model latency"
          description: "95th percentile latency is {{ $value }}s"
```

## Security Configuration

### 1. Authentication Setup

```python
# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 Configuration
OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')
OAUTH2_AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/auth"
OAUTH2_TOKEN_URL = "https://oauth2.googleapis.com/token"
```

### 2. SSL/TLS Configuration

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure HTTPS in FastAPI
uvicorn app:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### 3. Network Security

```yaml
# Docker network configuration
networks:
  mlops-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.name: mlops-br0
```

## Troubleshooting

### Common Issues

#### 1. Service Not Starting

```bash
# Check service logs
docker-compose logs service-name

# Check resource usage
docker stats

# Restart service
docker-compose restart service-name
```

#### 2. Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres

# Reset database (development only)
docker-compose down -v
docker-compose up -d
```

#### 3. Model Loading Issues

```bash
# Check model files
ls -la models/

# Check model metadata
python -c "import joblib; print(joblib.load('models/model.joblib').keys())"

# Rebuild model
docker-compose run model-training
```

#### 4. Monitoring Issues

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana datasources
curl http://admin:admin@localhost:3000/api/datasources

# Restart monitoring stack
docker-compose restart prometheus grafana
```

### Performance Optimization

#### 1. Resource Limits

```yaml
# docker-compose.yml
services:
  model-server:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### 2. Caching Configuration

```python
# Redis caching
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 10000
CACHE_KEY_PREFIX = "mlops:"
```

#### 3. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_predictions_timestamp ON predictions(timestamp);
CREATE INDEX idx_predictions_model_version ON predictions(model_version);

-- Optimize queries
ANALYZE predictions;
```

### Backup and Recovery

#### 1. Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U mlops mlops > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U mlops mlops < backup.sql
```

#### 2. Model Backup

```bash
# Backup models
tar -czf models_backup.tar.gz models/

# Restore models
tar -xzf models_backup.tar.gz
```

#### 3. Configuration Backup

```bash
# Backup configuration
tar -czf config_backup.tar.gz configs/

# Restore configuration
tar -xzf config_backup.tar.gz
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying the MLOps infrastructure. Follow the steps carefully and ensure all prerequisites are met before proceeding with deployment.

For additional support:
- Check the troubleshooting section
- Review the monitoring dashboards
- Consult the documentation
- Create an issue in the repository

Remember to:
- Test thoroughly in staging before production
- Monitor performance and resource usage
- Keep backups of critical data
- Update security configurations regularly
- Document any customizations made 