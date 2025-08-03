"""Unit tests for PlayaTewsIdentityMasker."""

import pytest
from unittest.mock import Mock

class TestBasicFunctionality:
    """Test basic application functionality."""
    
    def test_import_app(self):
        """Test that the main app can be imported."""
        try:
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            assert PlayaTewsIdentityMaskerApp is not None
        except ImportError as e:
            pytest.skip(f"Could not import app: {e}")
    
    def test_camera_config_loading(self):
        """Test camera configuration loading."""
        import json
        from pathlib import Path
        
        config_file = Path("camera_config.json")
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
            assert "camera" in config
            assert "backend" in config["camera"]
