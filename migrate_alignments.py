#!/usr/bin/env python3
"""
Qt Alignment Flag Migration Script

This script automatically migrates Qt.AlignmentFlag usage to direct Qt constants
for PyQt5 compatibility. It searches through all Python files in the project
and replaces PyQt6 enum-based alignment flags with PyQt5 direct constants.
"""

import re
import os
import sys
from pathlib import Path

def migrate_alignments_in_file(filepath):
    """Migrate Qt.AlignmentFlag usage to direct Qt constants in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace Qt.AlignmentFlag.AlignX with Qt.AlignX
        content = re.sub(r'Qt\.AlignmentFlag\.Align(\w+)', r'Qt.Align\1', content)
        
        # Replace specific alignment patterns
        alignment_replacements = {
            'Qt.AlignmentFlag.AlignLeft': 'Qt.AlignLeft',
            'Qt.AlignmentFlag.AlignLeading': 'Qt.AlignLeading',
            'Qt.AlignmentFlag.AlignRight': 'Qt.AlignRight',
            'Qt.AlignmentFlag.AlignTrailing': 'Qt.AlignTrailing',
            'Qt.AlignmentFlag.AlignHCenter': 'Qt.AlignHCenter',
            'Qt.AlignmentFlag.AlignJustify': 'Qt.AlignJustify',
            'Qt.AlignmentFlag.AlignAbsolute': 'Qt.AlignAbsolute',
            'Qt.AlignmentFlag.AlignHorizontal_Mask': 'Qt.AlignHorizontal_Mask',
            'Qt.AlignmentFlag.AlignTop': 'Qt.AlignTop',
            'Qt.AlignmentFlag.AlignBottom': 'Qt.AlignBottom',
            'Qt.AlignmentFlag.AlignVCenter': 'Qt.AlignVCenter',
            'Qt.AlignmentFlag.AlignVertical_Mask': 'Qt.AlignVertical_Mask',
            'Qt.AlignmentFlag.AlignCenter': 'Qt.AlignCenter',
            'Qt.AlignmentFlag.AlignBaseline': 'Qt.AlignBaseline',
        }
        
        for old_pattern, new_pattern in alignment_replacements.items():
            content = content.replace(old_pattern, new_pattern)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def migrate_imports_in_file(filepath):
    """Migrate PyQt6 imports to PyQt5 in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace PyQt6 imports with PyQt5
        content = re.sub(r'from PyQt6\.', 'from PyQt5.', content)
        content = re.sub(r'import PyQt6\.', 'import PyQt5.', content)
        
        # Only write if content changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing imports in {filepath}: {e}")
        return False

def should_skip_file(filepath):
    """Check if file should be skipped during migration"""
    skip_patterns = [
        '__pycache__',
        '.git',
        '.venv',
        'venv',
        'env',
        'node_modules',
        '.pytest_cache',
        'migrate_alignments.py',  # Skip this script itself
        'qt_compatibility.py',    # Skip compatibility layer
    ]
    
    filepath_str = str(filepath)
    return any(pattern in filepath_str for pattern in skip_patterns)

def migrate_all_files(dry_run=False):
    """Migrate all Python files in the project"""
    project_root = Path('.')
    migrated_files = []
    import_migrated_files = []
    
    print("Starting Qt migration...")
    print(f"Dry run mode: {dry_run}")
    print("-" * 50)
    
    for filepath in project_root.rglob('*.py'):
        if should_skip_file(filepath):
            continue
            
        try:
            # Migrate imports first
            if not dry_run:
                if migrate_imports_in_file(filepath):
                    import_migrated_files.append(str(filepath))
                    print(f"✓ Migrated imports: {filepath}")
            
            # Then migrate alignments
            if not dry_run:
                if migrate_alignments_in_file(filepath):
                    migrated_files.append(str(filepath))
                    print(f"✓ Migrated alignments: {filepath}")
            else:
                # In dry run mode, just check what would be changed
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for PyQt6 imports
                if 'PyQt6' in content:
                    import_migrated_files.append(str(filepath))
                    print(f"  Would migrate imports: {filepath}")
                
                # Check for alignment flags
                if 'Qt.AlignmentFlag' in content:
                    migrated_files.append(str(filepath))
                    print(f"  Would migrate alignments: {filepath}")
                    
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    
    print("-" * 50)
    print(f"Migration complete!")
    print(f"Files with import changes: {len(import_migrated_files)}")
    print(f"Files with alignment changes: {len(migrated_files)}")
    
    if dry_run:
        print("\nThis was a dry run. No files were actually modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print("\nMigration applied successfully!")
    
    return migrated_files, import_migrated_files

def update_requirements_file():
    """Update requirements file to use PyQt5 instead of PyQt6"""
    requirements_file = 'requirements-unified.txt'
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace PyQt6 with PyQt5
        content = re.sub(
            r'PyQt6>=6\.4\.0,<6\.7\.0',
            'PyQt5>=5.15.0,<5.16.0',
            content
        )
        
        # Update comment
        content = re.sub(
            r'# GUI Framework \(Updated from PyQt5 to PyQt6\)',
            '# GUI Framework (Changed from PyQt6 to PyQt5 for compatibility)',
            content
        )
        
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Updated {requirements_file} to use PyQt5")
        return True
        
    except Exception as e:
        print(f"Error updating requirements file: {e}")
        return False

def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate PyQt6 to PyQt5')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--update-requirements', action='store_true',
                       help='Update requirements file to use PyQt5')
    parser.add_argument('--migrate-imports', action='store_true',
                       help='Migrate PyQt6 imports to PyQt5')
    parser.add_argument('--migrate-alignments', action='store_true',
                       help='Migrate Qt.AlignmentFlag to direct constants')
    
    args = parser.parse_args()
    
    # Default behavior: do everything
    if not any([args.update_requirements, args.migrate_imports, args.migrate_alignments]):
        args.update_requirements = True
        args.migrate_imports = True
        args.migrate_alignments = True
    
    print("PyQt6 to PyQt5 Migration Tool")
    print("=" * 40)
    
    if args.update_requirements:
        update_requirements_file()
    
    if args.migrate_imports or args.migrate_alignments:
        migrate_all_files(dry_run=args.dry_run)
    
    print("\nMigration completed successfully!")
    print("\nNext steps:")
    print("1. Install PyQt5: pip install PyQt5>=5.15.0")
    print("2. Test the application")
    print("3. Run unit tests to verify functionality")
    print("4. Check for any remaining PyQt6 references")

if __name__ == '__main__':
    main()