@echo off
echo ========================================
echo PlayaTewsIdentityMasker - App Starter
echo ========================================

echo.
echo Starting PlayaTewsIdentityMasker application...
echo.

REM Try the optimized version first
echo Attempting to start optimized version...
python main.py run PlayaTewsIdentityMaskerOptimized

REM If that fails, try the OBS version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Optimized version failed, trying OBS version...
    python main.py run PlayaTewsIdentityMaskerOBS
)

REM If that fails, try the standard version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo OBS version failed, trying standard version...
    python main.py run PlayaTewsIdentityMasker
)

REM If all fail, show error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo ERROR: All app versions failed to start
    echo ========================================
    echo.
    echo Please check:
    echo 1. Python is installed and in PATH
    echo 2. All dependencies are installed
    echo 3. Check the log file: playatewsidentitymasker.log
    echo.
    echo Press any key to exit...
    pause > nul
) else (
    echo.
    echo ========================================
    echo SUCCESS: App started successfully!
    echo ========================================
    echo.
    echo The PlayaTewsIdentityMasker window should now be visible.
    echo If you don't see it, check your taskbar or alt+tab.
    echo.
    echo Press any key to exit this starter...
    pause > nul
) 