#!/usr/bin/env python3
"""
DFM Model Recovery Script
Helps recover and download missing DFM models
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DFMModelRecovery:
    """Recovers and downloads DFM models"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.dfm_models_dir = self.base_dir / "dfm_models"
        self.universal_dfm_dir = self.base_dir / "universal_dfm"
        self.universal_models_dir = self.universal_dfm_dir / "models" / "prebuilt"
        
        # Create necessary directories
        self.dfm_models_dir.mkdir(exist_ok=True)
        self.universal_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Popular DFM models that were in your registry
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
    
    def create_placeholder_models(self):
        """Create placeholder files for missing models"""
        logger.info("📝 Creating placeholder files for missing models...")
        
        for model_name in self.popular_models:
            # Create placeholder in dfm_models directory
            placeholder_path = self.dfm_models_dir / f"{model_name}.dfm"
            if not placeholder_path.exists():
                self._create_placeholder_file(placeholder_path, model_name)
            
            # Create placeholder in universal_dfm directory
            universal_placeholder_path = self.universal_models_dir / f"{model_name}.dfm"
            if not universal_placeholder_path.exists():
                self._create_placeholder_file(universal_placeholder_path, model_name)
    
    def _create_placeholder_file(self, file_path: Path, model_name: str):
        """Create a placeholder file for a model"""
        placeholder_data = {
            "model_name": model_name,
            "is_placeholder": True,
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": f"Placeholder for {model_name} - Download the real model file",
            "download_instructions": [
                "1. Visit DeepFaceLive model repositories",
                "2. Search for the model name",
                "3. Download the .dfm file (should be 50-200MB)",
                "4. Replace this placeholder file with the real model"
            ],
            "sources": [
                "https://github.com/iperov/DeepFaceLive/releases",
                "https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog",
                "https://www.deepfakes.com/forums/",
                "https://mrdeepfakes.com/"
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(placeholder_data, f, indent=2)
        
        logger.info(f"✅ Created placeholder: {file_path.name}")
    
    def restore_registry(self):
        """Restore the model registry with the models you had"""
        logger.info("📋 Restoring model registry...")
        
        registry_file = self.universal_dfm_dir / "config" / "model_registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        registry = {
            "version": "1.0",
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {},
            "categories": {
                "active": [],
                "archived": [],
                "custom": [],
                "prebuilt": []
            }
        }
        
        # Add all the models you had to the registry
        for model_name in self.popular_models:
            model_file = self.universal_models_dir / f"{model_name}.dfm"
            registry["categories"]["prebuilt"].append(model_name)
            registry["models"][model_name] = {
                "file": str(model_file),
                "category": "prebuilt",
                "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "placeholder"  # Mark as placeholder
            }
        
        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"✅ Registry restored with {len(self.popular_models)} models")
    
    def create_download_script(self):
        """Create a script to help download models"""
        logger.info("📥 Creating download helper script...")
        
        download_script = self.base_dir / "download_dfm_models.py"
        
        script_content = '''#!/usr/bin/env python3
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
'''
        
        with open(download_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"✅ Download script created: {download_script}")
    
    def create_recovery_report(self):
        """Create a recovery report"""
        logger.info("📊 Creating recovery report...")
        
        report_file = self.base_dir / "dfm_recovery_report.txt"
        
        report = f"""
DFM Model Recovery Report
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY:
- Total models in registry: {len(self.popular_models)}
- Placeholder files created: {len(self.popular_models)}
- Real models found: 0

MISSING MODELS:
{chr(10).join(f"- {model}" for model in self.popular_models)}

RECOVERY STATUS:
✅ Registry restored
✅ Placeholder files created  
✅ Directory structure fixed
❌ Real model files missing

NEXT STEPS:
1. Download real DFM model files from:
   - DeepFaceLive releases: https://github.com/iperov/DeepFaceLive/releases
   - Community repositories
   - Model sharing platforms

2. Replace placeholder files with real .dfm files

3. Run the app to verify models work

4. Check the download helper script: download_dfm_models.py

DIRECTORIES:
- dfm_models/: {self.dfm_models_dir}
- universal_dfm/models/prebuilt/: {self.universal_models_dir}

For help finding models, check:
- https://github.com/iperov/DeepFaceLive/releases
- https://mega.nz/folder/Po0nGQrA#dbbliNWojjt_9_12c5qjog
- Community forums and repositories
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ Recovery report created: {report_file}")
        return report
    
    def run_recovery(self):
        """Run the complete recovery process"""
        logger.info("🚀 Starting DFM model recovery...")
        
        self.create_placeholder_models()
        self.restore_registry()
        self.create_download_script()
        report = self.create_recovery_report()
        
        logger.info("✅ Recovery completed!")
        print("\n" + "="*60)
        print("DFM MODEL RECOVERY COMPLETED")
        print("="*60)
        print(report)
        print("="*60)

def main():
    """Main function"""
    recovery = DFMModelRecovery()
    recovery.run_recovery()

if __name__ == "__main__":
    main() 