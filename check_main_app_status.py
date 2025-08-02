#!/usr/bin/env python3
"""
Check Main App Status for PlayaTewsIdentityMasker
Identifies Qt application issues preventing camera display
"""

import subprocess
import time
from pathlib import Path

def check_running_processes():
    """Check what processes are currently running"""
    print("🔍 Checking Running Processes...")
    print("=" * 50)
    
    try:
        # Check for Python processes
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if "python.exe" in result.stdout:
            print("✅ Python processes running:")
            lines = result.stdout.split('\n')
            for line in lines:
                if "python.exe" in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ No Python processes running")
            
    except Exception as e:
        print(f"❌ Process check error: {e}")

def check_main_app_logs():
    """Check for any error logs from the main app"""
    print("\n🔍 Checking for Error Logs...")
    print("=" * 50)
    
    # Look for common log files
    log_patterns = [
        "*.log",
        "error*.txt",
        "debug*.txt"
    ]
    
    for pattern in log_patterns:
        log_files = list(Path('.').glob(pattern))
        for log_file in log_files:
            print(f"📄 Found log file: {log_file}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "error" in content.lower() or "exception" in content.lower():
                        print(f"   ⚠️ Contains errors/exceptions")
                        # Show last few lines
                        lines = content.split('\n')
                        for line in lines[-5:]:
                            if line.strip():
                                print(f"   {line.strip()}")
            except Exception as e:
                print(f"   ❌ Error reading log: {e}")

def check_qt_application():
    """Check if Qt application is properly initialized"""
    print("\n🔍 Checking Qt Application Status...")
    print("=" * 50)
    
    try:
        # Try to import Qt components
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QThread
        
        # Check if QApplication instance exists
        app = QApplication.instance()
        if app is not None:
            print("✅ QApplication instance exists")
            print(f"   Application name: {app.applicationName()}")
            print(f"   Application version: {app.applicationVersion()}")
        else:
            print("❌ No QApplication instance found")
            
        # Check thread information
        current_thread = QThread.currentThread()
        print(f"   Current thread: {current_thread}")
        print(f"   Thread is running: {current_thread.isRunning()}")
        
    except Exception as e:
        print(f"❌ Qt application check error: {e}")
        import traceback
        traceback.print_exc()

def check_camera_ui_connection():
    """Check camera UI connection in main app context"""
    print("\n🔍 Checking Camera UI Connection...")
    print("=" * 50)
    
    try:
        # Import main app components
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import QLiveSwap
        
        print("✅ Main app components import successful")
        
        # Check if we can create UI components
        from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import QBCFrameViewer
        print("✅ QBCFrameViewer import successful")
        
        # Check if backend components are available
        from apps.PlayaTewsIdentityMasker import backend
        print("✅ Backend components import successful")
        
        print("✅ All components available for UI connection")
        
    except Exception as e:
        print(f"❌ Camera UI connection check error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🎬 PlayaTewsIdentityMasker - Main App Status Check")
    print("=" * 60)
    print()
    
    check_running_processes()
    check_main_app_logs()
    check_qt_application()
    check_camera_ui_connection()
    
    print("\n📊 Status Check Complete!")
    print("=" * 40)
    print("\n🔧 Recommendations:")
    print("1. Ensure main app is running with proper Qt context")
    print("2. Check for Qt application initialization issues")
    print("3. Verify UI components are properly connected")
    print("4. Look for thread-related Qt errors")

if __name__ == "__main__":
    main() 