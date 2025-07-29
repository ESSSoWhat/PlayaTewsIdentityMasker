#!/usr/bin/env python3
"""
Download All DFM Models Script
Downloads all available DFM models from DeepFaceLive releases
"""

import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class DFMDownloader:
    def __init__(self, download_dir="dfm_models"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # All available DFM models from DeepFaceLive releases
        self.dfm_models = {
            'Tina_Shift.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/TINA_SHIFT/Tina_Shift.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            },
            'Meggie_Merkel.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/MEGGIE_MERKEL/Meggie_Merkel.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            },
            'Albica_Johns.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/ALBICA_JOHNS/Albica_Johns.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            },
            'Natalie_Fatman.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/NATALIE_FATMAN/Natalie_Fatman.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            },
            'Liu_Lice.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/LIU_LICE/Liu_Lice.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            }
        }
        
        self.downloaded_files = []
        self.failed_downloads = []
        self.total_size = sum(model['size'] for model in self.dfm_models.values())
        
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def download_file(self, model_name, model_info):
        """Download a single DFM model file"""
        url = model_info['url']
        file_path = self.download_dir / model_name
        temp_path = self.download_dir / f"{model_name}.part"
        
        # Check if file already exists
        if file_path.exists():
            file_size = file_path.stat().st_size
            if file_size >= model_info['size'] * 0.95:  # 95% complete
                print(f"✅ {model_name} already exists and appears complete ({self.format_size(file_size)})")
                return True
        
        print(f"📥 Starting download: {model_name} ({self.format_size(model_info['size'])})")
        print(f"   URL: {url}")
        
        try:
            # Start download with resume capability
            headers = {}
            if temp_path.exists():
                # Resume download
                downloaded_size = temp_path.stat().st_size
                headers['Range'] = f'bytes={downloaded_size}-'
                print(f"   Resuming from {self.format_size(downloaded_size)}")
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            if headers.get('Range'):
                total_size += temp_path.stat().st_size
            
            # Download with progress
            mode = 'ab' if temp_path.exists() else 'wb'
            downloaded_size = temp_path.stat().st_size if temp_path.exists() else 0
            
            with open(temp_path, mode) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress every 10MB
                        if downloaded_size % (10 * 1024 * 1024) < 8192:
                            progress = (downloaded_size / total_size) * 100 if total_size > 0 else 0
                            print(f"   Progress: {progress:.1f}% ({self.format_size(downloaded_size)}/{self.format_size(total_size)})")
            
            # Rename temp file to final file
            temp_path.rename(file_path)
            print(f"✅ Download completed: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {model_name} - {e}")
            return False
    
    def download_all_models(self, max_workers=2):
        """Download all DFM models with progress tracking"""
        print("🎬 PlayaTewsIdentityMasker - Download All DFM Models")
        print("=" * 60)
        print(f"📁 Download directory: {self.download_dir}")
        print(f"📊 Total models to download: {len(self.dfm_models)}")
        print(f"💾 Total size: {self.format_size(self.total_size)}")
        print(f"🔧 Max concurrent downloads: {max_workers}")
        print()
        
        # Check existing files
        existing_files = []
        for model_name in self.dfm_models:
            file_path = self.download_dir / model_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                existing_files.append((model_name, file_size))
        
        if existing_files:
            print("📋 Existing files found:")
            for model_name, file_size in existing_files:
                print(f"   ✅ {model_name} ({self.format_size(file_size)})")
            print()
        
        # Confirm download
        remaining_models = [name for name in self.dfm_models if not (self.download_dir / name).exists()]
        if not remaining_models:
            print("🎉 All models are already downloaded!")
            return
        
        print(f"📥 Models to download: {len(remaining_models)}")
        for model_name in remaining_models:
            size = self.format_size(self.dfm_models[model_name]['size'])
            print(f"   📦 {model_name} ({size})")
        
        print()
        print("⚠️  This will download several large files (685MB each)")
        print("   Estimated time: 10-30 minutes depending on your internet speed")
        print()
        
        confirm = input("Do you want to proceed with downloading all models? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Download cancelled.")
            return
        
        print()
        print("🚀 Starting downloads...")
        print()
        
        # Download with threading
        start_time = time.time()
        successful_downloads = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_model = {
                executor.submit(self.download_file, model_name, model_info): model_name
                for model_name, model_info in self.dfm_models.items()
                if not (self.download_dir / model_name).exists()
            }
            
            # Process completed downloads
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    success = future.result()
                    if success:
                        successful_downloads += 1
                        self.downloaded_files.append(model_name)
                    else:
                        self.failed_downloads.append(model_name)
                except Exception as e:
                    print(f"❌ Error downloading {model_name}: {e}")
                    self.failed_downloads.append(model_name)
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print()
        print("=" * 60)
        print("📊 Download Summary")
        print("=" * 60)
        print(f"⏱️  Total time: {duration:.1f} seconds")
        print(f"✅ Successful downloads: {successful_downloads}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        
        if self.downloaded_files:
            print()
            print("✅ Successfully downloaded:")
            for model_name in self.downloaded_files:
                print(f"   📦 {model_name}")
        
        if self.failed_downloads:
            print()
            print("❌ Failed downloads:")
            for model_name in self.failed_downloads:
                print(f"   ❌ {model_name}")
            print()
            print("💡 You can retry failed downloads by running this script again.")
        
        print()
        print("🎯 Next steps:")
        print("1. Check the downloaded models in the dfm_models directory")
        print("2. Restart the PlayaTewsIdentityMasker app to load new models")
        print("3. Select your preferred model in the DFM Quick Access panel")

def main():
    """Main function"""
    downloader = DFMDownloader()
    downloader.download_all_models()

if __name__ == "__main__":
    main() 