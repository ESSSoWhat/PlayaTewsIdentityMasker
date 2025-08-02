#!/usr/bin/env python3
"""
Test script for PlayaTews Identity Masker MLOps API
Tests all endpoints to ensure they're working correctly
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        if response.status_code == 200:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing PlayaTews Identity Masker MLOps API")
    print("=" * 50)
    print(f"Timestamp: {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Test results
    tests = []
    
    # Test root endpoint
    print("1. Testing Root Endpoint")
    print("-" * 30)
    tests.append(test_endpoint("/"))
    print()
    
    # Test health endpoint
    print("2. Testing Health Endpoint")
    print("-" * 30)
    tests.append(test_endpoint("/health"))
    print()
    
    # Test metrics endpoint
    print("3. Testing Metrics Endpoint")
    print("-" * 30)
    tests.append(test_endpoint("/metrics"))
    print()
    
    # Test models endpoint
    print("4. Testing Models Endpoint")
    print("-" * 30)
    tests.append(test_endpoint("/models"))
    print()
    
    # Test experiments endpoint
    print("5. Testing Experiments Endpoint")
    print("-" * 30)
    tests.append(test_endpoint("/experiments"))
    print()
    
    # Test prediction endpoint
    print("6. Testing Prediction Endpoint")
    print("-" * 30)
    test_data = {
        "image_path": "/path/to/test/image.jpg",
        "model_id": "face_detection_v1",
        "parameters": {
            "confidence_threshold": 0.8,
            "max_faces": 10
        }
    }
    tests.append(test_endpoint("/predict", method="POST", data=test_data))
    print()
    
    # Test API documentation
    print("7. Testing API Documentation")
    print("-" * 30)
    tests.append(test_endpoint("/docs"))
    print()
    
    # Summary
    print("Test Summary")
    print("=" * 50)
    passed = sum(tests)
    total = len(tests)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Excellent! API is working perfectly")
    elif success_rate >= 75:
        print("✅ Good! API is mostly working")
    elif success_rate >= 50:
        print("⚠️  Fair! Some issues detected")
    else:
        print("❌ Poor! Major issues detected")
    
    print()
    print("API Endpoints:")
    print(f"  Root: {BASE_URL}/")
    print(f"  Health: {BASE_URL}/health")
    print(f"  Metrics: {BASE_URL}/metrics")
    print(f"  Models: {BASE_URL}/models")
    print(f"  Experiments: {BASE_URL}/experiments")
    print(f"  Predict: {BASE_URL}/predict")
    print(f"  Docs: {BASE_URL}/docs")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 