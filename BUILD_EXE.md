# 📦 Creating Standalone .EXE

To create a standalone `.exe` file that launches without a console window:

## Option 1: Using PyInstaller (Recommended)

### Install PyInstaller
```bash
pip install pyinstaller
```

### Create .EXE
```bash
cd i18n-tools
pyinstaller --name="i18n Manager" --onefile --windowed --icon=icon.ico i18n_manager.py
```

**Flags explained:**
- `--onefile` - Single .exe file
- `--windowed` - No console window (same as --noconsole)
- `--icon=icon.ico` - Custom icon (optional, create one first)
- `--name="i18n Manager"` - Name of the executable

### Output
The `.exe` will be in `dist/i18n Manager.exe`

You can distribute just this one file!

## Option 2: Using Auto-py-to-exe (GUI for PyInstaller)

### Install
```bash
pip install auto-py-to-exe
```

### Run GUI
```bash
auto-py-to-exe
```

Then:
1. Select `i18n_manager.py` as script
2. Choose "One File"
3. Choose "Window Based" (no console)
4. Click "CONVERT .PY TO .EXE"

## Option 3: Using cx_Freeze

### Install
```bash
pip install cx_Freeze
```

### Create setup.py
```python
from cx_Freeze import setup, Executable

setup(
    name="i18n Manager",
    version="3.0",
    description="i18n Translation Manager",
    executables=[Executable("i18n_manager.py", base="Win32GUI")]
)
```

### Build
```bash
python setup.py build
```

## For Current Quick Launch (No Console)

The launchers are already configured to use `pythonw.exe` which runs Python scripts without showing a console window.

**Windows:**
- Double-click `launch-i18n-manager.bat` - NO console appears!

**Linux/Mac:**
- Run `./launch-i18n-manager.sh` - Runs in background

## Creating Desktop Shortcut

**Windows:**
1. Right-click `launch-i18n-manager.bat`
2. "Send to" → "Desktop (create shortcut)"
3. Right-click shortcut → Properties
4. "Run:" → "Minimized" (hides batch file window)
5. Click "Change Icon" to add custom icon

**Or use the included script:**
```bash
create-desktop-shortcut.bat
```

## Distribution

### If distributing source code:
- Share entire `i18n-tools` folder
- Users run `launch-i18n-manager.bat` (Windows) or `.sh` (Mac/Linux)
- No console appears!

### If distributing .EXE:
- Build with PyInstaller
- Share just the `.exe` file from `dist/` folder
- Include `README.md` for documentation

## Troubleshooting

### "Missing module" errors with .EXE
Add hidden imports to PyInstaller:
```bash
pyinstaller --hidden-import=deep_translator --hidden-import=customtkinter --onefile --windowed i18n_manager.py
```

### .EXE is too large
Normal! Includes Python + all libraries. Typical size: 50-100 MB

### Antivirus flags .EXE
Common with PyInstaller. Add exception or distribute source code instead.

---

**Recommendation:** For now, just use the batch/shell launchers - they already hide the console! Build .EXE only if you need single-file distribution.
