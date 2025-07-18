import numpy as np
import pyaudio
import threading
import queue
import time
from enum import IntEnum
from typing import Optional, Dict, Any
import librosa
import soundfile as sf
from scipy import signal
from scipy.fft import fft, ifft
import webrtcvad
import collections

from xlib.mp import csw as lib_csw
from .BackendBase import (BackendConnection, BackendDB, BackendHost,
                          BackendSignal, BackendWeakHeap, BackendWorker,
                          BackendWorkerState)


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


class VoiceChanger(BackendHost):
    """
    Real-time voice changer with multiple audio effects
    """
    def __init__(self, weak_heap: BackendWeakHeap,
                 backend_db: BackendDB = None):
        super().__init__(backend_db=backend_db,
                         sheet_cls=Sheet,
                         worker_cls=VoiceChangerWorker,
                         worker_state_cls=WorkerState,
                         worker_start_args=[weak_heap])

    def get_control_sheet(self) -> 'Sheet.Host': 
        return super().get_control_sheet()


class VoiceChangerWorker(BackendWorker):
    def get_state(self) -> 'WorkerState': 
        return super().get_state()
    
    def get_control_sheet(self) -> 'Sheet.Worker': 
        return super().get_control_sheet()

    def on_start(self, weak_heap: BackendWeakHeap):
        self.weak_heap = weak_heap
        
        # Audio settings
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.channels = 1
        
        # Audio processing components
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        
        # Audio buffers
        self.input_queue = queue.Queue(maxsize=100)
        self.output_queue = queue.Queue(maxsize=100)
        
        # Processing threads
        self.input_thread = None
        self.output_thread = None
        self.processing_thread = None
        self.running = False
        
        # Voice Activity Detection
        self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        # Effect parameters
        self.current_effect = VoiceEffectType.NONE
        self.effect_params = {
            'pitch_shift': 0.0,      # Semitones
            'formant_shift': 1.0,    # Multiplier
            'robot_rate': 0.1,       # Hz
            'echo_delay': 0.3,       # seconds
            'echo_decay': 0.5,       # 0-1
            'reverb_room_size': 0.8, # 0-1
            'reverb_damping': 0.5,   # 0-1
            'chorus_rate': 1.5,      # Hz
            'chorus_depth': 0.002,   # seconds
            'distortion_amount': 0.3, # 0-1
            'autotune_sensitivity': 0.1 # 0-1
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
        cs.enabled.enable()
        cs.enabled.set_flag(state.enabled if state.enabled is not None else False)
        
        cs.effect_type.enable()
        cs.effect_type.set_choices(VoiceEffectType, 
                                  ['None', 'Pitch Shift', 'Formant Shift', 'Robot', 
                                   'Helium', 'Deep', 'Echo', 'Reverb', 'Chorus', 
                                   'Distortion', 'Autotune'],
                                  none_choice_name='@misc.menu_select')
        cs.effect_type.select(state.effect_type if state.effect_type is not None else VoiceEffectType.NONE)
        
        # Initialize parameter controls
        self._init_parameter_controls(cs, state)
        
        # Initialize device lists
        self._init_device_lists(cs, state)

    def _init_parameter_controls(self, cs, state):
        """Initialize all parameter controls"""
        # Pitch shift
        cs.pitch_shift.enable()
        cs.pitch_shift.set_config(lib_csw.Number.Config(min=-12, max=12, step=0.5, decimals=1, allow_instant_update=True))
        cs.pitch_shift.set_number(state.pitch_shift if state.pitch_shift is not None else 0.0)
        
        # Formant shift
        cs.formant_shift.enable()
        cs.formant_shift.set_config(lib_csw.Number.Config(min=0.5, max=2.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.formant_shift.set_number(state.formant_shift if state.formant_shift is not None else 1.0)
        
        # Robot rate
        cs.robot_rate.enable()
        cs.robot_rate.set_config(lib_csw.Number.Config(min=0.1, max=10.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.robot_rate.set_number(state.robot_rate if state.robot_rate is not None else 0.1)
        
        # Echo parameters
        cs.echo_delay.enable()
        cs.echo_delay.set_config(lib_csw.Number.Config(min=0.1, max=1.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.echo_delay.set_number(state.echo_delay if state.echo_delay is not None else 0.3)
        
        cs.echo_decay.enable()
        cs.echo_decay.set_config(lib_csw.Number.Config(min=0.1, max=0.9, step=0.1, decimals=1, allow_instant_update=True))
        cs.echo_decay.set_number(state.echo_decay if state.echo_decay is not None else 0.5)
        
        # Reverb parameters
        cs.reverb_room_size.enable()
        cs.reverb_room_size.set_config(lib_csw.Number.Config(min=0.1, max=1.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.reverb_room_size.set_number(state.reverb_room_size if state.reverb_room_size is not None else 0.8)
        
        cs.reverb_damping.enable()
        cs.reverb_damping.set_config(lib_csw.Number.Config(min=0.1, max=1.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.reverb_damping.set_number(state.reverb_damping if state.reverb_damping is not None else 0.5)
        
        # Chorus parameters
        cs.chorus_rate.enable()
        cs.chorus_rate.set_config(lib_csw.Number.Config(min=0.1, max=5.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.chorus_rate.set_number(state.chorus_rate if state.chorus_rate is not None else 1.5)
        
        cs.chorus_depth.enable()
        cs.chorus_depth.set_config(lib_csw.Number.Config(min=0.001, max=0.01, step=0.001, decimals=3, allow_instant_update=True))
        cs.chorus_depth.set_number(state.chorus_depth if state.chorus_depth is not None else 0.002)
        
        # Distortion
        cs.distortion_amount.enable()
        cs.distortion_amount.set_config(lib_csw.Number.Config(min=0.1, max=1.0, step=0.1, decimals=1, allow_instant_update=True))
        cs.distortion_amount.set_number(state.distortion_amount if state.distortion_amount is not None else 0.3)
        
        # Autotune
        cs.autotune_sensitivity.enable()
        cs.autotune_sensitivity.set_config(lib_csw.Number.Config(min=0.01, max=1.0, step=0.01, decimals=2, allow_instant_update=True))
        cs.autotune_sensitivity.set_number(state.autotune_sensitivity if state.autotune_sensitivity is not None else 0.1)

    def _init_device_lists(self, cs, state):
        """Initialize input and output device lists"""
        # Get available devices
        input_devices = []
        output_devices = []
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append((i, device_info['name']))
            if device_info['maxOutputChannels'] > 0:
                output_devices.append((i, device_info['name']))
        
        # Set up input device control
        cs.input_device.enable()
        cs.input_device.set_choices([d[0] for d in input_devices], 
                                   [d[1] for d in input_devices],
                                   none_choice_name='@misc.menu_select')
        
        default_input = state.input_device if state.input_device is not None else 0
        if default_input < len(input_devices):
            cs.input_device.select(default_input)
        
        # Set up output device control
        cs.output_device.enable()
        cs.output_device.set_choices([d[0] for d in output_devices], 
                                    [d[1] for d in output_devices],
                                    none_choice_name='@misc.menu_select')
        
        default_output = state.output_device if state.output_device is not None else 0
        if default_output < len(output_devices):
            cs.output_device.select(default_output)

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
            self.input_stream.stop_stream()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        self.audio.terminate()

    def start_audio_processing(self):
        """Start audio processing threads"""
        if self.running:
            return
        
        self.running = True
        
        # Start input thread
        self.input_thread = threading.Thread(target=self._input_worker, daemon=True)
        self.input_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_worker, daemon=True)
        self.processing_thread.start()
        
        # Start output thread
        self.output_thread = threading.Thread(target=self._output_worker, daemon=True)
        self.output_thread.start()

    def stop_audio_processing(self):
        """Stop audio processing threads"""
        self.running = False

    def _input_worker(self):
        """Audio input worker thread"""
        try:
            self.input_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.get_state().input_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            
            while self.running:
                try:
                    data = self.input_stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    
                    if not self.input_queue.full():
                        self.input_queue.put(audio_data)
                except Exception as e:
                    print(f"Input error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start input stream: {e}")

    def _processing_worker(self):
        """Audio processing worker thread"""
        while self.running:
            try:
                if not self.input_queue.empty():
                    audio_data = self.input_queue.get(timeout=0.1)
                    processed_audio = self._apply_effects(audio_data)
                    
                    if not self.output_queue.full():
                        self.output_queue.put(processed_audio)
                else:
                    time.sleep(0.001)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")

    def _output_worker(self):
        """Audio output worker thread"""
        try:
            self.output_stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.get_state().output_device,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            
            while self.running:
                try:
                    if not self.output_queue.empty():
                        audio_data = self.output_queue.get(timeout=0.1)
                        self.output_stream.write(audio_data.tobytes())
                    else:
                        time.sleep(0.001)
                except Exception as e:
                    print(f"Output error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start output stream: {e}")

    def _apply_effects(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply selected audio effects"""
        if self.current_effect == VoiceEffectType.NONE:
            return audio_data
        
        # Apply effect based on type
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
        
        return audio_data

    def _pitch_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply pitch shifting effect"""
        semitones = self.effect_params['pitch_shift']
        if semitones == 0:
            return audio_data
        
        # Simple pitch shifting using librosa
        try:
            shifted = librosa.effects.pitch_shift(audio_data, sr=self.sample_rate, n_steps=semitones)
            return shifted
        except:
            # Fallback to simple resampling
            ratio = 2 ** (semitones / 12)
            return signal.resample(audio_data, int(len(audio_data) * ratio))

    def _formant_shift(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply formant shifting effect"""
        ratio = self.effect_params['formant_shift']
        if ratio == 1.0:
            return audio_data
        
        # Simple formant shifting using resampling
        resampled = signal.resample(audio_data, int(len(audio_data) * ratio))
        return signal.resample(resampled, len(audio_data))

    def _robot_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply robot effect using ring modulation"""
        rate = self.effect_params['robot_rate']
        t = np.linspace(0, len(audio_data) / self.sample_rate, len(audio_data))
        modulator = np.sin(2 * np.pi * rate * t)
        return audio_data * modulator

    def _helium_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply helium effect (high pitch)"""
        return self._pitch_shift(audio_data)  # Use pitch shift with positive value

    def _deep_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply deep voice effect (low pitch)"""
        return self._pitch_shift(audio_data)  # Use pitch shift with negative value

    def _echo_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply echo effect"""
        delay = self.effect_params['echo_delay']
        decay = self.effect_params['echo_decay']
        
        delay_samples = int(delay * self.sample_rate)
        echo = np.zeros_like(audio_data)
        
        if delay_samples < len(audio_data):
            echo[delay_samples:] = audio_data[:-delay_samples] * decay
        
        return audio_data + echo

    def _reverb_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply reverb effect"""
        room_size = self.effect_params['reverb_room_size']
        damping = self.effect_params['reverb_damping']
        
        # Simple reverb using multiple delays
        reverb = np.zeros_like(audio_data)
        delays = [int(room_size * self.sample_rate * 0.1 * i) for i in range(1, 6)]
        decays = [damping ** i for i in range(1, 6)]
        
        for delay, decay in zip(delays, decays):
            if delay < len(audio_data):
                reverb[delay:] += audio_data[:-delay] * decay
        
        return audio_data + reverb * 0.3

    def _chorus_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply chorus effect"""
        rate = self.effect_params['chorus_rate']
        depth = self.effect_params['chorus_depth']
        
        t = np.linspace(0, len(audio_data) / self.sample_rate, len(audio_data))
        mod = np.sin(2 * np.pi * rate * t) * depth * self.sample_rate
        
        # Create modulated version
        indices = np.arange(len(audio_data)) + mod
        indices = np.clip(indices, 0, len(audio_data) - 1).astype(int)
        modulated = audio_data[indices]
        
        return (audio_data + modulated) / 2

    def _distortion_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply distortion effect"""
        amount = self.effect_params['distortion_amount']
        return np.tanh(audio_data * (1 + amount * 10))

    def _autotune_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply autotune effect"""
        sensitivity = self.effect_params['autotune_sensitivity']
        
        # Simple autotune using pitch detection and correction
        # This is a simplified version - real autotune is much more complex
        try:
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=self.sample_rate)
            pitch_values = librosa.pitch_tuning(pitches)
            
            # Apply pitch correction
            corrected = librosa.effects.pitch_shift(audio_data, sr=self.sample_rate, 
                                                   n_steps=pitch_values * sensitivity)
            return corrected
        except:
            return audio_data

    # Control sheet callbacks
    def on_cs_enabled(self, enabled):
        state, cs = self.get_state(), self.get_control_sheet()
        state.enabled = enabled
        
        if enabled:
            self.start_audio_processing()
        else:
            self.stop_audio_processing()
        
        self.save_state()

    def on_cs_effect_type(self, idx, effect_type):
        state, cs = self.get_state(), self.get_control_sheet()
        state.effect_type = effect_type
        self.current_effect = effect_type
        self.save_state()

    def on_cs_pitch_shift(self, pitch_shift):
        state, cs = self.get_state(), self.get_control_sheet()
        state.pitch_shift = pitch_shift
        self.effect_params['pitch_shift'] = pitch_shift
        self.save_state()

    def on_cs_formant_shift(self, formant_shift):
        state, cs = self.get_state(), self.get_control_sheet()
        state.formant_shift = formant_shift
        self.effect_params['formant_shift'] = formant_shift
        self.save_state()

    def on_cs_robot_rate(self, robot_rate):
        state, cs = self.get_state(), self.get_control_sheet()
        state.robot_rate = robot_rate
        self.effect_params['robot_rate'] = robot_rate
        self.save_state()

    def on_cs_echo_delay(self, echo_delay):
        state, cs = self.get_state(), self.get_control_sheet()
        state.echo_delay = echo_delay
        self.effect_params['echo_delay'] = echo_delay
        self.save_state()

    def on_cs_echo_decay(self, echo_decay):
        state, cs = self.get_state(), self.get_control_sheet()
        state.echo_decay = echo_decay
        self.effect_params['echo_decay'] = echo_decay
        self.save_state()

    def on_cs_reverb_room_size(self, reverb_room_size):
        state, cs = self.get_state(), self.get_control_sheet()
        state.reverb_room_size = reverb_room_size
        self.effect_params['reverb_room_size'] = reverb_room_size
        self.save_state()

    def on_cs_reverb_damping(self, reverb_damping):
        state, cs = self.get_state(), self.get_control_sheet()
        state.reverb_damping = reverb_damping
        self.effect_params['reverb_damping'] = reverb_damping
        self.save_state()

    def on_cs_chorus_rate(self, chorus_rate):
        state, cs = self.get_state(), self.get_control_sheet()
        state.chorus_rate = chorus_rate
        self.effect_params['chorus_rate'] = chorus_rate
        self.save_state()

    def on_cs_chorus_depth(self, chorus_depth):
        state, cs = self.get_state(), self.get_control_sheet()
        state.chorus_depth = chorus_depth
        self.effect_params['chorus_depth'] = chorus_depth
        self.save_state()

    def on_cs_distortion_amount(self, distortion_amount):
        state, cs = self.get_state(), self.get_control_sheet()
        state.distortion_amount = distortion_amount
        self.effect_params['distortion_amount'] = distortion_amount
        self.save_state()

    def on_cs_autotune_sensitivity(self, autotune_sensitivity):
        state, cs = self.get_state(), self.get_control_sheet()
        state.autotune_sensitivity = autotune_sensitivity
        self.effect_params['autotune_sensitivity'] = autotune_sensitivity
        self.save_state()

    def on_cs_input_device(self, idx, device_idx):
        state, cs = self.get_state(), self.get_control_sheet()
        state.input_device = device_idx
        self.save_state()

    def on_cs_output_device(self, idx, device_idx):
        state, cs = self.get_state(), self.get_control_sheet()
        state.output_device = device_idx
        self.save_state()


class Sheet:
    class Host(lib_csw.Sheet.Host):
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

    class Worker(lib_csw.Sheet.Worker):
        def __init__(self):
            super().__init__()
            self.enabled = lib_csw.Flag.Worker()
            self.effect_type = lib_csw.DynamicSingleSwitch.Worker()
            self.pitch_shift = lib_csw.Number.Worker()
            self.formant_shift = lib_csw.Number.Worker()
            self.robot_rate = lib_csw.Number.Worker()
            self.echo_delay = lib_csw.Number.Worker()
            self.echo_decay = lib_csw.Number.Worker()
            self.reverb_room_size = lib_csw.Number.Worker()
            self.reverb_damping = lib_csw.Number.Worker()
            self.chorus_rate = lib_csw.Number.Worker()
            self.chorus_depth = lib_csw.Number.Worker()
            self.distortion_amount = lib_csw.Number.Worker()
            self.autotune_sensitivity = lib_csw.Number.Worker()
            self.input_device = lib_csw.DynamicSingleSwitch.Worker()
            self.output_device = lib_csw.DynamicSingleSwitch.Worker()


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