@echo off
echo ========================================
echo Voice Changer Server (Alternative)
echo ========================================

cd voice-changer\server

echo Checking Python...
python --version

echo Installing requirements...
python -m pip install -r requirements.txt

echo Checking for MMVCServerSIO.py...
if exist MMVCServerSIO.py (
    echo Starting server...
    python MMVCServerSIO.py
) else (
    echo ERROR: MMVCServerSIO.py not found
    echo Please check the voice-changer installation
)

pause
