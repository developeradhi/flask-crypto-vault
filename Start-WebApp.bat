@echo off
echo =================================================
echo   SECURE FILE ENCRYPTOR - WEB LAUNCHER
echo =================================================
echo.
echo Installing requirements (if not already installed)...
pip install -r requirements.txt >nul 2>&1

echo Starting the secure local server...
start /B python web.py >nul 2>&1

echo Waiting for server to boot up...
timeout /t 3 /nobreak >nul

echo Opening your default web browser...
start http://127.0.0.1:5000

echo.
echo [SUCCESS] The application is now running in your browser!
echo.
echo IMPORTANT: To completely stop the background server when you are done,
echo simply close this terminal window.
echo.
pause
