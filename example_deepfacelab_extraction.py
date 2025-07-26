#!/usr/bin/env python3
"""
Example: DeepFaceLab Face Extraction from URL Videos

This script demonstrates how to use the DeepFaceLab extractor component
to extract faces from YouTube videos and prepare them for training.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from deepfacelab_extractor import (
    DeepFaceLabExtractor, 
    ExtractionConfig, 
    DetectorType,
    VideoSourceType
)


def example_basic_extraction():
    """Basic example: Extract faces from two YouTube videos"""
    print("🎭 DeepFaceLab Face Extraction Example")
    print("=" * 50)
    
    # Configuration for face extraction
    config = ExtractionConfig(
        detector_type=DetectorType.YOLOV5,  # Fast and accurate
        threshold=0.5,                      # Detection confidence
        min_face_size=40,                   # Minimum face size
        max_faces=10,                       # Max faces per frame
        output_size=256,                    # Output image size
        quality_threshold=0.3,              # Quality filter
        device="CPU"                        # Use CPU (change to "CUDA" for GPU)
    )
    
    # Initialize extractor
    workspace_dir = Path("./example_workspace")
    extractor = DeepFaceLabExtractor(workspace_dir, config)
    
    # Example YouTube URLs (replace with your own)
    source_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    destination_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example URL
    
    print(f"📁 Workspace: {workspace_dir}")
    print(f"🎥 Source video: {source_url}")
    print(f"🎥 Destination video: {destination_url}")
    print(f"🔍 Detector: {config.detector_type.value}")
    print(f"⚙️ Device: {config.device}")
    print()
    
    try:
        # Process videos and prepare training dataset
        print("🚀 Starting face extraction...")
        result = extractor.prepare_training_dataset(
            source_video_url=source_url,
            destination_video_url=destination_url,
            source_name="example_source",
            destination_name="example_destination",
            frame_interval=30  # Process every 30th frame
        )
        
        # Display results
        print("\n✅ Extraction completed successfully!")
        print("=" * 50)
        print(f"📊 Source faces: {len(list(result['source_faces'].glob('*.jpg')))}")
        print(f"📊 Destination faces: {len(list(result['destination_faces'].glob('*.jpg')))}")
        print(f"📁 Training script: {result['training_script']}")
        print(f"📁 Source aligned: {result['training_data']['source_aligned']}")
        print(f"📁 Destination aligned: {result['training_data']['destination_aligned']}")
        print(f"📁 Model directory: {result['training_data']['model_dir']}")
        
        print("\n🎯 Next steps:")
        print("1. Review extracted faces for quality")
        print("2. Run the training script in DeepFaceLab")
        print("3. Export the trained model to DFM format")
        print("4. Use the DFM model in your face swap application")
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        return False
    
    return True


def example_advanced_extraction():
    """Advanced example: Custom configuration and batch processing"""
    print("\n🔧 Advanced DeepFaceLab Extraction Example")
    print("=" * 50)
    
    # Advanced configuration for high-quality extraction
    config = ExtractionConfig(
        detector_type=DetectorType.S3FD,    # High precision detector
        threshold=0.7,                      # Higher confidence threshold
        min_face_size=60,                   # Larger minimum face size
        max_faces=5,                        # Fewer faces per frame
        output_size=512,                    # Higher resolution output
        quality_threshold=0.5,              # Higher quality requirement
        device="CUDA"                       # Use GPU if available
    )
    
    # Initialize extractor
    workspace_dir = Path("./advanced_workspace")
    extractor = DeepFaceLabExtractor(workspace_dir, config)
    
    # Multiple video pairs for batch processing
    video_pairs = [
        {
            "source": "https://www.youtube.com/watch?v=example1",
            "destination": "https://www.youtube.com/watch?v=example2",
            "source_name": "person_a",
            "destination_name": "person_b"
        },
        {
            "source": "https://www.youtube.com/watch?v=example3", 
            "destination": "https://www.youtube.com/watch?v=example4",
            "source_name": "person_c",
            "destination_name": "person_d"
        }
    ]
    
    print(f"📁 Workspace: {workspace_dir}")
    print(f"🔍 Detector: {config.detector_type.value}")
    print(f"⚙️ Device: {config.device}")
    print(f"📊 Processing {len(video_pairs)} video pairs")
    print()
    
    results = []
    
    for i, pair in enumerate(video_pairs, 1):
        print(f"🎬 Processing pair {i}/{len(video_pairs)}: {pair['source_name']} → {pair['destination_name']}")
        
        try:
            result = extractor.prepare_training_dataset(
                source_video_url=pair['source'],
                destination_video_url=pair['destination'],
                source_name=pair['source_name'],
                destination_name=pair['destination_name'],
                frame_interval=15  # Process every 15th frame for better coverage
            )
            
            results.append(result)
            print(f"✅ Pair {i} completed successfully")
            
        except Exception as e:
            print(f"❌ Pair {i} failed: {str(e)}")
            continue
    
    print(f"\n📊 Batch processing completed: {len(results)}/{len(video_pairs)} successful")
    
    return len(results) > 0


def example_quality_control():
    """Example: Quality control and face filtering"""
    print("\n🔍 Quality Control Example")
    print("=" * 50)
    
    # Configuration optimized for quality
    config = ExtractionConfig(
        detector_type=DetectorType.S3FD,
        threshold=0.8,                      # Very high confidence
        min_face_size=80,                   # Large faces only
        max_faces=3,                        # Few faces per frame
        output_size=512,                    # High resolution
        quality_threshold=0.7,              # Very high quality
        device="CUDA"
    )
    
    workspace_dir = Path("./quality_workspace")
    extractor = DeepFaceLabExtractor(workspace_dir, config)
    
    print(f"📁 Workspace: {workspace_dir}")
    print(f"🎯 Quality threshold: {config.quality_threshold}")
    print(f"🔍 Detection threshold: {config.threshold}")
    print(f"📏 Minimum face size: {config.min_face_size}px")
    print()
    
    # Example with a high-quality video
    source_url = "https://www.youtube.com/watch?v=high_quality_video"
    
    try:
        result = extractor.process_url_video(
            url=source_url,
            output_name="high_quality_source",
            frame_interval=10  # Process more frames for better coverage
        )
        
        face_count = len(list(result.glob('*.jpg')))
        print(f"✅ Extracted {face_count} high-quality faces")
        print(f"📁 Face directory: {result}")
        
        # Show quality statistics
        print("\n📊 Quality Statistics:")
        print("- Only faces with quality score >= 0.7")
        print("- Only faces with detection confidence >= 0.8")
        print("- Only faces larger than 80x80 pixels")
        print("- Output resolution: 512x512 pixels")
        
    except Exception as e:
        print(f"❌ Quality extraction failed: {str(e)}")
        return False
    
    return True


def example_dfm_export():
    """Example: Export trained model to DFM format"""
    print("\n📦 DFM Export Example")
    print("=" * 50)
    
    from deepfacelab_extractor import DFMExporter
    
    # Path to your DeepFaceLab installation
    deepfacelab_dir = Path("/path/to/DeepFaceLab")  # Update this path
    
    if not deepfacelab_dir.exists():
        print(f"⚠️ DeepFaceLab directory not found: {deepfacelab_dir}")
        print("Please update the path in the script")
        return False
    
    # Path to your trained model
    model_dir = Path("/path/to/trained/model")  # Update this path
    
    if not model_dir.exists():
        print(f"⚠️ Model directory not found: {model_dir}")
        print("Please train a model first or update the path")
        return False
    
    try:
        # Initialize exporter
        exporter = DFMExporter(deepfacelab_dir)
        
        print(f"📁 DeepFaceLab directory: {deepfacelab_dir}")
        print(f"📁 Model directory: {model_dir}")
        print("🚀 Exporting to DFM format...")
        
        # Export to DFM
        dfm_path = exporter.export_to_dfm(
            model_dir=model_dir,
            model_type="SAEHD"  # or "Quick96", "AMP"
        )
        
        print(f"✅ DFM export completed!")
        print(f"📦 DFM file: {dfm_path}")
        print(f"📏 File size: {dfm_path.stat().st_size / (1024*1024):.1f} MB")
        
        print("\n🎯 Next steps:")
        print("1. Copy the DFM file to your face swap application")
        print("2. Load the model in the face swap interface")
        print("3. Configure settings for optimal results")
        
    except Exception as e:
        print(f"❌ DFM export failed: {str(e)}")
        return False
    
    return True


def main():
    """Run all examples"""
    print("🎭 DeepFaceLab Face Extractor Examples")
    print("=" * 60)
    
    # Check if required dependencies are available
    try:
        import cv2
        import numpy as np
        import yt_dlp
        print("✅ All required dependencies are available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements_deepfacelab_extractor.txt")
        return
    
    # Run examples
    examples = [
        ("Basic Extraction", example_basic_extraction),
        ("Advanced Extraction", example_advanced_extraction),
        ("Quality Control", example_quality_control),
        ("DFM Export", example_dfm_export)
    ]
    
    results = []
    
    for name, example_func in examples:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            result = example_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print(f"\n⏹️ {name} interrupted by user")
            results.append((name, False))
            break
        except Exception as e:
            print(f"\n❌ {name} failed with error: {str(e)}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Example Results Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:<25} {status}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {successful}/{total} examples completed successfully")
    
    if successful == total:
        print("🎉 All examples completed successfully!")
    else:
        print("⚠️ Some examples failed. Check the output above for details.")


if __name__ == "__main__":
    main()