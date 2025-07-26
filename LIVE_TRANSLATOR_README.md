# 🌍 Live Language Translator

A real-time speech-to-speech translation system with multiple interfaces and advanced features.

## Features

### Core Capabilities
- **Real-time speech recognition** using OpenAI Whisper and Google Speech Recognition
- **Multi-provider translation** with Google Translate, offline models, and more
- **High-quality text-to-speech** using Edge TTS, Google TTS, and local engines
- **Automatic language detection** with fallback mechanisms
- **Voice Activity Detection (VAD)** for optimal audio processing
- **Translation history** and session management

### Interfaces
- **Web Interface** - Modern Gradio-based UI for easy interaction
- **Command Line** - Simple CLI for quick testing and automation
- **Flask API** - RESTful API for integration with other applications

### Supported Languages
- English, Spanish, French, German, Italian, Portuguese
- Russian, Japanese, Korean, Chinese, Arabic, Hindi
- Auto-detection for source language
- Extensible to support additional languages

## Quick Start

### 1. Simple Version (Recommended for testing)

Install minimal dependencies:
```bash
pip install -r requirements_simple.txt
```

Run the simple translator:
```bash
# Continuous translation (auto-detect to English)
python simple_translator.py

# Spanish to English
python simple_translator.py --source es --target en

# Single translation mode
python simple_translator.py --single --source auto --target fr
```

### 2. Full Version (Advanced features)

Install all dependencies:
```bash
pip install -r requirements_live_translation.txt
```

Launch web interface:
```bash
# Default Gradio interface on port 7860
python live_translator.py

# Custom port and Flask interface
python live_translator.py --port 8080 --interface flask

# Different Whisper model
python live_translator.py --whisper-model small
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Microphone and speakers/headphones
- Internet connection (for cloud translation services)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-dev python3-pip portaudio19-dev espeak espeak-data libespeak1 libespeak-dev
```

**macOS:**
```bash
brew install portaudio espeak
```

**Windows:**
- Install Microsoft Visual C++ Build Tools
- Download PyAudio wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### Python Dependencies

**Option 1: Simple Version (Quick Setup)**
```bash
pip install -r requirements_simple.txt
```

**Option 2: Full Version (All Features)**
```bash
pip install -r requirements_live_translation.txt
```

**Option 3: Manual Installation**
```bash
# Core dependencies
pip install SpeechRecognition googletrans==4.0.0 gtts pygame pyaudio

# For advanced features
pip install openai-whisper faster-whisper transformers torch
pip install gradio flask edge-tts webrtcvad
```

## Usage

### Simple Command Line Interface

```bash
# Basic usage - auto-detect to English
python simple_translator.py

# Specify languages
python simple_translator.py --source es --target en

# Single translation mode
python simple_translator.py --single

# Custom listening duration
python simple_translator.py --duration 10
```

### Advanced Web Interface

```bash
# Launch Gradio interface (default)
python live_translator.py

# Access at http://localhost:7860
```

**Web Interface Features:**
- Language selection dropdowns
- Real-time translation display
- Translation history
- Audio playback of translations
- Start/stop controls

### API Usage

```bash
# Start Flask API server
python live_translator.py --interface flask --port 8080
```

**API Endpoints:**
- `POST /api/start` - Start translation session
- `POST /api/stop` - Stop translation
- `GET /api/history` - Get translation history
- `POST /api/clear` - Clear history

Example API call:
```python
import requests

# Start translation
response = requests.post('http://localhost:8080/api/start', 
                        json={'source_lang': 'auto', 'target_lang': 'en'})
print(response.json())
```

## Configuration

### Audio Settings
- **Sample Rate**: 16000 Hz (default)
- **Chunk Size**: 1024 samples
- **VAD Mode**: 3 (most aggressive)
- **Silence Timeout**: 2 seconds

### Translation Settings
- **Whisper Model**: base, small, medium, large
- **Translation Services**: Google, Microsoft, offline models
- **TTS Engine**: Edge TTS (default), Google TTS, pyttsx3

### Custom Configuration
```python
from live_translator import TranslationConfig, LiveTranslator

config = TranslationConfig(
    whisper_model="small",
    default_tts_engine="gtts",
    silence_timeout=3.0,
    sample_rate=44100
)

translator = LiveTranslator(config)
```

## Troubleshooting

### Common Issues

**1. Microphone not detected**
```bash
# Test microphone
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**2. PyAudio installation fails**
- Install system audio libraries (see Prerequisites)
- Use pre-compiled wheels for Windows

**3. Translation service errors**
- Check internet connection
- Verify Google Translate access
- Try different translation provider

**4. Audio playback issues**
- Install system audio codecs
- Check pygame/audio system compatibility
- Verify speaker/headphone connection

### Performance Optimization

**For better accuracy:**
- Use larger Whisper models (`medium` or `large`)
- Ensure quiet environment
- Use high-quality microphone
- Adjust VAD sensitivity

**For faster processing:**
- Use `base` Whisper model
- Enable faster-whisper
- Reduce audio chunk size
- Use local TTS engines

### Debug Mode
```bash
# Enable debug logging
python live_translator.py --verbose

# Test individual components
python -c "from live_translator import AudioCapture; AudioCapture().test_microphone()"
```

## Examples

### Use Cases

**1. Language Learning**
```bash
# Practice Spanish conversation
python simple_translator.py --source es --target en
```

**2. International Meetings**
```bash
# Real-time translation with web interface
python live_translator.py --port 7860
```

**3. Travel Assistant**
```bash
# Auto-detect to local language
python simple_translator.py --source auto --target es
```

**4. Integration with Applications**
```python
# Use as library
from live_translator import LiveTranslator
import asyncio

translator = LiveTranslator()
result = asyncio.run(translator.start_translation("auto", "en"))
```

## Architecture

### Components
- **AudioCapture**: Real-time audio recording with VAD
- **SpeechRecognizer**: Multi-engine speech-to-text
- **TranslationService**: Multi-provider translation
- **TextToSpeech**: Multi-engine text-to-speech
- **LiveTranslator**: Main orchestration class

### Data Flow
1. Audio capture with voice activity detection
2. Speech recognition using Whisper/Google
3. Language detection and text processing
4. Multi-provider translation
5. Text-to-speech synthesis
6. Audio playback and history logging

## Contributing

### Development Setup
```bash
git clone <repository>
cd live-translator
pip install -r requirements_live_translation.txt
python -m pytest tests/
```

### Adding Translation Providers
```python
class CustomTranslator:
    async def translate_text(self, text, source_lang, target_lang):
        # Implement custom translation logic
        return translated_text
```

### Adding TTS Engines
```python
class CustomTTS:
    async def speak_text(self, text, language):
        # Implement custom TTS logic
        return audio_bytes
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review system requirements
- Test with simple version first
- Check audio device compatibility

## Changelog

### Version 1.0.0
- Initial release with Gradio interface
- Multi-provider translation support
- Real-time speech processing
- Voice activity detection
- Translation history and session management