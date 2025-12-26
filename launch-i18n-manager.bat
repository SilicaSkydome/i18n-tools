@echo off
REM i18n Manager Launcher for Windows
REM Checks dependencies and launches app without console

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check and install dependencies silently
python -c "import customtkinter, deep_translator" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install customtkinter deep_translator pillow --quiet
)

REM Launch app without console window
start "" pythonw i18n_manager.py
exit
