#!/usr/bin/env python3
"""
Live Language Translator - Web Interface
A modern web-based real-time translation system with TTS support.
"""

import gradio as gr
import time
import threading
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import base64
import tempfile
import os
from typing import Optional, Tuple, List
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebTranslator:
    """Web-based live translator with modern UI."""
    
    def __init__(self):
        self.translation_history = []
        self.supported_languages = {
            'auto': 'Auto-detect',
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Simplified)',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'tr': 'Turkish',
            'pl': 'Polish',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'fi': 'Finnish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'ro': 'Romanian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sk': 'Slovak',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'lt': 'Lithuanian',
            'mt': 'Maltese',
            'cy': 'Welsh',
            'ga': 'Irish',
            'is': 'Icelandic',
            'mk': 'Macedonian',
            'sq': 'Albanian',
            'sr': 'Serbian',
            'bs': 'Bosnian',
            'me': 'Montenegrin',
            'he': 'Hebrew',
            'fa': 'Persian',
            'ur': 'Urdu',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'pa': 'Punjabi',
            'mr': 'Marathi',
            'ne': 'Nepali',
            'si': 'Sinhala',
            'my': 'Myanmar',
            'km': 'Khmer',
            'lo': 'Lao',
            'ka': 'Georgian',
            'am': 'Amharic',
            'sw': 'Swahili',
            'zu': 'Zulu',
            'af': 'Afrikaans',
            'eu': 'Basque',
            'ca': 'Catalan',
            'gl': 'Galician',
            'lb': 'Luxembourgish',
            'rm': 'Romansh'
        }

    def translate_text(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str, 
        enable_tts: bool = True
    ) -> Tuple[str, Optional[str], str]:
        """
        Translate text and optionally generate TTS.
        
        Returns:
            Tuple of (translated_text, audio_file_path, status_message)
        """
        if not text.strip():
            return "", None, "Please enter text to translate."
            
        try:
            # Handle auto-detect
            if source_lang == 'auto':
                # Use Google Translator's auto-detect
                translator = GoogleTranslator(source='auto', target=target_lang)
            else:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Perform translation
            translated_text = translator.translate(text)
            
            if not translated_text:
                return "", None, "Translation failed. Please try again."
            
            # Store in history
            self.translation_history.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source_text': text,
                'source_lang': source_lang,
                'translated_text': translated_text,
                'target_lang': target_lang
            })
            
            # Generate TTS if enabled
            audio_path = None
            if enable_tts:
                try:
                    audio_path = self.generate_tts(translated_text, target_lang)
                except Exception as e:
                    logger.warning(f"TTS generation failed: {e}")
            
            status_msg = f"✅ Successfully translated from {self.supported_languages.get(source_lang, source_lang)} to {self.supported_languages.get(target_lang, target_lang)}"
            
            return translated_text, audio_path, status_msg
            
        except Exception as e:
            error_msg = f"❌ Translation error: {str(e)}"
            logger.error(error_msg)
            return "", None, error_msg

    def generate_tts(self, text: str, lang: str) -> str:
        """Generate TTS audio file and return path."""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate TTS
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None

    def get_history_display(self) -> str:
        """Get formatted translation history."""
        if not self.translation_history:
            return "No translations yet."
        
        history_text = "## Translation History\n\n"
        
        # Show last 10 translations
        recent_history = self.translation_history[-10:]
        
        for i, entry in enumerate(reversed(recent_history), 1):
            source_lang_name = self.supported_languages.get(entry['source_lang'], entry['source_lang'])
            target_lang_name = self.supported_languages.get(entry['target_lang'], entry['target_lang'])
            
            history_text += f"**{i}. {entry['timestamp']}**\n"
            history_text += f"*{source_lang_name} → {target_lang_name}*\n"
            history_text += f"**Original:** {entry['source_text']}\n"
            history_text += f"**Translation:** {entry['translated_text']}\n\n"
            history_text += "---\n\n"
        
        return history_text

    def clear_history(self):
        """Clear translation history."""
        self.translation_history.clear()
        return "Translation history cleared."

    def create_interface(self):
        """Create the Gradio interface."""
        
        # Custom CSS for better styling
        custom_css = """
        .gradio-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main-header {
            text-align: center;
            color: #2d3748;
            margin-bottom: 2rem;
        }
        
        .translation-box {
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            padding: 1rem;
        }
        
        .status-success {
            color: #38a169;
            font-weight: bold;
        }
        
        .status-error {
            color: #e53e3e;
            font-weight: bold;
        }
        
        .history-panel {
            background-color: #f7fafc;
            border-radius: 8px;
            padding: 1rem;
            max-height: 400px;
            overflow-y: auto;
        }
        """
        
        with gr.Blocks(css=custom_css, title="🌍 Live Language Translator") as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🌍 Live Language Translator</h1>
                <p>Real-time translation with text-to-speech support</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    # Translation section
                    gr.Markdown("### 📝 Translation")
                    
                    with gr.Row():
                        source_lang = gr.Dropdown(
                            choices=list(self.supported_languages.keys()),
                            value='auto',
                            label="🔤 Source Language",
                            interactive=True
                        )
                        
                        target_lang = gr.Dropdown(
                            choices=list(self.supported_languages.keys()),
                            value='en',
                            label="🎯 Target Language", 
                            interactive=True
                        )
                    
                    source_text = gr.Textbox(
                        placeholder="Enter text to translate...",
                        label="📥 Source Text",
                        lines=3,
                        max_lines=5
                    )
                    
                    with gr.Row():
                        translate_btn = gr.Button("🔄 Translate", variant="primary", size="lg")
                        enable_tts = gr.Checkbox(label="🔊 Enable Text-to-Speech", value=True)
                    
                    translated_text = gr.Textbox(
                        label="📤 Translation",
                        lines=3,
                        max_lines=5,
                        interactive=False
                    )
                    
                    # Audio output
                    audio_output = gr.Audio(label="🎵 Audio Playback", type="filepath")
                    
                    # Status message
                    status_msg = gr.Markdown("Ready to translate...")
                
                with gr.Column(scale=1):
                    # History and controls
                    gr.Markdown("### 📚 Translation History")
                    
                    history_display = gr.Markdown(
                        "No translations yet.",
                        elem_classes=["history-panel"]
                    )
                    
                    with gr.Row():
                        refresh_history = gr.Button("🔄 Refresh", size="sm")
                        clear_history_btn = gr.Button("🗑️ Clear History", size="sm")
                    
                    # Quick translate buttons
                    gr.Markdown("### ⚡ Quick Actions")
                    
                    with gr.Column():
                        gr.Markdown("**Popular Language Pairs:**")
                        
                        quick_en_es = gr.Button("🇺🇸→🇪🇸 EN→ES", size="sm")
                        quick_en_fr = gr.Button("🇺🇸→🇫🇷 EN→FR", size="sm")
                        quick_en_de = gr.Button("🇺🇸→🇩🇪 EN→DE", size="sm")
                        quick_es_en = gr.Button("🇪🇸→🇺🇸 ES→EN", size="sm")
                        quick_fr_en = gr.Button("🇫🇷→🇺🇸 FR→EN", size="sm")
            
            # Event handlers
            def handle_translation(src_text, src_lang, tgt_lang, tts_enabled):
                result, audio, status = self.translate_text(src_text, src_lang, tgt_lang, tts_enabled)
                return result, audio, status
            
            def update_history():
                return self.get_history_display()
            
            def clear_hist():
                msg = self.clear_history()
                return msg, self.get_history_display()
            
            # Quick language pair setters
            def set_en_es():
                return 'en', 'es'
            
            def set_en_fr():
                return 'en', 'fr'
                
            def set_en_de():
                return 'en', 'de'
                
            def set_es_en():
                return 'es', 'en'
                
            def set_fr_en():
                return 'fr', 'en'
            
            # Connect events
            translate_btn.click(
                fn=handle_translation,
                inputs=[source_text, source_lang, target_lang, enable_tts],
                outputs=[translated_text, audio_output, status_msg]
            ).then(
                fn=update_history,
                outputs=[history_display]
            )
            
            # Real-time translation on text change (with debounce)
            source_text.submit(
                fn=handle_translation,
                inputs=[source_text, source_lang, target_lang, enable_tts],
                outputs=[translated_text, audio_output, status_msg]
            ).then(
                fn=update_history,
                outputs=[history_display]
            )
            
            refresh_history.click(
                fn=update_history,
                outputs=[history_display]
            )
            
            clear_history_btn.click(
                fn=clear_hist,
                outputs=[status_msg, history_display]
            )
            
            # Quick language setters
            quick_en_es.click(fn=set_en_es, outputs=[source_lang, target_lang])
            quick_en_fr.click(fn=set_en_fr, outputs=[source_lang, target_lang])
            quick_en_de.click(fn=set_en_de, outputs=[source_lang, target_lang])
            quick_es_en.click(fn=set_es_en, outputs=[source_lang, target_lang])
            quick_fr_en.click(fn=set_fr_en, outputs=[source_lang, target_lang])
            
            # Add some example inputs
            gr.Examples(
                examples=[
                    ["Hello, how are you today?", "en", "es"],
                    ["Bonjour, comment allez-vous?", "fr", "en"],
                    ["Hola, ¿cómo estás?", "es", "en"],
                    ["Guten Tag, wie geht es Ihnen?", "de", "en"],
                    ["こんにちは、元気ですか？", "ja", "en"],
                    ["I love this translation app!", "en", "fr"],
                ],
                inputs=[source_text, source_lang, target_lang],
                label="📋 Example Translations"
            )
        
        return interface

def main():
    """Main function to launch the web interface."""
    print("🌍 Starting Live Language Translator...")
    
    # Create translator instance
    translator = WebTranslator()
    
    # Create and launch interface
    interface = translator.create_interface()
    
    print("🚀 Launching web interface...")
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates public link
        show_error=True,
        show_tips=True,
        enable_queue=True,
        debug=False
    )

if __name__ == "__main__":
    main()