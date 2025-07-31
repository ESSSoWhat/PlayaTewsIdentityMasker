#!/usr/bin/env python3
"""
Enhanced PlayaTews Identity Masker Launcher

This script launches the enhanced version of the PlayaTews Identity Masker
with modern UI/UX improvements while maintaining all backend functionality.
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Setup environment variables and paths"""
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set environment variables for enhanced UI
    os.environ['PLAYATEWS_ENHANCED_UI'] = '1'
    os.environ['PLAYATEWS_VIDEO_SPACE_ALLOCATION'] = '80'
    os.environ['PLAYATEWS_RESPONSIVE_LAYOUT'] = '1'
    
    # Create necessary directories
    userdata_path = current_dir / 'userdata'
    userdata_path.mkdir(exist_ok=True)
    
    settings_path = current_dir / 'settings'
    settings_path.mkdir(exist_ok=True)
    
    return userdata_path, settings_path

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'PyQt5',
        'numpy',
        'cv2',
        'xlib'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - Missing")
    
    if missing_modules:
        print(f"\n⚠️ Missing required modules: {', '.join(missing_modules)}")
        print("Please install missing dependencies before running the enhanced app.")
        return False
    
    return True

def launch_enhanced_app(userdata_path):
    """Launch the enhanced application"""
    try:
        print("🚀 Launching PlayaTews Identity Masker - Enhanced UI...")
        
        # Import the enhanced application
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerEnhancedApp import PlayaTewsIdentityMaskerEnhancedApp
        
        # Create and run the application
        app = PlayaTewsIdentityMaskerEnhancedApp(userdata_path)
        app.initialize()
        
        print("✅ Enhanced application launched successfully!")
        print("🎮 Enhanced Features Available:")
        print("   • 80%+ video space allocation")
        print("   • Responsive layout design")
        print("   • Modern dark theme")
        print("   • Keyboard shortcuts (F11, Ctrl+S, Ctrl+R)")
        print("   • Performance monitoring")
        print("   • Memory optimization")
        
        # Start the application event loop
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Could not import enhanced application: {e}")
        print("   Falling back to standard application...")
        return launch_standard_app(userdata_path)
        
    except Exception as e:
        print(f"❌ Error launching enhanced application: {e}")
        print("   Falling back to standard application...")
        return launch_standard_app(userdata_path)

def launch_standard_app(userdata_path):
    """Launch the standard application as fallback"""
    try:
        print("🔄 Launching standard PlayaTews Identity Masker...")
        
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        app = PlayaTewsIdentityMaskerApp(userdata_path)
        app.initialize()
        
        print("✅ Standard application launched successfully!")
        
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error launching standard application: {e}")
        return 1

def show_welcome_message():
    """Show welcome message with enhanced features"""
    print("=" * 80)
    print("🎮 PlayaTews Identity Masker - Enhanced UI Edition")
    print("=" * 80)
    print()
    print("✨ Enhanced Features:")
    print("   📹 Video Display:")
    print("      • 80%+ space allocation for video feed")
    print("      • Stretch-fit mode by default")
    print("      • Multiple fit modes (Stretch, Fit, Fill, Original)")
    print("      • Fullscreen support (F11)")
    print()
    print("   📱 Responsive Design:")
    print("      • Adapts to different screen sizes")
    print("      • Dynamic panel sizing")
    print("      • Minimum/maximum size constraints")
    print()
    print("   ⌨️ Accessibility:")
    print("      • Keyboard shortcuts (F11, Ctrl+S, Ctrl+R, Ctrl+F)")
    print("      • High contrast support")
    print("      • Screen reader compatibility")
    print()
    print("   🎨 Modern Interface:")
    print("      • Dark theme with consistent styling")
    print("      • Hover effects and smooth animations")
    print("      • Collapsible settings panels")
    print("      • Performance monitoring")
    print()
    print("   🚀 Performance:")
    print("      • Optimized video rendering")
    print("      • Memory management")
    print("      • GPU acceleration support")
    print()
    print("🎮 Quick Start Guide:")
    print("   • F11: Toggle fullscreen")
    print("   • Ctrl+S: Toggle streaming")
    print("   • Ctrl+R: Toggle recording")
    print("   • Ctrl+F: Toggle face swap")
    print("   • F1: Show help")
    print("   • Resize window to test responsive layout")
    print()
    print("=" * 80)

def main():
    """Main entry point"""
    try:
        # Show welcome message
        show_welcome_message()
        
        # Setup environment
        userdata_path, settings_path = setup_environment()
        print(f"📁 User data path: {userdata_path}")
        print(f"⚙️ Settings path: {settings_path}")
        print()
        
        # Check dependencies
        print("🔍 Checking dependencies...")
        if not check_dependencies():
            print("\n❌ Please install missing dependencies and try again.")
            return 1
        print()
        
        # Launch the enhanced application
        return launch_enhanced_app(userdata_path)
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
        return 0
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 