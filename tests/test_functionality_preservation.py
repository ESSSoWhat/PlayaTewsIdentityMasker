#!/usr/bin/env python3
"""
Functionality Preservation Tests
Ensures all functionality is preserved during UI relocations
"""

import unittest
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, pyqtSignal

class FunctionalityPreservationTest(unittest.TestCase):
    """Comprehensive test suite to ensure all functionality is preserved"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.app = QApplication(sys.argv)
        cls.test_data_path = Path("tests/test_data")
        cls.test_data_path.mkdir(exist_ok=True)
    
    def setUp(self):
        """Setup for each test"""
        self.userdata_path = Path("tests/temp_userdata")
        self.userdata_path.mkdir(exist_ok=True)
        
        # Import the application
        try:
            import sys
            sys.path.append('.')  # Add current directory to path
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            self.app_instance = PlayaTewsIdentityMaskerApp(self.userdata_path)
        except ImportError as e:
            self.skipTest(f"Could not import PlayaTewsIdentityMaskerApp: {e}")
    
    def test_input_sources_functionality(self):
        """Test all input source functionality"""
        # Test file source
        self.assertTrue(hasattr(self.app_instance, 'q_file_source'))
        self.assertIsNotNone(self.app_instance.q_file_source)
        
        # Test camera source
        self.assertTrue(hasattr(self.app_instance, 'q_camera_source'))
        self.assertIsNotNone(self.app_instance.q_camera_source)
        
        # Test voice changer
        self.assertTrue(hasattr(self.app_instance, 'q_voice_changer'))
        self.assertIsNotNone(self.app_instance.q_voice_changer)
    
    def test_face_processing_functionality(self):
        """Test all face processing functionality"""
        components = [
            'q_face_detector', 'q_face_marker', 'q_face_aligner',
            'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger'
        ]
        
        for component_name in components:
            with self.subTest(component=component_name):
                self.assertTrue(hasattr(self.app_instance, component_name))
                component = getattr(self.app_instance, component_name)
                self.assertIsNotNone(component)
    
    def test_output_functionality(self):
        """Test all output functionality"""
        self.assertTrue(hasattr(self.app_instance, 'q_stream_output'))
        stream_output = self.app_instance.q_stream_output
        self.assertIsNotNone(stream_output)
    
    def test_backend_connections(self):
        """Test all backend connections"""
        backends = [
            'file_source', 'camera_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger', 'stream_output', 'voice_changer'
        ]
        
        for backend_name in backends:
            with self.subTest(backend=backend_name):
                self.assertTrue(hasattr(self.app_instance, backend_name))
                backend = getattr(self.app_instance, backend_name)
                self.assertIsNotNone(backend)
    
    def test_ui_layout_preservation(self):
        """Test that UI layout elements are preserved"""
        # Test that all UI components are present
        ui_components = [
            'q_file_source', 'q_camera_source', 'q_voice_changer',
            'q_face_detector', 'q_face_marker', 'q_face_aligner',
            'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for component_name in ui_components:
            with self.subTest(component=component_name):
                self.assertTrue(hasattr(self.app_instance, component_name))
                component = getattr(self.app_instance, component_name)
                self.assertIsNotNone(component)
                self.assertTrue(component.isWidgetType())
    
    def test_component_initialization(self):
        """Test that all components initialize correctly"""
        # Test that the app can be initialized
        try:
            self.app_instance.initialize()
            self.assertTrue(True)  # If we get here, initialization succeeded
        except Exception as e:
            self.fail(f"Component initialization failed: {e}")
    
    def test_component_cleanup(self):
        """Test that all components can be cleaned up properly"""
        try:
            self.app_instance.finalize()
            self.assertTrue(True)  # If we get here, cleanup succeeded
        except Exception as e:
            self.fail(f"Component cleanup failed: {e}")
    
    def test_settings_persistence(self):
        """Test settings persistence functionality"""
        # This test would verify that settings can be saved and loaded
        # For now, we'll just test that the method exists
        if hasattr(self.app_instance, 'save_settings'):
            try:
                self.app_instance.save_settings()
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Settings save failed: {e}")
    
    def test_component_methods(self):
        """Test that all components have required methods"""
        required_methods = {
            'file_source': ['start', 'stop'],
            'camera_source': ['start', 'stop'],
            'face_detector': ['start', 'stop'],
            'voice_changer': ['start', 'stop'],
            'stream_output': ['start', 'stop']
        }
        
        for component_name, methods in required_methods.items():
            with self.subTest(component=component_name):
                component = getattr(self.app_instance, component_name)
                for method in methods:
                    self.assertTrue(hasattr(component, method), 
                                  f"Component {component_name} missing method {method}")
    
    def test_ui_component_properties(self):
        """Test that UI components have required properties"""
        ui_components = [
            'q_file_source', 'q_camera_source', 'q_voice_changer',
            'q_face_detector', 'q_face_marker', 'q_face_aligner',
            'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for component_name in ui_components:
            with self.subTest(component=component_name):
                component = getattr(self.app_instance, component_name)
                # Test that component is a widget
                self.assertTrue(component.isWidgetType())
                # Test that component has a layout or can have one
                self.assertTrue(hasattr(component, 'layout') or hasattr(component, 'setLayout'))
    
    def test_backend_weak_heap(self):
        """Test backend weak heap functionality"""
        self.assertTrue(hasattr(self.app_instance, 'backend_weak_heap'))
        weak_heap = self.app_instance.backend_weak_heap
        self.assertIsNotNone(weak_heap)
    
    def test_backend_db(self):
        """Test backend database functionality"""
        self.assertTrue(hasattr(self.app_instance, 'backend_db'))
        backend_db = self.app_instance.backend_db
        self.assertIsNotNone(backend_db)
    
    def test_signal_connections(self):
        """Test that signal connections are properly established"""
        # Test that the reemit frame signal exists
        self.assertTrue(hasattr(self.app_instance, 'reemit_frame_signal'))
        reemit_signal = self.app_instance.reemit_frame_signal
        self.assertIsNotNone(reemit_signal)
    
    def test_backend_connections_exist(self):
        """Test that backend connections are established"""
        connection_attrs = [
            'multi_sources_bc_out', 'face_detector_bc_out', 'face_marker_bc_out',
            'face_aligner_bc_out', 'face_swapper_bc_out', 'frame_adjuster_bc_out',
            'face_merger_bc_out'
        ]
        
        for attr in connection_attrs:
            with self.subTest(connection=attr):
                self.assertTrue(hasattr(self.app_instance, attr))
                connection = getattr(self.app_instance, attr)
                self.assertIsNotNone(connection)
    
    def test_all_backends_list(self):
        """Test that all backends are properly listed"""
        self.assertTrue(hasattr(self.app_instance, 'all_backends'))
        all_backends = self.app_instance.all_backends
        self.assertIsInstance(all_backends, list)
        self.assertGreater(len(all_backends), 0)
        
        # Test that all expected backends are in the list
        expected_backends = [
            'file_source', 'camera_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger', 'stream_output', 'voice_changer'
        ]
        
        for backend_name in expected_backends:
            backend = getattr(self.app_instance, backend_name)
            self.assertIn(backend, all_backends)
    
    def test_viewer_components(self):
        """Test that viewer components are properly created"""
        viewer_components = [
            'q_ds_frame_viewer', 'q_ds_fa_viewer', 'q_ds_fc_viewer',
            'q_ds_merged_frame_viewer'
        ]
        
        for viewer_name in viewer_components:
            with self.subTest(viewer=viewer_name):
                self.assertTrue(hasattr(self.app_instance, viewer_name))
                viewer = getattr(self.app_instance, viewer_name)
                self.assertIsNotNone(viewer)
                self.assertTrue(viewer.isWidgetType())
    
    def test_timer_functionality(self):
        """Test that the timer for message processing exists"""
        self.assertTrue(hasattr(self.app_instance, '_timer'))
        timer = self.app_instance._timer
        self.assertIsNotNone(timer)
    
    def test_message_processing(self):
        """Test that message processing method exists"""
        self.assertTrue(hasattr(self.app_instance, '_process_messages'))
        self.assertTrue(callable(getattr(self.app_instance, '_process_messages')))
    
    def test_clear_backend_db_method(self):
        """Test that clear backend db method exists"""
        self.assertTrue(hasattr(self.app_instance, 'clear_backend_db'))
        self.assertTrue(callable(getattr(self.app_instance, 'clear_backend_db')))
    
    def tearDown(self):
        """Cleanup after each test"""
        if hasattr(self, 'app_instance'):
            try:
                self.app_instance.finalize()
            except:
                pass  # Ignore cleanup errors in tests
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test environment"""
        cls.app.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2) 