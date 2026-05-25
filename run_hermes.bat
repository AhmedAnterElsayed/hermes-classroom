@echo off
title Hermes AI Auto Runner

echo Starting Hermes System...

cd /d C:\Users\Mega Store\hermes

:: Kill old python servers (cleanup)
taskkill /F /IM python.exe >nul 2>&1

echo Starting Flask Backend...

start cmd /k python app.py

timeout /t 3 >nul

echo Starting Frontend Server...

start cmd /k python -m http.server 5500

timeout /t 2 >nul

echo Opening Browser...

start http://127.0.0.1:5500/index.html

echo Hermes is running successfully.
pause