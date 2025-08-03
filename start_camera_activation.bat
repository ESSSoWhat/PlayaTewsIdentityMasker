@echo off
echo ========================================
echo PlayaTews Identity Masker - CAMERA ACTIVATION LAUNCHER
echo ========================================
echo.
echo This launcher ensures the camera source activates properly
echo and the camera feed appears in the preview area.
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with camera activation fix...
echo.

python camera_activation_launcher.py

echo.
echo Application has finished running.
pause
