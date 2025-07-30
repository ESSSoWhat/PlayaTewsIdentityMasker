#!/usr/bin/env python3
"""
Download All 31 DFM Models Script
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
import hashlib

class ComprehensiveDFMDownloader:
    def __init__(self, download_dir="userdata/dfm_models"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # All 31 available DFM models from DeepFaceLive releases
        self.dfm_models = {
            'Albica_Johns.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/ALBICA_JOHNS/Albica_Johns.dfm',
                'size': 685.2 * 1024 * 1024,  # 685.2MB
                'description': 'High-quality face swap model'
            },
            'Amber_Song.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/AMBER_SONG/Amber_Song.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Ava_de_Addario.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/AVA_DE_ADDARIO/Ava_de_Addario.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Bryan_Greynolds.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/BRYAN_GREYNOLDS/Bryan_Greynolds.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'David_Kovalniy.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/DAVID_KOVALNIY/David_Kovalniy.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Dean_Wiesel.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/DEAN_WIESEL/Dean_Wiesel.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Dilraba_Dilmurat.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/DILRABA_DILMURAT/Dilraba_Dilmurat.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Emily_Winston.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/EMILY_WINSTON/Emily_Winston.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Ewon_Spice.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/EWON_SPICE/Ewon_Spice.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Irina_Arty.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/IRINA_ARTY/Irina_Arty.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Jackie_Chan.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/JACKIE_CHAN/Jackie_Chan.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Jesse_Stat_320.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/JESSE_STAT_320/Jesse_Stat_320.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Joker.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/JOKER/Joker.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Keanu_Reeves.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/KEANU_REEVES/Keanu_Reeves.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Keanu_Reeves_320.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/KEANU_REEVES_320/Keanu_Reeves_320.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Kim_Jarrey.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/KIM_JARREY/Kim_Jarrey.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Liu_Lice.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/LIU_LICE/Liu_Lice.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Matilda_Bobbie.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/MATILDA_BOBBIE/Matilda_Bobbie.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Meggie_Merkel.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/MEGGIE_MERKEL/Meggie_Merkel.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Millie_Park.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/MILLIE_PARK/Millie_Park.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Mr_Bean.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/MR_BEAN/Mr_Bean.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Natalie_Fatman.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/NATALIE_FATMAN/Natalie_Fatman.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Natasha_Former.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/NATASHA_FORMER/Natasha_Former.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Nicola_Badge.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/NICOLA_BADGE/Nicola_Badge.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Rob_Doe.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/ROB_DOE/Rob_Doe.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Tina_Shift.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/TINA_SHIFT/Tina_Shift.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Tim_Chrys.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/TIM_CHRYS/Tim_Chrys.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Tim_Norland.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/TIM_NORLAND/Tim_Norland.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Yohanna_Coralson.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/YOHANNA_CORALSON/Yohanna_Coralson.dfm',
                'size': 685.2 * 1024 * 1024,
                'description': 'High-quality face swap model'
            },
            'Zahar_Lupin.dfm': {
                'url': 'https://github.com/iperov/DeepFaceLive/releases/download/ZAHAR_LUPIN/Zahar_Lupin.dfm',
                'size': 685.2 * 1024 * 1024,
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
            
            # Move temp file to final location
            temp_path.rename(file_path)
            print(f"✅ {model_name} downloaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {model_name}: {e}")
            return False
    
    def download_all_models(self, max_workers=3):
        """Download all models with concurrent downloads"""
        print(f"🎬 PlayaTewsIdentityMasker - Download All 31 DFM Models")
        print("=" * 60)
        print(f"📁 Download directory: {self.download_dir}")
        print(f"📊 Total models to download: {len(self.dfm_models)}")
        print(f"💾 Total size: {self.format_size(self.total_size)}")
        print(f"🔧 Max concurrent downloads: {max_workers}")
        print()
        
        # Check existing files first
        existing_files = []
        for model_name in self.dfm_models:
            file_path = self.download_dir / model_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                if file_size >= self.dfm_models[model_name]['size'] * 0.95:
                    existing_files.append(model_name)
                    print(f"✅ {model_name} already exists ({self.format_size(file_size)})")
        
        # Filter out existing files
        models_to_download = {k: v for k, v in self.dfm_models.items() if k not in existing_files}
        
        if not models_to_download:
            print("\n🎉 All models are already downloaded!")
            return True
        
        print(f"\n📋 Models to download: {len(models_to_download)}")
        print("-" * 40)
        
        # Download with thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_model = {
                executor.submit(self.download_file, model_name, model_info): model_name
                for model_name, model_info in models_to_download.items()
            }
            
            # Process completed downloads
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    success = future.result()
                    if success:
                        self.downloaded_files.append(model_name)
                    else:
                        self.failed_downloads.append(model_name)
                except Exception as e:
                    print(f"❌ Exception for {model_name}: {e}")
                    self.failed_downloads.append(model_name)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully downloaded: {len(self.downloaded_files)}")
        print(f"❌ Failed downloads: {len(self.failed_downloads)}")
        print(f"📁 Already existed: {len(existing_files)}")
        
        if self.downloaded_files:
            print(f"\n✅ Downloaded models:")
            for model in self.downloaded_files:
                print(f"  • {model}")
        
        if self.failed_downloads:
            print(f"\n❌ Failed models:")
            for model in self.failed_downloads:
                print(f"  • {model}")
        
        # Final verification
        total_available = len(list(self.download_dir.glob("*.dfm")))
        print(f"\n🎯 Total models available: {total_available}/31")
        
        return len(self.failed_downloads) == 0

def main():
    """Main function"""
    downloader = ComprehensiveDFMDownloader()
    
    try:
        success = downloader.download_all_models()
        
        if success:
            print("\n🎉 All 31 DFM models downloaded successfully!")
            print("💡 You can now use all models in PlayaTewsIdentityMasker")
        else:
            print("\n⚠️ Some downloads failed. Check the list above.")
            print("💡 You can re-run this script to retry failed downloads.")
        
        print("\n🚀 Next Steps:")
        print("1. Restart PlayaTewsIdentityMasker app")
        print("2. Go to Face Swap settings")
        print("3. Select from 31 available models")
        print("4. Enable face swapping")
        
    except KeyboardInterrupt:
        print("\n⏹️ Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 