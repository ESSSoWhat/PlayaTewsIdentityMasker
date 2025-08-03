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
from .ui.QOBSStyleUI import QOBSStyleUI
from .ui.widgets.QBCFaceAlignViewer import QBCFaceAlignViewer
from .ui.widgets.QBCFaceSwapViewer import QBCFaceSwapViewer
from .ui.widgets.QBCFrameViewer import QBCFrameViewer
from .ui.widgets.QBCMergedFrameViewer import QBCMergedFrameViewer


class QLiveSwapOBS(qtx.QXWidget):
    def __init__(self, userdata_path: Path, settings_dirpath: Path):
        super().__init__()

        dfm_models_path = userdata_path / "dfm_models"
        dfm_models_path.mkdir(parents=True, exist_ok=True)

        animatables_path = userdata_path / "animatables"
        animatables_path.mkdir(parents=True, exist_ok=True)

        output_sequence_path = userdata_path / "output_sequence"
        output_sequence_path.mkdir(parents=True, exist_ok=True)

        # Construct backend config
        backend_db = self.backend_db = backend.BackendDB(
            settings_dirpath / "states.dat"
        )
        backend_weak_heap = self.backend_weak_heap = backend.BackendWeakHeap(
            size_mb=2048
        )
        reemit_frame_signal = self.reemit_frame_signal = backend.BackendSignal()

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
        face_swap_dfm = self.face_swap_dfm = backend.FaceSwapDFM(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_aligner_bc_out,
            bc_out=face_swapper_bc_out,
            dfm_models_path=dfm_models_path,
            backend_db=backend_db,
        )
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

        # Use enhanced streaming output
        from .backend.EnhancedStreamOutput import EnhancedStreamOutput

        stream_output = self.stream_output = EnhancedStreamOutput(
            weak_heap=backend_weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=face_merger_bc_out,
            save_default_path=userdata_path,
            backend_db=backend_db,
        )

        # Add voice changer backend
        from .backend.VoiceChanger import VoiceChanger

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

        # Create UI components
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
            self.face_swap_dfm, dfm_models_path=dfm_models_path
        )
        self.q_frame_adjuster = QFrameAdjuster(self.frame_adjuster)
        self.q_face_merger = QFaceMerger(self.face_merger)

        # Use enhanced streaming output UI
        from .ui.QEnhancedStreamOutput import QEnhancedStreamOutput

        self.q_stream_output = QEnhancedStreamOutput(self.stream_output)

        # Create viewers
        self.q_ds_frame_viewer = QBCFrameViewer(backend_weak_heap, multi_sources_bc_out)
        self.q_ds_fa_viewer = QBCFaceAlignViewer(
            backend_weak_heap, face_aligner_bc_out, preview_width=256
        )
        self.q_ds_fc_viewer = QBCFaceSwapViewer(
            backend_weak_heap, face_merger_bc_out, preview_width=256
        )
        self.q_ds_merged_frame_viewer = QBCMergedFrameViewer(
            backend_weak_heap, face_merger_bc_out
        )

        # Create face-swapping components dictionary
        face_swap_components = {
            "file_source": self.q_file_source,
            "camera_source": self.q_camera_source,
            "face_detector": self.q_face_detector,
            "face_marker": self.q_face_marker,
            "face_aligner": self.q_face_aligner,
            "face_animator": self.q_face_animator,
            "face_swap_insight": self.q_face_swap_insight,
            "face_swap_dfm": self.q_face_swap_dfm,
            "frame_adjuster": self.q_frame_adjuster,
            "face_merger": self.q_face_merger,
            "stream_output": self.q_stream_output,
        }

        # Create viewers dictionary
        viewers_components = {
            "frame_viewer": self.q_ds_frame_viewer,
            "face_align_viewer": self.q_ds_fa_viewer,
            "face_swap_viewer": self.q_ds_fc_viewer,
            "merged_frame_viewer": self.q_ds_merged_frame_viewer,
        }

        # Create OBS-style UI with integrated face-swapping components and viewers
        try:
            from .ui.QOptimizedOBSStyleUI import QOptimizedOBSStyleUI

            # Create optimized OBS-style UI with voice changer integration
            obs_widget = QOptimizedOBSStyleUI(
                self.stream_output,
                userdata_path,
                face_swap_components,
                viewers_components,
                self.voice_changer,  # Pass voice changer backend
            )
            self.q_obs_style_ui = obs_widget
        except ImportError as e:
            print(f"Warning: Could not import QOptimizedOBSStyleUI: {e}")
            # Fallback to original OBS-style UI
            try:
                from .ui.QOBSStyleUI import QOBSStyleUI

                obs_widget = QOBSStyleUI(
                    self.stream_output,
                    userdata_path,
                    face_swap_components,
                    viewers_components,
                )
                self.q_obs_style_ui = obs_widget
            except ImportError as e2:
                print(f"Warning: Could not import QOBSStyleUI: {e2}")
                # Create a simple placeholder widget
                self.q_obs_style_ui = qtx.QXLabel(
                    text="OBS-Style UI not available\nUsing Traditional Interface"
                )
                self.q_obs_style_ui.setStyleSheet(
                    "QLabel { background-color: #2d2d2d; color: #ffffff; padding: 20px; font-size: 14px; }"
                )
                self.q_obs_style_ui.setAlignment(Qt.AlignCenter)

        # Create main layout with OBS-style UI (viewers are now integrated)
        main_layout = qtx.QXVBoxLayout()
        main_layout.addWidget(self.q_obs_style_ui)
        self.setLayout(main_layout)

        self._timer = qtx.QXTimer(interval=5, timeout=self._on_timer_5ms, start=True)

    def _process_messages(self):
        self.backend_db.process_messages()
        for backend in self.all_backends:
            backend.process_messages()

    def _on_timer_5ms(self):
        self._process_messages()

    def clear_backend_db(self):
        self.backend_db.clear()

    def initialize(self):
        for bcknd in self.all_backends:
            default_state = True
            if isinstance(
                bcknd,
                (backend.CameraSource, backend.FaceAnimator, backend.FaceSwapInsight),
            ):
                default_state = False
            bcknd.restore_on_off_state(default_state=default_state)

    def finalize(self):
        # Gracefully stop the backend
        for backend in self.all_backends:
            while backend.is_starting() or backend.is_stopping():
                self._process_messages()

            backend.save_on_off_state()
            backend.stop()

        while not all(x.is_stopped() for x in self.all_backends):
            self._process_messages()

        self.backend_db.finish_pending_jobs()

        self.q_ds_frame_viewer.clear()
        self.q_ds_fa_viewer.clear()


class QDFLOBSAppWindow(qtx.QXWindow):
    def __init__(self, userdata_path, settings_dirpath):
        super().__init__(save_load_state=True, size_policy=("minimum", "minimum"))

        self._userdata_path = userdata_path
        self._settings_dirpath = settings_dirpath

        # Initialize backup manager
        from .ui.UILayoutBackupManager import UILayoutBackupManager

        self.backup_manager = UILayoutBackupManager(settings_dirpath, userdata_path)

        menu_bar = qtx.QXMenuBar(
            font=QXFontDB.get_default_font(size=10),
            size_policy=("fixed", "minimumexpanding"),
        )
        menu_file = menu_bar.addMenu(L("@QDFLAppWindow.file"))
        menu_language = menu_bar.addMenu(L("@QDFLAppWindow.language"))
        menu_view = menu_bar.addMenu(L("@QDFLAppWindow.view"))

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

        # Add backup manager menu items
        menu_file.addSeparator()
        menu_file_action_backup_layout = menu_file.addAction("Backup UI Layout")
        menu_file_action_backup_layout.triggered.connect(self._on_backup_layout)

        menu_file_action_restore_layout = menu_file.addAction("Restore UI Layout")
        menu_file_action_restore_layout.triggered.connect(self._on_restore_layout)

        menu_file_action_manage_backups = menu_file.addAction("Manage Layout Backups")
        menu_file_action_manage_backups.triggered.connect(self._on_manage_backups)

        menu_file_action_quit = menu_file.addAction(L("@QDFLAppWindow.quit"))
        menu_file_action_quit.triggered.connect(lambda: qtx.QXMainApplication.quit())

        menu_language_action_english = menu_language.addAction("English")
        menu_language_action_english.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("en-US"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_language_action_spanish = menu_language.addAction("Español")
        menu_language_action_spanish.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("es-ES"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_language_action_italian = menu_language.addAction("Italiano")
        menu_language_action_italian.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("it-IT"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_language_action_russian = menu_language.addAction("Русский")
        menu_language_action_russian.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("ru-RU"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_language_action_chinese = menu_language.addAction("汉语")
        menu_language_action_chinese.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("zh-CN"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_language_action_chinese = menu_language.addAction("日本語")
        menu_language_action_chinese.triggered.connect(
            lambda: (
                qtx.QXMainApplication.inst.set_language("ja-JP"),
                qtx.QXMainApplication.inst.reinitialize(),
            )
        )

        menu_help = menu_bar.addMenu(L("@QDFLAppWindow.help"))
        menu_help_action_github = menu_help.addAction(
            L("@QDFLAppWindow.visit_github_page")
        )
        menu_help_action_github.triggered.connect(
            lambda: qtx.QDesktopServices.openUrl(
                qtx.QUrl("https://github.com/iperov/DeepFaceLive")
            )
        )

        # Add view menu items for OBS-style features
        menu_view_action_toggle_controls = menu_view.addAction(
            "Toggle Traditional Controls"
        )
        menu_view_action_toggle_controls.triggered.connect(
            self._on_toggle_traditional_controls
        )

        menu_view_action_fullscreen = menu_view.addAction("Toggle Fullscreen")
        menu_view_action_fullscreen.triggered.connect(self._on_toggle_fullscreen)

        self.q_live_swap = None
        self.q_live_swap_container = qtx.QXWidget()

        self.content_l = qtx.QXVBoxLayout()

        cb_process_priority = self._cb_process_priority = qtx.QXSaveableComboBox(
            db_key="_QDFLAppWindow_process_priority",
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
                        [menu_bar, menu_bar_tail, qtx.QXFrame()],
                        size_policy=("minimumexpanding", "fixed"),
                    ),
                    5,
                    qtx.QXWidget(layout=self.content_l),
                ]
            )
        )

        self.call_on_closeEvent(self._on_closeEvent)

    def _on_reset_modules_settings(self):
        if self.q_live_swap is not None:
            self.q_live_swap.clear_backend_db()

    def _on_cb_process_priority_choice(self, prio: lib_os.ProcessPriority, _):
        lib_os.set_process_priority(prio)

    def _on_toggle_traditional_controls(self):
        # Toggle visibility of traditional controls
        pass

    def _on_toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _on_backup_layout(self):
        """Handle backup layout menu action"""
        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"obs_auto_backup_{timestamp}"
            success = self.backup_manager.create_backup(
                backup_name, "OBS UI auto backup from menu"
            )
            if success:
                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.information(
                    self,
                    "Backup Created",
                    f"OBS UI layout backup created successfully:\n{backup_name}",
                )
            else:
                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self, "Backup Failed", "Failed to create OBS UI layout backup"
                )
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Backup Error", f"Error creating backup: {e}")

    def _on_restore_layout(self):
        """Handle restore layout menu action"""
        try:
            backups = self.backup_manager.list_backups()
            if not backups:
                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.information(
                    self, "No Backups", "No OBS UI layout backups found"
                )
                return
            from .ui.QBackupManagerUI import QBackupManagerDialog

            dialog = QBackupManagerDialog(self.backup_manager, self)
            dialog.exec_()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.critical(self, "Restore Error", f"Error restoring layout: {e}")

    def _on_manage_backups(self):
        """Handle manage backups menu action"""
        try:
            from .ui.QBackupManagerUI import QBackupManagerDialog

            dialog = QBackupManagerDialog(self.backup_manager, self)
            dialog.exec_()
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox

            QMessageBox.critical(
                self, "Backup Manager Error", f"Error opening backup manager: {e}"
            )

    def finalize(self):
        if self.q_live_swap is not None:
            self.q_live_swap.finalize()

    def _on_closeEvent(self):
        self.finalize()


class PlayaTewsIdentityMaskerOBSStyleApp(qtx.QXMainApplication):
    def __init__(self, userdata_path):
        super().__init__(
            app_name="PlayaTewsIdentityMasker OBS Style",
            settings_dirpath=userdata_path / "settings",
        )

        self._userdata_path = userdata_path
        self._settings_dirpath = userdata_path / "settings"
        self._settings_dirpath.mkdir(parents=True, exist_ok=True)

        self._wnd = QDFLOBSAppWindow(userdata_path, self._settings_dirpath)
        self._wnd.show()

        # Initialize the main content
        self.initialize()

    def on_reinitialize(self):
        if self._wnd.q_live_swap is not None:
            self._wnd.q_live_swap.finalize()

        # Create the live swap component as a regular widget, not a window
        self._wnd.q_live_swap = QLiveSwapOBS(
            self._userdata_path, self._settings_dirpath
        )
        self._wnd.content_l.addWidget(self._wnd.q_live_swap)
        self._wnd.q_live_swap.initialize()

        # Ensure all backend components are properly initialized
        print("Initializing backend components...")
        from . import backend as backend_module

        for backend in self._wnd.q_live_swap.all_backends:
            print(f"Initializing {backend.__class__.__name__}")
            # Use restore_on_off_state instead of direct start
            default_state = True
            if isinstance(
                backend,
                (
                    backend_module.CameraSource,
                    backend_module.FaceAnimator,
                    backend_module.FaceSwapInsight,
                ),
            ):
                default_state = False
            backend.restore_on_off_state(default_state=default_state)

    def initialize(self):
        self.on_reinitialize()

    def finalize(self):
        if self._wnd is not None:
            self._wnd.finalize()

    def _on_splash_wnd_expired(self):
        pass
