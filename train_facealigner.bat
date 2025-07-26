@echo off
setlocal enabledelayedexpansion
echo Starting FaceAligner Trainer...
echo.

REM Check for most up-to-date launch resources
echo Checking for most up-to-date launch resources...
echo.

REM Check if git is available and this is a git repository
git --version >nul 2>&1
if not errorlevel 1 (
    REM Check if we're in a git repository
    git rev-parse --git-dir >nul 2>&1
    if not errorlevel 1 (
        echo Git repository detected. Checking for updates...
        
        REM Fetch latest changes from remote
        git fetch --quiet
        if errorlevel 1 (
            echo Warning: Could not fetch latest changes from remote repository
        ) else (
            REM Check if local is behind remote
            git rev-list HEAD...origin/main --count >nul 2>&1
            if not errorlevel 1 (
                for /f %%i in ('git rev-list HEAD...origin/main --count 2^>nul') do set BEHIND_COUNT=%%i
                if !BEHIND_COUNT! gtr 0 (
                    echo Warning: Local repository is !BEHIND_COUNT! commits behind remote
                    echo Consider running 'git pull' to update to the latest version
                    echo.
                    set /p UPDATE_CHOICE="Do you want to update now? (y/n): "
                    if /i "!UPDATE_CHOICE!"=="y" (
                        echo Updating repository...
                        git pull
                        if errorlevel 1 (
                            echo Error: Failed to update repository
                            echo Continuing with current version...
                        ) else (
                            echo Repository updated successfully
                        )
                    )
                ) else (
                    echo Repository is up to date
                )
            )
        )
    ) else (
        echo Not a git repository - skipping update check
    )
) else (
    echo Git not available - skipping update check
)

REM Check for critical resource files
echo Checking critical resource files...
if not exist "train_facealigner.py" (
    echo Error: train_facealigner.py not found
    echo Please ensure all required files are present
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo Warning: requirements.txt not found
    echo Dependencies may not be properly installed
)

echo Resource check completed.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Set default workspace and faceset paths if not provided
set WORKSPACE_DIR=%~1
set FACESET_PATH=%~2

if "%WORKSPACE_DIR%"=="" (
    echo No workspace directory specified. Using default: ./workspace
    set WORKSPACE_DIR=./workspace
)

if "%FACESET_PATH%"=="" (
    echo No faceset path specified. Using default: ./faceset.dfs
    set FACESET_PATH=./faceset.dfs
)

echo Workspace Directory: %WORKSPACE_DIR%
echo Faceset Path: %FACESET_PATH%
echo.

REM Run the FaceAligner trainer
python train_facealigner.py --workspace-dir "%WORKSPACE_DIR%" --faceset-path "%FACESET_PATH%"

echo.
echo FaceAligner training completed.
pause