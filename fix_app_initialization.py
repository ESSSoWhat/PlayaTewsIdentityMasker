#!/usr/bin/env python3
"""
Fix Application Initialization
Adds missing initialize method to PlayaTewsIdentityMaskerApp
"""

import os
import sys
from pathlib import Path

def fix_app_initialization():
    """Fix the missing initialize method in PlayaTewsIdentityMaskerApp"""
    
    app_file = Path("apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py")
    
    if not app_file.exists():
        print("❌ PlayaTewsIdentityMaskerApp.py not found!")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if initialize method already exists
    if "def initialize(self):" in content:
        print("✅ Initialize method already exists!")
        return True
    
    # Find the end of the PlayaTewsIdentityMaskerApp class
    class_start = content.find("class PlayaTewsIdentityMaskerApp(qtx.QXMainApplication):")
    if class_start == -1:
        print("❌ PlayaTewsIdentityMaskerApp class not found!")
        return False
    
    # Find the end of the class (next class or end of file)
    class_end = content.find("\nclass ", class_start + 1)
    if class_end == -1:
        class_end = len(content)
    
    # Add the initialize method before the end of the class
    initialize_method = '''
    def initialize(self):
        """Initialize the application"""
        try:
            # Initialize the QLiveSwap instance
            if hasattr(self, 'q_live_swap'):
                self.q_live_swap.initialize()
                print("✅ QLiveSwap initialized successfully")
            
            # Initialize the main window
            if hasattr(self, 'main_window'):
                self.main_window.show()
                print("✅ Main window displayed successfully")
            
            print("✅ PlayaTewsIdentityMaskerApp initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing application: {e}")
            raise
    
    def run(self):
        """Run the application"""
        try:
            # Start the Qt event loop
            return self.exec_()
        except Exception as e:
            print(f"❌ Error running application: {e}")
            raise
'''
    
    # Insert the methods before the end of the class
    insert_pos = class_end
    new_content = content[:insert_pos] + initialize_method + content[insert_pos:]
    
    # Write the updated content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Application initialization fixed successfully!")
    print("🔧 Added methods:")
    print("   - initialize(): Initializes QLiveSwap and main window")
    print("   - run(): Runs the Qt event loop")
    
    return True

def test_app_initialization():
    """Test if the app can be imported and initialized"""
    print("\n🧪 Testing application initialization...")
    
    try:
        # Import the app class
        sys.path.append(str(Path.cwd()))
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        print("✅ PlayaTewsIdentityMaskerApp imported successfully")
        
        # Test creating an instance
        userdata_path = Path.cwd()
        app = PlayaTewsIdentityMaskerApp(userdata_path)
        print("✅ PlayaTewsIdentityMaskerApp instance created successfully")
        
        # Test if initialize method exists
        if hasattr(app, 'initialize'):
            print("✅ Initialize method exists")
        else:
            print("❌ Initialize method missing")
            return False
        
        # Test if run method exists
        if hasattr(app, 'run'):
            print("✅ Run method exists")
        else:
            print("❌ Run method missing")
            return False
        
        print("✅ Application initialization test passed")
        
    except Exception as e:
        print(f"❌ Error testing application initialization: {e}")
        return False
    
    return True

def main():
    """Main function to fix application initialization"""
    print("🔧 Fixing Application Initialization")
    print("=" * 50)
    
    # Fix the application initialization
    if fix_app_initialization():
        # Test the fix
        test_app_initialization()
        
        print("\n🎉 Application initialization fix completed!")
        print("\n📋 Next steps:")
        print("1. The application should now start properly")
        print("2. Try running: python start_playatews_patched.py")
        print("3. The source buttons should be functional")
        
    else:
        print("❌ Failed to fix application initialization!")

if __name__ == "__main__":
    main() 