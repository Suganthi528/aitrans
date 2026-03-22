@echo off
echo ========================================
echo AI Transcription Service Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo.
    echo [2/4] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo.
echo [4/4] Installing dependencies...
echo This may take a few minutes on first run...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found, copying from .env.example
    copy .env.example .env
)

REM Start the server
echo.
echo ========================================
echo Starting AI Transcription Server...
echo ========================================
echo.
echo Server will be available at: http://localhost:5002
echo Press Ctrl+C to stop the server
echo.

python transcription_server.py

pause
