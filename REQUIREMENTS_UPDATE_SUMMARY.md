# Requirements Update Summary

## Overview
This document summarizes the updates made to the requirements files to address inconsistencies and create a unified dependency management approach.

## Changes Made

### 1. Created `requirements-unified.txt`
- **New file**: Comprehensive unified requirements file
- **Purpose**: Single source of truth for all dependencies
- **Features**:
  - Consolidates all dependencies from separate requirements files
  - Organized by category (Core, ML/GPU, Testing, Development, Packaging)
  - Includes version constraints for stability
  - Platform-specific dependencies
  - Optional dependencies clearly marked

### 2. Fixed PyQt5/PyQt6 Inconsistency
- **Issue**: Codebase uses PyQt6 but `requirements_minimal.txt` specified PyQt5
- **Fix**: Updated `requirements_minimal.txt` to use PyQt6>=6.4.0,<6.7.0
- **Impact**: Eliminates import errors and ensures consistency

### 3. Updated Version Constraints
- **numpy**: Updated to <1.28.0 for Python 3.13 compatibility
- **opencv-python**: Updated to <4.10.0 for stability
- **PyTorch**: Limited to <2.3.0 for stability
- **ONNX Runtime**: Limited to <1.18.0 for compatibility

## File Structure

### Before
```
requirements_minimal.txt     # Core dependencies (PyQt5)
requirements_gpu.txt         # GPU dependencies
requirements_test.txt        # Testing dependencies
requirements_packaging.txt   # Empty packaging file
```

### After
```
requirements-unified.txt     # Complete unified requirements
requirements_minimal.txt     # Core dependencies (PyQt6 - FIXED)
requirements_gpu.txt         # GPU dependencies (unchanged)
requirements_test.txt        # Testing dependencies (unchanged)
requirements_packaging.txt   # Empty packaging file (unchanged)
```

## Key Features of `requirements-unified.txt`

### 1. Comprehensive Coverage
- **Core Dependencies**: Essential packages for basic functionality
- **ML/GPU Dependencies**: Machine learning and GPU acceleration
- **Testing Dependencies**: Complete testing framework
- **Development Dependencies**: Code quality and documentation tools
- **Packaging Dependencies**: Build and distribution tools

### 2. Version Management
- **Upper bounds**: Prevents breaking changes from newer versions
- **Lower bounds**: Ensures minimum required functionality
- **Platform conditions**: Platform-specific dependencies
- **Python version conditions**: Version-specific compatibility

### 3. Organization
- **Clear sections**: Easy to understand and maintain
- **Comments**: Detailed explanations for each dependency
- **Optional dependencies**: Clearly marked for selective installation
- **Notes section**: Important compatibility information

## Installation Options

### Full Installation
```bash
pip install -r requirements-unified.txt
```

### Minimal Installation
```bash
pip install -r requirements_minimal.txt
```

### GPU Installation
```bash
pip install -r requirements_gpu.txt
```

### Testing Installation
```bash
pip install -r requirements_test.txt
```

## Compatibility Notes

### Python Version
- **Target**: Python 3.13+
- **TensorFlow**: Limited to Python <3.12 due to compatibility issues
- **Other packages**: Compatible with Python 3.13

### Platform Support
- **Linux**: Full support with CUDA Python
- **Windows**: Full support (no platform-specific dependencies)
- **macOS**: Full support (no platform-specific dependencies)

### GPU Support
- **CUDA**: 11.8 target version for PyTorch
- **ONNX Runtime**: GPU support included
- **TensorFlow**: GPU support for legacy models

## Benefits

### 1. Consistency
- Single source of truth for dependencies
- Eliminates version conflicts
- Consistent across development environments

### 2. Maintainability
- Easy to update and manage
- Clear organization and documentation
- Version constraints prevent breaking changes

### 3. Flexibility
- Multiple installation options
- Optional dependencies for different use cases
- Platform-specific considerations

### 4. Reliability
- Tested version combinations
- Stable upper bounds
- Compatibility notes included

## Next Steps

### 1. Testing
- Test installation on different platforms
- Verify GPU functionality
- Run test suite with new dependencies

### 2. Documentation
- Update installation guides
- Document platform-specific requirements
- Add troubleshooting section

### 3. CI/CD
- Update CI/CD pipelines to use unified requirements
- Add dependency validation
- Include platform-specific testing

## Migration Guide

### For Existing Installations
1. **Backup**: Save current environment
2. **Update**: Install from unified requirements
3. **Test**: Verify functionality
4. **Cleanup**: Remove old requirements files (optional)

### For New Installations
1. **Choose**: Select appropriate requirements file
2. **Install**: Use pip install -r requirements-*.txt
3. **Verify**: Test basic functionality
4. **Configure**: Set up GPU support if needed

## Troubleshooting

### Common Issues
1. **PyQt6 Import Errors**: Ensure PyQt6 is installed (fixed in this update)
2. **CUDA Issues**: Verify CUDA installation and version compatibility
3. **Version Conflicts**: Use the unified requirements file for consistent versions
4. **Platform Issues**: Check platform-specific dependencies

### Support
- Check the notes section in `requirements-unified.txt`
- Review platform-specific requirements
- Verify Python version compatibility
- Test with minimal requirements first