#!/usr/bin/env python3
"""
Create baseline functionality test before migration
"""

import json
import time
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

def create_baseline():
    """Create baseline of current functionality"""
    app = QApplication([])
    
    try:
        import sys
        sys.path.append('.')  # Add current directory to path
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = Path("tests/baseline_data")
        userdata_path.mkdir(exist_ok=True)
        
        try:
            app_instance = PlayaTewsIdentityMaskerApp(userdata_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not create app instance: {e}")
            app_instance = None
        
        baseline = {
            'timestamp': time.time(),
            'components': {},
            'signals': {},
            'settings': {},
            'performance': {}
        }
        
        # Test all components
        components = [
            'file_source', 'camera_source', 'voice_changer',
            'face_detector', 'face_marker', 'face_aligner',
            'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger', 'stream_output'
        ]
        
        if app_instance is not None:
            for component_name in components:
                try:
                    component = getattr(app_instance, component_name)
                    baseline['components'][component_name] = {
                        'exists': component is not None,
                        'methods': [method for method in dir(component) if not method.startswith('_')],
                        'type': type(component).__name__
                    }
                except Exception as e:
                    print(f"⚠️ Warning: Could not access component {component_name}: {e}")
                    baseline['components'][component_name] = {
                        'exists': False,
                        'methods': [],
                        'type': 'Error',
                        'error': str(e)
                    }
        else:
            # If app instance creation failed, mark all components as errors
            for component_name in components:
                baseline['components'][component_name] = {
                    'exists': False,
                    'methods': [],
                    'type': 'Error',
                    'error': 'App instance creation failed'
                }
        
        # Save baseline
        baseline_file = Path("tests/baseline_functionality.json")
        baseline_file.parent.mkdir(exist_ok=True)
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"✅ Baseline created: {baseline_file}")
        
        # Try to finalize, but don't fail if it errors
        if app_instance is not None:
            try:
                app_instance.finalize()
            except Exception as finalize_error:
                print(f"⚠️ Warning: Finalization error (non-critical): {finalize_error}")
        
    except Exception as e:
        print(f"❌ Error creating baseline: {e}")
        return False
    finally:
        app.quit()
    
    return True

if __name__ == "__main__":
    success = create_baseline()
    sys.exit(0 if success else 1) 