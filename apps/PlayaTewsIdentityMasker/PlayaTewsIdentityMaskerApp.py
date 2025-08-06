"""
PlayaTewsIdentityMasker - Professional Face-Swapping & Streaming Application

This application is built upon the excellent work of the open source community:

Core Technologies Used:
- DeepFaceLive by @iperov
  (https://github.com/iperov/DeepFaceLive.git): Real-time face swap technology
- DeepFaceLab by @iperov
  (https://github.com/iperov/DeepFaceLab): Face model training framework
- Voice Changer Technology: Real-time audio processing and effects

For full attribution details, see CREDITS_AND_ATTRIBUTIONS.md

License: GPL-3.0 (based on DeepFaceLive)
"""

from pathlib import Path
from typing import List, Optional
from xlib import os as lib_os
from xlib import qt as qtx

from apps.PlayaTewsIdentityMasker import backend
from apps.PlayaTewsIdentityMasker.ui.QCameraSource import QCameraSource
from apps.PlayaTewsIdentityMasker.ui.QFaceAligner import QFaceAligner
from apps.PlayaTewsIdentityMasker.ui.QFaceAnimator import QFaceAnimator
from apps.PlayaTewsIdentityMasker.ui.QFaceDetector import QFaceDetector
from apps.PlayaTewsIdentityMasker.ui.QFaceMarker import QFaceMarker
from apps.PlayaTewsIdentityMasker.ui.QFaceMerger import QFaceMerger
from apps.PlayaTewsIdentityMasker.ui.QFaceSwapDFM import QFaceSwapDFM
from apps.PlayaTewsIdentityMasker.ui.QFaceSwapInsight import QFaceSwapInsight
from apps.PlayaTewsIdentityMasker.ui.QFileSource import QFileSource
from apps.PlayaTewsIdentityMasker.ui.QFrameAdjuster import QFrameAdjuster
from apps.PlayaTewsIdentityMasker.ui.QUnifiedLiveSwap import (
    QUnifiedLiveSwap, UIMode
)
from apps.PlayaTewsIdentityMasker.ui.QVoiceChanger import QVoiceChanger
from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceAlignViewer import (
    QBCFaceAlignViewer,
)
from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFaceSwapViewer import (
    QBCFaceSwapViewer,
)
from apps.PlayaTewsIdentityMasker.ui.widgets.QBCFrameViewer import (
    QBCFrameViewer,
)
from apps.PlayaTewsIdentityMasker.ui.widgets.QBCMergedFrameViewer import (
    QBCMergedFrameViewer,
)
from localization.localization import Localization

# Import enhanced components
from apps.PlayaTewsIdentityMasker.backend.MemoryOptimizedFaceSwap import (
    MemoryOptimizedFaceSwap,
)
from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import (
    EnhancedStreamOutput,
)
from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger
from apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput import (
    QEnhancedStreamOutput,
)


class QLiveSwap(qtx.QXWidget):
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()

        dfm_models_path = userdata_path / "dfm_models"
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / "animatables"
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / "output_sequence"
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config with increased memory allocation
        backend_db = self.backend_db = backend.BackendDB(
            settings_dirpath / "states.dat"
        )
        backend_weak_heap = self.backend_weak_heap = (
            backend.BackendWeakHeap(size_mb=4096)
        )  # Increased to 4GB for memory optimization
        reemit_frame_signal = self.reemit_frame_signal = (
            backend.BackendSignal()
        )

        multi_sources_bc_out = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out = backend.BackendConnection()
        face_marker_bc_out = backend.BackendConnection()
        face_aligner_bc_out = backend.BackendConnection()
        face_swapper_bc_out = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out = backend.BackendConnection()

        file_source = self.file_source = backend.FileSource(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_out=multi_sources_bc_out,
            backend_db=backend_db,
        )
        camera_source = self.camera_source = backend.CameraSource(
            weak_heap=backend_weak_heap,
            bc_out=multi_sources_bc_out,
            backend_db=backend_db,
        )
        face_detector = self.face_detector = backend.FaceDetector(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=multi_sources_bc_out,
            bc_out=face_detector_bc_out,
            backend_db=backend_db,
        )
        face_marker = self.face_marker = backend.FaceMarker(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_detector_bc_out,
            bc_out=face_marker_bc_out,
            backend_db=backend_db,
        )
        face_aligner = self.face_aligner = backend.FaceAligner(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_marker_bc_out,
            bc_out=face_aligner_bc_out,
            backend_db=backend_db,
        )
        face_animator = self.face_animator = backend.FaceAnimator(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_merger_bc_out,
            animatables_path=animatables_path,
            backend_db=backend_db,
        )
        face_swap_insight = self.face_swap_insight = backend.FaceSwapInsight(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_swapper_bc_out,
            faces_path=animatables_path,
            backend_db=backend_db,
        )

        # Use Memory-Optimized Face Swap DFM for better performance
        try:
            face_swap_dfm = MemoryOptimizedFaceSwap(
                weak_heap=backend_weak_heap,
                reemit_frame_signal=reemit_frame_signal,
                bc_in=face_aligner_bc_out,
                bc_out=face_swapper_bc_out,
                dfm_models_path=dfm_models_path,
                backend_db=backend_db,
            )
            self.face_swap_dfm = face_swap_dfm
            print("🧠 Memory-optimized face swap backend loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load memory-optimized backend: {e}")
            print("   Falling back to standard face swap backend")
            face_swap_dfm = backend.FaceSwapDFM(
                weak_heap=backend_weak_heap,
                reemit_frame_signal=reemit_frame_signal,
                bc_in=face_aligner_bc_out,
                bc_out=face_swapper_bc_out,
                dfm_models_path=dfm_models_path,
                backend_db=backend_db,
            )  # type: ignore
            self.face_swap_dfm = face_swap_dfm
            # Type cast for compatibility
            face_swap_dfm = self.face_swap_dfm  # type: ignore

        frame_adjuster = self.frame_adjuster = backend.FrameAdjuster(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_swapper_bc_out,
            bc_out=frame_adjuster_bc_out,
            backend_db=backend_db,
        )
        face_merger = self.face_merger = backend.FaceMerger(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=frame_adjuster_bc_out,
            bc_out=face_merger_bc_out,
            backend_db=backend_db,
        )

        # Use enhanced streaming output for OBS-style functionality
        stream_output = self.stream_output = EnhancedStreamOutput(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_merger_bc_out,
            save_default_path=userdata_path,
            backend_db=backend_db,
        )

        # Add voice changer backend
        voice_changer = self.voice_changer = VoiceChanger(
            weak_heap=backend_weak_heap, backend_db=backend_db
        )

        self.all_backends: List[backend.BackendHost] = [
            file_source,
            camera_source,
            face_detector,
            face_marker,
            face_aligner,
            face_animator,
            face_swap_insight,
            face_swap_dfm,
            frame_adjuster,
            face_merger,
            stream_output,
            voice_changer,
        ]

        self.q_file_source = QFileSource(self.file_source)
        self.q_camera_source = QCameraSource(self.camera_source)
        self.q_face_detector = QFaceDetector(self.face_detector)
        self.q_face_marker = QFaceMarker(self.face_marker)
        self.q_face_aligner = QFaceAligner(self.face_aligner)
        self.q_face_animator = QFaceAnimator(
            self.face_animator, animatables_path=animatables_path
        )
        self.q_face_swap_insight = QFaceSwapInsight(
            self.face_swap_insight, faces_path=animatables_path
        )
        self.q_face_swap_dfm = QFaceSwapDFM(
            face_swap_dfm, dfm_models_path=dfm_models_path  # type: ignore
        )
        self.q_frame_adjuster = QFrameAdjuster(self.frame_adjuster)
        self.q_face_merger = QFaceMerger(self.face_merger)

        # Use enhanced streaming output UI
        self.q_stream_output = QEnhancedStreamOutput(self.stream_output)

        # Add voice changer UI (optional - skip if there are issues)
        self.q_voice_changer: Optional[QVoiceChanger] = None
        try:
            self.q_voice_changer = QVoiceChanger(
                self.voice_changer.get_control_sheet()
            )
            print("✅ Voice changer UI created successfully")
        except Exception as e:
            print(f"⚠️ Voice changer UI creation failed: {e}")
            print("   Continuing without voice changer UI")

        self.q_ds_frame_viewer = QBCFrameViewer(
            backend_weak_heap, multi_sources_bc_out
        )
        self.q_ds_fa_viewer = QBCFaceAlignViewer(
            backend_weak_heap, face_aligner_bc_out,
            preview_width=256
        )
        self.q_ds_fc_viewer = QBCFaceSwapViewer(
            backend_weak_heap, face_merger_bc_out,
            preview_width=256
        )
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(
            backend_weak_heap, face_merger_bc_out
        )

        # Configure memory optimization settings if using
        # memory-optimized backend
        self._configure_memory_optimization()

        # Create unified live swap UI
        self.q_unified_live_swap = QUnifiedLiveSwap(
            UIMode.OBS_STYLE,
            self.q_file_source,
            self.q_camera_source,
            self.q_face_detector,
            self.q_face_marker,
            self.q_face_aligner,
            self.q_face_animator,
            self.q_face_swap_insight,
            self.q_face_swap_dfm,
            self.q_frame_adjuster,
            self.q_face_merger,
            self.q_stream_output,
            self.q_voice_changer,
            self.q_ds_frame_viewer,
            self.q_ds_fa_viewer,
            self.q_ds_fc_viewer,
            self.q_ds_merged_frame_viewer,
        )

        # Create main layout
        main_layout = qtx.QXVBoxLayout()
        main_layout.addWidget(self.q_unified_live_swap)
        self.setLayout(main_layout)

    def _configure_memory_optimization(self) -> None:
        """Configure memory optimization settings for the face swap DFM"""
        try:
            # Check if we're using the memory-optimized backend
            if hasattr(self.face_swap_dfm, "get_control_sheet"):
                cs = self.face_swap_dfm.get_control_sheet()

                # Check if memory optimization controls are available
                if hasattr(cs, "ram_cache_size"):
                    # Set memory optimization settings
                    # RAM Cache Size: 2GB (2048 MB)
                    # Can be increased to 4GB for your 64GB system
                    cs.ram_cache_size.set_number(2048)

                    # Enable preprocessing cache
                    if hasattr(cs, "enable_preprocessing_cache"):
                        cs.enable_preprocessing_cache.set_flag(True)

                    # Enable postprocessing cache
                    if hasattr(cs, "enable_postprocessing_cache"):
                        cs.enable_postprocessing_cache.set_flag(True)

                    # Enable parallel processing
                    if hasattr(cs, "parallel_processing"):
                        cs.parallel_processing.set_flag(True)

                    print("🧠 Memory Optimization Configured:")
                    print("  • RAM Cache Size: 2GB")
                    print("  • Preprocessing Cache: Enabled")
                    print("  • Postprocessing Cache: Enabled")
                    print("  • Parallel Processing: Enabled")
                else:
                    print(
                        "ℹ️  Standard face swap backend - "
                        "memory optimization not available"
                    )
            else:
                print(
                    "ℹ️  Standard face swap backend - "
                    "memory optimization not available"
                )

        except Exception as e:
            print(f"⚠️ Warning: Could not configure memory optimization: {e}")

    def _process_messages(self) -> None:
        self.q_unified_live_swap._process_messages()

    def _on_timer_5ms(self) -> None:
        try:
            if hasattr(self, 'q_unified_live_swap'):
                self.q_unified_live_swap._on_timer_5ms()
        except Exception as e:
            print(f"⚠️ Timer processing failed: {e}")

    def clear_backend_db(self) -> None:
        self.backend_db.clear()

    def initialize(self) -> None:
        # Initialize all backends
        for backend_host in self.all_backends:
            try:
                if hasattr(backend_host, 'initialize'):
                    backend_host.initialize()
                elif hasattr(backend_host, 'start'):
                    backend_host.start()
                else:
                    backend_name = type(backend_host).__name__
                    print(f"⚠️ Backend {backend_name} has no "
                          f"initialize/start method")
            except Exception as e:
                backend_name = type(backend_host).__name__
                print(f"⚠️ Failed to initialize {backend_name}: {e}")

    def finalize(self) -> None:
        # Gracefully stop the backend
        for backend_host in self.all_backends:
            try:
                if hasattr(backend_host, 'finalize'):
                    backend_host.finalize()
                elif hasattr(backend_host, 'stop'):
                    backend_host.stop()
                else:
                    backend_name = type(backend_host).__name__
                    print(f"⚠️ Backend {backend_name} has no "
                          f"finalize/stop method")
            except Exception as e:
                backend_name = type(backend_host).__name__
                print(f"⚠️ Failed to finalize {backend_name}: {e}")


class QDFLAppWindow(qtx.QXWindow):
    def __init__(
        self,
        userdata_path: Path,
        settings_dirpath: Path,
        q_file_source,
        q_camera_source,
        q_face_detector,
        q_face_marker,
        q_face_aligner,
        q_face_animator,
        q_face_swap_insight,
        q_face_swap_dfm,
        q_frame_adjuster,
        q_face_merger,
        q_stream_output,
        q_voice_changer: Optional[QVoiceChanger],
        q_ds_frame_viewer,
        q_ds_fa_viewer,
        q_ds_fc_viewer,
        q_ds_merged_frame_viewer,
    ) -> None:
        super().__init__()

        self.userdata_path = userdata_path
        self.settings_dirpath = settings_dirpath

        # Store UI components
        self.q_file_source = q_file_source
        self.q_camera_source = q_camera_source
        self.q_face_detector = q_face_detector
        self.q_face_marker = q_face_marker
        self.q_face_aligner = q_face_aligner
        self.q_face_animator = q_face_animator
        self.q_face_swap_insight = q_face_swap_insight
        self.q_face_swap_dfm = q_face_swap_dfm
        self.q_frame_adjuster = q_frame_adjuster
        self.q_face_merger = q_face_merger
        self.q_stream_output = q_stream_output
        self.q_voice_changer = q_voice_changer
        self.q_ds_frame_viewer = q_ds_frame_viewer
        self.q_ds_fa_viewer = q_ds_fa_viewer
        self.q_ds_fc_viewer = q_ds_fc_viewer
        self.q_ds_merged_frame_viewer = q_ds_merged_frame_viewer

        # Set window properties
        self.setWindowTitle("PlayaTews Identity Masker")
        self.setMinimumSize(1200, 800)

        # Create menu bar
        self.create_menu_bar()

        # Create main layout with all UI components
        main_layout = qtx.QXHBoxLayout()

        # Left panel - Main controls
        left_panel = qtx.QXVBoxLayout()
        left_panel.addWidget(self.q_file_source)
        left_panel.addWidget(self.q_camera_source)
        left_panel.addWidget(self.q_face_detector)
        left_panel.addWidget(self.q_face_marker)
        left_panel.addWidget(self.q_face_aligner)
        left_panel.addWidget(self.q_face_animator)
        left_panel.addWidget(self.q_face_swap_insight)
        left_panel.addWidget(self.q_face_swap_dfm)
        left_panel.addWidget(self.q_frame_adjuster)
        left_panel.addWidget(self.q_face_merger)
        left_panel.addWidget(self.q_stream_output)

        if self.q_voice_changer is not None:
            left_panel.addWidget(self.q_voice_changer)

        left_panel.addStretch()

        # Right panel - Preview windows
        right_panel = qtx.QXVBoxLayout()
        right_panel.addWidget(self.q_ds_frame_viewer)
        right_panel.addWidget(self.q_ds_fa_viewer)
        right_panel.addWidget(self.q_ds_fc_viewer)
        right_panel.addWidget(self.q_ds_merged_frame_viewer)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 1)

        # Set main layout
        central_widget = qtx.QXWidget()
        central_widget.setLayout(main_layout)
        try:
            self.setCentralWidget(central_widget)
        except Exception as e:
            print(f"⚠️ setCentralWidget failed: {e}")
            # Fallback: set as main widget
            self.setLayout(main_layout)

        # Create timer for processing
        try:
            self.timer_5ms = qtx.QXTimer()
            self.timer_5ms.timeout.connect(self._on_timer_5ms)
            self.timer_5ms.start(5)
        except Exception as e:
            print(f"⚠️ Timer creation failed: {e}")
            self.timer_5ms = None  # type: ignore

    def create_menu_bar(self) -> None:
        """Create the application menu bar"""
        try:
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("&File")
            reset_action = file_menu.addAction("Reset All Settings")
            reset_action.triggered.connect(self._on_reset_modules_settings)

            # Tools menu
            tools_menu = menubar.addMenu("&Tools")
            memory_action = tools_menu.addAction("Start Memory Monitor")
            memory_action.triggered.connect(self._on_start_memory_monitor)
            report_action = tools_menu.addAction("Generate Memory Report")
            report_action.triggered.connect(self._on_generate_memory_report)

            # Cache menu
            cache_menu = menubar.addMenu("&Cache")
            clear_action = cache_menu.addAction("Clear All Caches")
            clear_action.triggered.connect(self._on_clear_all_caches)
            optimize_action = cache_menu.addAction("Optimize Cache Size")
            optimize_action.triggered.connect(self._on_optimize_cache_size)

            # Help menu
            help_menu = menubar.addMenu("&Help")
            guide_action = help_menu.addAction("Memory Optimization Guide")
            guide_action.triggered.connect(self._on_show_memory_guide)
            tips_action = help_menu.addAction("Performance Tips")
            tips_action.triggered.connect(self._on_show_performance_tips)
        except Exception as e:
            print(f"⚠️ Menu bar creation failed: {e}")
            print("   Continuing without menu bar")

    def _on_reset_modules_settings(self) -> None:
        """Reset all module settings to defaults"""
        try:
            # Reset settings for all modules
            modules = [
                self.q_file_source, self.q_camera_source, self.q_face_detector,
                self.q_face_marker, self.q_face_aligner, self.q_face_animator,
                self.q_face_swap_insight, self.q_face_swap_dfm,
                self.q_frame_adjuster, self.q_face_merger, self.q_stream_output
            ]
            for module in modules:
                if hasattr(module, 'reset_settings'):
                    module.reset_settings()
            print("✅ All module settings reset to defaults")
        except Exception as e:
            print(f"❌ Could not reset settings: {e}")

    def _on_start_memory_monitor(self) -> None:
        """Start memory monitoring"""
        try:
            import psutil  # type: ignore
            process = psutil.Process()
            memory_info = process.memory_info()
            print("🧠 Current Memory Usage:")
            print(f"  • RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
            print(f"  • VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
            print(f"  • Percent: {process.memory_percent():.1f}%")
        except Exception as e:
            print(f"❌ Could not get memory info: {e}")

    def _on_generate_memory_report(self) -> None:
        """Generate detailed memory report"""
        try:
            import psutil  # type: ignore
            process = psutil.Process()
            memory_info = process.memory_info()
            print("📊 Memory Report:")
            rss_mb = memory_info.rss / 1024 / 1024
            vms_mb = memory_info.vms / 1024 / 1024
            print(f"  • Resident Set Size: {rss_mb:.1f} MB")
            print(f"  • Virtual Memory Size: {vms_mb:.1f} MB")
            print(f"  • Memory Percent: {process.memory_percent():.1f}%")
            print(f"  • CPU Percent: {process.cpu_percent():.1f}%")
            print(f"  • Threads: {process.num_threads()}")
        except Exception as e:
            print(f"❌ Could not generate memory report: {e}")

    def _on_clear_all_caches(self) -> None:
        """Clear all caches"""
        try:
            # Clear caches for all modules
            modules = [
                self.q_file_source, self.q_camera_source, self.q_face_detector,
                self.q_face_marker, self.q_face_aligner, self.q_face_animator,
                self.q_face_swap_insight, self.q_face_swap_dfm,
                self.q_frame_adjuster, self.q_face_merger, self.q_stream_output
            ]
            for module in modules:
                if hasattr(module, 'clear_cache'):
                    module.clear_cache()
            print("✅ All caches cleared")
        except Exception as e:
            print(f"❌ Could not clear caches: {e}")

    def _on_optimize_cache_size(self) -> None:
        """Optimize cache sizes for better performance"""
        try:
            # Optimize cache sizes for modules that support it
            modules = [
                self.q_face_swap_dfm, self.q_face_detector,
                self.q_face_aligner, self.q_stream_output
            ]
            for module in modules:
                if hasattr(module, 'optimize_cache'):
                    module.optimize_cache()
            print("✅ Cache sizes optimized")
        except Exception as e:
            print(f"❌ Could not optimize caches: {e}")

    def _on_show_memory_guide(self) -> None:
        """Show memory optimization guide"""
        try:
            guide_text = """
🧠 Memory Optimization Guide

1. RAM Cache Size: Set to 2-4GB for optimal performance
2. Enable preprocessing cache for faster face detection
3. Enable postprocessing cache for smoother output
4. Use parallel processing when available
5. Monitor memory usage with Tools > Memory Monitor
6. Clear caches regularly if memory usage is high

For 64GB systems, you can safely use 4GB RAM cache.
            """
            print(guide_text)
        except Exception as e:
            print(f"❌ Could not show memory guide: {e}")

    def _on_show_performance_tips(self) -> None:
        """Show performance optimization tips"""
        try:
            tips_text = """
⚡ Performance Optimization Tips

1. Use SSD storage for faster file operations
2. Enable GPU acceleration when available
3. Close unnecessary applications
4. Use appropriate face detection models
5. Optimize video resolution for your needs
6. Monitor CPU and memory usage
7. Use the memory optimization features
            """
            print(tips_text)
        except Exception as e:
            print(f"❌ Could not show performance tips: {e}")

    def _on_cb_process_priority_choice(
        self, prio: lib_os.ProcessPriority, _: object
    ) -> None:
        """Handle process priority changes"""
        try:
            import psutil  # type: ignore

            current_process = psutil.Process()
            if prio == lib_os.ProcessPriority.HIGH:
                current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            elif prio == lib_os.ProcessPriority.NORMAL:
                current_process.nice(psutil.NORMAL_PRIORITY_CLASS)
            elif prio == lib_os.ProcessPriority.BELOW_NORMAL:
                current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            print(f"🎯 Process priority set to {prio.name}")
        except Exception as e:
            print(f"❌ Could not set process priority: {e}")

    def finalize(self) -> None:
        """Finalize the application"""
        if hasattr(self, "timer_5ms") and self.timer_5ms is not None:
            try:
                self.timer_5ms.stop()
            except Exception as e:
                print(f"⚠️ Timer stop failed: {e}")

    def _on_closeEvent(self) -> None:
        """Handle window close event"""
        self.finalize()
        self.close()


class PlayaTewsIdentityMaskerApp(qtx.QXMainApplication):
    def __init__(self, userdata_path: Path) -> None:
        super().__init__()
        self.userdata_path = userdata_path
        self.settings_dirpath = userdata_path / "settings"
        self.settings_dirpath.mkdir(parents=True, exist_ok=True)

        # Initialize localization
        Localization.set_language("en-US")

        # Fonts and images are loaded on demand (no initialization needed)

        # Create QLiveSwap instance first to get all UI components
        self.q_live_swap = QLiveSwap(userdata_path, self.settings_dirpath)

        # Create main window with UI components from QLiveSwap
        self.main_window = QDFLAppWindow(
            userdata_path,
            self.settings_dirpath,
            self.q_live_swap.q_file_source,
            self.q_live_swap.q_camera_source,
            self.q_live_swap.q_face_detector,
            self.q_live_swap.q_face_marker,
            self.q_live_swap.q_face_aligner,
            self.q_live_swap.q_face_animator,
            self.q_live_swap.q_face_swap_insight,
            self.q_live_swap.q_face_swap_dfm,
            self.q_live_swap.q_frame_adjuster,
            self.q_live_swap.q_face_merger,
            self.q_live_swap.q_stream_output,
            self.q_live_swap.q_voice_changer,
            self.q_live_swap.q_ds_frame_viewer,
            self.q_live_swap.q_ds_fa_viewer,
            self.q_live_swap.q_ds_fc_viewer,
            self.q_live_swap.q_ds_merged_frame_viewer,
        )

        # Don't automatically show splash screen or window
        # Let the launcher handle window display

    def initialize(self) -> None:
        """Initialize the application"""
        try:
            # Initialize the QLiveSwap instance
            if hasattr(self, 'q_live_swap'):
                self.q_live_swap.initialize()
                print("✅ QLiveSwap initialized successfully")

            # Initialize the main window
            if hasattr(self, 'main_window'):
                self.main_window.show()
                print("✅ Main window displayed successfully")

            print("✅ PlayaTewsIdentityMaskerApp initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing application: {e}")
            raise

    def run(self) -> int:
        """Run the application"""
        try:
            # Start the Qt event loop
            return self.exec_()
        except Exception as e:
            print(f"❌ Error running application: {e}")
            raise
