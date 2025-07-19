#!/usr/bin/env python3
"""
Live Language Translation System
A real-time speech-to-speech translation application with web interface.
"""

import asyncio
import json
import logging
import queue
import threading
import time
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import base64
import io

# Audio processing
import pyaudio
import numpy as np
import librosa
import webrtcvad
import soundfile as sf

# Speech recognition
import whisper
from faster_whisper import WhisperModel
import speech_recognition as sr

# Translation
from googletrans import Translator as GoogleTranslator
from deep_translator import GoogleTranslator as DeepGoogleTranslator, MicrosoftTranslator
from transformers import MarianMTModel, MarianTokenizer
import torch

# Text-to-speech
import pyttsx3
from gtts import gTTS
import edge_tts

# Language detection
from langdetect import detect
import pycld2 as cld2

# Web interface
from flask import Flask, render_template, request, jsonify, Response
import gradio as gr

# Utilities
import requests
from datetime import datetime
import uuid
import os
from dataclasses import dataclass, field


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TranslationConfig:
    """Configuration for the translation system."""
    # Audio settings
    sample_rate: int = 16000
    chunk_size: int = 1024
    channels: int = 1
    format: int = pyaudio.paInt16
    
    # VAD settings
    vad_mode: int = 3  # Most aggressive
    frame_duration_ms: int = 30
    
    # Speech recognition
    whisper_model: str = "base"
    use_faster_whisper: bool = True
    
    # Translation
    default_source_lang: str = "auto"
    default_target_lang: str = "en"
    translation_services: List[str] = field(default_factory=lambda: ["google", "microsoft"])
    
    # TTS
    default_tts_engine: str = "edge"  # edge, gtts, pyttsx3
    voice_speed: float = 1.0
    
    # Processing
    max_audio_length: float = 30.0  # seconds
    silence_timeout: float = 2.0    # seconds
    
    # Web interface
    web_port: int = 7860
    enable_gradio: bool = True


class AudioCapture:
    """Real-time audio capture with VAD."""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.vad = webrtcvad.Vad(config.vad_mode)
        self.audio_buffer = []
        self.silence_chunks = 0
        self.max_silence_chunks = int(config.silence_timeout * config.sample_rate / config.chunk_size)
        
        # Initialize PyAudio
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        
    def start_recording(self):
        """Start audio recording."""
        try:
            self.stream = self.pyaudio.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size,
                stream_callback=self._audio_callback
            )
            self.is_recording = True
            self.stream.start_stream()
            logger.info("Audio recording started")
        except Exception as e:
            logger.error(f"Failed to start audio recording: {e}")
            raise
    
    def stop_recording(self):
        """Stop audio recording."""
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        logger.info("Audio recording stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback."""
        if self.is_recording:
            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            
            # Check for voice activity
            is_speech = self.vad.is_speech(in_data, self.config.sample_rate)
            
            if is_speech:
                self.audio_buffer.extend(audio_data)
                self.silence_chunks = 0
            else:
                self.silence_chunks += 1
                if len(self.audio_buffer) > 0:
                    self.audio_buffer.extend(audio_data)
            
            # If we have enough silence or buffer is full, process the audio
            if (self.silence_chunks >= self.max_silence_chunks and len(self.audio_buffer) > 0) or \
               (len(self.audio_buffer) >= self.config.max_audio_length * self.config.sample_rate):
                
                if len(self.audio_buffer) > 0:
                    # Convert to audio format and add to queue
                    audio_array = np.array(self.audio_buffer, dtype=np.int16)
                    self.audio_queue.put(audio_array)
                    self.audio_buffer = []
                    self.silence_chunks = 0
        
        return (in_data, pyaudio.paContinue)
    
    def get_audio_segment(self) -> Optional[np.ndarray]:
        """Get the next audio segment from the queue."""
        try:
            return self.audio_queue.get_nowait()
        except queue.Empty:
            return None
    
    def __del__(self):
        """Cleanup resources."""
        self.stop_recording()
        if hasattr(self, 'pyaudio'):
            self.pyaudio.terminate()


class SpeechRecognizer:
    """Speech recognition using multiple engines."""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        
        # Initialize Whisper models
        if config.use_faster_whisper:
            self.whisper_model = WhisperModel(config.whisper_model, device="auto")
        else:
            self.whisper_model = whisper.load_model(config.whisper_model)
        
        # Initialize speech recognition
        self.sr_recognizer = sr.Recognizer()
        
    async def transcribe_audio(self, audio_data: np.ndarray, language: str = None) -> Tuple[str, str]:
        """Transcribe audio to text."""
        try:
            # Save audio to temporary file
            temp_file = f"/tmp/temp_audio_{uuid.uuid4().hex}.wav"
            sf.write(temp_file, audio_data, self.config.sample_rate)
            
            # Use Faster Whisper for transcription
            if self.config.use_faster_whisper:
                segments, info = self.whisper_model.transcribe(
                    temp_file,
                    language=language,
                    beam_size=5,
                    word_timestamps=True
                )
                
                transcription = ""
                detected_language = info.language
                
                for segment in segments:
                    transcription += segment.text + " "
                
                transcription = transcription.strip()
            else:
                # Use regular Whisper
                result = self.whisper_model.transcribe(temp_file, language=language)
                transcription = result["text"].strip()
                detected_language = result["language"]
            
            # Clean up temp file
            os.unlink(temp_file)
            
            logger.info(f"Transcribed ({detected_language}): {transcription}")
            return transcription, detected_language
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return "", "unknown"


class TranslationService:
    """Multi-provider translation service."""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        
        # Initialize translation services
        self.google_translator = GoogleTranslator()
        self.deep_google_translator = DeepGoogleTranslator(source='auto', target='en')
        
        # Initialize offline models for common language pairs
        self.offline_models = {}
        self._load_offline_models()
        
    def _load_offline_models(self):
        """Load offline translation models for common language pairs."""
        common_pairs = [
            ("en", "es"),  # English to Spanish
            ("en", "fr"),  # English to French
            ("en", "de"),  # English to German
            ("es", "en"),  # Spanish to English
            ("fr", "en"),  # French to English
            ("de", "en"),  # German to English
        ]
        
        for src, tgt in common_pairs:
            try:
                model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                self.offline_models[f"{src}-{tgt}"] = (tokenizer, model)
                logger.info(f"Loaded offline model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load offline model {src}-{tgt}: {e}")
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, str]:
        """Translate text using multiple services."""
        translations = {}
        
        # Google Translate
        try:
            if "google" in self.config.translation_services:
                google_result = self.google_translator.translate(
                    text, src=source_lang, dest=target_lang
                )
                translations["google"] = google_result.text
        except Exception as e:
            logger.error(f"Google Translate failed: {e}")
        
        # Deep Translator (Google)
        try:
            if "google" in self.config.translation_services:
                deep_translator = DeepGoogleTranslator(source=source_lang, target=target_lang)
                translations["deep_google"] = deep_translator.translate(text)
        except Exception as e:
            logger.error(f"Deep Google Translate failed: {e}")
        
        # Offline models
        try:
            model_key = f"{source_lang}-{target_lang}"
            if model_key in self.offline_models:
                tokenizer, model = self.offline_models[model_key]
                inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
                outputs = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
                translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
                translations["offline"] = translation
        except Exception as e:
            logger.error(f"Offline translation failed: {e}")
        
        # Return the best translation (prefer Google, then offline, then others)
        if "google" in translations:
            best_translation = translations["google"]
        elif "offline" in translations:
            best_translation = translations["offline"]
        elif "deep_google" in translations:
            best_translation = translations["deep_google"]
        else:
            best_translation = text  # Fallback to original text
        
        logger.info(f"Translated ({source_lang} -> {target_lang}): {text} -> {best_translation}")
        return {"best": best_translation, "all": translations}


class TextToSpeech:
    """Multi-engine text-to-speech synthesis."""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        
        # Initialize pyttsx3 engine
        try:
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty('rate', int(150 * config.voice_speed))
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            self.pyttsx3_engine = None
    
    async def speak_text(self, text: str, language: str = "en", voice: str = None) -> bytes:
        """Convert text to speech audio."""
        try:
            if self.config.default_tts_engine == "edge":
                return await self._edge_tts(text, language, voice)
            elif self.config.default_tts_engine == "gtts":
                return await self._gtts(text, language)
            elif self.config.default_tts_engine == "pyttsx3":
                return await self._pyttsx3_tts(text)
            else:
                # Fallback to gTTS
                return await self._gtts(text, language)
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            return b""
    
    async def _edge_tts(self, text: str, language: str, voice: str = None) -> bytes:
        """Generate speech using Edge TTS."""
        # Map language codes to Edge TTS voices
        voice_map = {
            "en": "en-US-JennyNeural",
            "es": "es-ES-ElviraNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural",
            "it": "it-IT-ElsaNeural",
            "pt": "pt-BR-FranciscaNeural",
            "ru": "ru-RU-SvetlanaNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "zh": "zh-CN-XiaoxiaoNeural",
        }
        
        selected_voice = voice or voice_map.get(language, "en-US-JennyNeural")
        
        communicate = edge_tts.Communicate(text, selected_voice)
        audio_data = b""
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    async def _gtts(self, text: str, language: str) -> bytes:
        """Generate speech using gTTS."""
        tts = gTTS(text=text, lang=language, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        return audio_buffer.getvalue()
    
    async def _pyttsx3_tts(self, text: str) -> bytes:
        """Generate speech using pyttsx3."""
        if not self.pyttsx3_engine:
            return b""
        
        # Save to temporary file
        temp_file = f"/tmp/tts_output_{uuid.uuid4().hex}.wav"
        self.pyttsx3_engine.save_to_file(text, temp_file)
        self.pyttsx3_engine.runAndWait()
        
        # Read audio data
        try:
            with open(temp_file, 'rb') as f:
                audio_data = f.read()
            os.unlink(temp_file)
            return audio_data
        except Exception as e:
            logger.error(f"Failed to read TTS output: {e}")
            return b""


class LiveTranslator:
    """Main live translation system."""
    
    def __init__(self, config: TranslationConfig = None):
        self.config = config or TranslationConfig()
        
        # Initialize components
        self.audio_capture = AudioCapture(self.config)
        self.speech_recognizer = SpeechRecognizer(self.config)
        self.translation_service = TranslationService(self.config)
        self.tts = TextToSpeech(self.config)
        
        # State
        self.is_running = False
        self.session_id = str(uuid.uuid4())
        self.translation_history = []
        
        # Event loop for async operations
        self.loop = None
        
    async def start_translation(self, source_lang: str = "auto", target_lang: str = "en"):
        """Start the live translation process."""
        logger.info(f"Starting live translation: {source_lang} -> {target_lang}")
        
        self.is_running = True
        self.audio_capture.start_recording()
        
        try:
            while self.is_running:
                # Get audio segment
                audio_data = self.audio_capture.get_audio_segment()
                
                if audio_data is not None:
                    # Process the audio
                    result = await self._process_audio_segment(
                        audio_data, source_lang, target_lang
                    )
                    
                    if result:
                        self.translation_history.append(result)
                        logger.info(f"Translation result: {result}")
                
                # Small delay to prevent CPU overload
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
        finally:
            self.audio_capture.stop_recording()
            self.is_running = False
    
    async def _process_audio_segment(self, audio_data: np.ndarray, source_lang: str, target_lang: str) -> Optional[Dict]:
        """Process a single audio segment."""
        timestamp = datetime.now().isoformat()
        
        try:
            # Transcribe audio
            transcription, detected_lang = await self.speech_recognizer.transcribe_audio(
                audio_data, language=source_lang if source_lang != "auto" else None
            )
            
            if not transcription.strip():
                return None
            
            # Use detected language if auto-detection was requested
            actual_source_lang = detected_lang if source_lang == "auto" else source_lang
            
            # Translate text
            translation_result = await self.translation_service.translate_text(
                transcription, actual_source_lang, target_lang
            )
            
            # Generate speech for translation
            audio_output = await self.tts.speak_text(
                translation_result["best"], target_lang
            )
            
            return {
                "timestamp": timestamp,
                "original_text": transcription,
                "source_language": actual_source_lang,
                "target_language": target_lang,
                "translation": translation_result["best"],
                "all_translations": translation_result["all"],
                "audio_output": base64.b64encode(audio_output).decode() if audio_output else None,
                "session_id": self.session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to process audio segment: {e}")
            return None
    
    def stop_translation(self):
        """Stop the live translation process."""
        self.is_running = False
        self.audio_capture.stop_recording()
        logger.info("Live translation stopped")
    
    def get_translation_history(self) -> List[Dict]:
        """Get the translation history for this session."""
        return self.translation_history.copy()
    
    def clear_history(self):
        """Clear the translation history."""
        self.translation_history.clear()


def create_flask_app(translator: LiveTranslator) -> Flask:
    """Create Flask web application."""
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return render_template('translator.html')
    
    @app.route('/api/start', methods=['POST'])
    def start_translation():
        data = request.json
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'en')
        
        # Start translation in background
        if not translator.is_running:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            def run_translation():
                loop.run_until_complete(
                    translator.start_translation(source_lang, target_lang)
                )
            
            thread = threading.Thread(target=run_translation)
            thread.daemon = True
            thread.start()
        
        return jsonify({"status": "started", "session_id": translator.session_id})
    
    @app.route('/api/stop', methods=['POST'])
    def stop_translation():
        translator.stop_translation()
        return jsonify({"status": "stopped"})
    
    @app.route('/api/history', methods=['GET'])
    def get_history():
        return jsonify(translator.get_translation_history())
    
    @app.route('/api/clear', methods=['POST'])
    def clear_history():
        translator.clear_history()
        return jsonify({"status": "cleared"})
    
    return app


def create_gradio_interface(translator: LiveTranslator):
    """Create Gradio web interface."""
    
    def start_translation_gradio(source_lang, target_lang):
        if not translator.is_running:
            # Start translation in background
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            def run_translation():
                loop.run_until_complete(
                    translator.start_translation(source_lang, target_lang)
                )
            
            thread = threading.Thread(target=run_translation)
            thread.daemon = True
            thread.start()
            
            return "Translation started!"
        else:
            return "Translation is already running!"
    
    def stop_translation_gradio():
        translator.stop_translation()
        return "Translation stopped!"
    
    def get_history_gradio():
        history = translator.get_translation_history()
        if not history:
            return "No translations yet."
        
        formatted_history = []
        for item in history[-10:]:  # Last 10 items
            formatted_history.append(
                f"**{item['source_language']} → {item['target_language']}**\n"
                f"Original: {item['original_text']}\n"
                f"Translation: {item['translation']}\n"
                f"Time: {item['timestamp']}\n---"
            )
        
        return "\n\n".join(formatted_history)
    
    # Language options
    languages = {
        "Auto-detect": "auto",
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Russian": "ru",
        "Japanese": "ja",
        "Korean": "ko",
        "Chinese": "zh",
        "Arabic": "ar",
        "Hindi": "hi"
    }
    
    with gr.Blocks(title="Live Language Translator", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🌍 Live Language Translator")
        gr.Markdown("Real-time speech-to-speech translation with multiple language support.")
        
        with gr.Row():
            with gr.Column():
                source_lang = gr.Dropdown(
                    choices=list(languages.keys()),
                    value="Auto-detect",
                    label="Source Language"
                )
                target_lang = gr.Dropdown(
                    choices=[k for k in languages.keys() if k != "Auto-detect"],
                    value="English",
                    label="Target Language"
                )
                
                with gr.Row():
                    start_btn = gr.Button("🎤 Start Translation", variant="primary")
                    stop_btn = gr.Button("⏹️ Stop Translation", variant="secondary")
                
                status_text = gr.Textbox(label="Status", interactive=False)
        
        with gr.Column():
            gr.Markdown("### Translation History")
            history_text = gr.Textbox(
                label="Recent Translations",
                lines=15,
                interactive=False,
                placeholder="Translations will appear here..."
            )
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh History")
                clear_btn = gr.Button("🗑️ Clear History")
        
        # Event handlers
        start_btn.click(
            fn=lambda src, tgt: start_translation_gradio(languages[src], languages[tgt]),
            inputs=[source_lang, target_lang],
            outputs=status_text
        )
        
        stop_btn.click(
            fn=stop_translation_gradio,
            outputs=status_text
        )
        
        refresh_btn.click(
            fn=get_history_gradio,
            outputs=history_text
        )
        
        clear_btn.click(
            fn=lambda: (translator.clear_history(), "History cleared!"),
            outputs=[history_text, status_text]
        )
    
    return interface


def main():
    """Main application entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Live Language Translator")
    parser.add_argument("--port", type=int, default=7860, help="Web interface port")
    parser.add_argument("--interface", choices=["gradio", "flask"], default="gradio", help="Web interface type")
    parser.add_argument("--whisper-model", default="base", help="Whisper model size")
    parser.add_argument("--source-lang", default="auto", help="Default source language")
    parser.add_argument("--target-lang", default="en", help="Default target language")
    
    args = parser.parse_args()
    
    # Create configuration
    config = TranslationConfig(
        whisper_model=args.whisper_model,
        default_source_lang=args.source_lang,
        default_target_lang=args.target_lang,
        web_port=args.port
    )
    
    # Create translator instance
    translator = LiveTranslator(config)
    
    try:
        if args.interface == "gradio":
            # Launch Gradio interface
            interface = create_gradio_interface(translator)
            interface.launch(
                server_name="0.0.0.0",
                server_port=args.port,
                share=False,
                show_api=False
            )
        else:
            # Launch Flask interface
            app = create_flask_app(translator)
            app.run(host="0.0.0.0", port=args.port, debug=False)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        translator.stop_translation()
    except Exception as e:
        logger.error(f"Application error: {e}")
        translator.stop_translation()


if __name__ == "__main__":
    main()