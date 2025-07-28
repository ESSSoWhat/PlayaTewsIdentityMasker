#!/usr/bin/env python3
"""
DeepFaceLive Releases Checker
Checks actual DeepFaceLive releases for available DFM models
"""

import os
import sys
import json
import requests
import re
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepFaceLiveReleasesChecker:
    """Checks DeepFaceLive releases for available models"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.releases_url = "https://api.github.com/repos/iperov/DeepFaceLive/releases"
        self.repo_url = "https://github.com/iperov/DeepFaceLive"
        
    def get_latest_releases(self):
        """Get the latest releases from DeepFaceLive"""
        try:
            logger.info("🔍 Checking DeepFaceLive releases...")
            response = requests.get(self.releases_url, timeout=30)
            response.raise_for_status()
            
            releases = response.json()
            logger.info(f"✅ Found {len(releases)} releases")
            
            return releases
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch releases: {e}")
            return []
    
    def find_dfm_models_in_release(self, release):
        """Find DFM models in a specific release"""
        dfm_models = []
        
        if 'assets' not in release:
            return dfm_models
        
        for asset in release['assets']:
            asset_name = asset.get('name', '')
            if asset_name.endswith('.dfm'):
                dfm_models.append({
                    'name': asset_name,
                    'download_url': asset.get('browser_download_url'),
                    'size': asset.get('size', 0),
                    'size_mb': asset.get('size', 0) / (1024 * 1024),
                    'release_tag': release.get('tag_name', 'unknown'),
                    'release_name': release.get('name', 'unknown')
                })
        
        return dfm_models
    
    def check_all_releases_for_models(self):
        """Check all releases for DFM models"""
        releases = self.get_latest_releases()
        
        all_models = []
        
        for release in releases[:5]:  # Check latest 5 releases
            release_name = release.get('name', 'Unknown')
            release_tag = release.get('tag_name', 'unknown')
            
            logger.info(f"📦 Checking release: {release_name} ({release_tag})")
            
            models = self.find_dfm_models_in_release(release)
            if models:
                logger.info(f"   Found {len(models)} DFM models")
                for model in models:
                    all_models.append(model)
            else:
                logger.info("   No DFM models found")
        
        return all_models
    
    def create_download_links_file(self, models):
        """Create a file with direct download links"""
        links_file = self.base_dir / "deepfacelive_download_links.txt"
        
        content = """# DeepFaceLive DFM Model Download Links
# Generated from actual DeepFaceLive releases

"""
        
        if not models:
            content += "No DFM models found in recent releases.\n"
            content += "Try checking:\n"
            content += "1. https://github.com/iperov/DeepFaceLive/releases\n"
            content += "2. https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog\n"
            content += "3. Community Discord: https://discord.gg/rxa7h9M6rH\n"
        else:
            content += f"Found {len(models)} DFM models in DeepFaceLive releases:\n\n"
            
            for model in models:
                content += f"## {model['name']}\n"
                content += f"- **Size**: {model['size_mb']:.1f}MB\n"
                content += f"- **Release**: {model['release_name']} ({model['release_tag']})\n"
                content += f"- **Download**: {model['download_url']}\n\n"
        
        content += """
# Manual Download Instructions:
1. Click the download link above
2. Save the .dfm file to your Downloads folder
3. Run: python quick_dfm_setup.py
4. Enter the path to your downloaded file
5. The model will be installed automatically

# Alternative Sources:
- Mega Repository: https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog
- HuggingFace: https://huggingface.co/datasets/deepfakes/dfm-models
- Community Discord: https://discord.gg/rxa7h9M6rH

# Model Categories:
- Celebrity models: Keanu_Reeves, Bryan_Greynolds, etc.
- Character models: Joker, Mr_Bean, etc.
- Quality varies by model size (50-200MB typical)
"""
        
        with open(links_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Download links saved to: {links_file}")
        return links_file
    
    def create_community_sources_guide(self):
        """Create a guide for community sources"""
        guide_file = self.base_dir / "COMMUNITY_DFM_SOURCES.md"
        
        guide = """# Community DFM Model Sources

## 🎯 DeepFaceLive Community Sources

Since direct downloads from DeepFaceLive releases may be limited, here are community sources:

### 1. Mega Repository (Most Reliable)
**URL**: https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog

**Steps**:
1. Open the Mega link
2. Browse through the model collection
3. Look for files ending in `.dfm`
4. Download models that are 50-200MB in size
5. Common models: `Keanu_Reeves.dfm`, `Bryan_Greynolds.dfm`

### 2. DeepFaceLive Discord Community
**URL**: https://discord.gg/rxa7h9M6rH

**Steps**:
1. Join the Discord server
2. Check the #models or #downloads channel
3. Look for pinned messages with model links
4. Ask community members for specific models

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

## 🎯 Popular Models to Look For

### High Priority:
1. **Keanu_Reeves.dfm** - Excellent quality, very popular
2. **Bryan_Greynolds.dfm** - Great results, well-documented
3. **Jesse_Stat.dfm** - Good for testing
4. **Ewon_Spice.dfm** - Good quality

### Medium Priority:
5. **Liu_Lice.dfm** - Popular model
6. **Meggie_Merkel.dfm** - Well-documented
7. **Irina_Arty.dfm** - Good quality
8. **Rob_Doe.dfm** - Popular

### Character Models:
9. **Joker.dfm** - Popular character
10. **Mr_Bean.dfm** - Fun character model

## 🔍 How to Identify Real Models

### File Characteristics:
- **Extension**: `.dfm`
- **Size**: 50-200MB (typically 100-150MB)
- **Format**: Binary files (not text/JSON)
- **Content**: ONNX-based neural network models

### Red Flags:
- Files smaller than 10MB (likely placeholders)
- Files with `.json` extension (not real models)
- Files that open as text (should be binary)

## 📥 Installation Process

### Step 1: Download
1. Find and download the `.dfm` file
2. Ensure it's the correct size (50-200MB)
3. Verify it has `.dfm` extension

### Step 2: Install
```bash
python quick_dfm_setup.py
```
Then enter the path to your downloaded file.

### Step 3: Verify
1. Check that the file appears in both directories:
   - `dfm_models/[model_name].dfm`
   - `universal_dfm/models/prebuilt/[model_name].dfm`
2. Restart the PlayaTewsIdentityMasker app
3. Models should appear in the dropdown

## 🚀 Quick Start Recommendations

1. **Start with 1-2 models** (e.g., Keanu_Reeves, Bryan_Greynolds)
2. **Test them** in the app to ensure they work
3. **Download more** as needed
4. **Replace placeholders** gradually

## 📞 Need Help?

- **Discord**: https://discord.gg/rxa7h9M6rH
- **GitHub Issues**: https://github.com/iperov/DeepFaceLive/issues
- **QQ Group**: 124500433 (Chinese)

---
*Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide)
        
        logger.info(f"✅ Community sources guide created: {guide_file}")
        return guide_file
    
    def run_check(self):
        """Run the complete release check"""
        logger.info("🔍 DeepFaceLive Releases Checker")
        logger.info("=" * 50)
        logger.info(f"Checking: {self.repo_url}")
        
        # Check releases for models
        models = self.check_all_releases_for_models()
        
        # Create download links file
        links_file = self.create_download_links_file(models)
        
        # Create community sources guide
        guide_file = self.create_community_sources_guide()
        
        # Summary
        print("\n" + "="*60)
        print("DEEPFACELIVE RELEASES CHECK SUMMARY")
        print("="*60)
        print(f"Models found in releases: {len(models)}")
        
        if models:
            print("\n✅ Found DFM models in DeepFaceLive releases!")
            print("Check the download links file for direct download URLs.")
        else:
            print("\n⚠️  No DFM models found in recent releases.")
            print("Use community sources instead.")
        
        print(f"\n📄 Files created:")
        print(f"  - {links_file}")
        print(f"  - {guide_file}")
        print("\n🎯 Next Steps:")
        print("1. Check the download links file for direct URLs")
        print("2. Use community sources if no direct links available")
        print("3. Download models manually and use quick_dfm_setup.py")
        print("="*60)

def main():
    """Main function"""
    checker = DeepFaceLiveReleasesChecker()
    checker.run_check()

if __name__ == "__main__":
    main() 