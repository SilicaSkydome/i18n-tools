#!/bin/bash
# i18n Manager Launcher for Linux/Mac
# Run this to launch i18n Manager (no terminal output)

cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+"
    exit 1
fi

# Run in background (detached from terminal)
nohup python3 i18n_manager.py > /dev/null 2>&1 &

# Exit immediately
exit 0
