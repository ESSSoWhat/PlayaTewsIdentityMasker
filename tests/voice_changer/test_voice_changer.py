#!/usr/bin/env python3
"""
Test script for the voice changer functionality
"""

import sys
import os
import time
import numpy as np
import pyaudio
import threading
import queue

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_audio_devices():
    """Test if audio devices are available"""
    print("Testing audio devices...")
    
    try:
        audio = pyaudio.PyAudio()
        
        print(f"Found {audio.get_device_count()} audio devices:")
        
        input_devices = []
        output_devices = []
        
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            print(f"  Device {i}: {device_info['name']}")
            print(f"    Max Input Channels: {device_info['maxInputChannels']}")
            print(f"    Max Output Channels: {device_info['maxOutputChannels']}")
            
            if device_info['maxInputChannels'] > 0:
                input_devices.append((i, device_info['name']))
            if device_info['maxOutputChannels'] > 0:
                output_devices.append((i, device_info['name']))
        
        print(f"\nInput devices: {len(input_devices)}")
        for idx, name in input_devices:
            print(f"  {idx}: {name}")
        
        print(f"\nOutput devices: {len(output_devices)}")
        for idx, name in output_devices:
            print(f"  {idx}: {name}")
        
        audio.terminate()
        return len(input_devices) > 0 and len(output_devices) > 0
        
    except Exception as e:
        print(f"Error testing audio devices: {e}")
        return False

def test_audio_processing():
    """Test basic audio processing"""
    print("\nTesting audio processing...")
    
    try:
        # Test numpy audio operations
        sample_rate = 44100
        duration = 1.0  # seconds
        frequency = 440.0  # Hz (A note)
        
        # Generate a test tone
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        print(f"Generated {len(audio_data)} samples at {sample_rate} Hz")
        print(f"Audio data shape: {audio_data.shape}")
        print(f"Audio data type: {audio_data.dtype}")
        print(f"Audio data range: {audio_data.min():.3f} to {audio_data.max():.3f}")
        
        # Test basic effects
        # Pitch shift (simple resampling)
        ratio = 2 ** (4 / 12)  # 4 semitones up
        shifted = np.interp(np.arange(0, len(audio_data) * ratio, ratio),
                           np.arange(len(audio_data)), audio_data)
        shifted = shifted[:len(audio_data)]
        
        print(f"Pitch shifted audio shape: {shifted.shape}")
        
        # Echo effect
        delay_samples = int(0.3 * sample_rate)  # 300ms delay
        echo = np.zeros_like(audio_data)
        echo[delay_samples:] = audio_data[:-delay_samples] * 0.5
        echo_audio = audio_data + echo
        
        print(f"Echo audio shape: {echo_audio.shape}")
        
        return True
        
    except Exception as e:
        print(f"Error testing audio processing: {e}")
        return False

def test_voice_changer_import():
    """Test if the voice changer module can be imported"""
    print("\nTesting voice changer import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger, VoiceEffectType
        print("✓ VoiceChanger module imported successfully")
        
        # Test enum values
        print(f"Available effects: {[e.name for e in VoiceEffectType]}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import VoiceChanger: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing voice changer import: {e}")
        return False

def test_ui_import():
    """Test if the voice changer UI can be imported"""
    print("\nTesting voice changer UI import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QVoiceChanger import QVoiceChanger
        print("✓ QVoiceChanger UI module imported successfully")
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import QVoiceChanger: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing voice changer UI import: {e}")
        return False

def main():
    """Run all tests"""
    print("Voice Changer Test Suite")
    print("=" * 50)
    
    tests = [
        ("Audio Devices", test_audio_devices),
        ("Audio Processing", test_audio_processing),
        ("Voice Changer Import", test_voice_changer_import),
        ("Voice Changer UI Import", test_ui_import),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✓ {test_name} passed")
            else:
                print(f"✗ {test_name} failed")
                
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Voice changer should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())