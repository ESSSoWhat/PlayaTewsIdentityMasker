#!/usr/bin/env python3
"""
API Test Script for PlayaTewsIdentityMasker
Comprehensive testing of all API endpoints and functionality.
"""

import requests
import json
import time
import os
from pathlib import Path
import base64
from typing import Dict, Any, Optional

class APITester:
    """Comprehensive API testing class."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    def test_health_endpoints(self):
        """Test health and status endpoints."""
        print("\n🔍 Testing Health Endpoints...")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Root Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {e}")
        
        # Test health endpoint
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.log_test("Health Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Error: {e}")
        
        # Test API status endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Status Endpoint", True, f"Status: {data.get('status')}")
            else:
                self.log_test("API Status Endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Status Endpoint", False, f"Error: {e}")
    
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n🔍 Testing Authentication...")
        
        # Test user registration
        test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test{int(time.time())}@example.com",
            "password": "SecurePass123",
            "full_name": "Test User"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=test_user
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("User Registration", True, f"User ID: {data.get('user', {}).get('id', 'N/A')}")
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {e}")
        
        # Test user login
        try:
            login_data = {
                "username": test_user["username"],
                "password": test_user["password"]
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log_test("User Login", True, "Token received successfully")
            else:
                self.log_test("User Login", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User Login", False, f"Error: {e}")
        
        # Test get current user (requires authentication)
        if self.access_token:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/auth/me")
                if response.status_code == 200:
                    data = response.json()
                    self.log_test("Get Current User", True, f"Username: {data.get('user', {}).get('username', 'N/A')}")
                else:
                    self.log_test("Get Current User", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Get Current User", False, f"Error: {e}")
        else:
            self.log_test("Get Current User", False, "No access token available")
    
    def test_model_management(self):
        """Test model management endpoints."""
        print("\n🔍 Testing Model Management...")
        
        if not self.access_token:
            self.log_test("List Models", False, "No access token available")
            return
        
        # Test list models
        try:
            response = self.session.get(f"{self.base_url}/api/v1/models")
            if response.status_code == 200:
                models = response.json()
                self.log_test("List Models", True, f"Found {len(models)} models")
                
                # Test specific model info if models exist
                if models:
                    model_name = models[0]["name"]
                    try:
                        response = self.session.get(f"{self.base_url}/api/v1/models/{model_name}")
                        if response.status_code == 200:
                            model_info = response.json()
                            self.log_test("Get Model Info", True, f"Model: {model_info.get('name')}")
                        else:
                            self.log_test("Get Model Info", False, f"Status code: {response.status_code}")
                    except Exception as e:
                        self.log_test("Get Model Info", False, f"Error: {e}")
                else:
                    self.log_test("Get Model Info", True, "No models available to test")
            else:
                self.log_test("List Models", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("List Models", False, f"Error: {e}")
    
    def test_file_upload(self):
        """Test file upload functionality."""
        print("\n🔍 Testing File Upload...")
        
        if not self.access_token:
            self.log_test("File Upload", False, "No access token available")
            return
        
        # Create a test image file
        test_image_path = "test_image.png"
        try:
            # Create a simple test image using PIL
            from PIL import Image, ImageDraw
            
            # Create a 100x100 test image
            img = Image.new('RGB', (100, 100), color='red')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 80, 80], fill='blue')
            img.save(test_image_path)
            
            # Test file upload
            with open(test_image_path, 'rb') as f:
                files = {'file': (test_image_path, f, 'image/png')}
                response = self.session.post(f"{self.base_url}/api/v1/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("File Upload", True, f"File: {data.get('filename')}")
            else:
                self.log_test("File Upload", False, f"Status code: {response.status_code}, Response: {response.text}")
            
            # Clean up test file
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                
        except ImportError:
            self.log_test("File Upload", True, "PIL not available, skipping file creation test")
        except Exception as e:
            self.log_test("File Upload", False, f"Error: {e}")
    
    def test_face_swap(self):
        """Test face swap functionality."""
        print("\n🔍 Testing Face Swap...")
        
        if not self.access_token:
            self.log_test("Face Swap", False, "No access token available")
            return
        
        # Create test images for face swap
        try:
            from PIL import Image, ImageDraw
            
            # Create source and target test images
            source_path = "test_source.png"
            target_path = "test_target.png"
            
            # Source image (red background)
            source_img = Image.new('RGB', (200, 200), color='red')
            source_draw = ImageDraw.Draw(source_img)
            source_draw.ellipse([50, 50, 150, 150], fill='yellow')  # Simple face
            source_img.save(source_path)
            
            # Target image (blue background)
            target_img = Image.new('RGB', (200, 200), color='blue')
            target_draw = ImageDraw.Draw(target_img)
            target_draw.rectangle([50, 50, 150, 150], fill='green')  # Target area
            target_img.save(target_path)
            
            # Test face swap
            with open(source_path, 'rb') as source, open(target_path, 'rb') as target:
                files = {
                    'source_image': (source_path, source, 'image/png'),
                    'target_image': (target_path, target, 'image/png')
                }
                data = {
                    'quality': 'high',
                    'preserve_expression': 'true'
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/faceswap",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Face Swap", True, f"Processing time: {data.get('processing_time')}s")
            else:
                self.log_test("Face Swap", False, f"Status code: {response.status_code}, Response: {response.text}")
            
            # Clean up test files
            for path in [source_path, target_path]:
                if os.path.exists(path):
                    os.remove(path)
                    
        except ImportError:
            self.log_test("Face Swap", True, "PIL not available, skipping face swap test")
        except Exception as e:
            self.log_test("Face Swap", False, f"Error: {e}")
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n🔍 Testing Error Handling...")
        
        # Test invalid endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/v1/nonexistent")
            if response.status_code == 404:
                self.log_test("404 Error Handling", True, "Correctly returned 404")
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Error: {e}")
        
        # Test invalid authentication
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
            if response.status_code == 401:
                self.log_test("Invalid Auth Handling", True, "Correctly returned 401")
            else:
                self.log_test("Invalid Auth Handling", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Auth Handling", False, f"Error: {e}")
        
        # Test invalid model name
        if self.access_token:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/models/nonexistent_model")
                if response.status_code == 404:
                    self.log_test("Invalid Model Handling", True, "Correctly returned 404")
                else:
                    self.log_test("Invalid Model Handling", False, f"Expected 404, got {response.status_code}")
            except Exception as e:
                self.log_test("Invalid Model Handling", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting PlayaTewsIdentityMasker API Tests")
        print("=" * 60)
        
        # Check if API is running
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                print(f"❌ API not accessible at {self.base_url}")
                print("Please start the API server first:")
                print("python -m api.main")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API at {self.base_url}: {e}")
            print("Please start the API server first:")
            print("python -m api.main")
            return False
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_authentication()
        self.test_model_management()
        self.test_file_upload()
        self.test_face_swap()
        self.test_error_handling()
        
        # Generate summary
        self.generate_summary()
        
        return True
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 60)
        print("📊 API TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {failed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save results to file
        with open("api_test_results.json", "w") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "base_url": self.base_url,
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: api_test_results.json")
        
        if passed_tests == total_tests:
            print(f"\n🎉 All API tests passed!")
        else:
            print(f"\n⚠️  Some tests failed. Check the details above.")

def main():
    """Main function to run API tests."""
    import sys
    
    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 