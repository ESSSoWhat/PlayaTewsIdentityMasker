@echo off
echo Voice Changer - Minimal Startup
echo ================================

cd voice-changer\server

echo Installing minimal dependencies...
python -m pip install uvicorn fastapi websockets numpy scipy

echo.
echo Testing server startup...
python -c "import MMVCServerSIO; print('Server module loaded successfully')"

echo.
echo If the test passed, starting server...
python MMVCServerSIO.py

pause
