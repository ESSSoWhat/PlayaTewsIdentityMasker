#!/usr/bin/env python3
"""
DFM Model Download Helper
Download popular DFM models from various sources
"""

import os
import sys
import requests
import time
from pathlib import Path

def download_model(model_name, url, output_dir):
    """Download a model from URL"""
    output_path = Path(output_dir) / f"{model_name}.dfm"
    
    if output_path.exists():
        print(f"⚠️  {model_name} already exists, skipping...")
        return True
    
    print(f"📥 Downloading {model_name}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ {model_name} downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {model_name}: {e}")
        return False

def main():
    """Download popular DFM models"""
    output_dir = Path("dfm_models")
    output_dir.mkdir(exist_ok=True)
    
    # Add your model URLs here
    models = {
        # Example URLs (you'll need to find the actual URLs)
        # "kevin_hart_model": "https://example.com/kevin_hart_model.dfm",
        # "Keanu_Reeves": "https://example.com/keanu_reeves.dfm",
    }
    
    print("🔍 DFM Model Download Helper")
    print("=" * 50)
    print("To download models:")
    print("1. Find the model URLs from DeepFaceLive repositories")
    print("2. Add them to the 'models' dictionary in this script")
    print("3. Run: python download_dfm_models.py")
    print()
    
    if not models:
        print("⚠️  No model URLs configured yet.")
        print("Please add model URLs to the script and run again.")
        return
    
    for model_name, url in models.items():
        download_model(model_name, url, output_dir)
        time.sleep(1)  # Be nice to servers

if __name__ == "__main__":
    main()
