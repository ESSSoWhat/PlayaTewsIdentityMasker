# FaceAligner Trainer Separation

## Overview

The FaceAligner trainer has been separated from the main DeepFaceLive UI and is now available as a standalone executable. This change improves modularity and allows the trainer to be run independently.

## Changes Made

### 1. Removed from Main UI
- Removed FaceAligner trainer integration from `main.py`
- Removed trainer-related command line arguments
- Cleaned up imports and dependencies

### 2. Created Standalone Executables

#### Windows (train_facealigner.bat)
```batch
# Basic usage
train_facealigner.bat

# With custom paths
train_facealigner.bat "C:\path\to\workspace" "C:\path\to\faceset.dfs"
```

#### Linux/Mac (train_facealigner.sh)
```bash
# Make executable (first time only)
chmod +x train_facealigner.sh

# Basic usage
./train_facealigner.sh

# With custom paths
./train_facealigner.sh "/path/to/workspace" "/path/to/faceset.dfs"
```

#### Direct Python Script (train_facealigner.py)
```bash
# Make executable (first time only)
chmod +x train_facealigner.py

# Basic usage
python3 train_facealigner.py

# With custom paths
python3 train_facealigner.py --workspace-dir "/path/to/workspace" --faceset-path "/path/to/faceset.dfs"

# Show help
python3 train_facealigner.py --help
```

## Usage Instructions

### Prerequisites
- Python 3.x installed and in PATH
- Required dependencies installed:
  - PyTorch with GPU support (recommended)
  - OpenCV (cv2)
  - NumPy
  - Other project dependencies (see requirements files)
- Workspace directory with training data
- Faceset file (.dfs format)

### Running the Trainer

1. **Prepare your data:**
   - Create a workspace directory
   - Prepare your faceset file (.dfs format)

2. **Run the trainer:**
   - **Windows:** Double-click `train_facealigner.bat` or run from command line
   - **Linux/Mac:** Run `./train_facealigner.sh` from terminal

3. **Optional parameters:**
   - First parameter: Workspace directory path
   - Second parameter: Faceset file path
   - If not provided, defaults to `./workspace` and `./faceset.dfs`

### Example Workflow

```bash
# 1. Create workspace directory
mkdir my_training_workspace

# 2. Prepare faceset (you need to create this from your training data)
# ... create faceset.dfs file ...

# 3. Run training
./train_facealigner.sh "my_training_workspace" "faceset.dfs"
```

## Benefits of Separation

1. **Modularity:** Trainer can be run independently of the main application
2. **Resource Management:** Training can be done on separate machines/systems
3. **Simplified UI:** Main application focuses on live face swapping
4. **Flexibility:** Different training configurations can be easily managed

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Ensure Python is installed and in your system PATH
   - Try running `python --version` to verify installation

2. **"Module not found" errors**
   - Install required dependencies: `pip install torch opencv-python numpy`
   - For GPU support: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
   - Check that all project dependencies are installed from requirements files

3. **"Permission denied" (Linux/Mac)**
   - Make the script executable: `chmod +x train_facealigner.sh`

4. **"No training data found"**
   - Verify workspace directory exists and contains training data
   - Check that faceset file path is correct

### Getting Help

- Check the original `DeepFaceLab_Training_Guide.md` for detailed training instructions
- Review the `FaceAlignerTrainerApp.py` source code for advanced configuration
- Ensure your GPU setup is correct for optimal training performance

## Migration from Previous Version

If you were using the trainer through the main application:

1. **Old way:** `python main.py train FaceAligner --workspace-dir path --faceset-path path`
2. **New way:** 
   - `./train_facealigner.sh path path` (Linux/Mac)
   - `train_facealigner.bat path path` (Windows)
   - `python3 train_facealigner.py --workspace-dir path --faceset-path path` (Direct)

The functionality remains the same, only the execution method has changed.

## Files Modified

- `main.py` - Removed trainer integration
- `train_facealigner.bat` - New Windows executable
- `train_facealigner.sh` - New Linux/Mac executable
- `train_facealigner.py` - New standalone Python script
- `TRAINER_SEPARATION_README.md` - This documentation

## Files Unchanged

- `apps/trainers/FaceAligner/` - Trainer implementation remains the same
- All other application files - No changes to core functionality