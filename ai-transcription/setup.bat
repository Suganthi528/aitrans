@echo off
echo Setting up AI Transcription Service...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating .env file...
copy .env.example .env

echo.
echo Setup complete!
echo.
echo To start the transcription service, run:
echo python transcription_service.py
echo.
pause
