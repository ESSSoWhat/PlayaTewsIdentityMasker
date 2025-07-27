@echo off
echo ========================================
echo PlayaTews Identity Masker Test Runner
echo ========================================

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

cd /d "%PROJECT_ROOT%"

if "%1"=="" (
    echo Usage: run_tests.bat [option]
    echo.
    echo Options:
    echo   all          - Run all tests
    echo   components   - Run component tests
    echo   performance  - Run performance tests
    echo   ui           - Run UI tests
    echo   voice        - Run voice changer tests
    echo   list         - List available test categories
    echo   coverage     - Run all tests with coverage
    echo   verbose      - Run all tests with verbose output
    echo.
    echo Examples:
    echo   run_tests.bat all
    echo   run_tests.bat components
    echo   run_tests.bat performance --verbose
    goto :eof
)

if "%1"=="all" (
    echo Running all tests...
    python scripts/run_tests.py --all
) else if "%1"=="components" (
    echo Running component tests...
    python scripts/run_tests.py --category components
) else if "%1"=="performance" (
    echo Running performance tests...
    python scripts/run_tests.py --category performance
) else if "%1"=="ui" (
    echo Running UI tests...
    python scripts/run_tests.py --category ui
) else if "%1"=="voice" (
    echo Running voice changer tests...
    python scripts/run_tests.py --category voice_changer
) else if "%1"=="list" (
    echo Listing test categories...
    python scripts/run_tests.py --list
) else if "%1"=="coverage" (
    echo Running all tests with coverage...
    python scripts/run_tests.py --all --coverage
) else if "%1"=="verbose" (
    echo Running all tests with verbose output...
    python scripts/run_tests.py --all --verbose
) else (
    echo Unknown option: %1
    echo Run without arguments to see available options.
)

echo.
echo Test execution completed.
pause 