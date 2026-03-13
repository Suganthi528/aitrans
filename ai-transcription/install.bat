@echo off
echo ========================================
echo AI Transcription Service - Installation
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing required packages...
echo This may take a few minutes...
echo.

pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created successfully
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the transcription service:
echo   python transcription_service.py
echo.
echo The service will run on http://localhost:5002
echo.
pause
