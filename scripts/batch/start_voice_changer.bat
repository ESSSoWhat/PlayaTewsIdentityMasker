@echo off
echo ========================================
echo Voice Changer Server Startup
echo ========================================

cd voice-changer\server

echo Installing requirements...
python -m pip install -r requirements.txt

echo Starting server...
python MMVCServerSIO.py

pause
