@echo off
echo ========================================
echo PlayaTews Identity Masker Launcher
echo ========================================

set SCRIPT_DIR=%~dp0
set BATCH_DIR=%SCRIPT_DIR%batch

cd /d "%SCRIPT_DIR%.."

if "%1"=="" (
    echo Usage: launcher.bat [option]
    echo.
    echo Application Options:
    echo   app          - Start main application
    echo   app-local    - Start with local Python
    echo.
    echo Voice Changer Options:
    echo   voice        - Start voice changer
    echo   voice-alt    - Start alternative voice changer
    echo   voice-min    - Start minimal voice changer
    echo   voice-simple - Start simple voice changer
    echo   voice-work   - Start working voice changer
    echo.
    echo Setup Options:
    echo   setup        - Setup local Python
    echo   trainer      - Start DeepFaceLab trainer
    echo   train        - Train face aligner
    echo.
    echo Test Options:
    echo   test-all     - Run all tests
    echo   test-comp    - Run component tests
    echo   test-perf    - Run performance tests
    echo   test-ui      - Run UI tests
    echo   test-voice   - Run voice changer tests
    echo.
    echo Examples:
    echo   launcher.bat app
    echo   launcher.bat voice
    echo   launcher.bat test-all
    goto :eof
)

if "%1"=="app" (
    echo Starting main application...
    call "%BATCH_DIR%\start_playatews_app.bat"
) else if "%1"=="app-local" (
    echo Starting application with local Python...
    call "%BATCH_DIR%\start_app_local_python.bat"
) else if "%1"=="voice" (
    echo Starting voice changer...
    call "%BATCH_DIR%\start_voice_changer.bat"
) else if "%1"=="voice-alt" (
    echo Starting alternative voice changer...
    call "%BATCH_DIR%\start_voice_changer_alt.bat"
) else if "%1"=="voice-min" (
    echo Starting minimal voice changer...
    call "%BATCH_DIR%\start_voice_changer_minimal.bat"
) else if "%1"=="voice-simple" (
    echo Starting simple voice changer...
    call "%BATCH_DIR%\start_voice_changer_simple.bat"
) else if "%1"=="voice-work" (
    echo Starting working voice changer...
    call "%BATCH_DIR%\start_voice_changer_working.bat"
) else if "%1"=="setup" (
    echo Setting up local Python...
    call "%BATCH_DIR%\setup_local_python.bat"
) else if "%1"=="trainer" (
    echo Starting DeepFaceLab trainer...
    call "%BATCH_DIR%\start_deepfacelab_trainer.bat"
) else if "%1"=="train" (
    echo Training face aligner...
    call "%BATCH_DIR%\train_facealigner.bat"
) else if "%1"=="test-all" (
    echo Running all tests...
    call "%SCRIPT_DIR%run_tests.bat" all
) else if "%1"=="test-comp" (
    echo Running component tests...
    call "%SCRIPT_DIR%run_tests.bat" components
) else if "%1"=="test-perf" (
    echo Running performance tests...
    call "%SCRIPT_DIR%run_tests.bat" performance
) else if "%1"=="test-ui" (
    echo Running UI tests...
    call "%SCRIPT_DIR%run_tests.bat" ui
) else if "%1"=="test-voice" (
    echo Running voice changer tests...
    call "%SCRIPT_DIR%run_tests.bat" voice
) else (
    echo Unknown option: %1
    echo Run without arguments to see available options.
)

echo.
echo Operation completed.
pause 