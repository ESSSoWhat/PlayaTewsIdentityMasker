"""
Optimized Test Configuration for DeepFaceLive
Provides shared fixtures, mocks, and performance optimizations
"""

import pytest
import time
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import numpy as np

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Global test configuration
TEST_CONFIG = {
    'mock_by_default': True,
    'use_real_hardware': False,
    'benchmark_enabled': True,
    'timeout_default': 30
}

# ============================================================================
# Session-scoped fixtures (expensive setup, shared across all tests)
# ============================================================================

@pytest.fixture(scope="session")
def mock_numpy():
    """Mock numpy for tests that don't need real computation"""
    mock_np = Mock()
    mock_np.zeros = Mock(return_value=Mock())
    mock_np.array = Mock(return_value=Mock())
    mock_np.float32 = np.float32
    mock_np.uint8 = np.uint8
    return mock_np


@pytest.fixture(scope="session")
def mock_opencv():
    """Mock OpenCV for camera-independent tests"""
    mock_cv2 = Mock()
    
    # Mock VideoCapture
    mock_cap = Mock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
    mock_cap.get.return_value = 30.0  # Mock FPS
    mock_cap.release.return_value = None
    
    mock_cv2.VideoCapture.return_value = mock_cap
    mock_cv2.CAP_PROP_FPS = 5
    mock_cv2.CAP_PROP_FRAME_WIDTH = 3
    mock_cv2.CAP_PROP_FRAME_HEIGHT = 4
    
    return mock_cv2


@pytest.fixture(scope="session")
def test_video_frame():
    """Cached test video frame for consistent testing"""
    if not hasattr(test_video_frame, '_frame'):
        test_video_frame._frame = np.random.randint(
            0, 255, (480, 640, 3), dtype=np.uint8
        )
    return test_video_frame._frame


@pytest.fixture(scope="session")
def performance_monitor():
    """Shared performance monitor for all tests"""
    class TestPerformanceMonitor:
        def __init__(self):
            self.metrics = []
            self.start_time = time.time()
        
        def record_metric(self, test_name, metric_type, value):
            self.metrics.append({
                'test': test_name,
                'type': metric_type,
                'value': value,
                'timestamp': time.time()
            })
        
        def get_summary(self):
            return {
                'total_tests': len(set(m['test'] for m in self.metrics)),
                'total_time': time.time() - self.start_time,
                'metrics': self.metrics
            }
    
    return TestPerformanceMonitor()

# ============================================================================
# Function-scoped fixtures (reset for each test)
# ============================================================================

@pytest.fixture
def temp_test_dir(tmp_path):
    """Temporary directory for each test"""
    test_dir = tmp_path / "deepface_test"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def mock_gpu_available():
    """Mock GPU availability for consistent testing"""
    with patch('torch.cuda.is_available', return_value=True):
        with patch('torch.cuda.device_count', return_value=1):
            yield True


@pytest.fixture
def mock_gpu_unavailable():
    """Mock GPU unavailability for fallback testing"""
    with patch('torch.cuda.is_available', return_value=False):
        with patch('torch.cuda.device_count', return_value=0):
            yield False


@pytest.fixture
def mock_camera_device():
    """Mock camera device for camera-dependent tests"""
    class MockCamera:
        def __init__(self):
            self.is_opened = True
            self.frame_count = 0
        
        def read(self):
            self.frame_count += 1
            return True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        def release(self):
            self.is_opened = False
        
        def isOpened(self):
            return self.is_opened
    
    return MockCamera()

# ============================================================================
# Auto-use fixtures (automatically applied)
# ============================================================================

@pytest.fixture(autouse=True)
def auto_mock_imports():
    """Automatically mock problematic imports unless real hardware is requested"""
    if not TEST_CONFIG['use_real_hardware']:
        # Mock heavy imports that may not be available
        mocks = {}
        
        # Mock deep learning frameworks if not available
        try:
            import torch
        except ImportError:
            mocks['torch'] = Mock()
            mocks['torch.cuda'] = Mock()
            mocks['torch.cuda.is_available'] = Mock(return_value=False)
        
        try:
            import cv2
        except ImportError:
            mocks['cv2'] = Mock()
        
        try:
            import numpy
        except ImportError:
            mocks['numpy'] = Mock()
        
        # Apply mocks
        with patch.dict('sys.modules', mocks):
            yield
    else:
        yield


@pytest.fixture(autouse=True)
def test_performance_tracking(request, performance_monitor):
    """Automatically track test performance"""
    test_name = request.node.name
    start_time = time.time()
    
    yield
    
    duration = time.time() - start_time
    performance_monitor.record_metric(test_name, 'duration', duration)
    
    # Alert on slow tests
    if duration > 1.0:  # 1 second threshold
        pytest.warns(UserWarning, f"Slow test detected: {test_name} took {duration:.2f}s")

# ============================================================================
# Parametrized fixtures for comprehensive testing
# ============================================================================

@pytest.fixture(params=[
    {'width': 640, 'height': 480, 'channels': 3},
    {'width': 1280, 'height': 720, 'channels': 3},
    {'width': 1920, 'height': 1080, 'channels': 3}
])
def video_resolution(request):
    """Test with different video resolutions"""
    return request.param


@pytest.fixture(params=[10, 30, 60])
def fps_values(request):
    """Test with different FPS values"""
    return request.param

# ============================================================================
# Conditional fixtures based on hardware availability
# ============================================================================

@pytest.fixture
def real_camera():
    """Real camera fixture - only available with --real-hardware flag"""
    if not TEST_CONFIG['use_real_hardware']:
        pytest.skip("Real hardware tests disabled. Use --real-hardware to enable.")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            pytest.skip("No camera available")
        yield cap
        cap.release()
    except ImportError:
        pytest.skip("OpenCV not available")


@pytest.fixture
def real_gpu():
    """Real GPU fixture - only available with GPU and --real-hardware flag"""
    if not TEST_CONFIG['use_real_hardware']:
        pytest.skip("Real hardware tests disabled. Use --real-hardware to enable.")
    
    try:
        import torch
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        yield torch.cuda.current_device()
    except ImportError:
        pytest.skip("PyTorch not available")

# ============================================================================
# Test data factories
# ============================================================================

@pytest.fixture
def frame_factory():
    """Factory for generating test video frames"""
    def create_frame(width=640, height=480, channels=3, dtype=np.uint8):
        return np.random.randint(0, 255, (height, width, channels), dtype=dtype)
    return create_frame


@pytest.fixture
def mask_factory():
    """Factory for generating test masks"""
    def create_mask(width=640, height=480, mask_type='random'):
        if mask_type == 'random':
            return np.random.randint(0, 2, (height, width), dtype=np.uint8) * 255
        elif mask_type == 'center':
            mask = np.zeros((height, width), dtype=np.uint8)
            center_x, center_y = width // 2, height // 2
            mask[center_y-50:center_y+50, center_x-50:center_x+50] = 255
            return mask
        else:
            return np.ones((height, width), dtype=np.uint8) * 255
    return create_mask

# ============================================================================
# Benchmark fixtures
# ============================================================================

@pytest.fixture
def benchmark_config():
    """Configuration for performance benchmarks"""
    return {
        'min_rounds': 5,
        'max_time': 1.0,
        'warmup': True,
        'warmup_iterations': 2
    }

# ============================================================================
# Pytest hooks for optimization
# ============================================================================

def pytest_configure(config):
    """Configure test session"""
    # Check for real hardware flag
    if config.getoption("--real-hardware", default=False):
        TEST_CONFIG['use_real_hardware'] = True
    
    print(f"\n[TEST] Test Configuration:")
    print(f"   Mock by default: {TEST_CONFIG['mock_by_default']}")
    print(f"   Real hardware: {TEST_CONFIG['use_real_hardware']}")
    print(f"   Benchmarks: {TEST_CONFIG['benchmark_enabled']}")


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--real-hardware",
        action="store_true",
        default=False,
        help="Enable tests that require real hardware (cameras, GPUs)"
    )
    parser.addoption(
        "--benchmark-only",
        action="store_true",
        default=False,
        help="Run only benchmark tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for optimization"""
    if config.getoption("--benchmark-only"):
        # Only run benchmark tests
        items[:] = [item for item in items if "benchmark" in item.keywords]
    
    # Add timeout marker to slow tests
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.timeout(60))
        elif "integration" in item.keywords:
            item.add_marker(pytest.mark.timeout(30))
        else:
            item.add_marker(pytest.mark.timeout(10))


@pytest.fixture(autouse=True, scope="session")
def session_performance_report(performance_monitor):
    """Generate performance report at end of session"""
    yield
    
    summary = performance_monitor.get_summary()
    print(f"\n[PERF] Performance Summary:")
    print(f"   Total tests: {summary['total_tests']}")
    print(f"   Total time: {summary['total_time']:.2f}s")
    
    if summary['metrics']:
        durations = [m['value'] for m in summary['metrics'] if m['type'] == 'duration']
        if durations:
            print(f"   Avg test time: {np.mean(durations):.3f}s")
            print(f"   Slowest test: {max(durations):.3f}s")
            print(f"   Fastest test: {min(durations):.3f}s")