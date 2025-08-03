@echo off
echo ========================================
echo PlayaTews Identity Masker - DIRECT CAMERA SOURCE FIX
echo ========================================
echo.
echo This launcher directly fixes the camera source module
echo and ensures it activates properly.
echo.
echo Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting PlayaTewsIdentityMasker with direct camera source fix...
python direct_camera_source_fix.py
echo.
echo Application has finished running.
pause 