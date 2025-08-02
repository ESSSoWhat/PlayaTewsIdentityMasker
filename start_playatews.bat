@echo off
echo ========================================
echo PlayaTews Identity Masker - Real Application Launcher
echo ========================================
echo.

if "%1"=="" (
    echo Usage: start_playatews.bat [option]
    echo.
    echo Application Options:
    echo   standard     - Start standard application (RECOMMENDED)
    echo   obs          - Start OBS-style streaming interface
    echo   optimized    - Start optimized version
    echo   enhanced     - Start enhanced UI version
    echo.
    echo Voice Changer Options:
    echo   voice        - Start voice changer server
    echo.
    echo Examples:
    echo   start_playatews.bat standard
    echo   start_playatews.bat obs
    echo   start_playatews.bat voice
    goto :eof
)

if "%1"=="standard" (
    echo Starting Standard PlayaTews Identity Masker...
    python main.py run PlayaTewsIdentityMasker
    goto :end
) else if "%1"=="obs" (
    echo Starting OBS-Style PlayaTews Identity Masker...
    python main.py run PlayaTewsIdentityMaskerOBS
    goto :end
) else if "%1"=="optimized" (
    echo Starting Optimized PlayaTews Identity Masker...
    python main.py run PlayaTewsIdentityMaskerOptimized
    goto :end
) else if "%1"=="enhanced" (
    echo Starting Enhanced PlayaTews Identity Masker...
    python main.py run PlayaTewsIdentityMaskerEnhanced
    goto :end
) else if "%1"=="voice" (
    echo Starting Voice Changer Server...
    cd voice-changer\server
    python MMVCServerSIO.py
    goto :end
) else (
    echo Unknown option: %1
    echo Run without arguments to see available options.
    goto :eof
)

:end
echo.
echo Application has finished running.
pause 