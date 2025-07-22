# PlayaTewsIdentityMasker - Local Python Environment Setup

This guide explains how to configure PlayaTewsIdentityMasker to use the local Python311 directory for all dependencies.

## 🎯 Overview

The application is now configured to use the local Python311 directory located at:
```
C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\
```

This ensures that all Python dependencies are isolated to this project and won't interfere with your system Python installation.

## 📁 Local Python Structure

```
Python311/
├── Scripts/           # Executables (pip, etc.)
└── site-packages/     # Python packages
    ├── numpy/         # Numerical computing
    ├── cv2/           # OpenCV
    ├── PyQt5/         # GUI framework
    ├── torch/         # PyTorch
    ├── tensorflow/    # TensorFlow
    └── ...            # Other packages
```

## 🚀 How to Start the Application

### Method 1: Using the Local Python Launcher (Recommended)
```bash
python run_with_local_python.py
```

This script automatically:
- Sets up the Python path to use local packages
- Configures environment variables
- Tests package imports
- Launches the application

### Method 2: Using the Original Launcher
```bash
python run_obs_style.py
```

### Method 3: Using Main Script
```bash
python main.py run PlayaTewsIdentityMasker
```

## 🔧 Installing Additional Dependencies

To install new packages to the local Python311 directory:

```bash
# Install a single package
Python311\Scripts\pip.exe install --target=Python311\site-packages package_name

# Install from requirements file
Python311\Scripts\pip.exe install --target=Python311\site-packages -r requirements_file.txt

# Upgrade existing packages
Python311\Scripts\pip.exe install --target=Python311\site-packages --upgrade package_name
```

## 📦 Currently Installed Packages

The local Python311 environment includes:

### Core Dependencies
- **NumPy** (1.26.4) - Numerical computing
- **OpenCV** (4.8.1) - Computer vision
- **PyQt5** (5.15.11) - GUI framework
- **Pillow** (11.3.0) - Image processing
- **psutil** (7.0.0) - System monitoring
- **PyYAML** (6.0.2) - Configuration files
- **ffmpeg-python** (0.2.0) - Video processing

### Machine Learning
- **PyTorch** - Deep learning framework
- **TensorFlow** - Machine learning framework
- **ONNX Runtime** - Model inference
- **Transformers** - NLP models

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Linting

## 🌍 Environment Variables

The local Python environment sets these variables:

```bash
PYTHONPATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\site-packages
PATH=C:\Users\son-l\Desktop\PlayaTewsIdentityMasker\PlayaTewsIdentityMasker-master\Python311\Scripts
```

## 🔍 Verification

To verify that the local Python environment is working:

```bash
python run_with_local_python.py
```

You should see:
```
✅ NumPy 1.26.4 imported from local directory
✅ OpenCV 4.8.1 imported from local directory
✅ PyQt5 imported from local directory
```

## 🛠️ Troubleshooting

### Package Import Errors
If you get import errors, install missing packages:
```bash
Python311\Scripts\pip.exe install --target=Python311\site-packages missing_package
```

### Version Conflicts
If there are version conflicts, you can install specific versions:
```bash
Python311\Scripts\pip.exe install --target=Python311\site-packages package==version
```

### Path Issues
Make sure the Python311 directory exists and contains the site-packages folder.

## 📋 Benefits of Local Python Environment

1. **Isolation**: Dependencies don't interfere with system Python
2. **Portability**: Easy to move or share the project
3. **Version Control**: Specific package versions for the project
4. **Clean Environment**: No conflicts with other projects
5. **Easy Cleanup**: Simply delete the Python311 directory to reset

## 🎯 Next Steps

1. **Start the Application**: Use `python run_with_local_python.py`
2. **Configure Settings**: Set up your workspace and models
3. **Install Models**: Download face-swapping models to the dfm_models directory
4. **Test Features**: Try face detection, swapping, and streaming features

## 📞 Support

If you encounter issues:
1. Check that all packages are installed in the local directory
2. Verify the Python311 directory structure
3. Try reinstalling packages with the `--upgrade` flag
4. Check the application logs for specific error messages 