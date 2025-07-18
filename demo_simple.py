#!/usr/bin/env python3
"""
Simple Demo for Live Language Translator
Works without audio devices and demonstrates core functionality.
"""

import time
import io
from deep_translator import GoogleTranslator
from gtts import gTTS

def demo_translation():
    """Demonstrate translation functionality."""
    print("🌍 Live Language Translator - Simple Demo")
    print("=" * 50)
    
    # Test translations
    translations = [
        ("Hello, how are you today?", "en", "es"),
        ("Bonjour, comment allez-vous?", "fr", "en"),
        ("Hola, ¿cómo estás?", "es", "en"),
        ("Guten Tag, wie geht es Ihnen?", "de", "en"),
        ("This is a live translation system.", "en", "fr"),
        ("I love technology and programming", "en", "ja"),
    ]
    
    print("\n📝 Translation Demo:")
    print("-" * 40)
    
    for original, src_lang, dest_lang in translations:
        try:
            # Create translator instance
            translator = GoogleTranslator(source=src_lang, target=dest_lang)
            
            # Translate
            translated = translator.translate(original)
            
            print(f"\n🔤 Source ({src_lang}): {original}")
            print(f"🔄 Translation ({dest_lang}): {translated}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Translation failed: {e}")

def demo_language_detection():
    """Demonstrate language detection (simulated)."""
    print("\n\n🔍 Language Detection Demo:")
    print("-" * 40)
    
    # Since we don't have reliable auto-detection, we'll simulate it
    test_phrases = [
        ("Hello, how are you?", "en"),
        ("Hola, ¿cómo estás?", "es"),
        ("Bonjour, comment allez-vous?", "fr"),
        ("Guten Tag, wie geht es Ihnen?", "de"),
        ("Ciao, come stai?", "it"),
        ("Olá, como está?", "pt"),
    ]
    
    for phrase, expected_lang in test_phrases:
        print(f"🔤 Text: {phrase}")
        print(f"🎯 Language: {expected_lang}")
        print()

def demo_text_to_speech():
    """Demonstrate text-to-speech generation."""
    print("\n🔊 Text-to-Speech Demo:")
    print("-" * 40)
    
    tts_examples = [
        ("Hello, this is a translation demo!", "en"),
        ("¡Hola, esta es una demostración de traducción!", "es"),
        ("Bonjour, ceci est une démonstration de traduction!", "fr"),
        ("Hallo, das ist eine Übersetzungsdemonstration!", "de"),
    ]
    
    for text, lang in tts_examples:
        try:
            print(f"\n🎵 Generating TTS for ({lang}): {text}")
            
            # Generate TTS
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            
            # Show success
            audio_size = len(audio_buffer.getvalue())
            print(f"✅ TTS audio generated: {audio_size} bytes")
            
        except Exception as e:
            print(f"❌ TTS failed: {e}")

def demo_conversation():
    """Demonstrate a bilingual conversation."""
    print("\n\n🎭 Bilingual Conversation Demo:")
    print("-" * 40)
    print("Simulating English ↔ Spanish conversation...")
    
    conversation = [
        ("Hello! Welcome to our store.", "en", "es"),
        ("¡Hola! Busco una camisa azul.", "es", "en"),
        ("We have blue shirts in aisle 3.", "en", "es"),
        ("¿Cuánto cuesta esta camisa?", "es", "en"),
        ("That shirt costs twenty dollars.", "en", "es"),
        ("Perfecto, me la llevo. ¡Gracias!", "es", "en"),
    ]
    
    for i, (text, src, dest) in enumerate(conversation, 1):
        try:
            translator = GoogleTranslator(source=src, target=dest)
            translation = translator.translate(text)
            
            speaker = "🧑‍💼 Clerk" if src == "en" else "👤 Customer"
            
            print(f"\n{i}. {speaker} ({src.upper()}): {text}")
            print(f"   🔄 Translation ({dest.upper()}): {translation}")
            
            time.sleep(1)  # Simulate conversation pace
            
        except Exception as e:
            print(f"❌ Step {i} failed: {e}")

def demo_language_pairs():
    """Demonstrate various language pairs."""
    print("\n\n🌐 Multiple Language Pairs Demo:")
    print("-" * 40)
    
    phrase = "Thank you very much for your help!"
    target_languages = {
        "es": "Spanish",
        "fr": "French", 
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ru": "Russian",
        "ar": "Arabic"
    }
    
    print(f"🔤 Original (English): {phrase}")
    print("\n🔄 Translations:")
    
    for lang_code, lang_name in target_languages.items():
        try:
            translator = GoogleTranslator(source="en", target=lang_code)
            translation = translator.translate(phrase)
            print(f"   {lang_name} ({lang_code}): {translation}")
            time.sleep(0.3)  # Avoid rate limiting
        except Exception as e:
            print(f"   {lang_name} ({lang_code}): ❌ Failed - {e}")

def main():
    """Main demo function."""
    try:
        print("🚀 Starting Live Language Translator Demo...\n")
        
        # Run demos
        demo_translation()
        demo_language_detection()
        demo_text_to_speech()
        demo_conversation()
        demo_language_pairs()
        
        # Summary
        print("\n\n✅ Demo completed successfully!")
        print("\n📋 Functionality Demonstrated:")
        print("- ✅ Text translation between multiple languages")
        print("- ✅ Language detection (simulated)")
        print("- ✅ Text-to-speech generation")
        print("- ✅ Real-time conversation simulation")
        print("- ✅ Multiple language pair support")
        
        print("\n🎯 Next Steps:")
        print("1. 🎤 For live speech input: python simple_translator.py")
        print("2. 🌐 For web interface: python live_translator.py")
        print("3. 📱 For advanced features: Install full requirements")
        
        print("\n💡 Usage Examples:")
        print("- python simple_translator.py --source auto --target es")
        print("- python simple_translator.py --single --duration 10")
        print("- python live_translator.py --port 8080 --interface gradio")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()