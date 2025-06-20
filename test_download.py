#!/usr/bin/env python3
"""
Test script to verify the MP3 downloader functionality
"""

import requests
import json
import time

# Test URL - using a public YouTube video that doesn't require authentication
TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (public video)
BASE_URL = "http://127.0.0.1:5000"

def test_single_download():
    """Test single track download"""
    print("Testing single track download...")
    print(f"URL: {TEST_URL}")
    
    # Start download
    response = requests.post(f"{BASE_URL}/download", 
                           json={"url": TEST_URL},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code != 200:
        print(f"Error starting download: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    download_id = data.get("download_id")
    print(f"Download started with ID: {download_id}")
    
    # Monitor progress
    while True:
        progress_response = requests.get(f"{BASE_URL}/progress/{download_id}")
        if progress_response.status_code != 200:
            print(f"Error checking progress: {progress_response.status_code}")
            break
            
        progress = progress_response.json()
        status = progress.get("status")
        percentage = progress.get("percentage", 0)
        message = progress.get("message", "")
        
        print(f"Status: {status} | Progress: {percentage:.1f}% | {message}")
        
        if status == "completed":
            print("✅ Download completed successfully!")
            print(f"Title: {progress.get('title', 'Unknown')}")
            print(f"Artist: {progress.get('artist', 'Unknown')}")
            print(f"Download URL: {BASE_URL}/download_file/{download_id}")
            return True
        elif status == "error":
            print(f"❌ Download failed: {progress.get('error', 'Unknown error')}")
            return False
        
        time.sleep(2)
    
    return False

def test_server_health():
    """Test if server is responding"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🎵 MP3 Downloader Test Suite")
    print("=" * 40)
    
    # Test server health
    if not test_server_health():
        print("Server is not responding. Please start the server first.")
        exit(1)
    
    # Test single download
    success = test_single_download()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")