# 🚀 i18n Manager - Standalone Executable

## ✅ Your App is Now a Standalone .EXE!

**Location:** `dist/i18n-Manager.exe`  
**Size:** ~20 MB  
**Requires:** Nothing! (Python and all libraries are included)

## 🎯 How to Use the .EXE

### Option 1: Run Directly
Just double-click `dist/i18n-Manager.exe` - that's it!

### Option 2: Copy Anywhere
Copy `i18n-Manager.exe` to anywhere on your computer (or USB drive):
- Your Desktop
- A project folder
- A network drive
- Send to a friend

It will work without installing Python or any dependencies!

### Option 3: Create Desktop Shortcut
1. Right-click `dist/i18n-Manager.exe`
2. "Send to" → "Desktop (create shortcut)"
3. Rename shortcut to "i18n Manager"

## 📦 Distribution

### To Share with Others:
1. Copy `dist/i18n-Manager.exe`
2. Send it via email, USB, cloud storage, etc.
3. Recipients just double-click to run
4. **No Python installation needed!**

### What's Included:
- ✅ Complete Python runtime
- ✅ CustomTkinter (modern UI library)
- ✅ Deep Translator (translation engine)
- ✅ All dependencies
- ✅ Your application code

## 🔄 Rebuilding the .EXE

If you modify `i18n_manager.py` and want to rebuild:

**Windows:**
```bash
build-exe.bat
```

**Manual:**
```bash
python -m PyInstaller --name="i18n-Manager" --onefile --windowed ^
    --hidden-import=customtkinter --hidden-import=deep_translator ^
    --collect-all customtkinter --noconfirm i18n_manager.py
```

The new .exe will be in `dist/i18n-Manager.exe`

## ⚠️ Common Issues

### "Windows protected your PC" warning
This is normal for unsigned executables. Click "More info" → "Run anyway"

To avoid this, you would need to:
- Code-sign the executable (requires purchasing a certificate ~$100/year)
- Or distribute the source code instead

### Antivirus flags it
Some antivirus software flag PyInstaller executables as suspicious:
- This is a false positive
- Add an exception in your antivirus
- Or use the source code version (`launch-i18n-manager.bat`)

### .EXE is large (20 MB)
This is normal! It includes:
- Python interpreter (~10 MB)
- CustomTkinter library (~5 MB)
- Other dependencies (~5 MB)

## 🆚 .EXE vs Source Code

| Feature | .EXE File | Source Code |
|---------|-----------|-------------|
| **Requires Python** | ❌ No | ✅ Yes (3.8+) |
| **File Size** | ~20 MB | < 1 MB |
| **Portability** | ✅ Single file | 📁 Folder |
| **Startup Time** | Slower (2-3 sec) | Faster |
| **Customization** | ❌ Rebuild needed | ✅ Edit .py file |
| **Distribution** | ✅ Easy | ⚠️ Needs Python |
| **Updates** | Rebuild required | Edit files |

## 🎯 Recommendation

**For yourself:** Use source code (`launch-i18n-manager.bat`)  
**For others:** Share the .exe file

## 📝 Files Created by Build Process

```
i18n-tools/
├── dist/
│   └── i18n-Manager.exe    ⭐ THE EXECUTABLE (distribute this!)
├── build/                   🗑️ Build cache (can delete)
│   └── i18n-Manager/
└── i18n-Manager.spec        📋 PyInstaller config (can delete)
```

**What to keep:**
- `dist/i18n-Manager.exe` - The final executable

**Can delete after building:**
- `build/` folder
- `i18n-Manager.spec` file

## 🎉 Success!

You now have a standalone application that:
- ✅ Launches without console window
- ✅ Works on any Windows PC
- ✅ Doesn't require Python installation
- ✅ Can be distributed as a single file
- ✅ Looks professional

**Double-click `dist/i18n-Manager.exe` to test it!**

---

Need help? Check `BUILD_EXE.md` for detailed build options.
