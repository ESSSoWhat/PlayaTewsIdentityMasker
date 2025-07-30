#!/usr/bin/env python3
"""
Fix DFM Model Loading Issues
Ensures DFM models are properly loaded in PlayaTewsIdentityMasker
"""

import os
import sys
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_dfm_loading():
    """Fix DFM model loading issues"""
    print("🔧 Fixing DFM Model Loading Issues...")
    print("=" * 50)
    
    base_dir = Path.cwd()
    dfm_models_dir = base_dir / "dfm_models"
    userdata_dfm_dir = base_dir / "userdata" / "dfm_models"
    
    # Ensure userdata/dfm_models directory exists
    userdata_dfm_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Userdata DFM directory: {userdata_dfm_dir}")
    
    # Check what models are available
    available_models = []
    
    # Check main dfm_models directory
    if dfm_models_dir.exists():
        for file in dfm_models_dir.glob("*.dfm"):
            if file.is_file():
                available_models.append(file)
                print(f"✅ Found model: {file.name}")
    
    # Check userdata/dfm_models directory
    if userdata_dfm_dir.exists():
        for file in userdata_dfm_dir.glob("*.dfm"):
            if file.is_file():
                available_models.append(file)
                print(f"✅ Found model in userdata: {file.name}")
    
    if not available_models:
        print("❌ No DFM models found!")
        print("💡 Please run: python download_all_dfm_models.py")
        return False
    
    # Copy models to userdata/dfm_models if they're not there
    models_copied = 0
    for model_file in available_models:
        target_file = userdata_dfm_dir / model_file.name
        
        if not target_file.exists():
            print(f"📋 Copying {model_file.name} to userdata...")
            try:
                shutil.copy2(model_file, target_file)
                models_copied += 1
                print(f"✅ Copied {model_file.name}")
            except Exception as e:
                print(f"❌ Failed to copy {model_file.name}: {e}")
        else:
            print(f"✅ {model_file.name} already in userdata")
    
    # List final models in userdata
    print("\n📋 Final DFM Models in userdata/dfm_models:")
    print("-" * 40)
    userdata_models = list(userdata_dfm_dir.glob("*.dfm"))
    for model in userdata_models:
        size_mb = model.stat().st_size / (1024 * 1024)
        print(f"  • {model.name} ({size_mb:.1f}MB)")
    
    print(f"\n🎉 DFM Loading Fix Complete!")
    print(f"📊 Total models available: {len(userdata_models)}")
    print(f"📋 Models copied: {models_copied}")
    
    if userdata_models:
        print("\n💡 Next Steps:")
        print("1. Restart the PlayaTewsIdentityMasker app")
        print("2. Go to Face Swap settings")
        print("3. Select a model from the dropdown")
        print("4. Enable face swapping")
        
        return True
    else:
        print("\n❌ No models available after fix!")
        return False

def verify_model_registry():
    """Verify the model registry is working"""
    print("\n🔍 Verifying Model Registry...")
    
    try:
        # Try to import the modelhub module
        import sys
        sys.path.append(str(Path.cwd()))
        
        from modelhub import DFLive
        
        userdata_dfm_dir = Path.cwd() / "userdata" / "dfm_models"
        if userdata_dfm_dir.exists():
            models_info = DFLive.get_available_models_info(userdata_dfm_dir)
            print(f"✅ Model registry found {len(models_info)} models")
            
            for model_info in models_info:
                print(f"  • {model_info.get_name()}")
            
            return True
        else:
            print("❌ userdata/dfm_models directory not found")
            return False
            
    except Exception as e:
        print(f"❌ Model registry error: {e}")
        return False

if __name__ == "__main__":
    print("🎬 PlayaTewsIdentityMasker - DFM Loading Fix")
    print("=" * 50)
    
    success = fix_dfm_loading()
    
    if success:
        print("\n🔍 Running verification...")
        verify_model_registry()
    
    print("\n✨ Fix complete! Restart the app to see the models.") 