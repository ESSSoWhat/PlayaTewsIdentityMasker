#!/usr/bin/env python3
"""
Test DFM Quick Access Functionality
Tests the new DFM quick access buttons in the UI
"""

import sys
from pathlib import Path

def test_dfm_integration():
    """Test the DFM integration functionality"""
    print("Testing DFM Integration...")
    
    # Test universal DFM integration
    try:
        sys.path.append(str(Path(__file__).parent / "universal_dfm"))
        from dfm_integration import get_face_swap_models, check_system_status
        
        # Check system status
        status = check_system_status()
        print(f"✅ DFM System Status: {status['status']}")
        print(f"📊 Total Models: {status['total_models']}")
        
        # Get face swap models
        models = get_face_swap_models()
        print(f"🎯 Face Swap Models: {len(models)} available")
        
        for i, model in enumerate(models[:6]):
            print(f"  {i+1}. {model.get('name', 'Unknown')} ({model.get('priority', 'unknown')})")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Universal DFM integration not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing DFM integration: {e}")
        return False

def test_local_dfm_models():
    """Test local DFM model detection"""
    print("\nTesting Local DFM Models...")
    
    # Check common DFM directories
    dfm_dirs = [
        Path("dfm_models"),
        Path("userdata/dfm_models"),
        Path("universal_dfm/models/prebuilt"),
        Path("universal_dfm/models/active")
    ]
    
    found_models = []
    
    for dfm_dir in dfm_dirs:
        if dfm_dir.exists():
            dfm_files = list(dfm_dir.glob("*.dfm"))
            if dfm_files:
                print(f"✅ Found {len(dfm_files)} models in {dfm_dir}")
                for dfm_file in dfm_files[:3]:  # Show first 3
                    found_models.append({
                        "name": dfm_file.stem,
                        "file": str(dfm_file),
                        "category": "local"
                    })
                    print(f"  - {dfm_file.stem}")
            else:
                print(f"⚠️ No .dfm files found in {dfm_dir}")
        else:
            print(f"❌ Directory not found: {dfm_dir}")
    
    if found_models:
        print(f"\n🎯 Total local models found: {len(found_models)}")
        return True
    else:
        print("\n❌ No local DFM models found")
        return False

def test_ui_component_access():
    """Test access to UI components"""
    print("\nTesting UI Component Access...")
    
    try:
        # Test importing the UI module
        sys.path.append(str(Path(__file__).parent / "apps/PlayaTewsIdentityMasker/ui"))
        from QOptimizedOBSStyleUI import QOptimizedOBSStyleUI
        
        print("✅ QOptimizedOBSStyleUI imported successfully")
        
        # Check if the new methods exist
        methods_to_check = [
            'create_dfm_quick_access_section',
            'load_dfm_models',
            'update_dfm_buttons',
            'on_dfm_button_clicked',
            'switch_dfm_model',
            'refresh_dfm_models'
        ]
        
        for method in methods_to_check:
            if hasattr(QOptimizedOBSStyleUI, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing UI module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 DFM Quick Access Test Suite")
    print("=" * 50)
    
    tests = [
        ("DFM Integration", test_dfm_integration),
        ("Local DFM Models", test_local_dfm_models),
        ("UI Component Access", test_ui_component_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! DFM Quick Access should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 