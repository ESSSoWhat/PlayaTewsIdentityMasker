from pathlib import Path
from typing import List, Dict, Optional
import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit,
                            QCheckBox, QGroupBox, QTabWidget, QSplitter, 
                            QListWidget, QListWidgetItem, QSlider, QFrame,
                            QTextEdit, QProgressBar, QScrollArea, QSizePolicy,
                            QDialog, QDialogButtonBox, QFormLayout, QSpinBox)

from localization import L
from resources.fonts import QXFontDB
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from .widgets.QBackendPanel import QBackendPanel
from .widgets.QCheckBoxCSWFlag import QCheckBoxCSWFlag
from .widgets.QComboBoxCSWDynamicSingleSwitch import QComboBoxCSWDynamicSingleSwitch
from .widgets.QErrorCSWError import QErrorCSWError
from .widgets.QLabelCSWNumber import QLabelCSWNumber
from .widgets.QLabelPopupInfo import QLabelPopupInfo
from .widgets.QLineEditCSWText import QLineEditCSWText
from .widgets.QPathEditCSWPaths import QPathEditCSWPaths
from .widgets.QSpinBoxCSWNumber import QSpinBoxCSWNumber
from .widgets.QXPushButtonCSWSignal import QXPushButtonCSWSignal

from ..backend.EnhancedStreamOutput import EnhancedStreamOutput, StreamingPlatform, RecordingFormat
from ..backend.StreamOutput import SourceType


class PlatformSettingsDialog(QDialog):
    """Dialog for configuring streaming platform settings"""
    
    def __init__(self, platform: StreamingPlatform, parent=None):
        super().__init__(parent)
        self.platform = platform
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"Configure {self.platform.name}")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Platform-specific settings
        form_layout = QFormLayout()
        
        self.enabled_checkbox = QCheckBox("Enable this platform")
        form_layout.addRow("Enabled:", self.enabled_checkbox)
        
        if self.platform != StreamingPlatform.CUSTOM_RTMP:
            self.stream_key_edit = QLineEdit()
            self.stream_key_edit.setPlaceholderText("Enter your stream key")
            self.stream_key_edit.setEchoMode(QLineEdit.Password)
            form_layout.addRow("Stream Key:", self.stream_key_edit)
        else:
            self.rtmp_url_edit = QLineEdit()
            self.rtmp_url_edit.setPlaceholderText("rtmp://your-server.com/live/stream-key")
            form_layout.addRow("RTMP URL:", self.rtmp_url_edit)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['1080p', '720p', '480p', '360p'])
        self.quality_combo.setCurrentText('720p')
        form_layout.addRow("Quality:", self.quality_combo)
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['30', '60'])
        self.fps_combo.setCurrentText('30')
        form_layout.addRow("FPS:", self.fps_combo)
        
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1000, 8000)
        self.bitrate_spin.setValue(2500)
        self.bitrate_spin.setSuffix(" kbps")
        form_layout.addRow("Bitrate:", self.bitrate_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class QEnhancedStreamOutput(QBackendPanel):
    """Enhanced streaming output panel with multi-platform support and scene management"""
    
    def __init__(self, backend: EnhancedStreamOutput):
        super().__init__(backend, L('@QEnhancedStreamOutput.module_title'))
        self.backend = backend
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the enhanced UI layout"""
        main_layout = QVBoxLayout()
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        
        # Streaming tab
        streaming_tab = self.create_streaming_tab()
        self.tabs.addTab(streaming_tab, "Streaming")
        
        # Recording tab
        recording_tab = self.create_recording_tab()
        self.tabs.addTab(recording_tab, "Recording")
        
        # Scenes tab
        scenes_tab = self.create_scenes_tab()
        self.tabs.addTab(scenes_tab, "Scenes")
        
        # Settings tab
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        
    def create_streaming_tab(self):
        """Create the streaming configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Main streaming controls
        controls_group = QGroupBox("Streaming Controls")
        controls_layout = QGridLayout()
        
        cs = self.backend.get_control_sheet()
        
        # FPS display
        q_average_fps_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.avg_fps'), 
                                             popup_info_text=L('@QEnhancedStreamOutput.help.avg_fps'))
        q_average_fps = QLabelCSWNumber(cs.avg_fps, reflect_state_widgets=[q_average_fps_label])
        
        # Streaming toggle
        q_is_streaming_label = QLabelPopupInfo(label='Multi-Platform Streaming')
        q_is_streaming = QCheckBoxCSWFlag(cs.is_streaming, reflect_state_widgets=[q_is_streaming_label])
        
        # Multi-platform toggle
        q_multi_platform_label = QLabelPopupInfo(label='Enable Multi-Platform')
        q_multi_platform = QCheckBoxCSWFlag(cs.multi_platform_streaming, reflect_state_widgets=[q_multi_platform_label])
        
        controls_layout.addWidget(q_average_fps_label, 0, 0)
        controls_layout.addWidget(q_average_fps, 0, 1)
        controls_layout.addWidget(q_is_streaming_label, 1, 0)
        controls_layout.addWidget(q_is_streaming, 1, 1)
        controls_layout.addWidget(q_multi_platform_label, 2, 0)
        controls_layout.addWidget(q_multi_platform, 2, 1)
        
        controls_group.setLayout(controls_layout)
        
        # Platform configuration
        platforms_group = QGroupBox("Streaming Platforms")
        platforms_layout = QVBoxLayout()
        
        self.platform_buttons = {}
        for platform in StreamingPlatform:
            if platform != StreamingPlatform.MULTI_PLATFORM:
                btn = QPushButton(f"Configure {platform.name}")
                btn.clicked.connect(lambda checked, p=platform: self.configure_platform(p))
                self.platform_buttons[platform] = btn
                platforms_layout.addWidget(btn)
        
        platforms_group.setLayout(platforms_layout)
        
        # Legacy streaming settings (for backward compatibility)
        legacy_group = QGroupBox("Legacy Streaming")
        legacy_layout = QGridLayout()
        
        q_stream_addr = QLineEditCSWText(cs.stream_addr, font=QXFontDB.get_fixedwidth_font())
        q_stream_port = QSpinBoxCSWNumber(cs.stream_port)
        
        legacy_layout.addWidget(QLabel("Stream Address:"), 0, 0)
        legacy_layout.addWidget(q_stream_addr, 0, 1)
        legacy_layout.addWidget(QLabel("Stream Port:"), 1, 0)
        legacy_layout.addWidget(q_stream_port, 1, 1)
        
        legacy_group.setLayout(legacy_layout)
        
        layout.addWidget(controls_group)
        layout.addWidget(platforms_group)
        layout.addWidget(legacy_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_recording_tab(self):
        """Create the recording configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        cs = self.backend.get_control_sheet()
        
        # Recording controls
        recording_group = QGroupBox("Recording Controls")
        recording_layout = QGridLayout()
        
        q_recording_enabled_label = QLabelPopupInfo(label='Enable Recording')
        q_recording_enabled = QCheckBoxCSWFlag(cs.recording_enabled, reflect_state_widgets=[q_recording_enabled_label])
        
        recording_layout.addWidget(q_recording_enabled_label, 0, 0)
        recording_layout.addWidget(q_recording_enabled, 0, 1)
        
        recording_group.setLayout(recording_layout)
        
        # Recording settings
        settings_group = QGroupBox("Recording Settings")
        settings_layout = QGridLayout()
        
        self.recording_format_combo = QComboBox()
        for format_type in RecordingFormat:
            self.recording_format_combo.addItem(format_type.name, format_type)
        self.recording_format_combo.setCurrentText('MP4')
        
        self.recording_quality_combo = QComboBox()
        self.recording_quality_combo.addItems(['1080p', '720p', '480p', '360p'])
        self.recording_quality_combo.setCurrentText('1080p')
        
        self.recording_fps_combo = QComboBox()
        self.recording_fps_combo.addItems(['30', '60'])
        self.recording_fps_combo.setCurrentText('30')
        
        self.recording_bitrate_spin = QSpinBox()
        self.recording_bitrate_spin.setRange(1000, 50000)
        self.recording_bitrate_spin.setValue(8000)
        self.recording_bitrate_spin.setSuffix(" kbps")
        
        settings_layout.addWidget(QLabel("Format:"), 0, 0)
        settings_layout.addWidget(self.recording_format_combo, 0, 1)
        settings_layout.addWidget(QLabel("Quality:"), 1, 0)
        settings_layout.addWidget(self.recording_quality_combo, 1, 1)
        settings_layout.addWidget(QLabel("FPS:"), 2, 0)
        settings_layout.addWidget(self.recording_fps_combo, 2, 1)
        settings_layout.addWidget(QLabel("Bitrate:"), 3, 0)
        settings_layout.addWidget(self.recording_bitrate_spin, 3, 1)
        
        settings_group.setLayout(settings_layout)
        
        # Legacy recording settings
        legacy_group = QGroupBox("Legacy Recording")
        legacy_layout = QGridLayout()
        
        q_save_sequence_path_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.save_sequence_path'), 
                                                    popup_info_text=L('@QEnhancedStreamOutput.help.save_sequence_path'))
        q_save_sequence_path = QPathEditCSWPaths(cs.save_sequence_path, reflect_state_widgets=[q_save_sequence_path_label])
        q_save_sequence_path_error = QErrorCSWError(cs.save_sequence_path_error)
        
        q_save_fill_frame_gap_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.save_fill_frame_gap'), 
                                                     popup_info_text=L('@QEnhancedStreamOutput.help.save_fill_frame_gap'))
        q_save_fill_frame_gap = QCheckBoxCSWFlag(cs.save_fill_frame_gap, reflect_state_widgets=[q_save_fill_frame_gap_label])
        
        legacy_layout.addWidget(q_save_sequence_path_label, 0, 0)
        legacy_layout.addWidget(q_save_sequence_path, 0, 1)
        legacy_layout.addWidget(q_save_sequence_path_error, 1, 0, 1, 2)
        legacy_layout.addWidget(q_save_fill_frame_gap_label, 2, 0)
        legacy_layout.addWidget(q_save_fill_frame_gap, 2, 1)
        
        legacy_group.setLayout(legacy_layout)
        
        layout.addWidget(recording_group)
        layout.addWidget(settings_group)
        layout.addWidget(legacy_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_scenes_tab(self):
        """Create the scenes management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        cs = self.backend.get_control_sheet()
        
        # Scene management
        scenes_group = QGroupBox("Scene Management")
        scenes_layout = QGridLayout()
        
        q_scene_name_label = QLabelPopupInfo(label='Current Scene')
        q_scene_name = QLineEditCSWText(cs.scene_name, reflect_state_widgets=[q_scene_name_label])
        
        q_add_scene = QXPushButtonCSWSignal(cs.add_scene, text="Add Scene", button_size=(None, 25))
        q_remove_scene = QXPushButtonCSWSignal(cs.remove_scene, text="Remove Scene", button_size=(None, 25))
        
        scenes_layout.addWidget(q_scene_name_label, 0, 0)
        scenes_layout.addWidget(q_scene_name, 0, 1)
        scenes_layout.addWidget(q_add_scene, 1, 0)
        scenes_layout.addWidget(q_remove_scene, 1, 1)
        
        scenes_group.setLayout(scenes_layout)
        
        # Scene list
        self.scenes_list = QListWidget()
        self.scenes_list.setMaximumHeight(200)
        self.update_scenes_list()
        
        # Source management
        sources_group = QGroupBox("Source Management")
        sources_layout = QVBoxLayout()
        
        self.sources_list = QListWidget()
        self.sources_list.setMaximumHeight(150)
        
        sources_buttons_layout = QHBoxLayout()
        self.add_source_btn = QPushButton("Add Source")
        self.remove_source_btn = QPushButton("Remove Source")
        self.source_properties_btn = QPushButton("Properties")
        
        sources_buttons_layout.addWidget(self.add_source_btn)
        sources_buttons_layout.addWidget(self.remove_source_btn)
        sources_buttons_layout.addWidget(self.source_properties_btn)
        sources_buttons_layout.addStretch()
        
        sources_layout.addWidget(self.sources_list)
        sources_layout.addLayout(sources_buttons_layout)
        
        sources_group.setLayout(sources_layout)
        
        layout.addWidget(scenes_group)
        layout.addWidget(QLabel("Available Scenes:"))
        layout.addWidget(self.scenes_list)
        layout.addWidget(sources_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def create_settings_tab(self):
        """Create the general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        cs = self.backend.get_control_sheet()
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QGridLayout()
        
        q_source_type_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.source_type'))
        q_source_type = QComboBoxCSWDynamicSingleSwitch(cs.source_type, reflect_state_widgets=[q_source_type_label])
        
        q_show_hide_window = QXPushButtonCSWSignal(cs.show_hide_window, text=L('@QEnhancedStreamOutput.show_hide_window'), button_size=(None, 22))
        
        q_aligned_face_id_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.aligned_face_id'), 
                                                 popup_info_text=L('@QEnhancedStreamOutput.help.aligned_face_id'))
        q_aligned_face_id = QSpinBoxCSWNumber(cs.aligned_face_id, reflect_state_widgets=[q_aligned_face_id_label])
        
        q_target_delay_label = QLabelPopupInfo(label=L('@QEnhancedStreamOutput.target_delay'), 
                                              popup_info_text=L('@QEnhancedStreamOutput.help.target_delay'))
        q_target_delay = QSpinBoxCSWNumber(cs.target_delay, reflect_state_widgets=[q_target_delay_label])
        
        display_layout.addWidget(q_source_type_label, 0, 0)
        display_layout.addWidget(q_source_type, 0, 1)
        display_layout.addWidget(q_show_hide_window, 0, 2)
        display_layout.addWidget(q_aligned_face_id_label, 1, 0)
        display_layout.addWidget(q_aligned_face_id, 1, 1, 1, 2)
        display_layout.addWidget(q_target_delay_label, 2, 0)
        display_layout.addWidget(q_target_delay, 2, 1, 1, 2)
        
        display_group.setLayout(display_layout)
        
        # Performance settings
        performance_group = QGroupBox("Performance Settings")
        performance_layout = QGridLayout()
        
        self.quality_preset_combo = QComboBox()
        self.quality_preset_combo.addItems(['High Quality', 'Balanced', 'Performance'])
        self.quality_preset_combo.setCurrentText('Balanced')
        
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        
        performance_layout.addWidget(QLabel("Quality Preset:"), 0, 0)
        performance_layout.addWidget(self.quality_preset_combo, 0, 1)
        performance_layout.addWidget(QLabel("Thread Count:"), 1, 0)
        performance_layout.addWidget(self.thread_count_spin, 1, 1)
        
        performance_group.setLayout(performance_layout)
        
        layout.addWidget(display_group)
        layout.addWidget(performance_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
        
    def configure_platform(self, platform: StreamingPlatform):
        """Open platform configuration dialog"""
        dialog = PlatformSettingsDialog(platform, self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply platform settings
            # This would update the backend with the new settings
            pass
            
    def update_scenes_list(self):
        """Update the scenes list widget"""
        self.scenes_list.clear()
        # This would populate the list with available scenes from the backend
        # For now, add a placeholder
        self.scenes_list.addItem("Default Scene")
        
    def setup_connections(self):
        """Setup signal connections"""
        # Connect recording format changes
        self.recording_format_combo.currentIndexChanged.connect(self.on_recording_format_changed)
        self.recording_quality_combo.currentIndexChanged.connect(self.on_recording_quality_changed)
        
        # Connect scene management
        self.add_source_btn.clicked.connect(self.add_source)
        self.remove_source_btn.clicked.connect(self.remove_source)
        self.source_properties_btn.clicked.connect(self.source_properties)
        
    def on_recording_format_changed(self):
        """Handle recording format change"""
        format_type = self.recording_format_combo.currentData()
        # Update backend recording format
        pass
        
    def on_recording_quality_changed(self):
        """Handle recording quality change"""
        quality = self.recording_quality_combo.currentText()
        # Update backend recording quality
        pass
        
    def add_source(self):
        """Add a new source to the current scene"""
        # This would open a dialog to select source type
        pass
        
    def remove_source(self):
        """Remove the selected source"""
        current_item = self.sources_list.currentItem()
        if current_item:
            self.sources_list.takeItem(self.sources_list.row(current_item))
            
    def source_properties(self):
        """Open source properties dialog"""
        current_item = self.sources_list.currentItem()
        if current_item:
            # This would open a properties dialog for the selected source
            pass