#!/usr/bin/env python3
"""
DFM Source Manager
Comprehensive management of DFM model files and organization
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

class DFMSourceManager:
    """Manages DFM model files and organization"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.dfm_source_dir = self.base_dir / "dfm_source"
        self.dfm_models_dir = self.base_dir / "dfm_models"
        self.universal_models_dir = self.base_dir / "universal_dfm" / "models" / "prebuilt"
        
        # Create organized structure
        self.placeholders_dir = self.dfm_source_dir / "placeholders"
        self.partial_downloads_dir = self.dfm_source_dir / "partial_downloads"
        self.real_models_dir = self.dfm_source_dir / "real_models"
        self.backups_dir = self.dfm_source_dir / "backups"
        self.downloads_dir = self.dfm_source_dir / "downloads"
        
        # Create all directories
        for dir_path in [self.dfm_source_dir, self.placeholders_dir, self.partial_downloads_dir, 
                        self.real_models_dir, self.backups_dir, self.downloads_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def organize_existing_files(self):
        """Organize existing DFM files into proper structure"""
        logger.info("🔧 Organizing existing DFM files...")
        
        # Move placeholder files (small JSON files)
        placeholder_files = list(self.dfm_models_dir.glob("*.dfm"))
        for file_path in placeholder_files:
            if file_path.stat().st_size < 1024:  # Less than 1KB
                dest_path = self.placeholders_dir / file_path.name
                if not dest_path.exists():
                    shutil.move(str(file_path), str(dest_path))
                    logger.info(f"   Moved placeholder: {file_path.name}")
        
        # Move partial downloads
        partial_files = list(self.dfm_models_dir.glob("*.dfm.part"))
        for file_path in partial_files:
            dest_path = self.partial_downloads_dir / file_path.name
            try:
                if not dest_path.exists():
                    shutil.move(str(file_path), str(dest_path))
                    logger.info(f"   Moved partial download: {file_path.name}")
            except PermissionError:
                logger.warning(f"   Could not move {file_path.name} (file in use)")
        
        # Move backup files
        backup_files = list(self.dfm_models_dir.glob("*.json"))
        for file_path in backup_files:
            dest_path = self.backups_dir / file_path.name
            if not dest_path.exists():
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"   Moved backup: {file_path.name}")
        
        # Copy universal models to placeholders
        universal_files = list(self.universal_models_dir.glob("*.dfm"))
        for file_path in universal_files:
            dest_path = self.placeholders_dir / file_path.name
            if not dest_path.exists():
                shutil.copy2(str(file_path), str(dest_path))
                logger.info(f"   Copied universal model: {file_path.name}")
    
    def create_model_inventory(self):
        """Create an inventory of all DFM models"""
        inventory = {
            "placeholders": [],
            "partial_downloads": [],
            "real_models": [],
            "backups": [],
            "downloads": []
        }
        
        # Scan placeholders
        for file_path in self.placeholders_dir.glob("*.dfm"):
            inventory["placeholders"].append({
                "name": file_path.stem,
                "size_mb": file_path.stat().st_size / (1024 * 1024),
                "path": str(file_path),
                "type": "placeholder"
            })
        
        # Scan partial downloads
        for file_path in self.partial_downloads_dir.glob("*.dfm.part"):
            inventory["partial_downloads"].append({
                "name": file_path.stem,
                "size_mb": file_path.stat().st_size / (1024 * 1024),
                "path": str(file_path),
                "type": "partial"
            })
        
        # Scan real models
        for file_path in self.real_models_dir.glob("*.dfm"):
            inventory["real_models"].append({
                "name": file_path.stem,
                "size_mb": file_path.stat().st_size / (1024 * 1024),
                "path": str(file_path),
                "type": "real"
            })
        
        # Scan backups
        for file_path in self.backups_dir.glob("*.json"):
            inventory["backups"].append({
                "name": file_path.stem,
                "size_mb": file_path.stat().st_size / (1024 * 1024),
                "path": str(file_path),
                "type": "backup"
            })
        
        # Save inventory
        inventory_file = self.dfm_source_dir / "model_inventory.json"
        with open(inventory_file, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2)
        
        logger.info(f"✅ Model inventory created: {inventory_file}")
        return inventory
    
    def create_organization_report(self):
        """Create a comprehensive organization report"""
        report_file = self.dfm_source_dir / "DFM_ORGANIZATION_REPORT.md"
        
        inventory = self.create_model_inventory()
        
        report = """# DFM Model Organization Report

## 📁 Directory Structure

```
dfm_source/
├── placeholders/      # Small JSON placeholder files (<1KB)
├── partial_downloads/ # Incomplete downloads (.dfm.part files)
├── real_models/       # Actual DFM models (50-200MB+)
├── backups/          # Backup and configuration files
└── downloads/        # New downloads (manual placement)
```

## 📊 Model Inventory

"""
        
        # Placeholders
        if inventory["placeholders"]:
            report += "### 🔲 Placeholder Models\n"
            report += "These are small JSON files that mark where real models should go:\n\n"
            for model in inventory["placeholders"]:
                report += f"- **{model['name']}** ({model['size_mb']:.3f}MB)\n"
            report += "\n"
        
        # Partial downloads
        if inventory["partial_downloads"]:
            report += "### ⏳ Partial Downloads\n"
            report += "These are incomplete downloads that need to be resumed:\n\n"
            for model in inventory["partial_downloads"]:
                report += f"- **{model['name']}** ({model['size_mb']:.1f}MB) - Incomplete\n"
            report += "\n"
        
        # Real models
        if inventory["real_models"]:
            report += "### ✅ Real Models\n"
            report += "These are actual DFM models ready for use:\n\n"
            for model in inventory["real_models"]:
                report += f"- **{model['name']}** ({model['size_mb']:.1f}MB) - Ready\n"
            report += "\n"
        else:
            report += "### ❌ No Real Models Found\n"
            report += "You need to download real DFM models to use face swapping.\n\n"
        
        # Backups
        if inventory["backups"]:
            report += "### 💾 Backup Files\n"
            report += "Configuration and backup files:\n\n"
            for model in inventory["backups"]:
                report += f"- **{model['name']}** ({model['size_mb']:.3f}MB)\n"
            report += "\n"
        
        report += """## 🎯 Next Steps

### 1. Download Real Models
Use the download guides to get real DFM models:
- `MANUAL_DFM_DOWNLOAD_GUIDE.md`
- `DEEPFACELIVE_MODELS_GUIDE.md`
- `download_deepfacelive_release_models.py`

### 2. Place Real Models
Download real models (50-200MB each) and place them in:
- `dfm_source/real_models/` (for organization)
- `dfm_models/` (for app to use)
- `universal_dfm/models/prebuilt/` (for universal access)

### 3. Replace Placeholders
Once you have real models, replace the placeholder files.

## 📋 File Types

### Placeholder Files (<1KB)
- Small JSON files
- Mark where real models should go
- Not usable for face swapping

### Real Models (50-200MB+)
- Large binary files
- ONNX-based neural networks
- Ready for face swapping

### Partial Downloads
- Incomplete downloads
- Need to be resumed or restarted
- Usually much smaller than expected

## 🔧 Management Commands

```bash
# Organize files
python dfm_source_manager.py

# Show inventory
python dfm_source_manager.py --inventory

# Clean up placeholders
python dfm_source_manager.py --cleanup
```

---
*Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ Organization report created: {report_file}")
        return report_file
    
    def setup_app_directories(self):
        """Set up the directories that the app expects"""
        logger.info("🔧 Setting up app directories...")
        
        # Ensure dfm_models directory exists and has placeholders
        self.dfm_models_dir.mkdir(exist_ok=True)
        
        # Copy placeholders back to dfm_models for app compatibility
        for placeholder_file in self.placeholders_dir.glob("*.dfm"):
            dest_file = self.dfm_models_dir / placeholder_file.name
            if not dest_file.exists():
                shutil.copy2(str(placeholder_file), str(dest_file))
                logger.info(f"   Restored placeholder: {placeholder_file.name}")
        
        # Ensure universal directory exists
        self.universal_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy placeholders to universal directory
        for placeholder_file in self.placeholders_dir.glob("*.dfm"):
            dest_file = self.universal_models_dir / placeholder_file.name
            if not dest_file.exists():
                shutil.copy2(str(placeholder_file), str(dest_file))
                logger.info(f"   Restored universal placeholder: {placeholder_file.name}")
    
    def install_real_model(self, model_path: Path):
        """Install a real DFM model to the app directories"""
        if not model_path.exists():
            logger.error(f"❌ Model file not found: {model_path}")
            return False
        
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb < 10:
            logger.warning(f"⚠️  File seems too small ({file_size_mb:.1f}MB). Real DFM files are 50-200MB.")
            return False
        
        model_name = model_path.stem
        
        # Copy to real_models directory
        real_model_path = self.real_models_dir / f"{model_name}.dfm"
        shutil.copy2(str(model_path), str(real_model_path))
        
        # Copy to app directories
        app_model_path = self.dfm_models_dir / f"{model_name}.dfm"
        universal_model_path = self.universal_models_dir / f"{model_name}.dfm"
        
        shutil.copy2(str(model_path), str(app_model_path))
        shutil.copy2(str(model_path), str(universal_model_path))
        
        logger.info(f"✅ Installed real model: {model_name}")
        logger.info(f"   Size: {file_size_mb:.1f}MB")
        logger.info(f"   Location: {real_model_path}")
        logger.info(f"   App ready: {app_model_path}")
        
        return True
    
    def run_organization(self):
        """Run the complete organization process"""
        logger.info("🎯 DFM Source Manager")
        logger.info("=" * 50)
        
        # Organize existing files
        self.organize_existing_files()
        
        # Set up app directories
        self.setup_app_directories()
        
        # Create inventory and report
        inventory = self.create_model_inventory()
        report_file = self.create_organization_report()
        
        # Summary
        print("\n" + "="*60)
        print("DFM ORGANIZATION SUMMARY")
        print("="*60)
        print(f"📁 Source directory: {self.dfm_source_dir}")
        print(f"📊 Placeholders: {len(inventory['placeholders'])}")
        print(f"⏳ Partial downloads: {len(inventory['partial_downloads'])}")
        print(f"✅ Real models: {len(inventory['real_models'])}")
        print(f"💾 Backups: {len(inventory['backups'])}")
        
        if len(inventory['real_models']) == 0:
            print("\n⚠️  No real models found!")
            print("   Download real DFM models to use face swapping.")
            print("   Check the organization report for guidance.")
        else:
            print("\n✅ Real models are ready for use!")
        
        print(f"\n📄 Report created: {report_file}")
        print("="*60)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DFM Source Manager')
    parser.add_argument('--inventory', action='store_true', help='Show model inventory')
    parser.add_argument('--cleanup', action='store_true', help='Clean up placeholders')
    parser.add_argument('--install', type=str, help='Install a real model file')
    
    args = parser.parse_args()
    
    manager = DFMSourceManager()
    
    if args.inventory:
        inventory = manager.create_model_inventory()
        print(json.dumps(inventory, indent=2))
    elif args.cleanup:
        # Remove placeholders (use with caution)
        for placeholder_file in manager.placeholders_dir.glob("*.dfm"):
            placeholder_file.unlink()
        print("🧹 Placeholders cleaned up")
    elif args.install:
        model_path = Path(args.install)
        manager.install_real_model(model_path)
    else:
        manager.run_organization()

if __name__ == "__main__":
    main() 