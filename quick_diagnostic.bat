@echo off
echo ========================================
echo PlayaTews Identity Masker - Quick Diagnostic
echo ========================================
echo.

echo 🔍 Running systematic UI analysis...
python systematic_ui_analysis.py

echo.
echo ========================================
echo 🚀 Launching app with comprehensive fixes...
echo ========================================
echo.

python final_app_launcher.py

echo.
echo Diagnostic and launch complete.
pause 