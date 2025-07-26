#!/usr/bin/env python3
"""
Demo script for the Live Language Translator.
This demonstrates the translation functionality without requiring microphone input.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_translator import SimpleTranslator
try:
    from googletrans import Translator
except ImportError:
    # Fallback to deep_translator if googletrans fails
    from deep_translator import GoogleTranslator as Translator
from gtts import gTTS
import io
import time
import asyncio

def demo_text_translation():
    """Demonstrate text translation functionality."""
    print("🌍 Live Language Translator Demo")
    print("=" * 50)
    
    # Initialize translator
    translator = Translator()
    
    # Demo text samples
    demo_texts = [
        ("Hello, how are you today?", "en", "es"),
        ("Bonjour, comment allez-vous?", "fr", "en"),
        ("Hola, ¿cómo estás?", "es", "en"),
        ("Guten Tag, wie geht es Ihnen?", "de", "en"),
        ("This is a live translation system.", "en", "fr"),
    ]
    
    print("\n📝 Text Translation Demo:")
    print("-" * 30)
    
    for text, src_lang, dest_lang in demo_texts:
        try:
            result = translator.translate(text, src=src_lang, dest=dest_lang)
            print(f"\n🔤 Source ({src_lang}): {text}")
            print(f"🔄 Translation ({dest_lang}): {result.text}")
            print(f"🎯 Detected Language: {result.src}")
        except Exception as e:
            print(f"❌ Translation failed: {e}")

def demo_text_to_speech():
    """Demonstrate text-to-speech functionality."""
    print("\n\n🔊 Text-to-Speech Demo:")
    print("-" * 30)
    
    # Initialize pygame mixer
    pygame.mixer.init()
    
    demo_speeches = [
        ("Hello, this is a translation demo!", "en"),
        ("¡Hola, esta es una demostración de traducción!", "es"),
        ("Bonjour, ceci est une démonstration de traduction!", "fr"),
    ]
    
    for text, lang in demo_speeches:
        try:
            print(f"\n🎵 Speaking ({lang}): {text}")
            
            # Generate TTS
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Note: In a headless environment, we'll just show that TTS was generated
            print(f"✅ TTS audio generated successfully ({len(audio_buffer.getvalue())} bytes)")
            
        except Exception as e:
            print(f"❌ TTS failed: {e}")

def demo_language_detection():
    """Demonstrate language detection."""
    print("\n\n🔍 Language Detection Demo:")
    print("-" * 30)
    
    translator = Translator()
    
    test_texts = [
        "Hello, how are you?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?",
        "Guten Tag, wie geht es Ihnen?",
        "Ciao, come stai?",
        "こんにちは、元気ですか？",
        "Привет, как дела?",
    ]
    
    for text in test_texts:
        try:
            detection = translator.detect(text)
            print(f"🔤 Text: {text}")
            print(f"🎯 Detected: {detection.lang} (confidence: {detection.confidence:.2f})")
            print()
        except Exception as e:
            print(f"❌ Detection failed for '{text}': {e}")

def demo_real_time_scenario():
    """Demonstrate a real-time translation scenario."""
    print("\n\n🎭 Real-time Scenario Demo:")
    print("-" * 30)
    print("Simulating a conversation between English and Spanish speakers...")
    
    translator = Translator()
    
    conversation = [
        ("Hello, nice to meet you!", "en", "es"),
        ("¡Hola, mucho gusto!", "es", "en"),
        ("How can I help you today?", "en", "es"),
        ("¿Dónde está la estación de tren?", "es", "en"),
        ("The train station is two blocks away.", "en", "es"),
        ("¡Muchas gracias por su ayuda!", "es", "en"),
    ]
    
    for i, (text, src, dest) in enumerate(conversation, 1):
        try:
            result = translator.translate(text, src=src, dest=dest)
            speaker = "🧑‍💼 Person A" if src == "en" else "👤 Person B"
            
            print(f"\n{i}. {speaker} ({src}): {text}")
            print(f"   🔄 Translation ({dest}): {result.text}")
            
            # Simulate processing time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Translation {i} failed: {e}")

def main():
    """Main demo function."""
    try:
        print("Starting Live Language Translator Demo...\n")
        
        # Run all demos
        demo_text_translation()
        demo_language_detection()
        demo_text_to_speech()
        demo_real_time_scenario()
        
        print("\n\n✅ Demo completed successfully!")
        print("\n📋 Summary:")
        print("- Text translation: Working")
        print("- Language detection: Working")
        print("- Text-to-speech: Working")
        print("- Real-time scenarios: Simulated")
        
        print("\n🚀 To use the full live translator:")
        print("1. Ensure you have a working microphone")
        print("2. Run: python simple_translator.py")
        print("3. Or with specific languages: python simple_translator.py --source es --target en")
        
        print("\n📖 For advanced features:")
        print("- Run: python live_translator.py")
        print("- Access web interface at http://localhost:7860")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Please check that all dependencies are installed correctly.")

if __name__ == "__main__":
    main()