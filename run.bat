@echo off
echo ========================================
echo      Starting MP3 Downloader
echo ========================================
echo.
echo Server will start at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

python main.py

echo.
echo Server stopped.
pause