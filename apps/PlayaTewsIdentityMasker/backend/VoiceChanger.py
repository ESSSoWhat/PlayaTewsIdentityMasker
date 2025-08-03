import collections
import logging
import queue
import threading
import time
from enum import IntEnum
from typing import Any, Dict, Optional

import librosa
import numpy as np
import pyaudio
import soundfile as sf
import webrtcvad
from scipy import signal
from scipy.fft import fft, ifft

from xlib.mp import csw as lib_csw

from .BackendBase import (
    BackendConnection,
    BackendDB,
    BackendHost,
    BackendSignal,
    BackendWeakHeap,
    BackendWorker,
    BackendWorkerState,
)


class VoiceEffectType(IntEnum):
    NONE = 0
    PITCH_SHIFT = 1
    FORMANT_SHIFT = 2
    ROBOT = 3
    HELIUM = 4
    DEEP = 5
    ECHO = 6
    REVERB = 7
    CHORUS = 8
    DISTORTION = 9
    AUTOTUNE = 10
    # New realistic voice effects
    MALE_VOICE = 11
    FEMALE_VOICE = 12
    CHILD_VOICE = 13
    ELDERLY_VOICE = 14
    BRITISH_ACCENT = 15
    SOUTHERN_ACCENT = 16


class VoiceChanger(BackendHost):
    """
    Real-time voice changer with multiple audio effects and realistic voice transformations
    """

    def __init__(self, weak_heap: BackendWeakHeap, backend_db: BackendDB = None):
        super().__init__(
            backend_db=backend_db,
            sheet_cls=Sheet,
            worker_cls=VoiceChangerWorker,
            worker_state_cls=WorkerState,
            worker_start_args=[weak_heap],
        )

    def get_control_sheet(self) -> "Sheet.Host":
        return super().get_control_sheet()


class VoiceChangerWorker(BackendWorker):
    def get_state(self) -> "WorkerState":
        return super().get_state()

    def get_control_sheet(self) -> "Sheet.Worker":
        return super().get_control_sheet()

    def on_start(self, weak_heap: BackendWeakHeap):
        self.weak_heap = weak_heap
        self.logger = logging.getLogger(__name__)

        # Audio settings with better compatibility
        self.sample_rate = 44100
        self.chunk_size = 2048  # Increased for better stability
        self.channels = 1
        self.format = pyaudio.paFloat32

        # Audio processing components
        try:
            self.audio = pyaudio.PyAudio()
        except Exception as e:
            self.logger.error(f"Failed to initialize PyAudio: {e}")
            self.audio = None

        self.input_stream = None
        self.output_stream = None

        # Audio buffers
        self.input_queue = queue.Queue(maxsize=50)  # Reduced for lower latency
        self.output_queue = queue.Queue(maxsize=50)

        # Processing threads
        self.input_thread = None
        self.output_thread = None
        self.processing_thread = None
        self.running = False

        # Voice Activity Detection
        try:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        except Exception as e:
            self.logger.warning(f"VAD initialization failed: {e}")
            self.vad = None

        # Effect parameters with realistic voice settings
        self.current_effect = VoiceEffectType.NONE
        self.effect_params = {
            "pitch_shift": 0.0,  # Semitones
            "formant_shift": 1.0,  # Multiplier
            "robot_rate": 0.1,  # Hz
            "echo_delay": 0.3,  # seconds
            "echo_decay": 0.5,  # 0-1
            "reverb_room_size": 0.8,  # 0-1
            "reverb_damping": 0.5,  # 0-1
            "chorus_rate": 1.5,  # Hz
            "chorus_depth": 0.002,  # seconds
            "distortion_amount": 0.3,  # 0-1
            "autotune_sensitivity": 0.1,  # 0-1
            # New realistic voice parameters
            "voice_gender": 0.5,  # 0=female, 1=male
            "voice_age": 0.5,  # 0=child, 1=elderly
            "accent_strength": 0.7,  # 0-1
            "breathiness": 0.2,  # 0-1
            "clarity": 0.8,  # 0-1
        }

        # Initialize control sheet
        state, cs = self.get_state(), self.get_control_sheet()

        # Setup callbacks
        cs.enabled.call_on_flag(self.on_cs_enabled)
        cs.effect_type.call_on_selected(self.on_cs_effect_type)
        cs.pitch_shift.call_on_number(self.on_cs_pitch_shift)
        cs.formant_shift.call_on_number(self.on_cs_formant_shift)
        cs.robot_rate.call_on_number(self.on_cs_robot_rate)
        cs.echo_delay.call_on_number(self.on_cs_echo_delay)
        cs.echo_decay.call_on_number(self.on_cs_echo_decay)
        cs.reverb_room_size.call_on_number(self.on_cs_reverb_room_size)
        cs.reverb_damping.call_on_number(self.on_cs_reverb_damping)
        cs.chorus_rate.call_on_number(self.on_cs_chorus_rate)
        cs.chorus_depth.call_on_number(self.on_cs_chorus_depth)
        cs.distortion_amount.call_on_number(self.on_cs_distortion_amount)
        cs.autotune_sensitivity.call_on_number(self.on_cs_autotune_sensitivity)
        cs.input_device.call_on_selected(self.on_cs_input_device)
        cs.output_device.call_on_selected(self.on_cs_output_device)

        # Initialize UI controls
        cs.enabled.set_flag(state.enabled if state.enabled is not None else False)

        # Note: Client objects don't have set_choices method
        # The choices will be set by the Host side when the UI is created
        cs.effect_type.select(
            state.effect_type if state.effect_type is not None else VoiceEffectType.NONE
        )

        # Initialize parameter controls
        self._init_parameter_controls(cs, state)

        # Initialize device lists
        self._init_device_lists(cs, state)

    def _init_parameter_controls(self, cs, state):
        """Initialize all parameter controls"""
        # Note: Client objects don't have set_config method
        # The configuration will be set by the Host side when the UI is created

        # Pitch shift
        cs.pitch_shift.set_number(
            state.pitch_shift if state.pitch_shift is not None else 0.0
        )

        # Formant shift
        cs.formant_shift.set_number(
            state.formant_shift if state.formant_shift is not None else 1.0
        )

        # Robot rate
        cs.robot_rate.set_number(
            state.robot_rate if state.robot_rate is not None else 0.1
        )

        # Echo parameters
        cs.echo_delay.set_number(
            state.echo_delay if state.echo_delay is not None else 0.3
        )

        cs.echo_decay.set_number(
            state.echo_decay if state.echo_decay is not None else 0.5
        )

        # Reverb parameters
        cs.reverb_room_size.set_number(
            state.reverb_room_size if state.reverb_room_size is not None else 0.8
        )

        cs.reverb_damping.set_number(
            state.reverb_damping if state.reverb_damping is not None else 0.5
        )

        # Chorus parameters
        cs.chorus_rate.set_number(
            state.chorus_rate if state.chorus_rate is not None else 1.5
        )

        cs.chorus_depth.set_number(
            state.chorus_depth if state.chorus_depth is not None else 0.002
        )

        # Distortion
        cs.distortion_amount.set_number(
            state.distortion_amount if state.distortion_amount is not None else 0.3
        )

        # Autotune
        cs.autotune_sensitivity.set_number(
            state.autotune_sensitivity
            if state.autotune_sensitivity is not None
            else 0.1
        )

    def _init_device_lists(self, cs, state):
        """Initialize input and output device lists with error handling"""
        # Get available devices
        input_devices = []
        output_devices = []

        if self.audio is None:
            self.logger.error("PyAudio not initialized, cannot get device list")
            return

        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info["maxInputChannels"] > 0:
                    input_devices.append((i, device_info["name"]))
                if device_info["maxOutputChannels"] > 0:
                    output_devices.append((i, device_info["name"]))
        except Exception as e:
            self.logger.error(f"Failed to get device list: {e}")
            return

        # Set up input device control
        # Note: Client objects don't have set_choices method
        # The choices will be set by the Host side when the UI is created
        if input_devices:
            default_input = state.input_device if state.input_device is not None else 0
            if default_input < len(input_devices):
                cs.input_device.select(default_input)
            else:
                cs.input_device.select(0)

        # Set up output device control
        # Note: Client objects don't have set_choices method
        # The choices will be set by the Host side when the UI is created
        if output_devices:
            default_output = (
                state.output_device if state.output_device is not None else 0
            )
            if default_output < len(output_devices):
                cs.output_device.select(default_output)
            else:
                cs.output_device.select(0)

    def on_stop(self):
        """Stop all audio processing"""
        self.running = False

        if self.input_thread and self.input_thread.is_alive():
            self.input_thread.join(timeout=1.0)

        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=1.0)

        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)

        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception as e:
                self.logger.warning(f"Error stopping input stream: {e}")

        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception as e:
                self.logger.warning(f"Error stopping output stream: {e}")

        if self.audio:
            try:
                self.audio.terminate()
            except Exception as e:
                self.logger.warning(f"Error terminating PyAudio: {e}")

    def start_audio_processing(self):
        """Start audio processing with error handling"""
        if self.running:
            return

        if self.audio is None:
            self.logger.error("Cannot start audio processing: PyAudio not initialized")
            return

        try:
            # Get device indices
            state, cs = self.get_state(), self.get_control_sheet()
            # Note: Client objects don't have get_selected method
            # Use state values instead
            input_device = state.input_device if state.input_device is not None else 0
            output_device = (
                state.output_device if state.output_device is not None else 0
            )

            if input_device is None or output_device is None:
                self.logger.error("No input or output device selected")
                return

            # Start input stream
            self.input_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=None,
            )

            # Start output stream
            self.output_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=output_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=None,
            )

            self.running = True

            # Start processing threads
            self.input_thread = threading.Thread(target=self._input_worker, daemon=True)
            self.output_thread = threading.Thread(
                target=self._output_worker, daemon=True
            )
            self.processing_thread = threading.Thread(
                target=self._processing_worker, daemon=True
            )

            self.input_thread.start()
            self.output_thread.start()
            self.processing_thread.start()

            self.logger.info("Audio processing started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start audio processing: {e}")
            self.running = False

    def stop_audio_processing(self):
        """Stop audio processing"""
        self.running = False
        self.on_stop()

    def _input_worker(self):
        """Input audio worker thread"""
        while self.running and self.input_stream:
            try:
                data = self.input_stream.read(
                    self.chunk_size, exception_on_overflow=False
                )
                audio_data = np.frombuffer(data, dtype=np.float32)

                if not self.input_queue.full():
                    self.input_queue.put(audio_data)

            except Exception as e:
                self.logger.warning(f"Input worker error: {e}")
                time.sleep(0.01)

    def _processing_worker(self):
        """Audio processing worker thread"""
        while self.running:
            try:
                if not self.input_queue.empty():
                    audio_data = self.input_queue.get()

                    # Apply effects
                    processed_audio = self._apply_effects(audio_data)

                    if not self.output_queue.full():
                        self.output_queue.put(processed_audio)
                else:
                    time.sleep(0.001)  # Small delay to prevent busy waiting

            except Exception as e:
                self.logger.warning(f"Processing worker error: {e}")
                time.sleep(0.01)

    def _output_worker(self):
        """Output audio worker thread"""
        while self.running and self.output_stream:
            try:
                if not self.output_queue.empty():
                    audio_data = self.output_queue.get()
                    output_data = audio_data.astype(np.float32).tobytes()
                    self.output_stream.write(output_data)
                else:
                    time.sleep(0.001)  # Small delay to prevent busy waiting

            except Exception as e:
                self.logger.warning(f"Output worker error: {e}")
                time.sleep(0.01)

    def _apply_effects(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply selected effects to audio data"""
        if self.current_effect == VoiceEffectType.NONE:
            return audio_data

        try:
            if self.current_effect == VoiceEffectType.PITCH_SHIFT:
                return self._pitch_shift(audio_data)
            elif self.current_effect == VoiceEffectType.FORMANT_SHIFT:
                return self._formant_shift(audio_data)
            elif self.current_effect == VoiceEffectType.ROBOT:
                return self._robot_effect(audio_data)
            elif self.current_effect == VoiceEffectType.HELIUM:
                return self._helium_effect(audio_data)
            elif self.current_effect == VoiceEffectType.DEEP:
                return self._deep_effect(audio_data)
            elif self.current_effect == VoiceEffectType.ECHO:
                return self._echo_effect(audio_data)
            elif self.current_effect == VoiceEffectType.REVERB:
                return self._reverb_effect(audio_data)
            elif self.current_effect == VoiceEffectType.CHORUS:
                return self._chorus_effect(audio_data)
            elif self.current_effect == VoiceEffectType.DISTORTION:
                return self._distortion_effect(audio_data)
            elif self.current_effect == VoiceEffectType.AUTOTUNE:
                return self._autotune_effect(audio_data)
            elif self.current_effect == VoiceEffectType.MALE_VOICE:
                return self._male_voice_effect(audio_data)
            elif self.current_effect == VoiceEffectType.FEMALE_VOICE:
                return self._female_voice_effect(audio_data)
            elif self.current_effect == VoiceEffectType.CHILD_VOICE:
                return self._child_voice_effect(audio_data)
            elif self.current_effect == VoiceEffectType.ELDERLY_VOICE:
                return self._elderly_voice_effect(audio_data)
            elif self.current_effect == VoiceEffectType.BRITISH_ACCENT:
                return self._british_accent_effect(audio_data)
            elif self.current_effect == VoiceEffectType.SOUTHERN_ACCENT:
                return self._southern_accent_effect(audio_data)
            else:
                return audio_data

        except Exception as e:
            self.logger.warning(f"Effect application error: {e}")
            return audio_data

    def _pitch_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Pitch shift effect"""
        try:
            pitch_shift = self.effect_params["pitch_shift"]
            if abs(pitch_shift) < 0.1:
                return audio_data

            # Use librosa for pitch shifting
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=pitch_shift
            )
            return y_shifted
        except Exception as e:
            self.logger.warning(f"Pitch shift error: {e}")
            return audio_data

    def _formant_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Formant shift effect"""
        try:
            formant_shift = self.effect_params["formant_shift"]
            if abs(formant_shift - 1.0) < 0.1:
                return audio_data

            # Simple formant shifting using spectral envelope manipulation
            stft = librosa.stft(audio_data, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Shift formants by scaling frequency bins
            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(
                freq_bins * formant_shift, 0, magnitude.shape[0] - 1
            ).astype(int)

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            return librosa.istft(shifted_stft)
        except Exception as e:
            self.logger.warning(f"Formant shift error: {e}")
            return audio_data

    def _robot_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Robot voice effect"""
        try:
            robot_rate = self.effect_params["robot_rate"]

            # Create a carrier wave
            t = np.arange(len(audio_data)) / self.sample_rate
            carrier = np.sin(2 * np.pi * robot_rate * t)

            # Modulate the audio
            modulated = audio_data * carrier

            # Add some filtering for robotic character
            b, a = signal.butter(4, 0.3, btype="low")
            filtered = signal.filtfilt(b, a, modulated)

            return filtered
        except Exception as e:
            self.logger.warning(f"Robot effect error: {e}")
            return audio_data

    def _helium_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Helium voice effect (high pitch + formant shift)"""
        try:
            # High pitch shift
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=8
            )

            # Formant shift to higher frequencies
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Shift formants up
            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 1.8, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            return librosa.istft(shifted_stft)
        except Exception as e:
            self.logger.warning(f"Helium effect error: {e}")
            return audio_data

    def _deep_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Deep voice effect (low pitch + formant shift)"""
        try:
            # Low pitch shift
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=-6
            )

            # Formant shift to lower frequencies
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Shift formants down
            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 0.6, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            return librosa.istft(shifted_stft)
        except Exception as e:
            self.logger.warning(f"Deep effect error: {e}")
            return audio_data

    def _echo_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Echo effect"""
        try:
            delay = self.effect_params["echo_delay"]
            decay = self.effect_params["echo_decay"]

            delay_samples = int(delay * self.sample_rate)
            echo = np.zeros_like(audio_data)

            if delay_samples < len(audio_data):
                echo[delay_samples:] = audio_data[:-delay_samples] * decay

            return audio_data + echo
        except Exception as e:
            self.logger.warning(f"Echo effect error: {e}")
            return audio_data

    def _reverb_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Reverb effect"""
        try:
            room_size = self.effect_params["reverb_room_size"]
            damping = self.effect_params["reverb_damping"]

            # Simple reverb using multiple delays
            reverb = np.zeros_like(audio_data)
            delays = [
                int(0.03 * self.sample_rate),
                int(0.05 * self.sample_rate),
                int(0.07 * self.sample_rate),
            ]
            decays = [0.6, 0.4, 0.2]

            for delay, decay in zip(delays, decays):
                if delay < len(audio_data):
                    reverb[delay:] += audio_data[:-delay] * decay * room_size

            return audio_data + reverb * damping
        except Exception as e:
            self.logger.warning(f"Reverb effect error: {e}")
            return audio_data

    def _chorus_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Chorus effect"""
        try:
            rate = self.effect_params["chorus_rate"]
            depth = self.effect_params["chorus_depth"]

            t = np.arange(len(audio_data)) / self.sample_rate
            modulation = np.sin(2 * np.pi * rate * t) * depth * self.sample_rate

            # Create modulated version
            modulated_indices = np.arange(len(audio_data)) + modulation
            modulated_indices = np.clip(
                modulated_indices, 0, len(audio_data) - 1
            ).astype(int)

            chorus = audio_data[modulated_indices]
            return (audio_data + chorus) / 2
        except Exception as e:
            self.logger.warning(f"Chorus effect error: {e}")
            return audio_data

    def _distortion_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Distortion effect"""
        try:
            amount = self.effect_params["distortion_amount"]

            # Soft clipping distortion
            distorted = np.tanh(audio_data * (1 + amount * 5))
            return distorted
        except Exception as e:
            self.logger.warning(f"Distortion effect error: {e}")
            return audio_data

    def _autotune_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Autotune effect"""
        try:
            sensitivity = self.effect_params["autotune_sensitivity"]

            # Simple pitch correction
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=self.sample_rate)

            # Find dominant pitch
            pitch_idx = np.argmax(magnitudes, axis=0)
            pitches = pitches[pitch_idx, np.arange(pitches.shape[1])]

            # Quantize to nearest semitone
            semitones = np.round(12 * np.log2(pitches / 440 + 1e-10))
            corrected_pitches = 440 * (2 ** (semitones / 12))

            # Apply correction
            corrected = librosa.effects.pitch_shift(
                audio_data,
                sr=self.sample_rate,
                n_steps=sensitivity * (corrected_pitches - pitches) / 100,
            )

            return corrected
        except Exception as e:
            self.logger.warning(f"Autotune effect error: {e}")
            return audio_data

    # New realistic voice effects
    def _male_voice_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Realistic male voice transformation"""
        try:
            # Lower pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=-3
            )

            # Lower formants
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 0.7, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            result = librosa.istft(shifted_stft)

            # Add some chest resonance
            b, a = signal.butter(4, [80, 200] / (self.sample_rate / 2), btype="band")
            resonance = signal.filtfilt(b, a, result)

            return result + resonance * 0.3
        except Exception as e:
            self.logger.warning(f"Male voice effect error: {e}")
            return audio_data

    def _female_voice_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Realistic female voice transformation"""
        try:
            # Higher pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=4
            )

            # Higher formants
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 1.3, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            result = librosa.istft(shifted_stft)

            # Add brightness
            b, a = signal.butter(4, 2000 / (self.sample_rate / 2), btype="high")
            brightness = signal.filtfilt(b, a, result)

            return result + brightness * 0.2
        except Exception as e:
            self.logger.warning(f"Female voice effect error: {e}")
            return audio_data

    def _child_voice_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Realistic child voice transformation"""
        try:
            # Higher pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=6
            )

            # Higher formants and smaller vocal tract
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 1.5, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            result = librosa.istft(shifted_stft)

            # Add nasality
            b, a = signal.butter(4, [2000, 3000] / (self.sample_rate / 2), btype="band")
            nasality = signal.filtfilt(b, a, result)

            return result + nasality * 0.4
        except Exception as e:
            self.logger.warning(f"Child voice effect error: {e}")
            return audio_data

    def _elderly_voice_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Realistic elderly voice transformation"""
        try:
            # Slightly lower pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=-1
            )

            # Lower formants and reduced clarity
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            freq_bins = np.arange(magnitude.shape[0])
            shifted_bins = np.clip(freq_bins * 0.8, 0, magnitude.shape[0] - 1).astype(
                int
            )

            shifted_magnitude = magnitude[shifted_bins]
            shifted_stft = shifted_magnitude * np.exp(1j * phase)

            result = librosa.istft(shifted_stft)

            # Reduce high frequencies (aging effect)
            b, a = signal.butter(4, 3000 / (self.sample_rate / 2), btype="low")
            result = signal.filtfilt(b, a, result)

            # Add slight tremor
            t = np.arange(len(result)) / self.sample_rate
            tremor = np.sin(2 * np.pi * 8 * t) * 0.1
            result = result * (1 + tremor)

            return result
        except Exception as e:
            self.logger.warning(f"Elderly voice effect error: {e}")
            return audio_data

    def _british_accent_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """British accent effect (RP accent characteristics)"""
        try:
            # Slightly higher pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=1
            )

            # Emphasize certain frequency ranges characteristic of RP
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Boost frequencies around 2000-3000 Hz (characteristic of British accent)
            freq_bins = np.arange(magnitude.shape[0])
            freq_hz = freq_bins * self.sample_rate / (2 * magnitude.shape[0])

            british_boost = np.where((freq_hz >= 2000) & (freq_hz <= 3000), 1.3, 1.0)
            magnitude = magnitude * british_boost[:, np.newaxis]

            shifted_stft = magnitude * np.exp(1j * phase)
            result = librosa.istft(shifted_stft)

            # Add slight nasality
            b, a = signal.butter(4, [2500, 3500] / (self.sample_rate / 2), btype="band")
            nasality = signal.filtfilt(b, a, result)

            return result + nasality * 0.2
        except Exception as e:
            self.logger.warning(f"British accent effect error: {e}")
            return audio_data

    def _southern_accent_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Southern accent effect (drawl characteristics)"""
        try:
            # Slightly lower pitch
            y_shifted = librosa.effects.pitch_shift(
                audio_data, sr=self.sample_rate, n_steps=-1
            )

            # Emphasize lower frequencies (characteristic of Southern drawl)
            stft = librosa.stft(y_shifted, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Boost frequencies around 500-1500 Hz (characteristic of Southern accent)
            freq_bins = np.arange(magnitude.shape[0])
            freq_hz = freq_bins * self.sample_rate / (2 * magnitude.shape[0])

            southern_boost = np.where((freq_hz >= 500) & (freq_hz <= 1500), 1.4, 1.0)
            magnitude = magnitude * southern_boost[:, np.newaxis]

            shifted_stft = magnitude * np.exp(1j * phase)
            result = librosa.istft(shifted_stft)

            # Add slight drawl effect (slower articulation)
            # This is a simplified version - real drawl would require more complex processing
            b, a = signal.butter(4, 800 / (self.sample_rate / 2), btype="low")
            drawl = signal.filtfilt(b, a, result)

            return result + drawl * 0.3
        except Exception as e:
            self.logger.warning(f"Southern accent effect error: {e}")
            return audio_data

    # Control sheet callbacks
    def on_cs_enabled(self, enabled):
        """Handle enabled state change"""
        if enabled:
            self.start_audio_processing()
        else:
            self.stop_audio_processing()

    def on_cs_effect_type(self, idx, effect_type):
        """Handle effect type change"""
        self.current_effect = effect_type
        self.logger.info(f"Voice effect changed to: {effect_type}")

    def on_cs_pitch_shift(self, pitch_shift):
        """Handle pitch shift change"""
        self.effect_params["pitch_shift"] = pitch_shift

    def on_cs_formant_shift(self, formant_shift):
        """Handle formant shift change"""
        self.effect_params["formant_shift"] = formant_shift

    def on_cs_robot_rate(self, robot_rate):
        """Handle robot rate change"""
        self.effect_params["robot_rate"] = robot_rate

    def on_cs_echo_delay(self, echo_delay):
        """Handle echo delay change"""
        self.effect_params["echo_delay"] = echo_delay

    def on_cs_echo_decay(self, echo_decay):
        """Handle echo decay change"""
        self.effect_params["echo_decay"] = echo_decay

    def on_cs_reverb_room_size(self, reverb_room_size):
        """Handle reverb room size change"""
        self.effect_params["reverb_room_size"] = reverb_room_size

    def on_cs_reverb_damping(self, reverb_damping):
        """Handle reverb damping change"""
        self.effect_params["reverb_damping"] = reverb_damping

    def on_cs_chorus_rate(self, chorus_rate):
        """Handle chorus rate change"""
        self.effect_params["chorus_rate"] = chorus_rate

    def on_cs_chorus_depth(self, chorus_depth):
        """Handle chorus depth change"""
        self.effect_params["chorus_depth"] = chorus_depth

    def on_cs_distortion_amount(self, distortion_amount):
        """Handle distortion amount change"""
        self.effect_params["distortion_amount"] = distortion_amount

    def on_cs_autotune_sensitivity(self, autotune_sensitivity):
        """Handle autotune sensitivity change"""
        self.effect_params["autotune_sensitivity"] = autotune_sensitivity

    def on_cs_input_device(self, idx, device_idx):
        """Handle input device change"""
        if self.running:
            self.stop_audio_processing()
            time.sleep(0.1)
            self.start_audio_processing()

    def on_cs_output_device(self, idx, device_idx):
        """Handle output device change"""
        if self.running:
            self.stop_audio_processing()
            time.sleep(0.1)
            self.start_audio_processing()


class Sheet:
    class Host(lib_csw.Sheet.Host):
        def __init__(self):
            super().__init__()

            self.enabled = lib_csw.Flag.Host()
            self.effect_type = lib_csw.DynamicSingleSwitch.Host()
            self.pitch_shift = lib_csw.Number.Host()
            self.formant_shift = lib_csw.Number.Host()
            self.robot_rate = lib_csw.Number.Host()
            self.echo_delay = lib_csw.Number.Host()
            self.echo_decay = lib_csw.Number.Host()
            self.reverb_room_size = lib_csw.Number.Host()
            self.reverb_damping = lib_csw.Number.Host()
            self.chorus_rate = lib_csw.Number.Host()
            self.chorus_depth = lib_csw.Number.Host()
            self.distortion_amount = lib_csw.Number.Host()
            self.autotune_sensitivity = lib_csw.Number.Host()
            self.input_device = lib_csw.DynamicSingleSwitch.Host()
            self.output_device = lib_csw.DynamicSingleSwitch.Host()

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()

            self.enabled = lib_csw.Flag.Client()
            self.effect_type = lib_csw.DynamicSingleSwitch.Client()
            self.pitch_shift = lib_csw.Number.Client()
            self.formant_shift = lib_csw.Number.Client()
            self.robot_rate = lib_csw.Number.Client()
            self.echo_delay = lib_csw.Number.Client()
            self.echo_decay = lib_csw.Number.Client()
            self.reverb_room_size = lib_csw.Number.Client()
            self.reverb_damping = lib_csw.Number.Client()
            self.chorus_rate = lib_csw.Number.Client()
            self.chorus_depth = lib_csw.Number.Client()
            self.distortion_amount = lib_csw.Number.Client()
            self.autotune_sensitivity = lib_csw.Number.Client()
            self.input_device = lib_csw.DynamicSingleSwitch.Client()
            self.output_device = lib_csw.DynamicSingleSwitch.Client()


class WorkerState(BackendWorkerState):
    enabled: bool = None
    effect_type: VoiceEffectType = None
    pitch_shift: float = None
    formant_shift: float = None
    robot_rate: float = None
    echo_delay: float = None
    echo_decay: float = None
    reverb_room_size: float = None
    reverb_damping: float = None
    chorus_rate: float = None
    chorus_depth: float = None
    distortion_amount: float = None
    autotune_sensitivity: float = None
    input_device: int = None
    output_device: int = None
