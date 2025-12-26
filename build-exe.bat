@echo off
REM Build standalone .exe file for i18n Manager
REM This creates a single executable file that includes everything

echo ========================================
echo   Building i18n Manager .EXE
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller --quiet
)

echo Installing dependencies...
python -m pip install customtkinter deep_translator pillow --quiet

echo.
echo Building executable...
echo This may take a few minutes...
echo.

REM Build the .exe (using python -m to avoid PATH issues)
python -m PyInstaller --name="i18n-Manager" ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --hidden-import=customtkinter ^
    --hidden-import=deep_translator ^
    --hidden-import=PIL ^
    --collect-all customtkinter ^
    --noconfirm ^
    i18n_manager.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETE!
echo ========================================
echo.
echo Your standalone .exe file is located at:
echo   dist\i18n-Manager.exe
echo.
echo You can:
echo   1. Run it directly from dist folder
echo   2. Copy it anywhere and it will work
echo   3. Create a desktop shortcut to it
echo   4. Share it with others (no Python needed!)
echo.
echo File size: ~50-80 MB (includes Python + all libraries)
echo.
pause
