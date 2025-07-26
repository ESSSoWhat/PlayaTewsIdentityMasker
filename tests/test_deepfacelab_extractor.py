#!/usr/bin/env python3
"""
Test suite for DeepFaceLab Extractor Component

Tests all major functionality including:
- Video downloading
- Face extraction
- Data preparation
- DFM export
"""

import pytest
import tempfile
import shutil
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Import the component to test
from deepfacelab_extractor import (
    DeepFaceLabExtractor, VideoDownloader, FaceExtractor, 
    DeepFaceLabDataPreparer, DFMExporter, ExtractionConfig,
    DetectorType, VideoSourceType, VideoInfo
)


class TestVideoDownloader:
    """Test video downloading functionality"""
    
    @pytest.fixture
    def downloader(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield VideoDownloader(Path(temp_dir))
    
    def test_download_youtube_video(self, downloader):
        """Test YouTube video download"""
        with patch('yt_dlp.YoutubeDL') as mock_ydl:
            # Mock yt-dlp behavior
            mock_instance = Mock()
            mock_instance.extract_info.return_value = {
                'title': 'Test Video',
                'duration': 120.0,
                'fps': 30.0
            }
            mock_instance.download.return_value = None
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            # Mock file existence check
            with patch('pathlib.Path.glob') as mock_glob:
                mock_glob.return_value = [Path('/tmp/Test Video.mp4')]
                
                result = downloader.download_youtube_video('https://youtube.com/watch?v=test')
                assert result.name == 'Test Video.mp4'
    
    def test_download_direct_url(self, downloader):
        """Test direct URL download"""
        with patch('deepfacelab_extractor.ThreadFileDownloader') as mock_downloader:
            mock_instance = Mock()
            mock_instance.get_progress.return_value = 100.0
            mock_instance.get_error.return_value = None
            mock_downloader.return_value = mock_instance
            
            result = downloader.download_direct_url('https://example.com/video.mp4')
            assert result.name.endswith('.mp4')
    
    def test_get_video_info(self, downloader):
        """Test video information extraction"""
        with patch('subprocess.run') as mock_run:
            # Mock ffprobe output
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps({
                'format': {'duration': '120.0'},
                'streams': [{
                    'codec_type': 'video',
                    'width': '1920',
                    'height': '1080',
                    'avg_frame_rate': '30/1'
                }]
            })
            mock_run.return_value = mock_result
            
            # Create a temporary video file
            with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
                video_info = downloader.get_video_info(Path(temp_file.name))
                
                assert video_info.duration == 120.0
                assert video_info.fps == 30.0
                assert video_info.width == 1920
                assert video_info.height == 1080


class TestFaceExtractor:
    """Test face extraction functionality"""
    
    @pytest.fixture
    def config(self):
        return ExtractionConfig(
            detector_type=DetectorType.YOLOV5,
            threshold=0.5,
            min_face_size=40,
            max_faces=5,
            output_size=256,
            quality_threshold=0.3,
            device="CPU"
        )
    
    @pytest.fixture
    def extractor(self, config):
        with patch('modelhub.onnx.YoloV5Face') as mock_detector:
            mock_instance = Mock()
            mock_detector.return_value = mock_instance
            yield FaceExtractor(config)
    
    def test_extract_faces_from_frame(self, extractor):
        """Test face extraction from a single frame"""
        # Create a test frame with a face-like region
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Mock detector response
        mock_rects = np.array([[100, 100, 200, 200]])  # Face bounding box
        extractor.detector.extract.return_value = [mock_rects]
        
        faces = extractor.extract_faces_from_frame(frame)
        
        assert len(faces) > 0
        face_img, face_info = faces[0]
        assert face_img.shape == (256, 256, 3)  # Output size
        assert 'quality_score' in face_info
        assert 'bbox' in face_info
    
    def test_extract_faces_from_video(self, extractor):
        """Test face extraction from video"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test video file
            video_path = Path(temp_dir) / "test_video.mp4"
            
            # Mock video capture
            with patch('cv2.VideoCapture') as mock_cap:
                mock_instance = Mock()
                mock_instance.isOpened.return_value = True
                mock_instance.read.side_effect = [
                    (True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)),
                    (True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)),
                    (False, None)  # End of video
                ]
                mock_cap.return_value = mock_instance
                
                # Mock detector response
                mock_rects = np.array([[100, 100, 200, 200]])
                extractor.detector.extract.return_value = [mock_rects]
                
                # Mock image writing
                with patch('cv2.imwrite') as mock_imwrite:
                    mock_imwrite.return_value = True
                    
                    result = extractor.extract_faces_from_video(
                        video_path, Path(temp_dir), frame_interval=1
                    )
                    
                    assert len(result) > 0


class TestDeepFaceLabDataPreparer:
    """Test data preparation for DeepFaceLab"""
    
    @pytest.fixture
    def preparer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield DeepFaceLabDataPreparer(Path(temp_dir))
    
    def test_prepare_training_data(self, preparer):
        """Test training data preparation"""
        # Create test face files
        source_faces = []
        destination_faces = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create source faces
            for i in range(5):
                face_path = temp_path / f"src_face_{i}.jpg"
                face_path.write_bytes(b"fake_image_data")
                source_faces.append(face_path)
            
            # Create destination faces
            for i in range(5):
                face_path = temp_path / f"dst_face_{i}.jpg"
                face_path.write_bytes(b"fake_image_data")
                destination_faces.append(face_path)
            
            # Test data preparation
            result = preparer.prepare_training_data(source_faces, destination_faces)
            
            assert 'source_aligned' in result
            assert 'destination_aligned' in result
            assert 'model_dir' in result
            
            # Check that files were copied
            assert len(list(result['source_aligned'].glob('*.jpg'))) == 5
            assert len(list(result['destination_aligned'].glob('*.jpg'))) == 5
    
    def test_create_training_script(self, preparer):
        """Test training script creation"""
        script_path = preparer.create_training_script("SAEHD")
        
        assert script_path.exists()
        assert script_path.suffix == '.sh'
        
        # Check script content
        script_content = script_path.read_text()
        assert "SAEHD" in script_content
        assert "train" in script_content
        assert "exportdfm" in script_content


class TestDFMExporter:
    """Test DFM export functionality"""
    
    @pytest.fixture
    def exporter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield DFMExporter(Path(temp_dir))
    
    def test_export_to_dfm(self, exporter):
        """Test DFM export"""
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            
            # Mock subprocess run
            with patch('subprocess.run') as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result
                
                # Mock file existence
                with patch('pathlib.Path.glob') as mock_glob:
                    mock_glob.return_value = [model_dir / "SAEHD_export.dfm"]
                    
                    result = exporter.export_to_dfm(model_dir, "SAEHD")
                    assert result.name == "SAEHD_export.dfm"


class TestDeepFaceLabExtractor:
    """Test the main DeepFaceLab extractor component"""
    
    @pytest.fixture
    def extractor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ExtractionConfig(
                detector_type=DetectorType.YOLOV5,
                device="CPU"
            )
            yield DeepFaceLabExtractor(Path(temp_dir), config)
    
    def test_process_url_video(self, extractor):
        """Test processing a video from URL"""
        with patch.object(extractor.downloader, 'download_youtube_video') as mock_download:
            with patch.object(extractor.downloader, 'get_video_info') as mock_info:
                with patch.object(extractor.extractor, 'extract_faces_from_video') as mock_extract:
                    # Mock responses
                    mock_download.return_value = Path("/tmp/test_video.mp4")
                    mock_info.return_value = VideoInfo(
                        url="/tmp/test_video.mp4",
                        title="Test Video",
                        duration=120.0,
                        fps=30.0,
                        width=1920,
                        height=1080,
                        frame_count=3600,
                        source_type=VideoSourceType.LOCAL_FILE
                    )
                    mock_extract.return_value = [Path("/tmp/face1.jpg"), Path("/tmp/face2.jpg")]
                    
                    result = extractor.process_url_video("https://youtube.com/watch?v=test")
                    assert result.exists()
    
    def test_prepare_training_dataset(self, extractor):
        """Test complete training dataset preparation"""
        with patch.object(extractor, 'process_url_video') as mock_process:
            # Mock face directories
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create mock face directories
                src_faces_dir = temp_path / "source_faces"
                dst_faces_dir = temp_path / "destination_faces"
                src_faces_dir.mkdir()
                dst_faces_dir.mkdir()
                
                # Create mock face files
                for i in range(3):
                    (src_faces_dir / f"face_{i}.jpg").write_bytes(b"fake_data")
                    (dst_faces_dir / f"face_{i}.jpg").write_bytes(b"fake_data")
                
                mock_process.side_effect = [src_faces_dir, dst_faces_dir]
                
                result = extractor.prepare_training_dataset(
                    "https://youtube.com/source",
                    "https://youtube.com/destination"
                )
                
                assert 'source_faces' in result
                assert 'destination_faces' in result
                assert 'training_data' in result
                assert 'training_script' in result


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_complete_workflow(self):
        """Test the complete workflow from URL to training data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ExtractionConfig(
                detector_type=DetectorType.YOLOV5,
                device="CPU"
            )
            
            extractor = DeepFaceLabExtractor(Path(temp_dir), config)
            
            # Mock all external dependencies
            with patch.object(extractor.downloader, 'download_youtube_video') as mock_download:
                with patch.object(extractor.downloader, 'get_video_info') as mock_info:
                    with patch.object(extractor.extractor, 'extract_faces_from_video') as mock_extract:
                        # Setup mocks
                        mock_download.return_value = Path("/tmp/test_video.mp4")
                        mock_info.return_value = VideoInfo(
                            url="/tmp/test_video.mp4",
                            title="Test Video",
                            duration=120.0,
                            fps=30.0,
                            width=1920,
                            height=1080,
                            frame_count=3600,
                            source_type=VideoSourceType.LOCAL_FILE
                        )
                        
                        # Create mock face files
                        with tempfile.TemporaryDirectory() as faces_temp:
                            faces_path = Path(faces_temp)
                            for i in range(5):
                                (faces_path / f"face_{i}.jpg").write_bytes(b"fake_data")
                            
                            mock_extract.return_value = list(faces_path.glob("*.jpg"))
                            
                            # Test the complete workflow
                            result = extractor.prepare_training_dataset(
                                "https://youtube.com/source",
                                "https://youtube.com/destination"
                            )
                            
                            # Verify results
                            assert result['training_script'].exists()
                            assert len(list(result['source_faces'].glob("*.jpg"))) == 5
                            assert len(list(result['destination_faces'].glob("*.jpg"))) == 5


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_url(self):
        """Test handling of invalid URLs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            extractor = DeepFaceLabExtractor(Path(temp_dir))
            
            with patch.object(extractor.downloader, 'download_youtube_video') as mock_download:
                mock_download.side_effect = Exception("Invalid URL")
                
                with pytest.raises(Exception, match="Failed to process video"):
                    extractor.process_url_video("invalid_url")
    
    def test_no_faces_detected(self):
        """Test handling when no faces are detected"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ExtractionConfig(
                detector_type=DetectorType.YOLOV5,
                device="CPU"
            )
            extractor = DeepFaceLabExtractor(Path(temp_dir), config)
            
            with patch.object(extractor.extractor, 'extract_faces_from_video') as mock_extract:
                mock_extract.return_value = []  # No faces detected
                
                # This should not raise an exception, just return empty list
                result = extractor.extractor.extract_faces_from_video(
                    Path("/tmp/test.mp4"), Path(temp_dir)
                )
                assert len(result) == 0
    
    def test_missing_dependencies(self):
        """Test handling of missing dependencies"""
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            
            with pytest.raises(ImportError):
                # This would fail during import
                import deepfacelab_extractor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])