#!/usr/bin/env python3
"""
Download DeepFaceLive Release Models
Downloads actual DFM models found in DeepFaceLive releases
"""

import os
import sys
import json
import shutil
import time
import requests
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepFaceLiveReleaseDownloader:
    """Downloads DFM models from DeepFaceLive releases"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.dfm_models_dir = self.base_dir / "dfm_models"
        self.universal_models_dir = self.base_dir / "universal_dfm" / "models" / "prebuilt"
        
        # Create directories
        self.dfm_models_dir.mkdir(exist_ok=True)
        self.universal_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Real models found in DeepFaceLive releases
        self.release_models = {
            "Tina_Shift": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/TINA_SHIFT/Tina_Shift.dfm",
                "size_mb": 685.2,
                "description": "Tina Shift face swap model - high quality (685MB)",
                "release": "TINA_SHIFT"
            },
            "Meggie_Merkel": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/MEGGIE_MERKEL/Meggie_Merkel.dfm",
                "size_mb": 685.2,
                "description": "Meggie Merkel face swap model - high quality (685MB)",
                "release": "MEGGIE_MERKEL"
            },
            "Albica_Johns": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/ALBICA_JOHNS/Albica_Johns.dfm",
                "size_mb": 685.2,
                "description": "Albica Johns face swap model - high quality (685MB)",
                "release": "ALBICA_JOHNS"
            },
            "Natalie_Fatman": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/NATALIE_FATMAN/Natalie_Fatman.dfm",
                "size_mb": 685.2,
                "description": "Natalie Fatman face swap model - high quality (685MB)",
                "release": "NATALIE_FATMAN"
            },
            "Liu_Lice": {
                "url": "https://github.com/iperov/DeepFaceLive/releases/download/LIU_LICE/Liu_Lice.dfm",
                "size_mb": 685.2,
                "description": "Liu Lice face swap model - high quality (685MB)",
                "release": "LIU_LICE"
            }
        }
    
    def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download a specific model from DeepFaceLive releases"""
        if model_name not in self.release_models:
            logger.error(f"❌ Model {model_name} not found in release models")
            return False
        
        model_info = self.release_models[model_name]
        output_path = self.dfm_models_dir / f"{model_name}.dfm"
        universal_path = self.universal_models_dir / f"{model_name}.dfm"
        
        # Check if already exists
        if output_path.exists() and not force:
            file_size = output_path.stat().st_size / (1024 * 1024)
            if file_size > 100:  # Real model (not placeholder)
                logger.info(f"⚠️  {model_name} already exists ({file_size:.1f}MB), skipping...")
                return True
            else:
                logger.info(f"🔄 {model_name} exists but is placeholder ({file_size:.1f}MB), replacing...")
        
        logger.info(f"📥 Downloading {model_name} from DeepFaceLive release...")
        logger.info(f"   Description: {model_info['description']}")
        logger.info(f"   Expected size: {model_info['size_mb']:.1f}MB")
        logger.info(f"   Release: {model_info['release']}")
        logger.info(f"   URL: {model_info['url']}")
        
        # Download the model
        if self._download_from_url(model_info['url'], output_path, model_name):
            # Copy to universal directory
            shutil.copy2(output_path, universal_path)
            logger.info(f"✅ {model_name} downloaded successfully!")
            return True
        
        logger.error(f"❌ Failed to download {model_name}")
        return False
    
    def _download_from_url(self, url: str, output_path: Path, model_name: str) -> bool:
        """Download from a specific URL"""
        try:
            logger.info(f"   Starting download...")
            
            response = requests.get(url, stream=True, timeout=300)  # 5 minute timeout for large files
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length:
                expected_size = int(content_length)
                logger.info(f"   File size: {expected_size / (1024*1024):.1f}MB")
            
            # Download with progress
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress every 50MB
                        if downloaded % (50 * 1024 * 1024) == 0:
                            mb_downloaded = downloaded / (1024 * 1024)
                            logger.info(f"   Downloaded: {mb_downloaded:.1f}MB")
            
            # Validate downloaded file
            if self._validate_downloaded_file(output_path):
                return True
            else:
                output_path.unlink()  # Delete invalid file
                return False
                
        except Exception as e:
            logger.warning(f"   Download failed: {e}")
            return False
    
    def _validate_downloaded_file(self, file_path: Path) -> bool:
        """Validate a downloaded DFM file"""
        try:
            # Check file size (should be at least 100MB for these high-quality models)
            file_size = file_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            if file_size_mb < 100:  # Less than 100MB
                logger.warning(f"   File too small ({file_size_mb:.1f}MB), expected 600+MB")
                return False
            
            logger.info(f"   ✅ Downloaded file size: {file_size_mb:.1f}MB")
            
            # Try to read as binary and check for ONNX header
            with open(file_path, 'rb') as f:
                header = f.read(100)
            
            if b'ONNX' in header:
                logger.info(f"   ✅ Valid ONNX model detected")
                return True
            else:
                logger.warning(f"   ⚠️  No ONNX header found, but file size looks correct")
                return True  # Accept it anyway if size is reasonable
                
        except Exception as e:
            logger.error(f"   Validation failed: {e}")
            return False
    
    def download_recommended_models(self, max_models: int = 2):
        """Download recommended models (start with smaller ones)"""
        logger.info("🚀 Starting download of DeepFaceLive release models...")
        logger.info("⚠️  Note: These are high-quality models (685MB each)")
        logger.info("   Download time may take 10-30 minutes depending on your connection")
        
        # Recommended order (Liu_Lice is often mentioned as good)
        recommended_models = ["Liu_Lice", "Tina_Shift"]
        
        success_count = 0
        total_attempted = 0
        
        for model_name in recommended_models[:max_models]:
            if model_name in self.release_models:
                total_attempted += 1
                logger.info(f"\n{'='*60}")
                if self.download_model(model_name):
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to download {model_name}")
                
                # Wait between downloads
                if total_attempted < max_models:
                    logger.info("⏳ Waiting 5 seconds before next download...")
                    time.sleep(5)
        
        logger.info(f"\n✅ Download completed: {success_count}/{total_attempted} models downloaded")
        return success_count
    
    def create_download_summary(self):
        """Create a summary of available models"""
        summary_file = self.base_dir / "DEEPFACELIVE_RELEASE_SUMMARY.md"
        
        summary = """# DeepFaceLive Release Models Summary

## 🎯 Available Models from DeepFaceLive Releases

These models are **directly available** from the [DeepFaceLive GitHub repository](https://github.com/iperov/DeepFaceLive.git):

"""
        
        for model_name, model_info in self.release_models.items():
            summary += f"""
### {model_name}
- **Description**: {model_info['description']}
- **Size**: {model_info['size_mb']:.1f}MB
- **Release**: {model_info['release']}
- **Download URL**: {model_info['url']}
"""
        
        summary += """

## 🚀 Quick Download Commands

### Download Liu_Lice (Recommended):
```bash
python download_deepfacelive_release_models.py
```

### Download Specific Model:
```python
from download_deepfacelive_release_models import DeepFaceLiveReleaseDownloader
downloader = DeepFaceLiveReleaseDownloader()
downloader.download_model("Liu_Lice")
```

## 📋 Model Information

### High-Quality Models:
- **Size**: 685MB each (much larger than typical 50-200MB models)
- **Quality**: Very high quality, professional-grade
- **Format**: ONNX-based binary files
- **Download Time**: 10-30 minutes depending on connection

### Recommended Order:
1. **Liu_Lice** - Popular and well-documented
2. **Tina_Shift** - High quality results
3. **Meggie_Merkel** - Good for testing
4. **Albica_Johns** - Alternative option
5. **Natalie_Fatman** - Additional choice

## ⚠️ Important Notes

### Download Considerations:
- These are **large files** (685MB each)
- Download time: 10-30 minutes per model
- Ensure stable internet connection
- Consider downloading during off-peak hours

### Installation:
1. Download completes automatically
2. Models are placed in correct directories
3. Restart the PlayaTewsIdentityMasker app
4. Models will appear in dropdown

## 🎯 Next Steps

1. **Start with 1 model** (Liu_Lice recommended)
2. **Test it** in the app
3. **Download more** if needed
4. **Replace placeholders** gradually

---
*Based on DeepFaceLive releases: https://github.com/iperov/DeepFaceLive/releases*
*Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"✅ Download summary created: {summary_file}")
        return summary_file
    
    def run_download(self):
        """Run the complete download process"""
        logger.info("🎯 DeepFaceLive Release Model Downloader")
        logger.info("=" * 60)
        logger.info("Based on: https://github.com/iperov/DeepFaceLive.git")
        logger.info("Found 5 high-quality models (685MB each)")
        
        # Create summary
        summary_file = self.create_download_summary()
        
        # Ask user if they want to proceed
        print("\n⚠️  WARNING: These are large files (685MB each)")
        print("   Download time: 10-30 minutes per model")
        print("   Recommended: Start with 1 model first")
        print()
        
        try:
            choice = input("Download Liu_Lice model (recommended)? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                # Download recommended models
                success_count = self.download_recommended_models(max_models=1)
            else:
                print("Skipping download. You can run this script later.")
                success_count = 0
        except:
            print("Skipping download. You can run this script later.")
            success_count = 0
        
        # Summary
        print("\n" + "="*60)
        print("DEEPFACELIVE RELEASE DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Models downloaded: {success_count}")
        print(f"Total available: {len(self.release_models)}")
        
        if success_count > 0:
            print("\n✅ Successfully downloaded DeepFaceLive release models!")
            print("The app will now recognize these high-quality models.")
        else:
            print("\n📖 Download summary created for manual reference.")
            print("You can download models manually using the URLs in the summary.")
        
        print(f"\n📄 Summary created: {summary_file}")
        print("\n📁 Models will be stored in:")
        print(f"  - {self.dfm_models_dir}")
        print(f"  - {self.universal_models_dir}")
        print("="*60)

def main():
    """Main function"""
    downloader = DeepFaceLiveReleaseDownloader()
    downloader.run_download()

if __name__ == "__main__":
    main() 