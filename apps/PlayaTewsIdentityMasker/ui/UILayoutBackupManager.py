#!/usr/bin/env python3
"""
UI Layout Backup Manager for PlayaTewsIdentityMasker
Provides comprehensive backup and restore functionality for UI layouts
"""

import json
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pickle
import hashlib

from xlib import qt as qtx
from xlib.db import KeyValueDB
from localization import L


@dataclass
class WidgetState:
    """Represents the state of a UI widget"""
    name: str
    class_name: str
    geometry: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    visible: bool = True
    enabled: bool = True
    custom_data: Dict[str, Any] = None
    parent_name: Optional[str] = None
    children: List[str] = None


@dataclass
class LayoutState:
    """Represents the complete layout state"""
    timestamp: str
    version: str = "1.0"
    window_geometry: Optional[Tuple[int, int, int, int]] = None
    window_state: Optional[str] = None  # normal, maximized, minimized, fullscreen
    widgets: Dict[str, WidgetState] = None
    layout_config: Dict[str, Any] = None
    custom_settings: Dict[str, Any] = None
    checksum: Optional[str] = None


class UILayoutBackupManager:
    """Manages UI layout backup and restore operations"""
    
    def __init__(self, settings_dirpath: Path, userdata_path: Path):
        self.settings_dirpath = settings_dirpath
        self.userdata_path = userdata_path
        self.backup_dir = userdata_path / 'ui_backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.current_layout_state: Optional[LayoutState] = None
        
        # Initialize backup database
        self.backup_db = KeyValueDB(self.backup_dir / 'backup_metadata.dat')
        
        # Maximum number of backups to keep
        self.max_backups = 10
        
        self.logger.info(f"UI Layout Backup Manager initialized at {self.backup_dir}")
    
    def create_backup(self, name: str = None, description: str = "") -> Optional[str]:
        """Create a backup of the current UI layout"""
        try:
            if name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"layout_backup_{timestamp}"
            
            self.logger.info(f"Creating UI layout backup: {name}")
            
            # Capture current layout state
            layout_state = self._capture_current_layout()
            if layout_state is None:
                self.logger.error("Failed to capture current layout state")
                return None
            
            # Add metadata
            layout_state.timestamp = datetime.now().isoformat()
            layout_state.custom_settings = {
                'description': description,
                'backup_name': name,
                'app_version': self._get_app_version()
            }
            
            # Calculate checksum
            layout_state.checksum = self._calculate_checksum(layout_state)
            
            # Save backup
            backup_path = self.backup_dir / f"{name}.json"
            self._save_layout_state(layout_state, backup_path)
            
            # Update backup metadata
            self._update_backup_metadata(name, layout_state, backup_path)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            self.logger.info(f"UI layout backup created successfully: {backup_path}")
            return name
            
        except Exception as e:
            self.logger.error(f"Failed to create UI layout backup: {e}")
            return None
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore a UI layout from backup"""
        try:
            self.logger.info(f"Restoring UI layout from backup: {backup_name}")
            
            # Load backup
            backup_path = self.backup_dir / f"{backup_name}.json"
            if not backup_path.exists():
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
            
            layout_state = self._load_layout_state(backup_path)
            if layout_state is None:
                self.logger.error("Failed to load layout state from backup")
                return False
            
            # Verify checksum
            if not self._verify_checksum(layout_state):
                self.logger.warning("Backup checksum verification failed - backup may be corrupted")
            
            # Apply layout state
            success = self._apply_layout_state(layout_state)
            
            if success:
                self.logger.info(f"UI layout restored successfully from backup: {backup_name}")
                # Update current state
                self.current_layout_state = layout_state
            else:
                self.logger.error("Failed to apply layout state")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to restore UI layout backup: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("*.json"):
                backup_name = backup_file.stem
                metadata = self.backup_db.get_value(f"backup_{backup_name}", {})
                
                backup_info = {
                    'name': backup_name,
                    'file_path': str(backup_file),
                    'timestamp': metadata.get('timestamp', 'Unknown'),
                    'description': metadata.get('description', ''),
                    'widget_count': metadata.get('widget_count', 0),
                    'file_size': backup_file.stat().st_size if backup_file.exists() else 0
                }
                backups.append(backup_info)
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []
    
    def delete_backup(self, backup_name: str) -> bool:
        """Delete a backup"""
        try:
            backup_path = self.backup_dir / f"{backup_name}.json"
            if backup_path.exists():
                backup_path.unlink()
                self.backup_db.set_value(f"backup_{backup_name}", None)
                self.logger.info(f"Deleted backup: {backup_name}")
                return True
            else:
                self.logger.warning(f"Backup not found: {backup_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_name}: {e}")
            return False
    
    def export_backup(self, backup_name: str, export_path: Path) -> bool:
        """Export a backup to a different location"""
        try:
            backup_path = self.backup_dir / f"{backup_name}.json"
            if not backup_path.exists():
                self.logger.error(f"Backup not found: {backup_name}")
                return False
            
            shutil.copy2(backup_path, export_path)
            self.logger.info(f"Exported backup {backup_name} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export backup {backup_name}: {e}")
            return False
    
    def import_backup(self, import_path: Path, name: str = None) -> Optional[str]:
        """Import a backup from a file"""
        try:
            if name is None:
                name = import_path.stem
            
            # Validate the backup file
            layout_state = self._load_layout_state(import_path)
            if layout_state is None:
                self.logger.error("Invalid backup file")
                return None
            
            # Copy to backup directory
            backup_path = self.backup_dir / f"{name}.json"
            shutil.copy2(import_path, backup_path)
            
            # Update metadata
            self._update_backup_metadata(name, layout_state, backup_path)
            
            self.logger.info(f"Imported backup: {name}")
            return name
            
        except Exception as e:
            self.logger.error(f"Failed to import backup: {e}")
            return None
    
    def _capture_current_layout(self) -> Optional[LayoutState]:
        """Capture the current UI layout state"""
        try:
            app = qtx.QXMainApplication.get_singleton()
            if app is None:
                self.logger.error("No QXMainApplication instance found")
                return None
            
            # Find the main window
            main_window = None
            for widget in app.topLevelWidgets():
                if hasattr(widget, '_QXW') and widget._QXW:
                    main_window = widget
                    break
            
            if main_window is None:
                self.logger.error("No main window found")
                return None
            
            layout_state = LayoutState(
                widgets={},
                layout_config={},
                custom_settings={}
            )
            
            # Capture window state
            layout_state.window_geometry = (
                main_window.pos().x(),
                main_window.pos().y(),
                main_window.size().width(),
                main_window.size().height()
            )
            
            if main_window.isMaximized():
                layout_state.window_state = "maximized"
            elif main_window.isMinimized():
                layout_state.window_state = "minimized"
            elif main_window.isFullScreen():
                layout_state.window_state = "fullscreen"
            else:
                layout_state.window_state = "normal"
            
            # Capture all widgets recursively
            self._capture_widget_tree(main_window, layout_state.widgets)
            
            # Capture layout configuration
            layout_state.layout_config = self._capture_layout_config(main_window)
            
            return layout_state
            
        except Exception as e:
            self.logger.error(f"Failed to capture current layout: {e}")
            return None
    
    def _capture_widget_tree(self, widget: qtx.QXWidget, widgets_dict: Dict[str, WidgetState], parent_name: str = None):
        """Recursively capture widget tree state"""
        try:
            widget_name = widget.get_name_id() if hasattr(widget, 'get_name_id') else widget.objectName()
            if not widget_name:
                widget_name = f"{widget.__class__.__name__}_{id(widget)}"
            
            # Capture widget state
            widget_state = WidgetState(
                name=widget_name,
                class_name=widget.__class__.__name__,
                geometry=(
                    widget.pos().x(),
                    widget.pos().y(),
                    widget.size().width(),
                    widget.size().height()
                ),
                visible=widget.isVisible(),
                enabled=widget.isEnabled(),
                custom_data={},
                parent_name=parent_name,
                children=[]
            )
            
            # Capture custom data for specific widget types
            self._capture_widget_custom_data(widget, widget_state.custom_data)
            
            # Capture children
            for child in widget.children():
                if isinstance(child, qtx.QXWidget):
                    child_name = self._capture_widget_tree(child, widgets_dict, widget_name)
                    if child_name:
                        widget_state.children.append(child_name)
            
            widgets_dict[widget_name] = widget_state
            return widget_name
            
        except Exception as e:
            self.logger.error(f"Failed to capture widget {widget}: {e}")
            return None
    
    def _capture_widget_custom_data(self, widget: qtx.QXWidget, custom_data: Dict[str, Any]):
        """Capture custom data for specific widget types"""
        try:
            # Capture widget-specific data
            if hasattr(widget, 'get_widget_data'):
                # Try to capture common widget data
                common_keys = ['value', 'text', 'checked', 'current_index', 'slider_position']
                for key in common_keys:
                    value = widget.get_widget_data(key)
                    if value is not None:
                        custom_data[key] = value
            
            # Capture specific widget type data
            if isinstance(widget, qtx.QXSaveableComboBox):
                custom_data['current_choice'] = widget.currentText()
                custom_data['current_index'] = widget.currentIndex()
            
            # Add more widget-specific captures as needed
            
        except Exception as e:
            self.logger.debug(f"Failed to capture custom data for widget {widget}: {e}")
    
    def _capture_layout_config(self, main_window: qtx.QXWindow) -> Dict[str, Any]:
        """Capture layout configuration"""
        try:
            config = {
                'window_title': main_window.windowTitle(),
                'window_icon': None,  # Could capture icon if needed
                'style_sheet': main_window.styleSheet(),
                'layout_type': 'QVBoxLayout' if hasattr(main_window, 'content_l') else 'Unknown'
            }
            
            # Capture specific layout information
            if hasattr(main_window, 'content_l'):
                config['content_layout'] = {
                    'spacing': main_window.content_l.spacing(),
                    'contents_margins': main_window.content_l.contentsMargins().getRect()
                }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to capture layout config: {e}")
            return {}
    
    def _apply_layout_state(self, layout_state: LayoutState) -> bool:
        """Apply a layout state to the current UI"""
        try:
            app = qtx.QXMainApplication.get_singleton()
            if app is None:
                return False
            
            # Find the main window
            main_window = None
            for widget in app.topLevelWidgets():
                if hasattr(widget, '_QXW') and widget._QXW:
                    main_window = widget
                    break
            
            if main_window is None:
                return False
            
            # Apply window state
            if layout_state.window_geometry:
                x, y, width, height = layout_state.window_geometry
                main_window.move(x, y)
                main_window.resize(width, height)
            
            if layout_state.window_state:
                if layout_state.window_state == "maximized":
                    main_window.showMaximized()
                elif layout_state.window_state == "minimized":
                    main_window.showMinimized()
                elif layout_state.window_state == "fullscreen":
                    main_window.showFullScreen()
                else:
                    main_window.showNormal()
            
            # Apply widget states
            for widget_name, widget_state in layout_state.widgets.items():
                self._apply_widget_state(main_window, widget_state)
            
            # Apply layout configuration
            self._apply_layout_config(main_window, layout_state.layout_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply layout state: {e}")
            return False
    
    def _apply_widget_state(self, main_window: qtx.QXWindow, widget_state: WidgetState):
        """Apply state to a specific widget"""
        try:
            # Find the widget
            widget = self._find_widget_by_name(main_window, widget_state.name)
            if widget is None:
                self.logger.debug(f"Widget not found: {widget_state.name}")
                return
            
            # Apply basic properties
            if widget_state.geometry:
                x, y, width, height = widget_state.geometry
                widget.move(x, y)
                widget.resize(width, height)
            
            widget.setVisible(widget_state.visible)
            widget.setEnabled(widget_state.enabled)
            
            # Apply custom data
            self._apply_widget_custom_data(widget, widget_state.custom_data)
            
        except Exception as e:
            self.logger.error(f"Failed to apply state to widget {widget_state.name}: {e}")
    
    def _find_widget_by_name(self, parent_widget: qtx.QXWidget, widget_name: str) -> Optional[qtx.QXWidget]:
        """Find a widget by name in the widget tree"""
        try:
            # Check if this is the widget we're looking for
            current_name = parent_widget.get_name_id() if hasattr(parent_widget, 'get_name_id') else parent_widget.objectName()
            if not current_name:
                current_name = f"{parent_widget.__class__.__name__}_{id(parent_widget)}"
            
            if current_name == widget_name:
                return parent_widget
            
            # Search children
            for child in parent_widget.children():
                if isinstance(child, qtx.QXWidget):
                    result = self._find_widget_by_name(child, widget_name)
                    if result:
                        return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find widget {widget_name}: {e}")
            return None
    
    def _apply_widget_custom_data(self, widget: qtx.QXWidget, custom_data: Dict[str, Any]):
        """Apply custom data to a widget"""
        try:
            for key, value in custom_data.items():
                if hasattr(widget, 'set_widget_data'):
                    widget.set_widget_data(key, value)
                
                # Apply specific widget type data
                if isinstance(widget, qtx.QXSaveableComboBox) and key == 'current_index':
                    widget.setCurrentIndex(value)
                
                # Add more widget-specific applications as needed
                
        except Exception as e:
            self.logger.debug(f"Failed to apply custom data to widget {widget}: {e}")
    
    def _apply_layout_config(self, main_window: qtx.QXWindow, config: Dict[str, Any]):
        """Apply layout configuration"""
        try:
            if 'window_title' in config:
                main_window.setWindowTitle(config['window_title'])
            
            if 'style_sheet' in config:
                main_window.setStyleSheet(config['style_sheet'])
            
            # Apply specific layout configurations as needed
            
        except Exception as e:
            self.logger.error(f"Failed to apply layout config: {e}")
    
    def _save_layout_state(self, layout_state: LayoutState, file_path: Path):
        """Save layout state to file"""
        try:
            # Convert to dict for JSON serialization
            state_dict = asdict(layout_state)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save layout state: {e}")
            raise
    
    def _load_layout_state(self, file_path: Path) -> Optional[LayoutState]:
        """Load layout state from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)
            
            # Convert back to LayoutState
            widgets_dict = {}
            for name, widget_data in state_dict.get('widgets', {}).items():
                widget_state = WidgetState(**widget_data)
                widgets_dict[name] = widget_state
            
            layout_state = LayoutState(
                timestamp=state_dict.get('timestamp', ''),
                version=state_dict.get('version', '1.0'),
                window_geometry=tuple(state_dict.get('window_geometry', [])) if state_dict.get('window_geometry') else None,
                window_state=state_dict.get('window_state'),
                widgets=widgets_dict,
                layout_config=state_dict.get('layout_config', {}),
                custom_settings=state_dict.get('custom_settings', {}),
                checksum=state_dict.get('checksum')
            )
            
            return layout_state
            
        except Exception as e:
            self.logger.error(f"Failed to load layout state: {e}")
            return None
    
    def _update_backup_metadata(self, backup_name: str, layout_state: LayoutState, backup_path: Path):
        """Update backup metadata"""
        try:
            metadata = {
                'timestamp': layout_state.timestamp,
                'description': layout_state.custom_settings.get('description', ''),
                'widget_count': len(layout_state.widgets),
                'file_size': backup_path.stat().st_size if backup_path.exists() else 0,
                'version': layout_state.version,
                'checksum': layout_state.checksum
            }
            
            self.backup_db.set_value(f"backup_{backup_name}", metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to update backup metadata: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backups if we exceed the maximum count"""
        try:
            backups = self.list_backups()
            if len(backups) > self.max_backups:
                # Remove oldest backups
                backups_to_remove = backups[self.max_backups:]
                for backup in backups_to_remove:
                    self.delete_backup(backup['name'])
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def _calculate_checksum(self, layout_state: LayoutState) -> str:
        """Calculate checksum for layout state"""
        try:
            # Create a string representation for hashing
            state_str = f"{layout_state.timestamp}{layout_state.version}{str(layout_state.widgets)}"
            return hashlib.md5(state_str.encode()).hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum: {e}")
            return ""
    
    def _verify_checksum(self, layout_state: LayoutState) -> bool:
        """Verify checksum of layout state"""
        try:
            if not layout_state.checksum:
                return True  # No checksum to verify
            
            calculated_checksum = self._calculate_checksum(layout_state)
            return calculated_checksum == layout_state.checksum
            
        except Exception as e:
            self.logger.error(f"Failed to verify checksum: {e}")
            return False
    
    def _get_app_version(self) -> str:
        """Get application version"""
        try:
            # This could be enhanced to get actual app version
            return "1.0.0"
        except Exception:
            return "Unknown" 