#!/usr/bin/env python3
"""
Manual DFM Download Guide
Comprehensive guide for downloading DFM models manually
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
import webbrowser

class ManualDFMDownloadGuide:
    """Provides comprehensive guide for manual DFM downloads"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.dfm_models_dir = self.base_dir / "dfm_models"
        self.universal_models_dir = self.base_dir / "universal_dfm" / "models" / "prebuilt"
        
        # Popular models that need to be downloaded
        self.popular_models = [
            "kevin_hart_model",
            "Keanu_Reeves", 
            "Keanu_Reeves_320",
            "Jackie_Chan",
            "Joker",
            "Dilraba_Dilmurat",
            "Emily_Winston",
            "Bryan_Greynolds",
            "David_Kovalniy",
            "Dean_Wiesel",
            "Ewon_Spice",
            "Irina_Arty",
            "Jesse_Stat_320",
            "Liu_Lice",
            "Matilda_Bobbie",
            "Meggie_Merkel"
        ]
    
    def create_comprehensive_guide(self):
        """Create a comprehensive download guide"""
        guide_file = self.base_dir / "MANUAL_DFM_DOWNLOAD_GUIDE.md"
        
        guide = """# Manual DFM Model Download Guide

## 🎯 Your Missing DFM Models

You need to download these models manually:

"""
        
        for i, model in enumerate(self.popular_models, 1):
            guide += f"{i}. **{model}**\n"
        
        guide += """

## 📥 Download Sources

### 1. DeepFaceLive Official Releases
**URL**: https://github.com/iperov/DeepFaceLive/releases

**Steps**:
1. Visit the releases page
2. Look for model files with `.dfm` extension
3. Download files that are 50-200MB in size
4. Common models: `kevin_hart_model.dfm`, `keanu_reeves_model.dfm`

### 2. Community Mega Repository
**URL**: https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog

**Steps**:
1. Open the Mega link
2. Browse through the model collection
3. Download `.dfm` files for your desired models
4. Files should be 50-200MB each

### 3. HuggingFace Model Hub
**URL**: https://huggingface.co/datasets/deepfakes/dfm-models

**Steps**:
1. Visit the HuggingFace dataset
2. Browse available models
3. Download `.dfm` files
4. May require login for some models

### 4. Community Forums
- **DeepFakes Forum**: https://www.deepfakes.com/forums/
- **MrDeepFakes**: https://mrdeepfakes.com/
- **Reddit r/DeepFakes**: https://www.reddit.com/r/deepfakes/

## 🔍 How to Find Models

### Search Terms to Use:
- `[model_name].dfm`
- `[model_name] face swap model`
- `DeepFaceLive [model_name]`
- `DFM [model_name]`

### File Characteristics:
- **Extension**: `.dfm`
- **Size**: 50-200MB (typically 100-150MB)
- **Format**: ONNX-based binary files
- **Content**: Face swap neural network models

## 📁 Installation Instructions

### Step 1: Download the Model
1. Find and download the `.dfm` file for your desired model
2. Ensure it's the correct size (50-200MB)
3. Verify it has `.dfm` extension

### Step 2: Place in Correct Directories
Copy the downloaded `.dfm` file to **BOTH** locations:

```
dfm_models/[model_name].dfm
universal_dfm/models/prebuilt/[model_name].dfm
```

### Step 3: Verify Installation
1. Check file size (should be 50-200MB)
2. Ensure file has `.dfm` extension
3. Restart the PlayaTewsIdentityMasker app
4. Models should appear in the model selection dropdown

## 🎯 Priority Models to Download

### High Priority (Most Popular):
1. **kevin_hart_model.dfm** - Very popular, good quality
2. **Keanu_Reeves.dfm** - Excellent results
3. **Jackie_Chan.dfm** - Good for testing
4. **Joker.dfm** - Popular character model

### Medium Priority:
5. **Dilraba_Dilmurat.dfm** - Popular actress
6. **Emily_Winston.dfm** - Good quality
7. **Bryan_Greynolds.dfm** - Popular actor

### Lower Priority:
8. **David_Kovalniy.dfm**
9. **Dean_Wiesel.dfm**
10. **Ewon_Spice.dfm**
11. **Irina_Arty.dfm**
12. **Jesse_Stat_320.dfm**
13. **Liu_Lice.dfm**
14. **Matilda_Bobbie.dfm**
15. **Meggie_Merkel.dfm**

## ⚠️ Important Notes

### File Validation:
- Real DFM files are **50-200MB**
- Placeholder files are **<1KB** (JSON text files)
- If you see a small file, it's a placeholder, not a real model

### Security:
- Only download from trusted sources
- Scan downloaded files with antivirus
- Avoid suspicious or unofficial sources

### Performance:
- Larger models (150-200MB) usually have better quality
- Smaller models (50-100MB) may be faster but lower quality
- Test models before using in production

## 🚀 Quick Start

1. **Download 1-2 models first** (e.g., Kevin Hart, Keanu Reeves)
2. **Test them** in the app
3. **Download more** as needed
4. **Replace placeholders** gradually

## 📞 Need Help?

If you can't find specific models:
1. Check community forums
2. Ask in DeepFakes communities
3. Look for alternative model names
4. Consider creating your own models

## 🔧 Troubleshooting

### Model Not Appearing:
- Ensure file is in both directories
- Check file size (should be 50-200MB)
- Restart the app
- Verify `.dfm` extension

### Poor Quality:
- Try larger models (150-200MB)
- Check lighting conditions
- Adjust face detection settings
- Try different models

### App Crashes:
- Check model compatibility
- Verify file integrity
- Try with CPU-only mode
- Update the app

---
*Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print(f"✅ Comprehensive guide created: {guide_file}")
        return guide_file
    
    def open_download_sources(self):
        """Open download sources in browser"""
        sources = [
            "https://github.com/iperov/DeepFaceLive/releases",
            "https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog",
            "https://huggingface.co/datasets/deepfakes/dfm-models",
            "https://www.deepfakes.com/forums/"
        ]
        
        print("🌐 Opening download sources in browser...")
        for source in sources:
            try:
                webbrowser.open(source)
                time.sleep(1)  # Small delay between opens
            except Exception as e:
                print(f"⚠️  Could not open {source}: {e}")
    
    def create_quick_download_script(self):
        """Create a script to help with manual downloads"""
        script_file = self.base_dir / "quick_dfm_setup.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Quick DFM Setup Helper
Helps you set up downloaded DFM models
"""

import os
import shutil
from pathlib import Path

def setup_downloaded_model(model_file_path):
    """Set up a downloaded DFM model"""
    model_file = Path(model_file_path)
    
    if not model_file.exists():
        print(f"❌ File not found: {model_file_path}")
        return False
    
    # Check file size
    file_size_mb = model_file.stat().st_size / (1024 * 1024)
    if file_size_mb < 10:
        print(f"⚠️  File seems too small ({file_size_mb:.1f}MB). Real DFM files are 50-200MB.")
        return False
    
    model_name = model_file.stem
    dfm_models_dir = Path("dfm_models")
    universal_models_dir = Path("universal_dfm/models/prebuilt")
    
    # Create directories
    dfm_models_dir.mkdir(exist_ok=True)
    universal_models_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy to both locations
    dest1 = dfm_models_dir / f"{model_name}.dfm"
    dest2 = universal_models_dir / f"{model_name}.dfm"
    
    shutil.copy2(model_file, dest1)
    shutil.copy2(model_file, dest2)
    
    print(f"✅ {model_name} set up successfully!")
    print(f"   Size: {file_size_mb:.1f}MB")
    print(f"   Location 1: {dest1}")
    print(f"   Location 2: {dest2}")
    
    return True

def main():
    """Main function"""
    print("🔧 Quick DFM Setup Helper")
    print("=" * 40)
    print("This script helps you set up downloaded DFM models.")
    print()
    print("Usage:")
    print("1. Download a .dfm file (50-200MB)")
    print("2. Run: python quick_dfm_setup.py")
    print("3. Enter the path to your downloaded .dfm file")
    print()
    
    while True:
        file_path = input("Enter path to downloaded .dfm file (or 'quit' to exit): ").strip()
        
        if file_path.lower() in ['quit', 'exit', 'q']:
            break
        
        if setup_downloaded_model(file_path):
            print("🎉 Model is ready to use! Restart the app to see it.")
        else:
            print("❌ Setup failed. Please check the file path and try again.")
        
        print()

if __name__ == "__main__":
    main()
'''
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"✅ Quick setup script created: {script_file}")
        return script_file
    
    def run_guide(self):
        """Run the complete guide creation"""
        print("📚 Creating Manual DFM Download Guide...")
        print("=" * 60)
        
        # Create comprehensive guide
        guide_file = self.create_comprehensive_guide()
        
        # Create quick setup script
        script_file = self.create_quick_download_script()
        
        # Summary
        print("\n" + "="*60)
        print("MANUAL DOWNLOAD GUIDE CREATED")
        print("="*60)
        print(f"📖 Comprehensive Guide: {guide_file}")
        print(f"🔧 Quick Setup Script: {script_file}")
        print()
        print("🎯 Next Steps:")
        print("1. Read the comprehensive guide")
        print("2. Download 1-2 models manually")
        print("3. Use the quick setup script to install them")
        print("4. Restart the app to see your models")
        print()
        print("🌐 Would you like me to open download sources in your browser?")
        
        try:
            choice = input("Open download sources? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                self.open_download_sources()
        except:
            pass
        
        print("="*60)

def main():
    """Main function"""
    guide = ManualDFMDownloadGuide()
    guide.run_guide()

if __name__ == "__main__":
    main() 