# UI Relocation Implementation Plan

## Phase 1: Consolidate LiveSwap Components

### Current Problem
Four different LiveSwap implementations with duplicate functionality:
- `QLiveSwap` (traditional)
- `QLiveSwapOBS` (OBS-style)
- `QOptimizedLiveSwap` (optimized)
- `QOBSStyleLiveSwap` (DeepFaceLive)

### Solution: Unified LiveSwap Component

```python
# apps/PlayaTewsIdentityMasker/ui/QUnifiedLiveSwap.py
from enum import Enum
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import pyqtSignal

class UIMode(Enum):
    TRADITIONAL = "traditional"
    OBS_STYLE = "obs_style"
    OPTIMIZED = "optimized"
    COMPACT = "compact"

class QUnifiedLiveSwap(QWidget):
    """Unified LiveSwap component with multiple presentation modes"""
    
    def __init__(self, userdata_path: Path, settings_dirpath: Path, mode: UIMode = UIMode.OPTIMIZED):
        super().__init__()
        self.userdata_path = userdata_path
        self.settings_dirpath = settings_dirpath
        self.mode = mode
        
        # Initialize backend components (shared across all modes)
        self.setup_backend()
        
        # Create UI based on mode
        self.setup_ui()
        
    def setup_backend(self):
        """Initialize shared backend components"""
        # Move backend initialization here from individual implementations
        self.backend_db = backend.BackendDB(self.settings_dirpath / 'states.dat')
        self.backend_weak_heap = backend.BackendWeakHeap(size_mb=2048)
        self.reemit_frame_signal = backend.BackendSignal()
        
        # Initialize all backend components
        self.setup_backend_connections()
        self.setup_backend_components()
        
    def setup_ui(self):
        """Setup UI based on selected mode"""
        if self.mode == UIMode.TRADITIONAL:
            self.setup_traditional_layout()
        elif self.mode == UIMode.OBS_STYLE:
            self.setup_obs_layout()
        elif self.mode == UIMode.OPTIMIZED:
            self.setup_optimized_layout()
        elif self.mode == UIMode.COMPACT:
            self.setup_compact_layout()
    
    def setup_optimized_layout(self):
        """New optimized layout with logical grouping"""
        main_layout = QHBoxLayout()
        
        # Input Panel (File, Camera, Voice)
        input_panel = self.create_input_panel()
        
        # Detection Panel (Face Detector, Face Marker)
        detection_panel = self.create_detection_panel()
        
        # Processing Panel (Face Aligner, Face Animator, Face Swap Insight)
        processing_panel = self.create_processing_panel()
        
        # Enhancement Panel (Face Swap DFM, Frame Adjuster, Face Merger)
        enhancement_panel = self.create_enhancement_panel()
        
        # Output Panel (Stream Output)
        output_panel = self.create_output_panel()
        
        # Add panels to layout with optimized sizing
        main_layout.addWidget(input_panel, 1)      # 300px
        main_layout.addWidget(detection_panel, 1)  # 250px
        main_layout.addWidget(processing_panel, 1) # 300px
        main_layout.addWidget(enhancement_panel, 1) # 250px
        main_layout.addWidget(output_panel, 1)     # 300px
        
        self.setLayout(main_layout)
    
    def create_input_panel(self):
        """Consolidated input panel with File, Camera, and Voice Changer"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # File and Camera sources in horizontal layout
        sources_layout = QHBoxLayout()
        sources_layout.addWidget(self.q_file_source)
        sources_layout.addWidget(self.q_camera_source)
        
        layout.addLayout(sources_layout)
        layout.addWidget(self.q_voice_changer)  # Moved from end to input section
        
        panel.setLayout(layout)
        return panel
    
    def create_detection_panel(self):
        """Detection panel with Face Detector and Face Marker"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(self.q_face_detector)
        layout.addWidget(self.q_face_marker)
        
        panel.setLayout(layout)
        return panel
    
    def create_processing_panel(self):
        """Processing panel with Face Aligner, Face Animator, and Face Swap Insight"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(self.q_face_aligner)
        layout.addWidget(self.q_face_animator)
        layout.addWidget(self.q_face_swap_insight)
        
        panel.setLayout(layout)
        return panel
    
    def create_enhancement_panel(self):
        """Enhancement panel with Face Swap DFM, Frame Adjuster, and Face Merger"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(self.q_face_swap_dfm)
        layout.addWidget(self.q_frame_adjuster)
        layout.addWidget(self.q_face_merger)
        
        panel.setLayout(layout)
        return panel
    
    def create_output_panel(self):
        """Output panel with Stream Output"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(self.q_stream_output)
        
        panel.setLayout(layout)
        return panel
```

## Phase 2: Relocate Unused Components

### Move QXTabWidget from _unused to Main UI

```python
# apps/PlayaTewsIdentityMasker/ui/widgets/QXTabWidget.py
from PyQt5.QtWidgets import QTabWidget, QWidget
from PyQt5.QtGui import QIcon

class QXTabWidget(QTabWidget):
    """Enhanced tab widget relocated from _unused"""
    
    def __init__(self, tabs=None, tab_shape=None, size_policy=None, 
                 maximum_width=None, hided=False, enabled=True):
        super().__init__()
        
        if tabs is not None:
            for tab, icon, name in tabs:
                self.addTab(tab, icon, name)
        
        if tab_shape is not None:
            self.setTabShape(tab_shape)
        
        if maximum_width is not None:
            self.setMaximumWidth(maximum_width)
        
        if size_policy is not None:
            self.setSizePolicy(*size_policy)
        
        if hided:
            self.hide()
        
        self.setEnabled(enabled)
    
    def add_tab_with_icon(self, widget, icon_path, title):
        """Add tab with icon from path"""
        icon = QIcon(icon_path) if icon_path else QIcon()
        self.addTab(widget, icon, title)
    
    def get_tab_by_title(self, title):
        """Get tab widget by title"""
        for i in range(self.count()):
            if self.tabText(i) == title:
                return self.widget(i)
        return None
```

### Move QXCollapsibleSection for Better Organization

```python
# apps/PlayaTewsIdentityMasker/ui/widgets/QXCollapsibleSection.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class QXCollapsibleSection(QWidget):
    """Collapsible section widget for organizing UI components"""
    
    section_toggled = pyqtSignal(bool)
    
    def __init__(self, title, content_widget=None, is_opened=False, 
                 allow_open_close=True, show_content_frame=True):
        super().__init__()
        
        self.title = title
        self.content_widget = content_widget
        self.is_opened = is_opened
        self.allow_open_close = allow_open_close
        self.show_content_frame = show_content_frame
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the collapsible section UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with toggle button
        header_layout = QHBoxLayout()
        
        self.toggle_btn = QToolButton()
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_btn.setStyleSheet('border: none; background: transparent;')
        self.toggle_btn.setArrowType(Qt.RightArrow if not self.is_opened else Qt.DownArrow)
        self.toggle_btn.setText(self.title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(self.is_opened)
        
        if self.allow_open_close:
            self.toggle_btn.toggled.connect(self.on_toggle)
        
        header_layout.addWidget(self.toggle_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Content area
        if self.content_widget:
            if self.show_content_frame:
                content_frame = QFrame()
                content_frame.setFrameShape(QFrame.StyledPanel)
                content_layout = QVBoxLayout(content_frame)
                content_layout.addWidget(self.content_widget)
                layout.addWidget(content_frame)
            else:
                layout.addWidget(self.content_widget)
        
        self.setLayout(layout)
        
        # Set initial visibility
        if self.content_widget:
            self.content_widget.setVisible(self.is_opened)
    
    def on_toggle(self, checked):
        """Handle toggle button click"""
        if self.content_widget:
            self.content_widget.setVisible(checked)
            self.toggle_btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        
        self.section_toggled.emit(checked)
    
    def set_content(self, widget):
        """Set the content widget"""
        if self.content_widget:
            self.layout().removeWidget(self.content_widget)
            self.content_widget.deleteLater()
        
        self.content_widget = widget
        if widget:
            self.layout().addWidget(widget)
            widget.setVisible(self.is_opened)
```

## Phase 3: Implement Tabbed Interface

### Create Tabbed Main Interface

```python
# apps/PlayaTewsIdentityMasker/ui/QTabbedMainInterface.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt

from .widgets.QXTabWidget import QXTabWidget
from .widgets.QXCollapsibleSection import QXCollapsibleSection
from .QUnifiedLiveSwap import QUnifiedLiveSwap

class QTabbedMainInterface(QWidget):
    """Main interface using tabbed layout for better organization"""
    
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()
        self.userdata_path = userdata_path
        self.settings_dirpath = settings_dirpath
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the tabbed interface"""
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QXTabWidget()
        
        # Create tabs
        self.create_input_tab()
        self.create_processing_tab()
        self.create_output_tab()
        self.create_settings_tab()
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def create_input_tab(self):
        """Create input tab with file, camera, and voice components"""
        input_widget = QWidget()
        input_layout = QVBoxLayout()
        
        # File and Camera sources section
        sources_section = QXCollapsibleSection(
            "Input Sources", 
            self.create_sources_layout(),
            is_opened=True
        )
        
        # Voice changer section
        voice_section = QXCollapsibleSection(
            "Voice Processing",
            self.create_voice_layout(),
            is_opened=True
        )
        
        input_layout.addWidget(sources_section)
        input_layout.addWidget(voice_section)
        input_layout.addStretch()
        
        input_widget.setLayout(input_layout)
        self.tab_widget.addTab(input_widget, "Input")
    
    def create_processing_tab(self):
        """Create processing tab with face processing components"""
        processing_widget = QWidget()
        processing_layout = QVBoxLayout()
        
        # Detection section
        detection_section = QXCollapsibleSection(
            "Face Detection",
            self.create_detection_layout(),
            is_opened=True
        )
        
        # Processing section
        processing_section = QXCollapsibleSection(
            "Face Processing",
            self.create_face_processing_layout(),
            is_opened=True
        )
        
        # Enhancement section
        enhancement_section = QXCollapsibleSection(
            "Face Enhancement",
            self.create_enhancement_layout(),
            is_opened=True
        )
        
        processing_layout.addWidget(detection_section)
        processing_layout.addWidget(processing_section)
        processing_layout.addWidget(enhancement_section)
        processing_layout.addStretch()
        
        processing_widget.setLayout(processing_layout)
        self.tab_widget.addTab(processing_widget, "Processing")
    
    def create_output_tab(self):
        """Create output tab with streaming and recording"""
        output_widget = QWidget()
        output_layout = QVBoxLayout()
        
        # Streaming section
        streaming_section = QXCollapsibleSection(
            "Streaming",
            self.create_streaming_layout(),
            is_opened=True
        )
        
        # Recording section
        recording_section = QXCollapsibleSection(
            "Recording",
            self.create_recording_layout(),
            is_opened=True
        )
        
        output_layout.addWidget(streaming_section)
        output_layout.addWidget(recording_section)
        output_layout.addStretch()
        
        output_widget.setLayout(output_layout)
        self.tab_widget.addTab(output_widget, "Output")
    
    def create_settings_tab(self):
        """Create settings tab with configuration options"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        
        # Performance settings
        performance_section = QXCollapsibleSection(
            "Performance Settings",
            self.create_performance_layout(),
            is_opened=False
        )
        
        # Advanced settings
        advanced_section = QXCollapsibleSection(
            "Advanced Settings",
            self.create_advanced_layout(),
            is_opened=False
        )
        
        settings_layout.addWidget(performance_section)
        settings_layout.addWidget(advanced_section)
        settings_layout.addStretch()
        
        settings_widget.setLayout(settings_layout)
        self.tab_widget.addTab(settings_widget, "Settings")
```

## Phase 4: Optimize Panel Sizing

### Dynamic Panel Sizing System

```python
# apps/PlayaTewsIdentityMasker/ui/PanelSizeOptimizer.py
from typing import Dict, List, Tuple
from dataclasses import dataclass
from PyQt5.QtWidgets import QWidget, QSplitter
from PyQt5.QtCore import Qt

@dataclass
class PanelInfo:
    name: str
    min_width: int
    preferred_width: int
    max_width: int
    priority: int  # Higher = more important

class PanelSizeOptimizer:
    """Optimizes panel sizing based on content and user preferences"""
    
    def __init__(self):
        self.panels: Dict[str, PanelInfo] = {}
        self.current_sizes: Dict[str, int] = {}
        
        # Define optimal panel sizes
        self.setup_panel_definitions()
    
    def setup_panel_definitions(self):
        """Define optimal sizes for each panel type"""
        self.panels = {
            'input': PanelInfo('input', 280, 300, 350, 1),
            'detection': PanelInfo('detection', 230, 250, 280, 2),
            'processing': PanelInfo('processing', 280, 300, 350, 3),
            'enhancement': PanelInfo('enhancement', 230, 250, 280, 4),
            'output': PanelInfo('output', 280, 300, 350, 5),
        }
    
    def optimize_layout(self, splitter: QSplitter, available_width: int):
        """Optimize panel sizes based on available width"""
        # Calculate total preferred width
        total_preferred = sum(panel.preferred_width for panel in self.panels.values())
        
        if total_preferred <= available_width:
            # Use preferred sizes
            sizes = [panel.preferred_width for panel in self.panels.values()]
        else:
            # Distribute proportionally
            sizes = self.distribute_proportionally(available_width)
        
        # Apply sizes to splitter
        splitter.setSizes(sizes)
        
        # Store current sizes
        for i, (panel_name, size) in enumerate(zip(self.panels.keys(), sizes)):
            self.current_sizes[panel_name] = size
    
    def distribute_proportionally(self, available_width: int) -> List[int]:
        """Distribute available width proportionally among panels"""
        total_priority = sum(panel.priority for panel in self.panels.values())
        sizes = []
        
        for panel in self.panels.values():
            # Calculate proportional size based on priority
            proportional = (panel.priority / total_priority) * available_width
            
            # Ensure within min/max bounds
            size = max(panel.min_width, min(panel.max_width, int(proportional)))
            sizes.append(size)
        
        return sizes
    
    def get_optimal_sizes(self, available_width: int) -> Dict[str, int]:
        """Get optimal sizes for current available width"""
        self.optimize_layout(None, available_width)
        return self.current_sizes.copy()
```

## Phase 5: Implementation Steps

### Step 1: Create Migration Script

```python
# scripts/migrate_ui_components.py
#!/usr/bin/env python3
"""
Migration script to relocate UI components for better efficiency
"""

import os
import shutil
from pathlib import Path

def migrate_unused_components():
    """Move unused components to main UI directory"""
    
    # Source and destination paths
    unused_dir = Path("xlib/qt/_unused")
    ui_widgets_dir = Path("apps/PlayaTewsIdentityMasker/ui/widgets")
    
    # Components to migrate
    components_to_migrate = [
        ("_unused.py", "QXTabWidget.py"),
        ("_unused.py", "QXCollapsibleSection.py"),
        ("_unused.py", "QXIconButton.py"),
    ]
    
    for source_file, dest_file in components_to_migrate:
        source_path = unused_dir / source_file
        dest_path = ui_widgets_dir / dest_file
        
        if source_path.exists():
            # Extract component from source file and create new file
            extract_component(source_path, dest_path, dest_file.replace('.py', ''))
            print(f"Migrated {dest_file}")

def extract_component(source_file: Path, dest_file: Path, component_name: str):
    """Extract a specific component from source file"""
    # Implementation to extract specific component code
    pass

def update_imports():
    """Update import statements in existing files"""
    files_to_update = [
        "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py",
        "apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerOBSStyleApp.py",
        "apps/PlayaTewsIdentityMasker/QOptimizedPlayaTewsIdentityMaskerApp.py",
    ]
    
    for file_path in files_to_update:
        update_file_imports(Path(file_path))

def update_file_imports(file_path: Path):
    """Update import statements in a specific file"""
    # Implementation to update imports
    pass

if __name__ == "__main__":
    print("Starting UI component migration...")
    migrate_unused_components()
    update_imports()
    print("Migration completed!")
```

### Step 2: Update Main Application

```python
# apps/PlayaTewsIdentityMasker/PlayaTewsIdentityMaskerApp.py (updated)
# ... existing imports ...
from .ui.QUnifiedLiveSwap import QUnifiedLiveSwap, UIMode

class PlayaTewsIdentityMaskerApp(qtx.QXMainApplication):
    def __init__(self, userdata_path):
        super().__init__()
        self._userdata_path = userdata_path
        self._settings_dirpath = userdata_path / 'settings'
        
        # Use unified LiveSwap component
        self.q_live_swap = QUnifiedLiveSwap(
            userdata_path=self._userdata_path,
            settings_dirpath=self._settings_dirpath,
            mode=UIMode.OPTIMIZED  # Use optimized layout by default
        )
```

## Expected Results

After implementing these relocations:

1. **Reduced Code Duplication**: 4 LiveSwap implementations → 1 unified component
2. **Better Organization**: Tabbed interface with collapsible sections
3. **Improved Performance**: Lazy loading and optimized panel sizing
4. **Enhanced UX**: Logical workflow and better space utilization
5. **Easier Maintenance**: Consolidated codebase with clear separation of concerns

The implementation should be done incrementally, testing each phase before proceeding to the next.