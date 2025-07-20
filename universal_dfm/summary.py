#!/usr/bin/env python3
"""
Universal DFM System Summary
Shows the current state and statistics of the universal DFM system
"""

import json
import time
from pathlib import Path
from dfm_integration import check_system_status, list_available_models

def print_summary():
    """Print a comprehensive summary of the universal DFM system"""
    print("🎯 Universal DFM System Summary")
    print("=" * 60)
    
    # Get system status
    status = check_system_status()
    
    if status['status'] == 'active':
        print(f"✅ System Status: {status['status'].upper()}")
        print(f"📁 Base Directory: {status['base_directory']}")
        print(f"📊 Total Models: {status['total_models']}")
        print(f"🕒 Last Updated: {status['last_updated']}")
        
        print("\n📂 Model Categories:")
        for category, count in status['categories'].items():
            if count > 0:
                print(f"  • {category.capitalize()}: {count} models")
        
        print("\n🔍 Model Details:")
        for category in ['prebuilt', 'custom', 'active', 'archived']:
            models = list_available_models(category)
            if models:
                print(f"\n{category.upper()} ({len(models)} models):")
                for model in models[:8]:  # Show first 8
                    print(f"  - {model}")
                if len(models) > 8:
                    print(f"  ... and {len(models) - 8} more")
        
        print("\n💡 Quick Commands:")
        print("  • List all models: python dfm_manager.py list")
        print("  • List prebuilt: python dfm_manager.py list --category prebuilt")
        print("  • Get model info: python dfm_manager.py info --model-name 'model_name'")
        print("  • Add new model: python dfm_manager.py add --model-path 'path.dfm' --category custom")
        
        print("\n🔧 Integration:")
        print("  • Use dfm_integration.py for programmatic access")
        print("  • Import: from dfm_integration import get_model_path, list_available_models")
        
    else:
        print(f"❌ System Status: {status['status']}")
        print("Run populate_registry.py to initialize the system")
    
    print("\n" + "=" * 60)
    print("🎉 Universal DFM System Ready!")

if __name__ == "__main__":
    print_summary() 