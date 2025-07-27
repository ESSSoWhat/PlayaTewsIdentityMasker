# Nuclear Push Fix Script
# This is a last resort solution for stuck Git pushes

Write-Host "NUCLEAR PUSH FIX - LAST RESORT SOLUTION" -ForegroundColor Red
Write-Host "=======================================" -ForegroundColor Red
Write-Host "This will create a fresh repository state and force push everything" -ForegroundColor Yellow
Write-Host "WARNING: This will overwrite the remote repository completely!" -ForegroundColor Red

$confirm = Read-Host "`nAre you absolutely sure you want to proceed? (type 'YES' to continue)"
if ($confirm -ne "YES") {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
    exit 0
}

Write-Host "`nStep 1: Creating backup branch..." -ForegroundColor Green
$backupBranch = "backup-nuclear-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
git branch $backupBranch
Write-Host "Backup branch created: $backupBranch" -ForegroundColor Green

Write-Host "`nStep 2: Killing all Git processes..." -ForegroundColor Green
try {
    Get-Process | Where-Object {$_.ProcessName -like "*git*"} | Stop-Process -Force
    Write-Host "All Git processes terminated" -ForegroundColor Green
} catch {
    Write-Host "No Git processes found or error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nStep 3: Configuring Git for maximum performance..." -ForegroundColor Green
git config --global http.postBuffer 1048576000
git config --global http.maxRequestBuffer 100M
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
git config --global core.compression 0
git config --global pack.windowMemory 100m
git config --global pack.packSizeLimit 100m
Write-Host "Git configured for maximum performance" -ForegroundColor Green

Write-Host "`nStep 4: Pushing LFS files first..." -ForegroundColor Green
try {
    git lfs push --all origin main
    Write-Host "LFS files pushed successfully" -ForegroundColor Green
} catch {
    Write-Host "LFS push failed, continuing anyway: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nStep 5: Force pushing everything..." -ForegroundColor Green
Write-Host "This may take several minutes..." -ForegroundColor Yellow

# Try multiple force push strategies
$strategies = @(
    "git push --force origin main",
    "git push --force-with-lease origin main",
    "git push --force --no-verify origin main"
)

foreach ($strategy in $strategies) {
    Write-Host "`nTrying: $strategy" -ForegroundColor Cyan
    try {
        Invoke-Expression $strategy
        Write-Host "SUCCESS with strategy: $strategy" -ForegroundColor Green
        break
    } catch {
        Write-Host "Failed with strategy: $strategy" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nStep 6: Verifying push..." -ForegroundColor Green
try {
    git fetch origin
    $status = git status --branch --porcelain
    Write-Host "Final status: $status" -ForegroundColor Cyan
    
    if ($status -like "*ahead*") {
        Write-Host "WARNING: Still ahead of origin/main" -ForegroundColor Red
    } else {
        Write-Host "SUCCESS: Repository is now synchronized!" -ForegroundColor Green
    }
} catch {
    Write-Host "Error verifying push: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nNuclear push fix completed!" -ForegroundColor Green
Write-Host "Backup branch: $backupBranch" -ForegroundColor Yellow 