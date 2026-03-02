@echo off
title Smart Cam Launcher - TURBO MODE
echo ===================================================
echo      TURBO LAUNCHING SHALINI PROJECT...
echo ===================================================

:: 1. Start Python App (Main Brain)
start "Core Brain" cmd /k "python app.py"

:: 2. Start Node Server (Internal AI)
cd server
start "Internal AI" cmd /k "npm start"
cd ..

:: 3. Start Generator Backend
cd image_generator_app\server
start "Gen Backend" cmd /k "npm start"
cd ..\..

:: 4. Start Generator Frontend
cd image_generator_app\client
start "Frontend" cmd /k "npm run dev"
cd ..\..

:: 5. Launch Browser Instantly (Wait 2s for boot)
timeout /t 2 >nul
start http://127.0.0.1:5000

exit
