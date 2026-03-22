@echo off
echo ========================================
echo Pushing AI Transcription Code to GitHub
echo ========================================
echo.

REM Wait for any git processes to finish
timeout /t 2 /nobreak >nul

REM Remove lock file if exists
if exist .git\index.lock (
    echo Removing git lock file...
    del /F .git\index.lock 2>nul
    timeout /t 1 /nobreak >nul
)

REM Add remote if not exists
git remote get-url aitrans >nul 2>&1
if errorlevel 1 (
    echo Adding aitrans remote...
    git remote add aitrans https://github.com/Suganthi528/aitrans.git
)

REM Stage all changes
echo.
echo Staging changes...
git add .

REM Commit changes
echo.
echo Committing changes...
git commit -m "Add AI-powered real-time transcription with language translation"

REM Push to aitrans repository
echo.
echo Pushing to aitrans repository...
git push aitrans main

echo.
echo ========================================
echo Done! Check: https://github.com/Suganthi528/aitrans
echo ========================================
pause
