#!/usr/bin/env python3
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