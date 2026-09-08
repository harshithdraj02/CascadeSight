@echo off
title CascadeSight Infrastructure Cascade Simulator
echo ========================================================
echo   ⚡ CascadeSight — Web Dashboard & Cascade Simulator
echo ========================================================
echo.
echo [*] Checking Python dependencies...
python -c "import flask, networkx" 2>nul
if %errorlevel% neq 0 (
    echo [!] Installing required Python packages (flask, networkx)...
    python -m pip install -r requirements.txt
) else (
    echo [✓] Dependencies verified.
)

echo.
echo [*] Launching CascadeSight Web Application Server...
echo ========================================================
python app.py
pause

