#!/usr/bin/env python3
"""
Download DFM Models to Face Swap DFM Folder
Downloads high-quality DFM models directly to userdata/dfm_models
"""

import os
import requests
import time
from pathlib import Path
from urllib.parse import urlparse

def download_file(url, filepath, chunk_size=8192):
    """Download a file with progress tracking"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        print(f"📥 Downloading: {os.path.basename(filepath)}")
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        mb_downloaded = downloaded_size / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"   Progress: {progress:.1f}% ({mb_downloaded:.1f}MB/{mb_total:.1f}MB)")
        
        print(f"✅ Downloaded: {os.path.basename(filepath)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {os.path.basename(filepath)}: {e}")
        return False

def main():
    print("🎭 PlayaTewsIdentityMasker - Download DFM Models to Face Swap Folder")
    print("=" * 70)
    
    # Define the target directory (Face Swap DFM folder)
    target_dir = Path("userdata/dfm_models")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Target directory: {target_dir.absolute()}")
    
    # High-quality DFM models from DeepFaceLive releases
    dfm_models = [
        {
            "name": "Albica_Johns.dfm",
            "url": "https://github.com/iperov/DeepFaceLive/releases/download/ALBICA_JOHNS/Albica_Johns.dfm",
            "size": "685MB"
        },
        {
            "name": "Liu_Lice.dfm", 
            "url": "https://github.com/iperov/DeepFaceLive/releases/download/LIU_LICE/Liu_Lice.dfm",
            "size": "685MB"
        },
        {
            "name": "Meggie_Merkel.dfm",
            "url": "https://github.com/iperov/DeepFaceLive/releases/download/MEGGIE_MERKEL/Meggie_Merkel.dfm", 
            "size": "685MB"
        },
        {
            "name": "Natalie_Fatman.dfm",
            "url": "https://github.com/iperov/DeepFaceLive/releases/download/NATALIE_FATMAN/Natalie_Fatman.dfm",
            "size": "685MB"
        },
        {
            "name": "Tina_Shift.dfm",
            "url": "https://github.com/iperov/DeepFaceLive/releases/download/TINA_SHIFT/Tina_Shift.dfm",
            "size": "685MB"
        }
    ]
    
    print(f"\n📊 Total models to download: {len(dfm_models)}")
    print(f"💾 Total size: ~3.4GB")
    
    # Check existing files
    existing_files = []
    for model in dfm_models:
        filepath = target_dir / model["name"]
        if filepath.exists() and filepath.stat().st_size > 700000000:  # > 700MB
            existing_files.append(model["name"])
            print(f"   ✅ {model['name']} (already exists)")
    
    # Filter out existing files
    models_to_download = [model for model in dfm_models if model["name"] not in existing_files]
    
    if not models_to_download:
        print("\n🎉 All models are already downloaded!")
        return
    
    print(f"\n📥 Models to download: {len(models_to_download)}")
    for model in models_to_download:
        print(f"   📦 {model['name']} ({model['size']})")
    
    print(f"\n⚠️  This will download several large files (685MB each)")
    print(f"   Estimated time: 10-30 minutes depending on your internet speed")
    
    response = input("\nDo you want to proceed with downloading all models? (y/N): ")
    if response.lower() != 'y':
        print("❌ Download cancelled")
        return
    
    print("\n🚀 Starting downloads...")
    
    # Download each model
    successful_downloads = 0
    for i, model in enumerate(models_to_download, 1):
        print(f"\n[{i}/{len(models_to_download)}] Downloading {model['name']}...")
        
        filepath = target_dir / model["name"]
        
        if download_file(model["url"], filepath):
            successful_downloads += 1
        else:
            print(f"⚠️  Failed to download {model['name']}")
        
        # Small delay between downloads
        if i < len(models_to_download):
            time.sleep(1)
    
    print(f"\n" + "=" * 70)
    print(f"✅ Download complete!")
    print(f"📊 Successfully downloaded: {successful_downloads}/{len(models_to_download)} models")
    print(f"📁 Models saved to: {target_dir.absolute()}")
    
    if successful_downloads > 0:
        print(f"\n🎭 Your Face Swap DFM models are ready!")
        print(f"💡 Restart the app to see the new models in the face swap settings")

if __name__ == "__main__":
    main() 