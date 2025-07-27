@echo off
echo Starting PlayaTewsIdentityMasker with Local Python Environment...
echo.

REM Set environment variables for local Python
set PYTHONPATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\site-packages;%PYTHONPATH%
set PATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\Scripts;%PATH%

echo Environment configured for local Python311 directory.
echo.

REM Start the application
python run_with_local_python.py

pause 