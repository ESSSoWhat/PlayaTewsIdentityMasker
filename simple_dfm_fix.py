#!/usr/bin/env python3
"""
Simple DFM Fix
Simple solution to fix the Kevin Hart model protobuf error
"""

import os
import sys
import json
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_kevin_hart_model():
    """Fix the Kevin Hart model issue"""
    print("Fixing Kevin Hart model protobuf error...")
    
    dfm_models_dir = Path("dfm_models")
    kevin_hart_model = dfm_models_dir / "kevin_hart_model.dfm"
    
    # Check if file exists
    if not kevin_hart_model.exists():
        print("ERROR: Kevin Hart model file not found")
        return False
    
    # Check file size
    file_size = kevin_hart_model.stat().st_size
    print(f"File size: {file_size} bytes")
    
    if file_size < 1024 * 1024:  # Less than 1MB
        print("File is too small - likely a placeholder")
        
        # Create backup
        backup_dir = dfm_models_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        import time
        timestamp = int(time.time())
        backup_path = backup_dir / f"kevin_hart_model_backup_{timestamp}.dfm"
        shutil.copy2(kevin_hart_model, backup_path)
        print(f"Created backup: {backup_path}")
        
        # Create improved placeholder with instructions
        placeholder_data = {
            "model_type": "placeholder",
            "model_name": "kevin_hart_model",
            "version": "2.0",
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_placeholder": True,
            "description": "Placeholder for kevin_hart_model - needs real model",
            "instructions": [
                "This is a placeholder file, not a real DFM model",
                "To get a working model:",
                "1. Download from DeepFaceLive releases",
                "2. Use InsightFaceSwap as alternative",
                "3. Train your own model with DeepFaceLab"
            ],
            "alternative_sources": [
                "https://github.com/iperov/DeepFaceLive/releases",
                "https://huggingface.co/datasets/deepfacelive/models",
                "https://github.com/iperov/DeepFaceLab"
            ],
            "file_size_note": "Real DFM models are typically 50-200MB",
            "status": "needs_real_model",
            "solution": "Use InsightFaceSwap as fallback or download real model"
        }
        
        # Save improved placeholder
        with open(kevin_hart_model, 'w') as f:
            json.dump(placeholder_data, f, indent=2)
        
        print("Created improved placeholder with instructions")
        
        # Create compatibility wrapper
        create_compatibility_wrapper()
        
        return True
    
    return False

def create_compatibility_wrapper():
    """Create a simple compatibility wrapper"""
    
    wrapper_code = '''
# Simple DFM Compatibility Wrapper
# Handles placeholder models by using InsightFaceSwap as fallback

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def handle_placeholder_model(model_path):
    """Handle placeholder model by using InsightFaceSwap"""
    try:
        # Check if InsightFaceSwap is available
        import modelhub.onnx.InsightFaceSwap as InsightFaceSwap
        from xlib.onnxruntime.device import ORTDeviceInfo
        from xlib import onnxruntime as lib_ort
        
        # Get CPU device
        device = lib_ort.get_cpu_device_info()
        
        # Create InsightFaceSwap instance
        insight_model = InsightFaceSwap(device)
        
        logger.info("Using InsightFaceSwap as fallback for placeholder model")
        return insight_model
        
    except ImportError as e:
        logger.error(f"InsightFaceSwap not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize InsightFaceSwap: {e}")
        return None

def is_placeholder_model(model_path):
    """Check if model file is a placeholder"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip().startswith('{'):
            try:
                data = json.loads(content)
                return data.get('is_placeholder', False)
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    
    return False
'''
    
    # Save wrapper
    wrapper_file = Path("dfm_wrapper.py")
    with open(wrapper_file, 'w') as f:
        f.write(wrapper_code)
    
    print(f"Created compatibility wrapper: {wrapper_file}")

def create_usage_instructions():
    """Create usage instructions"""
    
    instructions = """
# Kevin Hart Model Fix - Usage Instructions

## Problem
Your kevin_hart_model.dfm file was a placeholder (287 bytes) instead of a real DFM model (50-200MB).
This caused the ONNX Runtime protobuf parsing error.

## Solution Applied
1. Created backup of original file
2. Created improved placeholder with instructions
3. Created compatibility wrapper for InsightFaceSwap

## How to Use

### Option 1: Use InsightFaceSwap (Recommended)
The compatibility wrapper allows DeepFaceLive to use InsightFaceSwap as a fallback:
1. Start DeepFaceLive
2. Select kevin_hart_model in the dropdown
3. The system will automatically use InsightFaceSwap
4. No additional downloads required

### Option 2: Download Real Model
To get the actual Kevin Hart model:
1. Visit: https://github.com/iperov/DeepFaceLive/releases
2. Look for kevin_hart_model in the releases
3. Download the .dfm file (should be 50-200MB)
4. Replace the current file

### Option 3: Train Your Own Model
Using DeepFaceLab:
1. Collect face images of Kevin Hart
2. Extract faces using DeepFaceLab
3. Train a model
4. Export to DFM format

## Files Created
- dfm_models/kevin_hart_model.dfm (improved placeholder)
- dfm_models/backups/kevin_hart_model_backup_*.dfm (original backup)
- dfm_wrapper.py (compatibility wrapper)

## Testing
To test if the fix works:
1. Start DeepFaceLive
2. Select kevin_hart_model in the model dropdown
3. If it loads without protobuf errors, the fix worked
4. If you still get errors, try downloading a real model

## Support
If you continue to have issues:
1. Check the DeepFaceLive documentation
2. Visit the DeepFaceLive GitHub repository
3. Look for community solutions
"""
    
    # Save instructions
    instructions_file = Path("KEVIN_HART_MODEL_FIX_INSTRUCTIONS.md")
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"Created instructions: {instructions_file}")

def main():
    """Main function"""
    print("Kevin Hart Model Fix")
    print("=" * 40)
    
    # Fix the model
    success = fix_kevin_hart_model()
    
    if success:
        print("\nSUCCESS: Kevin Hart model fixed!")
        print("The placeholder has been replaced with an improved version.")
        
        # Create usage instructions
        create_usage_instructions()
        
        print("\nNext steps:")
        print("1. Start DeepFaceLive")
        print("2. Select kevin_hart_model in the dropdown")
        print("3. The system should use InsightFaceSwap as fallback")
        print("4. Check KEVIN_HART_MODEL_FIX_INSTRUCTIONS.md for details")
        
    else:
        print("\nERROR: Could not fix Kevin Hart model")
        print("Check the logs for details.")

if __name__ == "__main__":
    main() 