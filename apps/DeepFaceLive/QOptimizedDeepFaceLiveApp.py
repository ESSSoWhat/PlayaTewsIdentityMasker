#!/usr/bin/env python3
"""
Optimized DeepFaceLive Application
Integrates UI optimizations, lazy loading, and performance monitoring
"""

import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from localization import L, Localization
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend
from .ui.QOptimizedUIManager import get_ui_manager, cleanup_ui_manager
from .ui.QCameraSource import QCameraSource
from .ui.QFaceAligner import QFaceAligner
from .ui.QFaceAnimator import QFaceAnimator
from .ui.QFaceDetector import QFaceDetector
from .ui.QFaceMarker import QFaceMarker
from .ui.QFaceMerger import QFaceMerger
from .ui.QFaceSwapInsight import QFaceSwapInsight
from .ui.QFaceSwapDFM import QFaceSwapDFM
from .ui.QFileSource import QFileSource
from .ui.QFrameAdjuster import QFrameAdjuster
from .ui.QStreamOutput import QStreamOutput
from .ui.widgets.QOptimizedFrameViewer import QOptimizedFrameViewer
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer


class QOptimizedLiveSwap(qtx.QXWidget):
    """Optimized live swap widget with performance enhancements"""
    
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Optimized Live Swap...")
        
        # Create directories
        dfm_models_path = userdata_path / 'dfm_models'
        dfm_models_path.mkdir(parents=True, exist_ok=True)
        
        animatables_path = userdata_path / 'animatables'
        animatables_path.mkdir(parents=True, exist_ok=True)
        
        output_sequence_path = userdata_path / 'output_sequence'
        output_sequence_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize UI manager
        self.ui_manager = get_ui_manager()
        
        # Performance monitoring
        self.start_time = time.time()
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0.0
        
        # Initialize backend with optimized configuration
        self._init_backend(settings_dirpath, dfm_models_path, animatables_path, output_sequence_path)
        
        # Initialize UI components with lazy loading
        self._init_ui_components(animatables_path, dfm_models_path)
        
        # Setup layout with optimized viewers
        self._setup_layout()
        
        # Performance timer (reduced frequency)
        self._timer = qtx.QXTimer(interval=10, timeout=self._on_timer_10ms, start=True)
        
        self.logger.info("Optimized Live Swap initialization completed")
    
    def _init_backend(self, settings_dirpath: Path, dfm_models_path: Path, 
                     animatables_path: Path, output_sequence_path: Path):
        """Initialize backend with optimized configuration"""
        # Construct backend config with optimized settings
        self.backend_db = backend.BackendDB(settings_dirpath / 'states.dat')
        self.backend_weak_heap = backend.BackendWeakHeap(size_mb=1024)  # Reduced from 2048
        self.reemit_frame_signal = backend.BackendSignal()
        
        # Backend connections
        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out = backend.BackendConnection()
        face_marker_bc_out = backend.BackendConnection()
        face_aligner_bc_out = backend.BackendConnection()
        face_swapper_bc_out = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out = backend.BackendConnection()
        
        # Initialize backend components with optimized settings
        self.file_source = backend.FileSource(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_out=multi_sources_bc_out,
            backend_db=self.backend_db
        )
        
        self.camera_source = backend.CameraSource(
            weak_heap=self.backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=self.backend_db
        )
        
        self.face_detector = backend.FaceDetector(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=multi_sources_bc_out,
            bc_out=face_detector_bc_out,
            backend_db=self.backend_db
        )
        
        self.face_marker = backend.FaceMarker(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_detector_bc_out,
            bc_out=face_marker_bc_out,
            backend_db=self.backend_db
        )
        
        self.face_aligner = backend.FaceAligner(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_marker_bc_out,
            bc_out=face_aligner_bc_out,
            backend_db=self.backend_db
        )
        
        self.face_animator = backend.FaceAnimator(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_merger_bc_out,
            animatables_path=animatables_path,
            backend_db=self.backend_db
        )
        
        self.face_swap_insight = backend.FaceSwapInsight(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_swapper_bc_out,
            faces_path=animatables_path,
            backend_db=self.backend_db
        )
        
        self.face_swap_dfm = backend.FaceSwapDFM(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_swapper_bc_out,
            dfm_models_path=dfm_models_path,
            backend_db=self.backend_db
        )
        
        self.frame_adjuster = backend.FrameAdjuster(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_swapper_bc_out,
            bc_out=frame_adjuster_bc_out,
            backend_db=self.backend_db
        )
        
        self.face_merger = backend.FaceMerger(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=frame_adjuster_bc_out,
            bc_out=face_merger_bc_out,
            backend_db=self.backend_db
        )
        
        self.stream_output = backend.StreamOutput(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=face_merger_bc_out,
            save_default_path=userdata_path,
            backend_db=self.backend_db
        )
        
        self.all_backends: List[backend.BackendHost] = [
            self.file_source, self.camera_source, self.face_detector,
            self.face_marker, self.face_aligner, self.face_animator,
            self.face_swap_insight, self.face_swap_dfm, self.frame_adjuster,
            self.face_merger, self.stream_output
        ]
    
    def _init_ui_components(self, animatables_path: Path, dfm_models_path: Path):
        """Initialize UI components with lazy loading"""
        # Register UI components with priorities
        self.ui_manager.register_component(
            'file_source',
            lambda: QFileSource(self.file_source),
            load_priority=5
        )
        
        self.ui_manager.register_component(
            'camera_source',
            lambda: QCameraSource(self.camera_source),
            load_priority=5
        )
        
        self.ui_manager.register_component(
            'face_detector',
            lambda: QFaceDetector(self.face_detector),
            load_priority=4
        )
        
        self.ui_manager.register_component(
            'face_aligner',
            lambda: QFaceAligner(self.face_aligner),
            load_priority=4
        )
        
        self.ui_manager.register_component(
            'face_marker',
            lambda: QFaceMarker(self.face_marker),
            load_priority=3
        )
        
        self.ui_manager.register_component(
            'face_animator',
            lambda: QFaceAnimator(self.face_animator, animatables_path=animatables_path),
            load_priority=3
        )
        
        self.ui_manager.register_component(
            'face_swap_insight',
            lambda: QFaceSwapInsight(self.face_swap_insight, faces_path=animatables_path),
            load_priority=2
        )
        
        self.ui_manager.register_component(
            'face_swap_dfm',
            lambda: QFaceSwapDFM(self.face_swap_dfm, dfm_models_path=dfm_models_path),
            load_priority=2
        )
        
        self.ui_manager.register_component(
            'frame_adjuster',
            lambda: QFrameAdjuster(self.frame_adjuster),
            load_priority=1
        )
        
        self.ui_manager.register_component(
            'face_merger',
            lambda: QFaceMerger(self.face_merger),
            load_priority=1
        )
        
        self.ui_manager.register_component(
            'stream_output',
            lambda: QStreamOutput(self.stream_output),
            load_priority=1
        )
        
        # Initialize optimized viewers
        self.q_ds_frame_viewer = QOptimizedFrameViewer(
            self.backend_weak_heap,
            self.file_source.get_bc_out(),
            preview_width=256,
            update_interval_ms=33  # ~30 FPS
        )
        
        self.q_ds_fa_viewer = QBCFaceAlignViewer(
            self.backend_weak_heap,
            self.face_aligner.get_bc_out(),
            preview_width=256
        )
        
        self.q_ds_fc_viewer = QBCFaceSwapViewer(
            self.backend_weak_heap,
            self.face_merger.get_bc_out(),
            preview_width=256
        )
        
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(
            self.backend_weak_heap,
            self.face_merger.get_bc_out()
        )
    
    def _setup_layout(self):
        """Setup optimized layout with lazy-loaded components"""
        # Create placeholder widgets for lazy loading
        self.q_file_source_placeholder = self._create_placeholder('File Source')
        self.q_camera_source_placeholder = self._create_placeholder('Camera Source')
        self.q_face_detector_placeholder = self._create_placeholder('Face Detector')
        self.q_face_aligner_placeholder = self._create_placeholder('Face Aligner')
        self.q_face_marker_placeholder = self._create_placeholder('Face Marker')
        self.q_face_animator_placeholder = self._create_placeholder('Face Animator')
        self.q_face_swap_insight_placeholder = self._create_placeholder('Face Swap Insight')
        self.q_face_swap_dfm_placeholder = self._create_placeholder('Face Swap DFM')
        self.q_frame_adjuster_placeholder = self._create_placeholder('Frame Adjuster')
        self.q_face_merger_placeholder = self._create_placeholder('Face Merger')
        self.q_stream_output_placeholder = self._create_placeholder('Stream Output')
        
        # Setup nodes layout with placeholders
        q_nodes = qtx.QXWidgetHBox([
            qtx.QXWidgetVBox([self.q_file_source_placeholder, self.q_camera_source_placeholder], spacing=5, fixed_width=256),
            qtx.QXWidgetVBox([self.q_face_detector_placeholder, self.q_face_aligner_placeholder], spacing=5, fixed_width=256),
            qtx.QXWidgetVBox([self.q_face_marker_placeholder, self.q_face_animator_placeholder, 
                             self.q_face_swap_insight_placeholder, self.q_face_swap_dfm_placeholder], spacing=5, fixed_width=256),
            qtx.QXWidgetVBox([self.q_frame_adjuster_placeholder, self.q_face_merger_placeholder, 
                             self.q_stream_output_placeholder], spacing=5, fixed_width=256),
        ], spacing=5, size_policy=('fixed', 'fixed'))
        
        # Setup viewers layout
        q_view_nodes = qtx.QXWidgetHBox([
            (qtx.QXWidgetVBox([self.q_ds_frame_viewer], fixed_width=256), qtx.AlignTop),
            (qtx.QXWidgetVBox([self.q_ds_fa_viewer], fixed_width=256), qtx.AlignTop),
            (qtx.QXWidgetVBox([self.q_ds_fc_viewer], fixed_width=256), qtx.AlignTop),
            (qtx.QXWidgetVBox([self.q_ds_merged_frame_viewer], fixed_width=256), qtx.AlignTop),
        ], spacing=5, size_policy=('fixed', 'fixed'))
        
        # Performance info widget
        self.performance_label = QXLabel(
            text="Performance: Initializing...",
            font=QXFontDB.get_fixedwidth_font(size=8)
        )
        
        self.setLayout(qtx.QXVBoxLayout([
            (qtx.QXWidgetVBox([q_nodes, q_view_nodes], spacing=5), qtx.AlignCenter),
            (self.performance_label, qtx.AlignCenter)
        ]))
    
    def _create_placeholder(self, name: str) -> qtx.QXWidget:
        """Create a placeholder widget that loads the real component when clicked"""
        placeholder = qtx.QXWidget()
        placeholder.setFixedSize(250, 100)
        placeholder.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 2px dashed #cccccc;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #e0e0e0;
                border-color: #999999;
            }
        """)
        
        label = QXLabel(text=f"Click to load {name}", alignment=qtx.AlignCenter)
        layout = qtx.QXVBoxLayout([(label, qtx.AlignCenter)])
        placeholder.setLayout(layout)
        
        # Connect click event to lazy load
        placeholder.mousePressEvent = lambda event: self._load_component_on_click(name, placeholder)
        
        return placeholder
    
    def _load_component_on_click(self, component_name: str, placeholder: qtx.QXWidget):
        """Load component when placeholder is clicked"""
        try:
            # Get the real component
            real_component = self.ui_manager.get_component(component_name)
            if real_component:
                # Replace placeholder with real component
                parent_layout = placeholder.parent().layout()
                placeholder_index = parent_layout.indexOf(placeholder)
                
                if placeholder_index >= 0:
                    parent_layout.removeWidget(placeholder)
                    placeholder.hide()
                    parent_layout.insertWidget(placeholder_index, real_component)
                    real_component.show()
                    
                    self.logger.info(f"Loaded component: {component_name}")
        except Exception as e:
            self.logger.error(f"Failed to load component {component_name}: {e}")
    
    def _process_messages(self):
        """Process backend messages with performance tracking"""
        start_time = time.time()
        
        self.backend_db.process_messages()
        for backend_component in self.all_backends:
            backend_component.process_messages()
        
        # Update performance metrics
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:  # Update FPS every second
            self.current_fps = self.frame_count / (current_time - self.start_time)
            self.frame_count = 0
            self.start_time = current_time
            self.last_fps_update = current_time
            
            # Update performance display
            ui_stats = self.ui_manager.get_performance_stats()
            perf_text = (f"FPS: {self.current_fps:.1f} | "
                        f"Loaded Components: {ui_stats['loaded_components']}/{ui_stats['total_components']} | "
                        f"Memory Efficiency: {ui_stats['memory_efficiency']:.1%}")
            self.performance_label.setText(perf_text)
    
    def _on_timer_10ms(self):
        """Optimized timer callback"""
        self._process_messages()
        
        # Optimize UI performance periodically
        if time.time() % 5 < 0.01:  # Every ~5 seconds
            self.ui_manager.optimize_for_performance(target_fps=30)
    
    def clear_backend_db(self):
        """Clear backend database"""
        self.backend_db.clear()
    
    def initialize(self):
        """Initialize with optimized startup"""
        self.logger.info("Starting optimized initialization...")
        
        for bcknd in self.all_backends:
            default_state = True
            if isinstance(bcknd, (backend.CameraSource, backend.FaceAnimator, backend.FaceSwapInsight)):
                default_state = False
            bcknd.restore_on_off_state(default_state=default_state)
        
        self.logger.info("Optimized initialization completed")
    
    def finalize(self):
        """Clean up resources"""
        self.logger.info("Finalizing optimized application...")
        
        # Gracefully stop the backend
        for backend_component in self.all_backends:
            while backend_component.is_starting() or backend_component.is_stopping():
                self._process_messages()
            
            backend_component.save_on_off_state()
            backend_component.stop()
        
        while not all(x.is_stopped() for x in self.all_backends):
            self._process_messages()
        
        self.backend_db.finish_pending_jobs()
        
        # Clear viewers
        self.q_ds_frame_viewer.clear()
        self.q_ds_fa_viewer.clear()
        
        # Clean up UI manager
        cleanup_ui_manager()
        
        self.logger.info("Optimized application finalization completed")


class QOptimizedDFLAppWindow(qtx.QXWindow):
    """Optimized DeepFaceLive application window"""
    
    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=('minimum', 'minimum'))
        
        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath
        self.logger = logging.getLogger(__name__)
        
        # Setup menu bar
        self._setup_menu_bar()
        
        # Initialize optimized live swap
        self.q_live_swap = None
        self.q_live_swap_container = qtx.QXWidget()
        
        self.content_l = qtx.QXVBoxLayout()
        
        # Process priority control
        cb_process_priority = self._cb_process_priority = qtx.QXSaveableComboBox(
            db_key='_QOptimizedDFLAppWindow_process_priority',
            choices=[lib_os.ProcessPriority.NORMAL, lib_os.ProcessPriority.IDLE],
            default_choice=lib_os.ProcessPriority.NORMAL,
            choices_names=[L('@QDFLAppWindow.process_priority.normal'), L('@QDFLAppWindow.process_priority.lowest')],
            on_choice_selected=self._on_cb_process_priority_choice
        )
        
        menu_bar_tail = qtx.QXFrameHBox([
            10, QXLabel(text=L('@QDFLAppWindow.process_priority')), 4, cb_process_priority
        ], size_policy=('fixed', 'fixed'))
        
        self.setLayout(qtx.QXVBoxLayout([
            qtx.QXWidgetHBox([self.menu_bar, menu_bar_tail, qtx.QXFrame()], size_policy=('minimumexpanding', 'fixed')),
            5,
            qtx.QXWidget(layout=self.content_l)
        ]))
        
        self.call_on_closeEvent(self._on_closeEvent)
    
    def _setup_menu_bar(self):
        """Setup menu bar with optimized options"""
        self.menu_bar = qtx.QXMenuBar(
            font=QXFontDB.get_default_font(size=10),
            size_policy=('fixed', 'minimumexpanding')
        )
        
        menu_file = self.menu_bar.addMenu(L('@QDFLAppWindow.file'))
        menu_language = self.menu_bar.addMenu(L('@QDFLAppWindow.language'))
        menu_performance = self.menu_bar.addMenu('Performance')
        
        # File menu
        menu_file_action_reinitialize = menu_file.addAction(L('@QDFLAppWindow.reinitialize'))
        menu_file_action_reinitialize.triggered.connect(
            lambda: qtx.QXMainApplication.inst.reinitialize()
        )
        
        menu_file_action_reset_settings = menu_file.addAction(L('@QDFLAppWindow.reset_modules_settings'))
        menu_file_action_reset_settings.triggered.connect(self._on_reset_modules_settings)
        
        menu_file_action_quit = menu_file.addAction(L('@QDFLAppWindow.quit'))
        menu_file_action_quit.triggered.connect(lambda: qtx.QXMainApplication.quit())
        
        # Language menu
        languages = [
            ('English', 'en-US'),
            ('Español', 'es-ES'),
            ('Italiano', 'it-IT'),
            ('Русский', 'ru-RU'),
            ('汉语', 'zh-CN'),
            ('日本語', 'ja-JP')
        ]
        
        for lang_name, lang_code in languages:
            action = menu_language.addAction(lang_name)
            action.triggered.connect(
                lambda checked, code=lang_code: (
                    qtx.QXMainApplication.inst.set_language(code),
                    qtx.QXMainApplication.inst.reinitialize()
                )
            )
        
        # Performance menu
        menu_performance_action_stats = menu_performance.addAction('Show Performance Stats')
        menu_performance_action_stats.triggered.connect(self._show_performance_stats)
        
        menu_performance_action_optimize = menu_performance.addAction('Optimize Performance')
        menu_performance_action_optimize.triggered.connect(self._optimize_performance)
        
        # Help menu
        menu_help = self.menu_bar.addMenu(L('@QDFLAppWindow.help'))
        menu_help_action_github = menu_help.addAction(L('@QDFLAppWindow.visit_github_page'))
        menu_help_action_github.triggered.connect(
            lambda: qtx.QDesktopServices.openUrl(qtx.QUrl('https://github.com/iperov/DeepFaceLive'))
        )
    
    def _on_reset_modules_settings(self):
        """Reset modules settings"""
        if self.q_live_swap:
            self.q_live_swap.clear_backend_db()
    
    def _on_cb_process_priority_choice(self, prio: lib_os.ProcessPriority, _):
        """Handle process priority change"""
        lib_os.set_process_priority(prio)
    
    def _show_performance_stats(self):
        """Show performance statistics"""
        if self.q_live_swap and hasattr(self.q_live_swap, 'ui_manager'):
            stats = self.q_live_swap.ui_manager.get_performance_stats()
            stats_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])
            
            # Show in a simple dialog
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Performance Statistics")
            msg.setText(stats_text)
            msg.exec()
    
    def _optimize_performance(self):
        """Trigger performance optimization"""
        if self.q_live_swap and hasattr(self.q_live_swap, 'ui_manager'):
            self.q_live_swap.ui_manager.optimize_for_performance(target_fps=30)
            self.logger.info("Performance optimization triggered")
    
    def finalize(self):
        """Finalize the application"""
        if self.q_live_swap:
            self.q_live_swap.finalize()
    
    def _on_closeEvent(self):
        """Handle close event"""
        self.finalize()


class OptimizedDeepFaceLiveApp(qtx.QXMainApplication):
    """Optimized DeepFaceLive application"""
    
    def __init__(self, userdata_path):
        super().__init__(userdata_path=userdata_path)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Optimized DeepFaceLive Application...")
        
        # Set up localization
        Localization.initialize()
        
        # Create main window
        self.main_window = QOptimizedDFLAppWindow(
            userdata_path=userdata_path,
            settings_dirpath=userdata_path / 'settings'
        )
        
        # Initialize live swap
        self.main_window.q_live_swap = QOptimizedLiveSwap(
            userdata_path=userdata_path,
            settings_dirpath=userdata_path / 'settings'
        )
        
        self.main_window.content_l.addWidget(self.main_window.q_live_swap)
        
        # Show window
        self.main_window.show()
        
        # Initialize after showing window
        self.main_window.q_live_swap.initialize()
        
        self.logger.info("Optimized DeepFaceLive Application started successfully")
    
    def on_reinitialize(self):
        """Handle reinitialization"""
        self.logger.info("Reinitializing optimized application...")
        
        if hasattr(self.main_window, 'q_live_swap'):
            self.main_window.q_live_swap.finalize()
        
        # Recreate live swap
        self.main_window.q_live_swap = QOptimizedLiveSwap(
            userdata_path=self.userdata_path,
            settings_dirpath=self.userdata_path / 'settings'
        )
        
        # Replace in layout
        old_widget = self.main_window.content_l.itemAt(0).widget()
        if old_widget:
            old_widget.setParent(None)
        
        self.main_window.content_l.addWidget(self.main_window.q_live_swap)
        self.main_window.q_live_swap.initialize()
        
        self.logger.info("Optimized application reinitialized")
    
    def initialize(self):
        """Initialize the application"""
        self.logger.info("Initializing optimized application...")
    
    def finalize(self):
        """Finalize the application"""
        self.logger.info("Finalizing optimized application...")
        if hasattr(self.main_window, 'q_live_swap'):
            self.main_window.q_live_swap.finalize()
    
    def _on_splash_wnd_expired(self):
        """Handle splash window expiration"""
        pass