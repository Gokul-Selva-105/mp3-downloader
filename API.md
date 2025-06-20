# MP3 Downloader API Documentation

## Overview

The MP3 Downloader provides a RESTful API for downloading audio from various platforms. This document describes all available endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Home Page

**GET** `/`

Returns the main web interface.

**Response:**
- Content-Type: `text/html`
- Status: `200 OK`

---

### 2. Download Audio

**POST** `/download`

Initiates an audio download from a supported platform.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "download_id": "abc123def456",
  "platform": "youtube",
  "status": "started"
}
```

**Status Codes:**
- `200 OK` - Download initiated successfully
- `400 Bad Request` - Invalid URL or unsupported platform
- `500 Internal Server Error` - Server error

**Supported Platforms:**
- YouTube (`youtube.com`, `youtu.be`)
- Spotify (`open.spotify.com`) - *searches on YouTube*
- SoundCloud (`soundcloud.com`)
- Apple Music (`music.apple.com`) - *searches on YouTube*
- JioSaavn (`jiosaavn.com`)
- Bandcamp (`bandcamp.com`)
- Vimeo (`vimeo.com`)

---

### 3. Check Download Progress

**GET** `/progress/<download_id>`

Returns the current status and progress of a download.

**Parameters:**
- `download_id` (string) - Unique identifier returned from `/download`

**Response:**
```json
{
  "status": "downloading",
  "progress": 45.2,
  "filename": "Rick Astley - Never Gonna Give You Up.mp3",
  "platform": "youtube"
}
```

**Status Values:**
- `not_found` - Download ID not found
- `starting` - Download is being initialized
- `downloading` - Download in progress
- `processing` - Post-processing (metadata, conversion)
- `completed` - Download finished successfully
- `error` - Download failed

**Progress Field:**
- Float value between 0.0 and 100.0
- Only present when status is `downloading`

---

### 4. Download File

**GET** `/download_file/<download_id>`

Downloads the completed audio file.

**Parameters:**
- `download_id` (string) - Unique identifier from completed download

**Response:**
- Content-Type: `audio/mpeg` (for MP3 files)
- Content-Disposition: `attachment; filename="song.mp3"`
- Status: `200 OK`

**Error Response:**
```json
{
  "error": "File not ready or not found"
}
```

**Status Codes:**
- `200 OK` - File download started
- `404 Not Found` - File not ready or doesn't exist

---

## Usage Examples

### Python Example

```python
import requests
import time

# Start download
response = requests.post('http://localhost:5000/download', 
                        json={'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
data = response.json()
download_id = data['download_id']

# Poll for progress
while True:
    progress_response = requests.get(f'http://localhost:5000/progress/{download_id}')
    progress_data = progress_response.json()
    
    if progress_data['status'] == 'completed':
        print(f"Download completed: {progress_data['filename']}")
        break
    elif progress_data['status'] == 'error':
        print(f"Download failed: {progress_data.get('error', 'Unknown error')}")
        break
    else:
        print(f"Progress: {progress_data.get('progress', 0):.1f}%")
        time.sleep(2)

# Download the file
file_response = requests.get(f'http://localhost:5000/download_file/{download_id}')
with open('downloaded_song.mp3', 'wb') as f:
    f.write(file_response.content)
```

### JavaScript Example

```javascript
async function downloadAudio(url) {
    // Start download
    const response = await fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    });
    
    const data = await response.json();
    const downloadId = data.download_id;
    
    // Poll for progress
    while (true) {
        const progressResponse = await fetch(`/progress/${downloadId}`);
        const progressData = await progressResponse.json();
        
        if (progressData.status === 'completed') {
            console.log(`Download completed: ${progressData.filename}`);
            // Trigger file download
            window.location.href = `/download_file/${downloadId}`;
            break;
        } else if (progressData.status === 'error') {
            console.error(`Download failed: ${progressData.error || 'Unknown error'}`);
            break;
        } else {
            console.log(`Progress: ${progressData.progress || 0}%`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
}

// Usage
downloadAudio('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
```

### cURL Examples

```bash
# Start download
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Check progress
curl http://localhost:5000/progress/abc123def456

# Download file
curl -O -J http://localhost:5000/download_file/abc123def456
```

## Error Handling

### Common Error Responses

```json
{
  "error": "URL is required"
}
```

```json
{
  "error": "Unsupported platform: example.com"
}
```

```json
{
  "error": "Platform youtube is currently disabled"
}
```

```json
{
  "error": "Download failed: Video unavailable"
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

The API implements basic rate limiting:
- Maximum 10 concurrent downloads per IP
- Maximum 100 requests per hour per IP

## Configuration

The API behavior can be customized through the `config.py` file:

- `MAX_CONCURRENT_DOWNLOADS` - Maximum simultaneous downloads
- `AUDIO_QUALITY` - Default audio quality (128k, 192k, 320k)
- `AUDIO_FORMAT` - Output format (mp3, m4a, wav)
- Platform enable/disable flags

## Security Considerations

1. **Input Validation**: All URLs are validated before processing
2. **File Size Limits**: Downloads are limited by `MAX_FILE_SIZE_MB`
3. **Temporary Files**: Automatic cleanup after `CLEANUP_DELAY` seconds
4. **Rate Limiting**: Prevents abuse and resource exhaustion
5. **CORS**: Configure `ALLOWED_HOSTS` for cross-origin requests

## Troubleshooting

### Common Issues

1. **"Unsupported platform" error**
   - Check if the platform is enabled in `config.py`
   - Verify the URL format is correct

2. **"Download failed" error**
   - Video might be private, deleted, or geo-restricted
   - Check server logs for detailed error messages

3. **Slow downloads**
   - Adjust `AUDIO_QUALITY` setting
   - Check network connectivity
   - Verify FFmpeg installation

4. **File not found after completion**
   - Check `CLEANUP_DELAY` setting
   - Verify disk space availability
   - Check file permissions

### Logging

Enable detailed logging by setting `LOG_LEVEL = 'DEBUG'` in `config.py`. Logs include:
- Download start/completion times
- Error details and stack traces
- Platform detection results
- File processing steps

## License

This API is provided under the MIT License. Please ensure compliance with platform terms of service and copyright laws when using this service.