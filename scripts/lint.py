#!/usr/bin/env python3
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
        print("\n🎉 All code quality checks passed!")
        sys.exit(0)
    else:
        print("\n❌ Some code quality checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
