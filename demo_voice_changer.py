#!/usr/bin/env python3
"""
Voice Changer Demonstration Script
This script demonstrates the voice changer functionality of PlayaTewsIdentityMasker
"""

import sys
import os
import numpy as np
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_audio_effects():
    """Demonstrate various audio effects"""
    print("🎵 Voice Changer Audio Effects Demonstration")
    print("=" * 50)
    
    # Create a simple test signal (sine wave)
    sample_rate = 44100
    duration = 0.5  # 500ms
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    original_signal = np.sin(2 * np.pi * frequency * t)
    
    print(f"Original signal: {len(original_signal)} samples at {sample_rate}Hz")
    print(f"Frequency: {frequency}Hz (A4 note)")
    print(f"Duration: {duration}s")
    
    # Demonstrate different effects
    effects = [
        ("Pitch Shift (+4 semitones)", lambda x: np.interp(
            np.linspace(0, len(x), int(len(x) * 1.26)),  # 4 semitones up
            np.arange(len(x)), x
        )),
        ("Pitch Shift (-4 semitones)", lambda x: np.interp(
            np.linspace(0, len(x), int(len(x) * 0.79)),  # 4 semitones down
            np.arange(len(x)), x
        )),
        ("Robot Effect (AM)", lambda x: x * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t))),
        ("Echo Effect", lambda x: x + 0.3 * np.roll(x, int(0.1 * sample_rate))),
        ("Distortion", lambda x: np.tanh(x * 2)),
        ("Chorus Effect", lambda x: x + 0.3 * np.sin(2 * np.pi * 1.5 * t) * x)
    ]
    
    for effect_name, effect_func in effects:
        print(f"\n🎛️  {effect_name}")
        try:
            processed_signal = effect_func(original_signal)
            print(f"   ✓ Processed {len(processed_signal)} samples")
            
            # Calculate some basic statistics
            rms_original = np.sqrt(np.mean(original_signal**2))
            rms_processed = np.sqrt(np.mean(processed_signal**2))
            print(f"   ✓ RMS: {rms_original:.3f} → {rms_processed:.3f}")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")

def demo_voice_changer_features():
    """Demonstrate voice changer features"""
    print("\n🎤 Voice Changer Features")
    print("=" * 50)
    
    features = [
        "Real-time audio processing",
        "Multiple voice effects (10+ effects)",
        "Voice Activity Detection (VAD)",
        "Low latency (< 50ms)",
        "Professional audio quality",
        "Easy-to-use interface",
        "Quick presets for common effects",
        "Detailed parameter controls",
        "Audio device management",
        "Thread-safe processing"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature}")

def demo_effect_types():
    """Demonstrate available effect types"""
    print("\n🎭 Available Voice Effects")
    print("=" * 50)
    
    effects = [
        ("Pitch Shift", "Adjust voice pitch up or down by semitones"),
        ("Formant Shift", "Modify voice character without changing pitch"),
        ("Robot Effect", "Add amplitude modulation for robotic voice"),
        ("Helium Effect", "High-pitch voice effect"),
        ("Deep Voice", "Low-pitch voice effect"),
        ("Echo Effect", "Add delay and decay for echo"),
        ("Reverb Effect", "Simulate room acoustics"),
        ("Chorus Effect", "Add modulation for chorus effect"),
        ("Distortion Effect", "Add overdrive and clipping"),
        ("Autotune Effect", "Pitch correction and quantization")
    ]
    
    for i, (effect_name, description) in enumerate(effects, 1):
        print(f"{i:2d}. {effect_name:<15} - {description}")

def demo_usage_instructions():
    """Show usage instructions"""
    print("\n📖 Usage Instructions")
    print("=" * 50)
    
    instructions = [
        "1. Start the PlayaTewsIdentityMasker application",
        "2. Locate the Voice Changer panel in the UI",
        "3. Enable the Voice Changer by checking the checkbox",
        "4. Select an effect from the dropdown menu",
        "5. Adjust parameters in the Effects tab",
        "6. Choose input and output devices in the Devices tab",
        "7. Speak into your microphone to hear the effect",
        "8. Use quick presets for instant effect application"
    ]
    
    for instruction in instructions:
        print(f"   {instruction}")

def demo_technical_specs():
    """Show technical specifications"""
    print("\n⚙️  Technical Specifications")
    print("=" * 50)
    
    specs = [
        ("Sample Rate", "44.1 kHz"),
        ("Chunk Size", "1024 samples"),
        ("Channels", "Mono (1 channel)"),
        ("Latency", "< 50ms typical"),
        ("Processing", "Real-time"),
        ("Threading", "Multi-threaded"),
        ("VAD", "WebRTC Voice Activity Detection"),
        ("Audio I/O", "PyAudio"),
        ("Effects Engine", "Custom DSP algorithms"),
        ("UI Framework", "PyQt5")
    ]
    
    for spec_name, spec_value in specs:
        print(f"{spec_name:<20}: {spec_value}")

def main():
    """Main demonstration function"""
    print("🎤 PlayaTewsIdentityMasker Voice Changer Demo")
    print("=" * 60)
    print("This demonstration shows the voice changer functionality")
    print("that has been integrated into the PlayaTewsIdentityMasker application.")
    print()
    
    # Run demonstrations
    demo_audio_effects()
    demo_voice_changer_features()
    demo_effect_types()
    demo_usage_instructions()
    demo_technical_specs()
    
    print("\n" + "=" * 60)
    print("🎉 Voice Changer Demo Complete!")
    print("\nTo use the voice changer:")
    print("1. Ensure you have audio devices connected")
    print("2. Run: python main.py run PlayaTewsIdentityMasker")
    print("3. Enable the Voice Changer in the UI")
    print("4. Select effects and adjust parameters")
    print("5. Enjoy real-time voice modification!")
    
    print("\nFor more information, see:")
    print("- VOICE_CHANGER_STATUS.md - Implementation details")
    print("- test_voice_changer_simple.py - Testing script")
    print("- apps/PlayaTewsIdentityMasker/backend/VoiceChanger.py - Backend code")
    print("- apps/PlayaTewsIdentityMasker/ui/QVoiceChanger.py - UI code")

if __name__ == "__main__":
    main()