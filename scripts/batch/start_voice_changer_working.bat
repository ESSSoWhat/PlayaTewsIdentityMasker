@echo off
echo ========================================
echo Voice Changer - Working Startup
echo ========================================

cd voice-changer\server

echo Fixing torchaudio...
python -m pip uninstall torchaudio -y
python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing core dependencies...
python -m pip install uvicorn fastapi websockets numpy scipy

echo.
echo Installing audio dependencies...
python -m pip install librosa sounddevice resampy

echo.
echo Installing ML dependencies...
python -m pip install onnxruntime faiss-cpu torchcrepe

echo.
echo Testing server...
python -c "import MMVCServerSIO; print('Server test passed')"

echo.
echo Starting voice changer server...
python MMVCServerSIO.py

pause
