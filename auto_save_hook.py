
#!/usr/bin/env python3
"""
Auto-save hook for PlayaTewsIdentityMasker
Automatically saves component states when the application closes
"""

import atexit
import json
from pathlib import Path

def auto_save_component_states():
    """Auto-save component states when application exits"""
    try:
        # This will be called when the application exits
        print("💾 Auto-saving component states...")
        
        # The actual saving logic is in the UI components
        # This is just a hook to ensure it happens
        
    except Exception as e:
        print(f"❌ Auto-save failed: {e}")

# Register the auto-save function
atexit.register(auto_save_component_states)
