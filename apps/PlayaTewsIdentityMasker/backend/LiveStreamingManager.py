#!/usr/bin/env python3
"""
Live Streaming Manager for PlayaTewsIdentityMasker
Handles multi-platform streaming with automatic reconnection
"""

import subprocess
import threading
import time
import queue
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class StreamPlatform(Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    CUSTOM_RTMP = "custom_rtmp"

@dataclass
class StreamConfig:
    platform: StreamPlatform
    stream_key: str
    server_url: str
    enabled: bool = True
    bitrate: int = 2500
    resolution: str = "1920x1080"
    fps: int = 30
    encoder: str = "libx264"
    audio_bitrate: int = 128

class StreamProcess:
    """Individual stream process manager"""
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.process = None
        self.is_running = False
        self.frame_count = 0
        self.start_time = None
        self.last_frame_time = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        
    def start(self) -> bool:
        """Start the streaming process"""
        try:
            rtmp_url = self._get_rtmp_url()
            if not rtmp_url:
                logger.error(f"Invalid RTMP URL for {self.config.platform.value}")
                return False
                
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(rtmp_url)
            
            logger.info(f"Starting stream to {self.config.platform.value}")
            logger.debug(f"FFmpeg command: {' '.join(cmd)}")
            
            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_running = True
            self.start_time = time.time()
            self.reconnect_attempts = 0
            
            logger.info(f"✅ Stream started successfully: {self.config.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start stream to {self.config.platform.value}: {e}")
            return False
            
    def _get_rtmp_url(self) -> Optional[str]:
        """Get RTMP URL for the platform"""
        if self.config.platform == StreamPlatform.TWITCH:
            return f"rtmp://live.twitch.tv/app/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.YOUTUBE:
            return f"rtmp://a.rtmp.youtube.com/live2/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.FACEBOOK:
            return f"rtmp://live-api-s.facebook.com/rtmp/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.CUSTOM_RTMP:
            return self.config.server_url
        else:
            return None
            
    def _build_ffmpeg_command(self, rtmp_url: str) -> List[str]:
        """Build FFmpeg command for streaming"""
        width, height = map(int, self.config.resolution.split('x'))
        
        cmd = [
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{width}x{height}',
            '-r', str(self.config.fps),
            '-i', '-',
            '-c:v', self.config.encoder,
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            '-b:v', f'{self.config.bitrate}k',
            '-maxrate', f'{self.config.bitrate}k',
            '-bufsize', f'{self.config.bitrate * 2}k',
            '-g', str(self.config.fps * 2),
            '-f', 'flv',
            rtmp_url
        ]
        
        return cmd
        
    def send_frame(self, frame: np.ndarray):
        """Send frame to stream"""
        if not self.is_running or not self.process:
            return
            
        try:
            # Check if process is still alive
            if self.process.poll() is not None:
                logger.warning(f"Stream process died for {self.config.platform.value}")
                self._attempt_reconnect()
                return
                
            # Resize frame if needed
            width, height = map(int, self.config.resolution.split('x'))
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
                
            # Send frame to FFmpeg
            self.process.stdin.write(frame.tobytes())
            self.process.stdin.flush()
            
            self.frame_count += 1
            self.last_frame_time = time.time()
            
        except Exception as e:
            logger.error(f"❌ Frame send error for {self.config.platform.value}: {e}")
            self._attempt_reconnect()
            
    def _attempt_reconnect(self):
        """Attempt to reconnect the stream"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts reached for {self.config.platform.value}")
            self.stop()
            return
            
        self.reconnect_attempts += 1
        logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts} for {self.config.platform.value}")
        
        self.stop()
        time.sleep(2)  # Wait before reconnecting
        
        if self.start():
            logger.info(f"✅ Reconnected successfully to {self.config.platform.value}")
        else:
            logger.error(f"❌ Reconnection failed for {self.config.platform.value}")
            
    def stop(self):
        """Stop the streaming process"""
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info(f"🛑 Stream stopped: {self.config.platform.value}")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning(f"Force killed stream process: {self.config.platform.value}")
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
            finally:
                self.process = None
                
    def get_stats(self) -> Dict:
        """Get stream statistics"""
        if not self.start_time:
            return {}
            
        runtime = time.time() - self.start_time
        fps = self.frame_count / runtime if runtime > 0 else 0
        
        return {
            'platform': self.config.platform.value,
            'runtime': runtime,
            'frame_count': self.frame_count,
            'fps': fps,
            'is_running': self.is_running,
            'reconnect_attempts': self.reconnect_attempts
        }

class LiveStreamingManager:
    """Main streaming manager for handling multiple platforms"""
    
    def __init__(self):
        self.streams: Dict[str, StreamProcess] = {}
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=60)  # Increased buffer for streaming
        self.stream_configs: List[StreamConfig] = []
        self.frame_callback: Optional[Callable] = None
        self.stream_stats = {}
        self.frame_thread = None
        
        # Setup default configurations
        self._setup_default_configs()
        
    def _setup_default_configs(self):
        """Setup default streaming configurations"""
        # Twitch configuration
        twitch_config = StreamConfig(
            platform=StreamPlatform.TWITCH,
            stream_key="",
            server_url="rtmp://live.twitch.tv/app/",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.stream_configs.append(twitch_config)
        
        # YouTube configuration
        youtube_config = StreamConfig(
            platform=StreamPlatform.YOUTUBE,
            stream_key="",
            server_url="rtmp://a.rtmp.youtube.com/live2/",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.stream_configs.append(youtube_config)
        
        # Facebook configuration
        facebook_config = StreamConfig(
            platform=StreamPlatform.FACEBOOK,
            stream_key="",
            server_url="rtmp://live-api-s.facebook.com/rtmp/",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.stream_configs.append(facebook_config)
        
        # Custom RTMP configuration
        custom_config = StreamConfig(
            platform=StreamPlatform.CUSTOM_RTMP,
            stream_key="",
            server_url="",
            enabled=False,
            bitrate=2500,
            resolution="1920x1080",
            fps=30
        )
        self.stream_configs.append(custom_config)
        
    def add_stream_config(self, config: StreamConfig):
        """Add a new streaming configuration"""
        self.stream_configs.append(config)
        logger.info(f"Added stream config for {config.platform.value}")
        
    def get_stream_config(self, platform: StreamPlatform) -> Optional[StreamConfig]:
        """Get configuration for a specific platform"""
        for config in self.stream_configs:
            if config.platform == platform:
                return config
        return None
        
    def update_stream_config(self, platform: StreamPlatform, **kwargs):
        """Update configuration for a specific platform"""
        config = self.get_stream_config(platform)
        if config:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            logger.info(f"Updated config for {platform.value}")
            
    def start_streaming(self, frame_callback: Callable = None):
        """Start streaming to all enabled platforms"""
        if self.is_streaming:
            logger.warning("Streaming already in progress")
            return False
            
        self.frame_callback = frame_callback
        self.is_streaming = True
        
        # Start streams for each enabled configuration
        started_streams = 0
        for config in self.stream_configs:
            if config.enabled and config.stream_key:
                stream_id = f"{config.platform.value}_{config.stream_key[:8]}"
                stream_process = StreamProcess(config)
                
                if stream_process.start():
                    self.streams[stream_id] = stream_process
                    started_streams += 1
                    logger.info(f"✅ Started streaming to {config.platform.value}")
                else:
                    logger.error(f"❌ Failed to start streaming to {config.platform.value}")
                    
        if started_streams > 0:
            # Start frame processing thread
            self.frame_thread = threading.Thread(target=self._frame_processor, daemon=True)
            self.frame_thread.start()
            logger.info(f"🎬 Started streaming to {started_streams} platform(s)")
            return True
        else:
            self.is_streaming = False
            logger.error("❌ No streams started successfully")
            return False
        
    def stop_streaming(self):
        """Stop all active streams"""
        if not self.is_streaming:
            return
            
        self.is_streaming = False
        
        for stream_id, stream_process in self.streams.items():
            stream_process.stop()
            logger.info(f"🛑 Stopped stream: {stream_id}")
            
        self.streams.clear()
        
        # Clear frame queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
                
        logger.info("🛑 All streams stopped")
        
    def send_frame(self, frame: np.ndarray):
        """Send a frame to all active streams"""
        if not self.is_streaming or not self.streams:
            return
            
        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            # Drop frame if queue is full to maintain real-time performance
            pass
            
    def _frame_processor(self):
        """Process frames for streaming"""
        logger.info("🎬 Frame processor started")
        
        while self.is_streaming:
            try:
                frame = self.frame_queue.get(timeout=1.0)
                
                # Send frame to all active streams
                for stream_process in self.streams.values():
                    stream_process.send_frame(frame)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Frame processing error: {e}")
                
        logger.info("🛑 Frame processor stopped")
                
    def get_stream_stats(self) -> Dict[str, Dict]:
        """Get statistics for all streams"""
        stats = {}
        for stream_id, stream_process in self.streams.items():
            stats[stream_id] = stream_process.get_stats()
        return stats
        
    def get_active_stream_count(self) -> int:
        """Get number of active streams"""
        return len(self.streams)
        
    def is_any_stream_active(self) -> bool:
        """Check if any stream is active"""
        return len(self.streams) > 0