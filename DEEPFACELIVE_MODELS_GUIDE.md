# DeepFaceLive Models Download Guide

## 🎯 Available DeepFaceLive Models

Based on the [DeepFaceLive GitHub repository](https://github.com/iperov/DeepFaceLive.git), these models are available:


### Keanu_Reeves
- **Description**: Keanu Reeves face swap model - very popular and high quality
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Keanu_Reeves/examples.md)

### Irina_Arty
- **Description**: Irina Arty face swap model
- **Size**: ~150MB
- **Category**: celebrity

### Millie_Park
- **Description**: Millie Park face swap model
- **Size**: ~150MB
- **Category**: celebrity

### Rob_Doe
- **Description**: Rob Doe face swap model
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Rob_Doe/examples.md)

### Jesse_Stat
- **Description**: Jesse Stat face swap model
- **Size**: ~150MB
- **Category**: celebrity

### Bryan_Greynolds
- **Description**: Bryan Greynolds face swap model
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Bryan_Greynolds/examples.md)

### Mr_Bean
- **Description**: Mr. Bean face swap model
- **Size**: ~150MB
- **Category**: celebrity

### Ewon_Spice
- **Description**: Ewon Spice face swap model
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Ewon_Spice/examples.md)

### Liu_Lice
- **Description**: Liu Lice face swap model
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Liu_Lice/examples.md)

### Meggie_Merkel
- **Description**: Meggie Merkel face swap model
- **Size**: ~150MB
- **Category**: celebrity
- **Examples**: [View Examples](https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Meggie_Merkel/examples.md)


## 📥 Download Sources

### 1. DeepFaceLive Official Repository
**URL**: https://github.com/iperov/DeepFaceLive

**How to find models**:
1. Visit the repository
2. Check the `doc/celebs/` directory for model examples
3. Look for releases section
4. Models are typically in `.dfm` format

### 2. DeepFaceLive Releases
**URL**: https://github.com/iperov/DeepFaceLive/releases

**Steps**:
1. Visit the releases page
2. Look for model files with `.dfm` extension
3. Download files that are 50-200MB in size
4. Common models: `Keanu_Reeves.dfm`, `Bryan_Greynolds.dfm`

### 3. Community Sources
- **Mega Repository**: https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog
- **HuggingFace**: https://huggingface.co/datasets/deepfakes/dfm-models
- **Discord Community**: https://discord.gg/rxa7h9M6rH

## 🎯 Priority Models (Recommended Order)

### High Priority:
1. **Keanu_Reeves** - Excellent quality, very popular
2. **Bryan_Greynolds** - Great results, well-documented
3. **Jesse_Stat** - Good for testing

### Medium Priority:
4. **Ewon_Spice** - Good quality
5. **Liu_Lice** - Popular model
6. **Meggie_Merkel** - Well-documented

### Lower Priority:
7. **Irina_Arty**
8. **Millie_Park**
9. **Rob_Doe**
10. **Mr_Bean**

## 🔧 Installation

### Automatic Installation:
```bash
python download_deepfacelive_models.py
```

### Manual Installation:
1. Download `.dfm` file (50-200MB)
2. Place in: `dfm_models/`
3. Copy to: `universal_dfm/models/prebuilt/`
4. Restart the app

## 📋 Model Information

### File Characteristics:
- **Extension**: `.dfm`
- **Size**: 50-200MB (typically 100-150MB)
- **Format**: ONNX-based binary files
- **Content**: Face swap neural network models

### Quality Notes:
- Larger models (150-200MB) usually have better quality
- Smaller models (50-100MB) may be faster but lower quality
- Test models before using in production

## 🚀 Quick Start

1. **Download 1-2 models first** (e.g., Keanu_Reeves, Bryan_Greynolds)
2. **Test them** in the app
3. **Download more** as needed
4. **Replace placeholders** gradually

## 📞 Community Support

- **Discord**: https://discord.gg/rxa7h9M6rH
- **GitHub Issues**: https://github.com/iperov/DeepFaceLive/issues
- **QQ Group**: 124500433 (Chinese)

---
*Based on DeepFaceLive repository: https://github.com/iperov/DeepFaceLive.git*
*Generated on: 2025-07-28 20:29:32*
