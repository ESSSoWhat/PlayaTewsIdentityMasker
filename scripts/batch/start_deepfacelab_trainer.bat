@echo off
echo Starting DeepFaceLab Trainer...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the DeepFaceLab trainer startup script
python start_deepfacelab_trainer.py

echo.
echo DeepFaceLab training completed.
pause 