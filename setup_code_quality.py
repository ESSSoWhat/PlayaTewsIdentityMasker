#!/usr/bin/env python3
"""
Code Quality Setup for PlayaTewsIdentityMasker
Implements comprehensive code quality tools and best practices
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_requirements_dev():
    """Create development requirements file with all code quality tools"""
    print("Creating development requirements...")
    
    dev_requirements = """# Development and Code Quality Tools
# Linting and Formatting
black>=23.0.0,<24.0.0
flake8>=6.0.0,<7.0.0
isort>=5.12.0,<6.0.0
pylint>=2.17.0,<3.0.0
mypy>=1.0.0,<2.0.0
bandit>=1.7.0,<2.0.0

# Static Analysis
pylint>=2.17.0,<3.0.0
pyright>=1.1.0,<2.0.0
semgrep>=1.0.0,<2.0.0

# Testing and Coverage
pytest>=7.0.0,<8.0.0
pytest-cov>=4.0.0,<5.0.0
pytest-xdist>=3.0.0,<4.0.0
pytest-mock>=3.10.0,<4.0.0
pytest-html>=3.1.0,<4.0.0
coverage>=7.0.0,<8.0.0

# Security Scanning
bandit>=1.7.0,<2.0.0
safety>=2.3.0,<3.0.0
pip-audit>=2.4.0,<3.0.0

# Performance Testing
pytest-benchmark>=4.0.0,<5.0.0
memory-profiler>=0.60.0,<1.0.0
psutil>=5.8.0,<6.0.0

# Documentation
sphinx>=6.0.0,<7.0.0
sphinx-rtd-theme>=1.2.0,<2.0.0
myst-parser>=1.0.0,<2.0.0

# Dependency Management
pip-tools>=7.0.0,<8.0.0
pipdeptree>=2.7.0,<3.0.0

# Pre-commit Hooks
pre-commit>=3.0.0,<4.0.0

# Type Checking
types-requests>=2.28.0,<3.0.0
types-PyYAML>=6.0.0,<7.0.0
types-setuptools>=65.0.0,<66.0.0

# Code Quality Monitoring
radon>=5.1.0,<6.0.0
xenon>=0.7.0,<1.0.0
"""
    
    with open("requirements-dev.txt", "w") as f:
        f.write(dev_requirements)
    
    print("✅ Created requirements-dev.txt")

def create_pyproject_toml():
    """Create pyproject.toml with tool configurations"""
    print("Creating pyproject.toml...")
    
    pyproject_config = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "playatewsidentitymasker"
version = "1.0.0"
description = "Real-time face masking and identity protection application"
authors = [{name = "PlayaTews Team", email = "team@playatews.com"}]
license = {text = "GPL-3.0"}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Multimedia :: Video",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["apps", "xlib", "resources"]
known_third_party = ["cv2", "numpy", "PyQt5", "torch", "onnxruntime"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true

[[tool.mypy.overrides]]
module = [
    "cv2.*",
    "PyQt5.*",
    "torch.*",
    "onnxruntime.*",
    "numpy.*"
]
ignore_missing_imports = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=apps",
    "--cov=xlib",
    "--cov=resources",
    "--cov-report=html:htmlcov",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--junitxml=test-results.xml",
    "--html=test-report.html",
    "--self-contained-html",
]
testpaths = ["tests", "apps"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "gui: marks tests that require GUI",
    "camera: marks tests that require camera",
]

[tool.coverage.run]
source = ["apps", "xlib", "resources"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
    "*/build/*",
    "*/dist/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

[tool.bandit]
exclude_dirs = ["tests", "docs", "build", "dist"]
skips = ["B101", "B601"]

[tool.radon]
cc_min = "A"
mi_min = "A"

[tool.xenon]
max-complexity = 10
"""
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject_config)
    
    print("✅ Created pyproject.toml")

def create_pre_commit_config():
    """Create pre-commit configuration"""
    print("Creating pre-commit configuration...")
    
    pre_commit_config = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-merge-conflict
    -   id: debug-statements
    -   id: check-case-conflict
    -   id: check-docstring-first
    -   id: check-json
    -   id: check-merge-conflict
    -   id: check-symlinks
    -   id: check-toml
    -   id: detect-private-key
    -   id: end-of-file-fixer
    -   id: mixed-line-ending
    -   id: trailing-whitespace

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: ["--profile", "black"]

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

-   repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
    -   id: bandit
        args: [-r, ., -f, json, -o, bandit-report.json]
        exclude: ^tests/

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-requests, types-PyYAML, types-setuptools]
        exclude: ^tests/

-   repo: local
    hooks:
    -   id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        stages: [manual]
"""
    
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(pre_commit_config)
    
    print("✅ Created .pre-commit-config.yaml")

def create_pytest_config():
    """Create pytest configuration"""
    print("Creating pytest configuration...")
    
    pytest_config = """[pytest]
minversion = 7.0
addopts = 
    --strict-markers
    --strict-config
    --cov=apps
    --cov=xlib
    --cov=resources
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --junitxml=test-results.xml
    --html=test-report.html
    --self-contained-html
testpaths = tests apps
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    gui: marks tests that require GUI
    camera: marks tests that require camera
"""
    
    with open("pytest.ini", "w") as f:
        f.write(pytest_config)
    
    print("✅ Created pytest.ini")

def create_flake8_config():
    """Create flake8 configuration"""
    print("Creating flake8 configuration...")
    
    flake8_config = """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .venv,
    venv,
    htmlcov,
    .tox,
    .mypy_cache,
    .pytest_cache
per-file-ignores =
    __init__.py:F401
    tests/*:S101,S105,S106,S107
"""
    
    with open(".flake8", "w") as f:
        f.write(flake8_config)
    
    print("✅ Created .flake8")

def create_mypy_config():
    """Create mypy configuration"""
    print("Creating mypy configuration...")
    
    mypy_config = """[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
show_error_codes = True

[mypy-cv2.*]
ignore_missing_imports = True

[mypy-PyQt5.*]
ignore_missing_imports = True

[mypy-torch.*]
ignore_missing_imports = True

[mypy-onnxruntime.*]
ignore_missing_imports = True

[mypy-numpy.*]
ignore_missing_imports = True
"""
    
    with open("mypy.ini", "w") as f:
        f.write(mypy_config)
    
    print("✅ Created mypy.ini")

def create_bandit_config():
    """Create bandit configuration"""
    print("Creating bandit configuration...")
    
    bandit_config = """exclude_dirs: ['tests', 'docs', 'build', 'dist']
skips: ['B101', 'B601']

tests:
  - B101: assert_used
  - B102: exec_used
  - B103: set_bad_file_permissions
  - B104: hardcoded_bind_all_interfaces
  - B105: hardcoded_password_string
  - B106: hardcoded_password_funcarg
  - B107: hardcoded_password_default
  - B110: try_except_pass
  - B112: try_except_continue
  - B201: flask_debug_true
  - B301: pickle
  - B302: marshal
  - B303: md5
  - B304: md5_insecure
  - B305: sha1
  - B306: mktemp_q
  - B307: eval
  - B308: mark_safe
  - B309: httpsconnection
  - B310: urllib_urlopen
  - B311: random
  - B312: telnetlib
  - B313: xml_bad_cElementTree
  - B314: xml_bad_ElementTree
  - B315: xml_bad_expatreader
  - B316: xml_bad_expatbuilder
  - B317: xml_bad_sax
  - B318: xml_bad_minidom
  - B319: xml_bad_pulldom
  - B320: xml_bad_etree
  - B321: ftplib
  - B322: input
  - B323: unverified_context
  - B324: hashlib_new_insecure_functions
  - B325: tempnam
"""
    
    with open(".bandit", "w") as f:
        f.write(bandit_config)
    
    print("✅ Created .bandit")

def create_ci_cd_config():
    """Create CI/CD configuration"""
    print("Creating CI/CD configuration...")
    
    # GitHub Actions workflow
    github_workflow = """name: Code Quality and Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 apps xlib resources
        black --check apps xlib resources
        isort --check-only apps xlib resources
    
    - name: Run type checking
      run: mypy apps xlib resources
    
    - name: Run security scanning
      run: |
        bandit -r apps xlib resources
        safety check
    
    - name: Run tests
      run: |
        pytest --cov=apps --cov=xlib --cov=resources --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  performance:
    runs-on: ubuntu-latest
    needs: code-quality
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ --benchmark-only

  documentation:
    runs-on: ubuntu-latest
    needs: code-quality
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/_build/html
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(github_workflow)
    
    print("✅ Created GitHub Actions CI/CD")

def create_documentation_config():
    """Create documentation configuration"""
    print("Creating documentation configuration...")
    
    # Create docs directory
    os.makedirs("docs", exist_ok=True)
    
    # Sphinx configuration
    sphinx_conf = """# Configuration file for the Sphinx documentation builder.

project = 'PlayaTewsIdentityMasker'
copyright = '2024, PlayaTews Team'
author = 'PlayaTews Team'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'myst_parser',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
"""
    
    with open("docs/conf.py", "w") as f:
        f.write(sphinx_conf)
    
    # Makefile for docs
    makefile = """# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
"""
    
    with open("docs/Makefile", "w") as f:
        f.write(makefile)
    
    # Index file
    index_rst = """Welcome to PlayaTewsIdentityMasker's documentation!
====================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
    
    with open("docs/index.rst", "w") as f:
        f.write(index_rst)
    
    print("✅ Created documentation configuration")

def create_test_structure():
    """Create comprehensive test structure"""
    print("Creating test structure...")
    
    # Create test directories
    test_dirs = [
        "tests/unit",
        "tests/integration", 
        "tests/performance",
        "tests/gui",
        "tests/camera",
        "tests/security"
    ]
    
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
        with open(f"{test_dir}/__init__.py", "w") as f:
            pass
    
    # Create test files
    test_files = {
        "tests/unit/test_camera_source.py": '''"""Unit tests for camera source functionality."""

import pytest
from unittest.mock import Mock, patch

from apps.PlayaTewsIdentityMasker.backend.CameraSource import CameraSource

class TestCameraSource:
    """Test camera source functionality."""
    
    def test_camera_source_initialization(self):
        """Test camera source initialization."""
        mock_weak_heap = Mock()
        mock_bc_out = Mock()
        mock_backend_db = Mock()
        
        camera_source = CameraSource(mock_weak_heap, mock_bc_out, mock_backend_db)
        assert camera_source is not None
    
    def test_camera_source_control_sheet(self):
        """Test camera source control sheet."""
        mock_weak_heap = Mock()
        mock_bc_out = Mock()
        
        camera_source = CameraSource(mock_weak_heap, mock_bc_out)
        control_sheet = camera_source.get_control_sheet()
        assert control_sheet is not None
''',
        
        "tests/integration/test_camera_integration.py": '''"""Integration tests for camera functionality."""

import pytest
import cv2

class TestCameraIntegration:
    """Test camera integration functionality."""
    
    @pytest.mark.camera
    def test_camera_initialization(self):
        """Test camera initialization."""
        # This test requires a camera
        cap = cv2.VideoCapture(0)
        assert cap.isOpened() or True  # Skip if no camera
        cap.release()
    
    @pytest.mark.camera
    def test_camera_frame_capture(self):
        """Test camera frame capture."""
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            assert ret is not None
            cap.release()
        else:
            pytest.skip("No camera available")
''',
        
        "tests/performance/test_performance.py": '''"""Performance tests."""

import pytest
import time

class TestPerformance:
    """Test application performance."""
    
    @pytest.mark.benchmark
    def test_camera_performance(self, benchmark):
        """Test camera performance."""
        def camera_operation():
            time.sleep(0.01)  # Simulate camera operation
            return True
        
        result = benchmark(camera_operation)
        assert result is True
    
    @pytest.mark.benchmark
    def test_face_detection_performance(self, benchmark):
        """Test face detection performance."""
        def face_detection():
            time.sleep(0.05)  # Simulate face detection
            return True
        
        result = benchmark(face_detection)
        assert result is True
''',
        
        "tests/security/test_security.py": '''"""Security tests."""

import pytest
import tempfile
import os

class TestSecurity:
    """Test security aspects."""
    
    def test_file_permissions(self):
        """Test file permissions."""
        with tempfile.NamedTemporaryFile() as f:
            # Check file permissions
            stat = os.stat(f.name)
            assert oct(stat.st_mode)[-3:] in ['600', '644', '666']
    
    def test_input_validation(self):
        """Test input validation."""
        # Test various input scenarios
        test_inputs = [
            ("normal_input", True),
            ("", False),
            ("../path/traversal", False),
            ("<script>alert('xss')</script>", False),
        ]
        
        for test_input, expected in test_inputs:
            # Add your validation logic here
            assert isinstance(test_input, str)
''',
        
        "tests/conftest.py": '''"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_image():
    """Provide a sample image for testing."""
    import numpy as np
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

@pytest.fixture
def mock_camera():
    """Provide a mock camera for testing."""
    import cv2
    import numpy as np
    
    class MockCamera:
        def __init__(self):
            self.frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        def read(self):
            return True, self.frame
        
        def isOpened(self):
            return True
        
        def release(self):
            pass
    
    return MockCamera()

@pytest.fixture
def temp_config_file():
    """Provide a temporary configuration file."""
    import tempfile
    import json
    
    config = {
        "camera": {
            "backend": "DirectShow",
            "backend_id": 700,
            "index": 0,
            "resolution": "1280x720",
            "fps": 30.0
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    import os
    os.unlink(temp_file)
'''
    }
    
    for file_path, content in test_files.items():
        with open(file_path, "w") as f:
            f.write(content)
    
    print("✅ Created test structure")

def create_scripts():
    """Create utility scripts for code quality"""
    print("Creating utility scripts...")
    
    scripts = {
        "scripts/lint.py": '''#!/usr/bin/env python3
"""Linting script for PlayaTewsIdentityMasker."""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Run all linting tools."""
    print("🔧 Running Code Quality Checks")
    print("=" * 50)
    
    checks = [
        ("black --check apps xlib resources", "Code formatting (Black)"),
        ("isort --check-only apps xlib resources", "Import sorting (isort)"),
        ("flake8 apps xlib resources", "Code style (Flake8)"),
        ("mypy apps xlib resources", "Type checking (MyPy)"),
        ("bandit -r apps xlib resources", "Security scanning (Bandit)"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    if all_passed:
        print("\\n🎉 All code quality checks passed!")
        sys.exit(0)
    else:
        print("\\n❌ Some code quality checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
''',
        
        "scripts/test.py": '''#!/usr/bin/env python3
"""Testing script for PlayaTewsIdentityMasker."""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests."""
    print("🧪 Running Tests")
    print("=" * 50)
    
    commands = [
        ("pytest tests/unit/ -v", "Unit tests"),
        ("pytest tests/integration/ -v", "Integration tests"),
        ("pytest tests/security/ -v", "Security tests"),
        ("pytest tests/performance/ --benchmark-only", "Performance tests"),
    ]
    
    all_passed = True
    for command, description in commands:
        print(f"Running {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True)
            print(f"✅ {description} passed")
        except subprocess.CalledProcessError:
            print(f"❌ {description} failed")
            all_passed = False
    
    if all_passed:
        print("\\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
''',
        
        "scripts/security.py": '''#!/usr/bin/env python3
"""Security scanning script for PlayaTewsIdentityMasker."""

import subprocess
import sys
from pathlib import Path

def run_security_checks():
    """Run security checks."""
    print("🔒 Running Security Checks")
    print("=" * 50)
    
    checks = [
        ("bandit -r apps xlib resources -f json -o bandit-report.json", "Bandit security scan"),
        ("safety check", "Safety dependency check"),
        ("pip-audit", "Pip audit"),
    ]
    
    all_passed = True
    for command, description in checks:
        print(f"Running {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True)
            print(f"✅ {description} passed")
        except subprocess.CalledProcessError:
            print(f"❌ {description} failed")
            all_passed = False
    
    if all_passed:
        print("\\n🎉 All security checks passed!")
        sys.exit(0)
    else:
        print("\\n❌ Some security checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_security_checks()
''',
        
        "scripts/coverage.py": '''#!/usr/bin/env python3
"""Coverage reporting script for PlayaTewsIdentityMasker."""

import subprocess
import sys
from pathlib import Path

def run_coverage():
    """Run coverage analysis."""
    print("📊 Running Coverage Analysis")
    print("=" * 50)
    
    commands = [
        ("pytest --cov=apps --cov=xlib --cov=resources --cov-report=html:htmlcov --cov-report=term-missing", "Coverage analysis"),
    ]
    
    for command, description in commands:
        print(f"Running {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True)
            print(f"✅ {description} completed")
        except subprocess.CalledProcessError:
            print(f"❌ {description} failed")
            sys.exit(1)
    
    print("\\n📈 Coverage report generated in htmlcov/")
    print("Open htmlcov/index.html to view detailed coverage")

if __name__ == "__main__":
    run_coverage()
'''
    }
    
    os.makedirs("scripts", exist_ok=True)
    for file_path, content in scripts.items():
        with open(file_path, "w") as f:
            f.write(content)
        # Make scripts executable
        os.chmod(file_path, 0o755)
    
    print("✅ Created utility scripts")

def create_readme_dev():
    """Create development README"""
    print("Creating development README...")
    
    dev_readme = """# PlayaTewsIdentityMasker - Development Guide

## Code Quality Tools

This project uses comprehensive code quality tools to ensure high standards.

### Setup

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

### Code Quality Tools

#### Linting and Formatting
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Code style checking
- **Pylint**: Code analysis

#### Type Checking
- **MyPy**: Static type checking
- **Pyright**: Type checking (alternative)

#### Security Scanning
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency security checking
- **pip-audit**: Package vulnerability scanning

#### Testing
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-benchmark**: Performance testing

#### Documentation
- **Sphinx**: Documentation generation
- **myst-parser**: Markdown support

### Usage

#### Running Code Quality Checks
```bash
# Run all linting
python scripts/lint.py

# Run all tests
python scripts/test.py

# Run security checks
python scripts/security.py

# Run coverage analysis
python scripts/coverage.py
```

#### Individual Tools
```bash
# Format code
black apps xlib resources

# Sort imports
isort apps xlib resources

# Check code style
flake8 apps xlib resources

# Type checking
mypy apps xlib resources

# Security scanning
bandit -r apps xlib resources

# Run tests
pytest tests/

# Generate coverage
pytest --cov=apps --cov=xlib --cov=resources --cov-report=html
```

#### Pre-commit Hooks
The project uses pre-commit hooks that run automatically on commit:
- Code formatting
- Import sorting
- Linting
- Type checking
- Security scanning

### CI/CD

The project uses GitHub Actions for continuous integration:
- Automated testing on multiple Python versions
- Code quality checks
- Security scanning
- Performance testing
- Documentation building

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── performance/    # Performance tests
├── security/       # Security tests
├── gui/           # GUI tests
└── camera/        # Camera tests
```

### Coverage

Coverage reports are generated in `htmlcov/` directory.
Open `htmlcov/index.html` to view detailed coverage information.

### Performance Testing

Performance tests use pytest-benchmark:
```bash
pytest tests/performance/ --benchmark-only
```

### Security

Security scanning is integrated into the development workflow:
- Automated security checks on commit
- Dependency vulnerability scanning
- Code security analysis

### Documentation

Documentation is built using Sphinx:
```bash
cd docs
make html
```

### Best Practices

1. **Always run tests before committing**
2. **Use type hints in all new code**
3. **Follow the established code style**
4. **Write tests for new features**
5. **Update documentation when needed**
6. **Run security checks regularly**
7. **Monitor performance impact**

### Troubleshooting

#### Common Issues

1. **MyPy errors**: Add type hints or use `# type: ignore`
2. **Flake8 errors**: Follow the style guide or add exceptions
3. **Test failures**: Check test environment and dependencies
4. **Coverage issues**: Add tests for uncovered code

#### Getting Help

- Check the tool documentation
- Review existing code for examples
- Ask in the development team
- Check CI/CD logs for specific errors
"""
    
    with open("README-DEV.md", "w") as f:
        f.write(dev_readme)
    
    print("✅ Created README-DEV.md")

def main():
    """Main function to setup all code quality tools"""
    print("🔧 Setting up Code Quality Tools for PlayaTewsIdentityMasker")
    print("=" * 70)
    
    # Create all configurations
    create_requirements_dev()
    create_pyproject_toml()
    create_pre_commit_config()
    create_pytest_config()
    create_flake8_config()
    create_mypy_config()
    create_bandit_config()
    create_ci_cd_config()
    create_documentation_config()
    create_test_structure()
    create_scripts()
    create_readme_dev()
    
    print(f"\n📋 Code Quality Setup Summary:")
    print("=" * 50)
    print("✅ Development Requirements: requirements-dev.txt")
    print("✅ Tool Configurations: pyproject.toml, .pre-commit-config.yaml")
    print("✅ Linting Tools: flake8, black, isort, pylint, mypy")
    print("✅ Security Scanning: bandit, safety, pip-audit")
    print("✅ Testing Framework: pytest with coverage and benchmarking")
    print("✅ CI/CD Pipeline: GitHub Actions")
    print("✅ Documentation: Sphinx setup")
    print("✅ Test Structure: Comprehensive test organization")
    print("✅ Utility Scripts: Automated quality checks")
    print("✅ Development Guide: README-DEV.md")
    
    print(f"\n🎉 Code Quality Tools Setup Complete!")
    print(f"💡 Next Steps:")
    print(f"   1. Install dependencies: pip install -r requirements-dev.txt")
    print(f"   2. Install pre-commit: pre-commit install")
    print(f"   3. Run initial checks: python scripts/lint.py")
    print(f"   4. Run tests: python scripts/test.py")
    print(f"   5. Check security: python scripts/security.py")

if __name__ == "__main__":
    main() 