#!/usr/bin/env python3
"""
Comprehensive API Test Script for PlayaTewsIdentityMasker
Tests all endpoints and verifies API functionality.
"""

import requests
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add the current directory to Python path
sys.path.append('.')

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
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_health_endpoints(self) -> bool:
        """Test health check endpoints."""
        print("\n🔍 Testing Health Endpoints...")
        
        try:
            # Test basic health check
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Basic Health Check", True)
                else:
                    self.log_test("Basic Health Check", False, f"Unexpected status: {data.get('status')}")
            else:
                self.log_test("Basic Health Check", False, f"Status code: {response.status_code}")
            
            # Test detailed health check
            response = self.session.get(f"{self.base_url}/health/detailed")
            if response.status_code == 200:
                data = response.json()
                if "components" in data:
                    self.log_test("Detailed Health Check", True)
                else:
                    self.log_test("Detailed Health Check", False, "Missing components")
            else:
                self.log_test("Detailed Health Check", False, f"Status code: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Health Endpoints", False, f"Exception: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication endpoints."""
        print("\n🔐 Testing Authentication...")
        
        try:
            # Test user registration
            register_data = {
                "username": "testuser_api",
                "email": "test@api.com",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_test("User Registration", True)
                    self.access_token = data["access_token"]
                else:
                    self.log_test("User Registration", False, "No access token received")
            else:
                self.log_test("User Registration", False, f"Status code: {response.status_code}")
            
            # Test user login
            login_data = {
                "username": "testuser_api",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.log_test("User Login", True)
                    self.access_token = data["access_token"]
                else:
                    self.log_test("User Login", False, "No access token received")
            else:
                self.log_test("User Login", False, f"Status code: {response.status_code}")
            
            # Test getting current user info
            if self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = self.session.get(
                    f"{self.base_url}/api/v1/auth/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("username") == "testuser_api":
                        self.log_test("Get Current User", True)
                    else:
                        self.log_test("Get Current User", False, "Wrong user data")
                else:
                    self.log_test("Get Current User", False, f"Status code: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_model_management(self) -> bool:
        """Test model management endpoints."""
        print("\n🎭 Testing Model Management...")
        
        if not self.access_token:
            self.log_test("Model Management", False, "No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Test listing models
            response = self.session.get(
                f"{self.base_url}/api/v1/models",
                headers=headers
            )
            
            if response.status_code == 200:
                models = response.json()
                if isinstance(models, list):
                    self.log_test("List Models", True, f"Found {len(models)} models")
                    
                    # Test getting specific model info
                    if models:
                        model_name = models[0]["name"]
                        response = self.session.get(
                            f"{self.base_url}/api/v1/models/{model_name}",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            model_info = response.json()
                            if model_info.get("name") == model_name:
                                self.log_test("Get Model Info", True)
                            else:
                                self.log_test("Get Model Info", False, "Wrong model data")
                        else:
                            self.log_test("Get Model Info", False, f"Status code: {response.status_code}")
                else:
                    self.log_test("List Models", False, "Response is not a list")
            else:
                self.log_test("List Models", False, f"Status code: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Model Management", False, f"Exception: {str(e)}")
            return False
    
    def test_file_upload(self) -> bool:
        """Test file upload functionality."""
        print("\n📁 Testing File Upload...")
        
        if not self.access_token:
            self.log_test("File Upload", False, "No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Create a dummy image file for testing
            test_image_path = "test_image.jpg"
            self._create_dummy_image(test_image_path)
            
            # Test file upload
            with open(test_image_path, "rb") as f:
                files = {"file": ("test_image.jpg", f, "image/jpeg")}
                response = self.session.post(
                    f"{self.base_url}/api/v1/upload",
                    headers=headers,
                    files=files
                )
            
            # Clean up test file
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
            
            if response.status_code == 200:
                data = response.json()
                if "filename" in data and "url" in data:
                    self.log_test("File Upload", True, f"Uploaded: {data['filename']}")
                else:
                    self.log_test("File Upload", False, "Missing response fields")
            else:
                self.log_test("File Upload", False, f"Status code: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("File Upload", False, f"Exception: {str(e)}")
            return False
    
    def test_face_swap(self) -> bool:
        """Test face swap functionality."""
        print("\n🔄 Testing Face Swap...")
        
        if not self.access_token:
            self.log_test("Face Swap", False, "No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Test face swap request (simulated)
            face_swap_data = {
                "source_image": "/uploads/test_source.jpg",
                "target_image": "/uploads/test_target.jpg",
                "model_name": "Liu_Lice",
                "quality": "high",
                "preserve_expression": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/faceswap",
                json=face_swap_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result_image" in data and "processing_time" in data:
                    self.log_test("Face Swap", True, f"Processing time: {data['processing_time']}s")
                else:
                    self.log_test("Face Swap", False, "Missing response fields")
            else:
                self.log_test("Face Swap", False, f"Status code: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Face Swap", False, f"Exception: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and validation."""
        print("\n⚠️ Testing Error Handling...")
        
        try:
            # Test invalid authentication
            headers = {"Authorization": "Bearer invalid_token"}
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=headers
            )
            
            if response.status_code == 401:
                self.log_test("Invalid Token Handling", True)
            else:
                self.log_test("Invalid Token Handling", False, f"Expected 401, got {response.status_code}")
            
            # Test invalid registration data
            invalid_data = {
                "username": "a",  # Too short
                "email": "invalid-email",
                "password": "weak"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=invalid_data
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Input Validation", True)
            else:
                self.log_test("Input Validation", False, f"Expected 422, got {response.status_code}")
            
            # Test non-existent endpoint
            response = self.session.get(f"{self.base_url}/api/v1/nonexistent")
            
            if response.status_code == 404:
                self.log_test("404 Error Handling", True)
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality."""
        print("\n⏱️ Testing Rate Limiting...")
        
        try:
            # Make multiple requests quickly
            responses = []
            for i in range(105):  # Exceed the 100 request limit
                response = self.session.get(f"{self.base_url}/health")
                responses.append(response.status_code)
            
            # Check if rate limiting kicked in
            if 429 in responses:
                self.log_test("Rate Limiting", True, "Rate limit enforced")
            else:
                self.log_test("Rate Limiting", False, "Rate limit not enforced")
            
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Exception: {str(e)}")
            return False
    
    def _create_dummy_image(self, filename: str):
        """Create a dummy image file for testing."""
        try:
            from PIL import Image
            import numpy as np
            
            # Create a simple test image
            img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            img = Image.fromarray(img_array)
            img.save(filename, "JPEG")
            
        except ImportError:
            # Fallback: create a minimal JPEG file
            with open(filename, "wb") as f:
                f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\x27 ,#\x1c\x1c(7),01444\x1f\x27=9=82<.342\xff\xc0\x00\x11\x08\x00d\x00d\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests."""
        print("🚀 Starting PlayaTewsIdentityMasker API Tests")
        print("=" * 60)
        
        test_functions = [
            self.test_health_endpoints,
            self.test_authentication,
            self.test_model_management,
            self.test_file_upload,
            self.test_face_swap,
            self.test_error_handling,
            self.test_rate_limiting
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
                total_tests += 1
            except Exception as e:
                self.log_test(test_func.__name__, False, f"Test function failed: {str(e)}")
                total_tests += 1
        
        # Generate summary
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
    
    def generate_summary(self, summary: Dict[str, Any]):
        """Generate and display test summary."""
        print("\n" + "=" * 60)
        print("📊 API TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\nTimestamp: {summary['timestamp']}")
        
        # Save results to file
        results_file = "api_test_results.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        # Overall status
        if summary['success_rate'] >= 80:
            print("\n🎉 API is working well!")
        elif summary['success_rate'] >= 60:
            print("\n⚠️ API has some issues that need attention.")
        else:
            print("\n❌ API has significant issues that need to be fixed.")
        
        return summary['success_rate'] >= 80


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test PlayaTewsIdentityMasker API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--no-start", action="store_true", help="Don't start the API server")
    
    args = parser.parse_args()
    
    # Check if API is running
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API is not responding at {args.url}")
            print("Make sure the API server is running:")
            print("  python -m api.main")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to API at {args.url}")
        print("Make sure the API server is running:")
        print("  python -m api.main")
        return False
    
    # Run tests
    tester = APITester(args.url)
    summary = tester.run_all_tests()
    success = tester.generate_summary(summary)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 