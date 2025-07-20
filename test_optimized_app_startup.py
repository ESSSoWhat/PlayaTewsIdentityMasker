#!/usr/bin/env python3
"""
Test script to verify PlayaTewsIdentityMaskerOptimized application startup
"""

import sys
import time
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_optimized_app_startup():
    """Test that the optimized app starts successfully"""
    logger.info("🧪 Testing PlayaTewsIdentityMaskerOptimized startup...")
    
    try:
        # Start the optimized app in background
        process = subprocess.Popen(
            [sys.executable, "main.py", "run", "PlayaTewsIdentityMaskerOptimized"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            logger.info("✅ Application started successfully and is running")
            
            # Check for any error output
            stdout, stderr = process.communicate(timeout=2)
            
            if stderr:
                logger.warning(f"⚠️  Some warnings/errors during startup:\n{stderr}")
            
            if "ERROR" in stdout or "ERROR" in stderr:
                logger.error("❌ Errors detected during startup")
                return False
            else:
                logger.info("✅ No critical errors detected")
                return True
        else:
            # Process terminated
            stdout, stderr = process.communicate()
            logger.error(f"❌ Application failed to start. Exit code: {process.returncode}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Application startup timed out")
        process.kill()
        return False
    except Exception as e:
        logger.error(f"❌ Error testing application startup: {e}")
        return False

def test_backend_components():
    """Test that backend components can be imported and initialized"""
    logger.info("🧪 Testing backend component imports...")
    
    try:
        from apps.PlayaTewsIdentityMasker import backend
        logger.info("✅ Backend module imported successfully")
        
        # Test key backend classes
        from apps.PlayaTewsIdentityMasker.backend import (
            BackendDB, BackendWeakHeap, BackendSignal, BackendConnection,
            FileSource, CameraSource, FaceDetector, FaceAligner
        )
        logger.info("✅ Key backend classes imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Backend component import failed: {e}")
        return False

def test_ui_components():
    """Test that UI components can be imported"""
    logger.info("🧪 Testing UI component imports...")
    
    try:
        from apps.PlayaTewsIdentityMasker.ui import (
            QFileSource, QCameraSource, QFaceDetector, QFaceAligner
        )
        logger.info("✅ UI components imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ UI component import failed: {e}")
        return False

def test_optimized_app_class():
    """Test that the optimized app class can be instantiated"""
    logger.info("🧪 Testing optimized app class instantiation...")
    
    try:
        from apps.PlayaTewsIdentityMasker.QOptimizedPlayaTewsIdentityMaskerApp import (
            OptimizedPlayaTewsIdentityMaskerApp
        )
        logger.info("✅ Optimized app class imported successfully")
        
        # Test instantiation (without full initialization)
        userdata_path = Path("userdata")
        app = OptimizedPlayaTewsIdentityMaskerApp(userdata_path)
        logger.info("✅ Optimized app class instantiated successfully")
        
        return True
    except Exception as e:
        logger.error(f"❌ Optimized app class test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting PlayaTewsIdentityMaskerOptimized comprehensive tests...")
    
    tests = [
        ("Backend Components", test_backend_components),
        ("UI Components", test_ui_components),
        ("Optimized App Class", test_optimized_app_class),
        ("Application Startup", test_optimized_app_startup),
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
    logger.info("📊 TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! PlayaTewsIdentityMaskerOptimized is ready!")
        return True
    else:
        logger.error("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 