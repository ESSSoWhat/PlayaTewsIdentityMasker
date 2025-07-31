# MLOps Validation Script

## Overview

The `mlops-validation.sh` script provides comprehensive validation for all MLOps deployment environments. It checks local development, staging, production, Kubernetes, and cloud deployments.

## Quick Start

### 1. Basic Usage

```bash
# Make script executable
chmod +x mlops/scripts/mlops-validation.sh

# Run validation
./mlops/scripts/mlops-validation.sh
```

### 2. Configure for Your Environment

Edit the configuration file:
```bash
nano mlops/scripts/validation-config.env
```

Update the hostnames and settings for your specific environments:
```bash
# Update these values
LOCAL_HOST="localhost"
STAGING_HOST="staging.yourdomain.com"
PRODUCTION_HOST="production.yourdomain.com"
```

### 3. Run Specific Validations

```bash
# Local development only
LOCAL_HOST="localhost" ./mlops/scripts/mlops-validation.sh

# Staging only
STAGING_HOST="staging.yourdomain.com" ./mlops/scripts/mlops-validation.sh

# Production only
PRODUCTION_HOST="production.yourdomain.com" ./mlops/scripts/mlops-validation.sh
```

## What the Script Validates

### 1. Local Development ✅
- Docker services running (model-server, mlflow, prometheus, grafana, redis, postgres)
- Service endpoints responding (health, predict, metrics)
- MLflow UI and API accessible
- Grafana dashboards accessible
- Prometheus metrics collection
- Unit, integration, and performance tests passing

### 2. Staging Environment ✅
- Staging services responding
- Integration tests against staging
- Performance tests against staging
- Monitoring and alerting configured

### 3. Production Environment ✅
- Production services responding
- Health checks detailed
- Alerting active
- Zero-downtime deployment verified

### 4. Kubernetes Deployment ✅
- Namespace exists
- Pods running
- Services configured
- Horizontal Pod Autoscaler configured

### 5. Cloud Deployment ✅
- AWS ECS services (if AWS CLI configured)
- Azure containers (if Azure CLI configured)
- Google Cloud Run services (if gcloud configured)

### 6. Monitoring & Maintenance ✅
- Metrics collection active
- Log aggregation working
- Backup procedures in place
- Recent errors checked

## Output Examples

### Successful Validation
```
🔍 MLOps Deployment Validation
================================
Timestamp: 2024-01-15 10:30:00
Log file: mlops-validation-20240115-103000.log

1. Local Development Validation
----------------------------------------
Checking Docker services...
✅ model-server running
✅ mlflow running
✅ prometheus running
✅ grafana running
✅ redis running
✅ postgres running

Checking service endpoints...
✅ Model API Health responding
✅ Model API Predict responding
✅ Model API Metrics responding
✅ MLflow UI responding
✅ MLflow API responding
✅ Grafana UI responding
✅ Grafana API responding
✅ Prometheus UI responding
✅ Prometheus API responding

Running tests...
✅ Unit Tests passing
✅ Integration Tests passing
✅ Performance Tests passing

Validation Summary
==================
Local Development: 15/15 (100%)
Staging: 7/7 (100%)
Production: 7/7 (100%)

Overall Status: 29/29 (100%)

🎉 Excellent! MLOps deployment is healthy
```

### Issues Detected
```
❌ Model API not responding
❌ MLflow not accessible
⚠️  Production alerting not configured
⚠️  kubectl not available - skipping Kubernetes checks

Validation Summary
==================
Local Development: 12/15 (80%)
Staging: 5/7 (71%)
Production: 6/7 (86%)

Overall Status: 23/29 (79%)

⚠️  Good! Some issues need attention
```

## Configuration Options

### Environment Variables

You can override settings using environment variables:

```bash
# Custom hosts
LOCAL_HOST="dev.local" STAGING_HOST="staging.company.com" PRODUCTION_HOST="prod.company.com" ./mlops/scripts/mlops-validation.sh

# Custom timeouts
TIMEOUT="30" ./mlops/scripts/mlops-validation.sh

# Skip certain tests
RUN_PERFORMANCE_TESTS="false" ./mlops/scripts/mlops-validation.sh
```

### Configuration File

The script automatically loads `validation-config.env` if it exists in the same directory. You can specify a custom config file:

```bash
CONFIG_FILE="/path/to/custom-config.env" ./mlops/scripts/mlops-validation.sh
```

## Troubleshooting

### Common Issues

1. **Services not responding**
   ```bash
   # Check if Docker Compose is running
   docker-compose ps
   
   # Check service logs
   docker-compose logs model-server
   ```

2. **Tests failing**
   ```bash
   # Run tests manually to see detailed errors
   pytest tests/unit/ -v
   pytest tests/integration/ -v
   ```

3. **Kubernetes checks failing**
   ```bash
   # Check kubectl configuration
   kubectl config current-context
   kubectl get pods -n mlops
   ```

4. **Cloud checks failing**
   ```bash
   # Check AWS CLI
   aws sts get-caller-identity
   
   # Check Azure CLI
   az account show
   
   # Check Google Cloud CLI
   gcloud config get-value project
   ```

### Log Files

The script creates detailed log files with timestamps:
```
mlops-validation-20240115-103000.log
mlops-validation-20240115-143000.log
mlops-validation-20240115-183000.log
```

Check the log file for detailed error information:
```bash
tail -f mlops-validation-*.log
```

## Integration with CI/CD

### GitHub Actions

Add to your workflow:
```yaml
- name: Validate MLOps Deployment
  run: |
    chmod +x mlops/scripts/mlops-validation.sh
    ./mlops/scripts/mlops-validation.sh
```

### Jenkins Pipeline

Add to your pipeline:
```groovy
stage('Validate MLOps') {
    steps {
        sh 'chmod +x mlops/scripts/mlops-validation.sh'
        sh './mlops/scripts/mlops-validation.sh'
    }
}
```

### GitLab CI

Add to your `.gitlab-ci.yml`:
```yaml
validate_mlops:
  script:
    - chmod +x mlops/scripts/mlops-validation.sh
    - ./mlops/scripts/mlops-validation.sh
```

## Exit Codes

The script returns appropriate exit codes for CI/CD integration:

- `0`: Validation passed (≥75% success rate)
- `1`: Validation failed (<75% success rate)

## Customization

### Adding Custom Checks

You can extend the script by adding custom validation functions:

```bash
# Add to the script
check_custom_service() {
    local url=$1
    local service_name=$2
    
    if curl -f -s "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name not responding${NC}"
        return 1
    fi
}

# Use in validation
check_custom_service "http://localhost:8080/health" "Custom Service"
```

### Custom Test Suites

Add custom test paths:
```bash
# Add to script
run_tests "tests/custom/" "Custom Tests"
```

## Support

For issues with the validation script:

1. Check the log file for detailed error information
2. Verify your configuration in `validation-config.env`
3. Ensure all required tools are installed (curl, jq, pytest, docker-compose)
4. Check network connectivity to your services

## Dependencies

The script requires:
- `bash` (version 4.0+)
- `curl` (for HTTP requests)
- `jq` (for JSON parsing)
- `pytest` (for running tests)
- `docker-compose` (for checking Docker services)
- `kubectl` (optional, for Kubernetes checks)
- `aws` (optional, for AWS checks)
- `az` (optional, for Azure checks)
- `gcloud` (optional, for Google Cloud checks) 