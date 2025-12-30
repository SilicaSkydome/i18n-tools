# 🚀 Quick Start - Download & Run

## For End Users (No Technical Knowledge Required)

### Windows

1. **Download** `i18n-tools.exe` from the [Releases](https://github.com/SilicaSkydome/i18n-tools/releases) page
2. **Double-click** the `.exe` file
3. **Done!** The app will launch immediately

**That's it!** You don't need:
- ✗ Python installation
- ✗ Node.js or npm
- ✗ Any libraries or dependencies
- ✗ Internet connection (after download)

### macOS / Linux

1. Download the appropriate binary for your platform
2. Make it executable: `chmod +x i18n-tools`
3. Run it: `./i18n-tools`

---

## For Developers

### Running from Source
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run directly
python i18n_manager_modern.py
```

### Building the Standalone Executable

#### Windows
```bash
# Simple one-click build
build.bat
```

#### Linux/macOS
```bash
# Make build script executable
chmod +x build.sh

# Build
./build.sh
```

The executable will be created in the `dist/` folder.

---

## What Makes It Standalone?

✅ **All dependencies bundled**: flet, deep-translator, and all Python libraries are packed inside the .exe  
✅ **No runtime installation**: Removed auto-install code that would fail in packaged builds  
✅ **Self-contained assets**: Icons and images are embedded  
✅ **Native file dialogs**: Uses OS-native dialogs (tkinter) for maximum compatibility  

---

## Technical Details

- **Build tool**: PyInstaller (one-file mode)
- **Size**: ~84 MB (includes Python runtime + all libraries)
- **Platform**: Windows 10/11 (64-bit)
- **UI Framework**: Flet (Material Design 3)
- **Translation**: Google Translate API (no API key needed)

---

## Troubleshooting

### "Windows protected your PC" warning
This is normal for unsigned executables. Click **"More info"** → **"Run anyway"**

### App won't start
- Ensure you're running Windows 10 or later (64-bit)
- Check antivirus hasn't quarantined the file
- Try running as Administrator

### Missing .exe after build
- Check `dist/` folder
- Ensure PyInstaller completed without errors
- Review `build/i18n-tools/warn-i18n-tools.txt` for warnings

---

## Distribution

Share the `.exe` file from the `dist/` folder. Users can:
- Run it from anywhere (desktop, USB drive, network share)
- No installation needed
- No admin rights required
