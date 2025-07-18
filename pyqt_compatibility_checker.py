#!/usr/bin/env python3
"""
PyQt Compatibility Checker
Detects and prevents PyQt5/PyQt6 conflicts in the codebase
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set

class PyQtConflictDetector:
    """Detects PyQt version conflicts in Python files"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.pyqt5_files = []
        self.pyqt6_files = []
        self.mixed_files = []
        self.errors = []
        
    def scan_files(self) -> Dict[str, List[str]]:
        """Scan all Python files for PyQt imports"""
        python_files = list(self.root_path.rglob("*.py"))
        
        for file_path in python_files:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.pytest_cache', 'venv', 'env']):
                continue
                
            try:
                self._analyze_file(file_path)
            except Exception as e:
                self.errors.append(f"Error analyzing {file_path}: {e}")
        
        return {
            'pyqt5_files': self.pyqt5_files,
            'pyqt6_files': self.pyqt6_files,
            'mixed_files': self.mixed_files,
            'errors': self.errors
        }
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single file for PyQt imports"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check for PyQt imports using regex (faster than AST for this purpose)
        pyqt5_imports = re.findall(r'from\s+PyQt5\.|import\s+PyQt5', content)
        pyqt6_imports = re.findall(r'from\s+PyQt6\.|import\s+PyQt6', content)
        
        if pyqt5_imports and pyqt6_imports:
            self.mixed_files.append(str(file_path))
        elif pyqt5_imports:
            self.pyqt5_files.append(str(file_path))
        elif pyqt6_imports:
            self.pyqt6_files.append(str(file_path))
    
    def check_runtime_conflict(self) -> bool:
        """Check if both PyQt5 and PyQt6 are loaded in current runtime"""
        pyqt5_loaded = 'PyQt5' in sys.modules
        pyqt6_loaded = 'PyQt6' in sys.modules
        
        if pyqt5_loaded and pyqt6_loaded:
            print("🚨 CRITICAL: Both PyQt5 and PyQt6 are loaded in runtime!")
            print("This WILL cause crashes and memory corruption!")
            return True
        elif pyqt5_loaded:
            print("ℹ️  PyQt5 is currently loaded")
        elif pyqt6_loaded:
            print("ℹ️  PyQt6 is currently loaded")
        else:
            print("ℹ️  No PyQt modules are currently loaded")
        
        return False
    
    def generate_migration_plan(self) -> List[str]:
        """Generate step-by-step migration plan"""
        plan = []
        
        if self.mixed_files:
            plan.append("🔥 CRITICAL: Fix mixed PyQt files immediately:")
            for file_path in self.mixed_files:
                plan.append(f"   - {file_path}")
            plan.append("")
        
        if self.pyqt5_files:
            plan.append("📋 PyQt5 files to migrate to PyQt6:")
            for file_path in self.pyqt5_files:
                plan.append(f"   - {file_path}")
            plan.append("")
            
            plan.append("Migration steps for each file:")
            plan.append("1. Replace 'PyQt5' with 'PyQt6' in imports")
            plan.append("2. Update enum access (Qt.AlignCenter → Qt.AlignmentFlag.AlignCenter)")
            plan.append("3. Test functionality")
            plan.append("")
        
        return plan

def check_requirements_consistency():
    """Check if requirements files have consistent PyQt versions"""
    req_files = ['requirements.txt', 'requirements-unified.txt', 'requirements_minimal.txt']
    
    pyqt_versions = {}
    for req_file in req_files:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                content = f.read()
                if 'PyQt5' in content:
                    pyqt_versions[req_file] = 'PyQt5'
                elif 'PyQt6' in content:
                    pyqt_versions[req_file] = 'PyQt6'
    
    if len(set(pyqt_versions.values())) > 1:
        print("🚨 Inconsistent PyQt versions in requirements files:")
        for file, version in pyqt_versions.items():
            print(f"   {file}: {version}")
        return False
    
    return True

def create_pyqt6_migration_patch(file_path: str) -> str:
    """Create a migration patch for a PyQt5 file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Basic migration patterns
    migrations = [
        (r'from PyQt5\.', 'from PyQt6.'),
        (r'import PyQt5', 'import PyQt6'),
        (r'Qt\.AlignCenter', 'Qt.AlignmentFlag.AlignCenter'),
        (r'Qt\.AlignLeft', 'Qt.AlignmentFlag.AlignLeft'),
        (r'Qt\.AlignRight', 'Qt.AlignmentFlag.AlignRight'),
        (r'Qt\.AlignTop', 'Qt.AlignmentFlag.AlignTop'),
        (r'Qt\.AlignBottom', 'Qt.AlignmentFlag.AlignBottom'),
        (r'Qt\.Checked', 'Qt.CheckState.Checked'),
        (r'Qt\.Unchecked', 'Qt.CheckState.Unchecked'),
        (r'Qt\.LeftButton', 'Qt.MouseButton.LeftButton'),
        (r'Qt\.RightButton', 'Qt.MouseButton.RightButton'),
        (r'Qt\.MiddleButton', 'Qt.MouseButton.MiddleButton'),
    ]
    
    migrated_content = content
    for pattern, replacement in migrations:
        migrated_content = re.sub(pattern, replacement, migrated_content)
    
    return migrated_content

def main():
    """Main function to run the PyQt compatibility check"""
    print("🔍 PyQt Compatibility Checker")
    print("=" * 50)
    
    # Check current runtime
    runtime_conflict = PyQtConflictDetector().check_runtime_conflict()
    if runtime_conflict:
        print("\n⚠️  Runtime conflict detected. Restart Python to continue safely.")
        return 1
    
    # Check requirements consistency
    print("\n📋 Checking requirements files...")
    req_consistent = check_requirements_consistency()
    if req_consistent:
        print("✅ Requirements files are consistent")
    
    # Scan codebase
    print("\n🔍 Scanning codebase for PyQt imports...")
    detector = PyQtConflictDetector()
    results = detector.scan_files()
    
    print(f"\n📊 Results:")
    print(f"   PyQt5 files: {len(results['pyqt5_files'])}")
    print(f"   PyQt6 files: {len(results['pyqt6_files'])}")
    print(f"   Mixed files: {len(results['mixed_files'])} ⚠️")
    print(f"   Errors: {len(results['errors'])}")
    
    # Show details
    if results['mixed_files']:
        print(f"\n🚨 CRITICAL: Files with both PyQt5 and PyQt6:")
        for file_path in results['mixed_files']:
            print(f"   - {file_path}")
    
    if results['pyqt5_files']:
        print(f"\n📋 Files using PyQt5 (need migration):")
        for file_path in results['pyqt5_files'][:10]:  # Limit output
            print(f"   - {file_path}")
        if len(results['pyqt5_files']) > 10:
            print(f"   ... and {len(results['pyqt5_files']) - 10} more")
    
    if results['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in results['errors'][:5]:  # Limit output
            print(f"   - {error}")
    
    # Generate migration plan
    plan = detector.generate_migration_plan()
    if plan:
        print(f"\n📋 Migration Plan:")
        for step in plan:
            print(step)
    
    # Summary
    if results['mixed_files'] or results['pyqt5_files']:
        print(f"\n❌ PyQt conflicts detected. Action required.")
        return 1
    else:
        print(f"\n✅ No PyQt conflicts detected. All good!")
        return 0

if __name__ == '__main__':
    sys.exit(main())