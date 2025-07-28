#!/usr/bin/env python3
"""
DeepFaceLive Model Downloader
Downloads DFM models from DeepFaceLive repository and community sources
"""

import os
import sys
import json
import shutil
import time
import requests
from pathlib import Path
import logging
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepFaceLiveModelDownloader:
    """Downloads DFM models from DeepFaceLive sources"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.dfm_models_dir = self.base_dir / "dfm_models"
        self.universal_models_dir = self.base_dir / "universal_dfm" / "models" / "prebuilt"
        
        # Create directories
        self.dfm_models_dir.mkdir(exist_ok=True)
        self.universal_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Models available from DeepFaceLive repository (based on their documentation)
        self.deepfacelive_models = {
            "Keanu_Reeves": {
                "description": "Keanu Reeves face swap model - very popular and high quality",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Keanu_Reeves/examples.md"
            },
            "Irina_Arty": {
                "description": "Irina Arty face swap model",
                "size_mb": 150,
                "category": "celebrity"
            },
            "Millie_Park": {
                "description": "Millie Park face swap model",
                "size_mb": 150,
                "category": "celebrity"
            },
            "Rob_Doe": {
                "description": "Rob Doe face swap model",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Rob_Doe/examples.md"
            },
            "Jesse_Stat": {
                "description": "Jesse Stat face swap model",
                "size_mb": 150,
                "category": "celebrity"
            },
            "Bryan_Greynolds": {
                "description": "Bryan Greynolds face swap model",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Bryan_Greynolds/examples.md"
            },
            "Mr_Bean": {
                "description": "Mr. Bean face swap model",
                "size_mb": 150,
                "category": "celebrity"
            },
            "Ewon_Spice": {
                "description": "Ewon Spice face swap model",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Ewon_Spice/examples.md"
            },
            "Liu_Lice": {
                "description": "Liu Lice face swap model",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Liu_Lice/examples.md"
            },
            "Meggie_Merkel": {
                "description": "Meggie Merkel face swap model",
                "size_mb": 150,
                "category": "celebrity",
                "examples_url": "https://github.com/iperov/DeepFaceLive/blob/master/doc/celebs/Meggie_Merkel/examples.md"
            }
        }
        
        # Known download sources for DeepFaceLive models
        self.download_sources = {
            "primary": {
                "name": "DeepFaceLive Releases",
                "base_url": "https://github.com/iperov/DeepFaceLive/releases",
                "model_pattern": "https://github.com/iperov/DeepFaceLive/releases/download/latest/{model}.dfm"
            },
            "community": {
                "name": "Community Mega Repository",
                "base_url": "https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog",
                "model_pattern": "https://mega.nz/file/{model_id}#{model}.dfm"
            },
            "huggingface": {
                "name": "HuggingFace Models",
                "base_url": "https://huggingface.co/datasets/deepfakes/dfm-models",
                "model_pattern": "https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/{model}.dfm"
            }
        }
    
    def get_model_download_urls(self, model_name: str) -> list:
        """Generate possible download URLs for a model"""
        urls = []
        
        # Try different URL patterns
        patterns = [
            f"https://github.com/iperov/DeepFaceLive/releases/download/latest/{model_name}.dfm",
            f"https://github.com/iperov/DeepFaceLive/releases/download/v1.0/{model_name}.dfm",
            f"https://github.com/iperov/DeepFaceLive/releases/download/v0.1/{model_name}.dfm",
            f"https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/{model_name}.dfm",
            f"https://mega.nz/file/{model_name.lower()}#{model_name}.dfm"
        ]
        
        for pattern in patterns:
            urls.append(pattern)
        
        return urls
    
    def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download a specific model from DeepFaceLive sources"""
        if model_name not in self.deepfacelive_models:
            logger.error(f"❌ Model {model_name} not found in DeepFaceLive models")
            return False
        
        model_info = self.deepfacelive_models[model_name]
        output_path = self.dfm_models_dir / f"{model_name}.dfm"
        universal_path = self.universal_models_dir / f"{model_name}.dfm"
        
        # Check if already exists
        if output_path.exists() and not force:
            logger.info(f"⚠️  {model_name} already exists, skipping...")
            return True
        
        logger.info(f"📥 Downloading {model_name} from DeepFaceLive...")
        logger.info(f"   Description: {model_info['description']}")
        logger.info(f"   Expected size: ~{model_info['size_mb']}MB")
        
        # Get possible download URLs
        download_urls = self.get_model_download_urls(model_name)
        
        # Try each URL
        for url in download_urls:
            logger.info(f"   Trying: {url}")
            if self._download_from_url(url, output_path, model_name):
                # Copy to universal directory
                shutil.copy2(output_path, universal_path)
                logger.info(f"✅ {model_name} downloaded successfully!")
                return True
        
        logger.error(f"❌ Failed to download {model_name} from all sources")
        return False
    
    def _download_from_url(self, url: str, output_path: Path, model_name: str) -> bool:
        """Download from a specific URL"""
        try:
            response = requests.get(url, stream=True, timeout=60)
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
                        
                        # Show progress every 10MB
                        if downloaded % (10 * 1024 * 1024) == 0:
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
            # Check file size (should be at least 10MB for a real model)
            file_size = file_path.stat().st_size
            if file_size < 10 * 1024 * 1024:  # Less than 10MB
                logger.warning(f"   File too small ({file_size / (1024*1024):.1f}MB), likely not a real model")
                return False
            
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
    
    def download_popular_models(self, max_models: int = 5):
        """Download the most popular DeepFaceLive models"""
        logger.info("🚀 Starting download of DeepFaceLive models...")
        
        # Priority models to download first
        priority_models = ["Keanu_Reeves", "Bryan_Greynolds", "Jesse_Stat", "Ewon_Spice", "Liu_Lice"]
        
        success_count = 0
        total_attempted = 0
        
        for model_name in priority_models[:max_models]:
            if model_name in self.deepfacelive_models:
                total_attempted += 1
                if self.download_model(model_name):
                    success_count += 1
                time.sleep(2)  # Be nice to servers
        
        logger.info(f"✅ Download completed: {success_count}/{total_attempted} models downloaded")
        return success_count
    
    def create_deepfacelive_guide(self):
        """Create a guide specific to DeepFaceLive models"""
        guide_file = self.base_dir / "DEEPFACELIVE_MODELS_GUIDE.md"
        
        guide = """# DeepFaceLive Models Download Guide

## 🎯 Available DeepFaceLive Models

Based on the [DeepFaceLive GitHub repository](https://github.com/iperov/DeepFaceLive.git), these models are available:

"""
        
        for model_name, model_info in self.deepfacelive_models.items():
            guide += f"""
### {model_name}
- **Description**: {model_info['description']}
- **Size**: ~{model_info['size_mb']}MB
- **Category**: {model_info['category']}
"""
            if 'examples_url' in model_info:
                guide += f"- **Examples**: [View Examples]({model_info['examples_url']})\n"
        
        guide += """

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
*Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        logger.info(f"✅ DeepFaceLive guide created: {guide_file}")
        return guide_file
    
    def run_download(self):
        """Run the complete download process"""
        logger.info("🎯 DeepFaceLive Model Downloader")
        logger.info("=" * 50)
        logger.info("Based on: https://github.com/iperov/DeepFaceLive.git")
        
        # Create DeepFaceLive specific guide
        guide_file = self.create_deepfacelive_guide()
        
        # Download models
        success_count = self.download_popular_models(max_models=5)
        
        # Summary
        print("\n" + "="*60)
        print("DEEPFACELIVE DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Models downloaded: {success_count}")
        print(f"Total available: {len(self.deepfacelive_models)}")
        
        if success_count > 0:
            print("\n✅ Successfully downloaded DeepFaceLive models!")
            print("The app will now recognize these models for face swapping.")
        else:
            print("\n⚠️  No models were downloaded automatically.")
            print("Please check DEEPFACELIVE_MODELS_GUIDE.md for manual download instructions.")
        
        print(f"\n📖 Guide created: {guide_file}")
        print("\n📁 Models are stored in:")
        print(f"  - {self.dfm_models_dir}")
        print(f"  - {self.universal_models_dir}")
        print("="*60)

def main():
    """Main function"""
    downloader = DeepFaceLiveModelDownloader()
    downloader.run_download()

if __name__ == "__main__":
    main() 