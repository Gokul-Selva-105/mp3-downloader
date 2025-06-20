#!/usr/bin/env python3
import requests
import time
import json

def test_download(url, description):
    """Test download with a specific URL"""
    
    print(f"\n=== Testing: {description} ===")
    print(f"URL: {url}")
    
    try:
        # Test server health
        response = requests.get("http://127.0.0.1:5000")
        if response.status_code != 200:
            print(f"❌ Server not responding: {response.status_code}")
            return False
        
        # Start download
        download_data = {'url': url}
        response = requests.post("http://127.0.0.1:5000/download", json=download_data)
        
        if response.status_code != 200:
            print(f"❌ Download request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        result = response.json()
        download_id = result.get('download_id')
        
        if not download_id:
            print(f"❌ No download ID received: {result}")
            return False
        
        print(f"✅ Download started with ID: {download_id}")
        
        # Monitor progress
        for i in range(20):  # Wait up to 20 seconds
            time.sleep(1)
            
            progress_response = requests.get(f"http://127.0.0.1:5000/progress/{download_id}")
            if progress_response.status_code == 200:
                progress = progress_response.json()
                status = progress.get('status', 'unknown')
                percentage = progress.get('percentage', 0)
                message = progress.get('message', '')
                
                print(f"Progress: {status} - {percentage}% - {message}")
                
                if status == 'completed':
                    print(f"✅ SUCCESS! Downloaded: {progress.get('title', 'Unknown')}")
                    print(f"File: {progress.get('filename', 'Unknown')}")
                    return True
                elif status == 'error':
                    print(f"❌ FAILED: {progress.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Failed to get progress: {progress_response.status_code}")
                return False
        
        print("❌ Download timed out")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run comprehensive tests"""
    
    print("🚀 Starting MP3 Downloader Tests")
    
    # Test URLs - from most likely to work to least likely
    test_cases = [
        {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'description': 'Classic YouTube Video (Rick Roll)'
        },
        {
            'url': 'https://youtu.be/dQw4w9WgXcQ',
            'description': 'YouTube Short URL'
        },
        {
            'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
            'description': 'Another YouTube Video (Me at the zoo)'
        },
        {
            'url': 'https://soundcloud.com/forss/flickermood',
            'description': 'SoundCloud Track'
        },
        {
            'url': 'https://music.youtube.com/watch?v=dQw4w9WgXcQ',
            'description': 'YouTube Music (same video)'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        success = test_download(test_case['url'], test_case['description'])
        results.append({
            'description': test_case['description'],
            'url': test_case['url'],
            'success': success
        })
        
        # Wait between tests
        time.sleep(2)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    successful = 0
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} - {result['description']}")
        if result['success']:
            successful += 1
    
    print(f"\n🎯 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    if successful > 0:
        print("\n🎉 At least one platform is working!")
    else:
        print("\n💥 No platforms are working - need to investigate yt-dlp setup")

if __name__ == "__main__":
    main()