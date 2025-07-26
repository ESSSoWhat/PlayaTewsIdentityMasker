
# Simple DFM Compatibility Wrapper
# Handles placeholder models by using InsightFaceSwap as fallback

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def handle_placeholder_model(model_path):
    """Handle placeholder model by using InsightFaceSwap"""
    try:
        # Check if InsightFaceSwap is available
        import modelhub.onnx.InsightFaceSwap as InsightFaceSwap
        from xlib.onnxruntime.device import ORTDeviceInfo
        from xlib import onnxruntime as lib_ort
        
        # Get CPU device
        device = lib_ort.get_cpu_device_info()
        
        # Create InsightFaceSwap instance
        insight_model = InsightFaceSwap(device)
        
        logger.info("Using InsightFaceSwap as fallback for placeholder model")
        return insight_model
        
    except ImportError as e:
        logger.error(f"InsightFaceSwap not available: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize InsightFaceSwap: {e}")
        return None

def is_placeholder_model(model_path):
    """Check if model file is a placeholder"""
    try:
        with open(model_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.strip().startswith('{'):
            try:
                data = json.loads(content)
                return data.get('is_placeholder', False)
            except json.JSONDecodeError:
                pass
    except Exception:
        pass
    
    return False
