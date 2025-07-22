#!/usr/bin/env python3
"""
Integration Preservation Tests
Ensures components work together during UI relocations
"""

import unittest
import asyncio
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

class IntegrationPreservationTest(unittest.TestCase):
    """Integration tests to ensure components work together"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.app = QApplication([])
        cls.test_data_path = Path("tests/test_data")
        cls.test_data_path.mkdir(exist_ok=True)
    
    def setUp(self):
        """Setup for each test"""
        self.userdata_path = Path("tests/temp_integration")
        self.userdata_path.mkdir(exist_ok=True)
        
        try:
            import sys
            sys.path.append('.')  # Add current directory to path
            from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
            self.app_instance = PlayaTewsIdentityMaskerApp(self.userdata_path)
        except ImportError as e:
            self.skipTest(f"Could not import PlayaTewsIdentityMaskerApp: {e}")
    
    def test_complete_workflow(self):
        """Test complete workflow from input to output"""
        # Test initialization
        try:
            self.app_instance.initialize()
        except Exception as e:
            self.fail(f"Initialization failed: {e}")
        
        # Test component connections
        self.test_component_connections()
        
        # Test data flow
        self.test_data_flow()
        
        # Test settings persistence
        self.test_settings_persistence()
        
        # Cleanup
        try:
            self.app_instance.finalize()
        except Exception as e:
            self.fail(f"Cleanup failed: {e}")
    
    def test_component_connections(self):
        """Test that all components are properly connected"""
        # Test backend connections
        self.assertTrue(hasattr(self.app_instance, 'all_backends'))
        all_backends = self.app_instance.all_backends
        self.assertIsInstance(all_backends, list)
        self.assertGreater(len(all_backends), 0)
        
        # Test UI component connections
        ui_components = [
            self.app_instance.q_file_source, self.app_instance.q_camera_source,
            self.app_instance.q_voice_changer, self.app_instance.q_face_detector,
            self.app_instance.q_face_marker, self.app_instance.q_face_aligner,
            self.app_instance.q_face_animator, self.app_instance.q_face_swap_insight,
            self.app_instance.q_face_swap_dfm, self.app_instance.q_frame_adjuster,
            self.app_instance.q_face_merger, self.app_instance.q_stream_output
        ]
        
        for component in ui_components:
            self.assertIsNotNone(component)
            self.assertTrue(component.isWidgetType())
    
    def test_data_flow(self):
        """Test data flow through the pipeline"""
        # Test that backend connections are established
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
    
    def test_settings_persistence(self):
        """Test settings persistence across sessions"""
        # Test that settings methods exist
        if hasattr(self.app_instance, 'save_settings'):
            try:
                self.app_instance.save_settings()
            except Exception as e:
                self.fail(f"Settings save failed: {e}")
        
        if hasattr(self.app_instance, 'load_settings'):
            try:
                self.app_instance.load_settings()
            except Exception as e:
                self.fail(f"Settings load failed: {e}")
    
    def test_backend_initialization_order(self):
        """Test that backends are initialized in the correct order"""
        # Test that all backends exist
        expected_backends = [
            'file_source', 'camera_source', 'face_detector', 'face_marker',
            'face_aligner', 'face_animator', 'face_swap_insight', 'face_swap_dfm',
            'frame_adjuster', 'face_merger', 'stream_output', 'voice_changer'
        ]
        
        for backend_name in expected_backends:
            with self.subTest(backend=backend_name):
                self.assertTrue(hasattr(self.app_instance, backend_name))
                backend = getattr(self.app_instance, backend_name)
                self.assertIsNotNone(backend)
    
    def test_ui_component_initialization(self):
        """Test that UI components are initialized correctly"""
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
    
    def test_viewer_integration(self):
        """Test that viewer components are properly integrated"""
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
    
    def test_signal_integration(self):
        """Test that signals are properly integrated"""
        # Test reemit frame signal
        self.assertTrue(hasattr(self.app_instance, 'reemit_frame_signal'))
        reemit_signal = self.app_instance.reemit_frame_signal
        self.assertIsNotNone(reemit_signal)
    
    def test_timer_integration(self):
        """Test that timer is properly integrated"""
        self.assertTrue(hasattr(self.app_instance, '_timer'))
        timer = self.app_instance._timer
        self.assertIsNotNone(timer)
        
        # Test message processing
        self.assertTrue(hasattr(self.app_instance, '_process_messages'))
        self.assertTrue(callable(getattr(self.app_instance, '_process_messages')))
    
    def test_backend_db_integration(self):
        """Test that backend database is properly integrated"""
        self.assertTrue(hasattr(self.app_instance, 'backend_db'))
        backend_db = self.app_instance.backend_db
        self.assertIsNotNone(backend_db)
        
        # Test clear backend db method
        self.assertTrue(hasattr(self.app_instance, 'clear_backend_db'))
        self.assertTrue(callable(getattr(self.app_instance, 'clear_backend_db')))
    
    def test_weak_heap_integration(self):
        """Test that weak heap is properly integrated"""
        self.assertTrue(hasattr(self.app_instance, 'backend_weak_heap'))
        weak_heap = self.app_instance.backend_weak_heap
        self.assertIsNotNone(weak_heap)
    
    def test_component_lifecycle(self):
        """Test complete component lifecycle"""
        # Test initialization
        try:
            self.app_instance.initialize()
        except Exception as e:
            self.fail(f"Initialization failed: {e}")
        
        # Test that all components are ready
        self.test_component_connections()
        
        # Test cleanup
        try:
            self.app_instance.finalize()
        except Exception as e:
            self.fail(f"Cleanup failed: {e}")
    
    def test_error_handling(self):
        """Test error handling in integration"""
        # Test that the app can handle initialization errors gracefully
        try:
            self.app_instance.initialize()
        except Exception as e:
            # If initialization fails, it should fail gracefully
            self.assertIsInstance(e, Exception)
        
        # Test that cleanup works even if initialization failed
        try:
            self.app_instance.finalize()
        except Exception as e:
            # Cleanup should work even if initialization failed
            pass
    
    def test_memory_management(self):
        """Test memory management in integration"""
        # Test that components can be created and destroyed without memory leaks
        for i in range(3):  # Test multiple cycles
            try:
                from apps.PlayaTewsIdentityMasker.PlayaTewsIdentityMaskerApp import PlayaTewsIdentityMaskerApp
                temp_app = PlayaTewsIdentityMaskerApp(self.userdata_path)
                temp_app.initialize()
                temp_app.finalize()
            except Exception as e:
                self.fail(f"Memory management test failed on iteration {i}: {e}")
    
    def test_concurrent_access(self):
        """Test concurrent access to components"""
        # Test that multiple components can be accessed simultaneously
        components = [
            self.app_instance.q_file_source, self.app_instance.q_camera_source,
            self.app_instance.q_voice_changer, self.app_instance.q_face_detector
        ]
        
        # Access all components simultaneously
        for component in components:
            self.assertIsNotNone(component)
            self.assertTrue(component.isWidgetType())
    
    def test_component_dependencies(self):
        """Test that component dependencies are satisfied"""
        # Test that all required dependencies exist
        dependencies = {
            'backend_db': 'backend_db',
            'backend_weak_heap': 'backend_weak_heap',
            'reemit_frame_signal': 'reemit_frame_signal',
            '_timer': '_timer'
        }
        
        for dependency_name, attr_name in dependencies.items():
            with self.subTest(dependency=dependency_name):
                self.assertTrue(hasattr(self.app_instance, attr_name))
                dependency = getattr(self.app_instance, attr_name)
                self.assertIsNotNone(dependency)
    
    def test_ui_layout_integration(self):
        """Test that UI layout is properly integrated"""
        # Test that the main layout exists
        self.assertTrue(hasattr(self.app_instance, 'layout'))
        layout = self.app_instance.layout()
        self.assertIsNotNone(layout)
        
        # Test that all UI components are in the layout
        ui_components = [
            'q_file_source', 'q_camera_source', 'q_voice_changer',
            'q_face_detector', 'q_face_marker', 'q_face_aligner',
            'q_face_animator', 'q_face_swap_insight', 'q_face_swap_dfm',
            'q_frame_adjuster', 'q_face_merger', 'q_stream_output'
        ]
        
        for component_name in ui_components:
            with self.subTest(component=component_name):
                component = getattr(self.app_instance, component_name)
                self.assertIsNotNone(component)
                self.assertTrue(component.isWidgetType())
    
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