from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile
import threading
import time
import uuid
from urllib.parse import urlparse
import re
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
import requests
from io import BytesIO
import logging
from config import *

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH) if LOG_TO_FILE else logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global dictionary to store download progress
download_progress = {}

class DownloadProgressHook:
    def __init__(self, download_id):
        self.download_id = download_id
    
    def __call__(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percent = 0
            
            download_progress[self.download_id] = {
                'status': 'downloading',
                'percent': min(percent, 100),
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
        elif d['status'] == 'finished':
            download_progress[self.download_id] = {
                'status': 'finished',
                'percent': 100,
                'filename': d['filename']
            }
        elif d['status'] == 'error':
            download_progress[self.download_id] = {
                'status': 'error',
                'percent': 0,
                'error': str(d.get('error', 'Unknown error'))
            }

def detect_platform(url):
    """Detect the music platform from URL"""
    url = url.lower()
    
    if 'spotify.com' in url:
        return 'spotify'
    elif 'music.apple.com' in url:
        return 'apple_music'
    elif 'jiosaavn.com' in url or 'saavn.com' in url:
        return 'jiosaavn'
    elif 'music.youtube.com' in url or 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'soundcloud.com' in url:
        return 'soundcloud'
    else:
        return 'unknown'

def get_ydl_opts(output_path, progress_hook):
    """Get yt-dlp options for different platforms"""
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': AUDIO_FORMAT,
            'preferredquality': AUDIO_QUALITY,
        }],
        'progress_hooks': [progress_hook],
        'extractaudio': True,
        'audioformat': AUDIO_FORMAT,
        'audioquality': 0,  # Best quality
        'embed_subs': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'socket_timeout': TIMEOUT,
    }
    
    # Add proxy if configured
    if USE_PROXY and PROXY_URL:
        opts['proxy'] = PROXY_URL
    
    # Add user agent
    if USER_AGENT:
        opts['http_headers'] = {'User-Agent': USER_AGENT}
    
    return opts

def add_metadata(file_path, title, artist, album=None, thumbnail_url=None):
    """Add metadata to MP3 file"""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Add ID3 tag if it doesn't exist
        try:
            audio.add_tags()
        except:
            pass
        
        # Add basic metadata
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        if album:
            audio.tags.add(TALB(encoding=3, text=album))
        
        # Add thumbnail if available
        if thumbnail_url:
            try:
                response = requests.get(thumbnail_url, timeout=10)
                if response.status_code == 200:
                    audio.tags.add(APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=response.content
                    ))
            except:
                pass  # Skip thumbnail if download fails
        
        audio.save()
    except Exception as e:
        print(f"Error adding metadata: {e}")

def download_audio(url, download_id):
    """Download audio from URL"""
    temp_dir = tempfile.mkdtemp() if TEMP_DIR is None else TEMP_DIR
    
    try:
        logger.info(f"Starting download for {download_id}: {url}")
        platform = detect_platform(url)
        
        # Check if platform is enabled
        platform_enabled = {
            'spotify': ENABLE_SPOTIFY,
            'apple_music': ENABLE_APPLE_MUSIC,
            'jiosaavn': ENABLE_JIOSAAVN,
            'youtube': ENABLE_YOUTUBE,
            'soundcloud': ENABLE_SOUNDCLOUD
        }
        
        if not platform_enabled.get(platform, True):
            raise Exception(f"{platform.title()} downloads are disabled")
        
        progress_hook = DownloadProgressHook(download_id)
        ydl_opts = get_ydl_opts(temp_dir, progress_hook)
        
        # Platform-specific configurations
        if platform == 'spotify':
            # For Spotify, we'll search on YouTube Music
            ydl_opts['default_search'] = 'ytsearch:'
            logger.info(f"Spotify URL detected, will search YouTube for: {url}")
        elif platform == 'apple_music':
            # For Apple Music, we'll search on YouTube Music
            ydl_opts['default_search'] = 'ytsearch:'
            logger.info(f"Apple Music URL detected, will search YouTube for: {url}")
        elif platform == 'soundcloud':
            # SoundCloud specific options
            ydl_opts['extractor_args'] = {'soundcloud': {'client_id': 'auto'}}
        
        download_progress[download_id] = {
            'status': 'starting',
            'percent': 0
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            logger.info(f"Extracting info for {download_id}")
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info:  # Playlist
                # For now, download first entry
                info = info['entries'][0]
                logger.info(f"Playlist detected, downloading first track: {info.get('title', 'Unknown')}")
            
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', info.get('artist', 'Unknown Artist'))
            album = info.get('album')
            thumbnail = info.get('thumbnail')
            
            # Check file size if limit is set
            if MAX_FILE_SIZE > 0 and 'filesize' in info:
                file_size_mb = info['filesize'] / (1024 * 1024)
                if file_size_mb > MAX_FILE_SIZE:
                    raise Exception(f"File size ({file_size_mb:.1f}MB) exceeds limit ({MAX_FILE_SIZE}MB)")
            
            logger.info(f"Downloading: {title} by {artist}")
            
            # Download the audio
            ydl.download([url])
            
            # Find the downloaded file
            downloaded_files = [f for f in os.listdir(temp_dir) if f.endswith(f'.{AUDIO_FORMAT}')]
            
            if downloaded_files:
                file_path = os.path.join(temp_dir, downloaded_files[0])
                
                # Add metadata
                logger.info(f"Adding metadata to {download_id}")
                add_metadata(file_path, title, artist, album, thumbnail_url=thumbnail)
                
                # Move to a permanent location
                final_filename = f"{title} - {artist}.{AUDIO_FORMAT}"
                # Clean filename
                final_filename = re.sub(r'[<>:"/\\|?*]', '', final_filename)
                final_path = os.path.join(tempfile.gettempdir(), f"{download_id}_{final_filename}")
                
                shutil.move(file_path, final_path)
                
                download_progress[download_id] = {
                    'status': 'completed',
                    'percent': 100,
                    'file_path': final_path,
                    'filename': final_filename
                }
                
                logger.info(f"Download completed for {download_id}: {final_filename}")
            else:
                raise Exception(f"No {AUDIO_FORMAT} file was downloaded")
                
    except Exception as e:
        logger.error(f"Download failed for {download_id}: {str(e)}")
        download_progress[download_id] = {
            'status': 'error',
            'percent': 0,
            'error': str(e)
        }
    finally:
        # Clean up temp directory
        if TEMP_DIR is None:  # Only clean up if using system temp
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def start_download():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    platform = detect_platform(url)
    if platform == 'unknown':
        return jsonify({'error': 'Unsupported platform. Please use Spotify, Apple Music, JioSaavn, YouTube Music, or SoundCloud URLs.'}), 400
    
    download_id = str(uuid.uuid4())
    
    # Start download in background thread
    thread = threading.Thread(target=download_audio, args=(url, download_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'download_id': download_id,
        'platform': platform,
        'message': 'Download started'
    })

@app.route('/progress/<download_id>')
def get_progress(download_id):
    progress = download_progress.get(download_id, {'status': 'not_found', 'percent': 0})
    return jsonify(progress)

@app.route('/download_file/<download_id>')
def download_file(download_id):
    progress = download_progress.get(download_id)
    
    if not progress or progress['status'] != 'completed':
        return jsonify({'error': 'File not ready'}), 404
    
    file_path = progress['file_path']
    filename = progress['filename']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    def remove_file():
        time.sleep(CLEANUP_DELAY)  # Wait before removing
        try:
            os.remove(file_path)
            if download_id in download_progress:
                del download_progress[download_id]
            logger.info(f"Cleaned up file for {download_id}")
        except Exception as e:
            logger.warning(f"Failed to clean up file for {download_id}: {e}")
    
    # Schedule file removal
    cleanup_thread = threading.Thread(target=remove_file)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    logger.info(f"Starting MP3 Downloader on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Audio format: {AUDIO_FORMAT} at {AUDIO_QUALITY}kbps")
    
    try:
        app.run(debug=DEBUG_MODE, host=SERVER_HOST, port=SERVER_PORT)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")