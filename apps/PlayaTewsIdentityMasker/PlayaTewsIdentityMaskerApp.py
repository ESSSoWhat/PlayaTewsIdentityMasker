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
<<<<<<< Updated upstream
from typing import List
from xlib import qt as qtx
=======
from typing import List, Optional
>>>>>>> Stashed changes

from xlib import os as lib_os
from xlib import qt as qtx

<<<<<<< Updated upstream
from . import backend
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
from .ui.QVoiceChanger import QVoiceChanger
from .ui.QUnifiedLiveSwap import QUnifiedLiveSwap, UIMode
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer
=======
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
from apps.PlayaTewsIdentityMasker.ui.QUnifiedLiveSwap import QUnifiedLiveSwap, UIMode
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

# Break up long import lines
from apps.PlayaTewsIdentityMasker.backend.MemoryOptimizedFaceSwap import (
    MemoryOptimizedFaceSwap,
)
from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import (
    EnhancedStreamOutput,
)
from apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput import (
    QEnhancedStreamOutput,
)
>>>>>>> Stashed changes


class QLiveSwap(qtx.QXWidget):
    def __init__(self, userdata_path : Path,
                       settings_dirpath : Path):
        super().__init__()

        dfm_models_path = userdata_path / 'dfm_models'
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / 'animatables'
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / 'output_sequence'
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config with increased memory allocation for optimization
        backend_db          = self.backend_db          = backend.BackendDB( settings_dirpath / 'states.dat' )
        backend_weak_heap   = self.backend_weak_heap   = backend.BackendWeakHeap(size_mb=4096)  # Increased to 4GB for memory optimization
        reemit_frame_signal = self.reemit_frame_signal = backend.BackendSignal()

        multi_sources_bc_out  = backend.BackendConnection(multi_producer=True)
        face_detector_bc_out  = backend.BackendConnection()
        face_marker_bc_out    = backend.BackendConnection()
        face_aligner_bc_out   = backend.BackendConnection()
        face_swapper_bc_out   = backend.BackendConnection()
        frame_adjuster_bc_out = backend.BackendConnection()
        face_merger_bc_out    = backend.BackendConnection()

        file_source    = self.file_source    = backend.FileSource   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_out=multi_sources_bc_out, backend_db=backend_db)
        camera_source  = self.camera_source  = backend.CameraSource (weak_heap=backend_weak_heap, bc_out=multi_sources_bc_out, backend_db=backend_db)
        face_detector  = self.face_detector  = backend.FaceDetector (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=multi_sources_bc_out, bc_out=face_detector_bc_out, backend_db=backend_db )
        face_marker    = self.face_marker    = backend.FaceMarker   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_detector_bc_out, bc_out=face_marker_bc_out, backend_db=backend_db)
        face_aligner   = self.face_aligner   = backend.FaceAligner  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_marker_bc_out, bc_out=face_aligner_bc_out, backend_db=backend_db )
        face_animator  = self.face_animator  = backend.FaceAnimator (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_merger_bc_out, animatables_path=animatables_path, backend_db=backend_db )
        face_swap_insight  = self.face_swap_insight  = backend.FaceSwapInsight (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, faces_path=animatables_path, backend_db=backend_db )
        
        # Use Memory-Optimized Face Swap DFM for better performance
        try:
<<<<<<< Updated upstream
            from .backend.MemoryOptimizedFaceSwap import MemoryOptimizedFaceSwap
            face_swap_dfm   = self.face_swap_dfm   = MemoryOptimizedFaceSwap  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, dfm_models_path=dfm_models_path, backend_db=backend_db )
=======
            face_swap_dfm = self.face_swap_dfm = MemoryOptimizedFaceSwap(
                weak_heap=backend_weak_heap,
                reemit_frame_signal=reemit_frame_signal,
                bc_in=face_aligner_bc_out,
                bc_out=face_swapper_bc_out,
                dfm_models_path=dfm_models_path,
                backend_db=backend_db,
            )
>>>>>>> Stashed changes
            print("🧠 Memory-optimized face swap backend loaded successfully")
        except Exception as e:
            print(f"⚠️ Could not load memory-optimized backend: {e}")
            print("   Falling back to standard face swap backend")
            face_swap_dfm   = self.face_swap_dfm   = backend.FaceSwapDFM  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, dfm_models_path=dfm_models_path, backend_db=backend_db )
        
        frame_adjuster = self.frame_adjuster = backend.FrameAdjuster(weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_swapper_bc_out, bc_out=frame_adjuster_bc_out, backend_db=backend_db )
        face_merger    = self.face_merger    = backend.FaceMerger   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=frame_adjuster_bc_out, bc_out=face_merger_bc_out, backend_db=backend_db )
        
        # Use enhanced streaming output for OBS-style functionality
<<<<<<< Updated upstream
        from .backend.EnhancedStreamOutput import EnhancedStreamOutput
        stream_output  = self.stream_output  = EnhancedStreamOutput (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_merger_bc_out, save_default_path=userdata_path, backend_db=backend_db)

        # Add voice changer backend
        from .backend.VoiceChanger import VoiceChanger
        voice_changer = self.voice_changer = VoiceChanger(weak_heap=backend_weak_heap, backend_db=backend_db)
=======
        stream_output = self.stream_output = EnhancedStreamOutput(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_merger_bc_out,
            save_default_path=userdata_path,
            backend_db=backend_db,
        )

        # Add voice changer backend
        from apps.PlayaTewsIdentityMasker.backend.VoiceChanger import VoiceChanger
>>>>>>> Stashed changes

        self.all_backends : List[backend.BackendHost] = [file_source, camera_source, face_detector, face_marker, face_aligner, face_animator, face_swap_insight, face_swap_dfm, frame_adjuster, face_merger, stream_output, voice_changer]

        self.q_file_source    = QFileSource(self.file_source)
        self.q_camera_source  = QCameraSource(self.camera_source)
        self.q_face_detector  = QFaceDetector(self.face_detector)
        self.q_face_marker    = QFaceMarker(self.face_marker)
        self.q_face_aligner   = QFaceAligner(self.face_aligner)
        self.q_face_animator  = QFaceAnimator(self.face_animator, animatables_path=animatables_path)
        self.q_face_swap_insight = QFaceSwapInsight(self.face_swap_insight, faces_path=animatables_path)
        self.q_face_swap_dfm  = QFaceSwapDFM(self.face_swap_dfm, dfm_models_path=dfm_models_path)
        self.q_frame_adjuster = QFrameAdjuster(self.frame_adjuster)
        self.q_face_merger    = QFaceMerger(self.face_merger)
        
        # Use enhanced streaming output UI
<<<<<<< Updated upstream
        from .ui.QEnhancedStreamOutput import QEnhancedStreamOutput
        self.q_stream_output  = QEnhancedStreamOutput(self.stream_output)
        
        # Add voice changer UI
        self.q_voice_changer = QVoiceChanger(self.voice_changer.get_control_sheet())
=======
        self.q_stream_output = QEnhancedStreamOutput(self.stream_output)

        # Add voice changer UI (optional - skip if there are issues)
        try:
            self.q_voice_changer = QVoiceChanger(self.voice_changer.get_control_sheet())
            print("✅ Voice changer UI created successfully")
        except Exception as e:
            print(f"⚠️ Voice changer UI creation failed: {e}")
            print("   Continuing without voice changer UI")
            self.q_voice_changer = None
>>>>>>> Stashed changes

        self.q_ds_frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out)
        self.q_ds_fa_viewer    = QBCFaceAlignViewer(backend_weak_heap, face_aligner_bc_out, preview_width=256)
        self.q_ds_fc_viewer    = QBCFaceSwapViewer(backend_weak_heap, face_merger_bc_out, preview_width=256)
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(backend_weak_heap, face_merger_bc_out)

        # Configure memory optimization settings if using memory-optimized backend
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
            self.q_ds_merged_frame_viewer
        )

        # Create main layout
        main_layout = qtx.QXVBoxLayout()
        main_layout.addWidget(self.q_unified_live_swap)
        self.setLayout(main_layout)

    def _configure_memory_optimization(self) -> None:
        """Configure memory optimization settings for the face swap DFM"""
        try:
            # Check if we're using the memory-optimized backend
            if hasattr(self.face_swap_dfm, 'get_control_sheet'):
                cs = self.face_swap_dfm.get_control_sheet()
                
                # Check if memory optimization controls are available
                if hasattr(cs, 'ram_cache_size'):
                    # Set memory optimization settings
                    # RAM Cache Size: 2GB (2048 MB)
                    # Can be increased to 4GB for your 64GB system
                    cs.ram_cache_size.set_number(2048)
                    
                    # Enable preprocessing cache
                    if hasattr(cs, 'enable_preprocessing_cache'):
                        cs.enable_preprocessing_cache.set_flag(True)
                    
                    # Enable postprocessing cache
                    if hasattr(cs, 'enable_postprocessing_cache'):
                        cs.enable_postprocessing_cache.set_flag(True)
                    
                    # Enable parallel processing
                    if hasattr(cs, 'parallel_processing'):
                        cs.parallel_processing.set_flag(True)
<<<<<<< Updated upstream
                    
                    print("🧠 Memory Optimization Configured:")
=======

                    print(
                        "🧠 Memory Optimization Configured:"
                    )
>>>>>>> Stashed changes
                    print("  • RAM Cache Size: 2GB")
                    print("  • Preprocessing Cache: Enabled")
                    print("  • Postprocessing Cache: Enabled")
                    print("  • Parallel Processing: Enabled")
                else:
                    print("ℹ️  Standard face swap backend - memory optimization not available")
            else:
                print("ℹ️  Standard face swap backend - memory optimization not available")
                
        except Exception as e:
            print(f"⚠️ Warning: Could not configure memory optimization: {e}")

    def _process_messages(self) -> None:
        self.q_unified_live_swap._process_messages()

    def _on_timer_5ms(self) -> None:
        self.q_unified_live_swap._on_timer_5ms()

    def clear_backend_db(self) -> None:
        self.backend_db.clear()

    def initialize(self) -> None:
        # Initialize all backends
        for backend_host in self.all_backends:
            backend_host.start()

    def finalize(self) -> None:
        # Gracefully stop the backend
        for backend_host in self.all_backends:
            backend_host.stop()


class QDFLAppWindow(qtx.QXWindow):
<<<<<<< Updated upstream
    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True)
=======
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

>>>>>>> Stashed changes
        self.userdata_path = userdata_path
        self.settings_dirpath = settings_dirpath

        # Create main widget
        self.q_live_swap = QLiveSwap(userdata_path, settings_dirpath)
        
        # Add the main widget to this window
        self.add_widget(self.q_live_swap)

        # Set window properties
        self.setWindowTitle("PlayaTewsIdentityMasker - Memory Optimized")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Set window icon
        try:
            from resources.gfx import QXImageDB
            icon = QXImageDB.app_icon()
            if icon:
                self.setWindowIcon(icon.as_QIcon())
        except Exception:
            pass

        # Create timer for processing messages
        self.timer_5ms = qtx.QXTimer(interval_ms=5, timeout=self.q_live_swap._on_timer_5ms)
        self.timer_5ms.start()

        # Initialize the application
        self.q_live_swap.initialize()

    def create_menu_bar(self) -> None:
        """Create menu bar with memory optimization options"""
        # Note: QXWindow doesn't have built-in menu bar support
        # Menu functionality can be implemented using custom widgets if needed
        pass

    def _on_reset_modules_settings(self) -> None:
        """Reset all module settings"""
        self.q_live_swap.clear_backend_db()
        print("✅ All module settings have been reset")

    def _on_start_memory_monitor(self) -> None:
        """Start memory monitoring"""
        try:
            import subprocess
            import sys
            subprocess.Popen([sys.executable, "monitor_memory_performance.py"])
            print("🧠 Memory monitoring started in new window")
        except Exception as e:
            print(f"❌ Could not start memory monitoring: {e}")

    def _on_generate_memory_report(self) -> None:
        """Generate memory optimization report"""
        try:
            import subprocess
            import sys
            subprocess.run([sys.executable, "test_memory_optimization.py"])
            print("📄 Memory optimization report generated")
        except Exception as e:
            print(f"❌ Could not generate memory report: {e}")

    def _on_clear_all_caches(self) -> None:
        """Clear all caches"""
        try:
            # Clear backend weak heap
            self.q_live_swap.backend_weak_heap.clear()
            
            # Clear face swap DFM caches if available
            if hasattr(self.q_live_swap.face_swap_dfm, 'ram_cache'):
                self.q_live_swap.face_swap_dfm.ram_cache.clear()
            
            print("🧹 All caches cleared")
        except Exception as e:
            print(f"❌ Could not clear caches: {e}")

    def _on_optimize_cache_size(self) -> None:
        """Optimize cache size based on available memory"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_ram_gb = memory.available / (1024**3)
            
            # Calculate optimal cache size (25% of available RAM, max 4GB)
            optimal_cache_gb = min(available_ram_gb * 0.25, 4.0)
            optimal_cache_mb = int(optimal_cache_gb * 1024)
            
            # Set the cache size if memory-optimized backend is available
            if hasattr(self.q_live_swap.face_swap_dfm, 'get_control_sheet'):
                cs = self.q_live_swap.face_swap_dfm.get_control_sheet()
                if hasattr(cs, 'ram_cache_size'):
                    cs.ram_cache_size.set_number(optimal_cache_mb)
                    print(f"📦 Cache size optimized to {optimal_cache_mb}MB ({optimal_cache_gb:.1f}GB)")
                else:
                    print("ℹ️  Memory optimization not available in current backend")
            else:
                print("ℹ️  Memory optimization not available in current backend")
        except Exception as e:
            print(f"❌ Could not optimize cache size: {e}")

    def _on_show_memory_guide(self) -> None:
        """Show memory optimization guide"""
        try:
            import webbrowser
<<<<<<< Updated upstream
            import os
            guide_path = os.path.abspath("MEMORY_OPTIMIZATION_GUIDE.md")
            webbrowser.open(f"file://{guide_path}")
        except Exception as e:
            print(f"❌ Could not open memory guide: {e}")

    def _on_show_performance_tips(self):
        """Show performance tips"""
        tips = """
🚀 Performance Tips for Memory-Optimized Face Swap:
=======

            webbrowser.open(
                "https://github.com/PlayaTews/PlayaTewsIdentityMasker/wiki/Memory-Optimization"
            )
            print(
                "📖 Memory optimization guide opened in browser"
            )
        except Exception as e:
            print(f"❌ Could not open memory guide: {e}")

    def _on_show_performance_tips(self) -> None:
        """Show performance optimization tips"""
        try:
            import webbrowser
>>>>>>> Stashed changes

1. 🧠 RAM Usage:
   • Keep RAM usage below 80%
   • Monitor cache hit rates (should be 70-90%)
   • Adjust cache size based on available RAM

<<<<<<< Updated upstream
2. 📦 Cache Optimization:
   • Enable preprocessing cache for 30-50% CPU reduction
   • Enable postprocessing cache for 20-40% CPU reduction
   • Use 2GB cache for optimal performance

3. ⚡ Performance Settings:
   • Enable parallel processing for multi-core systems
   • Monitor FPS (should be 25+ for smooth operation)
   • Watch processing times (should decrease with caching)

4. 🔧 System Optimization:
   • Close unnecessary applications
   • Ensure adequate free disk space
   • Keep system drivers updated

5. 📊 Monitoring:
   • Use the Memory Monitor to track performance
   • Generate reports to analyze optimization
   • Adjust settings based on your specific use case
        """
        print(tips)

    def _on_cb_process_priority_choice(self, prio : lib_os.ProcessPriority, _):
        """Set process priority"""
        lib_os.set_process_priority(prio)
        print(f"✅ Process priority set to: {prio.name}")
=======
    def _on_cb_process_priority_choice(
        self, prio: lib_os.ProcessPriority, _: object
    ) -> None:
        """Handle process priority changes"""
        try:
            import psutil

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
>>>>>>> Stashed changes

    def finalize(self) -> None:
        """Finalize the application"""
        self.q_live_swap.finalize()

    def _on_closeEvent(self) -> None:
        """Handle window close event"""
        self.finalize()
        self.close()


class PlayaTewsIdentityMaskerApp(qtx.QXMainApplication):
    def __init__(self, userdata_path: Path) -> None:
        super().__init__()
        self.userdata_path = userdata_path
        self.settings_dirpath = userdata_path / 'settings'
        self.settings_dirpath.mkdir(parents=True, exist_ok=True)

        # Initialize localization
        Localization.set_language('en-US')

        # Fonts and images are loaded on demand (no initialization needed)

        # Create main window
        self.main_window = QDFLAppWindow(userdata_path, self.settings_dirpath)

        # Show splash screen
        self.show_splash_screen()

<<<<<<< Updated upstream
    def show_splash_screen(self):
        """Show memory optimization splash screen"""
        try:
            splash = qtx.QXWidget()
            splash.setFixedSize(400, 300)
            splash.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2d2d2d, stop:1 #1a1a1a);
                    color: #ffffff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """)
            
            layout = qtx.QXVBoxLayout()
            
            # Title
            title = QXLabel(text="🧠 Memory Optimized")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff88; margin: 20px;")
            title.setAlignment(qtx.Qt.AlignCenter)
            layout.addWidget(title)
            
            # Subtitle
            subtitle = QXLabel(text="PlayaTewsIdentityMasker")
            subtitle.setStyleSheet("font-size: 16px; color: #cccccc; margin: 10px;")
            subtitle.setAlignment(qtx.Qt.AlignCenter)
            layout.addWidget(subtitle)
            
            # Memory optimization info
            info = QXLabel(text="""
🚀 Memory Optimization Features:
• 2GB RAM Cache System
• Preprocessing Cache (30-50% CPU reduction)
• Postprocessing Cache (20-40% CPU reduction)
• Parallel Processing
• Smart Memory Management
• Real-time Performance Monitoring
            """)
            info.setStyleSheet("font-size: 12px; color: #aaaaaa; margin: 20px; line-height: 1.4;")
            info.setAlignment(qtx.Qt.AlignLeft)
            layout.addWidget(info)
            
            # Loading indicator
            loading = QXLabel(text="Initializing Memory Optimization...")
            loading.setStyleSheet("font-size: 14px; color: #00ff88; margin: 20px;")
            loading.setAlignment(qtx.Qt.AlignCenter)
            layout.addWidget(loading)
            
            splash.setLayout(layout)
            splash.show()
            
            # Auto-close after 3 seconds
            qtx.QXTimer.singleShot(3000, splash.close)
            qtx.QXTimer.singleShot(3000, self.main_window.show)
            
        except Exception as e:
            print(f"Could not show splash screen: {e}")
            self.main_window.show()

    def on_reinitialize(self):
        """Reinitialize the application"""
        try:
            self.main_window.finalize()
            self.main_window = QDFLAppWindow(self.userdata_path, self.settings_dirpath)
            self.main_window.show()
            print("✅ Application reinitialized with memory optimization")
        except Exception as e:
            print(f"❌ Failed to reinitialize: {e}")

    def initialize(self):
        """Initialize the application"""
        self.main_window.show()

    def finalize(self):
        """Finalize the application"""
        if hasattr(self, 'main_window'):
            self.main_window.finalize()

    def _on_splash_wnd_expired(self):
        """Handle splash window expiration"""
        self.main_window.show()
=======
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
>>>>>>> Stashed changes
