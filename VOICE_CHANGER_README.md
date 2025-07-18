# Voice Changer for PlayaTewsIdentityMasker

## Overview

The Voice Changer is a real-time audio processing module that has been integrated into the PlayaTewsIdentityMasker application. It provides various audio effects that can be applied to microphone input in real-time, making it perfect for live streaming, gaming, or content creation.

## Features

### Audio Effects
- **Pitch Shift**: Adjust the pitch of your voice up or down by semitones
- **Formant Shift**: Modify the formant frequencies to change voice character
- **Robot Effect**: Add robotic modulation to your voice
- **Helium Effect**: High-pitched voice effect
- **Deep Voice**: Low-pitched voice effect
- **Echo**: Add echo with configurable delay and decay
- **Reverb**: Add room reverb with adjustable room size and damping
- **Chorus**: Add chorus effect with rate and depth control
- **Distortion**: Add distortion/overdrive effect
- **Autotune**: Automatic pitch correction

### Technical Features
- Real-time audio processing with low latency
- Support for multiple input and output devices
- Voice Activity Detection (VAD) for efficient processing
- Configurable audio parameters
- Preset configurations for quick setup
- Cross-platform compatibility (Windows, macOS, Linux)

## Installation

### Prerequisites
- Python 3.8 or higher
- Microphone and speakers/headphones
- Audio drivers properly installed

### Dependencies
The voice changer requires the following additional dependencies:

```bash
pip install pyaudio librosa soundfile scipy webrtcvad
```

Or install all dependencies including the voice changer:

```bash
pip install -r requirements-unified.txt
```

### System-specific Setup

#### Windows
1. Install Microsoft Visual C++ Build Tools (if not already installed)
2. Install PortAudio: `pip install pyaudio`
3. Ensure your microphone is set as the default input device

#### macOS
1. Install PortAudio: `brew install portaudio`
2. Install PyAudio: `pip install pyaudio`
3. Grant microphone permissions to the application

#### Linux
1. Install system dependencies:
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   # or for Fedora/RHEL:
   sudo dnf install portaudio-devel python3-pyaudio
   ```
2. Install PyAudio: `pip install pyaudio`

## Usage

### Starting the Application
1. Run the main application:
   ```bash
   python main.py run PlayaTewsIdentityMasker
   ```

2. The Voice Changer panel will appear in the main interface

### Basic Operation

1. **Enable Voice Changer**: Check the "Voice Changer Control" checkbox to start audio processing

2. **Select Input/Output Devices**: 
   - Go to the "Devices" tab
   - Choose your microphone from the input device list
   - Choose your speakers/headphones from the output device list

3. **Choose an Effect**:
   - Select an effect type from the dropdown menu
   - Use the "Quick Presets" buttons for instant effects

4. **Adjust Parameters**:
   - Go to the "Effects" tab to fine-tune effect parameters
   - Each effect has its own set of adjustable parameters

### Effect Parameters

#### Pitch Shift
- **Pitch Shift (semitones)**: Range -12 to +12 semitones
  - Positive values: Higher pitch (helium effect)
  - Negative values: Lower pitch (deep voice)

#### Formant Shift
- **Formant Shift**: Range 0.5 to 2.0
  - Values < 1.0: More masculine sound
  - Values > 1.0: More feminine sound

#### Robot Effect
- **Modulation Rate (Hz)**: Range 0.1 to 10.0 Hz
  - Higher values create faster modulation

#### Echo Effect
- **Delay (seconds)**: Range 0.1 to 1.0 seconds
- **Decay**: Range 0.1 to 0.9 (how much the echo fades)

#### Reverb Effect
- **Room Size**: Range 0.1 to 1.0 (larger rooms = more reverb)
- **Damping**: Range 0.1 to 1.0 (higher values = less high-frequency reflection)

#### Chorus Effect
- **Rate (Hz)**: Range 0.1 to 5.0 Hz (modulation speed)
- **Depth (seconds)**: Range 0.001 to 0.01 seconds (modulation depth)

#### Distortion Effect
- **Amount**: Range 0.1 to 1.0 (higher values = more distortion)

#### Autotune Effect
- **Sensitivity**: Range 0.01 to 1.0 (higher values = more aggressive correction)

### Quick Presets

The application includes several preset configurations:

- **Helium**: High-pitched voice effect
- **Deep Voice**: Low-pitched voice effect  
- **Robot**: Robotic modulation effect
- **Echo**: Echo with 300ms delay
- **Reverb**: Room reverb effect
- **Chorus**: Chorus effect
- **Distortion**: Distortion effect
- **Autotune**: Pitch correction effect

## Troubleshooting

### Common Issues

#### No Audio Input/Output
1. Check that your microphone and speakers are properly connected
2. Verify device selection in the "Devices" tab
3. Check system audio settings and permissions
4. Ensure no other applications are using the audio devices

#### High Latency
1. Reduce the buffer size in the audio settings
2. Close other audio applications
3. Use headphones to avoid feedback loops
4. Check system performance and close unnecessary applications

#### Audio Quality Issues
1. Ensure microphone is not too close to speakers (feedback)
2. Adjust input volume in system settings
3. Use a high-quality microphone for better results
4. Check for background noise and use noise reduction if available

#### PyAudio Installation Issues
1. **Windows**: Install Microsoft Visual C++ Build Tools
2. **macOS**: Install PortAudio via Homebrew first
3. **Linux**: Install system dependencies before pip install

### Error Messages

#### "No module named 'pyaudio'"
```bash
pip install pyaudio
```

#### "PortAudio not found"
- **Windows**: Install Visual C++ Build Tools
- **macOS**: `brew install portaudio`
- **Linux**: `sudo apt-get install portaudio19-dev`

#### "No audio devices found"
1. Check audio drivers are installed
2. Verify microphone and speakers are connected
3. Check system audio settings

## Advanced Usage

### Combining Effects
While the interface allows selecting one effect at a time, you can create custom combinations by:
1. Applying one effect
2. Recording the output
3. Processing the recording with another effect

### Custom Presets
You can create custom presets by:
1. Setting up your desired effect parameters
2. Taking note of the values
3. Creating a script to apply these settings programmatically

### Integration with Streaming Software
The voice changer works well with:
- OBS Studio
- Streamlabs
- XSplit
- Discord
- Teams
- Zoom

Set the voice changer output as your microphone input in your streaming software.

## Technical Details

### Audio Specifications
- **Sample Rate**: 44.1 kHz
- **Buffer Size**: 1024 samples
- **Channels**: Mono
- **Format**: 32-bit Float
- **Latency**: ~23ms (typical)

### Processing Pipeline
1. **Input**: Audio captured from microphone
2. **VAD**: Voice Activity Detection (optional)
3. **Effect Processing**: Apply selected audio effect
4. **Output**: Processed audio sent to speakers/headphones

### Performance Considerations
- CPU usage varies by effect (5-20% typical)
- Memory usage: ~50MB for audio buffers
- GPU acceleration not currently used (CPU-based processing)

## Development

### Adding New Effects
To add a new audio effect:

1. Add the effect type to `VoiceEffectType` enum in `VoiceChanger.py`
2. Implement the effect method in `VoiceChangerWorker`
3. Add UI controls in `QVoiceChanger.py`
4. Update the preset configurations

### Testing
Run the test script to verify functionality:
```bash
python test_voice_changer.py
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Run the test script to diagnose problems
3. Check system audio settings and permissions
4. Ensure all dependencies are properly installed

## License

The Voice Changer is part of the PlayaTewsIdentityMasker project and follows the same license terms.