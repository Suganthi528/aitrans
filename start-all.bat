@echo off
echo ========================================
echo Starting HiiMeet Video Meeting Platform
echo ========================================
echo.

echo [1/3] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && npm start"

timeout /t 2 /nobreak > nul

echo [2/3] Starting AI Transcription Service...
start "AI Transcription" cmd /k "cd ai-transcription && python transcription_service.py"

timeout /t 3 /nobreak > nul

echo [3/3] Starting Frontend Server...
start "Frontend Server" cmd /k "cd video-meet\frontend-videocall && npm start"

echo.
echo ========================================
echo All services are starting!
echo ========================================
echo.
echo Backend:        http://localhost:5001
echo AI Service:     http://localhost:5002
echo Frontend:       http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul
