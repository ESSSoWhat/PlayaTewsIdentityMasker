#!/usr/bin/env python3
"""
Migration script for existing UI settings to enhanced UI
Helps users transition from old UI to new enhanced UI settings
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

def backup_existing_settings(settings_path):
    """Create backup of existing settings"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = settings_path / f"backup_before_enhanced_ui_{timestamp}"
    backup_path.mkdir(exist_ok=True)
    
    backed_up_files = []
    
    # Backup all existing settings files
    for file in settings_path.glob('*'):
        if file.is_file() and file.name != 'enhanced_ui_settings.json':
            try:
                shutil.copy2(file, backup_path / file.name)
                backed_up_files.append(file.name)
            except Exception as e:
                print(f"⚠️ Could not backup {file.name}: {e}")
    
    if backed_up_files:
        print(f"✅ Backed up {len(backed_up_files)} files to {backup_path}")
        print(f"   Files: {', '.join(backed_up_files)}")
    else:
        print("ℹ️ No existing settings files found to backup")
    
    return backup_path

def parse_old_settings(settings_path):
    """Parse existing settings files to extract relevant information"""
    migrated_data = {}
    
    # Try to read app.dat (common settings file)
    app_dat_path = settings_path / 'app.dat'
    if app_dat_path.exists():
        try:
            with open(app_dat_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                migrated_data['source_file'] = 'app.dat'
                
                # Extract video-related settings
                if 'video' in content.lower():
                    migrated_data['video_fit_mode'] = 'Fit'  # Default to Fit if video settings found
                
                # Extract window size information
                if 'window' in content.lower() or 'size' in content.lower():
                    migrated_data['window_size'] = [1400, 900]  # Default size
                
                # Extract theme information
                if 'dark' in content.lower():
                    migrated_data['theme'] = 'dark'
                elif 'light' in content.lower():
                    migrated_data['theme'] = 'light'
                
                print(f"✅ Parsed settings from {app_dat_path}")
                
        except Exception as e:
            print(f"⚠️ Could not parse {app_dat_path}: {e}")
    
    # Try to read states.dat (state information)
    states_dat_path = settings_path / 'states.dat'
    if states_dat_path.exists():
        try:
            with open(states_dat_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract state information
                if 'fullscreen' in content.lower():
                    migrated_data['fullscreen'] = True
                
                if 'streaming' in content.lower():
                    migrated_data['streaming_enabled'] = True
                
                print(f"✅ Parsed state information from {states_dat_path}")
                
        except Exception as e:
            print(f"⚠️ Could not parse {states_dat_path}: {e}")
    
    # Try to read global_face_swap_state.json
    face_swap_path = settings_path / 'global_face_swap_state.json'
    if face_swap_path.exists():
        try:
            with open(face_swap_path, 'r') as f:
                face_swap_data = json.load(f)
                
                # Extract face swap settings
                if 'enabled' in face_swap_data:
                    migrated_data['face_swap_enabled'] = face_swap_data['enabled']
                
                if 'quality' in face_swap_data:
                    migrated_data['face_swap_quality'] = face_swap_data['quality']
                
                print(f"✅ Parsed face swap settings from {face_swap_path}")
                
        except Exception as e:
            print(f"⚠️ Could not parse {face_swap_path}: {e}")
    
    return migrated_data

def create_enhanced_settings(migrated_data):
    """Create enhanced UI settings based on migrated data"""
    
    # Default enhanced UI settings
    enhanced_settings = {
        'ui': {
            'video_fit_mode': migrated_data.get('video_fit_mode', 'Stretch'),
            'panel_sizes': [300, 800, 300],
            'theme': migrated_data.get('theme', 'dark'),
            'window_size': migrated_data.get('window_size', [1400, 900]),
            'fullscreen': migrated_data.get('fullscreen', False)
        },
        'accessibility': {
            'keyboard_shortcuts': True,
            'high_contrast': False,
            'screen_reader': False,
            'large_text': False
        },
        'performance': {
            'target_fps': 30,
            'memory_limit_gb': 4,
            'gpu_acceleration': True,
            'video_quality': 'HD',
            'optimize_for_speed': False
        },
        'features': {
            'responsive_layout': True,
            'hover_effects': True,
            'animations': True,
            'performance_monitoring': True
        },
        'migration': {
            'migrated_from_old_ui': True,
            'migration_date': datetime.now().isoformat(),
            'source_files': migrated_data.get('source_file', 'unknown'),
            'migrated_data': migrated_data
        }
    }
    
    # Apply face swap settings if available
    if 'face_swap_enabled' in migrated_data:
        enhanced_settings['features']['face_swap_enabled'] = migrated_data['face_swap_enabled']
    
    if 'face_swap_quality' in migrated_data:
        enhanced_settings['performance']['face_swap_quality'] = migrated_data['face_swap_quality']
    
    # Apply streaming settings if available
    if 'streaming_enabled' in migrated_data:
        enhanced_settings['features']['streaming_enabled'] = migrated_data['streaming_enabled']
    
    return enhanced_settings

def save_enhanced_settings(settings_path, enhanced_settings):
    """Save enhanced UI settings to file"""
    enhanced_settings_file = settings_path / 'enhanced_ui_settings.json'
    
    try:
        with open(enhanced_settings_file, 'w') as f:
            json.dump(enhanced_settings, f, indent=2)
        
        print(f"✅ Enhanced UI settings saved to {enhanced_settings_file}")
        return enhanced_settings_file
        
    except Exception as e:
        print(f"❌ Could not save enhanced settings: {e}")
        return None

def show_migration_summary(migrated_data, enhanced_settings_file):
    """Show summary of migration results"""
    print("\n" + "=" * 60)
    print("📋 Migration Summary")
    print("=" * 60)
    
    print(f"✅ Migration completed successfully!")
    print(f"📁 Enhanced settings saved to: {enhanced_settings_file}")
    
    if migrated_data:
        print(f"\n🔄 Migrated settings:")
        for key, value in migrated_data.items():
            if key != 'source_file':
                print(f"   • {key}: {value}")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Launch enhanced UI: python launch_enhanced_ui.py")
    print(f"   2. Test features: python integration_test.py")
    print(f"   3. Review settings: {enhanced_settings_file}")
    print(f"   4. Customize as needed")
    
    print(f"\n📚 For more information:")
    print(f"   • UI_INTEGRATION_GUIDE.md - Complete integration guide")
    print(f"   • UI_UX_IMPROVEMENTS_SUMMARY.md - Feature overview")

def migrate_existing_settings():
    """Main migration function"""
    print("🔄 PlayaTews Identity Masker - UI Settings Migration")
    print("=" * 60)
    
    # Setup paths
    settings_path = Path('./settings')
    settings_path.mkdir(exist_ok=True)
    
    print(f"📁 Settings directory: {settings_path.absolute()}")
    
    # Check if enhanced settings already exist
    enhanced_settings_file = settings_path / 'enhanced_ui_settings.json'
    if enhanced_settings_file.exists():
        print(f"⚠️ Enhanced UI settings already exist: {enhanced_settings_file}")
        response = input("Do you want to overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Migration cancelled.")
            return 0
    
    # Backup existing settings
    backup_path = backup_existing_settings(settings_path)
    
    # Parse existing settings
    print("\n🔍 Parsing existing settings...")
    migrated_data = parse_old_settings(settings_path)
    
    if not migrated_data:
        print("ℹ️ No existing settings found to migrate")
        migrated_data = {}
    
    # Create enhanced settings
    print("\n⚙️ Creating enhanced UI settings...")
    enhanced_settings = create_enhanced_settings(migrated_data)
    
    # Save enhanced settings
    enhanced_settings_file = save_enhanced_settings(settings_path, enhanced_settings)
    
    if enhanced_settings_file:
        # Show migration summary
        show_migration_summary(migrated_data, enhanced_settings_file)
        return 0
    else:
        print("❌ Migration failed - could not save enhanced settings")
        return 1

def show_help():
    """Show help information"""
    help_text = """
    PlayaTews Identity Masker - UI Settings Migration
    
    This script migrates existing UI settings to the new enhanced UI format.
    
    Usage:
        python migrate_ui_settings.py          # Run migration
        python migrate_ui_settings.py --help   # Show this help
    
    What it does:
        • Creates backup of existing settings
        • Parses existing settings files (app.dat, states.dat, etc.)
        • Extracts relevant configuration data
        • Creates new enhanced UI settings format
        • Preserves user preferences where possible
    
    Files processed:
        • app.dat - Main application settings
        • states.dat - Application state information
        • global_face_swap_state.json - Face swap settings
        • Other settings files in ./settings/
    
    Output:
        • enhanced_ui_settings.json - New enhanced UI settings
        • backup_before_enhanced_ui_YYYYMMDD_HHMMSS/ - Backup of old settings
    
    Safety:
        • Always creates backup before modifying settings
        • Preserves all existing files
        • Can be run multiple times safely
    
    After migration:
        • Launch enhanced UI: python launch_enhanced_ui.py
        • Test features: python integration_test.py
        • Review and customize settings as needed
    """
    
    print(help_text)

def main():
    """Main function"""
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            return 0
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            return 1
    
    # Run migration
    return migrate_existing_settings()

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Migration cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1) 