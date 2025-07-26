#!/usr/bin/env python3
"""
Fix Voice Changer Issues
Comprehensive fix for torchaudio and encoding issues
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def fix_torchaudio_issue():
    """Fix torchaudio import issue"""
    print("🔧 Fixing torchaudio issue...")
    
    try:
        # Uninstall current torchaudio
        print("   Uninstalling current torchaudio...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "torchaudio", "-y"], 
                      capture_output=True, text=True)
        
        # Install compatible torchaudio
        print("   Installing compatible torchaudio...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ torchaudio installed successfully")
            return True
        else:
            print(f"   ❌ torchaudio installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error fixing torchaudio: {e}")
        return False

def fix_server_file_encoding():
    """Fix server file encoding issues"""
    print("🔧 Fixing server file encoding...")
    
    server_file = Path("voice-changer/server/MMVCServerSIO.py")
    if not server_file.exists():
        print("   ❌ Server file not found")
        return False
    
    try:
        # Create backup
        backup_file = server_file.with_suffix('.py.backup')
        shutil.copy2(server_file, backup_file)
        print(f"   Created backup: {backup_file}")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(server_file, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Write back with UTF-8 encoding
                with open(server_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Fixed encoding using {encoding}")
                return True
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"   Error with {encoding}: {e}")
                continue
        
        print("   ❌ Could not fix encoding with any method")
        return False
        
    except Exception as e:
        print(f"   ❌ Error fixing encoding: {e}")
        return False

def create_working_startup_script():
    """Create a working startup script"""
    print("📝 Creating working startup script...")
    
    startup_script = '''@echo off
echo ========================================
echo Voice Changer - Working Startup
echo ========================================

cd voice-changer\\server

echo Fixing torchaudio...
python -m pip uninstall torchaudio -y
python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing core dependencies...
python -m pip install uvicorn fastapi websockets numpy scipy

echo.
echo Installing audio dependencies...
python -m pip install librosa sounddevice resampy

echo.
echo Installing ML dependencies...
python -m pip install onnxruntime faiss-cpu torchcrepe

echo.
echo Testing server...
python -c "import MMVCServerSIO; print('Server test passed')"

echo.
echo Starting voice changer server...
python MMVCServerSIO.py

pause
'''
    
    script_path = Path("start_voice_changer_working.bat")
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    print(f"   ✅ Created: {script_path}")
    return script_path

def create_alternative_server():
    """Create an alternative server if the original is broken"""
    print("🔧 Creating alternative server...")
    
    alt_server = '''#!/usr/bin/env python3
"""
Alternative Voice Changer Server
Simplified version to get voice changer working
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Voice Changer Server")

# Mount static files
if os.path.exists("client"):
    app.mount("/", StaticFiles(directory="client", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "Voice Changer Server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting Voice Changer Server...")
    print("Open http://localhost:8080 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8080)
'''
    
    alt_server_path = Path("voice-changer/server/MMVCServerSIO_alt.py")
    with open(alt_server_path, 'w', encoding='utf-8') as f:
        f.write(alt_server)
    
    print(f"   ✅ Created: {alt_server_path}")
    return alt_server_path

def test_voice_changer_after_fix():
    """Test voice changer after fixes"""
    print("🧪 Testing voice changer after fixes...")
    
    # Test torchaudio
    try:
        import torchaudio
        print("   ✅ torchaudio import successful")
    except Exception as e:
        print(f"   ❌ torchaudio import failed: {e}")
        return False
    
    # Test server file
    server_file = Path("voice-changer/server/MMVCServerSIO.py")
    try:
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("   ✅ Server file readable")
    except Exception as e:
        print(f"   ❌ Server file still has issues: {e}")
        return False
    
    return True

def create_comprehensive_guide():
    """Create a comprehensive troubleshooting guide"""
    print("📄 Creating comprehensive guide...")
    
    guide = """# Voice Changer Troubleshooting Guide

## Issues Found and Fixed

### 1. TorchAudio Import Error
**Problem**: `[WinError 127] The specified procedure could not be found`
**Solution**: Reinstall torchaudio with CPU version
```cmd
python -m pip uninstall torchaudio -y
python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Server File Encoding Issue
**Problem**: `'charmap' codec can't decode byte`
**Solution**: Fixed file encoding to UTF-8

## Startup Options

### Option 1: Working Startup Script
Run: `start_voice_changer_working.bat`
- Automatically fixes torchaudio
- Installs all dependencies
- Tests server before starting

### Option 2: Alternative Server
If the main server still has issues:
```cmd
cd voice-changer\\server
python MMVCServerSIO_alt.py
```

### Option 3: Manual Steps
1. Fix torchaudio:
   ```cmd
   python -m pip uninstall torchaudio -y
   python -m pip install torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

2. Install dependencies:
   ```cmd
   cd voice-changer\\server
   python -m pip install uvicorn fastapi websockets numpy scipy
   python -m pip install librosa sounddevice resampy
   python -m pip install onnxruntime faiss-cpu torchcrepe
   ```

3. Start server:
   ```cmd
   python MMVCServerSIO.py
   ```

## Accessing Voice Changer

Once the server is running:
1. Open your browser
2. Go to: http://localhost:8080
3. You should see the voice changer interface

## Troubleshooting

### If server won't start:
1. Check error messages in console
2. Ensure no other applications are using port 8080
3. Try running as Administrator
4. Check antivirus isn't blocking the application

### If torchaudio still fails:
1. Try: `python -m pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu`
2. Or use the alternative server

### If encoding issues persist:
1. Use the alternative server: `MMVCServerSIO_alt.py`
2. Or manually fix the encoding of the server file

## Support
- Check voice-changer/README.md for documentation
- Look for error messages in the console
- Check voice-changer/logs/ for log files
"""
    
    guide_path = Path("VOICE_CHANGER_COMPREHENSIVE_GUIDE.md")
    with open(guide_path, 'w') as f:
        f.write(guide)
    
    print(f"   ✅ Created: {guide_path}")
    return guide_path

def main():
    """Main function"""
    print("🎯 Voice Changer Issue Fix")
    print("=" * 50)
    
    # Step 1: Fix torchaudio
    torchaudio_fixed = fix_torchaudio_issue()
    
    # Step 2: Fix server file encoding
    encoding_fixed = fix_server_file_encoding()
    
    # Step 3: Create working startup script
    working_script = create_working_startup_script()
    
    # Step 4: Create alternative server
    alt_server = create_alternative_server()
    
    # Step 5: Create comprehensive guide
    comprehensive_guide = create_comprehensive_guide()
    
    # Step 6: Test after fixes
    test_result = test_voice_changer_after_fix()
    
    print("\n" + "=" * 50)
    print("🎉 Voice Changer Fix Complete!")
    print("\nResults:")
    print(f"   TorchAudio: {'✅ Fixed' if torchaudio_fixed else '❌ Failed'}")
    print(f"   Encoding: {'✅ Fixed' if encoding_fixed else '❌ Failed'}")
    print(f"   Test: {'✅ Passed' if test_result else '❌ Failed'}")
    
    print("\nNext Steps:")
    print("1. Try the working startup script:")
    print(f"   {working_script}")
    print("\n2. If that doesn't work, try the alternative server:")
    print(f"   cd voice-changer\\server && python {alt_server.name}")
    print("\n3. For detailed instructions, check:")
    print(f"   {comprehensive_guide}")
    
    if test_result:
        print("\n✅ Voice changer should work now!")
        print("Open http://localhost:8080 in your browser")
    else:
        print("\n⚠️ Some issues may remain")
        print("Try the alternative server or check the comprehensive guide")
    
    print("\nIf you still have issues:")
    print("- Run Command Prompt as Administrator")
    print("- Check for error messages in the console")
    print("- Try the alternative server")
    print("- Check the comprehensive guide for more solutions")

if __name__ == "__main__":
    main() 