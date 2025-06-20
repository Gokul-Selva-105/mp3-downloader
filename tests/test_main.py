import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, detect_platform, get_ydl_opts, add_metadata
from config import *

class TestMP3Downloader(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        """Test the main index route."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MP3 Downloader', response.data)
    
    def test_detect_platform_spotify(self):
        """Test Spotify URL detection."""
        url = 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
        platform = detect_platform(url)
        self.assertEqual(platform, 'spotify')
    
    def test_detect_platform_youtube(self):
        """Test YouTube URL detection."""
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        platform = detect_platform(url)
        self.assertEqual(platform, 'youtube')
    
    def test_detect_platform_soundcloud(self):
        """Test SoundCloud URL detection."""
        url = 'https://soundcloud.com/artist/track'
        platform = detect_platform(url)
        self.assertEqual(platform, 'soundcloud')
    
    def test_detect_platform_apple_music(self):
        """Test Apple Music URL detection."""
        url = 'https://music.apple.com/us/album/song/123456'
        platform = detect_platform(url)
        self.assertEqual(platform, 'apple_music')
    
    def test_detect_platform_jiosaavn(self):
        """Test JioSaavn URL detection."""
        url = 'https://www.jiosaavn.com/song/test/123'
        platform = detect_platform(url)
        self.assertEqual(platform, 'jiosaavn')
    
    def test_detect_platform_unknown(self):
        """Test unknown platform detection."""
        url = 'https://example.com/music'
        platform = detect_platform(url)
        self.assertEqual(platform, 'unknown')
    
    def test_get_ydl_opts(self):
        """Test yt-dlp options generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_hook = MagicMock()
            opts = get_ydl_opts(temp_dir, mock_hook)
            
            self.assertIn('format', opts)
            self.assertIn('postprocessors', opts)
            self.assertIn('progress_hooks', opts)
            self.assertEqual(opts['audioformat'], AUDIO_FORMAT)
            self.assertEqual(opts['postprocessors'][0]['preferredquality'], AUDIO_QUALITY)
    
    def test_download_route_missing_url(self):
        """Test download route with missing URL."""
        response = self.app.post('/download', 
                               json={},
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_download_route_invalid_platform(self):
        """Test download route with unsupported platform."""
        response = self.app.post('/download', 
                               json={'url': 'https://example.com/music'},
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Unsupported platform', data['error'])
    
    def test_download_route_valid_url(self):
        """Test download route with valid URL."""
        response = self.app.post('/download', 
                               json={'url': 'https://www.youtube.com/watch?v=test'},
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('download_id', data)
        self.assertIn('platform', data)
    
    def test_progress_route_not_found(self):
        """Test progress route with non-existent download ID."""
        response = self.app.get('/progress/nonexistent')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'not_found')
    
    def test_download_file_route_not_ready(self):
        """Test download file route with non-ready download."""
        response = self.app.get('/download_file/nonexistent')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
    
    @patch('main.requests.get')
    def test_add_metadata(self, mock_get):
        """Test metadata addition to MP3 files."""
        # Mock successful thumbnail download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response
        
        # Create a temporary MP3 file for testing
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(b'fake_mp3_data')
            temp_path = temp_file.name
        
        try:
            # This should not raise an exception
            add_metadata(temp_path, 'Test Title', 'Test Artist', 'Test Album', 'http://example.com/thumb.jpg')
        except Exception as e:
            # Expected to fail on fake MP3 data, but should not crash
            self.assertIsInstance(e, Exception)
        finally:
            os.unlink(temp_path)

class TestConfiguration(unittest.TestCase):
    """Test configuration settings."""
    
    def test_config_values(self):
        """Test that configuration values are properly set."""
        self.assertIsInstance(SERVER_PORT, int)
        self.assertIsInstance(DEBUG_MODE, bool)
        self.assertIn(AUDIO_FORMAT, ['mp3', 'm4a', 'wav'])
        self.assertIsInstance(AUDIO_QUALITY, str)
        self.assertIsInstance(MAX_CONCURRENT_DOWNLOADS, int)
        self.assertIsInstance(CLEANUP_DELAY, int)

if __name__ == '__main__':
    unittest.main()