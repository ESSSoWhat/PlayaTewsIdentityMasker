#!/usr/bin/env python3
"""
Download Remaining DFM Models
Downloads the remaining DFM models that have partial downloads
"""

import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class RemainingDFMDownloader:
    def __init__(self, download_dir="dfm_models"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Models that need to be completed (based on partial downloads found)
        self.remaining_models = {
            'Bryan_Greynolds.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/BRYAN_GREYNOLDS/Bryan_Greynolds.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Bryan Greynolds face swap model'
            },
            'Jesse_Stat_320.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/JESSE_STAT_320/Jesse_Stat_320.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Jesse Stat 320 face swap model'
            },
            'Kim_Jarrey.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/KIM_JARREY/Kim_Jarrey.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Kim Jarrey face swap model'
            },
            'Joker.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/JOKER/Joker.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Joker face swap model'
            },
            'Emily_Winston.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/EMILY_WINSTON/Emily_Winston.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Emily Winston face swap model'
            },
            'David_Kovalniy.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/DAVID_KOVALNIY/David_Kovalniy.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'David Kovalniy face swap model'
            },
            'Dilraba_Dilmurat.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/DILRABA_DILMURAT/Dilraba_Dilmurat.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'Dilraba Dilmurat face swap model'
            }
        }
        
        # Alternative sources for models
        self.alternative_sources = {
            'Bryan_Greynolds.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Bryan_Greynolds.dfm',
                'https://mega.nz/file/example/Bryan_Greynolds.dfm'
            ],
            'Jesse_Stat_320.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Jesse_Stat_320.dfm',
                'https://mega.nz/file/example/Jesse_Stat_320.dfm'
            ],
            'Kim_Jarrey.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Kim_Jarrey.dfm',
                'https://mega.nz/file/example/Kim_Jarrey.dfm'
            ],
            'Joker.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Joker.dfm',
                'https://mega.nz/file/example/Joker.dfm'
            ],
            'Emily_Winston.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Emily_Winston.dfm',
                'https://mega.nz/file/example/Emily_Winston.dfm'
            ],
            'David_Kovalniy.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/David_Kovalniy.dfm',
                'https://mega.nz/file/example/David_Kovalniy.dfm'
            ],
            'Dilraba_Dilmurat.dfm': [
                'https://huggingface.co/datasets/deepfakes/dfm-models/resolve/main/Dilraba_Dilmurat.dfm',
                'https://mega.nz/file/example/Dilraba_Dilmurat.dfm'
            ]
        }
        
        self.downloaded_files = []
        self.failed_downloads = []
        
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
    
    def check_existing_files(self):
        """Check which files already exist and their status"""
        print("🔍 Checking existing files...")
        existing_files = []
        partial_files = []
        
        for model_name in self.remaining_models.keys():
            file_path = self.download_dir / model_name
            part_path = self.download_dir / f"{model_name}.part"
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                expected_size = self.remaining_models[model_name]['size']
                if file_size >= expected_size * 0.95:  # 95% complete
                    existing_files.append(model_name)
                    print(f"✅ {model_name} - Complete ({self.format_size(file_size)})")
                else:
                    partial_files.append(model_name)
                    print(f"⚠️  {model_name} - Incomplete ({self.format_size(file_size)} / {self.format_size(expected_size)})")
            elif part_path.exists():
                part_size = part_path.stat().st_size
                expected_size = self.remaining_models[model_name]['size']
                partial_files.append(model_name)
                print(f"📥 {model_name} - Partial download ({self.format_size(part_size)} / {self.format_size(expected_size)})")
            else:
                print(f"❌ {model_name} - Not found")
        
        return existing_files, partial_files
    
    def download_file(self, model_name, model_info):
        """Download a single DFM model file"""
        url = model_info['url']
        file_path = self.download_dir / model_name
        temp_path = self.download_dir / f"{model_name}.part"
        
        # Check if file already exists and is complete
        if file_path.exists():
            file_size = file_path.stat().st_size
            if file_size >= model_info['size'] * 0.95:  # 95% complete
                print(f"✅ {model_name} already exists and appears complete ({self.format_size(file_size)})")
                return True
        
        print(f"📥 Starting download: {model_name} ({self.format_size(model_info['size'])})")
        print(f"   URL: {url}")
        
        # Try primary URL first
        if self._download_from_url(url, temp_path, model_name):
            # Rename from .part to .dfm
            if temp_path.exists():
                temp_path.rename(file_path)
            print(f"✅ {model_name} downloaded successfully!")
            return True
        
        # Try alternative sources
        if model_name in self.alternative_sources:
            for alt_url in self.alternative_sources[model_name]:
                print(f"🔄 Trying alternative URL for {model_name}...")
                if self._download_from_url(alt_url, temp_path, model_name):
                    if temp_path.exists():
                        temp_path.rename(file_path)
                    print(f"✅ {model_name} downloaded from alternative source!")
                    return True
        
        print(f"❌ Failed to download {model_name} from all sources")
        return False
    
    def _download_from_url(self, url: str, output_path: Path, model_name: str) -> bool:
        """Download from a specific URL"""
        try:
            # Start download with resume capability
            headers = {}
            if output_path.exists():
                # Resume download
                downloaded_size = output_path.stat().st_size
                headers['Range'] = f'bytes={downloaded_size}-'
                print(f"   Resuming from {self.format_size(downloaded_size)}")
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            if headers.get('Range'):
                total_size += output_path.stat().st_size
            
            # Download with progress
            mode = 'ab' if output_path.exists() else 'wb'
            downloaded_size = output_path.stat().st_size if output_path.exists() else 0
            
            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress every 10MB
                        if downloaded_size % (10 * 1024 * 1024) < 8192:
                            progress = (downloaded_size / total_size * 100) if total_size > 0 else 0
                            print(f"   Progress: {self.format_size(downloaded_size)} / {self.format_size(total_size)} ({progress:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Download failed: {str(e)}")
            return False
    
    def download_remaining_models(self, max_workers=2):
        """Download all remaining models"""
        print("🎬 PlayaTewsIdentityMasker - Download Remaining DFM Models")
        print("=" * 60)
        print(f"📁 Download directory: {self.download_dir}")
        print(f"📊 Models to download: {len(self.remaining_models)}")
        print(f"🔧 Max concurrent downloads: {max_workers}")
        print()
        
        # Check existing files first
        existing_files, partial_files = self.check_existing_files()
        print()
        
        # Remove existing files from download list
        models_to_download = {k: v for k, v in self.remaining_models.items() 
                            if k not in existing_files}
        
        if not models_to_download:
            print("🎉 All models are already downloaded!")
            return
        
        print(f"📥 Downloading {len(models_to_download)} remaining models...")
        print()
        
        # Download with threading
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for model_name, model_info in models_to_download.items():
                future = executor.submit(self.download_file, model_name, model_info)
                futures.append((model_name, future))
            
            # Wait for all downloads to complete
            for model_name, future in futures:
                try:
                    success = future.result()
                    if success:
                        self.downloaded_files.append(model_name)
                    else:
                        self.failed_downloads.append(model_name)
                except Exception as e:
                    print(f"❌ Error downloading {model_name}: {str(e)}")
                    self.failed_downloads.append(model_name)
        
        # Summary
        print()
        print("=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully downloaded: {len(self.downloaded_files)}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        
        if self.downloaded_files:
            print("\n✅ Downloaded models:")
            for model in self.downloaded_files:
                print(f"   - {model}")
        
        if self.failed_downloads:
            print("\n❌ Failed models:")
            for model in self.failed_downloads:
                print(f"   - {model}")
            print("\n💡 Try downloading these models manually from:")
            print("   - https://github.com/iperov/DeepFaceLive/releases")
            print("   - https://huggingface.co/datasets/deepfakes/dfm-models")
            print("   - https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog")

def main():
    """Main function"""
    downloader = RemainingDFMDownloader()
    downloader.download_remaining_models()

if __name__ == "__main__":
    main() 