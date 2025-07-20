@echo off
echo Setting up PlayaTewsIdentityMasker to use local Python311 directory...

REM Set environment variables to use local Python311
set PYTHONPATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\site-packages;%PYTHONPATH%
set PATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\Scripts;%PATH%

REM Create a local pip configuration to install to the local directory
echo Creating pip configuration for local installation...
if not exist "Python311\pip.conf" (
    echo [global] > Python311\pip.conf
    echo target = C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\site-packages >> Python311\pip.conf
)

REM Install any missing dependencies to the local directory
echo Installing dependencies to local Python311 directory...
Python311\Scripts\pip.exe install --target=Python311\site-packages -r requirements_minimal.txt

echo.
echo Environment setup complete!
echo.
echo To run the application with local Python dependencies:
echo   python run_obs_style.py
echo.
echo Or use the local pip for future installations:
echo   Python311\Scripts\pip.exe install --target=Python311\site-packages package_name
echo.
pause 