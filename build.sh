#!/bin/bash
# Build standalone i18n-tools executable for Linux/macOS
# Creates a single executable with all dependencies bundled

echo "========================================"
echo "Building i18n-tools Standalone"
echo "========================================"
echo

echo "Cleaning previous builds..."
rm -rf build dist i18n-tools.spec
echo

echo "Installing dependencies..."
python3 -m pip install -q -r requirements.txt
echo

echo "Building with PyInstaller..."
python3 -m PyInstaller --noconfirm --onefile --windowed \
    --icon "icon.ico" \
    --name "i18n-tools" \
    --add-data "img:img" \
    --add-data "icon.ico:." \
    --hidden-import "flet" \
    --hidden-import "flet.core" \
    --hidden-import "flet.controls" \
    --hidden-import "deep_translator" \
    --hidden-import "deep_translator.google" \
    --hidden-import "deep_translator.exceptions" \
    i18n_manager_modern.py

echo
if [ -f "dist/i18n-tools" ]; then
    echo "========================================"
    echo "BUILD SUCCESSFUL!"
    echo "========================================"
    echo
    echo "Executable location: dist/i18n-tools"
    ls -lh dist/i18n-tools
    echo
    echo "You can now distribute dist/i18n-tools"
    echo "Users need NO Python, NO dependencies - just run it!"
else
    echo "========================================"
    echo "BUILD FAILED!"
    echo "========================================"
    echo "Check the output above for errors."
fi
