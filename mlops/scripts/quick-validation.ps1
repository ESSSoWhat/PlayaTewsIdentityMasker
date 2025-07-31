# Quick MLOps Validation Script (PowerShell)
# Basic validation for MLOps deployment environments

Write-Host "🔍 MLOps Deployment Validation" -ForegroundColor Blue
Write-Host "================================" -ForegroundColor White
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor White
Write-Host "" -ForegroundColor White

# Initialize counters
$LocalChecks = 0
$LocalPassed = 0
$StagingChecks = 0
$StagingPassed = 0
$ProductionChecks = 0
$ProductionPassed = 0

# Helper functions
function Test-Service {
    param([string]$Url, [string]$ServiceName)
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $ServiceName responding" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $ServiceName not responding (Status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ $ServiceName not responding" -ForegroundColor Red
        return $false
    }
}

function Test-DockerService {
    param([string]$ServiceName)
    
    try {
        $result = docker-compose ps | Select-String "$ServiceName.*Up"
        if ($result) {
            Write-Host "✅ $ServiceName running" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ $ServiceName not running" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ $ServiceName not running" -ForegroundColor Red
        return $false
    }
}

# 1. Local Development Validation
Write-Host "1. Local Development Validation" -ForegroundColor Blue
Write-Host "----------------------------------------" -ForegroundColor White

# Check Docker services
Write-Host "Checking Docker services..." -ForegroundColor White
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

Write-Host "" -ForegroundColor White
Write-Host "Checking service endpoints..." -ForegroundColor White

# Check service endpoints
$LocalChecks++
if (Test-Service "http://localhost:8000/health" "Model API Health") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:8000/predict" "Model API Predict") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:8000/metrics" "Model API Metrics") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:5000" "MLflow UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:5000/api/2.0/mlflow/experiments/list" "MLflow API") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:3000" "Grafana UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:3000/api/health" "Grafana API") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:9090" "Prometheus UI") { $LocalPassed++ }

$LocalChecks++
if (Test-Service "http://localhost:9090/api/v1/query?query=up" "Prometheus API") { $LocalPassed++ }

# 2. Staging Validation
Write-Host "" -ForegroundColor White
Write-Host "2. Staging Validation" -ForegroundColor Blue
Write-Host "---------------------------" -ForegroundColor White

# Check staging environment (using localhost for demo)
$StagingChecks++
if (Test-Service "http://localhost:8000/health" "Staging Model API") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://localhost:8000/metrics" "Staging Metrics") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://localhost:5000" "Staging MLflow") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://localhost:3000" "Staging Grafana") { $StagingPassed++ }

$StagingChecks++
if (Test-Service "http://localhost:9090" "Staging Prometheus") { $StagingPassed++ }

# 3. Production Validation
Write-Host "" -ForegroundColor White
Write-Host "3. Production Validation" -ForegroundColor Blue
Write-Host "-------------------------------" -ForegroundColor White

# Check production environment (using localhost for demo)
$ProductionChecks++
if (Test-Service "http://localhost:8000/health" "Production Model API") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://localhost:8000/metrics" "Production Metrics") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://localhost:5000" "Production MLflow") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://localhost:3000/api/health" "Production Grafana") { $ProductionPassed++ }

$ProductionChecks++
if (Test-Service "http://localhost:9090/-/healthy" "Production Prometheus") { $ProductionPassed++ }

# 4. Kubernetes Validation
Write-Host "" -ForegroundColor White
Write-Host "4. Kubernetes Validation" -ForegroundColor Blue
Write-Host "----------------------------------------" -ForegroundColor White

if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    Write-Host "Checking Kubernetes deployment..." -ForegroundColor White
    
    try {
        $namespace = kubectl get namespace mlops 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ MLOps namespace exists" -ForegroundColor Green
            
            $pods = kubectl get pods -n mlops 2>$null
            if ($pods -match "Running") {
                Write-Host "✅ Kubernetes pods running" -ForegroundColor Green
            } else {
                Write-Host "❌ Kubernetes pods not running" -ForegroundColor Red
            }
        } else {
            Write-Host "⚠️  MLOps namespace not found" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  Kubernetes checks failed" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  kubectl not available - skipping Kubernetes checks" -ForegroundColor Yellow
}

# 5. Cloud Deployment Validation
Write-Host "" -ForegroundColor White
Write-Host "5. Cloud Deployment Validation" -ForegroundColor Blue
Write-Host "-----------------------------------------------" -ForegroundColor White

# Check AWS CLI
if (Get-Command aws -ErrorAction SilentlyContinue) {
    try {
        $identity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ AWS CLI configured" -ForegroundColor Green
        } else {
            Write-Host "⚠️  AWS CLI not authenticated" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  AWS CLI not authenticated" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  AWS CLI not available" -ForegroundColor Yellow
}

# Check Azure CLI
if (Get-Command az -ErrorAction SilentlyContinue) {
    try {
        $account = az account show 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Azure CLI configured" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Azure CLI not authenticated" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  Azure CLI not authenticated" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Azure CLI not available" -ForegroundColor Yellow
}

# Check Google Cloud CLI
if (Get-Command gcloud -ErrorAction SilentlyContinue) {
    try {
        $project = gcloud config get-value project 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Google Cloud CLI configured" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Google Cloud CLI not authenticated" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  Google Cloud CLI not authenticated" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Google Cloud CLI not available" -ForegroundColor Yellow
}

# 6. Monitoring & Maintenance Validation
Write-Host "" -ForegroundColor White
Write-Host "6. Monitoring and Maintenance Validation" -ForegroundColor Blue
Write-Host "----------------------------------------" -ForegroundColor White

# Check monitoring stack
$LocalChecks++
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/query?query=up" -UseBasicParsing -ErrorAction Stop
    $metrics = $response.Content | ConvertFrom-Json
    if ($metrics.data.result.Count -gt 0) {
        Write-Host "✅ Monitoring metrics being collected" -ForegroundColor Green
        $LocalPassed++
    } else {
        Write-Host "❌ Monitoring metrics not being collected" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ Monitoring metrics not being collected" -ForegroundColor Red
}

# Check backup procedures
$backupDir = "/backups/mlops"
if (Test-Path $backupDir) {
    $todayBackup = Join-Path $backupDir "backup-$(Get-Date -Format 'yyyyMMdd').sql"
    if (Test-Path $todayBackup) {
        Write-Host "✅ Today's backup exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Today's backup not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Backup directory not found" -ForegroundColor Yellow
}

# Validation Summary
Write-Host "" -ForegroundColor White
Write-Host "Validation Summary" -ForegroundColor Blue
Write-Host "==================" -ForegroundColor White

# Calculate percentages
$LocalPercent = if ($LocalChecks -gt 0) { [math]::Round(($LocalPassed * 100) / $LocalChecks) } else { 0 }
$StagingPercent = if ($StagingChecks -gt 0) { [math]::Round(($StagingPassed * 100) / $StagingChecks) } else { 0 }
$ProductionPercent = if ($ProductionChecks -gt 0) { [math]::Round(($ProductionPassed * 100) / $ProductionChecks) } else { 0 }

Write-Host "Local Development: $LocalPassed of $LocalChecks checks passed" -ForegroundColor White
Write-Host "Staging: $StagingPassed of $StagingChecks checks passed" -ForegroundColor White
Write-Host "Production: $ProductionPassed of $ProductionChecks checks passed" -ForegroundColor White

# Overall status
$TotalChecks = $LocalChecks + $StagingChecks + $ProductionChecks
$TotalPassed = $LocalPassed + $StagingPassed + $ProductionPassed
$OverallPercent = if ($TotalChecks -gt 0) { [math]::Round(($TotalPassed * 100) / $TotalChecks) } else { 0 }

Write-Host "" -ForegroundColor White
Write-Host "Overall Status: $TotalPassed of $TotalChecks checks passed" -ForegroundColor White

if ($OverallPercent -ge 90) {
    Write-Host "🎉 Excellent! MLOps deployment is healthy" -ForegroundColor Green
} elseif ($OverallPercent -ge 75) {
    Write-Host "⚠️  Good! Some issues need attention" -ForegroundColor Yellow
} elseif ($OverallPercent -ge 50) {
    Write-Host "⚠️  Fair! Several issues need fixing" -ForegroundColor Yellow
} else {
    Write-Host "❌ Poor! Major issues detected" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "Validation complete!" -ForegroundColor White

# Exit with appropriate code
if ($OverallPercent -ge 75) {
    exit 0
} else {
    exit 1
} 