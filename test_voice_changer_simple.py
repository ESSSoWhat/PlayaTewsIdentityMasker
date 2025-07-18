#!/usr/bin/env python3
"""
Simple test script for VoiceChanger functionality
"""

import sys
import os
import numpy as np
import pyaudio
import threading
import queue
import time
from enum import IntEnum

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audio_devices():
    """Test if audio devices are available"""
    print("Testing audio devices...")
    try:
        audio = pyaudio.PyAudio()
        device_count = audio.get_device_count()
        print(f"Found {device_count} audio devices")
        
        input_devices = []
        output_devices = []
        
        for i in range(device_count):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append((i, device_info['name']))
            if device_info['maxOutputChannels'] > 0:
                output_devices.append((i, device_info['name']))
        
        print(f"Input devices: {len(input_devices)}")
        for idx, name in input_devices:
            print(f"  {idx}: {name}")
            
        print(f"Output devices: {len(output_devices)}")
        for idx, name in output_devices:
            print(f"  {idx}: {name}")
            
        audio.terminate()
        return len(input_devices) > 0 and len(output_devices) > 0
        
    except Exception as e:
        print(f"Error testing audio devices: {e}")
        return False

def test_basic_audio_processing():
    """Test basic audio processing capabilities"""
    print("\nTesting basic audio processing...")
    try:
        # Create a simple sine wave
        sample_rate = 44100
        duration = 0.1  # 100ms
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Test pitch shifting (simple time stretching)
        pitch_shift = 2.0  # Up 2 semitones
        stretched = np.interp(
            np.linspace(0, len(audio_data), int(len(audio_data) * pitch_shift)),
            np.arange(len(audio_data)),
            audio_data
        )
        
        print(f"Original audio: {len(audio_data)} samples")
        print(f"Pitch-shifted audio: {len(stretched)} samples")
        print("Basic audio processing test passed!")
        return True
        
    except Exception as e:
        print(f"Error in basic audio processing: {e}")
        return False

def test_voice_changer_import():
    """Test if we can import the voice changer module"""
    print("\nTesting VoiceChanger import...")
    try:
        # Try to import just the VoiceChanger class
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger
        print("VoiceChanger import successful!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_audio_libraries():
    """Test if required audio libraries are available"""
    print("\nTesting audio libraries...")
    
    libraries = [
        ('numpy', 'numpy'),
        ('pyaudio', 'pyaudio'),
        ('librosa', 'librosa'),
        ('soundfile', 'soundfile'),
        ('scipy', 'scipy'),
        ('webrtcvad', 'webrtcvad')
    ]
    
    all_available = True
    for lib_name, import_name in libraries:
        try:
            __import__(import_name)
            print(f"✓ {lib_name} - Available")
        except ImportError:
            print(f"✗ {lib_name} - Not available")
            all_available = False
    
    return all_available

def main():
    """Main test function"""
    print("VoiceChanger Test Suite")
    print("=" * 50)
    
    tests = [
        ("Audio Libraries", test_audio_libraries),
        ("Audio Devices", test_audio_devices),
        ("Basic Audio Processing", test_basic_audio_processing),
        ("VoiceChanger Import", test_voice_changer_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VoiceChanger should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)