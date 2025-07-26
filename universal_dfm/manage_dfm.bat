@echo off
echo Universal DFM Manager
echo ===================
echo.
echo Available commands:
echo   list - List all models
echo   add - Add a new model
echo   remove - Remove a model
echo   move - Move model between categories
echo   info - Get model information
echo.
echo Examples:
echo   manage_dfm.bat list
echo   manage_dfm.bat list --category prebuilt
echo   manage_dfm.bat add --model-path "path/to/model.dfm" --category custom
echo   manage_dfm.bat info --model-name "kevin_hart_model"
echo.
python dfm_manager.py %*
pause 