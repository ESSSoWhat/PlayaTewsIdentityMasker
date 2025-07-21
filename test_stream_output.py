#!/usr/bin/env python3
"""
Test script to verify StreamOutput module functionality
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_stream_output_import():
    """Test if StreamOutput can be imported"""
    logger.info("🧪 Testing StreamOutput import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend.StreamOutput import StreamOutput
        logger.info("✅ StreamOutput backend import successful")
        return True
    except Exception as e:
        logger.error(f"❌ StreamOutput backend import failed: {e}")
        return False

def test_qstream_output_import():
    """Test if QStreamOutput can be imported"""
    logger.info("🧪 Testing QStreamOutput import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QStreamOutput import QStreamOutput
        logger.info("✅ QStreamOutput UI import successful")
        return True
    except Exception as e:
        logger.error(f"❌ QStreamOutput UI import failed: {e}")
        return False

def test_enhanced_stream_output_import():
    """Test if EnhancedStreamOutput can be imported"""
    logger.info("🧪 Testing EnhancedStreamOutput import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend.EnhancedStreamOutput import EnhancedStreamOutput
        logger.info("✅ EnhancedStreamOutput backend import successful")
        return True
    except Exception as e:
        logger.error(f"❌ EnhancedStreamOutput backend import failed: {e}")
        return False

def test_qenhanced_stream_output_import():
    """Test if QEnhancedStreamOutput can be imported"""
    logger.info("🧪 Testing QEnhancedStreamOutput import...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui.QEnhancedStreamOutput import QEnhancedStreamOutput
        logger.info("✅ QEnhancedStreamOutput UI import successful")
        return True
    except Exception as e:
        logger.error(f"❌ QEnhancedStreamOutput UI import failed: {e}")
        return False

def test_stream_output_creation():
    """Test if StreamOutput can be created (without full initialization)"""
    logger.info("🧪 Testing StreamOutput creation...")
    
    try:
        from apps.PlayaTewsIdentityMasker.backend.StreamOutput import StreamOutput
        from apps.PlayaTewsIdentityMasker.backend.BackendWeakHeap import BackendWeakHeap
        from apps.PlayaTewsIdentityMasker.backend.BackendSignal import BackendSignal
        from apps.PlayaTewsIdentityMasker.backend.BackendConnection import BackendConnection
        from apps.PlayaTewsIdentityMasker.backend.BackendDB import BackendDB
        
        # Create minimal components for testing
        weak_heap = BackendWeakHeap(size_mb=64)
        reemit_frame_signal = BackendSignal()
        bc_in = BackendConnection()
        backend_db = BackendDB()
        
        # Create StreamOutput instance
        stream_output = StreamOutput(
            weak_heap=weak_heap,
            reemit_frame_signal=reemit_frame_signal,
            bc_in=bc_in,
            save_default_path=Path("test_output"),
            backend_db=backend_db
        )
        
        logger.info("✅ StreamOutput creation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ StreamOutput creation failed: {e}")
        return False

def main():
    """Run all StreamOutput tests"""
    logger.info("🚀 Starting StreamOutput Module Tests...")
    
    tests = [
        ("StreamOutput Backend Import", test_stream_output_import),
        ("QStreamOutput UI Import", test_qstream_output_import),
        ("EnhancedStreamOutput Backend Import", test_enhanced_stream_output_import),
        ("QEnhancedStreamOutput UI Import", test_qenhanced_stream_output_import),
        ("StreamOutput Creation", test_stream_output_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 STREAMOUTPUT TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 StreamOutput module is working correctly!")
        return True
    else:
        logger.error("⚠️  Some StreamOutput tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 