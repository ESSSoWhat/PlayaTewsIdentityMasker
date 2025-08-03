@echo off
echo ========================================
echo PlayaTews Identity Masker - ORIGINAL WORKING LAUNCHER
echo ========================================
echo.
echo This launcher uses the original working approach from the
echo baseline functionality test that was proven to work.
echo.

echo 🔧 Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo.
echo 🚀 Starting PlayaTewsIdentityMasker with original working approach...
echo.

python original_working_launcher.py

echo.
echo Application has finished running.
pause 