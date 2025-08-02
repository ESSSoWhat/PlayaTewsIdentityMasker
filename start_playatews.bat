@echo off
echo ========================================
echo PlayaTews Identity Masker - Unified Launcher
echo ========================================
echo.

if "%1"=="" (
    echo Usage: start_playatews.bat [option]
    echo.
    echo Application Options:
    echo   production    - Start production enhanced UI (RECOMMENDED)
    echo   enhanced      - Start enhanced UI with fallback
    echo   simple        - Start simplified enhanced UI
    echo   standard      - Start standard application
    echo.
    echo Voice Changer Options:
    echo   voice         - Start voice changer server
    echo.
    echo Examples:
    echo   start_playatews.bat production
    echo   start_playatews.bat enhanced
    echo   start_playatews.bat voice
    goto :eof
)

if "%1"=="production" (
    echo Starting Production Enhanced UI...
    python launch_production.py
) else if "%1"=="enhanced" (
    echo Starting Enhanced UI...
    python launch_enhanced_app.py
) else if "%1"=="simple" (
    echo Starting Simplified Enhanced UI...
    python launch_enhanced_app_simple.py
) else if "%1"=="standard" (
    echo Starting Standard Application...
    python main.py run PlayaTewsIdentityMasker
) else if "%1"=="voice" (
    echo Starting Voice Changer Server...
    cd voice-changer\server
    python MMVCServerSIO.py
) else (
    echo Unknown option: %1
    echo Run without arguments to see available options.
)

echo.
echo Operation completed.
pause 