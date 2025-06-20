@echo off
echo ========================================
echo    MP3 Downloader Setup Script
echo ========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)
echo Python found!

echo.
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: FFmpeg not found in PATH
    echo.
    echo Please install FFmpeg:
    echo 1. Download from: https://ffmpeg.org/download.html
    echo 2. Extract and add to system PATH
    echo 3. Or install via chocolatey: choco install ffmpeg
    echo.
    echo The application may not work properly without FFmpeg!
    pause
) else (
    echo FFmpeg found!
)

echo.
echo [4/4] Setup complete!
echo.
echo To start the MP3 Downloader:
echo 1. Run: python main.py
echo 2. Open browser to: http://localhost:5000
echo.
echo Press any key to start the application now...
pause >nul

echo Starting MP3 Downloader...
python main.py