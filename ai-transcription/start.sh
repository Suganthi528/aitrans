#!/bin/bash

echo "========================================"
echo "AI Transcription Service Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Checking Python installation..."
python3 --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
else
    echo ""
    echo "[2/4] Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo ""
echo "[4/4] Installing dependencies..."
echo "This may take a few minutes on first run..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found, copying from .env.example"
    cp .env.example .env
fi

# Start the server
echo ""
echo "========================================"
echo "Starting AI Transcription Server..."
echo "========================================"
echo ""
echo "Server will be available at: http://localhost:5002"
echo "Press Ctrl+C to stop the server"
echo ""

python3 transcription_server.py
