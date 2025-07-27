#!/usr/bin/env python3
"""
Test Voice Changer Dependencies
Quick test to identify what's working and what's not
"""

import sys
import subprocess
from pathlib import Path

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"   Error importing {module_name}: {e}")
        return False

def test_voice_changer_dependencies():
    """Test voice changer dependencies"""
    print("🧪 Testing Voice Changer Dependencies")
    print("=" * 40)
    
    # Core dependencies
    core_deps = [
        "uvicorn", "fastapi", "websockets", "numpy", "scipy"
    ]
    
    print("Core Dependencies:")
    for dep in core_deps:
        if test_import(dep):
            print(f"   ✅ {dep}")
        else:
            print(f"   ❌ {dep}")
    
    # PyTorch dependencies
    print("\nPyTorch Dependencies:")
    torch_deps = ["torch", "torchaudio"]
    for dep in torch_deps:
        if test_import(dep):
            print(f"   ✅ {dep}")
        else:
            print(f"   ❌ {dep}")
    
    # Audio dependencies
    print("\nAudio Dependencies:")
    audio_deps = ["librosa", "sounddevice", "resampy"]
    for dep in audio_deps:
        if test_import(dep):
            print(f"   ✅ {dep}")
        else:
            print(f"   ❌ {dep}")
    
    # ML dependencies
    print("\nML Dependencies:")
    ml_deps = ["onnxruntime", "faiss", "torchcrepe"]
    for dep in ml_deps:
        if test_import(dep):
            print(f"   ✅ {dep}")
        else:
            print(f"   ❌ {dep}")

def test_voice_changer_server():
    """Test if voice changer server can start"""
    print("\n🔧 Testing Voice Changer Server")
    print("=" * 40)
    
    server_dir = Path("voice-changer/server")
    if not server_dir.exists():
        print("❌ Server directory not found")
        return False
    
    # Check if MMVCServerSIO.py exists
    server_file = server_dir / "MMVCServerSIO.py"
    if not server_file.exists():
        print("❌ MMVCServerSIO.py not found")
        return False
    
    print("✅ Server files found")
    
    # Try to import the server module
    try:
        import sys
        sys.path.insert(0, str(server_dir))
        
        # Try to import just the basic structure
        with open(server_file, 'r') as f:
            content = f.read()
        
        if "class MMVCServerSIO" in content:
            print("✅ Server class found in file")
        else:
            print("❌ Server class not found in file")
            
        if "if __name__ == '__main__'" in content:
            print("✅ Main entry point found")
        else:
            print("❌ Main entry point not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error reading server file: {e}")
        return False

def create_minimal_startup_script():
    """Create a minimal startup script"""
    print("\n📝 Creating Minimal Startup Script")
    print("=" * 40)
    
    minimal_script = '''@echo off
echo Voice Changer - Minimal Startup
echo ================================

cd voice-changer\\server

echo Installing minimal dependencies...
python -m pip install uvicorn fastapi websockets numpy scipy

echo.
echo Testing server startup...
python -c "import MMVCServerSIO; print('Server module loaded successfully')"

echo.
echo If the test passed, starting server...
python MMVCServerSIO.py

pause
'''
    
    script_path = Path("start_voice_changer_minimal.bat")
    with open(script_path, 'w') as f:
        f.write(minimal_script)
    
    print(f"✅ Created: {script_path}")
    return script_path

def main():
    """Main function"""
    print("🎯 Voice Changer Dependency Test")
    print("=" * 50)
    
    # Test dependencies
    test_voice_changer_dependencies()
    
    # Test server
    server_ok = test_voice_changer_server()
    
    # Create minimal startup script
    minimal_script = create_minimal_startup_script()
    
    print("\n" + "=" * 50)
    print("🎉 Dependency Test Complete!")
    print("\nRecommendations:")
    
    if server_ok:
        print("✅ Server files look good")
        print("Try running: start_voice_changer_minimal.bat")
    else:
        print("❌ Server files have issues")
        print("Check the voice-changer installation")
    
    print("\nIf you see missing dependencies:")
    print("1. Run: python -m pip install <missing_package>")
    print("2. For PyTorch issues, try:")
    print("   python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu")
    print("3. For audio issues, try:")
    print("   python -m pip install librosa sounddevice")

if __name__ == "__main__":
    main() 