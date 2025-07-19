#!/usr/bin/env python3
"""
Simple Live Language Translator
A minimal command-line version for quick testing.
"""

import asyncio
import logging
import time
from pathlib import Path
import tempfile
import os

# Basic imports for minimal functionality
try:
    import speech_recognition as sr
    from googletrans import Translator
    from gtts import gTTS
    import pygame
    import io
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install required packages:")
    print("pip install SpeechRecognition googletrans==4.0.0 gtts pygame pyaudio")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleTranslator:
    """Simple live translation system."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.translator = Translator()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Adjust for ambient noise
        logger.info("Adjusting for ambient noise... Please be quiet.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        logger.info("Ready!")
    
    def listen_and_translate(self, source_lang="auto", target_lang="en", max_duration=5):
        """Listen for speech and translate it."""
        try:
            logger.info(f"Listening for {max_duration} seconds...")
            
            # Listen for audio
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=max_duration, phrase_time_limit=max_duration)
            
            logger.info("Processing speech...")
            
            # Recognize speech
            if source_lang == "auto":
                # Try multiple languages
                text = None
                detected_lang = None
                
                for lang in ["en-US", "es-ES", "fr-FR", "de-DE", "it-IT"]:
                    try:
                        text = self.recognizer.recognize_google(audio, language=lang)
                        detected_lang = lang.split("-")[0]
                        break
                    except sr.UnknownValueError:
                        continue
                
                if text is None:
                    text = self.recognizer.recognize_google(audio)
                    detected_lang = "en"
            else:
                text = self.recognizer.recognize_google(audio, language=source_lang)
                detected_lang = source_lang
            
            logger.info(f"Recognized ({detected_lang}): {text}")
            
            # Translate text
            if detected_lang != target_lang:
                translation = self.translator.translate(text, src=detected_lang, dest=target_lang)
                translated_text = translation.text
                logger.info(f"Translated ({target_lang}): {translated_text}")
            else:
                translated_text = text
                logger.info("No translation needed (same language)")
            
            # Convert to speech
            self.speak_text(translated_text, target_lang)
            
            return {
                "original": text,
                "translation": translated_text,
                "source_lang": detected_lang,
                "target_lang": target_lang
            }
            
        except sr.UnknownValueError:
            logger.error("Could not understand the audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    def speak_text(self, text, language="en"):
        """Convert text to speech and play it."""
        try:
            # Create TTS
            tts = gTTS(text=text, lang=language, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                
                # Play audio
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def continuous_translation(self, source_lang="auto", target_lang="en"):
        """Run continuous translation loop."""
        logger.info(f"Starting continuous translation: {source_lang} -> {target_lang}")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                result = self.listen_and_translate(source_lang, target_lang)
                if result:
                    print(f"\n{'='*50}")
                    print(f"Original ({result['source_lang']}): {result['original']}")
                    print(f"Translation ({result['target_lang']}): {result['translation']}")
                    print(f"{'='*50}\n")
                
                # Small delay before next iteration
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Translation stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous translation: {e}")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Live Language Translator")
    parser.add_argument("--source", default="auto", help="Source language (auto, en, es, fr, de, etc.)")
    parser.add_argument("--target", default="en", help="Target language (en, es, fr, de, etc.)")
    parser.add_argument("--single", action="store_true", help="Single translation mode")
    parser.add_argument("--duration", type=int, default=5, help="Max listening duration in seconds")
    
    args = parser.parse_args()
    
    # Create translator
    translator = SimpleTranslator()
    
    if args.single:
        # Single translation
        print(f"\nSingle translation mode: {args.source} -> {args.target}")
        print("Speak now...")
        result = translator.listen_and_translate(args.source, args.target, args.duration)
        
        if result:
            print(f"\nResult:")
            print(f"Original ({result['source_lang']}): {result['original']}")
            print(f"Translation ({result['target_lang']}): {result['translation']}")
        else:
            print("Translation failed")
    else:
        # Continuous translation
        translator.continuous_translation(args.source, args.target)


if __name__ == "__main__":
    main()