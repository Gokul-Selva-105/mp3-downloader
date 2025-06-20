#!/usr/bin/env python3

import os
import sys
import tempfile
import threading
import time
import uuid
import shutil
import zipfile
import logging
from pathlib import Path
import re
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, render_template, request, jsonify, send_file
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for download progress
download_progress = {}
playlist_progress = {}

# Configuration
CONFIG = {
    'AUDIO_FORMAT': 'mp3',
    'AUDIO_QUALITY': '320',
    'MAX_CONCURRENT_DOWNLOADS': 3,
    'TEMP_DIR': tempfile.gettempdir(),
    'DOWNLOAD_DIR': os.path.join(os.getcwd(), 'downloads'),
    'CLEANUP_DELAY': 300  # 5 minutes
}

# Ensure download directory exists
os.makedirs(CONFIG['DOWNLOAD_DIR'], exist_ok=True)

# Platform support configuration
PLATFORM_SUPPORT = {
    'youtube.com': {
        'supported': True,
        'name': 'YouTube',
        'notes': 'Fully supported'
    },
    'youtu.be': {
        'supported': True,
        'name': 'YouTube',
        'notes': 'Fully supported'
    },
    'music.youtube.com': {
        'supported': True,
        'name': 'YouTube Music',
        'notes': 'May require sign-in for some content'
    },
    'soundcloud.com': {
        'supported': True,
        'name': 'SoundCloud',
        'notes': 'Fully supported for public tracks'
    },
    'bandcamp.com': {
        'supported': True,
        'name': 'Bandcamp',
        'notes': 'Supported for free tracks'
    },
    'vimeo.com': {
        'supported': True,
        'name': 'Vimeo',
        'notes': 'Supported for public videos'
    },
    'dailymotion.com': {
        'supported': True,
        'name': 'Dailymotion',
        'notes': 'Supported for public videos'
    },
    'music.apple.com': {
        'supported': False,
        'name': 'Apple Music',
        'notes': 'Not supported due to DRM protection',
        'alternative': 'Try finding the same song on YouTube or SoundCloud'
    },
    'open.spotify.com': {
        'supported': False,
        'name': 'Spotify',
        'notes': 'Not supported due to DRM protection',
        'alternative': 'Try finding the same song on YouTube or SoundCloud'
    },
    'music.amazon.com': {
        'supported': False,
        'name': 'Amazon Music',
        'notes': 'Not supported due to DRM protection',
        'alternative': 'Try finding the same song on YouTube or SoundCloud'
    },
    'tidal.com': {
        'supported': False,
        'name': 'Tidal',
        'notes': 'Not supported due to DRM protection',
        'alternative': 'Try finding the same song on YouTube or SoundCloud'
    },
    'deezer.com': {
        'supported': False,
        'name': 'Deezer',
        'notes': 'Not supported due to DRM protection',
        'alternative': 'Try finding the same song on YouTube or SoundCloud'
    }
}

def detect_platform(url):
    """Detect the platform from URL and return support information"""
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc.replace('www.', '')
        
        # Check exact domain match
        if domain in PLATFORM_SUPPORT:
            return PLATFORM_SUPPORT[domain]
        
        # Check subdomain matches
        for platform_domain, info in PLATFORM_SUPPORT.items():
            if domain.endswith(platform_domain):
                return info
        
        # Unknown platform - assume it might work
        return {
            'supported': True,
            'name': 'Unknown Platform',
            'notes': 'Platform not recognized, attempting download'
        }
    except Exception:
        return {
            'supported': False,
            'name': 'Invalid URL',
            'notes': 'URL format is invalid'
        }

def validate_url(url):
    """Validate URL and check platform support"""
    if not url or not isinstance(url, str):
        return False, "Invalid URL format"
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Invalid URL format"
    
    platform_info = detect_platform(url)
    
    if not platform_info['supported']:
        error_msg = f"{platform_info['name']} is not supported. {platform_info['notes']}"
        if 'alternative' in platform_info:
            error_msg += f" {platform_info['alternative']}"
        return False, error_msg
    
    return True, platform_info['notes']

class DownloadProgressHook:
    def __init__(self, download_id, playlist_id=None, track_index=None):
        self.download_id = download_id
        self.playlist_id = playlist_id
        self.track_index = track_index
        
    def __call__(self, d):
        try:
            if d['status'] == 'downloading':
                if 'total_bytes' in d and d['total_bytes']:
                    percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                    percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    percent = 0
                
                speed = d.get('speed', 0) or 0
                eta = d.get('eta', 0) or 0
                
                progress_data = {
                    'status': 'downloading',
                    'percentage': min(percent, 100),
                    'speed': speed,
                    'eta': eta,
                    'downloaded_bytes': d.get('downloaded_bytes', 0),
                    'total_bytes': d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                }
                
                download_progress[self.download_id] = progress_data
                
                # Update playlist progress if this is part of a playlist
                if self.playlist_id and self.track_index is not None:
                    if self.playlist_id not in playlist_progress:
                        playlist_progress[self.playlist_id] = {'tracks': {}}
                    
                    playlist_progress[self.playlist_id]['tracks'][self.track_index] = {
                        'status': 'downloading',
                        'percentage': percent,
                        'title': d.get('info_dict', {}).get('title', f'Track {self.track_index + 1}')
                    }
                    
            elif d['status'] == 'finished':
                download_progress[self.download_id] = {
                    'status': 'processing',
                    'percentage': 100,
                    'message': 'Converting to MP3...'
                }
                
                if self.playlist_id and self.track_index is not None:
                    if self.playlist_id not in playlist_progress:
                        playlist_progress[self.playlist_id] = {'tracks': {}}
                    
                    playlist_progress[self.playlist_id]['tracks'][self.track_index] = {
                        'status': 'completed',
                        'percentage': 100,
                        'title': d.get('info_dict', {}).get('title', f'Track {self.track_index + 1}')
                    }
                    
        except Exception as e:
            logger.error(f"Progress hook error: {e}")

def get_ydl_opts(output_path, progress_hook):
    """Get enhanced yt-dlp options for better platform support"""
    return {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best[height<=720]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': CONFIG['AUDIO_FORMAT'],
            'preferredquality': CONFIG['AUDIO_QUALITY'],
        }],
        'progress_hooks': [progress_hook],
        'extractaudio': True,
        'audioformat': CONFIG['AUDIO_FORMAT'],
        'embed_subs': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
        'no_warnings': False,
        'extract_flat': False,
        # Enhanced options for better compatibility
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
        'keepvideo': False,
        'noplaylist': True,  # Force single video download
        # User agent to avoid blocking
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        # Geo bypass options
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        # Cookie handling
        'cookiefile': None,
        # Timeout settings
        'socket_timeout': 30,
        # Prefer free formats
        'prefer_free_formats': True,
        # Age limit bypass
        'age_limit': None
    }

def is_playlist_url(url):
    """Check if URL is a playlist"""
    playlist_indicators = [
        'playlist', 'album', 'list=', 'sets/',
        '/playlist/', '/album/', '/artist/'
    ]
    return any(indicator in url.lower() for indicator in playlist_indicators)

def add_metadata(file_path, title=None, artist=None, album=None):
    """Add metadata to MP3 file"""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        if audio.tags is None:
            audio.add_tags()
            
        if title:
            audio.tags["TIT2"] = TIT2(encoding=3, text=title)
        if artist:
            audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
        if album:
            audio.tags["TALB"] = TALB(encoding=3, text=album)
            
        audio.save()
        logger.info(f"Added metadata to {file_path}")
    except Exception as e:
        logger.error(f"Failed to add metadata to {file_path}: {e}")

def download_single_track(url, download_id, playlist_id=None, track_index=None):
    """Download a single track"""
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='mp3dl_')
        
        # Initialize progress
        download_progress[download_id] = {
            'status': 'starting',
            'percentage': 0,
            'message': 'Initializing download...'
        }
        
        # Create progress hook
        progress_hook = DownloadProgressHook(download_id, playlist_id, track_index)
        
        # Get yt-dlp options
        ydl_opts = get_ydl_opts(temp_dir, progress_hook)
        
        # Download with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            download_progress[download_id]['status'] = 'extracting'
            download_progress[download_id]['message'] = 'Extracting track information...'
            
            # Extract info
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Failed to extract video information")
                
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', info.get('artist', 'Unknown Artist'))
            
            download_progress[download_id]['message'] = f'Downloading: {title}'
            
            # Download
            ydl.download([url])
            
        # Find the downloaded file
        downloaded_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
        
        if not downloaded_files:
            raise Exception("No MP3 file found after download")
            
        downloaded_file = downloaded_files[0]
        temp_file_path = os.path.join(temp_dir, downloaded_file)
        
        # Add metadata
        add_metadata(temp_file_path, title, artist)
        
        # Move to permanent location
        final_filename = f"{download_id}_{downloaded_file}"
        final_path = os.path.join(CONFIG['DOWNLOAD_DIR'], final_filename)
        shutil.move(temp_file_path, final_path)
        
        # Update progress
        download_progress[download_id] = {
            'status': 'completed',
            'percentage': 100,
            'file_path': final_path,
            'filename': final_filename,
            'title': title,
            'artist': artist,
            'message': 'Download completed!'
        }
        
        logger.info(f"Successfully downloaded: {title}")
        return final_path
        
    except Exception as e:
        error_msg = str(e)
        if "Please sign in" in error_msg:
            error_msg = "This video requires authentication. Please try a different URL or a public video."
        elif "Video unavailable" in error_msg:
            error_msg = "This video is not available. It may be private, deleted, or region-restricted."
        elif "Unsupported URL" in error_msg:
            error_msg = "This platform is not supported. Please use YouTube, SoundCloud, or other supported platforms."
        elif "Failed to extract video information" in error_msg:
            error_msg = "Unable to extract video information. The URL may be invalid or the platform may not be supported."
        
        logger.error(f"Download failed for {url}: {error_msg}")
        
        download_progress[download_id] = {
            'status': 'error',
            'percentage': 0,
            'error': error_msg,
            'message': f'Download failed: {error_msg}'
        }
        
        if playlist_id and track_index is not None:
            if playlist_id not in playlist_progress:
                playlist_progress[playlist_id] = {'tracks': {}}
            playlist_progress[playlist_id]['tracks'][track_index] = {
                'status': 'error',
                'percentage': 0,
                'title': f'Track {track_index + 1}',
                'error': error_msg
            }
        
        return None
        
    finally:
        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")

def download_playlist(url, playlist_id):
    """Download a playlist"""
    temp_dir = None
    try:
        # Initialize playlist progress
        playlist_progress[playlist_id] = {
            'status': 'starting',
            'overall_percentage': 0,
            'completed_tracks': 0,
            'total_tracks': 0,
            'tracks': {},
            'message': 'Extracting playlist information...'
        }
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='mp3dl_playlist_')
        
        # Extract playlist info
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            
        if 'entries' not in playlist_info:
            raise Exception("No tracks found in playlist")
            
        entries = list(playlist_info['entries'])
        total_tracks = len(entries)
        
        playlist_progress[playlist_id].update({
            'total_tracks': total_tracks,
            'playlist_title': playlist_info.get('title', 'Unknown Playlist'),
            'message': f'Found {total_tracks} tracks. Starting downloads...'
        })
        
        downloaded_files = []
        
        # Download each track
        for i, entry in enumerate(entries):
            if entry is None:
                continue
                
            track_url = entry.get('url') or entry.get('webpage_url')
            if not track_url:
                track_url = f"https://www.youtube.com/watch?v={entry['id']}"
                
            track_download_id = f"{playlist_id}_track_{i}"
            
            playlist_progress[playlist_id]['message'] = f'Downloading track {i+1}/{total_tracks}'
            
            # Download track
            file_path = download_single_track(track_url, track_download_id, playlist_id, i)
            
            if file_path and os.path.exists(file_path):
                downloaded_files.append(file_path)
                playlist_progress[playlist_id]['completed_tracks'] += 1
            
            # Update overall progress
            overall_percentage = (playlist_progress[playlist_id]['completed_tracks'] / total_tracks) * 100
            playlist_progress[playlist_id]['overall_percentage'] = overall_percentage
        
        if not downloaded_files:
            raise Exception("No tracks were successfully downloaded")
            
        # Create ZIP file
        playlist_progress[playlist_id]['message'] = 'Creating ZIP file...'
        zip_filename = f"playlist_{playlist_id}.zip"
        zip_path = os.path.join(CONFIG['DOWNLOAD_DIR'], zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in downloaded_files:
                if os.path.exists(file_path):
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
        
        # Update final progress
        playlist_progress[playlist_id].update({
            'status': 'completed',
            'overall_percentage': 100,
            'zip_path': zip_path,
            'zip_filename': zip_filename,
            'message': f'Playlist download completed! {len(downloaded_files)} tracks downloaded.'
        })
        
        logger.info(f"Playlist download completed: {len(downloaded_files)} tracks")
        
        # Schedule cleanup of individual files
        def cleanup_files():
            time.sleep(CONFIG['CLEANUP_DELAY'])
            for file_path in downloaded_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to cleanup file {file_path}: {e}")
        
        threading.Thread(target=cleanup_files, daemon=True).start()
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Playlist download failed: {error_msg}")
        
        playlist_progress[playlist_id] = {
            'status': 'error',
            'overall_percentage': 0,
            'error': error_msg,
            'message': f'Playlist download failed: {error_msg}'
        }
        
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL and check platform support
        is_valid, validation_message = validate_url(url)
        if not is_valid:
            return jsonify({'error': validation_message}), 400
        
        platform_info = detect_platform(url)
        logger.info(f"Attempting download from {platform_info['name']}: {url}")
            
        # Check if it's a playlist
        if is_playlist_url(url):
            return jsonify({
                'error': 'This appears to be a playlist URL. Please use the "Download Playlist" button instead.',
                'is_playlist': True
            }), 400
            
        # Generate download ID
        download_id = str(uuid.uuid4())
        
        # Start download in background thread
        thread = threading.Thread(
            target=download_single_track,
            args=(url, download_id),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'download_id': download_id,
            'message': f'Download started from {platform_info["name"]}',
            'platform': platform_info['name'],
            'platform_notes': platform_info['notes']
        })
        
    except Exception as e:
        logger.error(f"Download endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_playlist', methods=['POST'])
def download_playlist_route():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL and check platform support
        is_valid, validation_message = validate_url(url)
        if not is_valid:
            return jsonify({'error': validation_message}), 400
        
        platform_info = detect_platform(url)
        logger.info(f"Attempting playlist download from {platform_info['name']}: {url}")
            
        # Check if it's actually a playlist
        if not is_playlist_url(url):
            return jsonify({
                'error': 'This does not appear to be a playlist URL. Please use the "Download Single" button instead.',
                'is_playlist': False
            }), 400
            
        # Generate playlist ID
        playlist_id = str(uuid.uuid4())
        
        # Start playlist download in background thread
        thread = threading.Thread(
            target=download_playlist,
            args=(url, playlist_id),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'playlist_id': playlist_id,
            'message': 'Playlist download started',
            'platform': 'detected'
        })
        
    except Exception as e:
        logger.error(f"Playlist download endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<download_id>')
def get_progress(download_id):
    progress = download_progress.get(download_id, {
        'status': 'not_found',
        'percentage': 0,
        'message': 'Download not found'
    })
    return jsonify(progress)

@app.route('/playlist_progress/<playlist_id>')
def get_playlist_progress(playlist_id):
    progress = playlist_progress.get(playlist_id, {
        'status': 'not_found',
        'overall_percentage': 0,
        'message': 'Playlist not found'
    })
    return jsonify(progress)

@app.route('/download_file/<download_id>')
def download_file(download_id):
    try:
        progress = download_progress.get(download_id)
        
        if not progress or progress.get('status') != 'completed':
            return jsonify({'error': 'Download not completed or not found'}), 404
            
        file_path = progress.get('file_path')
        filename = progress.get('filename')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # Schedule file cleanup
        def cleanup_file():
            time.sleep(CONFIG['CLEANUP_DELAY'])
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup file: {e}")
                
        threading.Thread(target=cleanup_file, daemon=True).start()
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"File download error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_playlist/<playlist_id>')
def download_playlist_file(playlist_id):
    try:
        progress = playlist_progress.get(playlist_id)
        
        if not progress or progress.get('status') != 'completed':
            return jsonify({'error': 'Playlist download not completed or not found'}), 404
            
        zip_path = progress.get('zip_path')
        zip_filename = progress.get('zip_filename')
        
        if not zip_path or not os.path.exists(zip_path):
            return jsonify({'error': 'ZIP file not found'}), 404
            
        # Schedule ZIP cleanup
        def cleanup_zip():
            time.sleep(CONFIG['CLEANUP_DELAY'])
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    logger.info(f"Cleaned up ZIP file: {zip_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup ZIP file: {e}")
                
        threading.Thread(target=cleanup_zip, daemon=True).start()
        
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
        
    except Exception as e:
        logger.error(f"Playlist file download error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting MP3 Downloader...")
    logger.info(f"Download directory: {CONFIG['DOWNLOAD_DIR']}")
    logger.info(f"Audio format: {CONFIG['AUDIO_FORMAT']} at {CONFIG['AUDIO_QUALITY']}kbps")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)