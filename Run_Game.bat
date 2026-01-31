@echo off
title 🎭 MASK IT IF YOU CAN - Launcher
echo Checking Python installation...


py --version >nul 2>&1
if %errorlevel% == 0 (
    set PY_CMD=py
) else (
    python --version >nul 2>&1
    if %errorlevel% == 0 (
        set PY_CMD=python
    ) else (
        echo [ERROR] Python is not installed or not in PATH.
        pause
        exit
    )
)

echo.
echo Installing dependencies (if missing)...
%PY_CMD% -m pip install opencv-python mediapipe numpy Pillow --quiet

echo.
echo Starting the game...
%PY_CMD% Maskitifyoucan.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The game crashed. See the error above.
)
pause