@echo off
echo Starting QR Attendance System...
start /B python run.py
timeout /t 2 /nobreak
start "" "start_app.html"
echo Application started! Please wait for the browser to open... 