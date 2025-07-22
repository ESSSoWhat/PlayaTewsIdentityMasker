#!/usr/bin/env python3
"""
Fix QSimpleLazyLoader Issue
"""

import os
import sys
from pathlib import Path

def fix_lazy_loader():
    """Fix the QSimpleLazyLoader create_placeholder issue"""
    print("🔧 Fixing QSimpleLazyLoader issue...")
    
    # Find the QSimpleLazyLoader file
    lazy_loader_path = Path("apps/PlayaTewsIdentityMasker/ui/QSimpleLazyLoader.py")
    
    if not lazy_loader_path.exists():
        print("   ❌ QSimpleLazyLoader.py not found")
        return False
    
    try:
        # Read the current file
        with open(lazy_loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if create_placeholder method exists
        if 'def create_placeholder' not in content:
            print("   Adding create_placeholder method...")
            
            # Add the missing method
            placeholder_method = '''
    def create_placeholder(self, component_name: str):
        """Create a placeholder widget for lazy loading"""
        from xlib.qt.widgets.QXLabel import QXLabel
        placeholder = QXLabel(f"Loading {component_name}...")
        placeholder.setStyleSheet("QLabel { color: gray; font-style: italic; }")
        return placeholder
'''
            
            # Insert the method before the last closing brace
            if 'class QSimpleLazyLoader' in content:
                # Find the end of the class
                lines = content.split('\n')
                insert_index = -1
                for i, line in enumerate(lines):
                    if line.strip() == '}' or line.strip() == 'pass':
                        insert_index = i
                        break
                
                if insert_index != -1:
                    lines.insert(insert_index, placeholder_method)
                    content = '\n'.join(lines)
                    
                    # Write back the fixed content
                    with open(lazy_loader_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("   ✅ Fixed QSimpleLazyLoader")
                    return True
                else:
                    print("   ❌ Could not find insertion point")
                    return False
            else:
                print("   ❌ Could not find QSimpleLazyLoader class")
                return False
        else:
            print("   ✅ create_placeholder method already exists")
            return True
            
    except Exception as e:
        print(f"   ❌ Error fixing lazy loader: {e}")
        return False

def create_working_app_starter():
    """Create a working app starter that bypasses the lazy loader issue"""
    print("📝 Creating working app starter...")
    
    starter_code = '''#!/usr/bin/env python3
"""
Working PlayaTewsIdentityMasker App Starter
Bypasses lazy loader issues
"""

import sys
import os
from pathlib import Path

def start_app():
    """Start the PlayaTewsIdentityMasker app"""
    print("🎯 Starting PlayaTewsIdentityMasker...")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    try:
        # Set environment variable to disable lazy loading
        os.environ['DISABLE_LAZY_LOADING'] = '1'
        
        # Try to import the app
        print("📦 Importing application...")
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        # Set up userdata path
        userdata_path = current_dir / "userdata"
        userdata_path.mkdir(exist_ok=True)
        
        print(f"📁 Using userdata path: {userdata_path}")
        
        # Create and run the app
        print("🚀 Creating application...")
        app = PlayaTewsIdentityMaskerApp(userdata_path=userdata_path)
        
        print("✅ Application created successfully!")
        print("🪟 The app window should appear shortly...")
        print("💡 If you don't see it, check your taskbar or try Alt+Tab")
        
        # Run the app
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("💡 Check the log file: playatewsidentitymasker.log")
        return False
    
    return True

if __name__ == "__main__":
    success = start_app()
    if not success:
        print("\\n🔧 Troubleshooting:")
        print("1. Make sure Python is installed")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Check the log file for detailed errors")
        print("4. Try running as Administrator")
        
        input("\\nPress Enter to exit...")
'''
    
    starter_path = Path("start_app_working.py")
    with open(starter_path, 'w', encoding='utf-8') as f:
        f.write(starter_code)
    
    print(f"   ✅ Created: {starter_path}")
    return starter_path

def main():
    """Main function"""
    print("🎯 PlayaTewsIdentityMasker Lazy Loader Fix")
    print("=" * 50)
    
    # Step 1: Fix the lazy loader
    lazy_loader_fixed = fix_lazy_loader()
    
    # Step 2: Create working app starter
    working_starter = create_working_app_starter()
    
    print("\n" + "=" * 50)
    print("🎉 Fix Complete!")
    print("\nResults:")
    print(f"   Lazy Loader: {'✅ Fixed' if lazy_loader_fixed else '❌ Failed'}")
    print(f"   Working Starter: ✅ Created")
    
    print("\nNext Steps:")
    print("1. Try the working app starter:")
    print(f"   python {working_starter.name}")
    print("\n2. Or try the original starter:")
    print("   python start_app_simple.py")
    print("\n3. Or use the batch script:")
    print("   start_playatews_app.bat")
    
    if lazy_loader_fixed:
        print("\n✅ Lazy loader issue should be resolved!")
    else:
        print("\n⚠️ Lazy loader issue may persist")
        print("Try the working app starter instead")

if __name__ == "__main__":
    main() 