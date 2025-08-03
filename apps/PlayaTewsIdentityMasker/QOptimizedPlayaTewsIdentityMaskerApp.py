#!/usr/bin/env python3
"""
Optimized DeepFaceLive Application
Integrates UI optimizations, lazy loading, and performance monitoring
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from localization import L, Localization
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend

# Lazy loading temporarily disabled to fix widget hierarchy issues
from .ui.QCameraSource import QCameraSource
from .ui.QEnhancedStreamOutput import QEnhancedStreamOutput
from .ui.QFaceAligner import QFaceAligner
from .ui.QFaceAnimator import QFaceAnimator
from .ui.QFaceDetector import QFaceDetector
from .ui.QFaceMarker import QFaceMarker
from .ui.QFaceMerger import QFaceMerger
from .ui.QFaceSwapDFM import QFaceSwapDFM
from .ui.QFaceSwapInsight import QFaceSwapInsight
from .ui.QFileSource import QFileSource
from .ui.QFrameAdjuster import QFrameAdjuster
from .ui.QStreamOutput import QStreamOutput
from .ui.QVoiceChanger import QVoiceChanger
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer


class QOptimizedLiveSwap(qtx.QXWidget):
    """Optimized live swap widget with performance enhancements"""

    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Optimized Live Swap...")

        # Create directories
        dfm_models_path = userdata_path / "dfm_models"
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / "animatables"
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / "output_sequence"
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Performance monitoring
        self.start_time = time.time()
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0.0

        # Initialize backend with optimized configuration
        self._init_backend(
            settings_dirpath,
            dfm_models_path,
            animatables_path,
            output_sequence_path,
            userdata_path,
        )

        # Initialize UI components directly (avoiding lazy loading for now)
        self._init_ui_components(animatables_path, dfm_models_path)

        # Setup layout with optimized viewers
        self._setup_layout()

        # Performance timer (reduced frequency)
        self._timer = qtx.QXTimer(interval=10, timeout=self._on_timer_10ms, start=True)

        self.logger.info("Optimized Live Swap initialization completed")

    def _init_backend(
        self,
        settings_dirpath: Path,
        dfm_models_path: Path,
        animatables_path: Path,
        output_sequence_path: Path,
        userdata_path: Path,
    ):
        """Initialize backend with optimized configuration"""
        # Construct backend config with optimized settings
        self.backend_db = backend.BackendDB(settings_dirpath / "states.dat")
        self.backend_weak_heap = backend.BackendWeakHeap(
            size_mb=1024
        )  # Reduced from 2048
        self.reemit_frame_signal = backend.BackendSignal()

        # Backend connections
        self.multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        self.face_detector_bc_out = backend.BackendConnection()
        self.face_marker_bc_out = backend.BackendConnection()
        self.face_aligner_bc_out = backend.BackendConnection()
        self.face_swapper_bc_out = backend.BackendConnection()
        self.frame_adjuster_bc_out = backend.BackendConnection()
        self.face_merger_bc_out = backend.BackendConnection()

        # Initialize backend components with optimized settings
        self.file_source = backend.FileSource(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_out=self.multi_sources_bc_out,
            backend_db=self.backend_db,
        )

        self.camera_source = backend.CameraSource(
            weak_heap=self.backend_weak_heap,
            bc_out=self.multi_sources_bc_out,
            backend_db=self.backend_db,
        )

        self.face_detector = backend.FaceDetector(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.multi_sources_bc_out,
            bc_out=self.face_detector_bc_out,
            backend_db=self.backend_db,
        )

        self.face_marker = backend.FaceMarker(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_detector_bc_out,
            bc_out=self.face_marker_bc_out,
            backend_db=self.backend_db,
        )

        self.face_aligner = backend.FaceAligner(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_marker_bc_out,
            bc_out=self.face_aligner_bc_out,
            backend_db=self.backend_db,
        )

        self.face_animator = backend.FaceAnimator(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_aligner_bc_out,
            bc_out=self.face_merger_bc_out,
            animatables_path=animatables_path,
            backend_db=self.backend_db,
        )

        self.face_swap_insight = backend.FaceSwapInsight(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_aligner_bc_out,
            bc_out=self.face_swapper_bc_out,
            faces_path=animatables_path,
            backend_db=self.backend_db,
        )

        self.face_swap_dfm = backend.FaceSwapDFM(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_aligner_bc_out,
            bc_out=self.face_swapper_bc_out,
            dfm_models_path=dfm_models_path,
            backend_db=self.backend_db,
        )

        self.frame_adjuster = backend.FrameAdjuster(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_swapper_bc_out,
            bc_out=self.frame_adjuster_bc_out,
            backend_db=self.backend_db,
        )

        self.face_merger = backend.FaceMerger(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.frame_adjuster_bc_out,
            bc_out=self.face_merger_bc_out,
            backend_db=self.backend_db,
        )

        # Use standard streaming output for compatibility
        self.stream_output = backend.StreamOutput(
            weak_heap=self.backend_weak_heap,
            reemit_frame_signal=self.reemit_frame_signal,
            bc_in=self.face_merger_bc_out,
            save_default_path=userdata_path,
            backend_db=self.backend_db,
        )

        # Add voice changer backend
        from .backend.VoiceChanger import VoiceChanger

        self.voice_changer = VoiceChanger(
            weak_heap=self.backend_weak_heap, backend_db=self.backend_db
        )

        self.all_backends: List[backend.BackendHost] = [
            self.file_source,
            self.camera_source,
            self.face_detector,
            self.face_marker,
            self.face_aligner,
            self.face_animator,
            self.face_swap_insight,
            self.face_swap_dfm,
            self.frame_adjuster,
            self.face_merger,
            self.stream_output,
            self.voice_changer,
        ]

    def _init_ui_components(self, animatables_path: Path, dfm_models_path: Path):
        """Initialize UI components with lazy loading"""
        # Store paths for lazy loading
        self.animatables_path = animatables_path
        self.dfm_models_path = dfm_models_path

        # Initialize lazy loader
        from .ui.QSimpleLazyLoader import QSimpleLazyLoader

        self.lazy_loader = QSimpleLazyLoader()

        # Register components for lazy loading
        self.lazy_loader.register_component(
            "file_source", lambda: QFileSource(self.file_source)
        )
        self.lazy_loader.register_component(
            "camera_source", lambda: QCameraSource(self.camera_source)
        )
        self.lazy_loader.register_component(
            "face_detector", lambda: QFaceDetector(self.face_detector)
        )
        self.lazy_loader.register_component(
            "face_marker", lambda: QFaceMarker(self.face_marker)
        )
        self.lazy_loader.register_component(
            "face_aligner", lambda: QFaceAligner(self.face_aligner)
        )
        self.lazy_loader.register_component(
            "face_animator",
            lambda: QFaceAnimator(
                self.face_animator, animatables_path=animatables_path
            ),
        )
        self.lazy_loader.register_component(
            "face_swap_insight",
            lambda: QFaceSwapInsight(
                self.face_swap_insight, faces_path=animatables_path
            ),
        )
        self.lazy_loader.register_component(
            "face_swap_dfm",
            lambda: QFaceSwapDFM(self.face_swap_dfm, dfm_models_path=dfm_models_path),
        )
        self.lazy_loader.register_component(
            "frame_adjuster", lambda: QFrameAdjuster(self.frame_adjuster)
        )
        self.lazy_loader.register_component(
            "face_merger", lambda: QFaceMerger(self.face_merger)
        )
        self.lazy_loader.register_component(
            "stream_output", lambda: QStreamOutput(self.stream_output)
        )

        # Register voice changer with error handling
        def create_voice_changer():
            try:
                return QVoiceChanger(self.voice_changer.get_control_sheet())
            except Exception as e:
                self.logger.warning(f"VoiceChanger UI initialization failed: {e}")
                from xlib.qt.widgets.QXLabel import QXLabel

                placeholder = QXLabel("Voice Changer: Initialization Error")
                placeholder.setStyleSheet("color: #ff6b6b; padding: 10px;")
                return placeholder

        self.lazy_loader.register_component("voice_changer", create_voice_changer)

        # Register viewers
        self.lazy_loader.register_component(
            "frame_viewer",
            lambda: QBCFrameViewer(self.backend_weak_heap, self.multi_sources_bc_out),
        )

        self.lazy_loader.register_component(
            "fa_viewer",
            lambda: QBCFaceAlignViewer(
                self.backend_weak_heap, self.face_aligner_bc_out, preview_width=256
            ),
        )

        self.lazy_loader.register_component(
            "fc_viewer",
            lambda: QBCFaceSwapViewer(
                self.backend_weak_heap, self.face_merger_bc_out, preview_width=256
            ),
        )

        self.lazy_loader.register_component(
            "merged_frame_viewer",
            lambda: QBCMergedFrameViewer(
                self.backend_weak_heap, self.face_merger_bc_out
            ),
        )

        # Create lazy loading placeholders
        self.q_file_source = self.lazy_loader.get_placeholder("file_source")
        self.q_camera_source = self.lazy_loader.get_placeholder("camera_source")
        self.q_face_detector = self.lazy_loader.get_placeholder("face_detector")
        self.q_face_marker = self.lazy_loader.get_placeholder("face_marker")
        self.q_face_aligner = self.lazy_loader.get_placeholder("face_aligner")
        self.q_face_animator = self.lazy_loader.get_placeholder("face_animator")
        self.q_face_swap_insight = self.lazy_loader.get_placeholder("face_swap_insight")
        self.q_face_swap_dfm = self.lazy_loader.get_placeholder("face_swap_dfm")
        self.q_frame_adjuster = self.lazy_loader.get_placeholder("frame_adjuster")
        self.q_face_merger = self.lazy_loader.get_placeholder("face_merger")
        self.q_stream_output = self.lazy_loader.get_placeholder("stream_output")
        self.q_voice_changer = self.lazy_loader.get_placeholder("voice_changer")

        # Create viewer placeholders
        self.q_ds_frame_viewer = self.lazy_loader.get_placeholder("frame_viewer")
        self.q_ds_fa_viewer = self.lazy_loader.get_placeholder("fa_viewer")
        self.q_ds_fc_viewer = self.lazy_loader.get_placeholder("fc_viewer")
        self.q_ds_merged_frame_viewer = self.lazy_loader.get_placeholder(
            "merged_frame_viewer"
        )

    def _setup_layout(self):
        """Setup layout with direct UI components"""
        # Setup nodes layout with direct components
        q_nodes = qtx.QXWidgetHBox(
            [
                qtx.QXWidgetVBox(
                    [self.q_file_source, self.q_camera_source],
                    spacing=5,
                    fixed_width=256,
                ),
                qtx.QXWidgetVBox(
                    [self.q_face_detector, self.q_face_aligner],
                    spacing=5,
                    fixed_width=256,
                ),
                qtx.QXWidgetVBox(
                    [
                        self.q_face_marker,
                        self.q_face_animator,
                        self.q_face_swap_insight,
                        self.q_face_swap_dfm,
                    ],
                    spacing=5,
                    fixed_width=256,
                ),
                qtx.QXWidgetVBox(
                    [self.q_frame_adjuster, self.q_face_merger, self.q_stream_output],
                    spacing=5,
                    fixed_width=256,
                ),
                qtx.QXWidgetVBox([self.q_voice_changer], spacing=5, fixed_width=300),
            ],
            spacing=5,
            size_policy=("fixed", "fixed"),
        )

        # Setup viewers layout
        q_view_nodes = qtx.QXWidgetHBox(
            [
                (
                    qtx.QXWidgetVBox([self.q_ds_frame_viewer], fixed_width=256),
                    qtx.AlignTop,
                ),
                (
                    qtx.QXWidgetVBox([self.q_ds_fa_viewer], fixed_width=256),
                    qtx.AlignTop,
                ),
                (
                    qtx.QXWidgetVBox([self.q_ds_fc_viewer], fixed_width=256),
                    qtx.AlignTop,
                ),
                (
                    qtx.QXWidgetVBox([self.q_ds_merged_frame_viewer], fixed_width=256),
                    qtx.AlignTop,
                ),
            ],
            spacing=5,
            size_policy=("fixed", "fixed"),
        )

        # Performance info widget
        self.performance_label = QXLabel(
            text="Performance: Initializing...",
            font=QXFontDB.get_fixedwidth_font(size=8),
        )

        # Main layout
        self.setLayout(
            qtx.QXVBoxLayout(
                [
                    (
                        qtx.QXWidgetVBox([q_nodes, q_view_nodes], spacing=5),
                        qtx.AlignCenter,
                    ),
                    (self.performance_label, qtx.AlignCenter),
                ]
            )
        )

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

            # Update performance display with lazy loading info
            stats = (
                self.lazy_loader.get_stats()
                if hasattr(self, "lazy_loader")
                else {"loaded_components": 0, "total_components": 0}
            )
            loaded_components = stats.get("loaded_components", 0)
            total_components = stats.get("total_components", 0)
            perf_text = f"FPS: {self.current_fps:.1f} | Lazy Loading: {loaded_components}/{total_components} | Optimized Mode Active"
            self.performance_label.setText(perf_text)

    def _on_timer_10ms(self):
        """Optimized timer callback"""
        self._process_messages()

    def clear_backend_db(self):
        """Clear backend database"""
        self.backend_db.clear()

    def initialize(self):
        """Initialize with optimized startup"""
        self.logger.info("Starting optimized initialization...")

        for bcknd in self.all_backends:
            default_state = True
            if isinstance(
                bcknd,
                (backend.CameraSource, backend.FaceAnimator, backend.FaceSwapInsight),
            ):
                default_state = False
            bcknd.restore_on_off_state(default_state=default_state)

        self.logger.info("Optimized initialization completed")

        # Preload essential components for better performance
        self._preload_essential_components()

    def _preload_essential_components(self):
        """Preload essential components for better performance"""
        try:
            self.logger.info("Preloading essential components...")

            # Preload core components that are commonly used
            essential_components = [
                "face_detector",
                "face_aligner",
                "face_merger",
                "stream_output",
            ]

            for component_name in essential_components:
                try:
                    self.lazy_loader.preload_component(component_name)
                    self.logger.debug(f"Preloaded component: {component_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to preload {component_name}: {e}")

            self.logger.info("Essential components preloaded")

        except Exception as e:
            self.logger.warning(f"Error during component preloading: {e}")

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

        # Clear viewers with lazy loading support
        try:
            if hasattr(self.q_ds_frame_viewer, "clear"):
                self.q_ds_frame_viewer.clear()
            if hasattr(self.q_ds_fa_viewer, "clear"):
                self.q_ds_fa_viewer.clear()
        except Exception as e:
            self.logger.warning(f"Error clearing viewers: {e}")

        # Cleanup lazy loader
        if hasattr(self, "lazy_loader"):
            try:
                self.lazy_loader.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up lazy loader: {e}")

        # Cleanup completed

        self.logger.info("Optimized application finalization completed")


class QOptimizedDFLAppWindow(qtx.QXWindow):
    """Optimized DeepFaceLive application window"""

    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=("minimum", "minimum"))

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
            db_key="_QOptimizedDFLAppWindow_process_priority",
            choices=[lib_os.ProcessPriority.NORMAL, lib_os.ProcessPriority.IDLE],
            default_choice=lib_os.ProcessPriority.NORMAL,
            choices_names=[
                L("@QDFLAppWindow.process_priority.normal"),
                L("@QDFLAppWindow.process_priority.lowest"),
            ],
            on_choice_selected=self._on_cb_process_priority_choice,
        )

        menu_bar_tail = qtx.QXFrameHBox(
            [
                10,
                QXLabel(text=L("@QDFLAppWindow.process_priority")),
                4,
                cb_process_priority,
            ],
            size_policy=("fixed", "fixed"),
        )

        self.setLayout(
            qtx.QXVBoxLayout(
                [
                    qtx.QXWidgetHBox(
                        [self.menu_bar, menu_bar_tail, qtx.QXFrame()],
                        size_policy=("minimumexpanding", "fixed"),
                    ),
                    5,
                    qtx.QXWidget(layout=self.content_l),
                ]
            )
        )

        self.call_on_closeEvent(self._on_closeEvent)

    def _setup_menu_bar(self):
        """Setup menu bar with optimized options"""
        self.menu_bar = qtx.QXMenuBar(
            font=QXFontDB.get_default_font(size=10),
            size_policy=("fixed", "minimumexpanding"),
        )

        menu_file = self.menu_bar.addMenu(L("@QDFLAppWindow.file"))
        menu_language = self.menu_bar.addMenu(L("@QDFLAppWindow.language"))
        menu_performance = self.menu_bar.addMenu("Performance")

        # File menu
        menu_file_action_reinitialize = menu_file.addAction(
            L("@QDFLAppWindow.reinitialize")
        )
        menu_file_action_reinitialize.triggered.connect(
            lambda: qtx.QXMainApplication.inst.reinitialize()
        )

        menu_file_action_reset_settings = menu_file.addAction(
            L("@QDFLAppWindow.reset_modules_settings")
        )
        menu_file_action_reset_settings.triggered.connect(
            self._on_reset_modules_settings
        )

        menu_file_action_quit = menu_file.addAction(L("@QDFLAppWindow.quit"))
        menu_file_action_quit.triggered.connect(lambda: qtx.QXMainApplication.quit())

        # Language menu
        languages = [
            ("English", "en-US"),
            ("Español", "es-ES"),
            ("Italiano", "it-IT"),
            ("Русский", "ru-RU"),
            ("汉语", "zh-CN"),
            ("日本語", "ja-JP"),
        ]

        for lang_name, lang_code in languages:
            action = menu_language.addAction(lang_name)
            action.triggered.connect(
                lambda checked, code=lang_code: (
                    qtx.QXMainApplication.inst.set_language(code),
                    qtx.QXMainApplication.inst.reinitialize(),
                )
            )

        # Performance menu
        menu_performance_action_stats = menu_performance.addAction(
            "Show Performance Stats"
        )
        menu_performance_action_stats.triggered.connect(self._show_performance_stats)

        menu_performance_action_optimize = menu_performance.addAction(
            "Optimize Performance"
        )
        menu_performance_action_optimize.triggered.connect(self._optimize_performance)

        # Help menu
        menu_help = self.menu_bar.addMenu(L("@QDFLAppWindow.help"))
        menu_help_action_github = menu_help.addAction(
            L("@QDFLAppWindow.visit_github_page")
        )
        menu_help_action_github.triggered.connect(
            lambda: qtx.QDesktopServices.openUrl(
                qtx.QUrl("https://github.com/iperov/DeepFaceLive")
            )
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
        if self.q_live_swap and hasattr(self.q_live_swap, "ui_manager"):
            stats = self.q_live_swap.ui_manager.get_performance_stats()
            stats_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])

            # Show in a simple dialog
            from PyQt5.QtWidgets import QMessageBox

            msg = QMessageBox()
            msg.setWindowTitle("Performance Statistics")
            msg.setText(stats_text)
            msg.exec()

    def _optimize_performance(self):
        """Trigger performance optimization"""
        if self.q_live_swap and hasattr(self.q_live_swap, "ui_manager"):
            self.q_live_swap.ui_manager.optimize_for_performance(target_fps=30)
            self.logger.info("Performance optimization triggered")

    def finalize(self):
        """Finalize the application"""
        if self.q_live_swap:
            self.q_live_swap.finalize()

    def _on_closeEvent(self):
        """Handle close event"""
        self.finalize()


class OptimizedPlayaTewsIdentityMaskerApp(qtx.QXMainApplication):
    """Optimized DeepFaceLive application"""

    def __init__(self, userdata_path):
        super().__init__(
            app_name="PlayaTewsIdentityMasker",
            settings_dirpath=userdata_path / "settings",
        )

        self.userdata_path = userdata_path
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Optimized DeepFaceLive Application...")

        # Set up localization
        Localization.set_language(self.get_language())

        # Create main window
        self.main_window = QOptimizedDFLAppWindow(
            userdata_path=userdata_path, settings_dirpath=userdata_path / "settings"
        )

        # Initialize live swap
        self.main_window.q_live_swap = QOptimizedLiveSwap(
            userdata_path=userdata_path, settings_dirpath=userdata_path / "settings"
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

        if hasattr(self.main_window, "q_live_swap"):
            self.main_window.q_live_swap.finalize()

        # Recreate live swap
        self.main_window.q_live_swap = QOptimizedLiveSwap(
            userdata_path=self.userdata_path,
            settings_dirpath=self.userdata_path / "settings",
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
        if hasattr(self.main_window, "q_live_swap"):
            self.main_window.q_live_swap.finalize()

    def _on_splash_wnd_expired(self):
        """Handle splash window expiration"""
        pass
