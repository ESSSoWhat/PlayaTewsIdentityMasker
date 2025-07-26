#!/usr/bin/env python3
"""
DeepFaceLab Face Extractor Component

A comprehensive component for extracting faces from URL videos for DeepFaceLab training.
Supports video download, face extraction, data preparation, and DFM export.

Features:
- Download videos from URLs (YouTube, direct links, etc.)
- Extract frames from videos
- Detect and extract faces using multiple detectors
- Prepare data for DeepFaceLab training
- Export trained models to DFM format
- Batch processing capabilities
"""

import os
import sys
import time
import logging
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import urllib.request
import tempfile
import shutil

import numpy as np
import cv2
from PIL import Image
import yt_dlp

# Import existing components
from xlib import face as lib_face
from xlib import cv as lib_cv
from xlib import path as lib_path
from xlib.net import ThreadFileDownloader
from modelhub import onnx as onnx_models


class DetectorType(Enum):
    """Available face detection methods"""
    CENTER_FACE = "centerface"
    S3FD = "s3fd"
    YOLOV5 = "yolov5"


class VideoSourceType(Enum):
    """Supported video source types"""
    YOUTUBE = "youtube"
    DIRECT_URL = "direct_url"
    LOCAL_FILE = "local_file"


@dataclass
class ExtractionConfig:
    """Configuration for face extraction"""
    detector_type: DetectorType = DetectorType.YOLOV5
    threshold: float = 0.5
    min_face_size: int = 40
    max_faces: int = 10
    output_size: int = 256
    quality_threshold: float = 0.3
    device: str = "CPU"
    temporal_smoothing: int = 1


@dataclass
class VideoInfo:
    """Video information"""
    url: str
    title: str
    duration: float
    fps: float
    width: int
    height: int
    frame_count: int
    source_type: VideoSourceType


class VideoDownloader:
    """Handles video downloads from various sources"""
    
    def __init__(self, download_dir: Path):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def download_youtube_video(self, url: str, output_name: Optional[str] = None) -> Path:
        """Download video from YouTube URL"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=1080]',  # Limit to 1080p
                'outtmpl': str(self.download_dir / f'{output_name or "%(title)s.%(ext)s"}'),
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'unknown')
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                downloaded_file = None
                for file in self.download_dir.glob(f"{title}.*"):
                    if file.suffix in ['.mp4', '.mkv', '.avi', '.webm']:
                        downloaded_file = file
                        break
                
                if downloaded_file is None:
                    raise Exception(f"Could not find downloaded video file for {url}")
                
                return downloaded_file
                
        except Exception as e:
            raise Exception(f"Failed to download YouTube video {url}: {str(e)}")
    
    def download_direct_url(self, url: str, output_name: Optional[str] = None) -> Path:
        """Download video from direct URL"""
        try:
            if output_name is None:
                output_name = f"video_{int(time.time())}.mp4"
            
            output_path = self.download_dir / output_name
            
            # Use ThreadFileDownloader for direct URLs
            downloader = ThreadFileDownloader(url=url, savepath=output_path)
            
            # Wait for download to complete
            while downloader.get_progress() < 100.0:
                time.sleep(0.1)
                if downloader.get_error():
                    raise Exception(f"Download failed: {downloader.get_error()}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to download video from {url}: {str(e)}")
    
    def get_video_info(self, video_path: Path) -> VideoInfo:
        """Extract video information using ffprobe"""
        try:
            # Use ffprobe to get video information
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {result.stderr}")
            
            import json
            data = json.loads(result.stdout)
            
            # Find video stream
            video_stream = None
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if video_stream is None:
                raise Exception("No video stream found")
            
            # Extract information
            duration = float(data['format'].get('duration', 0))
            fps_str = video_stream.get('avg_frame_rate', '0/1')
            fps = eval(fps_str) if '/' in fps_str else float(fps_str)
            width = int(video_stream.get('width', 0))
            height = int(video_stream.get('height', 0))
            frame_count = int(duration * fps) if duration > 0 and fps > 0 else 0
            
            return VideoInfo(
                url=str(video_path),
                title=video_path.stem,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                frame_count=frame_count,
                source_type=VideoSourceType.LOCAL_FILE
            )
            
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")


class FaceExtractor:
    """Handles face detection and extraction from video frames"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.detector = self._initialize_detector()
        
    def _initialize_detector(self):
        """Initialize the face detector based on configuration"""
        try:
            if self.config.detector_type == DetectorType.CENTER_FACE:
                return onnx_models.CenterFace(self.config.device)
            elif self.config.detector_type == DetectorType.S3FD:
                return onnx_models.S3FD(self.config.device)
            elif self.config.detector_type == DetectorType.YOLOV5:
                return onnx_models.YoloV5Face(self.config.device)
            else:
                raise ValueError(f"Unsupported detector type: {self.config.detector_type}")
        except Exception as e:
            raise Exception(f"Failed to initialize detector: {str(e)}")
    
    def extract_faces_from_frame(self, frame: np.ndarray) -> List[Tuple[np.ndarray, Dict]]:
        """Extract faces from a single frame"""
        try:
            # Detect faces
            rects = self.detector.extract(
                frame,
                threshold=self.config.threshold,
                fixed_window=0,
                min_face_size=self.config.min_face_size
            )[0]
            
            extracted_faces = []
            
            for rect in rects[:self.config.max_faces]:
                # Extract face region
                x1, y1, x2, y2 = rect.astype(int)
                face_img = frame[y1:y2, x1:x2]
                
                if face_img.size == 0:
                    continue
                
                # Resize to output size
                face_img = cv2.resize(face_img, (self.config.output_size, self.config.output_size))
                
                # Calculate quality score (simple blur detection)
                gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                quality_score = min(1.0, laplacian_var / 100.0)  # Normalize
                
                # Filter by quality
                if quality_score >= self.config.quality_threshold:
                    face_info = {
                        'bbox': rect,
                        'quality_score': quality_score,
                        'size': face_img.shape
                    }
                    extracted_faces.append((face_img, face_info))
            
            return extracted_faces
            
        except Exception as e:
            logging.error(f"Error extracting faces from frame: {str(e)}")
            return []
    
    def extract_faces_from_video(self, video_path: Path, output_dir: Path, 
                                frame_interval: int = 30) -> List[Path]:
        """Extract faces from video frames at specified intervals"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise Exception(f"Could not open video: {video_path}")
            
            extracted_faces = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every nth frame
                if frame_count % frame_interval == 0:
                    faces = self.extract_faces_from_frame(frame)
                    
                    for i, (face_img, face_info) in enumerate(faces):
                        # Save face image
                        face_filename = f"face_{frame_count:06d}_{i:02d}.jpg"
                        face_path = output_dir / face_filename
                        
                        cv2.imwrite(str(face_path), face_img)
                        extracted_faces.append(face_path)
                        extracted_count += 1
                        
                        # Log progress
                        if extracted_count % 100 == 0:
                            logging.info(f"Extracted {extracted_count} faces...")
                
                frame_count += 1
            
            cap.release()
            logging.info(f"Extracted {len(extracted_faces)} faces from {frame_count} frames")
            return extracted_faces
            
        except Exception as e:
            raise Exception(f"Failed to extract faces from video: {str(e)}")


class DeepFaceLabDataPreparer:
    """Prepares extracted faces for DeepFaceLab training"""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)
        self.data_src_dir = self.workspace_dir / "data_src"
        self.data_dst_dir = self.workspace_dir / "data_dst"
        self.model_dir = self.workspace_dir / "model"
        
        # Create directory structure
        for dir_path in [self.data_src_dir, self.data_dst_dir, self.model_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def prepare_training_data(self, source_faces: List[Path], 
                            destination_faces: List[Path]) -> Dict[str, Path]:
        """Prepare training data for DeepFaceLab"""
        try:
            # Create aligned directories
            src_aligned = self.data_src_dir / "aligned"
            dst_aligned = self.data_dst_dir / "aligned"
            
            for aligned_dir in [src_aligned, dst_aligned]:
                aligned_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy source faces
            logging.info(f"Copying {len(source_faces)} source faces...")
            for i, face_path in enumerate(source_faces):
                dst_path = src_aligned / f"src_{i:06d}.jpg"
                shutil.copy2(face_path, dst_path)
            
            # Copy destination faces
            logging.info(f"Copying {len(destination_faces)} destination faces...")
            for i, face_path in enumerate(destination_faces):
                dst_path = dst_aligned / f"dst_{i:06d}.jpg"
                shutil.copy2(face_path, dst_path)
            
            return {
                'source_aligned': src_aligned,
                'destination_aligned': dst_aligned,
                'model_dir': self.model_dir
            }
            
        except Exception as e:
            raise Exception(f"Failed to prepare training data: {str(e)}")
    
    def create_training_script(self, model_type: str = "SAEHD") -> Path:
        """Create a training script for DeepFaceLab"""
        try:
            script_content = f"""#!/bin/bash
# DeepFaceLab Training Script
# Generated by DeepFaceLab Extractor

cd "{self.workspace_dir}"

# Extract faces (if not already done)
python main.py extract --input-dir data_src --output-dir data_src/aligned --detector s3fd
python main.py extract --input-dir data_dst --output-dir data_dst/aligned --detector s3fd

# Sort faces by quality
python main.py sort --input-dir data_src/aligned --by blur
python main.py sort --input-dir data_dst/aligned --by blur

# Train the model
python main.py train \\
    --training-data-src-dir data_src/aligned \\
    --training-data-dst-dir data_dst/aligned \\
    --model-dir model \\
    --model {model_type} \\
    --cpu-only false \\
    --force-gpu-idxs 0

# Export to DFM format
python main.py exportdfm --model-dir model --model {model_type}

echo "Training completed! Check model/ directory for results."
"""
            
            script_path = self.workspace_dir / "train.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            return script_path
            
        except Exception as e:
            raise Exception(f"Failed to create training script: {str(e)}")


class DFMExporter:
    """Handles export of trained models to DFM format"""
    
    def __init__(self, deepfacelab_dir: Path):
        self.deepfacelab_dir = Path(deepfacelab_dir)
    
    def export_to_dfm(self, model_dir: Path, model_type: str = "SAEHD") -> Path:
        """Export trained model to DFM format"""
        try:
            # Change to DeepFaceLab directory
            original_cwd = os.getcwd()
            os.chdir(self.deepfacelab_dir)
            
            # Run export command
            cmd = [
                sys.executable, "main.py", "exportdfm",
                "--model-dir", str(model_dir),
                "--model", model_type
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode != 0:
                raise Exception(f"Export failed: {result.stderr}")
            
            # Find the exported DFM file
            dfm_files = list(model_dir.glob(f"*{model_type}*.dfm"))
            if not dfm_files:
                raise Exception("No DFM file found after export")
            
            return dfm_files[0]
            
        except Exception as e:
            raise Exception(f"Failed to export to DFM: {str(e)}")


class DeepFaceLabExtractor:
    """Main component for DeepFaceLab face extraction from URL videos"""
    
    def __init__(self, workspace_dir: Path, config: Optional[ExtractionConfig] = None):
        self.workspace_dir = Path(workspace_dir)
        self.config = config or ExtractionConfig()
        
        # Initialize components
        self.downloader = VideoDownloader(self.workspace_dir / "downloads")
        self.extractor = FaceExtractor(self.config)
        self.preparer = DeepFaceLabDataPreparer(self.workspace_dir / "deepfacelab_workspace")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.workspace_dir / "extraction.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_url_video(self, url: str, output_name: Optional[str] = None,
                         frame_interval: int = 30) -> Path:
        """Process a video from URL and extract faces"""
        try:
            self.logger.info(f"Processing video from URL: {url}")
            
            # Download video
            if "youtube.com" in url or "youtu.be" in url:
                video_path = self.downloader.download_youtube_video(url, output_name)
            else:
                video_path = self.downloader.download_direct_url(url, output_name)
            
            self.logger.info(f"Downloaded video: {video_path}")
            
            # Get video information
            video_info = self.downloader.get_video_info(video_path)
            self.logger.info(f"Video info: {video_info.title}, {video_info.duration:.1f}s, {video_info.fps:.1f} fps")
            
            # Extract faces
            faces_output_dir = self.workspace_dir / "extracted_faces" / video_path.stem
            extracted_faces = self.extractor.extract_faces_from_video(
                video_path, faces_output_dir, frame_interval
            )
            
            self.logger.info(f"Extracted {len(extracted_faces)} faces")
            
            return faces_output_dir
            
        except Exception as e:
            self.logger.error(f"Failed to process video: {str(e)}")
            raise
    
    def prepare_training_dataset(self, source_video_url: str, destination_video_url: str,
                               source_name: Optional[str] = None,
                               destination_name: Optional[str] = None) -> Dict[str, Path]:
        """Prepare a complete training dataset from two video URLs"""
        try:
            self.logger.info("Preparing training dataset from video URLs")
            
            # Process source video
            source_faces_dir = self.process_url_video(
                source_video_url, source_name or "source"
            )
            source_faces = list(source_faces_dir.glob("*.jpg"))
            
            # Process destination video
            destination_faces_dir = self.process_url_video(
                destination_video_url, destination_name or "destination"
            )
            destination_faces = list(destination_faces_dir.glob("*.jpg"))
            
            # Prepare training data
            training_data = self.preparer.prepare_training_data(source_faces, destination_faces)
            
            # Create training script
            script_path = self.preparer.create_training_script()
            
            self.logger.info(f"Training dataset prepared:")
            self.logger.info(f"  Source faces: {len(source_faces)}")
            self.logger.info(f"  Destination faces: {len(destination_faces)}")
            self.logger.info(f"  Training script: {script_path}")
            
            return {
                'source_faces': source_faces_dir,
                'destination_faces': destination_faces_dir,
                'training_data': training_data,
                'training_script': script_path
            }
            
        except Exception as e:
            self.logger.error(f"Failed to prepare training dataset: {str(e)}")
            raise
    
    def export_to_dfm(self, deepfacelab_dir: Path, model_dir: Path, 
                     model_type: str = "SAEHD") -> Path:
        """Export trained model to DFM format"""
        try:
            exporter = DFMExporter(deepfacelab_dir)
            dfm_path = exporter.export_to_dfm(model_dir, model_type)
            
            self.logger.info(f"Exported DFM model: {dfm_path}")
            return dfm_path
            
        except Exception as e:
            self.logger.error(f"Failed to export DFM: {str(e)}")
            raise


def main():
    """Example usage of the DeepFaceLab Extractor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DeepFaceLab Face Extractor")
    parser.add_argument("--workspace", type=str, default="./deepfacelab_extraction",
                       help="Workspace directory")
    parser.add_argument("--source-url", type=str, required=True,
                       help="Source video URL")
    parser.add_argument("--destination-url", type=str, required=True,
                       help="Destination video URL")
    parser.add_argument("--detector", type=str, default="yolov5",
                       choices=["centerface", "s3fd", "yolov5"],
                       help="Face detector to use")
    parser.add_argument("--device", type=str, default="CPU",
                       help="Device to use (CPU, CUDA, etc.)")
    parser.add_argument("--frame-interval", type=int, default=30,
                       help="Process every Nth frame")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ExtractionConfig(
        detector_type=DetectorType(args.detector),
        device=args.device
    )
    
    # Initialize extractor
    extractor = DeepFaceLabExtractor(args.workspace, config)
    
    try:
        # Process videos and prepare training dataset
        result = extractor.prepare_training_dataset(
            args.source_url, args.destination_url,
            frame_interval=args.frame_interval
        )
        
        print(f"\n✅ Training dataset prepared successfully!")
        print(f"📁 Workspace: {args.workspace}")
        print(f"🎯 Training script: {result['training_script']}")
        print(f"📊 Source faces: {len(list(result['source_faces'].glob('*.jpg')))}")
        print(f"📊 Destination faces: {len(list(result['destination_faces'].glob('*.jpg')))}")
        print(f"\n🚀 To start training, run: {result['training_script']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()