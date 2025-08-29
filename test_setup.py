#!/usr/bin/env python3
"""
Test Setup Script for Gomaa Automation
Verifies that all dependencies are properly installed and working
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    # Test basic Python packages
    try:
        import json
        import asyncio
        import threading
        import time
        from datetime import datetime
        print("✅ Basic Python packages: OK")
    except ImportError as e:
        print(f"❌ Basic Python packages: FAILED - {e}")
        return False
    
    # Test Flask and Socket.IO
    try:
        from flask import Flask
        from flask_socketio import SocketIO
        print("✅ Flask and Socket.IO: OK")
    except ImportError as e:
        print(f"❌ Flask and Socket.IO: FAILED - {e}")
        return False
    
    # Test browser-use
    try:
        from browser_use import Agent, ChatGoogle
        from browser_use.browser import BrowserSession
        print("✅ browser-use: OK")
    except ImportError as e:
        print(f"⚠️  browser-use: NOT AVAILABLE - {e}")
        print("   This will limit some functionality")
    
    # Test Laminar
    try:
        from lmnr import Laminar
        print("✅ Laminar: OK")
    except ImportError as e:
        print(f"⚠️  Laminar: NOT AVAILABLE - {e}")
        print("   This will limit some functionality")
    
    # Test dotenv
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv: OK")
    except ImportError as e:
        print(f"❌ python-dotenv: FAILED - {e}")
        return False
    
    return True

def test_config_files():
    """Test for the presence of configuration files."""
    print("\n🔍 Testing for configuration files...")
    
    config_file = Path("professional_test_config.json")
    if config_file.exists():
        print(f"✅ Found '{config_file}'")
    else:
        print(f"⚠️  '{config_file}' not found. It will be created on first configuration save.")

    results_file = Path("professional_test_results.json")
    if results_file.exists():
        print(f"✅ Found '{results_file}'")
    else:
        print(f"⚠️  '{results_file}' not found. It will be created when a test is run.")

    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "professional_ai_automation.py",
        "templates/professional_dashboard.html",
        "requirements.txt",
        "pyproject.toml",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}: OK")
        else:
            print(f"❌ {file_path}: MISSING")
            all_exist = False
    
    return all_exist

def test_browser_automation():
    """Test basic browser automation setup"""
    print("\n🔍 Testing browser automation setup...")
    
    try:
        from browser_use.browser import BrowserSession
        
        # Test creating a browser session (without actually launching)
        session = BrowserSession(
            headless=True,  # Don't actually launch browser
            window_size={"width": 1920, "height": 1080}
        )
        print("✅ Browser session creation: OK")
        
    except Exception as e:
        print(f"❌ Browser session creation: FAILED - {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Gomaa Automation - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Config Files", test_config_files),
        ("File Structure", test_file_structure),
        ("Browser Automation", test_browser_automation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Gomaa Automation is ready to use.")
        print("\nNext steps:")
        print("1. Set your API keys in the .env file")
        print("2. Run: python professional_ai_automation.py")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: uv sync")
        print("2. Create .env file with API keys")
        print("3. Check file permissions and paths")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
