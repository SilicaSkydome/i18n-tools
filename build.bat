@echo off
REM Build standalone i18n-tools.exe
REM This creates a single executable with all dependencies bundled

echo ========================================
echo Building i18n-tools Standalone .exe
echo ========================================
echo.

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist i18n-tools.spec del i18n-tools.spec
echo.

echo Installing dependencies...
python -m pip install -q -r requirements.txt
echo.

echo Building with PyInstaller...
python -m PyInstaller --noconfirm --onefile --windowed ^
    --icon "icon.ico" ^
    --name "i18n-tools" ^
    --add-data "img;img" ^
    --add-data "icon.ico;." ^
    --hidden-import "flet" ^
    --hidden-import "flet.core" ^
    --hidden-import "flet.controls" ^
    --hidden-import "deep_translator" ^
    --hidden-import "deep_translator.google" ^
    --hidden-import "deep_translator.exceptions" ^
    i18n_manager_modern.py

echo.
if exist dist\i18n-tools.exe (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\i18n-tools.exe
    echo File size:
    dir dist\i18n-tools.exe | findstr "i18n-tools.exe"
    echo.
    echo You can now distribute dist\i18n-tools.exe
    echo Users need NO Python, NO dependencies - just run it!
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the output above for errors.
)

pause
