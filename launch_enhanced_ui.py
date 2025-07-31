#!/usr/bin/env python3
"""
Launch script for PlayaTewsIdentityMasker with enhanced UI
Provides easy access to all the new UI/UX improvements
"""

import sys
import os
from pathlib import Path
import json
import time

def setup_environment():
    """Setup environment for enhanced UI"""
    
    # Add application paths
    app_root = Path(__file__).parent
    sys.path.insert(0, str(app_root))
    sys.path.insert(0, str(app_root / 'apps' / 'PlayaTewsIdentityMasker'))
    
    # Set environment variables for enhanced UI
    os.environ['PLAYATEWS_ENHANCED_UI'] = '1'
    os.environ['PLAYATEWS_VIDEO_FIT_MODE'] = 'Stretch'
    os.environ['PLAYATEWS_ACCESSIBILITY'] = '1'
    os.environ['PLAYATEWS_RESPONSIVE_LAYOUT'] = '1'
    
    # Create necessary directories
    userdata_path = Path('./userdata')
    userdata_path.mkdir(exist_ok=True)
    
    settings_path = Path('./settings')
    settings_path.mkdir(exist_ok=True)
    
    return userdata_path, settings_path

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt5
        print("✅ PyQt5 available")
    except ImportError:
        missing_deps.append("PyQt5")
        print("❌ PyQt5 not found")
    
    try:
        import numpy as np
        print("✅ NumPy available")
    except ImportError:
        missing_deps.append("NumPy")
        print("❌ NumPy not found")
    
    try:
        import cv2
        print("✅ OpenCV available")
    except ImportError:
        print("⚠️ OpenCV not available - video features may be limited")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install missing dependencies:")
        for dep in missing_deps:
            if dep == "PyQt5":
                print("  pip install PyQt5")
            elif dep == "NumPy":
                print("  pip install numpy")
        return False
    
    return True

def create_default_settings(settings_path):
    """Create default enhanced UI settings"""
    default_settings = {
        'ui': {
            'video_fit_mode': 'Stretch',
            'panel_sizes': [300, 800, 300],
            'theme': 'dark',
            'window_size': [1400, 900],
            'fullscreen': False
        },
        'accessibility': {
            'keyboard_shortcuts': True,
            'high_contrast': False,
            'screen_reader': False,
            'large_text': False
        },
        'performance': {
            'target_fps': 30,
            'memory_limit_gb': 4,
            'gpu_acceleration': True,
            'video_quality': 'HD',
            'optimize_for_speed': False
        },
        'features': {
            'responsive_layout': True,
            'hover_effects': True,
            'animations': True,
            'performance_monitoring': True
        }
    }
    
    settings_file = settings_path / 'enhanced_ui_settings.json'
    if not settings_file.exists():
        with open(settings_file, 'w') as f:
            json.dump(default_settings, f, indent=2)
        print(f"✅ Created default settings: {settings_file}")
    
    return default_settings

def show_welcome_message():
    """Show welcome message with feature overview"""
    welcome_text = """
    🎉 Welcome to PlayaTews Identity Masker - Enhanced UI!
    
    ✨ New Features Available:
    
    📹 Video Display:
       • 80%+ space allocation for video feed
       • Stretch-fit mode by default
       • Multiple fit modes (Stretch, Fit, Fill, Original)
       • Fullscreen support (F11)
    
    📱 Responsive Design:
       • Adapts to different screen sizes
       • Dynamic panel sizing
       • Minimum/maximum size constraints
    
    ⌨️ Accessibility:
       • Keyboard shortcuts (F11, Ctrl+S, Ctrl+R, Ctrl+F)
       • High contrast support
       • Screen reader compatibility
    
    🎨 Modern Interface:
       • Dark theme with consistent styling
       • Hover effects and smooth animations
       • Collapsible settings panels
       • Performance monitoring
    
    🚀 Performance:
       • Optimized video rendering
       • Memory management
       • GPU acceleration support
    
    Press Enter to continue or Ctrl+C to exit...
    """
    
    print(welcome_text)
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

def launch_enhanced_ui():
    """Launch the application with enhanced UI"""
    
    print("🚀 Initializing PlayaTews Identity Masker Enhanced UI...")
    print("=" * 60)
    
    # Setup environment
    userdata_path, settings_path = setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Cannot launch without required dependencies")
        return 1
    
    # Create default settings
    settings = create_default_settings(settings_path)
    
    # Show welcome message
    show_welcome_message()
    
    try:
        # Import required modules
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from PyQt5.QtGui import QIcon
        
        # Try to import the main application
        try:
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            print("✅ Main application imported successfully")
        except ImportError as e:
            print(f"⚠️ Could not import main application: {e}")
            print("   Launching enhanced UI test mode instead...")
            return launch_test_mode()
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("PlayaTews Identity Masker - Enhanced")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("PlayaTews")
        
        # Set application icon if available
        icon_path = Path('./resources/gfx/images/app_icon.png')
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Create and show main application
        print("🎯 Creating main application window...")
        main_app = PlayaTewsIdentityMaskerApp(userdata_path)
        
        # Apply enhanced UI settings
        apply_enhanced_settings(main_app, settings)
        
        # Show the application
        main_app.show()
        
        print("✅ PlayaTews Identity Masker Enhanced UI launched successfully!")
        print("\n🎮 Quick Start Guide:")
        print("   • F11: Toggle fullscreen")
        print("   • Ctrl+S: Toggle streaming")
        print("   • Ctrl+R: Toggle recording")
        print("   • Ctrl+F: Toggle face swap")
        print("   • Resize window to test responsive layout")
        print("   • Hover over buttons for tooltips")
        
        # Start the application
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Error importing enhanced UI components: {e}")
        print("Please ensure all required files are in place.")
        print("Try running: python integration_test.py")
        return 1
    except Exception as e:
        print(f"❌ Error launching enhanced UI: {e}")
        print("Falling back to test mode...")
        return launch_test_mode()

def launch_test_mode():
    """Launch enhanced UI in test mode with mock data"""
    try:
        print("🧪 Launching Enhanced UI Test Mode...")
        
        # Import test components
        from integration_test import IntegrationTest
        
        # Create and run test
        test = IntegrationTest()
        result = test.run_test()
        test.cleanup()
        
        return result
        
    except Exception as e:
        print(f"❌ Error launching test mode: {e}")
        print("Please check that integration_test.py is available")
        return 1

def apply_enhanced_settings(main_app, settings):
    """Apply enhanced UI settings to the main application"""
    try:
        # Apply window size
        if 'window_size' in settings['ui']:
            width, height = settings['ui']['window_size']
            main_app.resize(width, height)
        
        # Apply fullscreen setting
        if settings['ui'].get('fullscreen', False):
            main_app.showFullScreen()
        
        # Apply accessibility settings
        if settings['accessibility'].get('high_contrast', False):
            # Apply high contrast theme
            pass
        
        # Apply performance settings
        if 'performance' in settings:
            perf_settings = settings['performance']
            if hasattr(main_app, 'set_performance_settings'):
                main_app.set_performance_settings(perf_settings)
        
        print("✅ Enhanced settings applied")
        
    except Exception as e:
        print(f"⚠️ Could not apply all settings: {e}")

def show_help():
    """Show help information"""
    help_text = """
    PlayaTews Identity Masker Enhanced UI - Help
    
    Usage:
        python launch_enhanced_ui.py          # Launch with enhanced UI
        python launch_enhanced_ui.py --test   # Launch test mode
        python launch_enhanced_ui.py --help   # Show this help
    
    Features:
        • Enhanced video display with 80%+ space allocation
        • Responsive layout that adapts to screen size
        • Modern dark theme with consistent styling
        • Comprehensive keyboard shortcuts
        • Performance monitoring and optimization
        • Accessibility features (WCAG 2.1 AA compliant)
    
    Keyboard Shortcuts:
        F11          - Toggle fullscreen
        Ctrl+S       - Toggle streaming
        Ctrl+R       - Toggle recording
        Ctrl+F       - Toggle face swap
        Ctrl+,       - Open settings
        F1           - Show help
        Escape       - Exit fullscreen
    
    Troubleshooting:
        • If the app doesn't start, try: python integration_test.py
        • Check that PyQt5 and NumPy are installed
        • Ensure all UI files are in the correct locations
    
    For more information, see UI_INTEGRATION_GUIDE.md
    """
    
    print(help_text)

def main():
    """Main function"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            return 0
        elif sys.argv[1] in ['--test', '-t', 'test']:
            return launch_test_mode()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return 1
    
    # Launch enhanced UI
    return launch_enhanced_ui()

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 