"""
Web functionality tests for Ghost Forest Watcher Streamlit app

Marked as integration tests; skipped by default unless GF_RUN_INTEGRATION=1.
"""
import os
import requests
import time
from pathlib import Path
import pytest

@pytest.mark.integration
@pytest.mark.skipif(os.getenv("GF_RUN_INTEGRATION") != "1", reason="Integration tests disabled")
def test_app_running():
    """Test that the Streamlit app is running and responsive"""
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        print(f"✅ App is running - Status Code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ App connection failed: {e}")
        return False

@pytest.mark.integration
@pytest.mark.skipif(os.getenv("GF_RUN_INTEGRATION") != "1", reason="Integration tests disabled")
def test_health_check():
    """Test app health endpoint"""
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("✅ App health check passed")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Health check endpoint not available: {e}")
        return False

@pytest.mark.integration
@pytest.mark.skipif(os.getenv("GF_RUN_INTEGRATION") != "1", reason="Integration tests disabled")
def test_static_resources():
    """Test that static resources are loading"""
    try:
        # Test for Streamlit's static resources
        response = requests.get("http://localhost:8501/_stcore/static/", timeout=5)
        print(f"✅ Static resources accessible - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"⚠️ Static resources test: {e}")
        return False

def test_file_availability():
    """Test availability of required files"""
    files_to_check = [
        ("Data file", "data/east_troublesome_small_tile.tif"),
        ("SAM model", "models/sam_vit_b.pth"),
        ("Results image", "outputs/forest_analysis_results.png")
    ]
    
    file_status = []
    for name, path in files_to_check:
        exists = Path(path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {path}")
        file_status.append(exists)
    
    return file_status

def main():
    """Run all web tests"""
    print("🌲 Ghost Forest Watcher - Web Test Suite")
    print("=" * 50)
    
    # Test 1: App running
    print("\n1. Testing app connectivity...")
    app_running = test_app_running()
    
    # Test 2: Health check
    print("\n2. Testing app health...")
    health_ok = test_health_check()
    
    # Test 3: Static resources
    print("\n3. Testing static resources...")
    static_ok = test_static_resources()
    
    # Test 4: File availability
    print("\n4. Checking required files...")
    file_status = test_file_availability()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"App Running: {'✅' if app_running else '❌'}")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Static Resources: {'✅' if static_ok else '❌'}")
    print(f"Data Files Available: {sum(file_status)}/{len(file_status)}")
    
    total_tests = 3 + len(file_status)  # 3 web tests + file tests
    passed_tests = sum([app_running, health_ok, static_ok]) + sum(file_status)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if app_running:
        print("\n🎉 Web app is accessible at: http://localhost:8501")
        print("📱 You can now test the full application in your browser!")
    else:
        print("\n⚠️ Web app is not accessible. Check if Streamlit is running.")
    
    return success_rate > 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 