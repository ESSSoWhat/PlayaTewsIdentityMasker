#!/usr/bin/env python3
"""
Optimized PlayaTewsIdentityMasker OBS-Style Application
Uses optimized components and fixed widget hierarchy
"""

from pathlib import Path
from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter

from localization import L, Localization
from resources.fonts import QXFontDB
from resources.gfx import QXImageDB
from xlib import os as lib_os
from xlib import qt as qtx
from xlib.qt.widgets.QXLabel import QXLabel

from . import backend
from .ui.QOptimizedOBSStyleUI import QOptimizedOBSStyleUI
from .ui.QCameraSource import QCameraSource
from .ui.QFaceAligner import QFaceAligner
from .ui.QOptimizedFaceAnimator import QOptimizedFaceAnimator
from .ui.QFaceDetector import QFaceDetector
from .ui.QOptimizedFaceMarker import QOptimizedFaceMarker
from .ui.QOptimizedFaceMerger import QOptimizedFaceMerger
from .ui.QFaceSwapInsight import QFaceSwapInsight
from .ui.QFaceSwapDFM import QFaceSwapDFM
from .ui.QFileSource import QFileSource
from .ui.QOptimizedFrameAdjuster import QOptimizedFrameAdjuster
from .ui.QEnhancedStreamOutput import QEnhancedStreamOutput
from .ui.QGroupedFaceDetection import QGroupedFaceDetection
from .ui.QGroupedInputSources import QGroupedInputSources
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer


class QLiveSwapOptimized(qtx.QXWidget):
    def __init__(self, userdata_path : Path,
                       settings_dirpath : Path):
        super().__init__()

        dfm_models_path = userdata_path / 'dfm_models'
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / 'animatables'
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / 'output_sequence'
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config
        backend_db          = self.backend_db          = backend.BackendDB( settings_dirpath / 'states.dat' )
        backend_weak_heap   = self.backend_weak_heap   = backend.BackendWeakHeap(size_mb=2048)
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
        face_swap_dfm   = self.face_swap_dfm   = backend.FaceSwapDFM  (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_aligner_bc_out, bc_out=face_swapper_bc_out, dfm_models_path=dfm_models_path, backend_db=backend_db )
        frame_adjuster = self.frame_adjuster = backend.FrameAdjuster(weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_swapper_bc_out, bc_out=frame_adjuster_bc_out, backend_db=backend_db )
        face_merger    = self.face_merger    = backend.FaceMerger   (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=frame_adjuster_bc_out, bc_out=face_merger_bc_out, backend_db=backend_db )
        
        # Use enhanced streaming output
        from .backend.EnhancedStreamOutput import EnhancedStreamOutput
        stream_output  = self.stream_output  = EnhancedStreamOutput (weak_heap=backend_weak_heap, reemit_frame_signal=reemit_frame_signal, bc_in=face_merger_bc_out, save_default_path=userdata_path, backend_db=backend_db)

        self.all_backends : List[backend.BackendHost] = [file_source, camera_source, face_detector, face_marker, face_aligner, face_animator, face_swap_insight, face_swap_dfm, frame_adjuster, face_merger, stream_output]

        # Create optimized UI components
        self.q_file_source    = QFileSource(self.file_source)
        self.q_camera_source  = QCameraSource(self.camera_source)
        self.q_face_detector  = QFaceDetector(self.face_detector)
        self.q_face_marker    = QOptimizedFaceMarker(self.face_marker)
        self.q_face_aligner   = QFaceAligner(self.face_aligner)
        self.q_face_animator  = QOptimizedFaceAnimator(self.face_animator, animatables_path=animatables_path)
        self.q_face_swap_insight = QFaceSwapInsight(self.face_swap_insight, faces_path=animatables_path)
        self.q_face_swap_dfm  = QFaceSwapDFM(self.face_swap_dfm, dfm_models_path=dfm_models_path)
        self.q_frame_adjuster = QOptimizedFrameAdjuster(self.frame_adjuster)
        self.q_face_merger    = QOptimizedFaceMerger(self.face_merger)
        
        # Use enhanced streaming output UI
        self.q_stream_output  = QEnhancedStreamOutput(self.stream_output)

        # Create grouped components for better organization
        self.q_grouped_input_sources = QGroupedInputSources(self.q_file_source, self.q_camera_source)
        self.q_grouped_face_detection = QGroupedFaceDetection(self.q_face_detector, self.q_face_aligner)

        # Create viewers
        self.q_ds_frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out)
        self.q_ds_fa_viewer    = QBCFaceAlignViewer(backend_weak_heap, face_aligner_bc_out, preview_width=256)
        self.q_ds_fc_viewer    = QBCFaceSwapViewer(backend_weak_heap, face_merger_bc_out, preview_width=256)
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(backend_weak_heap, face_merger_bc_out)

        # Create face-swapping components dictionary with optimized components
        face_swap_components = {
            'file_source': self.q_file_source,
            'camera_source': self.q_camera_source,
            'face_detector': self.q_face_detector,
            'face_marker': self.q_face_marker,
            'face_aligner': self.q_face_aligner,
            'face_animator': self.q_face_animator,
            'face_swap_insight': self.q_face_swap_insight,
            'face_swap_dfm': self.q_face_swap_dfm,
            'frame_adjuster': self.q_frame_adjuster,
            'face_merger': self.q_face_merger,
            'stream_output': self.q_stream_output,
            # Add grouped components
            'grouped_input_sources': self.q_grouped_input_sources,
            'grouped_face_detection': self.q_grouped_face_detection
        }

        # Create viewers dictionary
        viewers_components = {
            'frame_viewer': self.q_ds_frame_viewer,
            'face_align_viewer': self.q_ds_fa_viewer,
            'face_swap_viewer': self.q_ds_fc_viewer,
            'merged_frame_viewer': self.q_ds_merged_frame_viewer
        }

        # Create optimized OBS-style UI
        try:
            self.q_obs_style_ui = QOptimizedOBSStyleUI(self.stream_output, userdata_path, face_swap_components, viewers_components)
        except Exception as e:
            print(f"Warning: Could not create optimized OBS-style UI: {e}")
            # Create a simple placeholder widget
            self.q_obs_style_ui = qtx.QXLabel(text="Optimized OBS-Style UI not available\nUsing Traditional Interface")
            self.q_obs_style_ui.setStyleSheet("QLabel { background-color: #2d2d2d; color: #ffffff; padding: 20px; font-size: 14px; }")
            self.q_obs_style_ui.setAlignment(Qt.AlignCenter)

        # Create main layout with optimized OBS-style UI
        main_layout = qtx.QXVBoxLayout()
        main_layout.addWidget(self.q_obs_style_ui)
        self.setLayout(main_layout)

        # Set window properties
        self.setWindowTitle("PlayaTewsIdentityMasker - Optimized OBS-Style Interface")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Set window icon
        try:
            icon = QXImageDB.app_icon()
            if icon:
                self.setWindowIcon(icon.as_QIcon())
        except:
            pass

        # Create menu bar
        self.create_menu_bar()

        self._timer = qtx.QXTimer(interval=5, timeout=self._on_timer_5ms, start=True)

    def _process_messages(self):
        self.backend_db.process_messages()
        for backend in self.all_backends:
            backend.process_messages()

    def _on_timer_5ms(self):
        self._process_messages()

    def clear_backend_db(self):
        self.backend_db.clear()

    def create_menu_bar(self):
        """Create menu bar for the optimized app"""
        menu_bar = qtx.QXMenuBar(font=QXFontDB.get_default_font(size=10), size_policy=('fixed', 'minimumexpanding'))
        menu_file = menu_bar.addMenu(L('@QDFLAppWindow.file'))
        menu_language = menu_bar.addMenu(L('@QDFLAppWindow.language'))
        menu_view = menu_bar.addMenu(L('@QDFLAppWindow.view'))

        # File menu
        menu_file_action_reinitialize = menu_file.addAction(L('@QDFLAppWindow.reinitialize'))
        menu_file_action_reinitialize.triggered.connect(lambda: qtx.QXMainApplication.inst.reinitialize())

        menu_file_action_reset_settings = menu_file.addAction(L('@QDFLAppWindow.reset_modules_settings'))
        menu_file_action_reset_settings.triggered.connect(self._on_reset_modules_settings)

        menu_file.addSeparator()
        menu_file_action_quit = menu_file.addAction(L('@QDFLAppWindow.quit'))
        menu_file_action_quit.triggered.connect(lambda: qtx.QXMainApplication.quit())

        # Language menu
        menu_language_action_english = menu_file.addAction('English')
        menu_language_action_english.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('en-US'), qtx.QXMainApplication.inst.reinitialize()))

        menu_language_action_spanish = menu_file.addAction('Español')
        menu_language_action_spanish.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('es-ES'), qtx.QXMainApplication.inst.reinitialize()))

        menu_language_action_italian = menu_file.addAction('Italiano')
        menu_language_action_italian.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('it-IT'), qtx.QXMainApplication.inst.reinitialize()))

        menu_language_action_russian = menu_file.addAction('Русский')
        menu_language_action_russian.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('ru-RU'), qtx.QXMainApplication.inst.reinitialize()))

        # View menu
        menu_view_action_fullscreen = menu_view.addAction("Toggle Fullscreen")
        menu_view_action_fullscreen.triggered.connect(self._on_toggle_fullscreen)

        # Note: Menu bar is set in the main window, not in this widget
        pass

    def _on_reset_modules_settings(self):
        self.clear_backend_db()
        qtx.QXMainApplication.inst.reinitialize()

    def _on_toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def initialize(self):
        for bcknd in self.all_backends:
            default_state = True
            if isinstance(bcknd, (backend.CameraSource, backend.FaceAnimator, backend.FaceSwapInsight) ):
                default_state = False
            bcknd.restore_on_off_state(default_state=default_state)

    def finalize(self):
        # Gracefully stop the backend
        for backend in self.all_backends:
            while backend.is_starting() or backend.is_stopping():
                self._process_messages()

            backend.save_on_off_state()
            backend.stop()

        while not all( x.is_stopped() for x in self.all_backends ):
            self._process_messages()

        self.backend_db.finish_pending_jobs()

        self.q_ds_frame_viewer.clear()
        self.q_ds_fa_viewer.clear()


class QDFLOptimizedAppWindow(qtx.QXWindow):

    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=('minimum', 'minimum') )

        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath

        # Initialize backup manager
        from .ui.UILayoutBackupManager import UILayoutBackupManager
        self.backup_manager = UILayoutBackupManager(settings_dirpath, userdata_path)

        menu_bar = qtx.QXMenuBar( font=QXFontDB.get_default_font(size=10), size_policy=('fixed', 'minimumexpanding') )
        menu_file = menu_bar.addMenu( L('@QDFLAppWindow.file') )
        menu_language = menu_bar.addMenu( L('@QDFLAppWindow.language') )
        menu_view = menu_bar.addMenu( L('@QDFLAppWindow.view') )

        menu_file_action_reinitialize = menu_file.addAction( L('@QDFLAppWindow.reinitialize') )
        menu_file_action_reinitialize.triggered.connect(lambda: qtx.QXMainApplication.inst.reinitialize() )

        menu_file_action_reset_settings = menu_file.addAction( L('@QDFLAppWindow.reset_modules_settings') )
        menu_file_action_reset_settings.triggered.connect(self._on_reset_modules_settings)

        # Add backup manager menu items
        menu_file.addSeparator()
        menu_file_action_backup_layout = menu_file.addAction( "Backup UI Layout" )
        menu_file_action_backup_layout.triggered.connect(self._on_backup_layout)
        
        menu_file_action_restore_layout = menu_file.addAction( "Restore UI Layout" )
        menu_file_action_restore_layout.triggered.connect(self._on_restore_layout)
        
        menu_file_action_manage_backups = menu_file.addAction( "Manage Layout Backups" )
        menu_file_action_manage_backups.triggered.connect(self._on_manage_backups)

        menu_file_action_quit = menu_file.addAction( L('@QDFLAppWindow.quit') )
        menu_file_action_quit.triggered.connect(lambda: qtx.QXMainApplication.quit() )

        menu_language_action_english = menu_file.addAction('English' )
        menu_language_action_english.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('en-US'), qtx.QXMainApplication.inst.reinitialize()) )

        menu_language_action_spanish = menu_file.addAction('Español' )
        menu_language_action_spanish.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('es-ES'), qtx.QXMainApplication.inst.reinitialize()) )

        menu_language_action_italian = menu_file.addAction('Italiano' )
        menu_language_action_italian.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('it-IT'), qtx.QXMainApplication.inst.reinitialize()) )

        menu_language_action_russian = menu_file.addAction('Русский')
        menu_language_action_russian.triggered.connect(lambda: (qtx.QXMainApplication.inst.set_language('ru-RU'), qtx.QXMainApplication.inst.reinitialize()) )

        # Add view menu items
        menu_view_action_toggle_controls = menu_view.addAction( "Toggle Traditional Controls" )
        menu_view_action_toggle_controls.triggered.connect(self._on_toggle_traditional_controls)
        
        menu_view_action_fullscreen = menu_view.addAction( "Toggle Fullscreen" )
        menu_view_action_fullscreen.triggered.connect(self._on_toggle_fullscreen)

        self.setMenuBar(menu_bar)

        # Create optimized live swap widget
        self.q_live_swap = QLiveSwapOptimized(userdata_path, settings_dirpath)
        self.add_widget(self.q_live_swap)

        # Set window properties
        self.setWindowTitle("PlayaTewsIdentityMasker - Optimized OBS-Style Interface")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Set window icon
        try:
            icon = QXImageDB.app_icon()
            if icon:
                self.setWindowIcon(icon.as_QIcon())
        except:
            pass

    def _on_reset_modules_settings(self):
        self.q_live_swap.clear_backend_db()
        qtx.QXMainApplication.inst.reinitialize()

    def _on_cb_process_priority_choice(self, prio : lib_os.ProcessPriority, _):
        lib_os.set_process_priority(prio)

    def finalize(self):
        self.q_live_swap.finalize()

    def _on_closeEvent(self):
        self.finalize()

    def _on_backup_layout(self):
        """Backup current UI layout"""
        try:
            backup_name = self.backup_manager.create_backup(
                name="Optimized_UI_Backup",
                description="Optimized OBS-style UI layout backup"
            )
            
            # Show success message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Backup Created", 
                f"UI layout backup created successfully:\n{backup_name}"
            )
        except Exception as e:
            # Show error message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Backup Failed", 
                f"Failed to create UI layout backup:\n{str(e)}"
            )

    def _on_restore_layout(self):
        """Restore UI layout from backup"""
        try:
            # Get list of available backups
            backups = self.backup_manager.list_backups()
            
            if not backups:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "No Backups", 
                    "No UI layout backups found."
                )
                return
            
            # Show backup selection dialog
            from PyQt5.QtWidgets import QInputDialog
            backup_names = [backup['name'] for backup in backups]
            backup_name, ok = QInputDialog.getItem(
                self, 
                "Select Backup", 
                "Choose a backup to restore:",
                backup_names, 
                0, 
                False
            )
            
            if ok and backup_name:
                self.backup_manager.restore_backup(backup_name)
                
                # Show success message
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "Restore Successful", 
                    f"UI layout restored from backup:\n{backup_name}"
                )
        except Exception as e:
            # Show error message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Restore Failed", 
                f"Failed to restore UI layout:\n{str(e)}"
            )

    def _on_manage_backups(self):
        """Open backup management dialog"""
        try:
            from .ui.QBackupManagerUI import QBackupManagerDialog
            dialog = QBackupManagerDialog(self.backup_manager, self)
            dialog.exec_()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to open backup manager:\n{str(e)}"
            )

    def _on_toggle_traditional_controls(self):
        """Toggle visibility of traditional controls"""
        # This would show/hide the traditional control panels
        pass

    def _on_toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()


class PlayaTewsIdentityMaskerOptimizedApp(qtx.QXMainApplication):
    def __init__(self, userdata_path):
        self.userdata_path = userdata_path
        settings_dirpath = self.settings_dirpath = userdata_path / 'settings'
        if not settings_dirpath.exists():
            settings_dirpath.mkdir(parents=True)
        super().__init__(app_name='PlayaTewsIdentityMaskerOptimized', settings_dirpath=settings_dirpath)

        self.setFont(QXFontDB.get_default_font())
        self.setWindowIcon(QXImageDB.app_icon().as_QIcon())

        # Create main window using QDFLOptimizedAppWindow
        self.q_main_window = QDFLOptimizedAppWindow(userdata_path, self.settings_dirpath)

    def on_reinitialize(self):
        """Handle application reinitialization"""
        try:
            # Finalize current state
            if hasattr(self, 'q_main_window'):
                self.q_main_window.finalize()
            
            # Recreate main window
            self.q_main_window = QDFLOptimizedAppWindow(self.userdata_path, self.settings_dirpath)
            
            # Show main window
            self.q_main_window.show()
            
        except Exception as e:
            print(f"Error during reinitialization: {e}")

    def initialize(self):
        """Initialize the application"""
        self.q_main_window.show()

    def finalize(self):
        """Finalize the application"""
        if hasattr(self, 'q_main_window'):
            self.q_main_window.finalize()

    def _on_splash_wnd_expired(self):
        """Handle splash window expiration"""
        self.initialize() 