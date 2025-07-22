#!/usr/bin/env python3
"""
Universal DFM Manager
Manages DFM models in the universal folder structure
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
import argparse

class DFMManager:
    def __init__(self, base_dir="./universal_dfm"):
        # If we're already in the universal_dfm directory, use current directory
        if Path.cwd().name == "universal_dfm":
            self.base_dir = Path.cwd()
        else:
            self.base_dir = Path(base_dir).resolve()
        self.dfm_dir = self.base_dir / "models"
        self.config_dir = self.base_dir / "config"
        self.registry_file = self.config_dir / "model_registry.json"
        
    def list_models(self, category="all"):
        """List all models or models in a specific category"""
        if not self.registry_file.exists():
            print("No model registry found. Creating new registry...")
            self._create_registry()
        
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        print(f"\nDFM Models ({category}):")
        print("-" * 50)
        
        if category == "all":
            for cat, models in registry["categories"].items():
                if models:
                    print(f"\n{cat.upper()}:")
                    for model in models:
                        print(f"  - {model}")
        else:
            models = registry["categories"].get(category, [])
            if models:
                for model in models:
                    print(f"  - {model}")
            else:
                print(f"No models found in category: {category}")
    
    def _create_registry(self):
        """Create a new model registry"""
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
        
        # Scan existing models
        for category in ["active", "archived", "custom", "prebuilt"]:
            category_dir = self.dfm_dir / category
            if category_dir.exists():
                for dfm_file in category_dir.glob("*.dfm"):
                    model_name = dfm_file.stem
                    registry["categories"][category].append(model_name)
                    registry["models"][model_name] = {
                        "file": str(dfm_file),
                        "category": category,
                        "added_date": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def add_model(self, model_path, category="custom"):
        """Add a new model to the registry"""
        model_path = Path(model_path)
        if not model_path.exists():
            print(f"Model file not found: {model_path}")
            return False
        
        # Copy model to appropriate directory
        dest_dir = self.dfm_dir / category
        dest_file = dest_dir / model_path.name
        shutil.copy2(model_path, dest_file)
        
        # Update registry
        if not self.registry_file.exists():
            self._create_registry()
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        model_name = model_path.stem
        if model_name not in registry["categories"][category]:
            registry["categories"][category].append(model_name)
            registry["models"][model_name] = {
                "file": str(dest_file),
                "category": category,
                "added_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        registry["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"✓ Added model: {model_name} to {category}")
        return True
    
    def remove_model(self, model_name, category="custom"):
        """Remove a model from the registry"""
        if not self.registry_file.exists():
            print("No model registry found.")
            return False
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if model_name in registry["categories"][category]:
            registry["categories"][category].remove(model_name)
            if model_name in registry["models"]:
                del registry["models"][model_name]
            
            registry["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"✓ Removed model: {model_name} from {category}")
            return True
        else:
            print(f"Model {model_name} not found in {category}")
            return False
    
    def move_model(self, model_name, from_category, to_category):
        """Move a model between categories"""
        if not self.registry_file.exists():
            print("No model registry found.")
            return False
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if model_name in registry["categories"][from_category]:
            # Move file
            old_file = Path(registry["models"][model_name]["file"])
            new_file = self.dfm_dir / to_category / old_file.name
            
            if old_file.exists():
                shutil.move(str(old_file), str(new_file))
            
            # Update registry
            registry["categories"][from_category].remove(model_name)
            registry["categories"][to_category].append(model_name)
            registry["models"][model_name]["category"] = to_category
            registry["models"][model_name]["file"] = str(new_file)
            
            registry["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"✓ Moved model: {model_name} from {from_category} to {to_category}")
            return True
        else:
            print(f"Model {model_name} not found in {from_category}")
            return False
    
    def get_model_info(self, model_name):
        """Get detailed information about a specific model"""
        if not self.registry_file.exists():
            print("No model registry found.")
            return False
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if model_name in registry["models"]:
            model_info = registry["models"][model_name]
            print(f"\nModel Information: {model_name}")
            print("-" * 40)
            print(f"Category: {model_info['category']}")
            print(f"File: {model_info['file']}")
            print(f"Added: {model_info['added_date']}")
            
            # Check file size
            file_path = Path(model_info['file'])
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"Size: {size_mb:.1f} MB")
            else:
                print("Size: File not found")
            
            return True
        else:
            print(f"Model {model_name} not found in registry")
            return False

def main():
    parser = argparse.ArgumentParser(description="Universal DFM Manager")
    parser.add_argument("--base-dir", default="./universal_dfm", help="Base directory")
    parser.add_argument("command", choices=["list", "add", "remove", "move", "info"], help="Command to execute")
    parser.add_argument("--category", default="all", help="Model category")
    parser.add_argument("--model-path", help="Path to model file (for add command)")
    parser.add_argument("--model-name", help="Model name (for remove/move/info commands)")
    parser.add_argument("--from-category", help="Source category (for move command)")
    parser.add_argument("--to-category", help="Destination category (for move command)")
    
    args = parser.parse_args()
    
    manager = DFMManager(args.base_dir)
    
    if args.command == "list":
        manager.list_models(args.category)
    elif args.command == "add":
        if not args.model_path:
            print("Error: --model-path required for add command")
            return 1
        manager.add_model(args.model_path, args.category)
    elif args.command == "remove":
        if not args.model_name:
            print("Error: --model-name required for remove command")
            return 1
        manager.remove_model(args.model_name, args.category)
    elif args.command == "move":
        if not all([args.model_name, args.from_category, args.to_category]):
            print("Error: --model-name, --from-category, and --to-category required for move command")
            return 1
        manager.move_model(args.model_name, args.from_category, args.to_category)
    elif args.command == "info":
        if not args.model_name:
            print("Error: --model-name required for info command")
            return 1
        manager.get_model_info(args.model_name)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 