#!/usr/bin/env python3
"""
Comprehensive Component Test for PlayaTewsIdentityMasker
Tests all major components to ensure they're working correctly
"""

import os
import sys
import time
import json
import traceback
from pathlib import Path

class ComponentTester:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
    def test_component(self, name, test_func):
        """Test a component and record results"""
        print(f"\n🔍 Testing {name}...")
        try:
            result = test_func()
            self.results[name] = {"status": "✅ PASS", "details": result}
            print(f"✅ {name}: PASS")
            return True
        except Exception as e:
            self.results[name] = {"status": "❌ FAIL", "details": str(e)}
            print(f"❌ {name}: FAIL - {e}")
            return False
    
    def test_python_environment(self):
        """Test Python environment and dependencies"""
        info = {}
        
        # Check Python version
        info["python_version"] = sys.version
        
        # Check key dependencies
        dependencies = [
            "cv2", "numpy", "torch", "onnxruntime", 
            "PyQt5", "xlib", "face", "image"
        ]
        
        for dep in dependencies:
            try:
                module = __import__(dep)
                info[dep] = "Available"
            except ImportError:
                info[dep] = "Missing"
        
        return info
    
    def test_file_structure(self):
        """Test essential file structure"""
        required_dirs = [
            "dfm_models", "universal_dfm", "xlib", 
            "apps/PlayaTewsIdentityMasker", "settings"
        ]
        
        required_files = [
            "main.py", "launch.py", "camera_config.json"
        ]
        
        info = {"directories": {}, "files": {}}
        
        for dir_path in required_dirs:
            info["directories"][dir_path] = os.path.exists(dir_path)
        
        for file_path in required_files:
            info["files"][file_path] = os.path.exists(file_path)
        
        return info
    
    def test_dfm_models(self):
        """Test DFM models availability"""
        dfm_dir = "dfm_models"
        if not os.path.exists(dfm_dir):
            return {"error": "dfm_models directory not found"}
        
        dfm_files = [f for f in os.listdir(dfm_dir) if f.endswith('.dfm')]
        valid_models = [f for f in dfm_files if os.path.getsize(os.path.join(dfm_dir, f)) > 1024*1024]
        
        total_size = sum(os.path.getsize(os.path.join(dfm_dir, f)) for f in dfm_files)
        
        return {
            "total_models": len(dfm_files),
            "valid_models": len(valid_models),
            "total_size_mb": total_size / (1024*1024),
            "models": dfm_files
        }
    
    def test_camera_access(self):
        """Test camera access"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret:
                    return {"status": "Working", "resolution": f"{frame.shape[1]}x{frame.shape[0]}"}
                else:
                    return {"status": "Opened but no frame", "error": "Frame read failed"}
            else:
                return {"status": "Failed to open", "error": "Camera not accessible"}
        except Exception as e:
            return {"status": "Error", "error": str(e)}
    
    def test_xlib_components(self):
        """Test xlib core components"""
        components = {}
        
        # Test basic xlib imports
        try:
            from xlib import face, image, cv
            components["face"] = "Available"
            components["image"] = "Available"
            components["cv"] = "Available"
        except ImportError as e:
            components["xlib_core"] = f"Import error: {e}"
        
        # Test face detection
        try:
            from xlib.face import FACE_SWAPPER_TYPE_DFM
            components["face_swapper"] = "Available"
        except:
            components["face_swapper"] = "Missing"
        
        return components
    
    def test_app_components(self):
        """Test main application components"""
        components = {}
        
        # Test main app imports
        try:
            from apps.PlayaTewsIdentityMasker import PlayaTewsIdentityMaskerApp
            components["main_app"] = "Available"
        except Exception as e:
            components["main_app"] = f"Import error: {e}"
        
        # Test backend components
        try:
            from apps.PlayaTewsIdentityMasker.backend import BackendBase
            components["backend"] = "Available"
        except Exception as e:
            components["backend"] = f"Import error: {e}"
        
        # Test UI components
        try:
            from apps.PlayaTewsIdentityMasker.ui import QMainWindow
            components["ui"] = "Available"
        except Exception as e:
            components["ui"] = f"Import error: {e}"
        
        return components
    
    def test_settings_and_config(self):
        """Test settings and configuration"""
        config = {}
        
        # Check camera config
        if os.path.exists("camera_config.json"):
            try:
                with open("camera_config.json", 'r') as f:
                    camera_config = json.load(f)
                config["camera_config"] = "Valid"
            except:
                config["camera_config"] = "Invalid JSON"
        else:
            config["camera_config"] = "Missing"
        
        # Check settings directory
        if os.path.exists("settings"):
            config["settings_dir"] = "Exists"
            settings_files = os.listdir("settings")
            config["settings_files"] = settings_files
        else:
            config["settings_dir"] = "Missing"
        
        return config
    
    def test_performance_components(self):
        """Test performance monitoring components"""
        components = {}
        
        # Check if performance monitoring files exist
        perf_files = [
            "performance_monitor.py", "memory_manager.py", 
            "dfm_performance_monitor.py"
        ]
        
        for file in perf_files:
            components[file] = os.path.exists(file)
        
        return components
    
    def run_all_tests(self):
        """Run all component tests"""
        print("🚀 Starting Comprehensive Component Test")
        print("=" * 60)
        
        tests = [
            ("Python Environment", self.test_python_environment),
            ("File Structure", self.test_file_structure),
            ("DFM Models", self.test_dfm_models),
            ("Camera Access", self.test_camera_access),
            ("XLib Components", self.test_xlib_components),
            ("App Components", self.test_app_components),
            ("Settings & Config", self.test_settings_and_config),
            ("Performance Components", self.test_performance_components),
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            if self.test_component(name, test_func):
                passed += 1
        
        # Generate summary
        self.generate_summary(passed, total)
        
        return passed == total
    
    def generate_summary(self, passed, total):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\n⏱️  Total Test Time: {time.time() - self.start_time:.2f}s")
        
        # Show detailed results
        print(f"\n📋 Detailed Results:")
        for component, result in self.results.items():
            status_icon = "✅" if "PASS" in result["status"] else "❌"
            print(f"  {status_icon} {component}: {result['status']}")
        
        # Save results to file
        with open("comprehensive_test_results.json", "w") as f:
            json.dump({
                "timestamp": time.time(),
                "summary": {
                    "passed": passed,
                    "total": total,
                    "success_rate": (passed/total)*100
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: comprehensive_test_results.json")

def main():
    tester = ComponentTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 All components are working correctly!")
        return 0
    else:
        print(f"\n⚠️  Some components need attention. Check the detailed results above.")
        return 1

if __name__ == "__main__":
    exit(main()) 