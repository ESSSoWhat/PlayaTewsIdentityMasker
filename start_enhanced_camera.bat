@echo off
echo ========================================
echo PlayaTews Identity Masker - ENHANCED CAMERA LAUNCHER
echo ========================================
echo.
echo This launcher forces camera source activation
echo and bypasses all API issues for immediate results.
echo.
echo Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting PlayaTewsIdentityMasker with enhanced camera fix...
python enhanced_camera_launcher.py
echo.
echo Application has finished running.
pause 