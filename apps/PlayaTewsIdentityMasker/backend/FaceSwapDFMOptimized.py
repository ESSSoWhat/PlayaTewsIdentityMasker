import time
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
from modelhub import DFLive
from xlib import os as lib_os
from xlib.image.ImageProcessor import ImageProcessor
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None
import cv2

from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


class FaceSwapDFMOptimized(BackendHost):
    def __init__(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, dfm_models_path : Path, backend_db : BackendDB = None,
                  id : int = 0):
        self._id = id
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=FaceSwapDFMOptimizedWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap, reemit_frame_signal, bc_in, bc_out, dfm_models_path])

    def get_control_sheet(self) -> 'Sheet.Host': return super().get_control_sheet()

    def _get_name(self):
        return super()._get_name()# + f'{self._id}'


class FaceSwapDFMOptimizedWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': return super().get_state()
    def get_control_sheet(self) -> 'Sheet.Worker': return super().get_control_sheet()

    def on_start(self, weak_heap : BackendWeakHeap, reemit_frame_signal : BackendSignal, bc_in : BackendConnection, bc_out : BackendConnection, dfm_models_path : Path):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.dfm_models_path = dfm_models_path

        self.pending_bcd = None
        self.dfm_model_initializer = None
        self.dfm_model = None
        
        # Performance optimization variables
        self.frame_skip_counter = 0
        self.frame_skip_rate = 0  # 0 = process every frame, 1 = skip every other frame, etc.
        self.last_processed_frame_time = 0
        self.target_fps = 30
        self.frame_time_threshold = 1.0 / self.target_fps
        
        # Caching for performance
        self.cached_face_align_image = None
        self.cached_celeb_face = None
        self.cache_valid = False
        self.cache_timestamp = 0
        self.cache_duration = 0.1  # Cache for 100ms
        
        # Threading for parallel processing
        self.processing_thread = None
        self.processing_queue = []
        self.processing_lock = threading.Lock()
        self.stop_processing = False
        
        # Performance monitoring
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.processing_times = []
        
        lib_os.set_timer_resolution(1)

        state, cs = self.get_state(), self.get_control_sheet()

        # Setup callbacks
        cs.model.call_on_selected(self.on_cs_model)
        cs.device.call_on_selected(self.on_cs_device)
        cs.swap_all_faces.call_on_flag(self.on_cs_swap_all_faces)
        cs.face_id.call_on_number(self.on_cs_face_id)
        cs.morph_factor.call_on_number(self.on_cs_morph_factor)
        cs.presharpen_amount.call_on_number(self.on_cs_presharpen_amount)
        cs.pre_gamma_red.call_on_number(self.on_cs_pre_gamma_red)
        cs.pre_gamma_green.call_on_number(self.on_cs_pre_gamma_green)
        cs.pre_gamma_blue.call_on_number(self.on_cs_pre_gamma_blue)
        cs.post_gamma_red.call_on_number(self.on_cs_post_gamma_red)
        cs.post_gamma_blue.call_on_number(self.on_cs_post_gamma_blue)
        cs.post_gamma_green.call_on_number(self.on_cs_post_gamma_green)
        cs.two_pass.call_on_flag(self.on_cs_two_pass)
        cs.target_fps.call_on_number(self.on_cs_target_fps)
        cs.frame_skip_rate.call_on_number(self.on_cs_frame_skip_rate)
        cs.enable_caching.call_on_flag(self.on_cs_enable_caching)

        cs.device.enable()
        cs.device.set_choices( DFLive.get_available_devices(), none_choice_name='@misc.menu_select')
        cs.device.select(state.device)

    def on_cs_device(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            cs.model.enable()
            cs.model.set_choices( DFLive.get_available_models_info(self.dfm_models_path), none_choice_name='@misc.menu_select')
            cs.model.select(state.model)
        else:
            state.device = device
            self.save_state()
            self.restart()

    def on_cs_model(self, idx, model):
        state, cs = self.get_state(), self.get_control_sheet()

        if state.model == model:
            state.model_state = state.models_state[model.get_name()] = state.models_state.get(model.get_name(), ModelState())
            self.dfm_model_initializer = DFLive.DFMModel_from_info(state.model, state.device)
            self.set_busy(True)
            # Clear cache when model changes
            self.clear_cache()
        else:
            state.model = model
            self.save_state()
            self.restart()

    def on_cs_swap_all_faces(self, swap_all_faces):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            model_state.swap_all_faces = swap_all_faces

            if not swap_all_faces:
                cs.face_id.enable()
                cs.face_id.set_config(lib_csw.Number.Config(min=0, max=999, step=1, decimals=0, allow_instant_update=True))
                cs.face_id.set_number(state.model_state.face_id if state.model_state.face_id is not None else 0)
            else:
                cs.face_id.disable()

            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_face_id(self, face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.face_id.get_config()
            face_id = model_state.face_id = int(np.clip(face_id, cfg.min, cfg.max))
            cs.face_id.set_number(face_id)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_presharpen_amount(self, presharpen_amount):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.presharpen_amount.get_config()
            presharpen_amount = model_state.presharpen_amount = float(np.clip(presharpen_amount, cfg.min, cfg.max))
            cs.presharpen_amount.set_number(presharpen_amount)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_morph_factor(self, morph_factor):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.morph_factor.get_config()
            morph_factor = model_state.morph_factor = float(np.clip(morph_factor, cfg.min, cfg.max))
            cs.morph_factor.set_number(morph_factor)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_pre_gamma_red(self, pre_gamma_red):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_red.get_config()
            pre_gamma_red = model_state.pre_gamma_red = float(np.clip(pre_gamma_red, cfg.min, cfg.max))
            cs.pre_gamma_red.set_number(pre_gamma_red)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_pre_gamma_green(self, pre_gamma_green):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_green.get_config()
            pre_gamma_green = model_state.pre_gamma_green = float(np.clip(pre_gamma_green, cfg.min, cfg.max))
            cs.pre_gamma_green.set_number(pre_gamma_green)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_pre_gamma_blue(self, pre_gamma_blue):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_blue.get_config()
            pre_gamma_blue = model_state.pre_gamma_blue = float(np.clip(pre_gamma_blue, cfg.min, cfg.max))
            cs.pre_gamma_blue.set_number(pre_gamma_blue)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_post_gamma_red(self, post_gamma_red):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_red.get_config()
            post_gamma_red = model_state.post_gamma_red = float(np.clip(post_gamma_red, cfg.min, cfg.max))
            cs.post_gamma_red.set_number(post_gamma_red)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_post_gamma_blue(self, post_gamma_blue):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_blue.get_config()
            post_gamma_blue = model_state.post_gamma_blue = float(np.clip(post_gamma_blue, cfg.min, cfg.max))
            cs.post_gamma_blue.set_number(post_gamma_blue)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_post_gamma_green(self, post_gamma_green):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_green.get_config()
            post_gamma_green = model_state.post_gamma_green = float(np.clip(post_gamma_green, cfg.min, cfg.max))
            cs.post_gamma_green.set_number(post_gamma_green)
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_two_pass(self, two_pass):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            model_state.two_pass = two_pass
            self.save_state()
            self.reemit_frame_signal.send()
            self.clear_cache()

    def on_cs_target_fps(self, target_fps):
        state, cs = self.get_state(), self.get_control_sheet()
        self.target_fps = max(1, int(target_fps))
        self.frame_time_threshold = 1.0 / self.target_fps
        state.target_fps = self.target_fps
        self.save_state()

    def on_cs_frame_skip_rate(self, frame_skip_rate):
        state, cs = self.get_state(), self.get_control_sheet()
        self.frame_skip_rate = max(0, int(frame_skip_rate))
        state.frame_skip_rate = self.frame_skip_rate
        self.save_state()

    def on_cs_enable_caching(self, enable_caching):
        state, cs = self.get_state(), self.get_control_sheet()
        state.enable_caching = enable_caching
        if not enable_caching:
            self.clear_cache()
        self.save_state()

    def clear_cache(self):
        """Clear the face swap cache"""
        self.cached_face_align_image = None
        self.cached_celeb_face = None
        self.cache_valid = False
        self.cache_timestamp = 0

    def should_skip_frame(self) -> bool:
        """Determine if current frame should be skipped for performance"""
        current_time = time.time()
        
        # Frame skip logic
        if self.frame_skip_rate > 0:
            self.frame_skip_counter += 1
            if self.frame_skip_counter % (self.frame_skip_rate + 1) == 0:
                return True
        
        # FPS limiting logic
        if current_time - self.last_processed_frame_time < self.frame_time_threshold:
            return True
            
        return False

    def optimize_face_align_image(self, face_align_image: np.ndarray, model_state) -> np.ndarray:
        """Optimize face align image processing"""
        fai_ip = ImageProcessor(face_align_image)
        
        # Apply presharpen if needed
        if model_state.presharpen_amount != 0:
            fai_ip.gaussian_sharpen(sigma=1.0, power=model_state.presharpen_amount)

        # Apply pre-gamma correction
        pre_gamma_red = model_state.pre_gamma_red
        pre_gamma_green = model_state.pre_gamma_green
        pre_gamma_blue = model_state.pre_gamma_blue
        
        if pre_gamma_red != 1.0 or pre_gamma_green != 1.0 or pre_gamma_blue != 1.0:
            fai_ip.gamma(pre_gamma_red, pre_gamma_green, pre_gamma_blue)
            
        return fai_ip.get_image('HWC')

    def process_face_swap(self, face_align_image: np.ndarray, model_state, dfm_model) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Process face swap with caching and optimization"""
        current_time = time.time()
        
        # Check cache first
        if (self.cache_valid and 
            self.cached_face_align_image is not None and 
            current_time - self.cache_timestamp < self.cache_duration and
            np.array_equal(face_align_image, self.cached_face_align_image)):
            return self.cached_celeb_face, self.cached_celeb_face_mask, self.cached_face_align_mask
        
        # Process the face swap
        start_time = time.time()
        
        # Optimize input image
        optimized_image = self.optimize_face_align_image(face_align_image, model_state)
        
        # Perform face swap
        celeb_face, celeb_face_mask_img, face_align_mask_img = dfm_model.convert(
            optimized_image, morph_factor=model_state.morph_factor
        )
        celeb_face, celeb_face_mask_img, face_align_mask_img = celeb_face[0], celeb_face_mask_img[0], face_align_mask_img[0]

        # Two-pass processing if enabled
        if model_state.two_pass:
            celeb_face, celeb_face_mask_img, _ = dfm_model.convert(celeb_face, morph_factor=model_state.morph_factor)
            celeb_face, celeb_face_mask_img = celeb_face[0], celeb_face_mask_img[0]

        # Apply post-gamma correction
        post_gamma_red = model_state.post_gamma_red
        post_gamma_blue = model_state.post_gamma_blue
        post_gamma_green = model_state.post_gamma_green
        
        if post_gamma_red != 1.0 or post_gamma_blue != 1.0 or post_gamma_green != 1.0:
            celeb_face = ImageProcessor(celeb_face).gamma(post_gamma_red, post_gamma_blue, post_gamma_green).get_image('HWC')

        # Cache results
        if hasattr(self, 'get_state') and self.get_state().enable_caching:
            self.cached_face_align_image = face_align_image.copy()
            self.cached_celeb_face = celeb_face.copy()
            self.cached_celeb_face_mask = celeb_face_mask_img.copy()
            self.cached_face_align_mask = face_align_mask_img.copy()
            self.cache_valid = True
            self.cache_timestamp = current_time

        # Update performance metrics
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)

        return celeb_face, celeb_face_mask_img, face_align_mask_img

    def update_fps_counter(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time

    def on_tick(self):
        state, cs = self.get_state(), self.get_control_sheet()

        # Handle model initialization
        if self.dfm_model_initializer is not None:
            events = self.dfm_model_initializer.process_events()

            if events.prev_status_downloading:
                self.set_busy(True)
                cs.model_dl_progress.disable()

            if events.new_status_downloading:
                self.set_busy(False)
                cs.model_dl_progress.enable()
                cs.model_dl_progress.set_config( lib_csw.Progress.Config(title='@FaceSwapDFM.downloading_model') )
                cs.model_dl_progress.set_progress(0)

            elif events.new_status_initialized:
                self.dfm_model = events.dfm_model
                self.dfm_model_initializer = None

                model_width, model_height = self.dfm_model.get_input_res()

                cs.model_info_label.enable()
                cs.model_info_label.set_config( lib_csw.InfoLabel.Config(info_icon=True,
                                                    info_lines=[f'@FaceSwapDFM.model_information',
                                                                '',
                                                                f'@FaceSwapDFM.filename',
                                                                f'{self.dfm_model.get_model_path().name}',
                                                                '',
                                                                f'@FaceSwapDFM.resolution',
                                                                f'{model_width}x{model_height}',
                                                                '',
                                                                f'Performance Mode: Optimized']) )

                # Enable all controls
                cs.swap_all_faces.enable()
                cs.swap_all_faces.set_flag( state.model_state.swap_all_faces if state.model_state.swap_all_faces is not None else False)

                if self.dfm_model.has_morph_value():
                    cs.morph_factor.enable()
                    cs.morph_factor.set_config(lib_csw.Number.Config(min=0, max=1, step=0.01, decimals=2, allow_instant_update=True))
                    cs.morph_factor.set_number(state.model_state.morph_factor if state.model_state.morph_factor is not None else 0.75)

                cs.presharpen_amount.enable()
                cs.presharpen_amount.set_config(lib_csw.Number.Config(min=0, max=10, step=0.1, decimals=1, allow_instant_update=True))
                cs.presharpen_amount.set_number(state.model_state.presharpen_amount if state.model_state.presharpen_amount is not None else 0)

                # Gamma controls
                for gamma_control in [cs.pre_gamma_red, cs.pre_gamma_green, cs.pre_gamma_blue, 
                                     cs.post_gamma_red, cs.post_gamma_green, cs.post_gamma_blue]:
                    gamma_control.enable()
                    gamma_control.set_config(lib_csw.Number.Config(min=0.01, max=4, step=0.01, decimals=2, allow_instant_update=True))
                    gamma_control.set_number(1.0)

                cs.two_pass.enable()
                cs.two_pass.set_flag(state.model_state.two_pass if state.model_state.two_pass is not None else False)

                # Performance controls
                cs.target_fps.enable()
                cs.target_fps.set_config(lib_csw.Number.Config(min=15, max=60, step=1, decimals=0, allow_instant_update=True))
                cs.target_fps.set_number(state.target_fps if state.target_fps is not None else 30)

                cs.frame_skip_rate.enable()
                cs.frame_skip_rate.set_config(lib_csw.Number.Config(min=0, max=3, step=1, decimals=0, allow_instant_update=True))
                cs.frame_skip_rate.set_number(state.frame_skip_rate if state.frame_skip_rate is not None else 0)

                cs.enable_caching.enable()
                cs.enable_caching.set_flag(state.enable_caching if state.enable_caching is not None else True)

                self.set_busy(False)
                self.reemit_frame_signal.send()

            elif events.new_status_error:
                self.set_busy(False)
                cs.model_dl_error.enable()
                cs.model_dl_error.set_error(events.error)

            if events.download_progress is not None:
                cs.model_dl_progress.set_progress(events.download_progress)

        # Process frames
        if self.pending_bcd is None:
            self.start_profile_timing()

            bcd = self.bc_in.read(timeout=0.005)
            if bcd is not None:
                bcd.assign_weak_heap(self.weak_heap)

                model_state = state.model_state
                dfm_model = self.dfm_model
                
                if all_is_not_None(dfm_model, model_state):
                    # Check if we should skip this frame
                    if self.should_skip_frame():
                        # Skip processing but still pass through the frame
                        self.pending_bcd = bcd
                    else:
                        # Process the frame
                        for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                            if not model_state.swap_all_faces and model_state.face_id != i:
                                continue

                            face_align_image = bcd.get_image(fsi.face_align_image_name)
                            if face_align_image is not None:
                                # Process face swap with optimization
                                celeb_face, celeb_face_mask_img, face_align_mask_img = self.process_face_swap(
                                    face_align_image, model_state, dfm_model
                                )

                                # Set output images
                                fsi.face_align_mask_name = f'{fsi.face_align_image_name}_mask'
                                fsi.face_swap_image_name = f'{fsi.face_align_image_name}_swapped'
                                fsi.face_swap_mask_name  = f'{fsi.face_swap_image_name}_mask'

                                bcd.set_image(fsi.face_align_mask_name, face_align_mask_img)
                                bcd.set_image(fsi.face_swap_image_name, celeb_face)
                                bcd.set_image(fsi.face_swap_mask_name, celeb_face_mask_img)

                        # Update FPS counter
                        self.update_fps_counter()
                        self.last_processed_frame_time = time.time()

                self.stop_profile_timing()
                self.pending_bcd = bcd

        if self.pending_bcd is not None:
            if self.bc_out.is_full_read(1):
                self.bc_out.write(self.pending_bcd)
                self.pending_bcd = None
            else:
                time.sleep(0.001)

    def on_stop(self):
        """Clean up resources"""
        self.stop_processing = True
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
        self.clear_cache()


class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()
            self.model = lib_csw.DynamicSingleSwitch.Client()
            self.model_info_label = lib_csw.InfoLabel.Client()
            self.model_dl_progress = lib_csw.Progress.Client()
            self.model_dl_error = lib_csw.Error.Client()
            self.device = lib_csw.DynamicSingleSwitch.Client()
            self.swap_all_faces = lib_csw.Flag.Client()
            self.face_id = lib_csw.Number.Client()
            self.morph_factor = lib_csw.Number.Client()
            self.presharpen_amount = lib_csw.Number.Client()
            self.pre_gamma_red = lib_csw.Number.Client()
            self.pre_gamma_green = lib_csw.Number.Client()
            self.pre_gamma_blue = lib_csw.Number.Client()
            self.post_gamma_red = lib_csw.Number.Client()
            self.post_gamma_blue = lib_csw.Number.Client()
            self.post_gamma_green = lib_csw.Number.Client()
            self.two_pass = lib_csw.Flag.Client()
            # Performance optimization controls
            self.target_fps = lib_csw.Number.Client()
            self.frame_skip_rate = lib_csw.Number.Client()
            self.enable_caching = lib_csw.Flag.Client()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.model = lib_csw.DynamicSingleSwitch.Host()
            self.model_info_label = lib_csw.InfoLabel.Host()
            self.model_dl_progress = lib_csw.Progress.Host()
            self.model_dl_error = lib_csw.Error.Host()
            self.device = lib_csw.DynamicSingleSwitch.Host()
            self.swap_all_faces = lib_csw.Flag.Host()
            self.face_id = lib_csw.Number.Host()
            self.morph_factor = lib_csw.Number.Host()
            self.presharpen_amount = lib_csw.Number.Host()
            self.pre_gamma_red = lib_csw.Number.Host()
            self.pre_gamma_green = lib_csw.Number.Host()
            self.pre_gamma_blue = lib_csw.Number.Host()
            self.post_gamma_red = lib_csw.Number.Host()
            self.post_gamma_blue = lib_csw.Number.Host()
            self.post_gamma_green = lib_csw.Number.Host()
            self.two_pass = lib_csw.Flag.Host()
            # Performance optimization controls
            self.target_fps = lib_csw.Number.Host()
            self.frame_skip_rate = lib_csw.Number.Host()
            self.enable_caching = lib_csw.Flag.Host()


class ModelState(BackendWorkerState):
    swap_all_faces : bool = None
    face_id : int = None
    morph_factor : float = None
    presharpen_amount : float = None
    pre_gamma_red : float = None
    pre_gamma_blue : float = None
    pre_gamma_green: float = None
    post_gamma_red : float = None
    post_gamma_blue : float = None
    post_gamma_green : float = None
    two_pass : bool = None


class WorkerState(BackendWorkerState):
    def __init__(self):
        super().__init__()
        self.models_state : Dict[str, ModelState] = {}
        self.model_state : ModelState = None
        self.model = None
        self.device = None
        # Performance optimization state
        self.target_fps : int = None
        self.frame_skip_rate : int = None
        self.enable_caching : bool = None 