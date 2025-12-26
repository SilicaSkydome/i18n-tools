@echo off
REM Create Desktop Shortcut for i18n Manager (Windows)

echo ========================================
echo   Creating Desktop Shortcut
echo ========================================
echo.

REM Get the current directory
set CURRENT_DIR=%~dp0

REM Create VBS script to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\i18n Manager.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CURRENT_DIR%launch-i18n-manager.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "i18n Manager - Universal Translation Tool" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,13" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript CreateShortcut.vbs //Nologo

REM Clean up
del CreateShortcut.vbs

echo.
echo ✅ Desktop shortcut created successfully!
echo.
echo You can now launch i18n Manager from your desktop.
echo.
pause
