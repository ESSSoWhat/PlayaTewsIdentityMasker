# DeepFaceLab Training Guide

## Overview

This guide covers the complete workflow for training custom face swap models using DeepFaceLab and then using them in DeepFaceLive for real-time streaming.

## Prerequisites

✅ **GPU Setup Complete:**
- NVIDIA RTX 3050 with CUDA 12.8
- PyTorch with GPU support
- ONNX Runtime with GPU support
- DeepFaceLab repository cloned

## Directory Structure

```
DeepFaceLab/
├── workspace/
│   ├── data_src/          # Source face images (person A)
│   │   └── aligned/       # Extracted and aligned faces
│   ├── data_dst/          # Destination face images (person B)
│   │   └── aligned/       # Extracted and aligned faces
│   └── model/             # Trained models will be saved here
├── main.py                # Main training script
└── models/                # Available model architectures
    ├── Model_SAEHD/       # High-quality model (recommended)
    ├── Model_Quick96/     # Fast training model
    └── Model_AMP/         # Advanced model
```

## Complete Workflow

### Step 1: Prepare Source and Destination Images

1. **Source Images (Person A):** The person whose face you want to swap FROM
   - Place high-quality images of Person A in `workspace/data_src/`
   - Multiple angles, expressions, lighting conditions
   - Recommended: 1000-5000 images

2. **Destination Images (Person B):** The person whose face you want to swap TO
   - Place images of Person B in `workspace/data_dst/`
   - Should match the source video/stream
   - Recommended: 1000-5000 images

### Step 2: Extract Faces

```bash
# Navigate to DeepFaceLab directory
cd DeepFaceLab

# Extract faces from source images
python main.py extract --input-dir workspace/data_src --output-dir workspace/data_src/aligned --detector s3fd

# Extract faces from destination images
python main.py extract --input-dir workspace/data_dst --output-dir workspace/data_dst/aligned --detector s3fd
```

### Step 3: Sort and Clean Faces

```bash
# Sort source faces by quality
python main.py sort --input-dir workspace/data_src/aligned --by blur

# Sort destination faces by quality
python main.py sort --input-dir workspace/data_dst/aligned --by blur

# Remove low-quality faces manually
# Keep only the best 1000-2000 faces from each set
```

### Step 4: Train the Model

```bash
# Train with SAEHD model (recommended for quality)
python main.py train --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model SAEHD

# Alternative: Train with Quick96 model (faster training)
python main.py train --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model Quick96
```

### Step 5: Monitor Training

During training, you'll see:
- **Loss values** decreasing over time
- **Preview images** showing the swap quality
- **Training progress** with iterations and time

**Training Times (RTX 3050):**
- Quick96: 2-4 hours
- SAEHD: 8-24 hours
- AMP: 12-48 hours

### Step 6: Export Model for DeepFaceLive

```bash
# Export the trained model to DFM format
python main.py exportdfm --model-dir workspace/model --model SAEHD
```

### Step 7: Use in DeepFaceLive

1. **Copy the exported model** to DeepFaceLive's model directory
2. **Launch DeepFaceLive** with GPU support
3. **Select your custom model** in the interface

## Training Commands Reference

### Basic Training
```bash
python main.py train --training-data-src-dir workspace/data_src/aligned --training-data-dst-dir workspace/data_dst/aligned --model-dir workspace/model --model SAEHD
```

### Advanced Training Options
```bash
python main.py train \
  --training-data-src-dir workspace/data_src/aligned \
  --training-data-dst-dir workspace/data_dst/aligned \
  --model-dir workspace/model \
  --model SAEHD \
  --cpu-only false \
  --force-gpu-idxs 0 \
  --no-preview false
```

### Model Export
```bash
python main.py exportdfm --model-dir workspace/model --model SAEHD
```

## Model Types

| Model | Quality | Speed | VRAM Usage | Training Time |
|-------|---------|-------|------------|---------------|
| **Quick96** | Good | Fast | 4GB | 2-4 hours |
| **SAEHD** | Excellent | Medium | 6GB | 8-24 hours |
| **AMP** | Best | Slow | 8GB | 12-48 hours |

## Training Tips

### 1. Data Quality
- **High-resolution images** (1080p or higher)
- **Good lighting** and clear faces
- **Multiple angles** (front, side, tilted)
- **Various expressions** (neutral, smiling, serious)

### 2. Training Parameters
- **Batch size:** Start with 4-8, increase if VRAM allows
- **Resolution:** 256x256 for Quick96, 512x512 for SAEHD
- **Iterations:** 100,000+ for good quality

### 3. Monitoring
- **Loss should decrease** over time
- **Preview images** should show clear face swapping
- **Stop training** when loss plateaus

### 4. Troubleshooting
- **Out of memory:** Reduce batch size
- **Poor quality:** Add more training data
- **Slow training:** Use Quick96 model first

## Integration with DeepFaceLive

### Model Transfer
```bash
# Copy exported model to DeepFaceLive
cp workspace/model/SAEHD_export.dfm ../dfm_models/
```

### Live Streaming Setup
1. Launch DeepFaceLive with GPU support
2. Select your custom model
3. Configure camera settings
4. Start streaming

## Performance Expectations

### RTX 3050 Performance
- **Training:** 8-24 hours for SAEHD model
- **Inference:** 30-60 FPS at 1080p
- **Memory:** 8GB VRAM available

### Quality vs Speed Trade-offs
- **Quick96:** Fast training, good quality
- **SAEHD:** Medium training, excellent quality
- **AMP:** Slow training, best quality

## Troubleshooting

### Common Issues

1. **"No training data found"**
   - Ensure images are in the correct directories
   - Check that faces were extracted properly

2. **"Out of memory"**
   - Reduce batch size in training settings
   - Close other GPU applications

3. **"Poor swap quality"**
   - Add more training data
   - Train for more iterations
   - Use higher resolution images

4. **"Training too slow"**
   - Use Quick96 model for faster training
   - Reduce image resolution
   - Ensure GPU is being used

### GPU Verification
```bash
# Test GPU support
python -c "import torch; print('PyTorch CUDA:', torch.cuda.is_available())"
python -c "import onnxruntime as ort; print('ONNX CUDA:', 'CUDAExecutionProvider' in ort.get_available_providers())"
```

## Next Steps

1. **Prepare your training data** with high-quality images
2. **Extract and sort faces** using the provided commands
3. **Train your first model** with SAEHD
4. **Export and test** in DeepFaceLive
5. **Iterate and improve** based on results

## Resources

- **DeepFaceLab Documentation:** Check the `doc/` directory
- **Model Architecture Details:** See `models/` directory
- **GPU Setup Status:** See `GPU_SETUP_STATUS.md`
- **Training Examples:** Check the README.md file

---

**Happy Training! 🚀**

Your RTX 3050 is ready to create amazing face swap models for your anonymous streaming platform! 