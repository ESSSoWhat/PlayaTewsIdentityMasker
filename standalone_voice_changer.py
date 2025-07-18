#!/usr/bin/env python3
"""
Standalone Voice Changer
A simplified voice changer that works without complex backend dependencies
"""

import numpy as np
import sys
import os

try:
    import librosa
    import soundfile as sf
    from scipy import signal
    AUDIO_LIBS_AVAILABLE = True
except ImportError as e:
    print(f"Audio libraries not available: {e}")
    AUDIO_LIBS_AVAILABLE = False

class StandaloneVoiceChanger:
    """Voice changer that works without backend dependencies"""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.chunk_size = 1024
        
        # Define available effects
        self.effects = {
            'none': self._no_effect,
            'pitch_up': self._pitch_up,
            'pitch_down': self._pitch_down,
            'echo': self._echo_effect,
            'robot': self._robot_effect,
            'deep': self._deep_voice,
            'helium': self._helium_voice,
            'whisper': self._whisper_effect,
            'distortion': self._distortion_effect,
            'reverb': self._reverb_effect
        }
        
        self.current_effect = 'none'
        
    def get_available_effects(self):
        """Get list of available effects"""
        return list(self.effects.keys())
    
    def set_effect(self, effect_name):
        """Set the current effect"""
        if effect_name in self.effects:
            self.current_effect = effect_name
            print(f"Effect set to: {effect_name}")
            return True
        else:
            print(f"Unknown effect: {effect_name}")
            print(f"Available effects: {', '.join(self.effects.keys())}")
            return False
    
    def _no_effect(self, audio):
        """No effect - return original audio"""
        return audio
    
    def _pitch_up(self, audio):
        """Pitch shift up by 2 semitones"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio * 0.8  # Simple volume reduction as fallback
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=2)
    
    def _pitch_down(self, audio):
        """Pitch shift down by 2 semitones"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio * 1.2  # Simple volume increase as fallback
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=-2)
    
    def _helium_voice(self, audio):
        """High-pitched helium voice effect"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio * 0.7
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=7)
    
    def _deep_voice(self, audio):
        """Low-pitched deep voice effect"""
        if not AUDIO_LIBS_AVAILABLE:
            return audio * 1.3
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=-5)
    
    def _echo_effect(self, audio):
        """Echo effect with delay and decay"""
        delay_samples = int(0.2 * self.sample_rate)  # 200ms delay
        decay = 0.4
        
        if len(audio) <= delay_samples:
            return audio
        
        echo = np.zeros_like(audio)
        echo[delay_samples:] = audio[:-delay_samples] * decay
        return audio + echo
    
    def _robot_effect(self, audio):
        """Robot voice effect using amplitude modulation"""
        t = np.linspace(0, len(audio) / self.sample_rate, len(audio))
        modulation = np.sin(2 * np.pi * 30 * t)  # 30 Hz modulation
        return audio * (0.5 + 0.5 * modulation)
    
    def _whisper_effect(self, audio):
        """Whisper effect using high-frequency emphasis"""
        # Simple high-pass filter for whisper effect
        if len(audio) < 100:
            return audio * 0.3
            
        # Create a simple high-pass filter
        filtered = np.copy(audio)
        for i in range(1, len(filtered)):
            filtered[i] = audio[i] - 0.8 * audio[i-1]
        
        return filtered * 0.5
    
    def _distortion_effect(self, audio):
        """Distortion effect using soft clipping"""
        # Soft clipping distortion
        drive = 3.0
        return np.tanh(audio * drive) / drive
    
    def _reverb_effect(self, audio):
        """Simple reverb effect using multiple delayed copies"""
        # Create multiple delayed and decayed copies
        reverb = np.copy(audio)
        
        delays = [0.05, 0.1, 0.15, 0.25]  # Different delay times in seconds
        decays = [0.3, 0.2, 0.15, 0.1]   # Corresponding decay amounts
        
        for delay_time, decay in zip(delays, decays):
            delay_samples = int(delay_time * self.sample_rate)
            if delay_samples < len(audio):
                delayed = np.zeros_like(audio)
                delayed[delay_samples:] = audio[:-delay_samples] * decay
                reverb += delayed
        
        return reverb * 0.7  # Reduce overall volume
    
    def process_audio(self, audio_data):
        """Process audio with current effect"""
        try:
            effect_func = self.effects[self.current_effect]
            return effect_func(audio_data)
        except Exception as e:
            print(f"Error processing audio with effect '{self.current_effect}': {e}")
            return audio_data
    
    def process_file(self, input_file, output_file=None, effect=None):
        """Process an audio file with specified effect"""
        if not AUDIO_LIBS_AVAILABLE:
            print("Cannot process files: audio libraries not available")
            return False
        
        try:
            # Load audio file
            audio, sr = librosa.load(input_file, sr=self.sample_rate)
            print(f"Loaded {input_file}: {len(audio)} samples at {sr} Hz")
            
            # Set effect if specified
            if effect:
                self.set_effect(effect)
            
            # Process audio
            processed = self.process_audio(audio)
            
            # Save processed audio
            if output_file is None:
                name, ext = os.path.splitext(input_file)
                output_file = f"{name}_{self.current_effect}{ext}"
            
            sf.write(output_file, processed, sr)
            print(f"Saved processed audio to: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return False
    
    def generate_test_audio(self, duration=2.0, frequency=440.0):
        """Generate test audio for demonstration"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Generate a more interesting test signal (combination of tones)
        audio = (np.sin(2 * np.pi * frequency * t) * 0.5 +
                np.sin(2 * np.pi * frequency * 1.5 * t) * 0.3 +
                np.sin(2 * np.pi * frequency * 2 * t) * 0.2)
        
        # Add some envelope to make it sound more natural
        envelope = np.exp(-t * 0.5) * (1 - np.exp(-t * 10))
        audio *= envelope
        
        return audio
    
    def test_all_effects(self):
        """Test all effects with generated audio"""
        print("Testing Standalone Voice Changer")
        print("=" * 40)
        
        # Generate test audio
        test_audio = self.generate_test_audio(duration=1.0)
        print(f"Generated test audio: {len(test_audio)} samples")
        
        # Test each effect
        for effect_name in self.effects.keys():
            print(f"\nTesting effect: {effect_name}")
            self.set_effect(effect_name)
            
            try:
                processed = self.process_audio(test_audio.copy())
                print(f"  ✓ Processed {len(processed)} samples")
                
                # Basic validation
                if len(processed) != len(test_audio):
                    print(f"  ⚠️  Warning: Length changed from {len(test_audio)} to {len(processed)}")
                
                if np.isnan(processed).any():
                    print(f"  ❌ Error: NaN values in output")
                elif np.isinf(processed).any():
                    print(f"  ❌ Error: Infinite values in output")
                else:
                    rms = np.sqrt(np.mean(processed**2))
                    print(f"  ✓ RMS level: {rms:.4f}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print("\n" + "=" * 40)
        print("Voice changer testing complete!")
        return True
    
    def interactive_mode(self):
        """Interactive mode for testing effects"""
        print("Standalone Voice Changer - Interactive Mode")
        print("Commands:")
        print("  list - Show available effects")
        print("  set <effect> - Set current effect")
        print("  test - Test current effect")
        print("  testall - Test all effects")
        print("  quit - Exit")
        
        while True:
            try:
                command = input(f"\n[{self.current_effect}] > ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'list':
                    print("Available effects:", ', '.join(self.get_available_effects()))
                elif command.startswith('set '):
                    effect = command[4:].strip()
                    self.set_effect(effect)
                elif command == 'test':
                    print(f"Testing effect: {self.current_effect}")
                    test_audio = self.generate_test_audio(duration=0.5)
                    processed = self.process_audio(test_audio)
                    print(f"Processed {len(processed)} samples with {self.current_effect}")
                elif command == 'testall':
                    self.test_all_effects()
                elif command == 'help':
                    print("Commands: list, set <effect>, test, testall, quit")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Standalone Voice Changer")
    parser.add_argument('--test', action='store_true', help='Run effect tests')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--input', type=str, help='Input audio file')
    parser.add_argument('--output', type=str, help='Output audio file')
    parser.add_argument('--effect', type=str, default='none', help='Effect to apply')
    parser.add_argument('--list-effects', action='store_true', help='List available effects')
    
    args = parser.parse_args()
    
    # Create voice changer instance
    vc = StandaloneVoiceChanger()
    
    if args.list_effects:
        print("Available effects:")
        for effect in vc.get_available_effects():
            print(f"  - {effect}")
        return
    
    if args.test:
        vc.test_all_effects()
        return
    
    if args.interactive:
        vc.interactive_mode()
        return
    
    if args.input:
        if not AUDIO_LIBS_AVAILABLE:
            print("Error: Audio processing libraries not available for file processing")
            print("Please install: pip3 install librosa soundfile scipy")
            return
        
        success = vc.process_file(args.input, args.output, args.effect)
        if success:
            print("File processing completed successfully!")
        else:
            print("File processing failed!")
        return
    
    # Default: run tests
    print("No specific action requested. Running default tests...")
    vc.test_all_effects()


if __name__ == "__main__":
    main()