# 📋 i18n Manager - Quick Reference

**Version 3.0 - Standalone Edition**

## 🚀 Launch

```bash
# Windows
python i18n_manager.py
# or double-click: launch-i18n-manager.bat

# Linux/Mac
python3 i18n_manager.py
```

## 📖 Workflow Steps

### 1. Select Project
Click **📂 Browse** → Choose your React/TypeScript project

### 2. Choose Languages
Check boxes for languages you want (English always included)

### 3. Run Workflow
Click **🚀 Run Complete Workflow** (or run steps individually)

## 🎯 What Each Step Does

| Step | Button | What It Does | Output |
|------|--------|--------------|--------|
| 1 | 1️⃣ Detect Text | Finds hardcoded strings | List of detected text |
| 2 | 2️⃣ Generate Keys | Creates translation keys | Keys grouped by section |
| 3 | 3️⃣ Translate | Auto-translates text | Updated language files |
| 4 | 4️⃣ Replace Code | Updates source files | Modified .tsx files |

## 📁 Files Created

### If Project Has NO i18n:
```
src/i18n/
├── config.ts          # Configuration
├── index.ts           # Exports
└── locales/
    ├── en.json        # English
    ├── es.json        # Spanish
    └── ...
```

### Backups Location:
```
i18n-tools/.backups/TIMESTAMP/
```

## 🌍 Supported Languages (22+)

🇬🇧 English | 🇪🇸 Spanish | 🇫🇷 French | 🇩🇪 German | 🇮🇹 Italian  
🇵🇹 Portuguese | 🇳🇱 Dutch | 🇷🇺 Russian | 🇵🇱 Polish | 🇨🇿 Czech  
🇬🇷 Greek | 🇷🇴 Romanian | 🇨🇳 Chinese | 🇯🇵 Japanese | 🇰🇷 Korean  
🇦🇪 Arabic | 🇮🇳 Hindi | 🇹🇷 Turkish | 🇻🇳 Vietnamese | 🇹🇭 Thai  
🇸🇪 Swedish | 🇩🇰 Danish | 🇳🇴 Norwegian | 🇫🇮 Finnish

## 🔧 Integration Steps

After setup wizard creates files:

1. **Install dependencies:**
   ```bash
   npm install react-i18next i18next
   ```

2. **Import in App.tsx:**
   ```tsx
   import './i18n';
   ```

3. **Use in components:**
   ```tsx
   import { useTranslation } from 'react-i18next';
   
   function MyComponent() {
     const { t } = useTranslation();
     return <h1>{t("section.key")}</h1>;
   }
   ```

## 💡 Tips & Tricks

### ✅ Do:
- Commit your project before running
- Review changes in output panel
- Check backups if something goes wrong
- Test with small project first

### ❌ Don't:
- Cancel during "Replace Code" step
- Delete `.backups/` folder immediately
- Run on uncommitted changes
- Skip reviewing the preview

## 🆘 Quick Fixes

### "No i18n configured"
→ Click "Yes" when wizard appears

### Translation fails
→ Check internet, try fewer languages

### Code breaks
→ Restore from `.backups/` folder

### GUI freezes
→ Wait - long operations take time (see progress bar)

## 📊 Status Indicators

| Icon | Meaning |
|------|---------|
| ✅ | Success |
| ⚠️ | Warning (still works) |
| ❌ | Error (check output) |
| 🔍 | Detecting |
| 🔑 | Generating keys |
| 🌍 | Translating |
| ✏️ | Replacing code |
| 📁 | File operations |

## 🎯 Common Use Cases

### Case 1: New Project (No i18n)
1. Select project → Setup wizard appears
2. Click "Yes" → Files created
3. Select languages → Run workflow
4. Install npm packages → Import in App.tsx

### Case 2: Existing i18n Project
1. Select project → Detects i18n
2. Select languages → Run workflow
3. Done! (already integrated)

### Case 3: Add New Language
1. Select project
2. Check new language box
3. Run "3️⃣ Translate" only
4. Done! New language file created

### Case 4: Update Translations
1. Select project
2. Run "1️⃣ Detect" → "2️⃣ Generate"
3. Run "3️⃣ Translate"
4. Skip replacement (already done)

## 🔐 Safety Features

✅ **Automatic backups** before any file changes  
✅ **Confirmation dialogs** for destructive operations  
✅ **Progress tracking** with visual feedback  
✅ **Error handling** with helpful messages  
✅ **Rollback capability** via backups  

## 📝 Translation File Format

```json
{
  "nav": {
    "home": "Home",
    "about": "About"
  },
  "button": {
    "save": "Save",
    "cancel": "Cancel"
  },
  "common": {
    "welcome": "Welcome"
  }
}
```

Keys use dot notation: `t("nav.home")`, `t("button.save")`

## ⚙️ Settings Saved

The tool remembers:
- Last project used
- Language selections
- Window position

Settings stored in: `i18n-tools/user_settings.json`

## 🚀 Performance

| Operation | Typical Time |
|-----------|--------------|
| Detect | 5-30 seconds |
| Generate Keys | < 5 seconds |
| Translate (per language) | 1-3 minutes |
| Replace Code | 10-30 seconds |
| **Complete Workflow** | **5-10 minutes** |

*Times vary based on project size and number of strings*

## 🎨 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+O | Open project (when button focused) |
| Ctrl+R | Run workflow (when button focused) |
| Esc | Close dialogs |

## 📞 Support

Check in this order:
1. **Output Panel** - Shows errors and suggestions
2. **TESTING_GUIDE.md** - Troubleshooting section
3. **Backups** - `.backups/` folder for file recovery

## 🎉 Success Checklist

After workflow completes:

- [ ] Output panel shows ✅ success messages
- [ ] Translation files exist: `src/i18n/locales/*.json`
- [ ] Source files updated (check one manually)
- [ ] Backups created: `i18n-tools/.backups/TIMESTAMP/`
- [ ] Project builds: `npm run build`
- [ ] App runs: `npm run dev`
- [ ] Translations work (switch language in app)

---

**🌟 Pro Tip:** Run on a git branch first, review all changes, then merge!

---

Made with ❤️ for developers who value their time
