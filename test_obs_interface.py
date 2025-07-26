#!/usr/bin/env python3
"""
Test script for OBS-Style DeepFaceLive Interface

This script tests the major components of the OBS-style interface
without requiring a full application launch.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test core Qt imports
        from xlib import qt as qtx
        print("✓ Qt framework imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Qt framework: {e}")
        return False
    
    try:
        # Test streaming engine
        from apps.DeepFaceLive.streaming import (
            StreamingEngine, RecordingEngine, StreamConfig, StreamPlatform
        )
        print("✓ Streaming components imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import streaming components: {e}")
        return False
    
    try:
        # Test OBS-style app
        from apps.DeepFaceLive.OBSStyleApp import (
            QOBSSceneManager, QOBSStreamManager, QOBSMainPreview,
            QOBSStyleLiveSwap, OBSStyleDeepFaceLiveApp
        )
        print("✓ OBS-style interface components imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import OBS-style components: {e}")
        return False
    
    return True

def test_streaming_engine():
    """Test streaming engine functionality"""
    print("\nTesting streaming engine...")
    
    try:
        from apps.DeepFaceLive.streaming import (
            StreamingEngine, StreamConfig, StreamPlatform, validate_stream_config
        )
        
        # Create streaming engine
        engine = StreamingEngine()
        print("✓ StreamingEngine created successfully")
        
        # Test configuration validation
        config = StreamConfig(
            platform=StreamPlatform.TWITCH,
            stream_key="test_key_123",
            server_url="rtmp://live.twitch.tv/live",
            bitrate=3500
        )
        
        errors = validate_stream_config(config)
        if not errors:
            print("✓ Stream configuration validation passed")
        else:
            print(f"✗ Stream configuration validation failed: {errors}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Streaming engine test failed: {e}")
        return False

def test_recording_engine():
    """Test recording engine functionality"""
    print("\nTesting recording engine...")
    
    try:
        from apps.DeepFaceLive.streaming import RecordingEngine
        
        # Create recording engine
        engine = RecordingEngine()
        print("✓ RecordingEngine created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Recording engine test failed: {e}")
        return False

def test_scene_management():
    """Test scene management components"""
    print("\nTesting scene management...")
    
    try:
        from apps.DeepFaceLive.OBSStyleApp import Scene
        
        # Create test scene
        scene = Scene(name="Test Scene", sources=[])
        print("✓ Scene creation successful")
        
        # Test scene properties
        if scene.name == "Test Scene" and scene.sources == [] and not scene.active:
            print("✓ Scene properties correct")
        else:
            print("✗ Scene properties incorrect")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Scene management test failed: {e}")
        return False

def test_platform_configs():
    """Test platform-specific configurations"""
    print("\nTesting platform configurations...")
    
    try:
        from apps.DeepFaceLive.streaming import (
            StreamPlatform, get_platform_config, PLATFORM_CONFIGS
        )
        
        # Test all platforms have configs
        for platform in StreamPlatform:
            config = get_platform_config(platform)
            if platform in PLATFORM_CONFIGS:
                if 'name' in config and 'max_bitrate' in config:
                    print(f"✓ {platform.value} configuration valid")
                else:
                    print(f"✗ {platform.value} configuration incomplete")
                    return False
            else:
                print(f"⚠ {platform.value} has no predefined configuration (OK for custom)")
                
        return True
        
    except Exception as e:
        print(f"✗ Platform configuration test failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")
    
    dependencies = {
        'numpy': 'numpy',
        'opencv': 'cv2', 
        'PyQt5': 'PyQt5',
        'threading': 'threading',
        'subprocess': 'subprocess',
        'pathlib': 'pathlib',
        'json': 'json',
        'time': 'time',
        'queue': 'queue'
    }
    
    missing_deps = []
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} available")
        except ImportError:
            print(f"✗ {name} missing")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install -r requirements_minimal.txt")
        return False
    
    return True

def check_ffmpeg():
    """Check if FFmpeg is available"""
    print("\nChecking FFmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✓ FFmpeg available: {version_line}")
            return True
        else:
            print("✗ FFmpeg command failed")
            return False
    except FileNotFoundError:
        print("✗ FFmpeg not found in PATH")
        print("Install FFmpeg for streaming/recording functionality")
        return False
    except subprocess.TimeoutExpired:
        print("✗ FFmpeg command timed out")
        return False

def main():
    """Run all tests"""
    print("OBS-Style DeepFaceLive Interface Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Streaming Engine", test_streaming_engine),
        ("Recording Engine", test_recording_engine),
        ("Scene Management", test_scene_management),
        ("Platform Configs", test_platform_configs)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
    
    # Optional FFmpeg check
    ffmpeg_available = check_ffmpeg()
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} core tests passed")
    
    if ffmpeg_available:
        print("✓ FFmpeg available for streaming/recording")
    else:
        print("⚠ FFmpeg not available (streaming/recording disabled)")
    
    if passed == total:
        print("\n🎉 All core tests passed! OBS-style interface should work correctly.")
        if ffmpeg_available:
            print("🚀 Ready for streaming and recording!")
        else:
            print("⚠ Install FFmpeg for full functionality")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed. Please fix issues before using the interface.")
        return 1

if __name__ == "__main__":
    sys.exit(main())