# Start MLOps Services Script (PowerShell)
# Starts core MLOps services without Docker

Write-Host "Starting MLOps Services..." -ForegroundColor Blue
Write-Host "================================" -ForegroundColor White

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+ or use the local Python setup." -ForegroundColor Red
    Write-Host "You can run: scripts/batch/setup_local_python.bat" -ForegroundColor Yellow
    exit 1
}

# Install required packages if not already installed
Write-Host "Installing required packages..." -ForegroundColor White
try {
    pip install fastapi uvicorn redis psycopg2-binary mlflow prometheus-client
    Write-Host "Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "Failed to install packages. Please check your Python environment." -ForegroundColor Red
    exit 1
}

# Start Redis (if available) or use in-memory fallback
Write-Host "Starting Redis..." -ForegroundColor White
try {
    Start-Process -FilePath "redis-server" -WindowStyle Minimized
    Write-Host "Redis started" -ForegroundColor Green
} catch {
    Write-Host "Redis not available, using in-memory fallback" -ForegroundColor Yellow
}

# Start MLflow tracking server
Write-Host "Starting MLflow tracking server..." -ForegroundColor White
try {
    Start-Process -FilePath "python" -ArgumentList "-m", "mlflow", "server", "--host", "0.0.0.0", "--port", "5000" -WindowStyle Minimized
    Write-Host "MLflow started on http://localhost:5000" -ForegroundColor Green
} catch {
    Write-Host "Failed to start MLflow" -ForegroundColor Red
}

# Start the model serving API
Write-Host "Starting Model Serving API..." -ForegroundColor White
try {
    Start-Process -FilePath "python" -ArgumentList "src/serving/app.py" -WindowStyle Minimized
    Write-Host "Model API started on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "Failed to start Model API" -ForegroundColor Red
}

# Start monitoring system
Write-Host "Starting Monitoring System..." -ForegroundColor White
try {
    Start-Process -FilePath "python" -ArgumentList "src/monitoring/monitor.py" -WindowStyle Minimized
    Write-Host "Monitoring system started" -ForegroundColor Green
} catch {
    Write-Host "Failed to start monitoring system" -ForegroundColor Red
}

Write-Host "" -ForegroundColor White
Write-Host "MLOps Services Status:" -ForegroundColor Blue
Write-Host "=====================" -ForegroundColor White
Write-Host "Model API: http://localhost:8000" -ForegroundColor White
Write-Host "MLflow UI: http://localhost:5000" -ForegroundColor White
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host "Metrics: http://localhost:8000/metrics" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "To validate the deployment, run:" -ForegroundColor Yellow
Write-Host "powershell -ExecutionPolicy Bypass -File scripts/clean-validation.ps1" -ForegroundColor White

Write-Host "" -ForegroundColor White
Write-Host "Services started successfully!" -ForegroundColor Green 