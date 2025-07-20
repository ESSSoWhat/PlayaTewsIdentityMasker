#!/usr/bin/env python3
"""
Universal DFM Integration
Provides easy access to the universal DFM system for other applications
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional

class DFMIntegration:
    def __init__(self, base_dir: str = "./universal_dfm"):
        """Initialize DFM integration with the universal system"""
        # If we're already in the universal_dfm directory, use current directory
        if Path.cwd().name == "universal_dfm":
            self.base_dir = Path.cwd()
        else:
            self.base_dir = Path(base_dir).resolve()
        self.dfm_dir = self.base_dir / "models"
        self.config_dir = self.base_dir / "config"
        self.registry_file = self.config_dir / "model_registry.json"
        
    def get_model_path(self, model_name: str, category: str = "prebuilt") -> Optional[str]:
        """Get the full path to a specific model"""
        if not self.registry_file.exists():
            return None
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if model_name in registry["models"]:
            model_info = registry["models"][model_name]
            if model_info["category"] == category:
                return model_info["file"]
        
        return None
    
    def list_models_by_category(self, category: str = "all") -> List[str]:
        """List all models in a specific category"""
        if not self.registry_file.exists():
            return []
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if category == "all":
            all_models = []
            for models in registry["categories"].values():
                all_models.extend(models)
            return all_models
        else:
            return registry["categories"].get(category, [])
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a model"""
        if not self.registry_file.exists():
            return None
            
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        if model_name in registry["models"]:
            return registry["models"][model_name]
        
        return None
    
    def get_active_models(self) -> List[str]:
        """Get all models in the active category"""
        return self.list_models_by_category("active")
    
    def get_prebuilt_models(self) -> List[str]:
        """Get all prebuilt models"""
        return self.list_models_by_category("prebuilt")
    
    def get_custom_models(self) -> List[str]:
        """Get all custom models"""
        return self.list_models_by_category("custom")
    
    def model_exists(self, model_name: str, category: str = "prebuilt") -> bool:
        """Check if a model exists in the specified category"""
        model_path = self.get_model_path(model_name, category)
        return model_path is not None and Path(model_path).exists()
    
    def get_models_for_face_swap(self) -> List[Dict]:
        """Get all models suitable for face swapping (active + prebuilt)"""
        models = []
        
        # Get active models
        active_models = self.get_active_models()
        for model_name in active_models:
            model_info = self.get_model_info(model_name)
            if model_info:
                model_info["priority"] = "high"  # Active models have high priority
                models.append(model_info)
        
        # Get prebuilt models
        prebuilt_models = self.get_prebuilt_models()
        for model_name in prebuilt_models:
            model_info = self.get_model_info(model_name)
            if model_info:
                model_info["priority"] = "medium"  # Prebuilt models have medium priority
                models.append(model_info)
        
        return models
    
    def get_system_info(self) -> Dict:
        """Get information about the universal DFM system"""
        if not self.registry_file.exists():
            return {"status": "not_initialized"}
        
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        total_models = sum(len(models) for models in registry["categories"].values())
        
        return {
            "status": "active",
            "base_directory": str(self.base_dir),
            "total_models": total_models,
            "categories": {
                category: len(models) for category, models in registry["categories"].items()
            },
            "last_updated": registry.get("last_updated", "unknown")
        }

# Convenience functions for easy integration
def get_model_path(model_name: str, category: str = "prebuilt") -> Optional[str]:
    """Quick function to get model path"""
    dfm = DFMIntegration()
    return dfm.get_model_path(model_name, category)

def list_available_models(category: str = "all") -> List[str]:
    """Quick function to list available models"""
    dfm = DFMIntegration()
    return dfm.list_models_by_category(category)

def get_face_swap_models() -> List[Dict]:
    """Quick function to get models suitable for face swapping"""
    dfm = DFMIntegration()
    return dfm.get_models_for_face_swap()

def check_system_status() -> Dict:
    """Quick function to check system status"""
    dfm = DFMIntegration()
    return dfm.get_system_info()

# Example usage for DeepFaceLab integration
class DeepFaceLabIntegration:
    """Integration class specifically for DeepFaceLab"""
    
    def __init__(self):
        self.dfm = DFMIntegration()
    
    def get_model_for_training(self, model_name: str) -> Optional[str]:
        """Get model path for training purposes"""
        # Try active first, then prebuilt
        for category in ["active", "prebuilt"]:
            model_path = self.dfm.get_model_path(model_name, category)
            if model_path:
                return model_path
        return None
    
    def get_models_for_inference(self) -> List[Dict]:
        """Get models suitable for inference/face swapping"""
        return self.dfm.get_models_for_face_swap()
    
    def validate_model(self, model_name: str) -> bool:
        """Validate that a model exists and is accessible"""
        return self.dfm.model_exists(model_name)

if __name__ == "__main__":
    # Example usage
    print("Universal DFM Integration Test")
    print("=" * 40)
    
    # Check system status
    status = check_system_status()
    print(f"System Status: {status['status']}")
    if status['status'] == 'active':
        print(f"Total Models: {status['total_models']}")
    else:
        print("System not initialized")
    
    # List available models
    models = list_available_models("prebuilt")
    print(f"\nPrebuilt Models ({len(models)}):")
    for model in models[:5]:  # Show first 5
        print(f"  - {model}")
    if len(models) > 5:
        print(f"  ... and {len(models) - 5} more")
    
    # Test model path retrieval
    model_path = get_model_path("kevin_hart_model", "prebuilt")
    if model_path:
        print(f"\nKevin Hart Model Path: {model_path}")
    
    # Test DeepFaceLab integration
    dfl = DeepFaceLabIntegration()
    training_model = dfl.get_model_for_training("kevin_hart_model")
    if training_model:
        print(f"Training Model Path: {training_model}")
    
    print("\n✅ Integration test completed successfully!") 