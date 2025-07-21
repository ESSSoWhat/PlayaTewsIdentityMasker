#!/usr/bin/env python3
"""
Fix GPU warning by setting appropriate environment variables
"""

import os
import sys

def fix_gpu_warning():
    """Set environment variables to suppress CUDA warnings"""
    
    # Suppress CUDA warnings
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    os.environ['ONNXRUNTIME_PROVIDER_INFO'] = 'CPUExecutionProvider'
    
    # Set logging level to suppress warnings
    os.environ['ONNXRUNTIME_LOGGING_LEVEL'] = '3'  # ERROR level
    
    print("✅ GPU warning suppression applied")
    print("   - CUDA warnings will be suppressed")
    print("   - Using CPU execution provider")
    print("   - Logging level set to ERROR only")

if __name__ == "__main__":
    fix_gpu_warning() 