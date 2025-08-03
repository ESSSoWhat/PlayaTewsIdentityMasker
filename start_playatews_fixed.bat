@echo off
echo ========================================
echo PlayaTews Identity Masker - FIXED LAUNCHER
echo ========================================
echo.
echo This launcher uses the comprehensive fix that ensures:
echo - Proper Qt application context
echo - DirectShow camera backend
echo - Camera feed appears in preview area
echo - Enhanced output integrated into main UI
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with comprehensive fixes...
echo.

python final_app_launcher.py

echo.
echo Application has finished running.
pause 