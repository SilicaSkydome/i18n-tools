# ✅ Standalone Verification Checklist

This document verifies that `i18n-tools.exe` is truly standalone and ready for distribution.

## Pre-Distribution Checklist

### 1. Build Verification
- [x] PyInstaller build completed without errors
- [x] Executable created in `dist/` folder
- [x] File size reasonable (~84 MB)
- [x] All assets bundled (icon.ico, img/ folder)

### 2. Code Verification
- [x] Removed auto-install code (`subprocess.check_call`)
- [x] All imports are static (no dynamic installation)
- [x] Asset paths use `sys._MEIPASS` for PyInstaller compatibility
- [x] Native file dialogs (tkinter) for cross-environment compatibility

### 3. Dependency Verification
- [x] `requirements.txt` matches actual dependencies
- [x] No `customtkinter` reference (uses `flet`)
- [x] All hidden imports specified in build command:
  - `flet`, `flet.core`, `flet.controls`
  - `deep_translator`, `deep_translator.google`, `deep_translator.exceptions`

### 4. Runtime Testing
Test on a **clean machine** (no Python installed):
- [ ] .exe launches without errors
- [ ] UI displays correctly (Material Design 3)
- [ ] Can select project folder (native file dialog)
- [ ] Can detect strings in .tsx files
- [ ] Can generate translation keys
- [ ] Can translate to multiple languages (requires internet)
- [ ] Can replace strings in source code
- [ ] Backups are created before modifications

### 5. Platform Testing
- [ ] Windows 10 (64-bit)
- [ ] Windows 11 (64-bit)
- [ ] Antivirus scan passed (no false positives)

### 6. Distribution Readiness
- [x] Build script created (`build.bat`, `build.sh`)
- [x] Quick start guide created (`QUICKSTART.md`)
- [x] README updated with standalone instructions
- [x] Copilot instructions updated
- [ ] GitHub release created with .exe attached
- [ ] Release notes written

## Known Limitations

1. **Windows Defender Warning**: Unsigned .exe files trigger SmartScreen. Users need to click "More info" → "Run anyway"
2. **File Size**: ~84 MB due to bundled Python runtime and libraries (acceptable for standalone app)
3. **First Launch**: May take 2-3 seconds to unpack resources
4. **Translation**: Requires internet connection for Google Translate API

## Verification Commands

```bash
# Check .exe exists
dir dist\i18n-tools.exe

# Test launch (Windows)
.\dist\i18n-tools.exe

# Verify no Python dependency
# (Run on machine without Python - should still work)
```

## Post-Release Monitoring

Monitor for:
- User reports of missing dependencies
- Launch failures on clean systems
- Antivirus false positives
- Translation API issues

## Emergency Rollback

If critical issues found:
1. Remove release from GitHub
2. Fix issue in `i18n_manager_modern.py`
3. Rebuild: `build.bat`
4. Re-test on clean machine
5. Re-release with version bump
