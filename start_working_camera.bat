@echo off
echo ========================================
echo PlayaTews Identity Masker - WORKING CAMERA LAUNCHER
echo ========================================
echo.
echo This launcher bypasses API issues and directly
echo activates the camera source for immediate results.
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with working camera fix...
echo.

python working_camera_launcher.py

echo.
echo Application has finished running.
pause
