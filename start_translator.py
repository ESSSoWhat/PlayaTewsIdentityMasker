#!/usr/bin/env python3
"""
Startup script for the Live Language Translator web interface.
"""

import os
import sys
import signal
import threading
import time
from web_translator import WebTranslator

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print('\n🛑 Shutting down Live Language Translator...')
    print('Thank you for using the translator!')
    sys.exit(0)

def main():
    """Main function to start the translator."""
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🌍 Live Language Translator")
    print("=" * 50)
    print("🚀 Initializing web interface...")
    
    try:
        # Create translator instance
        translator = WebTranslator()
        
        # Create interface
        interface = translator.create_interface()
        
        print("✅ Interface created successfully!")
        print("\n📊 Features:")
        print("  • Real-time text translation")
        print("  • Text-to-speech (TTS) support")
        print("  • Translation history")
        print("  • 70+ language support")
        print("  • Modern responsive UI")
        
        print(f"\n🔗 Supported Languages: {len(translator.supported_languages)}")
        print("🎯 Popular pairs: EN↔ES, EN↔FR, EN↔DE, and more!")
        
        print("\n🌐 Starting web server...")
        print("📍 Server will be available at:")
        print("   • Local: http://localhost:7860")
        print("   • Network: http://0.0.0.0:7860")
        
        # Launch the interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,  # Set to True for public sharing
            show_error=True,
            show_tips=True,
            enable_queue=True,
            debug=False,
            quiet=False
        )
        
    except KeyboardInterrupt:
        print('\n🛑 Interrupted by user')
    except Exception as e:
        print(f'\n❌ Error starting translator: {e}')
        print('💡 Please check your internet connection and try again.')
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)