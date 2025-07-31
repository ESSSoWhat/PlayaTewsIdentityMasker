#!/bin/bash
# MLOps Deployment Validation Script
# Comprehensive validation for all MLOps environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LOCAL_HOST="localhost"
STAGING_HOST="staging-host"
PRODUCTION_HOST="production-host"
TIMEOUT=10

# Logging
LOG_FILE="mlops-validation-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "🔍 MLOps Deployment Validation"
echo "================================"
echo "Timestamp: $(date)"
echo "Log file: $LOG_FILE"
echo ""

# Helper functions
check_service() {
    local url=$1
    local service_name=$2
    local timeout=${3:-$TIMEOUT}
    
    if curl -f -s --max-time $timeout "$url" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name responding${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name not responding${NC}"
        return 1
    fi
}

check_docker_service() {
    local service_name=$1
    if docker-compose ps | grep -q "$service_name.*Up"; then
        echo -e "${GREEN}✅ $service_name running${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name not running${NC}"
        return 1
    fi
}

run_tests() {
    local test_path=$1
    local test_name=$2
    local env_var=${3:-""}
    
    if [ -n "$env_var" ]; then
        export $env_var
    fi
    
    if pytest "$test_path" -q --tb=no 2>/dev/null; then
        echo -e "${GREEN}✅ $test_name passing${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name failing${NC}"
        return 1
    fi
}

# Initialize counters
local_checks=0
local_passed=0
staging_checks=0
staging_passed=0
production_checks=0
production_passed=0

echo -e "${BLUE}1. Local Development Validation${NC}"
echo "----------------------------------------"

# Check Docker services
echo "Checking Docker services..."
((local_checks++))
check_docker_service "model-server" && ((local_passed++))
((local_checks++))
check_docker_service "mlflow" && ((local_passed++))
((local_checks++))
check_docker_service "prometheus" && ((local_passed++))
((local_checks++))
check_docker_service "grafana" && ((local_passed++))
((local_checks++))
check_docker_service "redis" && ((local_passed++))
((local_checks++))
check_docker_service "postgres" && ((local_passed++))

echo ""
echo "Checking service endpoints..."

# Check service endpoints
((local_checks++))
check_service "http://$LOCAL_HOST:8000/health" "Model API Health" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:8000/predict" "Model API Predict" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:8000/metrics" "Model API Metrics" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:5000" "MLflow UI" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:5000/api/2.0/mlflow/experiments/list" "MLflow API" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:3000" "Grafana UI" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:3000/api/health" "Grafana API" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:9090" "Prometheus UI" && ((local_passed++))

((local_checks++))
check_service "http://$LOCAL_HOST:9090/api/v1/query?query=up" "Prometheus API" && ((local_passed++))

echo ""
echo "Running tests..."

# Run tests
((local_checks++))
run_tests "tests/unit/" "Unit Tests" && ((local_passed++))

((local_checks++))
run_tests "tests/integration/" "Integration Tests" && ((local_passed++))

((local_checks++))
run_tests "tests/performance/" "Performance Tests" && ((local_passed++))

echo ""
echo -e "${BLUE}2. Staging Validation${NC}"
echo "---------------------------"

# Check staging environment
((staging_checks++))
check_service "http://$STAGING_HOST:8000/health" "Staging Model API" && ((staging_passed++))

((staging_checks++))
check_service "http://$STAGING_HOST:8000/metrics" "Staging Metrics" && ((staging_passed++))

((staging_checks++))
check_service "http://$STAGING_HOST:5000" "Staging MLflow" && ((staging_passed++))

((staging_checks++))
check_service "http://$STAGING_HOST:3000" "Staging Grafana" && ((staging_passed++))

((staging_checks++))
check_service "http://$STAGING_HOST:9090" "Staging Prometheus" && ((staging_passed++))

# Run staging-specific tests
((staging_checks++))
run_tests "tests/integration/" "Staging Integration Tests" "STAGING_URL=http://$STAGING_HOST:8000" && ((staging_passed++))

((staging_checks++))
run_tests "tests/performance/" "Staging Performance Tests" "STAGING_URL=http://$STAGING_HOST:8000" && ((staging_passed++))

echo ""
echo -e "${BLUE}3. Production Validation${NC}"
echo "-------------------------------"

# Check production environment
((production_checks++))
check_service "http://$PRODUCTION_HOST:8000/health" "Production Model API" && ((production_passed++))

((production_checks++))
check_service "http://$PRODUCTION_HOST:8000/metrics" "Production Metrics" && ((production_passed++))

((production_checks++))
check_service "http://$PRODUCTION_HOST:5000" "Production MLflow" && ((production_passed++))

((production_checks++))
check_service "http://$PRODUCTION_HOST:3000/api/health" "Production Grafana" && ((production_passed++))

((production_checks++))
check_service "http://$PRODUCTION_HOST:9090/-/healthy" "Production Prometheus" && ((production_passed++))

# Check production-specific features
((production_checks++))
if curl -f -s "http://$PRODUCTION_HOST:8000/health" | jq -e '.status == "healthy"' >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Production health check detailed${NC}"
    ((production_passed++))
else
    echo -e "${RED}❌ Production health check failed${NC}"
fi

((production_checks++))
if curl -f -s "http://$PRODUCTION_HOST:9090/api/v1/alerts" | jq -e '.data.alerts | length > 0' >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Production alerting active${NC}"
    ((production_passed++))
else
    echo -e "${YELLOW}⚠️  Production alerting not configured${NC}"
fi

echo ""
echo -e "${BLUE}4. Kubernetes Validation (if applicable)${NC}"
echo "----------------------------------------"

# Check if kubectl is available
if command -v kubectl &> /dev/null; then
    echo "Checking Kubernetes deployment..."
    
    # Check namespace
    if kubectl get namespace mlops &> /dev/null; then
        echo -e "${GREEN}✅ MLOps namespace exists${NC}"
        
        # Check pods
        if kubectl get pods -n mlops | grep -q "Running"; then
            echo -e "${GREEN}✅ Kubernetes pods running${NC}"
        else
            echo -e "${RED}❌ Kubernetes pods not running${NC}"
        fi
        
        # Check services
        if kubectl get services -n mlops &> /dev/null; then
            echo -e "${GREEN}✅ Kubernetes services configured${NC}"
        else
            echo -e "${RED}❌ Kubernetes services not configured${NC}"
        fi
        
        # Check HPA
        if kubectl get hpa -n mlops &> /dev/null; then
            echo -e "${GREEN}✅ Horizontal Pod Autoscaler configured${NC}"
        else
            echo -e "${YELLOW}⚠️  Horizontal Pod Autoscaler not configured${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  MLOps namespace not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  kubectl not available - skipping Kubernetes checks${NC}"
fi

echo ""
echo -e "${BLUE}5. Cloud Deployment Validation (if applicable)${NC}"
echo "-----------------------------------------------"

# Check AWS CLI
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity &> /dev/null; then
        echo -e "${GREEN}✅ AWS CLI configured${NC}"
        
        # Check ECS services
        if aws ecs describe-services --cluster mlops-cluster --services mlops-service &> /dev/null 2>&1; then
            echo -e "${GREEN}✅ AWS ECS service found${NC}"
        else
            echo -e "${YELLOW}⚠️  AWS ECS service not found${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  AWS CLI not authenticated${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  AWS CLI not available${NC}"
fi

# Check Azure CLI
if command -v az &> /dev/null; then
    if az account show &> /dev/null; then
        echo -e "${GREEN}✅ Azure CLI configured${NC}"
        
        # Check Azure containers
        if az container list --resource-group mlops-rg &> /dev/null 2>&1; then
            echo -e "${GREEN}✅ Azure containers found${NC}"
        else
            echo -e "${YELLOW}⚠️  Azure containers not found${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Azure CLI not authenticated${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Azure CLI not available${NC}"
fi

# Check Google Cloud CLI
if command -v gcloud &> /dev/null; then
    if gcloud config get-value project &> /dev/null; then
        echo -e "${GREEN}✅ Google Cloud CLI configured${NC}"
        
        # Check Cloud Run services
        if gcloud run services list --filter="metadata.name=mlops" &> /dev/null 2>&1; then
            echo -e "${GREEN}✅ Google Cloud Run service found${NC}"
        else
            echo -e "${YELLOW}⚠️  Google Cloud Run service not found${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Google Cloud CLI not authenticated${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Google Cloud CLI not available${NC}"
fi

echo ""
echo -e "${BLUE}6. Monitoring & Maintenance Validation${NC}"
echo "----------------------------------------"

# Check monitoring stack
((local_checks++))
if curl -f -s "http://$LOCAL_HOST:9090/api/v1/query?query=up" | jq -e '.data.result | length > 0' >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Monitoring metrics being collected${NC}"
    ((local_passed++))
else
    echo -e "${RED}❌ Monitoring metrics not being collected${NC}"
fi

# Check log aggregation
if command -v journalctl &> /dev/null; then
    if journalctl -u mlops --since "1 hour ago" | grep -q "ERROR\|WARN\|CRITICAL"; then
        echo -e "${YELLOW}⚠️  Recent errors found in logs${NC}"
    else
        echo -e "${GREEN}✅ No recent errors in logs${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  journalctl not available - skipping log checks${NC}"
fi

# Check backup procedures
if [ -d "/backups/mlops" ]; then
    if [ -f "/backups/mlops/backup-$(date +%Y%m%d).sql" ]; then
        echo -e "${GREEN}✅ Today's backup exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Today's backup not found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Backup directory not found${NC}"
fi

echo ""
echo -e "${BLUE}Validation Summary${NC}"
echo "=================="

# Calculate percentages
local_percent=$((local_passed * 100 / local_checks))
staging_percent=$((staging_passed * 100 / staging_checks))
production_percent=$((production_passed * 100 / production_checks))

echo -e "Local Development: ${local_passed}/${local_checks} (${local_percent}%)"
echo -e "Staging: ${staging_passed}/${staging_checks} (${staging_percent}%)"
echo -e "Production: ${production_passed}/${production_checks} (${production_percent}%)"

# Overall status
total_checks=$((local_checks + staging_checks + production_checks))
total_passed=$((local_passed + staging_passed + production_passed))
overall_percent=$((total_passed * 100 / total_checks))

echo ""
echo -e "Overall Status: ${total_passed}/${total_checks} (${overall_percent}%)"

if [ $overall_percent -ge 90 ]; then
    echo -e "${GREEN}🎉 Excellent! MLOps deployment is healthy${NC}"
elif [ $overall_percent -ge 75 ]; then
    echo -e "${YELLOW}⚠️  Good! Some issues need attention${NC}"
elif [ $overall_percent -ge 50 ]; then
    echo -e "${YELLOW}⚠️  Fair! Several issues need fixing${NC}"
else
    echo -e "${RED}❌ Poor! Major issues detected${NC}"
fi

echo ""
echo "Validation complete!"
echo "Check the log file for detailed information: $LOG_FILE"

# Exit with appropriate code
if [ $overall_percent -ge 75 ]; then
    exit 0
else
    exit 1
fi 