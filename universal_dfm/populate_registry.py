#!/usr/bin/env python3
"""
Populate Model Registry
Manually populate the model registry with existing DFM files
"""

import json
import time
from pathlib import Path

def populate_registry():
    """Populate the model registry with existing DFM files"""
    base_dir = Path.cwd()
    config_dir = base_dir / "config"
    registry_file = config_dir / "model_registry.json"
    
    # Create registry structure
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
        category_dir = base_dir / "models" / category
        if category_dir.exists():
            print(f"Scanning {category} directory...")
            for dfm_file in category_dir.glob("*.dfm"):
                model_name = dfm_file.stem
                registry["categories"][category].append(model_name)
                registry["models"][model_name] = {
                    "file": str(dfm_file),
                    "category": category,
                    "added_date": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                print(f"  ✓ Added: {model_name}")
    
    # Save registry
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"\nRegistry populated with {len(registry['models'])} models")
    print(f"Registry saved to: {registry_file}")
    
    # Print summary
    for category, models in registry["categories"].items():
        if models:
            print(f"\n{category.upper()}: {len(models)} models")
            for model in models[:5]:  # Show first 5
                print(f"  - {model}")
            if len(models) > 5:
                print(f"  ... and {len(models) - 5} more")

if __name__ == "__main__":
    populate_registry() 