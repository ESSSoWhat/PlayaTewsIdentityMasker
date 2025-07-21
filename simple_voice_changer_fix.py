#!/usr/bin/env python3
"""
Simple Voice Changer Fix
Simple solution to get voice changer running after killing all instances
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_voice_changer_status():
    """Check voice changer status"""
    print("🔍 Checking voice changer status...")
    
    # Check if voice-changer directory exists
    voice_changer_dir = Path("voice-changer")
    if not voice_changer_dir.exists():
        print("❌ Voice-changer directory not found")
        return False
    
    server_dir = voice_changer_dir / "server"
    if not server_dir.exists():
        print("❌ Server directory not found")
        return False
    
    # Check key files
    key_files = [
        server_dir / "MMVCServerSIO.py",
        server_dir / "requirements.txt",
        server_dir / "const.py"
    ]
    
    for file_path in key_files:
        if not file_path.exists():
            print(f"❌ Missing file: {file_path}")
            return False
    
    print("✅ Voice changer files found")
    return True

def clean_temporary_files():
    """Clean temporary files"""
    print("🧹 Cleaning temporary files...")
    
    voice_changer_dir = Path("voice-changer")
    
    # Clean tmp directory
    tmp_dir = voice_changer_dir / "tmp_dir"
    if tmp_dir.exists():
        try:
            for file in tmp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    print(f"   Deleted: {file.name}")
        except Exception as e:
            print(f"   Error cleaning tmp_dir: {e}")
    
    # Clean logs
    logs_dir = voice_changer_dir / "logs"
    if logs_dir.exists():
        try:
            for file in logs_dir.glob("*.log"):
                if file.stat().st_size > 5 * 1024 * 1024:  # Larger than 5MB
                    file.unlink()
                    print(f"   Deleted large log: {file.name}")
        except Exception as e:
            print(f"   Error cleaning logs: {e}")

def check_ports():
    """Check port availability"""
    print("🌐 Checking ports...")
    
    ports = [8080, 8081, 8082, 8083]
    
    for port in ports:
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            if str(port) in result.stdout:
                print(f"   Port {port}: IN USE")
            else:
                print(f"   Port {port}: AVAILABLE")
        except Exception as e:
            print(f"   Port {port}: ERROR - {e}")

def create_startup_script():
    """Create a startup script"""
    print("📝 Creating startup script...")
    
    startup_script = '''@echo off
echo ========================================
echo Voice Changer Server Startup
echo ========================================

cd voice-changer\\server

echo Installing requirements...
python -m pip install -r requirements.txt

echo Starting server...
python MMVCServerSIO.py

pause
'''
    
    script_path = Path("start_voice_changer.bat")
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    print(f"✅ Created: {script_path}")
    return script_path

def create_alternative_startup_script():
    """Create an alternative startup script with error handling"""
    print("📝 Creating alternative startup script...")
    
    alt_script = '''@echo off
echo ========================================
echo Voice Changer Server (Alternative)
echo ========================================

cd voice-changer\\server

echo Checking Python...
python --version

echo Installing requirements...
python -m pip install -r requirements.txt

echo Checking for MMVCServerSIO.py...
if exist MMVCServerSIO.py (
    echo Starting server...
    python MMVCServerSIO.py
) else (
    echo ERROR: MMVCServerSIO.py not found
    echo Please check the voice-changer installation
)

pause
'''
    
    script_path = Path("start_voice_changer_alt.bat")
    with open(script_path, 'w') as f:
        f.write(alt_script)
    
    print(f"✅ Created: {script_path}")
    return script_path

def create_manual_startup_guide():
    """Create a manual startup guide"""
    print("📄 Creating manual startup guide...")
    
    guide = """# Voice Changer Manual Startup Guide

## Quick Start
1. Open Command Prompt as Administrator
2. Navigate to your project directory
3. Run: `start_voice_changer.bat`

## Manual Steps (if batch file doesn't work)

### Step 1: Navigate to Server Directory
```cmd
cd voice-changer\\server
```

### Step 2: Install Requirements
```cmd
python -m pip install -r requirements.txt
```

### Step 3: Start Server
```cmd
python MMVCServerSIO.py
```

### Step 4: Access Web Interface
Open your browser and go to:
- http://localhost:8080
- http://localhost:8081 (alternative port)

## Troubleshooting

### If you get import errors:
1. Make sure you're in the correct directory
2. Try: `python -m pip install --upgrade pip`
3. Try: `python -m pip install -r requirements.txt --force-reinstall`

### If ports are in use:
1. Check what's using the ports: `netstat -ano | findstr :8080`
2. Kill the process or use a different port

### If server won't start:
1. Check the error messages
2. Look for missing dependencies
3. Try running as Administrator

## Common Issues

### Torch/TorchAudio Issues
If you get torch-related errors:
1. Try: `python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu`
2. Or: `python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Port Already in Use
If port 8080 is in use:
1. Find the process: `netstat -ano | findstr :8080`
2. Kill it: `taskkill /PID <PID> /F`
3. Or modify the server to use a different port

### Permission Issues
If you get permission errors:
1. Run Command Prompt as Administrator
2. Check file permissions
3. Make sure antivirus isn't blocking the application

## Support
- Check voice-changer/README.md for documentation
- Look for error messages in the console
- Check voice-changer/logs/ for log files
"""
    
    guide_path = Path("VOICE_CHANGER_MANUAL_GUIDE.md")
    with open(guide_path, 'w') as f:
        f.write(guide)
    
    print(f"✅ Created: {guide_path}")
    return guide_path

def test_voice_changer_startup():
    """Test if voice changer can start"""
    print("🧪 Testing voice changer startup...")
    
    server_dir = Path("voice-changer/server")
    if not server_dir.exists():
        print("❌ Server directory not found")
        return False
    
    try:
        # Change to server directory
        original_dir = os.getcwd()
        os.chdir(server_dir)
        
        # Test if MMVCServerSIO.py can be imported
        print("   Testing import...")
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.append('.'); import MMVCServerSIO; print('Import successful')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Import test passed")
            os.chdir(original_dir)
            return True
        else:
            print(f"   ❌ Import test failed: {result.stderr}")
            os.chdir(original_dir)
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ Import test timed out")
        os.chdir(original_dir)
        return False
    except Exception as e:
        print(f"   ❌ Import test error: {e}")
        os.chdir(original_dir)
        return False

def main():
    """Main function"""
    print("🎯 Voice Changer Fix")
    print("=" * 40)
    
    # Step 1: Check status
    if not check_voice_changer_status():
        print("\n❌ Voice changer installation incomplete")
        print("Please ensure voice-changer directory exists with all required files")
        return
    
    # Step 2: Clean files
    clean_temporary_files()
    
    # Step 3: Check ports
    check_ports()
    
    # Step 4: Create startup scripts
    startup_script = create_startup_script()
    alt_script = create_alternative_startup_script()
    
    # Step 5: Create manual guide
    manual_guide = create_manual_startup_guide()
    
    # Step 6: Test startup
    test_result = test_voice_changer_startup()
    
    print("\n" + "=" * 40)
    print("🎉 Voice Changer Fix Complete!")
    print("\nNext Steps:")
    print("1. Run the startup script:")
    print(f"   {startup_script}")
    print("\n2. If that doesn't work, try the alternative:")
    print(f"   {alt_script}")
    print("\n3. For manual steps, check:")
    print(f"   {manual_guide}")
    
    if test_result:
        print("\n✅ Voice changer should start successfully")
        print("Open http://localhost:8080 in your browser")
    else:
        print("\n⚠️ Voice changer may have dependency issues")
        print("Check the manual guide for troubleshooting steps")
    
    print("\nIf you encounter issues:")
    print("- Run Command Prompt as Administrator")
    print("- Check for error messages in the console")
    print("- Ensure no other applications are using ports 8080-8083")
    print("- Try the manual startup steps in the guide")

if __name__ == "__main__":
    main() 