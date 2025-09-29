@echo off
echo Starting Weapon Detection Surveillance System on Port 8080...
echo.
echo Opening browser to http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the surveillance server
python surveillance_server.py

pause
