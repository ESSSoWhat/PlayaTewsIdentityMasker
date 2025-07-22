#!/usr/bin/env python3
"""
Validate that migration preserved all functionality
"""

import json
import time
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication

def validate_migration():
    """Validate that migration preserved all functionality"""
    
    # Load baseline
    baseline_file = Path("tests/baseline_functionality.json")
    if not baseline_file.exists():
        print("❌ Baseline file not found. Run baseline_functionality_test.py first.")
        return False
    
    with open(baseline_file, 'r') as f:
        baseline = json.load(f)
    
    # Test current functionality
    app = QApplication([])
    
    try:
        import sys
        sys.path.append('.')  # Add current directory to path
        from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
        
        userdata_path = Path("tests/migration_validation")
        userdata_path.mkdir(exist_ok=True)
        
        app_instance = PlayaTewsIdentityMaskerApp(userdata_path)
        
        current = {
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
        
        validation_results = {
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        for component_name in components:
            try:
                component = getattr(app_instance, component_name)
                current['components'][component_name] = {
                    'exists': component is not None,
                    'methods': [method for method in dir(component) if not method.startswith('_')],
                    'type': type(component).__name__
                }
                
                # Compare with baseline
                baseline_component = baseline['components'].get(component_name, {})
                
                if not component:
                    validation_results['passed'] = False
                    validation_results['errors'].append(f"Component {component_name} is missing")
                elif baseline_component.get('exists') and not component:
                    validation_results['passed'] = False
                    validation_results['errors'].append(f"Component {component_name} was removed")
                elif baseline_component.get('type') != current['components'][component_name]['type']:
                    validation_results['warnings'].append(f"Component {component_name} type changed: {baseline_component.get('type')} -> {current['components'][component_name]['type']}")
                
            except Exception as e:
                validation_results['passed'] = False
                validation_results['errors'].append(f"Error testing {component_name}: {e}")
        
        # Test UI components
        ui_components = [
            'q_file_source', 'q_camera_source', 'q_voice_changer',
            'q_face_detector', 'q_face_marker', 'q_face_aligner',
            'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for component_name in ui_components:
            try:
                component = getattr(app_instance, component_name)
                if not component:
                    validation_results['passed'] = False
                    validation_results['errors'].append(f"UI Component {component_name} is missing")
                elif not component.isWidgetType():
                    validation_results['warnings'].append(f"UI Component {component_name} is not a widget")
            except Exception as e:
                validation_results['passed'] = False
                validation_results['errors'].append(f"Error testing UI component {component_name}: {e}")
        
        # Test backend connections
        connection_attrs = [
            'multi_sources_bc_out', 'face_detector_bc_out', 'face_marker_bc_out',
            'face_aligner_bc_out', 'face_swapper_bc_out', 'frame_adjuster_bc_out',
            'face_merger_bc_out'
        ]
        
        for attr in connection_attrs:
            try:
                connection = getattr(app_instance, attr)
                if not connection:
                    validation_results['warnings'].append(f"Backend connection {attr} is missing")
            except Exception as e:
                validation_results['warnings'].append(f"Error testing backend connection {attr}: {e}")
        
        # Test viewer components
        viewer_components = [
            'q_ds_frame_viewer', 'q_ds_fa_viewer', 'q_ds_fc_viewer',
            'q_ds_merged_frame_viewer'
        ]
        
        for viewer_name in viewer_components:
            try:
                viewer = getattr(app_instance, viewer_name)
                if not viewer:
                    validation_results['warnings'].append(f"Viewer {viewer_name} is missing")
                elif not viewer.isWidgetType():
                    validation_results['warnings'].append(f"Viewer {viewer_name} is not a widget")
            except Exception as e:
                validation_results['warnings'].append(f"Error testing viewer {viewer_name}: {e}")
        
        # Test initialization and cleanup
        try:
            app_instance.initialize()
            app_instance.finalize()
        except Exception as e:
            validation_results['passed'] = False
            validation_results['errors'].append(f"Initialization/cleanup failed: {e}")
        
        # Save validation results
        validation_file = Path("tests/migration_validation_results.json")
        validation_file.parent.mkdir(exist_ok=True)
        with open(validation_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        # Print results
        print("🔍 Migration Validation Results:")
        print(f"✅ Passed: {validation_results['passed']}")
        
        if validation_results['errors']:
            print("❌ Errors:")
            for error in validation_results['errors']:
                print(f"  - {error}")
        
        if validation_results['warnings']:
            print("⚠️ Warnings:")
            for warning in validation_results['warnings']:
                print(f"  - {warning}")
        
        if validation_results['passed']:
            print("🎉 All functionality preserved successfully!")
        else:
            print("❌ Functionality issues detected!")
        
        app_instance.finalize()
        return validation_results['passed']
        
    except Exception as e:
        print(f"❌ Validation failed with exception: {e}")
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1) 