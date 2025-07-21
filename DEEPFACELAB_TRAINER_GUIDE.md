# DeepFaceLab Trainer Guide

## Overview

This guide explains how to use the DeepFaceLab trainer for training face swap models. The trainer has been integrated into the PlayaTewsIdentityMasker project and can be started using the provided startup scripts.

## Quick Start

### Method 1: Using the Startup Script (Recommended)

1. **Run the startup script:**
   ```bash
   python start_deepfacelab_trainer.py
   ```

2. **Or use the Windows batch file:**
   ```bash
   start_deepfacelab_trainer.bat
   ```

3. **Follow the prompts:**
   - Select your model type (SAEHD is recommended for most cases)
   - The trainer will start automatically

### Method 2: Direct Command Line

Navigate to the DeepFaceLab directory and run:
```bash
cd DeepFaceLab
python main.py train --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model SAEHD --silent-start
```

## Prerequisites

Before starting training, ensure you have:

1. **Training Data Prepared:**
   - Source images in `DeepFaceLab/workspace/data_src/`
   - Destination images in `DeepFaceLab/workspace/data_dst/`
   - Extracted faces in `DeepFaceLab/workspace/data_src/aligned/`
   - Extracted faces in `DeepFaceLab/workspace/data_dst/aligned/`

2. **Dependencies Installed:**
   - Python 3.6+
   - TensorFlow
   - OpenCV
   - NumPy
   - Other required packages (see requirements files)

## Available Models

### 1. SAEHD (Recommended)
- **Best quality** for most use cases
- **Longer training time** but better results
- **Higher memory requirements**

### 2. Quick96
- **Fast training** with lower quality
- **Good for testing** and quick iterations
- **Lower memory requirements**

### 3. AMP (Advanced)
- **Advanced model** with specific use cases
- **Requires more experience** to configure properly

### 4. XSeg
- **For face segmentation** and masking
- **Used for advanced** face swap techniques

## Training Process

### 1. Data Preparation

If you don't have extracted faces yet:

```bash
# Extract faces from source images
python main.py extract --input-dir workspace/data_src --output-dir workspace/data_src/aligned --detector s3fd --face-type whole_face

# Extract faces from destination images  
python main.py extract --input-dir workspace/data_dst --output-dir workspace/data_dst/aligned --detector s3fd --face-type whole_face
```

### 2. Starting Training

When you start the trainer:
- It will ask for a **model name** if no saved models exist
- Choose a descriptive name (e.g., "my_face_swap_model")
- Training will begin automatically

### 3. Training Progress

During training, you'll see:
- **Loss values** decreasing over time
- **Preview images** showing swap quality
- **Training iterations** and progress
- **GPU memory usage** and performance metrics

### 4. Monitoring Training

- **Loss should decrease** over time
- **Preview images** should show improving quality
- **Training can take hours** to days depending on data size and model
- **Save periodically** by pressing 'S' in the trainer window

## Training Tips

### 1. Data Quality
- **Use high-quality images** with clear faces
- **Ensure good lighting** in source and destination images
- **Include various angles** and expressions
- **Remove blurry or low-quality** face images

### 2. Training Parameters
- **Start with default settings** for first training
- **Adjust batch size** based on your GPU memory
- **Use learning rate** of 0.001 for most cases
- **Enable preview** to monitor progress

### 3. Hardware Requirements
- **GPU with 6GB+ VRAM** recommended for SAEHD
- **SSD storage** for faster data loading
- **Adequate RAM** (16GB+ recommended)

## Exporting Models

After training, export your model to DFM format:

```bash
python main.py exportdfm --model-dir workspace/model --model SAEHD
```

The exported DFM file can be used in the main PlayaTewsIdentityMasker application.

## Troubleshooting

### Common Issues

1. **"No saved models found"**
   - This is normal for new training
   - Enter a model name when prompted

2. **AttributeError messages**
   - These are TensorFlow warnings
   - They don't affect training functionality

3. **Out of memory errors**
   - Reduce batch size
   - Use Quick96 model instead of SAEHD
   - Close other applications

4. **Poor training results**
   - Check data quality
   - Ensure sufficient training time
   - Verify face extraction quality

### Getting Help

- Check the DeepFaceLab documentation
- Review training logs in the workspace directory
- Ensure all dependencies are properly installed

## Advanced Usage

### Custom Training Parameters

You can modify training parameters in the model configuration files located in:
```
DeepFaceLab/workspace/model/[model_name]_options.dat
```

### Multiple GPU Training

For systems with multiple GPUs:
```bash
python main.py train --force-gpu-idxs 0,1 --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model SAEHD
```

### CPU Training

For systems without GPU:
```bash
python main.py train --cpu-only --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model SAEHD
```

## Integration with PlayaTewsIdentityMasker

Trained models can be used in the main application:

1. **Export to DFM format** after training
2. **Place DFM file** in the models directory
3. **Select the model** in the main application
4. **Start face swapping** with your trained model

---

For more detailed information, refer to the DeepFaceLab documentation and the project's README files. 