import hashlib
import mmap
import pickle
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
import psutil

from modelhub import DFLive
from xlib import os as lib_os
from xlib.image.ImageProcessor import ImageProcessor
from xlib.mp import csw as lib_csw
from xlib.python import all_is_not_None

from .BackendBase import (
    BackendConnection,
    BackendDB,
    BackendHost,
    BackendSignal,
    BackendWeakHeap,
    BackendWorker,
    BackendWorkerState,
)


class MemoryOptimizedFaceSwap(BackendHost):
    def __init__(
        self,
        weak_heap: BackendWeakHeap,
        reemit_frame_signal: BackendSignal,
        bc_in: BackendConnection,
        bc_out: BackendConnection,
        dfm_models_path: Path,
        backend_db: BackendDB = None,
        id: int = 0,
    ):
        self._id = id
        super().__init__(
            backend_db=backend_db,
            sheet_cls=Sheet,
            worker_cls=MemoryOptimizedFaceSwapWorker,
            worker_state_cls=WorkerState,
            worker_start_args=[
                weak_heap,
                reemit_frame_signal,
                bc_in,
                bc_out,
                dfm_models_path,
            ],
        )

    def get_control_sheet(self) -> "Sheet.Host":
        return super().get_control_sheet()

    def _get_name(self):
        return super()._get_name()  # + f'{self._id}'


class RAMCache:
    """High-performance RAM-based cache for face swap results"""

    def __init__(self, max_size_mb: int = 2048):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.cache = {}
        self.access_times = {}
        self.lock = threading.RLock()

        # Memory mapping for large objects
        self.mmap_cache = {}
        self.mmap_files = {}

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _get_memory_hash(self, data: np.ndarray) -> str:
        """Generate hash for numpy array"""
        return hashlib.md5(data.tobytes()).hexdigest()

    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of object"""
        if isinstance(obj, np.ndarray):
            return obj.nbytes
        elif isinstance(obj, dict):
            return sum(self._estimate_size(v) for v in obj.values())
        elif isinstance(obj, (list, tuple)):
            return sum(self._estimate_size(item) for item in obj)
        else:
            return len(pickle.dumps(obj))

    def _evict_oldest(self, needed_size: int):
        """Evict oldest entries to make space"""
        while self.current_size + needed_size > self.max_size_bytes and self.cache:
            oldest_key = min(
                self.access_times.keys(), key=lambda k: self.access_times[k]
            )
            self._remove_entry(oldest_key)
            self.evictions += 1

    def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.cache:
            size = self._estimate_size(self.cache[key])
            self.current_size -= size
            del self.cache[key]
            del self.access_times[key]

        if key in self.mmap_cache:
            size = self._estimate_size(self.mmap_cache[key])
            self.current_size -= size
            del self.mmap_cache[key]
            if key in self.mmap_files:
                self.mmap_files[key].close()
                del self.mmap_files[key]

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                self.hits += 1
                return self.cache[key]
            elif key in self.mmap_cache:
                self.access_times[key] = time.time()
                self.hits += 1
                return self.mmap_cache[key]
            else:
                self.misses += 1
                return None

    def put(self, key: str, value: Any):
        """Put item in cache with memory management"""
        with self.lock:
            size = self._estimate_size(value)

            # Remove existing entry if present
            if key in self.cache or key in self.mmap_cache:
                self._remove_entry(key)

            # Check if we need to evict
            if self.current_size + size > self.max_size_bytes:
                self._evict_oldest(size)

            # Store in appropriate cache
            if size > 10 * 1024 * 1024:  # 10MB threshold for mmap
                self._store_mmap(key, value, size)
            else:
                self.cache[key] = value
                self.current_size += size

            self.access_times[key] = time.time()

    def _store_mmap(self, key: str, value: Any, size: int):
        """Store large objects using memory mapping"""
        try:
            # Create temporary file
            temp_file = Path(f"temp_cache_{key}.mmap")
            with open(temp_file, "wb") as f:
                pickle.dump(value, f)

            # Memory map the file
            with open(temp_file, "rb") as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                self.mmap_cache[key] = pickle.loads(mm.read())
                self.mmap_files[key] = mm

            # Clean up temp file
            temp_file.unlink(missing_ok=True)
            self.current_size += size

        except Exception as e:
            print(f"MMAP storage failed for {key}: {e}")
            # Fallback to regular cache
            self.cache[key] = value
            self.current_size += size

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "evictions": self.evictions,
                "current_size_mb": self.current_size / (1024 * 1024),
                "max_size_mb": self.max_size_bytes / (1024 * 1024),
                "entries": len(self.cache) + len(self.mmap_cache),
            }

    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()

            for mm in self.mmap_files.values():
                mm.close()
            self.mmap_cache.clear()
            self.mmap_files.clear()

            self.current_size = 0
            self.hits = 0
            self.misses = 0
            self.evictions = 0


class MemoryOptimizedFaceSwapWorker(BackendWorker):
    def get_state(self) -> "WorkerState":
        return super().get_state()

    def get_control_sheet(self) -> "Sheet.Worker":
        return super().get_control_sheet()

    def on_start(
        self,
        weak_heap: BackendWeakHeap,
        reemit_frame_signal: BackendSignal,
        bc_in: BackendConnection,
        bc_out: BackendConnection,
        dfm_models_path: Path,
    ):
        self.weak_heap = weak_heap
        self.reemit_frame_signal = reemit_frame_signal
        self.bc_in = bc_in
        self.bc_out = bc_out
        self.dfm_models_path = dfm_models_path

        self.pending_bcd = None
        self.dfm_model_initializer = None
        self.dfm_model = None

        # Memory optimization components
        self.ram_cache = RAMCache(max_size_mb=2048)  # 2GB RAM cache
        self.preprocessing_cache = {}
        self.postprocessing_cache = {}

        # Memory management
        self.memory_monitor_thread = None
        self.memory_monitoring = False
        self.available_ram = psutil.virtual_memory().total / (1024**3)  # GB

        # Performance tracking
        self.processing_times = []
        self.cache_hit_rates = []
        self.memory_usage = []

        # Threading for parallel processing
        self.processing_queue = []
        self.processing_lock = threading.Lock()
        self.worker_threads = []
        self.max_workers = min(4, psutil.cpu_count())

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
        cs.ram_cache_size.call_on_number(self.on_cs_ram_cache_size)
        cs.enable_preprocessing_cache.call_on_flag(
            self.on_cs_enable_preprocessing_cache
        )
        cs.enable_postprocessing_cache.call_on_flag(
            self.on_cs_enable_postprocessing_cache
        )
        cs.parallel_processing.call_on_flag(self.on_cs_parallel_processing)

        cs.device.enable()
        cs.device.set_choices(
            DFLive.get_available_devices(), none_choice_name="@misc.menu_select"
        )
        cs.device.select(state.device)

        # Start memory monitoring
        self.start_memory_monitoring()

    def start_memory_monitoring(self):
        """Start memory usage monitoring"""
        if not self.memory_monitoring:
            self.memory_monitoring = True
            self.memory_monitor_thread = threading.Thread(
                target=self._memory_monitor_loop, daemon=True
            )
            self.memory_monitor_thread.start()

    def _memory_monitor_loop(self):
        """Monitor memory usage and optimize cache"""
        while self.memory_monitoring:
            try:
                memory = psutil.virtual_memory()
                self.memory_usage.append(memory.percent)

                # Keep only last 60 readings
                if len(self.memory_usage) > 60:
                    self.memory_usage.pop(0)

                # Adjust cache size based on available memory
                if memory.percent > 85:
                    # High memory usage, reduce cache
                    new_size = max(512, self.ram_cache.max_size_bytes // 2)
                    self.ram_cache.max_size_bytes = new_size
                elif (
                    memory.percent < 60 and memory.available > 4 * 1024**3
                ):  # 4GB available
                    # Low memory usage, increase cache
                    new_size = min(
                        4096 * 1024 * 1024, self.ram_cache.max_size_bytes * 2
                    )  # Max 4GB
                    self.ram_cache.max_size_bytes = new_size

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                print(f"Memory monitoring error: {e}")
                time.sleep(5)

    def on_cs_device(self, idx, device):
        state, cs = self.get_state(), self.get_control_sheet()
        if device is not None and state.device == device:
            cs.model.enable()
            cs.model.set_choices(
                DFLive.get_available_models_info(self.dfm_models_path),
                none_choice_name="@misc.menu_select",
            )
            cs.model.select(state.model)
        else:
            state.device = device
            self.save_state()
            self.restart()

    def on_cs_model(self, idx, model):
        state, cs = self.get_state(), self.get_control_sheet()

        if state.model == model:
            state.model_state = state.models_state[model.get_name()] = (
                state.models_state.get(model.get_name(), ModelState())
            )
            self.dfm_model_initializer = DFLive.DFMModel_from_info(
                state.model, state.device
            )
            self.set_busy(True)
            # Clear caches when model changes
            self.clear_caches()
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
                cs.face_id.set_config(
                    lib_csw.Number.Config(
                        min=0, max=999, step=1, decimals=0, allow_instant_update=True
                    )
                )
                cs.face_id.set_number(
                    state.model_state.face_id
                    if state.model_state.face_id is not None
                    else 0
                )
            else:
                cs.face_id.disable()

            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_face_id(self, face_id):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.face_id.get_config()
            face_id = model_state.face_id = int(np.clip(face_id, cfg.min, cfg.max))
            cs.face_id.set_number(face_id)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_presharpen_amount(self, presharpen_amount):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.presharpen_amount.get_config()
            presharpen_amount = model_state.presharpen_amount = float(
                np.clip(presharpen_amount, cfg.min, cfg.max)
            )
            cs.presharpen_amount.set_number(presharpen_amount)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_morph_factor(self, morph_factor):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.morph_factor.get_config()
            morph_factor = model_state.morph_factor = float(
                np.clip(morph_factor, cfg.min, cfg.max)
            )
            cs.morph_factor.set_number(morph_factor)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_pre_gamma_red(self, pre_gamma_red):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_red.get_config()
            pre_gamma_red = model_state.pre_gamma_red = float(
                np.clip(pre_gamma_red, cfg.min, cfg.max)
            )
            cs.pre_gamma_red.set_number(pre_gamma_red)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_pre_gamma_green(self, pre_gamma_green):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_green.get_config()
            pre_gamma_green = model_state.pre_gamma_green = float(
                np.clip(pre_gamma_green, cfg.min, cfg.max)
            )
            cs.pre_gamma_green.set_number(pre_gamma_green)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_pre_gamma_blue(self, pre_gamma_blue):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.pre_gamma_blue.get_config()
            pre_gamma_blue = model_state.pre_gamma_blue = float(
                np.clip(pre_gamma_blue, cfg.min, cfg.max)
            )
            cs.pre_gamma_blue.set_number(pre_gamma_blue)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_post_gamma_red(self, post_gamma_red):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_red.get_config()
            post_gamma_red = model_state.post_gamma_red = float(
                np.clip(post_gamma_red, cfg.min, cfg.max)
            )
            cs.post_gamma_red.set_number(post_gamma_red)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_post_gamma_blue(self, post_gamma_blue):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_blue.get_config()
            post_gamma_blue = model_state.post_gamma_blue = float(
                np.clip(post_gamma_blue, cfg.min, cfg.max)
            )
            cs.post_gamma_blue.set_number(post_gamma_blue)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_post_gamma_green(self, post_gamma_green):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            cfg = cs.post_gamma_green.get_config()
            post_gamma_green = model_state.post_gamma_green = float(
                np.clip(post_gamma_green, cfg.min, cfg.max)
            )
            cs.post_gamma_green.set_number(post_gamma_green)
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_two_pass(self, two_pass):
        state, cs = self.get_state(), self.get_control_sheet()
        model_state = state.model_state
        if model_state is not None:
            model_state.two_pass = two_pass
            self.save_state()
            self.reemit_frame_signal.send()

    def on_cs_ram_cache_size(self, ram_cache_size):
        state, cs = self.get_state(), self.get_control_sheet()
        # Convert MB to bytes
        new_size = int(ram_cache_size * 1024 * 1024)
        self.ram_cache.max_size_bytes = new_size
        state.ram_cache_size = ram_cache_size
        self.save_state()

    def on_cs_enable_preprocessing_cache(self, enable_preprocessing_cache):
        state, cs = self.get_state(), self.get_control_sheet()
        state.enable_preprocessing_cache = enable_preprocessing_cache
        if not enable_preprocessing_cache:
            self.preprocessing_cache.clear()
        self.save_state()

    def on_cs_enable_postprocessing_cache(self, enable_postprocessing_cache):
        state, cs = self.get_state(), self.get_control_sheet()
        state.enable_postprocessing_cache = enable_postprocessing_cache
        if not enable_postprocessing_cache:
            self.postprocessing_cache.clear()
        self.save_state()

    def on_cs_parallel_processing(self, parallel_processing):
        state, cs = self.get_state(), self.get_control_sheet()
        state.parallel_processing = parallel_processing
        self.max_workers = min(4, psutil.cpu_count()) if parallel_processing else 1
        self.save_state()

    def clear_caches(self):
        """Clear all caches"""
        self.ram_cache.clear()
        self.preprocessing_cache.clear()
        self.postprocessing_cache.clear()

    def _get_cache_key(self, face_align_image: np.ndarray, model_state) -> str:
        """Generate cache key for face processing"""
        # Create a hash of the input image and processing parameters
        image_hash = hashlib.md5(face_align_image.tobytes()).hexdigest()
        params_hash = hashlib.md5(
            str(sorted(model_state.__dict__.items())).encode()
        ).hexdigest()
        return f"{image_hash}_{params_hash}"

    def _preprocess_face_align_image(
        self, face_align_image: np.ndarray, model_state
    ) -> np.ndarray:
        """Preprocess face align image with caching"""
        if (
            not hasattr(self.get_state(), "enable_preprocessing_cache")
            or not self.get_state().enable_preprocessing_cache
        ):
            return self._apply_preprocessing(face_align_image, model_state)

        cache_key = f"pre_{self._get_cache_key(face_align_image, model_state)}"
        cached_result = self.preprocessing_cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        result = self._apply_preprocessing(face_align_image, model_state)
        self.preprocessing_cache[cache_key] = result

        # Limit cache size
        if len(self.preprocessing_cache) > 100:
            # Remove oldest entries
            oldest_key = next(iter(self.preprocessing_cache))
            del self.preprocessing_cache[oldest_key]

        return result

    def _apply_preprocessing(
        self, face_align_image: np.ndarray, model_state
    ) -> np.ndarray:
        """Apply preprocessing to face align image"""
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

        return fai_ip.get_image("HWC")

    def _postprocess_face_swap_result(
        self, celeb_face: np.ndarray, model_state
    ) -> np.ndarray:
        """Postprocess face swap result with caching"""
        if (
            not hasattr(self.get_state(), "enable_postprocessing_cache")
            or not self.get_state().enable_postprocessing_cache
        ):
            return self._apply_postprocessing(celeb_face, model_state)

        cache_key = f"post_{self._get_cache_key(celeb_face, model_state)}"
        cached_result = self.postprocessing_cache.get(cache_key)

        if cached_result is not None:
            return cached_result

        result = self._apply_postprocessing(celeb_face, model_state)
        self.postprocessing_cache[cache_key] = result

        # Limit cache size
        if len(self.postprocessing_cache) > 100:
            oldest_key = next(iter(self.postprocessing_cache))
            del self.postprocessing_cache[oldest_key]

        return result

    def _apply_postprocessing(self, celeb_face: np.ndarray, model_state) -> np.ndarray:
        """Apply postprocessing to face swap result"""
        post_gamma_red = model_state.post_gamma_red
        post_gamma_blue = model_state.post_gamma_blue
        post_gamma_green = model_state.post_gamma_green

        if post_gamma_red != 1.0 or post_gamma_blue != 1.0 or post_gamma_green != 1.0:
            return (
                ImageProcessor(celeb_face)
                .gamma(post_gamma_red, post_gamma_blue, post_gamma_green)
                .get_image("HWC")
            )

        return celeb_face

    def _process_face_swap_with_ram_cache(
        self, face_align_image: np.ndarray, model_state, dfm_model
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Process face swap with RAM caching"""
        cache_key = self._get_cache_key(face_align_image, model_state)

        # Check RAM cache first
        cached_result = self.ram_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Process the face swap
        start_time = time.time()

        # Preprocess input image
        optimized_image = self._preprocess_face_align_image(
            face_align_image, model_state
        )

        # Perform face swap
        celeb_face, celeb_face_mask_img, face_align_mask_img = dfm_model.convert(
            optimized_image, morph_factor=model_state.morph_factor
        )
        celeb_face, celeb_face_mask_img, face_align_mask_img = (
            celeb_face[0],
            celeb_face_mask_img[0],
            face_align_mask_img[0],
        )

        # Two-pass processing if enabled
        if model_state.two_pass:
            celeb_face, celeb_face_mask_img, _ = dfm_model.convert(
                celeb_face, morph_factor=model_state.morph_factor
            )
            celeb_face, celeb_face_mask_img = celeb_face[0], celeb_face_mask_img[0]

        # Postprocess result
        celeb_face = self._postprocess_face_swap_result(celeb_face, model_state)

        # Cache result in RAM
        result = (celeb_face, celeb_face_mask_img, face_align_mask_img)
        self.ram_cache.put(cache_key, result)

        # Update performance metrics
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        self.processing_times.append(processing_time)
        if len(self.processing_times) > 100:
            self.processing_times.pop(0)

        return result

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
                cs.model_dl_progress.set_config(
                    lib_csw.Progress.Config(title="@FaceSwapDFM.downloading_model")
                )
                cs.model_dl_progress.set_progress(0)

            elif events.new_status_initialized:
                self.dfm_model = events.dfm_model
                self.dfm_model_initializer = None

                model_width, model_height = self.dfm_model.get_input_res()

                cs.model_info_label.enable()
                cs.model_info_label.set_config(
                    lib_csw.InfoLabel.Config(
                        info_icon=True,
                        info_lines=[
                            f"@FaceSwapDFM.model_information",
                            "",
                            f"@FaceSwapDFM.filename",
                            f"{self.dfm_model.get_model_path().name}",
                            "",
                            f"@FaceSwapDFM.resolution",
                            f"{model_width}x{model_height}",
                            "",
                            f"Memory Mode: RAM Optimized",
                            f"Available RAM: {self.available_ram:.1f}GB",
                        ],
                    )
                )

                # Enable all controls
                cs.swap_all_faces.enable()
                cs.swap_all_faces.set_flag(
                    state.model_state.swap_all_faces
                    if state.model_state.swap_all_faces is not None
                    else False
                )

                if self.dfm_model.has_morph_value():
                    cs.morph_factor.enable()
                    cs.morph_factor.set_config(
                        lib_csw.Number.Config(
                            min=0,
                            max=1,
                            step=0.01,
                            decimals=2,
                            allow_instant_update=True,
                        )
                    )
                    cs.morph_factor.set_number(
                        state.model_state.morph_factor
                        if state.model_state.morph_factor is not None
                        else 0.75
                    )

                cs.presharpen_amount.enable()
                cs.presharpen_amount.set_config(
                    lib_csw.Number.Config(
                        min=0, max=10, step=0.1, decimals=1, allow_instant_update=True
                    )
                )
                cs.presharpen_amount.set_number(
                    state.model_state.presharpen_amount
                    if state.model_state.presharpen_amount is not None
                    else 0
                )

                # Gamma controls
                for gamma_control in [
                    cs.pre_gamma_red,
                    cs.pre_gamma_green,
                    cs.pre_gamma_blue,
                    cs.post_gamma_red,
                    cs.post_gamma_green,
                    cs.post_gamma_blue,
                ]:
                    gamma_control.enable()
                    gamma_control.set_config(
                        lib_csw.Number.Config(
                            min=0.01,
                            max=4,
                            step=0.01,
                            decimals=2,
                            allow_instant_update=True,
                        )
                    )
                    gamma_control.set_number(1.0)

                cs.two_pass.enable()
                cs.two_pass.set_flag(
                    state.model_state.two_pass
                    if state.model_state.two_pass is not None
                    else False
                )

                # Memory optimization controls
                cs.ram_cache_size.enable()
                cs.ram_cache_size.set_config(
                    lib_csw.Number.Config(
                        min=512,
                        max=8192,
                        step=256,
                        decimals=0,
                        allow_instant_update=True,
                    )
                )
                cs.ram_cache_size.set_number(
                    state.ram_cache_size if state.ram_cache_size is not None else 2048
                )

                cs.enable_preprocessing_cache.enable()
                cs.enable_preprocessing_cache.set_flag(
                    state.enable_preprocessing_cache
                    if state.enable_preprocessing_cache is not None
                    else True
                )

                cs.enable_postprocessing_cache.enable()
                cs.enable_postprocessing_cache.set_flag(
                    state.enable_postprocessing_cache
                    if state.enable_postprocessing_cache is not None
                    else True
                )

                cs.parallel_processing.enable()
                cs.parallel_processing.set_flag(
                    state.parallel_processing
                    if state.parallel_processing is not None
                    else True
                )

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
                    for i, fsi in enumerate(bcd.get_face_swap_info_list()):
                        if not model_state.swap_all_faces and model_state.face_id != i:
                            continue

                        face_align_image = bcd.get_image(fsi.face_align_image_name)
                        if face_align_image is not None:
                            # Process face swap with RAM caching
                            (
                                celeb_face,
                                celeb_face_mask_img,
                                face_align_mask_img,
                            ) = self._process_face_swap_with_ram_cache(
                                face_align_image, model_state, dfm_model
                            )

                            # Set output images
                            fsi.face_align_mask_name = (
                                f"{fsi.face_align_image_name}_mask"
                            )
                            fsi.face_swap_image_name = (
                                f"{fsi.face_align_image_name}_swapped"
                            )
                            fsi.face_swap_mask_name = f"{fsi.face_swap_image_name}_mask"

                            bcd.set_image(fsi.face_align_mask_name, face_align_mask_img)
                            bcd.set_image(fsi.face_swap_image_name, celeb_face)
                            bcd.set_image(fsi.face_swap_mask_name, celeb_face_mask_img)

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
        self.memory_monitoring = False
        if self.memory_monitor_thread and self.memory_monitor_thread.is_alive():
            self.memory_monitor_thread.join(timeout=1.0)

        self.clear_caches()


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
            # Memory optimization controls
            self.ram_cache_size = lib_csw.Number.Client()
            self.enable_preprocessing_cache = lib_csw.Flag.Client()
            self.enable_postprocessing_cache = lib_csw.Flag.Client()
            self.parallel_processing = lib_csw.Flag.Client()

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
            # Memory optimization controls
            self.ram_cache_size = lib_csw.Number.Host()
            self.enable_preprocessing_cache = lib_csw.Flag.Host()
            self.enable_postprocessing_cache = lib_csw.Flag.Host()
            self.parallel_processing = lib_csw.Flag.Host()


class ModelState(BackendWorkerState):
    swap_all_faces: bool = None
    face_id: int = None
    morph_factor: float = None
    presharpen_amount: float = None
    pre_gamma_red: float = None
    pre_gamma_blue: float = None
    pre_gamma_green: float = None
    post_gamma_red: float = None
    post_gamma_blue: float = None
    post_gamma_green: float = None
    two_pass: bool = None


class WorkerState(BackendWorkerState):
    def __init__(self):
        super().__init__()
        self.models_state: Dict[str, ModelState] = {}
        self.model_state: ModelState = None
        self.model = None
        self.device = None
        # Memory optimization state
        self.ram_cache_size: int = None
        self.enable_preprocessing_cache: bool = None
        self.enable_postprocessing_cache: bool = None
        self.parallel_processing: bool = None
