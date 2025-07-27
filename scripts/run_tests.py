#!/usr/bin/env python3
"""
Master Test Runner for PlayaTews Identity Masker

This script provides a convenient way to run different categories of tests
and manage test execution across the project.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        
    def run_tests(self, category=None, pattern=None, verbose=False, coverage=False):
        """Run tests based on category and pattern"""
        cmd = ["python", "-m", "pytest"]
        
        if category:
            test_path = self.tests_dir / category
            if not test_path.exists():
                print(f"Error: Test category '{category}' not found")
                return False
            cmd.append(str(test_path))
        else:
            cmd.append(str(self.tests_dir))
        
        if pattern:
            cmd.extend(["-k", pattern])
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=.", "--cov-report=html"])
        
        print(f"Running: {' '.join(cmd)}")
        return subprocess.run(cmd).returncode == 0
    
    def list_categories(self):
        """List available test categories"""
        print("Available test categories:")
        for item in self.tests_dir.iterdir():
            if item.is_dir():
                test_count = len(list(item.glob("test_*.py")))
                print(f"  {item.name}/ ({test_count} test files)")
        
        # Count root level tests
        root_tests = len(list(self.tests_dir.glob("test_*.py")))
        if root_tests > 0:
            print(f"  root/ ({root_tests} test files)")
    
    def run_all_tests(self, verbose=False, coverage=False):
        """Run all tests"""
        print("Running all tests...")
        return self.run_tests(verbose=verbose, coverage=coverage)
    
    def run_component_tests(self, verbose=False):
        """Run component tests"""
        print("Running component tests...")
        return self.run_tests("components", verbose=verbose)
    
    def run_performance_tests(self, verbose=False):
        """Run performance tests"""
        print("Running performance tests...")
        return self.run_tests("performance", verbose=verbose)
    
    def run_ui_tests(self, verbose=False):
        """Run UI tests"""
        print("Running UI tests...")
        return self.run_tests("ui", verbose=verbose)
    
    def run_voice_changer_tests(self, verbose=False):
        """Run voice changer tests"""
        print("Running voice changer tests...")
        return self.run_tests("voice_changer", verbose=verbose)

def main():
    parser = argparse.ArgumentParser(description="PlayaTews Identity Masker Test Runner")
    parser.add_argument("--category", "-c", choices=["components", "performance", "ui", "voice_changer"],
                       help="Run tests from specific category")
    parser.add_argument("--pattern", "-k", help="Run tests matching pattern")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--list", "-l", action="store_true", help="List available test categories")
    parser.add_argument("--all", "-a", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        runner.list_categories()
        return
    
    success = True
    
    if args.all:
        success = runner.run_all_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.category:
        if args.category == "components":
            success = runner.run_component_tests(verbose=args.verbose)
        elif args.category == "performance":
            success = runner.run_performance_tests(verbose=args.verbose)
        elif args.category == "ui":
            success = runner.run_ui_tests(verbose=args.verbose)
        elif args.category == "voice_changer":
            success = runner.run_voice_changer_tests(verbose=args.verbose)
    else:
        success = runner.run_tests(pattern=args.pattern, verbose=args.verbose, coverage=args.coverage)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 