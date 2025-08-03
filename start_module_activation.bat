@echo off
echo ========================================
echo PlayaTews Identity Masker - MODULE ACTIVATION LAUNCHER
echo ========================================
echo.
echo This launcher forces all modules to activate
echo and ensures they start working properly.
echo.
echo Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting PlayaTewsIdentityMasker with module activation fix...
python module_activation_launcher.py
echo.
echo Application has finished running.
pause
