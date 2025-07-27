# Tests Directory

This directory contains all test files for the PlayaTews Identity Masker project, organized by category and functionality.

## Directory Structure

```
tests/
├── components/      # Component-specific tests
├── performance/     # Performance and optimization tests
├── ui/             # User interface tests
├── voice_changer/  # Voice changer functionality tests
├── integration/    # Integration tests
├── unit/           # Unit tests
├── validation_data/ # Test data and validation files
├── conftest.py     # Pytest configuration
├── baseline_functionality.json # Baseline test data
└── README.md       # This file
```

## Test Categories

### Components Tests (`tests/components/`)
Tests for individual components and functionality modules:
- `test_all_components.py` - Comprehensive component testing
- `test_backend_components.py` - Backend component tests
- `test_face_swap_functionality.py` - Face swap feature tests
- `test_dfm_quick_access.py` - DFM model access tests
- `test_global_face_swap_control.py` - Global face swap control tests
- `test_global_face_swap_demo.py` - Face swap demo tests

### Performance Tests (`tests/performance/`)
Tests focused on performance, optimization, and resource usage:
- `test_fps_optimization.py` - FPS optimization tests
- `test_memory_optimization.py` - Memory usage optimization tests
- `test_optimizations.py` - General optimization tests
- `test_optimizations_applied.py` - Applied optimization verification
- `test_optimized_app_startup.py` - Startup performance tests
- `test_optimized_ui.py` - UI performance tests

### UI Tests (`tests/ui/`)
Tests for user interface components and interactions:
- `test_ui_components.py` - UI component tests
- `test_ui_optimizations.py` - UI optimization tests
- `test_ui_optimizations_simple.py` - Simple UI optimization tests
- `test_simple_ui.py` - Basic UI functionality tests

### Voice Changer Tests (`tests/voice_changer/`)
Tests specific to voice changer functionality:
- `test_voice_changer.py` - Main voice changer tests
- `test_voice_changer_deps.py` - Voice changer dependency tests
- `test_voice_changer_simple.py` - Simple voice changer tests
- `test_pyqt5_voice_changer_compatibility.py` - PyQt5 compatibility tests

### General Tests (Root of tests/)
General application and functionality tests:
- `test_app.py` - Main application tests
- `test_app_running.py` - Application runtime tests
- `test_app_status.py` - Application status tests
- `test_anonymous_streaming.py` - Anonymous streaming tests
- `test_camera_fix.py` - Camera functionality tests
- `test_crash_prevention.py` - Crash prevention tests
- `test_deepfacelab_optimization.py` - DeepFaceLab optimization tests
- `test_device_availability.py` - Device availability tests
- `test_gpu_setup.py` - GPU setup and configuration tests
- `test_lazy_loading.py` - Lazy loading functionality tests
- `test_lazy_loading_simple.py` - Simple lazy loading tests
- `test_minimal_optimized.py` - Minimal optimization tests
- `test_obs_interface.py` - OBS interface tests
- `test_popup_window.py` - Popup window tests
- `test_processing_window.py` - Processing window tests
- `test_stream_output.py` - Stream output tests

## Running Tests

### Prerequisites
1. Install pytest: `pip install pytest`
2. Install test dependencies: `pip install -r requirements_test.txt`
3. Ensure all main application dependencies are installed

### Running All Tests
```bash
# From the project root
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage
pytest tests/ --cov=.
```

### Running Specific Test Categories
```bash
# Run only component tests
pytest tests/components/

# Run only performance tests
pytest tests/performance/

# Run only UI tests
pytest tests/ui/

# Run only voice changer tests
pytest tests/voice_changer/
```

### Running Individual Tests
```bash
# Run a specific test file
pytest tests/test_app.py

# Run a specific test function
pytest tests/test_app.py::test_app_startup

# Run tests matching a pattern
pytest -k "voice_changer"
```

## Test Configuration

### Pytest Configuration (`conftest.py`)
Contains shared fixtures and configuration for all tests:
- Common test data
- Mock objects
- Test environment setup
- Shared utilities

### Baseline Data (`baseline_functionality.json`)
Contains baseline test data for regression testing and validation.

## Test Guidelines

### Writing New Tests
1. Follow the existing naming convention: `test_<feature>_<aspect>.py`
2. Place tests in the appropriate category directory
3. Use descriptive test function names
4. Include proper setup and teardown
5. Add docstrings explaining test purpose

### Test Structure
```python
def test_feature_functionality():
    """
    Test description of what this test verifies.
    """
    # Arrange
    # Setup test data and conditions
    
    # Act
    # Execute the functionality being tested
    
    # Assert
    # Verify the expected outcomes
```

### Best Practices
- Keep tests independent and isolated
- Use meaningful test data
- Clean up resources after tests
- Mock external dependencies when appropriate
- Test both success and failure scenarios
- Include edge case testing

## Continuous Integration

Tests are automatically run in CI/CD pipelines:
- Unit tests run on every commit
- Integration tests run on pull requests
- Performance tests run on scheduled intervals
- All tests must pass before merging

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Path Issues**: Run tests from the project root directory
3. **Resource Conflicts**: Some tests may require exclusive access to devices
4. **Timing Issues**: Some tests may be sensitive to system performance

### Debug Mode
Run tests with debug output:
```bash
pytest tests/ -v -s --tb=long
```

### Test Isolation
Run tests in isolation to avoid conflicts:
```bash
pytest tests/ --dist=no
```

## Contributing

When adding new tests:
1. Follow the existing organization structure
2. Update this README if adding new categories
3. Ensure tests are comprehensive and well-documented
4. Add appropriate error handling and cleanup
5. Test on multiple environments when possible 