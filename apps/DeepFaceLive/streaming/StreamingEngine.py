import json
import queue
import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

import cv2
import numpy as np


class StreamPlatform(Enum):
    TWITCH = "twitch"
    YOUTUBE = "youtube"
    FACEBOOK = "facebook"
    RTMP_CUSTOM = "rtmp_custom"


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


class StreamingEngine:
    def __init__(self):
        self.streams: Dict[str, "StreamProcess"] = {}
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=30)
        self.stream_configs: List[StreamConfig] = []
        self.frame_callback: Optional[Callable] = None

    def add_stream_config(self, config: StreamConfig):
        """Add a new streaming configuration"""
        self.stream_configs.append(config)

    def remove_stream_config(self, platform: StreamPlatform):
        """Remove a streaming configuration"""
        self.stream_configs = [
            config for config in self.stream_configs if config.platform != platform
        ]

    def start_streaming(self, frame_callback: Callable = None):
        """Start streaming to all configured platforms"""
        if self.is_streaming:
            return False

        self.frame_callback = frame_callback
        self.is_streaming = True

        # Start streams for each enabled configuration
        for config in self.stream_configs:
            if config.enabled and config.stream_key:
                stream_id = f"{config.platform.value}_{config.stream_key[:8]}"
                stream_process = StreamProcess(config)

                if stream_process.start():
                    self.streams[stream_id] = stream_process
                    print(f"Started streaming to {config.platform.value}")
                else:
                    print(f"Failed to start streaming to {config.platform.value}")

        # Start frame processing thread
        self.frame_thread = threading.Thread(target=self._frame_processor, daemon=True)
        self.frame_thread.start()

        return len(self.streams) > 0

    def stop_streaming(self):
        """Stop all active streams"""
        self.is_streaming = False

        # Stop all stream processes
        for stream_id, stream_process in self.streams.items():
            stream_process.stop()
            print(f"Stopped stream: {stream_id}")

        self.streams.clear()

        # Clear frame queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

    def send_frame(self, frame: np.ndarray):
        """Send a frame to all active streams"""
        if not self.is_streaming or not self.streams:
            return

        try:
            # Put frame in queue for processing
            self.frame_queue.put_nowait(frame.copy())
        except queue.Full:
            # Skip frame if queue is full
            pass

    def _frame_processor(self):
        """Process frames from queue and send to streams"""
        while self.is_streaming:
            try:
                frame = self.frame_queue.get(timeout=0.1)

                # Apply frame callback if provided
                if self.frame_callback:
                    frame = self.frame_callback(frame)

                # Send frame to all active streams
                for stream_process in self.streams.values():
                    stream_process.send_frame(frame)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing frame: {e}")

    def get_stream_stats(self) -> Dict[str, Dict]:
        """Get statistics for all active streams"""
        stats = {}
        for stream_id, stream_process in self.streams.items():
            stats[stream_id] = stream_process.get_stats()
        return stats


class StreamProcess:
    """Handles individual stream process using FFmpeg"""

    def __init__(self, config: StreamConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.frames_sent = 0
        self.start_time = None

    def start(self) -> bool:
        """Start the FFmpeg streaming process"""
        try:
            # Get RTMP URL
            rtmp_url = self._get_rtmp_url()
            if not rtmp_url:
                return False

            # Parse resolution
            width, height = map(int, self.config.resolution.split("x"))

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output files
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                "bgr24",
                "-s",
                f"{width}x{height}",
                "-r",
                str(self.config.fps),
                "-i",
                "-",  # Input from stdin
                "-c:v",
                self.config.encoder,
                "-preset",
                "ultrafast",
                "-tune",
                "zerolatency",
                "-b:v",
                f"{self.config.bitrate}k",
                "-maxrate",
                f"{self.config.bitrate}k",
                "-bufsize",
                f"{self.config.bitrate * 2}k",
                "-pix_fmt",
                "yuv420p",
                "-g",
                str(self.config.fps * 2),  # Keyframe interval
                "-keyint_min",
                str(self.config.fps),
                "-f",
                "flv",
                rtmp_url,
            ]

            # Start FFmpeg process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
            )

            self.is_running = True
            self.start_time = time.time()
            return True

        except Exception as e:
            print(f"Error starting stream process: {e}")
            return False

    def stop(self):
        """Stop the streaming process"""
        self.is_running = False

        if self.process:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                print(f"Error stopping stream process: {e}")

            self.process = None

    def send_frame(self, frame: np.ndarray):
        """Send a frame to the stream"""
        if not self.is_running or not self.process:
            return

        try:
            # Resize frame to target resolution
            width, height = map(int, self.config.resolution.split("x"))
            if frame.shape[:2] != (height, width):
                frame = cv2.resize(frame, (width, height))

            # Send frame to FFmpeg
            self.process.stdin.write(frame.tobytes())
            self.process.stdin.flush()
            self.frames_sent += 1

        except Exception as e:
            print(f"Error sending frame to stream: {e}")
            self.stop()

    def get_stats(self) -> Dict:
        """Get stream statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        fps = self.frames_sent / uptime if uptime > 0 else 0

        return {
            "platform": self.config.platform.value,
            "is_running": self.is_running,
            "frames_sent": self.frames_sent,
            "uptime": uptime,
            "fps": fps,
            "bitrate": self.config.bitrate,
            "resolution": self.config.resolution,
        }

    def _get_rtmp_url(self) -> Optional[str]:
        """Get the RTMP URL for the platform"""
        if self.config.platform == StreamPlatform.TWITCH:
            return f"rtmp://live.twitch.tv/live/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.YOUTUBE:
            return f"rtmp://a.rtmp.youtube.com/live2/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.FACEBOOK:
            return f"rtmps://live-api-s.facebook.com:443/rtmp/{self.config.stream_key}"
        elif self.config.platform == StreamPlatform.RTMP_CUSTOM:
            return f"{self.config.server_url}/{self.config.stream_key}"
        else:
            return None


class RecordingEngine:
    """Handles video recording functionality"""

    def __init__(self):
        self.is_recording = False
        self.recorder: Optional["VideoRecorder"] = None

    def start_recording(
        self,
        output_path: Path,
        format: str = "mp4",
        resolution: str = "1920x1080",
        fps: int = 30,
        quality: str = "high",
    ) -> bool:
        """Start recording video"""
        if self.is_recording:
            return False

        self.recorder = VideoRecorder(output_path, format, resolution, fps, quality)
        success = self.recorder.start()

        if success:
            self.is_recording = True
            print(f"Started recording to: {output_path}")
        else:
            print(f"Failed to start recording")

        return success

    def stop_recording(self):
        """Stop recording"""
        if self.recorder:
            self.recorder.stop()
            self.recorder = None

        self.is_recording = False
        print("Recording stopped")

    def record_frame(self, frame: np.ndarray):
        """Record a frame"""
        if self.is_recording and self.recorder:
            self.recorder.write_frame(frame)


class VideoRecorder:
    """Individual video recorder using OpenCV"""

    def __init__(
        self, output_path: Path, format: str, resolution: str, fps: int, quality: str
    ):
        self.output_path = output_path
        self.format = format
        self.resolution = resolution
        self.fps = fps
        self.quality = quality
        self.writer: Optional[cv2.VideoWriter] = None

    def start(self) -> bool:
        """Start the video writer"""
        try:
            # Parse resolution
            width, height = map(int, self.resolution.split("x"))

            # Get codec based on format
            if self.format.lower() == "mp4":
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            elif self.format.lower() == "avi":
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
            elif self.format.lower() == "mov":
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            else:
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            # Create output directory if it doesn't exist
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Initialize video writer
            self.writer = cv2.VideoWriter(
                str(self.output_path), fourcc, self.fps, (width, height)
            )

            return self.writer.isOpened()

        except Exception as e:
            print(f"Error starting video recorder: {e}")
            return False

    def stop(self):
        """Stop the video writer"""
        if self.writer:
            self.writer.release()
            self.writer = None

    def write_frame(self, frame: np.ndarray):
        """Write a frame to the video"""
        if self.writer and self.writer.isOpened():
            try:
                # Resize frame to target resolution
                width, height = map(int, self.resolution.split("x"))
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))

                self.writer.write(frame)
            except Exception as e:
                print(f"Error writing frame to video: {e}")


# Platform-specific configurations
PLATFORM_CONFIGS = {
    StreamPlatform.TWITCH: {
        "name": "Twitch",
        "server_url": "rtmp://live.twitch.tv/live",
        "max_bitrate": 6000,
        "recommended_bitrate": 3500,
        "max_resolution": "1920x1080",
        "max_fps": 60,
    },
    StreamPlatform.YOUTUBE: {
        "name": "YouTube",
        "server_url": "rtmp://a.rtmp.youtube.com/live2",
        "max_bitrate": 51000,
        "recommended_bitrate": 4500,
        "max_resolution": "3840x2160",
        "max_fps": 60,
    },
    StreamPlatform.FACEBOOK: {
        "name": "Facebook",
        "server_url": "rtmps://live-api-s.facebook.com:443/rtmp",
        "max_bitrate": 4000,
        "recommended_bitrate": 2000,
        "max_resolution": "1920x1080",
        "max_fps": 30,
    },
}


def get_platform_config(platform: StreamPlatform) -> Dict:
    """Get configuration for a specific platform"""
    return PLATFORM_CONFIGS.get(platform, {})


def validate_stream_config(config: StreamConfig) -> List[str]:
    """Validate a stream configuration and return list of errors"""
    errors = []

    if not config.stream_key:
        errors.append("Stream key is required")

    if config.bitrate < 500:
        errors.append("Bitrate too low (minimum 500 kbps)")

    platform_config = get_platform_config(config.platform)
    if platform_config:
        max_bitrate = platform_config.get("max_bitrate", 10000)
        if config.bitrate > max_bitrate:
            errors.append(
                f"Bitrate too high for {platform_config['name']} (maximum {max_bitrate} kbps)"
            )

    try:
        width, height = map(int, config.resolution.split("x"))
        if width < 320 or height < 240:
            errors.append("Resolution too low (minimum 320x240)")
    except ValueError:
        errors.append("Invalid resolution format (use WIDTHxHEIGHT)")

    if config.fps < 10 or config.fps > 60:
        errors.append("FPS must be between 10 and 60")

    return errors
