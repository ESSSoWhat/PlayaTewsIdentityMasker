#!/usr/bin/env python3
"""
Professional Recorder for PlayaTewsIdentityMasker
Handles high-quality video recording with multiple formats
"""

import cv2
import numpy as np
import threading
import time
from pathlib import Path
from typing import Optional, Dict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RecordingFormat(Enum):
    MP4 = "mp4"
    MKV = "mkv"
    AVI = "avi"
    MOV = "mov"

class RecordingQuality(Enum):
    ULTRA_HD = "4k"
    FULL_HD = "1080p"
    HD = "720p"
    SD = "480p"

class ProfessionalRecorder:
    """Professional video recorder with multiple format support"""
    
    def __init__(self):
        self.is_recording = False
        self.recorder = None
        self.output_path = None
        self.recording_format = RecordingFormat.MP4
        self.recording_quality = RecordingQuality.FULL_HD
        self.fps = 30
        self.start_time = None
        self.frame_count = 0
        self.file_size = 0
        self.last_frame_time = None
        
    def start_recording(self, output_path: Path, 
                       format: RecordingFormat = RecordingFormat.MP4,
                       quality: RecordingQuality = RecordingQuality.FULL_HD,
                       fps: int = 30) -> bool:
        """Start recording"""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
            
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.output_path = output_path
            self.recording_format = format
            self.recording_quality = quality
            self.fps = fps
            
            # Get video codec and settings
            codec, bitrate = self._get_recording_settings()
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*codec)
            width, height = self._get_resolution()
            
            logger.info(f"Starting recording: {output_path}")
            logger.info(f"Format: {format.value}, Quality: {quality.value}, FPS: {fps}")
            
            self.recorder = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps,
                (width, height)
            )
            
            if not self.recorder.isOpened():
                logger.error("Failed to open video writer")
                return False
                
            self.is_recording = True
            self.start_time = time.time()
            self.frame_count = 0
            self.file_size = 0
            self.last_frame_time = None
            
            logger.info(f"✅ Started recording: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            return False
            
    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        if self.recorder:
            self.recorder.release()
            self.recorder = None
            
        runtime = time.time() - self.start_time if self.start_time else 0
        
        # Get final file size
        if self.output_path and self.output_path.exists():
            self.file_size = self.output_path.stat().st_size
            
        logger.info(f"🛑 Stopped recording. Runtime: {runtime:.1f}s, Frames: {self.frame_count}")
        logger.info(f"📁 Output file: {self.output_path} ({self.file_size / (1024*1024):.1f} MB)")
        
    def record_frame(self, frame: np.ndarray):
        """Record a frame"""
        if not self.is_recording or not self.recorder:
            return
            
        try:
            # Resize frame if needed
            width, height = self._get_resolution()
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
                
            self.recorder.write(frame)
            self.frame_count += 1
            self.last_frame_time = time.time()
            
        except Exception as e:
            logger.error(f"❌ Frame recording error: {e}")
            self.stop_recording()
            
    def pause_recording(self):
        """Pause recording (not implemented in OpenCV, but can be used for status)"""
        if self.is_recording:
            logger.info("⏸️ Recording paused")
            
    def resume_recording(self):
        """Resume recording"""
        if self.is_recording:
            logger.info("▶️ Recording resumed")
            
    def _get_recording_settings(self) -> tuple:
        """Get codec and bitrate for recording format"""
        settings = {
            RecordingFormat.MP4: ('mp4v', 8000),
            RecordingFormat.MKV: ('XVID', 8000),
            RecordingFormat.AVI: ('XVID', 6000),
            RecordingFormat.MOV: ('mp4v', 8000)
        }
        return settings.get(self.recording_format, ('mp4v', 8000))
        
    def _get_resolution(self) -> tuple:
        """Get resolution for quality setting"""
        resolutions = {
            RecordingQuality.ULTRA_HD: (3840, 2160),
            RecordingQuality.FULL_HD: (1920, 1080),
            RecordingQuality.HD: (1280, 720),
            RecordingQuality.SD: (854, 480)
        }
        return resolutions.get(self.recording_quality, (1920, 1080))
        
    def get_recording_stats(self) -> Dict:
        """Get recording statistics"""
        if not self.start_time:
            return {}
            
        runtime = time.time() - self.start_time
        fps = self.frame_count / runtime if runtime > 0 else 0
        
        # Calculate file size if recording
        current_file_size = 0
        if self.output_path and self.output_path.exists():
            current_file_size = self.output_path.stat().st_size
            
        return {
            'runtime': runtime,
            'frame_count': self.frame_count,
            'fps': fps,
            'is_recording': self.is_recording,
            'output_path': str(self.output_path) if self.output_path else None,
            'file_size_mb': current_file_size / (1024*1024),
            'format': self.recording_format.value,
            'quality': self.recording_quality.value
        }
        
    def get_estimated_file_size(self) -> float:
        """Get estimated file size in MB"""
        if not self.is_recording or not self.start_time:
            return 0.0
            
        runtime = time.time() - self.start_time
        if runtime <= 0:
            return 0.0
            
        # Estimate based on current bitrate and runtime
        width, height = self._get_resolution()
        estimated_bitrate = width * height * self.fps * 0.1  # Rough estimate
        estimated_size_mb = (estimated_bitrate * runtime) / (8 * 1024 * 1024)
        
        return estimated_size_mb

class RecordingManager:
    """Manager for handling multiple recording sessions"""
    
    def __init__(self):
        self.recorders: Dict[str, ProfessionalRecorder] = {}
        self.recording_sessions = {}
        
    def start_session(self, session_id: str, output_path: Path, 
                     format: RecordingFormat = RecordingFormat.MP4,
                     quality: RecordingQuality = RecordingQuality.FULL_HD,
                     fps: int = 30) -> bool:
        """Start a new recording session"""
        if session_id in self.recorders:
            logger.warning(f"Session {session_id} already exists")
            return False
            
        recorder = ProfessionalRecorder()
        success = recorder.start_recording(output_path, format, quality, fps)
        
        if success:
            self.recorders[session_id] = recorder
            self.recording_sessions[session_id] = {
                'output_path': output_path,
                'format': format,
                'quality': quality,
                'fps': fps,
                'start_time': time.time()
            }
            logger.info(f"✅ Started recording session: {session_id}")
            return True
        else:
            logger.error(f"❌ Failed to start recording session: {session_id}")
            return False
            
    def stop_session(self, session_id: str):
        """Stop a recording session"""
        if session_id not in self.recorders:
            logger.warning(f"Session {session_id} not found")
            return
            
        recorder = self.recorders[session_id]
        recorder.stop_recording()
        
        del self.recorders[session_id]
        del self.recording_sessions[session_id]
        
        logger.info(f"🛑 Stopped recording session: {session_id}")
        
    def record_frame_to_session(self, session_id: str, frame: np.ndarray):
        """Record a frame to a specific session"""
        if session_id not in self.recorders:
            return
            
        recorder = self.recorders[session_id]
        recorder.record_frame(frame)
        
    def get_session_stats(self, session_id: str) -> Dict:
        """Get statistics for a specific session"""
        if session_id not in self.recorders:
            return {}
            
        recorder = self.recorders[session_id]
        return recorder.get_recording_stats()
        
    def get_all_sessions_stats(self) -> Dict[str, Dict]:
        """Get statistics for all sessions"""
        stats = {}
        for session_id, recorder in self.recorders.items():
            stats[session_id] = recorder.get_recording_stats()
        return stats
        
    def get_active_session_count(self) -> int:
        """Get number of active recording sessions"""
        return len(self.recorders)
        
    def stop_all_sessions(self):
        """Stop all recording sessions"""
        for session_id in list(self.recorders.keys()):
            self.stop_session(session_id)
            
    def is_any_session_active(self) -> bool:
        """Check if any recording session is active"""
        return len(self.recorders) > 0