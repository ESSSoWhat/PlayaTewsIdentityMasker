#!/usr/bin/env python3
"""
GPU Setup Test Script
Tests all GPU frameworks for PlayaTewsIdentityMasker and DeepFaceLab
"""

import sys
import subprocess

def test_onnx_runtime():
    """Test ONNX Runtime GPU support"""
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        print("✅ ONNX Runtime GPU Support:")
        print(f"   Version: {ort.__version__}")
        print(f"   Available providers: {providers}")
        return 'CUDAExecutionProvider' in providers
    except Exception as e:
        print(f"❌ ONNX Runtime Error: {e}")
        return False

def test_pytorch():
    """Test PyTorch GPU support"""
    try:
        import torch
        print("✅ PyTorch GPU Support:")
        print(f"   Version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA device count: {torch.cuda.device_count()}")
            print(f"   Current device: {torch.cuda.current_device()}")
            print(f"   Device name: {torch.cuda.get_device_name()}")
        return torch.cuda.is_available()
    except Exception as e:
        print(f"❌ PyTorch Error: {e}")
        return False

def test_tensorflow():
    """Test TensorFlow GPU support"""
    try:
        import tensorflow as tf
        print("⚠️  TensorFlow GPU Support:")
        print(f"   Version: {tf.__version__}")
        gpus = tf.config.list_physical_devices('GPU')
        print(f"   GPU devices: {len(gpus)}")
        if len(gpus) > 0:
            print(f"   GPU names: {[gpu.name for gpu in gpus]}")
        return len(gpus) > 0
    except Exception as e:
        print(f"❌ TensorFlow Error: {e}")
        return False

def test_nvidia_smi():
    """Test NVIDIA GPU detection"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU Detection:")
            lines = result.stdout.split('\n')
            for line in lines[:5]:  # Show first 5 lines
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print("❌ NVIDIA GPU not detected")
            return False
    except Exception as e:
        print(f"❌ NVIDIA SMI Error: {e}")
        return False

def main():
    """Run all GPU tests"""
    print("=" * 60)
    print("GPU SETUP VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    # Test NVIDIA GPU
    results['nvidia'] = test_nvidia_smi()
    print()
    
    # Test ONNX Runtime (for PlayaTewsIdentityMasker)
    results['onnx'] = test_onnx_runtime()
    print()
    
    # Test PyTorch (for DeepFaceLab training)
    results['pytorch'] = test_pytorch()
    print()
    
    # Test TensorFlow (for DeepFaceLab training)
    results['tensorflow'] = test_tensorflow()
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if results['nvidia']:
        print("✅ NVIDIA GPU detected")
    else:
        print("❌ NVIDIA GPU not detected")
    
    if results['onnx']:
        print("✅ ONNX Runtime GPU support - PlayaTewsIdentityMasker ready")
    else:
        print("❌ ONNX Runtime GPU support - PlayaTewsIdentityMasker may be slow")
    
    if results['pytorch']:
        print("✅ PyTorch GPU support - DeepFaceLab training ready")
    else:
        print("❌ PyTorch GPU support - DeepFaceLab training will be slow")
    
    if results['tensorflow']:
        print("✅ TensorFlow GPU support - Full DeepFaceLab support")
    else:
        print("⚠️  TensorFlow CPU only - PyTorch training recommended")
    
    print()
    print("RECOMMENDATIONS:")
    if results['pytorch'] and results['onnx']:
        print("✅ Your setup is ready for both training and live streaming!")
        print("   - Use PyTorch for DeepFaceLab training")
        print("   - Use ONNX Runtime for PlayaTewsIdentityMasker streaming")
    elif results['onnx']:
        print("✅ Ready for live streaming, training will be slower")
    else:
        print("❌ GPU setup needs attention")

if __name__ == "__main__":
    main() 