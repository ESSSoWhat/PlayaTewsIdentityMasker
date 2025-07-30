#!/usr/bin/env python3
"""
Unit Tests for Backend Components
Comprehensive testing of backend components with mocking and isolation
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestBackendBase:
    """Test backend base components"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_path = Path(self.temp_dir) / "test_states.dat"
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.unit
    def test_backend_db_creation(self):
        """Test BackendDB creation and basic operations"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendDB
            
            # Test creation
            db = BackendDB(self.settings_path)
            assert db is not None
            assert hasattr(db, 'get')
            assert hasattr(db, 'set')
            
            # Test basic operations
            db.set('test_key', 'test_value')
            value = db.get('test_key')
            assert value == 'test_value'
            
        except ImportError as e:
            pytest.skip(f"BackendDB not available: {e}")
    
    @pytest.mark.unit
    def test_backend_weak_heap_creation(self):
        """Test BackendWeakHeap creation and memory management"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendWeakHeap
            
            # Test creation with different sizes
            heap_small = BackendWeakHeap(size_mb=1)
            assert heap_small is not None
            
            heap_large = BackendWeakHeap(size_mb=1024)
            assert heap_large is not None
            
            # Test memory allocation
            test_data = b"test data for heap"
            ref = heap_small.add_data(test_data)
            assert ref is not None
            
            # Test data retrieval
            retrieved_data = heap_small.get_data(ref)
            assert retrieved_data == test_data
            
        except ImportError as e:
            pytest.skip(f"BackendWeakHeap not available: {e}")
    
    @pytest.mark.unit
    def test_backend_signal(self):
        """Test BackendSignal functionality"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendSignal
            
            signal = BackendSignal()
            assert signal is not None
            
            # Test signal sending and receiving
            signal.send()
            received = signal.recv()
            assert received is True
            
        except ImportError as e:
            pytest.skip(f"BackendSignal not available: {e}")
    
    @pytest.mark.unit
    def test_backend_connection(self):
        """Test BackendConnection functionality"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendConnection, BackendConnectionData
            
            # Test single producer connection
            conn = BackendConnection()
            assert conn is not None
            
            # Test multi-producer connection
            multi_conn = BackendConnection(multi_producer=True)
            assert multi_conn is not None
            
            # Test data writing and reading
            data = BackendConnectionData(uid="test")
            conn.write(data)
            
            read_data = conn.read()
            assert read_data is not None
            assert read_data._uid == "test"
            
        except ImportError as e:
            pytest.skip(f"BackendConnection not available: {e}")

class TestBackendWorkers:
    """Test backend worker components"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_path = Path(self.temp_dir) / "test_states.dat"
        
        # Create mock backend infrastructure
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendDB, BackendWeakHeap, BackendSignal, BackendConnection
            self.backend_db = BackendDB(self.settings_path)
            self.weak_heap = BackendWeakHeap(size_mb=512)
            self.reemit_signal = BackendSignal()
            self.bc_in = BackendConnection()
            self.bc_out = BackendConnection()
        except ImportError:
            pytest.skip("Backend components not available")
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.unit
    def test_file_source_worker(self):
        """Test FileSource worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FileSource
            
            worker = FileSource(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
            # Test state management
            state = worker.get_state()
            assert state is not None
            
        except ImportError as e:
            pytest.skip(f"FileSource not available: {e}")
    
    @pytest.mark.unit
    def test_camera_source_worker(self):
        """Test CameraSource worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import CameraSource
            
            worker = CameraSource(
                weak_heap=self.weak_heap,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
        except ImportError as e:
            pytest.skip(f"CameraSource not available: {e}")
    
    @pytest.mark.unit
    def test_face_detector_worker(self):
        """Test FaceDetector worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FaceDetector
            
            worker = FaceDetector(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.bc_in,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
        except ImportError as e:
            pytest.skip(f"FaceDetector not available: {e}")
    
    @pytest.mark.unit
    def test_face_marker_worker(self):
        """Test FaceMarker worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FaceMarker
            
            worker = FaceMarker(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.bc_in,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
        except ImportError as e:
            pytest.skip(f"FaceMarker not available: {e}")
    
    @pytest.mark.unit
    def test_face_aligner_worker(self):
        """Test FaceAligner worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FaceAligner
            
            worker = FaceAligner(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.bc_in,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
        except ImportError as e:
            pytest.skip(f"FaceAligner not available: {e}")
    
    @pytest.mark.unit
    def test_face_merger_worker(self):
        """Test FaceMerger worker"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FaceMerger
            
            worker = FaceMerger(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.bc_in,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            assert worker is not None
            assert hasattr(worker, 'get_state')
            assert hasattr(worker, 'set_state')
            
        except ImportError as e:
            pytest.skip(f"FaceMerger not available: {e}")

class TestBackendDataStructures:
    """Test backend data structures"""
    
    @pytest.mark.unit
    def test_backend_connection_data(self):
        """Test BackendConnectionData functionality"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendConnectionData, BackendFaceSwapInfo
            
            # Test basic data creation
            data = BackendConnectionData(uid="test_uid")
            assert data._uid == "test_uid"
            
            # Test face swap info
            fsi = BackendFaceSwapInfo()
            assert fsi is not None
            assert fsi.image_name is None
            assert fsi.face_urect is None
            
            # Test adding face swap info
            data.add_face_swap_info(fsi)
            assert len(data._face_swap_info_list) == 1
            
        except ImportError as e:
            pytest.skip(f"BackendConnectionData not available: {e}")
    
    @pytest.mark.unit
    def test_backend_face_swap_info(self):
        """Test BackendFaceSwapInfo functionality"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendFaceSwapInfo
            from xlib.face import FRect, FLandmarks2D, FPose
            
            fsi = BackendFaceSwapInfo()
            
            # Test property assignment
            fsi.image_name = "test_image.jpg"
            fsi.face_urect = FRect(0, 0, 100, 100)
            fsi.face_pose = FPose()
            fsi.face_ulmrks = FLandmarks2D()
            
            assert fsi.image_name == "test_image.jpg"
            assert fsi.face_urect is not None
            assert fsi.face_pose is not None
            assert fsi.face_ulmrks is not None
            
        except ImportError as e:
            pytest.skip(f"BackendFaceSwapInfo not available: {e}")

class TestBackendIntegration:
    """Test backend component integration"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_path = Path(self.temp_dir) / "test_states.dat"
        
        # Create backend infrastructure
        try:
            from apps.PlayaTewsIdentityMasker.backend import (
                BackendDB, BackendWeakHeap, BackendSignal, BackendConnection
            )
            self.backend_db = BackendDB(self.settings_path)
            self.weak_heap = BackendWeakHeap(size_mb=1024)
            self.reemit_signal = BackendSignal()
            
            # Create connection chain
            self.multi_sources_bc_out = BackendConnection(multi_producer=True)
            self.face_detector_bc_out = BackendConnection()
            self.face_marker_bc_out = BackendConnection()
            self.face_aligner_bc_out = BackendConnection()
            self.face_swapper_bc_out = BackendConnection()
            self.frame_adjuster_bc_out = BackendConnection()
            self.face_merger_bc_out = BackendConnection()
            
        except ImportError:
            pytest.skip("Backend components not available")
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.integration
    def test_backend_pipeline_creation(self):
        """Test creation of complete backend pipeline"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import (
                FileSource, CameraSource, FaceDetector, FaceMarker,
                FaceAligner, FaceMerger
            )
            
            # Create source components
            file_source = FileSource(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_out=self.multi_sources_bc_out,
                backend_db=self.backend_db
            )
            
            camera_source = CameraSource(
                weak_heap=self.weak_heap,
                bc_out=self.multi_sources_bc_out,
                backend_db=self.backend_db
            )
            
            # Create processing pipeline
            face_detector = FaceDetector(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.multi_sources_bc_out,
                bc_out=self.face_detector_bc_out,
                backend_db=self.backend_db
            )
            
            face_marker = FaceMarker(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.face_detector_bc_out,
                bc_out=self.face_marker_bc_out,
                backend_db=self.backend_db
            )
            
            face_aligner = FaceAligner(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.face_marker_bc_out,
                bc_out=self.face_aligner_bc_out,
                backend_db=self.backend_db
            )
            
            face_merger = FaceMerger(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_in=self.face_aligner_bc_out,
                bc_out=self.face_merger_bc_out,
                backend_db=self.backend_db
            )
            
            # Verify all components created successfully
            assert file_source is not None
            assert camera_source is not None
            assert face_detector is not None
            assert face_marker is not None
            assert face_aligner is not None
            assert face_merger is not None
            
        except ImportError as e:
            pytest.skip(f"Backend pipeline components not available: {e}")
    
    @pytest.mark.integration
    def test_backend_state_persistence(self):
        """Test backend state persistence across components"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import FileSource
            
            # Create component
            file_source = FileSource(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            # Set state
            state = file_source.get_state()
            state.test_setting = "test_value"
            file_source.set_state(state)
            
            # Create new component instance
            file_source2 = FileSource(
                weak_heap=self.weak_heap,
                reemit_frame_signal=self.reemit_signal,
                bc_out=self.bc_out,
                backend_db=self.backend_db
            )
            
            # Verify state persistence
            state2 = file_source2.get_state()
            assert hasattr(state2, 'test_setting')
            assert state2.test_setting == "test_value"
            
        except ImportError as e:
            pytest.skip(f"Backend state persistence not available: {e}")

class TestBackendPerformance:
    """Test backend performance characteristics"""
    
    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.settings_path = Path(self.temp_dir) / "test_states.dat"
        
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendDB, BackendWeakHeap, BackendSignal, BackendConnection
            self.backend_db = BackendDB(self.settings_path)
            self.weak_heap = BackendWeakHeap(size_mb=1024)
            self.reemit_signal = BackendSignal()
            self.bc_in = BackendConnection()
            self.bc_out = BackendConnection()
        except ImportError:
            pytest.skip("Backend components not available")
    
    def teardown_method(self):
        """Cleanup after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.benchmark
    def test_weak_heap_performance(self, benchmark):
        """Benchmark weak heap performance"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendWeakHeap
            
            def heap_operations():
                heap = BackendWeakHeap(size_mb=512)
                refs = []
                
                # Add data
                for i in range(100):
                    data = f"test_data_{i}".encode()
                    ref = heap.add_data(data)
                    refs.append(ref)
                
                # Retrieve data
                for ref in refs:
                    data = heap.get_data(ref)
                    assert data is not None
                
                return len(refs)
            
            result = benchmark(heap_operations)
            assert result == 100
            
        except ImportError as e:
            pytest.skip(f"Weak heap not available: {e}")
    
    @pytest.mark.benchmark
    def test_connection_performance(self, benchmark):
        """Benchmark connection performance"""
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendConnection, BackendConnectionData
            
            def connection_operations():
                conn = BackendConnection()
                data_count = 0
                
                # Write data
                for i in range(50):
                    data = BackendConnectionData(uid=f"test_{i}")
                    conn.write(data)
                    data_count += 1
                
                # Read data
                for i in range(50):
                    data = conn.read()
                    if data is not None:
                        data_count += 1
                
                return data_count
            
            result = benchmark(connection_operations)
            assert result >= 50  # At least writes should succeed
            
        except ImportError as e:
            pytest.skip(f"Connection not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 