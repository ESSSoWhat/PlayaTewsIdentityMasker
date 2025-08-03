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

# Testing and Coverage
pytest>=7.0.0,<8.0.0
pytest-cov>=4.0.0,<5.0.0
pytest-xdist>=3.0.0,<4.0.0
pytest-mock>=3.10.0,<4.0.0
pytest-html>=3.1.0,<4.0.0
coverage>=7.0.0,<8.0.0

# Security Scanning
safety>=2.3.0,<3.0.0
pip-audit>=2.4.0,<3.0.0

# Performance Testing
pytest-benchmark>=4.0.0,<5.0.0
memory-profiler>=0.60.0,<1.0.0

# Documentation
sphinx>=6.0.0,<7.0.0
sphinx-rtd-theme>=1.2.0,<2.0.0

# Pre-commit Hooks
pre-commit>=3.0.0,<4.0.0

# Type Checking
types-requests>=2.28.0,<3.0.0
types-PyYAML>=6.0.0,<7.0.0
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

[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["apps", "xlib", "resources"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
disallow_untyped_defs = true
check_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--cov=apps",
    "--cov=xlib",
    "--cov=resources",
    "--cov-report=html:htmlcov",
    "--cov-report=term-missing",
]
testpaths = ["tests", "apps"]
python_files = ["test_*.py", "*_test.py"]
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
"""
    
    with open(".pre-commit-config.yaml", "w") as f:
        f.write(pre_commit_config)
    
    print("✅ Created .pre-commit-config.yaml")

def create_test_structure():
    """Create comprehensive test structure"""
    print("Creating test structure...")
    
    # Create test directories
    test_dirs = [
        "tests/unit",
        "tests/integration", 
        "tests/performance",
        "tests/security"
    ]
    
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
        with open(f"{test_dir}/__init__.py", "w") as f:
            pass
    
    # Create basic test file
    test_file = '''"""Unit tests for PlayaTewsIdentityMasker."""

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
'''
    
    with open("tests/unit/test_basic.py", "w") as f:
        f.write(test_file)
    
    print("✅ Created test structure")

def create_ci_cd_config():
    """Create CI/CD configuration"""
    print("Creating CI/CD configuration...")
    
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
"""
    
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/ci.yml", "w") as f:
        f.write(github_workflow)
    
    print("✅ Created GitHub Actions CI/CD")

def create_scripts():
    """Create utility scripts for code quality"""
    print("Creating utility scripts...")
    
    os.makedirs("scripts", exist_ok=True)
    
    # Linting script
    lint_script = '''#!/usr/bin/env python3
"""Linting script for PlayaTewsIdentityMasker."""

import subprocess
import sys

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
'''
    
    with open("scripts/lint.py", "w") as f:
        f.write(lint_script)
    
    # Test script
    test_script = '''#!/usr/bin/env python3
"""Testing script for PlayaTewsIdentityMasker."""

import subprocess
import sys

def run_tests():
    """Run all tests."""
    print("🧪 Running Tests")
    print("=" * 50)
    
    try:
        result = subprocess.run("pytest tests/ -v", shell=True, check=True)
        print("✅ All tests passed!")
        sys.exit(0)
    except subprocess.CalledProcessError:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
'''
    
    with open("scripts/test.py", "w") as f:
        f.write(test_script)
    
    # Make scripts executable
    os.chmod("scripts/lint.py", 0o755)
    os.chmod("scripts/test.py", 0o755)
    
    print("✅ Created utility scripts")

def main():
    """Main function to setup all code quality tools"""
    print("🔧 Setting up Code Quality Tools for PlayaTewsIdentityMasker")
    print("=" * 70)
    
    # Create all configurations
    create_requirements_dev()
    create_pyproject_toml()
    create_pre_commit_config()
    create_test_structure()
    create_ci_cd_config()
    create_scripts()
    
    print(f"\n📋 Code Quality Setup Summary:")
    print("=" * 50)
    print("✅ Development Requirements: requirements-dev.txt")
    print("✅ Tool Configurations: pyproject.toml, .pre-commit-config.yaml")
    print("✅ Linting Tools: flake8, black, isort, mypy, bandit")
    print("✅ Testing Framework: pytest with coverage")
    print("✅ CI/CD Pipeline: GitHub Actions")
    print("✅ Test Structure: Basic test organization")
    print("✅ Utility Scripts: Automated quality checks")
    
    print(f"\n🎉 Code Quality Tools Setup Complete!")
    print(f"💡 Next Steps:")
    print(f"   1. Install dependencies: pip install -r requirements-dev.txt")
    print(f"   2. Install pre-commit: pre-commit install")
    print(f"   3. Run initial checks: python scripts/lint.py")
    print(f"   4. Run tests: python scripts/test.py")

if __name__ == "__main__":
    main() 