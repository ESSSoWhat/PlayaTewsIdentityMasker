#!/usr/bin/env python3
"""
Diagnostic script to locate and check the PlayaTewsIdentityMasker application window
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

class WindowFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlayaTewsIdentityMasker Window Finder")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔍 PlayaTewsIdentityMasker Window Finder")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("""
This tool will help you locate the PlayaTewsIdentityMasker application window.

Instructions:
1. Make sure PlayaTewsIdentityMasker is running
2. Click 'Find Windows' below
3. Look for the results in the text area
4. Follow the guidance to locate your window
        """)
        layout.addWidget(instructions)
        
        # Find button
        self.find_btn = QPushButton("🔍 Find PlayaTewsIdentityMasker Windows")
        self.find_btn.clicked.connect(self.find_windows)
        layout.addWidget(self.find_btn)
        
        # Results area
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)
        
        # Status
        self.status = QLabel("Ready to search for windows...")
        layout.addWidget(self.status)
        
        self.setLayout(layout)
        
    def find_windows(self):
        """Find all windows and look for PlayaTewsIdentityMasker"""
        self.results.clear()
        self.status.setText("Searching for windows...")
        
        try:
            # Get all top-level windows
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            windows = app.topLevelWidgets()
            
            self.results.append("🔍 SEARCHING FOR WINDOWS...\n")
            self.results.append(f"Found {len(windows)} top-level windows:\n")
            
            playatews_found = False
            
            for i, window in enumerate(windows):
                if window.isVisible():
                    title = window.windowTitle()
                    class_name = window.__class__.__name__
                    
                    self.results.append(f"Window {i+1}:")
                    self.results.append(f"  Title: '{title}'")
                    self.results.append(f"  Class: {class_name}")
                    self.results.append(f"  Visible: {window.isVisible()}")
                    self.results.append(f"  Geometry: {window.geometry()}")
                    self.results.append("")
                    
                    # Check if this looks like PlayaTewsIdentityMasker
                    if any(keyword in title.lower() for keyword in ['playatews', 'identity', 'masker', 'deepface']):
                        playatews_found = True
                        self.results.append("🎯 LIKELY PLAYA TEWS WINDOW FOUND!")
                        self.results.append("This appears to be the PlayaTewsIdentityMasker application.")
                        self.results.append("")
            
            if not playatews_found:
                self.results.append("⚠️ No obvious PlayaTewsIdentityMasker window found.")
                self.results.append("The application might be:")
                self.results.append("  - Minimized to system tray")
                self.results.append("  - Running in background")
                self.results.append("  - Not fully launched yet")
                self.results.append("")
            
            self.results.append("📋 NEXT STEPS:")
            self.results.append("1. Look for any of the windows listed above")
            self.results.append("2. If you see a PlayaTewsIdentityMasker window:")
            self.results.append("   - Click on it to bring it to front")
            self.results.append("   - Look for tabs or panels")
            self.results.append("   - Find the 'Viewers' tab")
            self.results.append("   - Look for 'Camera Feed' section")
            self.results.append("3. If no window is found, restart the application")
            
            self.status.setText("Search completed!")
            
        except Exception as e:
            self.results.append(f"❌ Error searching for windows: {e}")
            self.status.setText("Error occurred during search")

def main():
    app = QApplication(sys.argv)
    finder = WindowFinder()
    finder.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 