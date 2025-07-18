#!/usr/bin/env python3
"""
PlayaTewsIdentityMasker Desktop Application Builder
Packages the application into standalone executables for Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """Create PyInstaller spec file for PlayaTewsIdentityMasker"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

block_cipher = None

# Collect all necessary data files
datas = [
    ('localization', 'localization'),
    ('resources', 'resources'),
    ('modelhub', 'modelhub'),
    ('xlib', 'xlib'),
    ('apps', 'apps'),
]

# Collect all necessary binaries
binaries = []

# Hidden imports for PyQt6 and ML libraries
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'onnxruntime',
    'torch',
    'torchvision',
    'cv2',
    'numpy',
    'psutil',
    'yaml',
    'asyncio',
    'xlib.appargs',
    'xlib.os',
    'xlib.qt',
                'apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp',
            'apps.PlayaTewsIdentityMasker.backend',
            'apps.PlayaTewsIdentityMasker.ui',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
 cursor/update-application-and-repository-name-ad7b
            name='PlayaTewsIdentityMasker',
=======
    name='PlayaTewsIdentityMasker',
 main
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
'''
    
    with open('PlayaTewsIdentityMasker.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created PlayaTewsIdentityMasker.spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building PlayaTewsIdentityMasker executable...")
    
    # Build command
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'PlayaTewsIdentityMasker.spec'
    ]
    
    subprocess.check_call(cmd)
    print("Build completed successfully!")

def create_installer_script():
    """Create installer scripts for different platforms"""
    
    # Windows NSIS installer script
    nsis_script = '''!include "MUI2.nsh"

Name "PlayaTewsIdentityMasker"
OutFile "PlayaTewsIdentityMasker-Setup.exe"
InstallDir "$PROGRAMFILES\\PlayaTewsIdentityMasker"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath "$INSTDIR"
    File /r "dist\\PlayaTewsIdentityMasker\\*.*"
 cursor/update-application-and-repository-name-ad7b

CreateDirectory "$SMPROGRAMS\\PlayaTewsIdentityMasker"
CreateShortCut "$SMPROGRAMS\\PlayaTewsIdentityMasker\\PlayaTewsIdentityMasker.lnk" "$INSTDIR\\PlayaTewsIdentityMasker.exe"
CreateShortCut "$DESKTOP\\PlayaTewsIdentityMasker.lnk" "$INSTDIR\\PlayaTewsIdentityMasker.exe"
=======
    
    CreateDirectory "$SMPROGRAMS\\PlayaTewsIdentityMasker"
    CreateShortCut "$SMPROGRAMS\\PlayaTewsIdentityMasker\\PlayaTewsIdentityMasker.lnk" "$INSTDIR\\PlayaTewsIdentityMasker.exe"
    CreateShortCut "$DESKTOP\\PlayaTewsIdentityMasker.lnk" "$INSTDIR\\PlayaTewsIdentityMasker.exe"
 main
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PlayaTewsIdentityMasker" "DisplayName" "PlayaTewsIdentityMasker"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PlayaTewsIdentityMasker" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$SMPROGRAMS\\PlayaTewsIdentityMasker\\PlayaTewsIdentityMasker.lnk"
    Delete "$DESKTOP\\PlayaTewsIdentityMasker.lnk"
    RMDir "$SMPROGRAMS\\PlayaTewsIdentityMasker"
    RMDir /r "$INSTDIR"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\PlayaTewsIdentityMasker"
SectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    # Linux AppImage script
    appimage_script = '''#!/bin/bash
# AppImage build script for PlayaTewsIdentityMasker

# Create AppDir structure
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy executable and dependencies
cp -r dist/PlayaTewsIdentityMasker/* AppDir/usr/bin/

# Create desktop file
cat > AppDir/usr/share/applications/playatewsidentitymasker.desktop << EOF
[Desktop Entry]
Name=PlayaTewsIdentityMasker
Comment=Real-time face swapping application
Exec=playatewsidentitymasker
Icon=playatewsidentitymasker
Type=Application
Categories=Graphics;Video;
EOF

# Create AppRun script
cat > AppDir/AppRun << EOF
#!/bin/bash
cd "\$APPDIR/usr/bin"
exec "\$APPDIR/usr/bin/PlayaTewsIdentityMasker" "\$@"
EOF

chmod +x AppDir/AppRun

# Build AppImage (requires appimagetool)
if command -v appimagetool &> /dev/null; then
    appimagetool AppDir PlayaTewsIdentityMasker-x86_64.AppImage
else
    echo "appimagetool not found. Install it to create AppImage."
fi
'''
    
    with open('build_appimage.sh', 'w') as f:
        f.write(appimage_script)
    os.chmod('build_appimage.sh', 0o755)

def main():
    """Main build process"""
    print("PlayaTewsIdentityMasker Desktop Application Builder")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    build_executable()
    
    # Create installer scripts
    create_installer_script()
    
    print("\nBuild completed!")
    print("Executable location: dist/PlayaTewsIdentityMasker/")
    print("\nNext steps:")
    print("1. Test the executable: ./dist/PlayaTewsIdentityMasker/PlayaTewsIdentityMasker")
    print("2. Create installer (Windows): makensis installer.nsi")
    print("3. Create AppImage (Linux): ./build_appimage.sh")

if __name__ == "__main__":
    main()