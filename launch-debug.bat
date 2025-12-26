@echo off
REM Debug launcher - shows errors in a window
REM Use this if the normal launcher isn't working

cd /d "%~dp0"

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Checking dependencies...
python -c "import customtkinter; print('✓ CustomTkinter installed')"
if errorlevel 1 (
    echo Installing CustomTkinter...
    python -m pip install customtkinter pillow
)

python -c "import deep_translator; print('✓ Deep Translator installed')"
if errorlevel 1 (
    echo Installing Deep Translator...
    python -m pip install deep-translator
)

echo.
echo Starting i18n Manager...
echo.

REM Run with visible console to see errors
python i18n_manager.py

if errorlevel 1 (
    echo.
    echo =======================================
    echo   ERROR: App failed to start!
    echo =======================================
    echo.
    echo Check the error message above.
)

pause
