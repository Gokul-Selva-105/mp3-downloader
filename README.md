# 🎵 MP3 Downloader - High Quality Music Downloads

A fast, elegant, and lightweight web application for downloading high-quality MP3 files from popular music platforms including Spotify, Apple Music, JioSaavn, YouTube Music, and SoundCloud.

## ✨ Features

- **Multi-Platform Support**: Download from Spotify, Apple Music, JioSaavn, YouTube Music, and SoundCloud
- **High Quality Audio**: 320kbps MP3 downloads with embedded metadata
- **Beautiful UI**: Modern, responsive design with real-time progress tracking
- **No Database Required**: Completely stateless and lightweight
- **No Registration**: Start downloading immediately
- **Metadata Embedding**: Automatic title, artist, album, and thumbnail embedding
- **Progress Tracking**: Real-time download progress with speed and ETA
- **Auto Cleanup**: Temporary files are automatically cleaned up

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- FFmpeg (for audio conversion)

### Installation

1. **Clone or download this repository**
   ```bash
   cd mp3downloader
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   
   **Windows:**
   - Download FFmpeg from https://ffmpeg.org/download.html
   - Extract and add to your system PATH
   - Or use chocolatey: `choco install ffmpeg`
   
   **macOS:**
   ```bash
   brew install ffmpeg
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

1. **Copy a music URL** from any supported platform:
   - Spotify: `https://open.spotify.com/track/...`
   - Apple Music: `https://music.apple.com/...`
   - JioSaavn: `https://jiosaavn.com/...`
   - YouTube Music: `https://music.youtube.com/...`
   - SoundCloud: `https://soundcloud.com/...`

2. **Paste the URL** into the input field on the web interface

3. **Click "Download MP3"** and wait for the process to complete

4. **Download your file** when the "Download Your MP3" button appears

## 🛠️ Technical Details

### Backend Architecture
- **Framework**: Flask (Python)
- **Audio Processing**: yt-dlp + FFmpeg
- **Metadata**: Mutagen library
- **Threading**: Background downloads with progress tracking

### Frontend Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Progress tracking via AJAX polling
- **Modern UI**: Tailwind CSS with custom animations
- **Platform Detection**: Automatic URL platform recognition

### Supported Platforms

| Platform | Status | Notes |
|----------|-----------|-------|
| YouTube Music | ✅ Full Support | Direct yt-dlp integration |
| SoundCloud | ✅ Full Support | Direct yt-dlp integration |
| Spotify | ⚠️ Search-based | Searches YouTube for matching tracks |
| Apple Music | ⚠️ Search-based | Searches YouTube for matching tracks |
| JioSaavn | ⚠️ Limited | Depends on yt-dlp extractor support |

## 📁 Project Structure

```
mp3downloader/
├── main.py                 # Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── templates/
    └── index.html         # Web interface
```

## ⚙️ Configuration

### Environment Variables

You can customize the application behavior using environment variables:

```bash
# Change the port (default: 5000)
export FLASK_PORT=8080

# Enable debug mode
export FLASK_DEBUG=1

# Change host (default: 0.0.0.0)
export FLASK_HOST=127.0.0.1
```

### Audio Quality Settings

The application is configured to download the highest quality audio available:
- **Preferred Quality**: 320kbps MP3
- **Fallback**: Best available quality
- **Format**: MP3 with embedded metadata

## 🔧 Troubleshooting

### Common Issues

1. **"FFmpeg not found" error**
   - Install FFmpeg and ensure it's in your system PATH
   - Test with: `ffmpeg -version`

2. **Download fails for Spotify/Apple Music**
   - These platforms require searching YouTube for matching tracks
   - Ensure the track is available on YouTube

3. **Slow downloads**
   - Check your internet connection
   - Some platforms may have rate limiting

4. **Permission errors**
   - Ensure the application has write permissions to the temp directory
   - Run with appropriate user permissions

### Debug Mode

To enable debug mode for troubleshooting:

```bash
export FLASK_DEBUG=1
python main.py
```

## 📝 Legal Notice

**Important**: This tool is for educational and personal use only. Please respect copyright laws and the terms of service of the platforms you're downloading from. Users are responsible for ensuring they have the right to download and use the content.

### Recommendations:
- Only download content you own or have permission to download
- Respect artists and creators by supporting them through official channels
- Use this tool responsibly and in accordance with local laws

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- Report bugs and issues
- Suggest new features
- Improve documentation
- Add support for new platforms
- Optimize performance

## 📄 License

This project is provided as-is for educational purposes. Please use responsibly and in accordance with applicable laws and platform terms of service.

## 🔮 Future Enhancements

- [ ] Playlist download support
- [ ] Batch URL processing
- [ ] Download history (optional)
- [ ] Custom audio quality selection
- [ ] Dark/Light theme toggle
- [ ] Mobile app version
- [ ] Docker containerization

---

**Made with ❤️ for music lovers**

Enjoy your high-quality music downloads! 🎶