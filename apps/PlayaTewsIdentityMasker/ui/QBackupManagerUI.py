#!/usr/bin/env python3
"""
UI Component for Layout Backup Manager
Provides a user-friendly interface for managing UI layout backups
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from xlib import qt as qtx
from localization import L

from .UILayoutBackupManager import UILayoutBackupManager


class QBackupManagerUI(qtx.QXWidget):
    """UI component for managing UI layout backups"""
    
    def __init__(self, backup_manager: UILayoutBackupManager):
        super().__init__()
        
        self.backup_manager = backup_manager
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._refresh_backup_list()
    
    def _setup_ui(self):
        """Setup the UI components"""
        # Main layout
        main_layout = qtx.QXVBoxLayout()
        
        # Title
        title_label = qtx.QXLabel(text="UI Layout Backup Manager", font=qtx.QXFontDB.get_default_font(size=14, bold=True))
        main_layout.addWidget(title_label)
        
        # Create backup section
        create_backup_group = self._create_backup_section()
        main_layout.addWidget(create_backup_group)
        
        # Backup list section
        backup_list_group = self._create_backup_list_section()
        main_layout.addWidget(backup_list_group)
        
        # Actions section
        actions_group = self._create_actions_section()
        main_layout.addWidget(actions_group)
        
        # Status section
        status_group = self._create_status_section()
        main_layout.addWidget(status_group)
        
        self.setLayout(main_layout)
    
    def _create_backup_section(self) -> qtx.QXWidget:
        """Create the backup creation section"""
        group = qtx.QXGroupBox(title="Create New Backup")
        layout = qtx.QXVBoxLayout()
        
        # Backup name input
        name_layout = qtx.QXHBoxLayout()
        name_layout.addWidget(qtx.QXLabel(text="Backup Name:"))
        self.backup_name_edit = qtx.QXLineEdit(placeholder_text="Enter backup name (optional)")
        name_layout.addWidget(self.backup_name_edit)
        layout.addLayout(name_layout)
        
        # Description input
        desc_layout = qtx.QXHBoxLayout()
        desc_layout.addWidget(qtx.QXLabel(text="Description:"))
        self.backup_desc_edit = qtx.QXLineEdit(placeholder_text="Enter description (optional)")
        desc_layout.addWidget(self.backup_desc_edit)
        layout.addLayout(desc_layout)
        
        # Create button
        self.create_backup_btn = qtx.QXPushButton(text="Create Backup", on_clicked=self._on_create_backup)
        layout.addWidget(self.create_backup_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_backup_list_section(self) -> qtx.QXWidget:
        """Create the backup list section"""
        group = qtx.QXGroupBox(title="Available Backups")
        layout = qtx.QXVBoxLayout()
        
        # Backup list
        self.backup_list = qtx.QXListWidget(on_item_selection_changed=self._on_backup_selected)
        layout.addWidget(self.backup_list)
        
        # Refresh button
        refresh_btn = qtx.QXPushButton(text="Refresh List", on_clicked=self._refresh_backup_list)
        layout.addWidget(refresh_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_actions_section(self) -> qtx.QXWidget:
        """Create the actions section"""
        group = qtx.QXGroupBox(title="Backup Actions")
        layout = qtx.QXHBoxLayout()
        
        # Restore button
        self.restore_btn = qtx.QXPushButton(text="Restore Selected", on_clicked=self._on_restore_backup)
        self.restore_btn.setEnabled(False)
        layout.addWidget(self.restore_btn)
        
        # Delete button
        self.delete_btn = qtx.QXPushButton(text="Delete Selected", on_clicked=self._on_delete_backup)
        self.delete_btn.setEnabled(False)
        layout.addWidget(self.delete_btn)
        
        # Export button
        self.export_btn = qtx.QXPushButton(text="Export Selected", on_clicked=self._on_export_backup)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_status_section(self) -> qtx.QXWidget:
        """Create the status section"""
        group = qtx.QXGroupBox(title="Status")
        layout = qtx.QXVBoxLayout()
        
        # Status label
        self.status_label = qtx.QXLabel(text="Ready")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = qtx.QXProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        group.setLayout(layout)
        return group
    
    def _refresh_backup_list(self):
        """Refresh the backup list"""
        try:
            self.backup_list.clear()
            backups = self.backup_manager.list_backups()
            
            for backup in backups:
                # Create display text
                timestamp = backup.get('timestamp', 'Unknown')
                description = backup.get('description', '')
                widget_count = backup.get('widget_count', 0)
                
                display_text = f"{backup['name']} - {timestamp}"
                if description:
                    display_text += f" ({description})"
                display_text += f" - {widget_count} widgets"
                
                # Create list item
                item = qtx.QXListWidgetItem(text=display_text)
                item.setData(qtx.Qt.UserRole, backup)
                self.backup_list.addItem(item)
            
            self._update_status(f"Found {len(backups)} backups")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh backup list: {e}")
            self._update_status(f"Error refreshing list: {e}", error=True)
    
    def _on_backup_selected(self, current_item: qtx.QXListWidgetItem, previous_item: qtx.QXListWidgetItem):
        """Handle backup selection"""
        has_selection = current_item is not None
        self.restore_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        
        if has_selection:
            backup_data = current_item.data(qtx.Qt.UserRole)
            self._update_status(f"Selected: {backup_data['name']}")
    
    def _on_create_backup(self):
        """Handle backup creation"""
        try:
            self.create_backup_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # Get backup details
            name = self.backup_name_edit.text().strip() or None
            description = self.backup_desc_edit.text().strip()
            
            self._update_status("Creating backup...")
            self.progress_bar.setValue(25)
            
            # Create backup
            backup_name = self.backup_manager.create_backup(name, description)
            
            if backup_name:
                self.progress_bar.setValue(100)
                self._update_status(f"Backup created successfully: {backup_name}")
                
                # Clear inputs
                self.backup_name_edit.clear()
                self.backup_desc_edit.clear()
                
                # Refresh list
                self._refresh_backup_list()
            else:
                self._update_status("Failed to create backup", error=True)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            self._update_status(f"Error creating backup: {e}", error=True)
        
        finally:
            self.create_backup_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def _on_restore_backup(self):
        """Handle backup restoration"""
        try:
            current_item = self.backup_list.currentItem()
            if current_item is None:
                return
            
            backup_data = current_item.data(qtx.Qt.UserRole)
            backup_name = backup_data['name']
            
            # Confirm restoration
            reply = qtx.QXMessageBox.question(
                self,
                "Confirm Restore",
                f"Are you sure you want to restore the layout from backup '{backup_name}'?\n\nThis will replace your current UI layout.",
                qtx.QXMessageBox.StandardButton.Yes | qtx.QXMessageBox.StandardButton.No
            )
            
            if reply == qtx.QXMessageBox.StandardButton.Yes:
                self.restore_btn.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                
                self._update_status("Restoring backup...")
                self.progress_bar.setValue(50)
                
                # Restore backup
                success = self.backup_manager.restore_backup(backup_name)
                
                if success:
                    self.progress_bar.setValue(100)
                    self._update_status(f"Backup restored successfully: {backup_name}")
                else:
                    self._update_status("Failed to restore backup", error=True)
                
                self.progress_bar.setVisible(False)
                self.restore_btn.setEnabled(True)
        
        except Exception as e:
            self.logger.error(f"Failed to restore backup: {e}")
            self._update_status(f"Error restoring backup: {e}", error=True)
            self.restore_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def _on_delete_backup(self):
        """Handle backup deletion"""
        try:
            current_item = self.backup_list.currentItem()
            if current_item is None:
                return
            
            backup_data = current_item.data(qtx.Qt.UserRole)
            backup_name = backup_data['name']
            
            # Confirm deletion
            reply = qtx.QXMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the backup '{backup_name}'?\n\nThis action cannot be undone.",
                qtx.QXMessageBox.StandardButton.Yes | qtx.QXMessageBox.StandardButton.No
            )
            
            if reply == qtx.QXMessageBox.StandardButton.Yes:
                # Delete backup
                success = self.backup_manager.delete_backup(backup_name)
                
                if success:
                    self._update_status(f"Backup deleted: {backup_name}")
                    self._refresh_backup_list()
                else:
                    self._update_status("Failed to delete backup", error=True)
        
        except Exception as e:
            self.logger.error(f"Failed to delete backup: {e}")
            self._update_status(f"Error deleting backup: {e}", error=True)
    
    def _on_export_backup(self):
        """Handle backup export"""
        try:
            current_item = self.backup_list.currentItem()
            if current_item is None:
                return
            
            backup_data = current_item.data(qtx.Qt.UserRole)
            backup_name = backup_data['name']
            
            # Get export path
            export_path, _ = qtx.QXFileDialog.getSaveFileName(
                self,
                "Export Backup",
                f"{backup_name}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if export_path:
                export_path = Path(export_path)
                success = self.backup_manager.export_backup(backup_name, export_path)
                
                if success:
                    self._update_status(f"Backup exported to: {export_path}")
                else:
                    self._update_status("Failed to export backup", error=True)
        
        except Exception as e:
            self.logger.error(f"Failed to export backup: {e}")
            self._update_status(f"Error exporting backup: {e}", error=True)
    
    def _update_status(self, message: str, error: bool = False):
        """Update status message"""
        try:
            if error:
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setStyleSheet("")
            
            self.status_label.setText(message)
            
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")


class QBackupManagerDialog(qtx.QXDialog):
    """Dialog for the backup manager"""
    
    def __init__(self, backup_manager: UILayoutBackupManager, parent=None):
        super().__init__(parent)
        
        self.backup_manager = backup_manager
        
        self.setWindowTitle("UI Layout Backup Manager")
        self.setModal(True)
        self.resize(600, 500)
        
        # Create main widget
        self.backup_ui = QBackupManagerUI(backup_manager)
        
        # Create layout
        layout = qtx.QXVBoxLayout()
        layout.addWidget(self.backup_ui)
        
        # Add close button
        close_btn = qtx.QXPushButton(text="Close", on_clicked=self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout) 