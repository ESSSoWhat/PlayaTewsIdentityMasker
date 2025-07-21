# UI Layout Backup System

## Overview

The UI Layout Backup System for PlayaTewsIdentityMasker provides comprehensive backup and restore functionality for your UI layouts. This system allows you to save your current UI configuration and restore it later, preventing the need to rebuild your layout from scratch.

## Features

### 🔄 **Automatic Backup Points**
- Create backup points at any time with custom names and descriptions
- Automatic timestamp-based naming for quick backups
- Backup metadata tracking (creation time, widget count, file size)

### 📦 **Complete Layout Capture**
- Window position and size
- Widget positions, sizes, and visibility states
- Custom widget data and configurations
- Layout hierarchy and relationships
- Application settings and preferences

### 🔧 **Easy Management**
- User-friendly backup manager dialog
- List, restore, delete, and export backups
- Backup validation and integrity checking
- Automatic cleanup of old backups

### 📤 **Import/Export**
- Export backups to share with others
- Import backups from other installations
- Cross-platform compatibility

## How to Use

### Quick Backup
1. **From the Menu**: Go to `File` → `Backup UI Layout`
   - Creates an automatic backup with timestamp
   - No user input required

### Manual Backup
1. **From the Menu**: Go to `File` → `Manage Layout Backups`
2. **Enter Details**:
   - **Backup Name**: Optional custom name (auto-generated if empty)
   - **Description**: Optional description for the backup
3. **Click "Create Backup"**

### Restore Layout
1. **From the Menu**: Go to `File` → `Restore UI Layout` or `Manage Layout Backups`
2. **Select Backup**: Choose from the list of available backups
3. **Confirm**: Click "Restore Selected" and confirm the action

### Manage Backups
1. **From the Menu**: Go to `File` → `Manage Layout Backups`
2. **Available Actions**:
   - **Create New Backup**: Create a new backup with custom details
   - **Restore Selected**: Restore the selected backup
   - **Delete Selected**: Remove the selected backup
   - **Export Selected**: Save backup to a different location
   - **Refresh List**: Update the backup list

## File Structure

### Backup Storage
Backups are stored in the `userdata/ui_backups/` directory:
```
userdata/
└── ui_backups/
    ├── backup_metadata.dat          # Backup metadata database
    ├── layout_backup_20250101_120000.json
    ├── my_custom_layout.json
    └── auto_backup_20250101_130000.json
```

### Backup File Format
Each backup is stored as a JSON file containing:
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "version": "1.0",
  "window_geometry": [100, 100, 1200, 800],
  "window_state": "normal",
  "widgets": {
    "widget_name": {
      "name": "widget_name",
      "class_name": "QXWidget",
      "geometry": [0, 0, 100, 50],
      "visible": true,
      "enabled": true,
      "custom_data": {},
      "parent_name": "parent_widget",
      "children": []
    }
  },
  "layout_config": {
    "window_title": "PlayaTewsIdentityMasker",
    "style_sheet": "",
    "layout_type": "QVBoxLayout"
  },
  "custom_settings": {
    "description": "My custom layout",
    "backup_name": "my_custom_layout",
    "app_version": "1.0.0"
  },
  "checksum": "md5_hash_for_integrity"
}
```

## Technical Details

### Backup Manager Class
The core functionality is provided by `UILayoutBackupManager`:
- **Location**: `apps/PlayaTewsIdentityMasker/ui/UILayoutBackupManager.py`
- **Features**: Complete backup/restore operations, metadata management, integrity checking

### UI Components
- **QBackupManagerUI**: Main backup management interface
- **QBackupManagerDialog**: Modal dialog for backup operations
- **Integration**: Seamlessly integrated into the main application menu

### Data Capture
The system captures:
- **Widget States**: Position, size, visibility, enabled state
- **Custom Data**: Widget-specific settings and configurations
- **Layout Hierarchy**: Parent-child relationships between widgets
- **Window State**: Position, size, maximized/minimized state
- **Application Settings**: Style sheets, window properties

### Safety Features
- **Checksum Validation**: Ensures backup integrity
- **Error Handling**: Graceful handling of backup/restore failures
- **Automatic Cleanup**: Removes old backups to prevent disk space issues
- **Confirmation Dialogs**: Prevents accidental data loss

## Configuration

### Backup Settings
- **Maximum Backups**: Default 10 backups (configurable)
- **Backup Directory**: `userdata/ui_backups/`
- **File Format**: JSON with metadata
- **Compression**: Not currently implemented (future enhancement)

### Customization
You can modify the backup behavior by editing:
- `UILayoutBackupManager.max_backups`: Maximum number of backups to keep
- `UILayoutBackupManager.backup_dir`: Backup storage location
- Widget capture logic in `_capture_widget_custom_data()`

## Troubleshooting

### Common Issues

**Backup Creation Fails**
- Check disk space in the backup directory
- Verify write permissions to `userdata/ui_backups/`
- Check application logs for detailed error messages

**Restore Doesn't Work**
- Verify backup file integrity (checksum validation)
- Check if widgets have changed since backup creation
- Try restoring to a fresh application instance

**Missing Widgets After Restore**
- Some widgets may not be available in the current application state
- Check application logs for widget restoration errors
- Consider creating a new backup after application updates

### Logging
The backup system uses Python's logging module:
```python
import logging
logging.getLogger('apps.PlayaTewsIdentityMasker.ui.UILayoutBackupManager').setLevel(logging.DEBUG)
```

## Testing

Run the test script to verify the backup system:
```bash
python scripts/test_ui_backup.py
```

This will test:
- Backup creation and restoration
- File structure validation
- Import/export functionality
- Metadata management

## Future Enhancements

### Planned Features
- **Backup Compression**: Reduce backup file sizes
- **Incremental Backups**: Only save changes since last backup
- **Cloud Sync**: Automatic backup to cloud storage
- **Backup Scheduling**: Automatic backups at regular intervals
- **Backup Encryption**: Secure sensitive layout data
- **Backup Templates**: Pre-configured layout templates

### API Extensions
- **Plugin System**: Allow third-party backup extensions
- **Custom Widget Support**: Enhanced capture for custom widgets
- **Backup Validation**: More comprehensive integrity checking
- **Performance Optimization**: Faster backup/restore operations

## Support

If you encounter issues with the backup system:
1. Check the application logs for error messages
2. Verify backup file integrity using the test script
3. Try creating a fresh backup to isolate the issue
4. Report bugs with detailed error information and backup files

## Contributing

To contribute to the backup system:
1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure backward compatibility with existing backups 