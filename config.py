# Configuration file for MP3 Downloader

# Server Configuration
SERVER_HOST = '0.0.0.0'  # Use '127.0.0.1' for localhost only
SERVER_PORT = 5000
DEBUG_MODE = False

# Download Configuration
AUDIO_QUALITY = '320'  # Preferred audio quality in kbps (320, 256, 192, 128)
AUDIO_FORMAT = 'mp3'   # Output format (mp3, m4a, wav)
MAX_CONCURRENT_DOWNLOADS = 3  # Maximum simultaneous downloads

# File Management
TEMP_DIR = None  # Use None for system temp directory
CLEANUP_DELAY = 5  # Seconds to wait before cleaning up downloaded files
MAX_FILE_SIZE = 100  # Maximum file size in MB (0 for no limit)

# Platform Settings
ENABLE_SPOTIFY = True
ENABLE_APPLE_MUSIC = True
ENABLE_JIOSAAVN = True
ENABLE_YOUTUBE = True
ENABLE_SOUNDCLOUD = True

# Advanced Settings
USE_PROXY = False
PROXY_URL = None  # Example: 'http://proxy.example.com:8080'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
TIMEOUT = 30  # Request timeout in seconds

# UI Customization
APP_TITLE = 'MP3 Downloader'
APP_DESCRIPTION = 'Download high-quality music from your favorite platforms'
SHOW_PLATFORM_ICONS = True
SHOW_FEATURES_SECTION = True

# Security Settings
ALLOWED_HOSTS = ['*']  # List of allowed hosts, ['*'] for all
RATE_LIMIT_ENABLED = False
RATE_LIMIT_PER_MINUTE = 10  # Downloads per minute per IP

# Logging
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = False
LOG_FILE_PATH = 'mp3downloader.log'