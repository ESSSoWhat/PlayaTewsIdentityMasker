@echo off
echo ========================================
echo PlayaTews Identity Masker - SIMPLE WORKING LAUNCHER
echo ========================================
echo.
echo This launcher uses a simple, working approach that avoids
echo widget hierarchy issues while maintaining all functionality.
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with simple working approach...
echo.

python simple_working_launcher.py

echo.
echo Application has finished running.
pause 