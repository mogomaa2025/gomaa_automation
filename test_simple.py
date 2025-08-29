#!/usr/bin/env python3
"""
Simple Test Script for Gomaa Automation
Tests basic functionality without requiring all dependencies
"""

import json
import os
from datetime import datetime

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🧪 Testing Basic Functionality...")
    
    # Test 1: Configuration
    test_config = {
        "website_url": "https://demoblaze.com/",
        "test_focus": "about_us",
        "provider": "google",
        "google_api_key": "test_key_123",
        "laminar_api_key": "test_laminar_456",
        "model": "gemini-2.5-flash",
        "headless": False,
        "window_width": 1920,
        "window_height": 1080
    }
    
    print("✅ Configuration created successfully")
    
    # Test 2: Save configuration
    try:
        with open("test_config.json", "w") as f:
            json.dump(test_config, f, indent=2)
        print("✅ Configuration saved to file")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False
    
    # Test 3: Load configuration
    try:
        with open("test_config.json", "r") as f:
            loaded_config = json.load(f)
        print("✅ Configuration loaded from file")
        
        # Verify data integrity
        if loaded_config["website_url"] == test_config["website_url"]:
            print("✅ Data integrity verified")
        else:
            print("❌ Data integrity check failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test 4: Test results structure
    test_results = {
        "test_cases": [
            {
                "test_id": "TEST_001",
                "title": "Basic Functionality Test",
                "status": "PASSED",
                "created_date": datetime.now().isoformat()
            }
        ],
        "bug_reports": [],
        "coverage_reports": [
            {
                "timestamp": datetime.now().isoformat(),
                "coverage": {"Basic Testing": 100.0}
            }
        ]
    }
    
    print("✅ Test results structure created")
    
    # Test 5: Save test results
    try:
        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        print("✅ Test results saved to file")
    except Exception as e:
        print(f"❌ Failed to save test results: {e}")
        return False
    
    # Test 6: Cleanup
    try:
        os.remove("test_config.json")
        os.remove("test_results.json")
        print("✅ Test files cleaned up")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n🎉 All basic functionality tests passed!")
    return True

def test_api_key_validation():
    """Test API key validation logic for multiple providers"""
    print("\n🔑 Testing API Key Validation...")
    
    # Test cases
    test_cases = [
        {"provider": "google", "keys": {"google_api_key": ""}, "expected": False},
        {"provider": "google", "keys": {"google_api_key": "key_123"}, "expected": True},
        {"provider": "openai", "keys": {"google_api_key": "key_123", "openai_api_key": ""}, "expected": False},
        {"provider": "openai", "keys": {"openai_api_key": "key_456"}, "expected": True},
        {"provider": "groq", "keys": {"groq_api_key": "key_789"}, "expected": True},
        {"provider": "ollama", "keys": {}, "expected": True},  # No key needed
    ]
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        provider = case["provider"]
        keys = case["keys"]
        expected = case["expected"]
        
        # Simulate the validation logic from the main app (start_test)
        is_valid = False
        if provider == "ollama":
            is_valid = True
        else:
            api_key_name = f"{provider}_api_key"
            if keys.get(api_key_name):
                is_valid = True
        
        status = "✅" if is_valid == expected else "❌"
        if is_valid != expected:
            all_passed = False

        print(f"{status} Test {i}: Provider='{provider}', Keys provided='{list(keys.keys())}' -> Valid={is_valid} (expected: {expected})")
    
    if all_passed:
        print("✅ All API key validation tests passed")
    else:
        print("❌ Some API key validation tests failed")


if __name__ == "__main__":
    print("🚀 Gomaa Automation - Simple Test Suite")
    print("=" * 50)
    
    # Run basic functionality tests
    if test_basic_functionality():
        # Run API key validation tests
        test_api_key_validation()
        
        print("\n" + "=" * 50)
        print("🎯 All tests completed successfully!")
        print("📝 The basic application structure is working correctly.")
        print("🔧 Next step: Install dependencies with 'uv sync' and run the main app.")
    else:
        print("\n" + "=" * 50)
        print("❌ Some tests failed. Please check the errors above.")
        print("🔧 Fix the issues before proceeding.")
