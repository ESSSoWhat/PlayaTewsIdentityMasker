# MLOps Deployment Validation Script (PowerShell)
# Comprehensive validation for all MLOps deployment environments

param(
    [string]$ConfigFile = "scripts/validation-config.env",
    [string]$LocalHost = "localhost",
    [string]$StagingHost = "staging.yourdomain.com",
    [string]$ProductionHost = "production.yourdomain.com",
    [int]$Timeout = 10
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Logging
$LogFile = "mlops-validation-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$LogPath = Join-Path $PWD $LogFile

# Initialize counters
$LocalChecks = 0
$LocalPassed = 0
$StagingChecks = 0
$StagingPassed = 0
$ProductionChecks = 0
$ProductionPassed = 0

# Helper functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = $White
    )
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path $LogPath -Value $Message
}

function Test-Service {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$TimeoutSeconds = $Timeout
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✅ $ServiceName responding" $Green
            return $true
        } else {
            Write-ColorOutput "❌ $ServiceName not responding (Status: $($response.StatusCode))" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ $ServiceName not responding" $Red
        return $false
    }
}

function Test-DockerService {
    param([string]$ServiceName)
    
    try {
        $result = docker-compose ps | Select-String "$ServiceName.*Up"
        if ($result) {
            Write-ColorOutput "✅ $ServiceName running" $Green
            return $true
        } else {
            Write-ColorOutput "❌ $ServiceName not running" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ $ServiceName not running" $Red
        return $false
    }
}

function Test-PythonTests {
    param(
        [string]$TestPath,
        [string]$TestName,
        [string]$EnvVar = ""
    )
    
    try {
        if ($EnvVar) {
            $env:STAGING_URL = $EnvVar
        }
        
        $result = python -m pytest $TestPath -q --tb=no 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ $TestName passing" $Green
            return $true
        } else {
            Write-ColorOutput "❌ $TestName failing" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "❌ $TestName failing" $Red
        return $false
    }
}

# Start validation
Write-ColorOutput "🔍 MLOps Deployment Validation" $Blue
Write-ColorOutput "================================" $White
Write-ColorOutput "Timestamp: $(Get-Date)" $White
Write-ColorOutput "Log file: $LogPath" $White
Write-ColorOutput "" $White

# 1. Local Development Validation
Write-ColorOutput "1. Local Development Validation" $Blue
Write-ColorOutput "----------------------------------------" $White

# Check Docker services
Write-ColorOutput "Checking Docker services..." $White
$LocalChecks++
if (Test-DockerService "model-server") { $LocalPassed++ }

$LocalChecks++
if (Test-DockerService "mlflow") { $LocalPassed++ }

$LocalChecks++
if (Test-DockerService "prometheus") { $LocalPassed++ }

$LocalChecks++
if (Test-DockerService "grafana") { $LocalPassed++ }

$LocalChecks++
if (Test-DockerService "redis") { $LocalPassed++ }

$LocalChecks++
if (Test-DockerService "postgres") { $LocalPassed++ }

Write-ColorOutput "" $White
Write-ColorOutput "Checking service endpoints..." $White

# Check service endpoints
$LocalChecks++
if (Test-Service "http://$LocalHost`:8000/health" "Model API Health") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:8000/predict" "Model API Predict") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:8000/metrics" "Model API Metrics") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:5000" "MLflow UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:5000/api/2.0/mlflow/experiments/list" "MLflow API") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:3000" "Grafana UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:3000/api/health" "Grafana API") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:9090" "Prometheus UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://$LocalHost`:9090/api/v1/query?query=up" "Prometheus API") { $LocalPassed++ }

Write-ColorOutput "" $White
Write-ColorOutput "Running tests..." $White

# Run tests (if pytest is available)
if (Get-Command python -ErrorAction SilentlyContinue) {
    $LocalChecks++
    if (Test-PythonTests "tests/unit/" "Unit Tests") { $LocalPassed++ }

    $LocalChecks++
    if (Test-PythonTests "tests/integration/" "Integration Tests") { $LocalPassed++ }

    $LocalChecks++
    if (Test-PythonTests "tests/performance/" "Performance Tests") { $LocalPassed++ }
} else {
    Write-ColorOutput "⚠️  Python not available - skipping tests" $Yellow
}

# 2. Staging Validation
Write-ColorOutput "" $White
Write-ColorOutput "2. Staging Validation" $Blue
Write-ColorOutput "---------------------------" $White

# Check staging environment
$StagingChecks++
if (Test-Service "http://$StagingHost`:8000/health" "Staging Model API") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://$StagingHost`:8000/metrics" "Staging Metrics") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://$StagingHost`:5000" "Staging MLflow") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://$StagingHost`:3000" "Staging Grafana") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://$StagingHost`:9090" "Staging Prometheus") { $StagingPassed++ }

# Run staging-specific tests
if (Get-Command python -ErrorAction SilentlyContinue) {
    $StagingChecks++
    if (Test-PythonTests "tests/integration/" "Staging Integration Tests" "http://$StagingHost`:8000") { $StagingPassed++ }

    $StagingChecks++
    if (Test-PythonTests "tests/performance/" "Staging Performance Tests" "http://$StagingHost`:8000") { $StagingPassed++ }
}

# 3. Production Validation
Write-ColorOutput "" $White
Write-ColorOutput "3. Production Validation" $Blue
Write-ColorOutput "-------------------------------" $White

# Check production environment
$ProductionChecks++
if (Test-Service "http://$ProductionHost`:8000/health" "Production Model API") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://$ProductionHost`:8000/metrics" "Production Metrics") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://$ProductionHost`:5000" "Production MLflow") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://$ProductionHost`:3000/api/health" "Production Grafana") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://$ProductionHost`:9090/-/healthy" "Production Prometheus") { $ProductionPassed++ }

# Check production-specific features
$ProductionChecks++
try {
    $response = Invoke-WebRequest -Uri "http://$ProductionHost`:8000/health" -UseBasicParsing -ErrorAction Stop
    $healthData = $response.Content | ConvertFrom-Json
    if ($healthData.status -eq "healthy") {
        Write-ColorOutput "✅ Production health check detailed" $Green
        $ProductionPassed++
    } else {
        Write-ColorOutput "❌ Production health check failed" $Red
    }
}
catch {
    Write-ColorOutput "❌ Production health check failed" $Red
}

# 4. Kubernetes Validation (if applicable)
Write-ColorOutput "" $White
Write-ColorOutput "4. Kubernetes Validation (if applicable)" $Blue
Write-ColorOutput "----------------------------------------" $White

# Check if kubectl is available
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    Write-ColorOutput "Checking Kubernetes deployment..." $White
    
    try {
        # Check namespace
        $namespace = kubectl get namespace mlops 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ MLOps namespace exists" $Green
            
            # Check pods
            $pods = kubectl get pods -n mlops 2>$null
            if ($pods -match "Running") {
                Write-ColorOutput "✅ Kubernetes pods running" $Green
            } else {
                Write-ColorOutput "❌ Kubernetes pods not running" $Red
            }
            
            # Check services
            $services = kubectl get services -n mlops 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ Kubernetes services configured" $Green
            } else {
                Write-ColorOutput "❌ Kubernetes services not configured" $Red
            }
            
            # Check HPA
            $hpa = kubectl get hpa -n mlops 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ Horizontal Pod Autoscaler configured" $Green
            } else {
                Write-ColorOutput "⚠️  Horizontal Pod Autoscaler not configured" $Yellow
            }
        } else {
            Write-ColorOutput "⚠️  MLOps namespace not found" $Yellow
        }
    }
    catch {
        Write-ColorOutput "⚠️  Kubernetes checks failed" $Yellow
    }
} else {
    Write-ColorOutput "⚠️  kubectl not available - skipping Kubernetes checks" $Yellow
}

# 5. Cloud Deployment Validation (if applicable)
Write-ColorOutput "" $White
Write-ColorOutput "5. Cloud Deployment Validation (if applicable)" $Blue
Write-ColorOutput "-----------------------------------------------" $White

# Check AWS CLI
if (Get-Command aws -ErrorAction SilentlyContinue) {
    try {
        $identity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ AWS CLI configured" $Green
            
            # Check ECS services
            $ecs = aws ecs describe-services --cluster mlops-cluster --services mlops-service 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ AWS ECS service found" $Green
            } else {
                Write-ColorOutput "⚠️  AWS ECS service not found" $Yellow
            }
        } else {
            Write-ColorOutput "⚠️  AWS CLI not authenticated" $Yellow
        }
    }
    catch {
        Write-ColorOutput "⚠️  AWS CLI not authenticated" $Yellow
    }
} else {
    Write-ColorOutput "⚠️  AWS CLI not available" $Yellow
}

# Check Azure CLI
if (Get-Command az -ErrorAction SilentlyContinue) {
    try {
        $account = az account show 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Azure CLI configured" $Green
            
            # Check Azure containers
            $containers = az container list --resource-group mlops-rg 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ Azure containers found" $Green
            } else {
                Write-ColorOutput "⚠️  Azure containers not found" $Yellow
            }
        } else {
            Write-ColorOutput "⚠️  Azure CLI not authenticated" $Yellow
        }
    }
    catch {
        Write-ColorOutput "⚠️  Azure CLI not authenticated" $Yellow
    }
} else {
    Write-ColorOutput "⚠️  Azure CLI not available" $Yellow
}

# Check Google Cloud CLI
if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    try {
        $project = gcloud config get-value project 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Google Cloud CLI configured" $Green
            
            # Check Cloud Run services
            $services = gcloud run services list --filter="metadata.name=mlops" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ Google Cloud Run service found" $Green
            } else {
                Write-ColorOutput "⚠️  Google Cloud Run service not found" $Yellow
            }
        } else {
            Write-ColorOutput "⚠️  Google Cloud CLI not authenticated" $Yellow
        }
    }
    catch {
        Write-ColorOutput "⚠️  Google Cloud CLI not authenticated" $Yellow
    }
} else {
    Write-ColorOutput "⚠️  Google Cloud CLI not available" $Yellow
}

# 6. Monitoring & Maintenance Validation
Write-ColorOutput "" $White
Write-ColorOutput "6. Monitoring and Maintenance Validation" $Blue
Write-ColorOutput "----------------------------------------" $White

# Check monitoring stack
$LocalChecks++
try {
    $response = Invoke-WebRequest -Uri "http://$LocalHost`:9090/api/v1/query?query=up" -UseBasicParsing -ErrorAction Stop
    $metrics = $response.Content | ConvertFrom-Json
    if ($metrics.data.result.Count -gt 0) {
        Write-ColorOutput "✅ Monitoring metrics being collected" $Green
        $LocalPassed++
    } else {
        Write-ColorOutput "❌ Monitoring metrics not being collected" $Red
    }
}
catch {
    Write-ColorOutput "❌ Monitoring metrics not being collected" $Red
}

# Check backup procedures
$backupDir = "/backups/mlops"
if (Test-Path $backupDir) {
    $todayBackup = Join-Path $backupDir "backup-$(Get-Date -Format 'yyyyMMdd').sql"
    if (Test-Path $todayBackup) {
        Write-ColorOutput "✅ Today's backup exists" $Green
    } else {
        Write-ColorOutput "⚠️  Today's backup not found" $Yellow
    }
} else {
    Write-ColorOutput "⚠️  Backup directory not found" $Yellow
}

# Validation Summary
Write-ColorOutput "" $White
Write-ColorOutput "Validation Summary" $Blue
Write-ColorOutput "==================" $White

# Calculate percentages
$LocalPercent = if ($LocalChecks -gt 0) { [math]::Round(($LocalPassed * 100) / $LocalChecks) } else { 0 }
$StagingPercent = if ($StagingChecks -gt 0) { [math]::Round(($StagingPassed * 100) / $StagingChecks) } else { 0 }
$ProductionPercent = if ($ProductionChecks -gt 0) { [math]::Round(($ProductionPassed * 100) / $ProductionChecks) } else { 0 }

Write-ColorOutput ("Local Development: " + $LocalPassed + "/" + $LocalChecks + " (" + $LocalPercent + " percent)") $White
Write-ColorOutput ("Staging: " + $StagingPassed + "/" + $StagingChecks + " (" + $StagingPercent + " percent)") $White
Write-ColorOutput ("Production: " + $ProductionPassed + "/" + $ProductionChecks + " (" + $ProductionPercent + " percent)") $White

# Overall status
$TotalChecks = $LocalChecks + $StagingChecks + $ProductionChecks
$TotalPassed = $LocalPassed + $StagingPassed + $ProductionPassed
$OverallPercent = if ($TotalChecks -gt 0) { [math]::Round(($TotalPassed * 100) / $TotalChecks) } else { 0 }

Write-ColorOutput "" $White
Write-ColorOutput ("Overall Status: " + $TotalPassed + "/" + $TotalChecks + " (" + $OverallPercent + " percent)") $White

if ($OverallPercent -ge 90) {
    Write-ColorOutput "🎉 Excellent! MLOps deployment is healthy" $Green
} elseif ($OverallPercent -ge 75) {
    Write-ColorOutput "⚠️  Good! Some issues need attention" $Yellow
} elseif ($OverallPercent -ge 50) {
    Write-ColorOutput "⚠️  Fair! Several issues need fixing" $Yellow
} else {
    Write-ColorOutput "❌ Poor! Major issues detected" $Red
}

Write-ColorOutput "" $White
Write-ColorOutput "Validation complete!" $White
Write-ColorOutput "Check the log file for detailed information: $LogPath" $White

# Exit with appropriate code
if ($OverallPercent -ge 75) {
    exit 0
} else {
    exit 1
} 