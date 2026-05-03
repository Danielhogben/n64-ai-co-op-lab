@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 🚀 Launching Project Nexus: Space Universe...
python nexus_3d.py
if errorlevel 1 (
    echo.
    echo ERROR: Make sure Python and dependencies are installed.
    echo Run: pip install -r requirements.txt
    pause
)
