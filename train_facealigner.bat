@echo off
echo Starting FaceAligner Trainer...
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