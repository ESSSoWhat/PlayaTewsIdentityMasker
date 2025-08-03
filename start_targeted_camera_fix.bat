@echo off
echo ========================================
echo PlayaTews Identity Masker - TARGETED CAMERA SOURCE FIX
echo ========================================
echo.
echo This launcher applies targeted fixes to the camera source module
echo and addresses specific implementation issues.
echo.
echo Terminating any existing Python processes...
taskkill /F /IM python.exe >nul 2>&1
echo.
echo Starting PlayaTewsIdentityMasker with targeted camera source fix...
python targeted_camera_fix.py
echo.
echo Application has finished running.
pause 