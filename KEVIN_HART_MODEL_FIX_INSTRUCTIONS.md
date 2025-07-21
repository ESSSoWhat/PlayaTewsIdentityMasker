
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
