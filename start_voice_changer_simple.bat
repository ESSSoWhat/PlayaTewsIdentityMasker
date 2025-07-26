@echo off
echo ========================================
echo Voice Changer Server - Simple Startup
echo ========================================

cd voice-changer\server

echo Checking Python version...
python --version

echo.
echo Installing/updating pip...
python -m pip install --upgrade pip

echo.
echo Installing core dependencies...
python -m pip install uvicorn fastapi websockets numpy

echo.
echo Installing PyTorch (CPU version for compatibility)...
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing other dependencies...
python -m pip install scipy librosa sounddevice

echo.
echo Installing ONNX Runtime...
python -m pip install onnxruntime

echo.
echo Installing remaining dependencies...
python -m pip install -r requirements.txt --no-deps

echo.
echo Starting voice changer server...
python MMVCServerSIO.py

pause 