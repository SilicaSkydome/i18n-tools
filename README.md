# 🌍 i18n Manager - Standalone Translation Tool

**Version 3.0 - Completely Refactored**

A modern, portable desktop application for managing internationalization (i18n) in React/TypeScript projects. 100% standalone - no CLI dependencies, fully portable, works on any computer.

## ✨ Key Features

### 🎨 Modern GUI
- Beautiful, modern interface with custom styling
- Real-time progress tracking with visual feedback
- Intuitive workflow with step-by-step guidance
- Responsive design with hover effects

### 🚀 Completely Standalone
- **No CLI scripts** - All functionality embedded in GUI
- **100% Portable** - Copy folder to any computer and it works
- **Self-contained** - All state stored in tool directory
- **Auto-install dependencies** - Installs what it needs automatically

### 🔧 i18n Setup from Scratch
- **Detects missing i18n setup** automatically
- **Setup wizard** creates all necessary files
- Generates proper directory structure
- Creates configuration files (config.ts, locales/, etc.)
- Provides integration instructions

### ⚡ Complete Workflow
1. **Detect** - Finds all hardcoded text in your code
2. **Generate** - Creates organized translation keys
3. **Translate** - Auto-translates to 22+ languages
4. **Replace** - Updates code with `t()` calls

### 🛡️ Safe & Reliable
- Automatic backups before any changes
- Project structure detection
- Smart text detection (user-facing only)
- Error handling with helpful messages

## 🚀 Quick Start

### Option 1: Direct Launch (Easiest)

**Windows:**
```bash
python i18n_manager.py
```

**Or double-click:**
```bash
launch-i18n-manager.bat
```

**Linux/Mac:**
```bash
python3 i18n_manager.py
```

### Option 2: Make Portable

1. Copy entire `i18n-tools/` folder to USB drive, cloud storage, or anywhere
2. On any computer, run `python i18n_manager.py`
3. Done! It works immediately

## 📖 How to Use

### 1. Select Your Project

Click **"📂 Browse"** and select your React/TypeScript project folder.

The app will automatically:
- Detect if i18n is configured
- Find source directory (`src/`, `app/`, etc.)
- Locate locales folder if it exists

### 2. If i18n is NOT Configured

Don't worry! The app will offer to set it up for you.

Click **"Yes"** when prompted, and the setup wizard will:
- Create `src/i18n/` directory structure
- Generate `config.ts` with proper setup
- Create initial translation files
- Provide integration instructions

### 3. Select Languages

Choose which languages you want to support:
- ✅ English (always included)
- Choose from 22+ languages
- Languages are auto-detected if already exist

### 4. Run the Workflow

#### Complete Workflow (Recommended)
Click **"🚀 Run Complete Workflow"** to do everything automatically:
1. Detects all hardcoded text
2. Generates translation keys
3. Translates to all selected languages
4. Updates your source code

#### Or Run Steps Individually
- **1️⃣ Detect Text** - Find hardcoded strings
- **2️⃣ Generate Keys** - Create translation keys
- **3️⃣ Translate** - Auto-translate
- **4️⃣ Replace Code** - Update source files

### 5. Check Results

Watch the progress panel for:
- ✅ Success messages
- 📊 Statistics (strings found, keys generated, etc.)
- 📁 File locations
- ⚠️ Warnings or errors

## 📁 What Gets Created

### When Setting Up i18n

```
your-project/
├── src/
│   └── i18n/
│       ├── config.ts          # i18n configuration
│       ├── index.ts           # Exports
│       └── locales/
│           ├── en.json        # English (source)
│           ├── es.json        # Spanish
│           ├── fr.json        # French
│           └── ...
```

### Translation File Format

```json
{
  "common": {
    "welcome": "Welcome",
    "hello": "Hello"
  },
  "nav": {
    "home": "Home",
    "about": "About"
  },
  "button": {
    "save": "Save Changes",
    "cancel": "Cancel"
  }
}
```

### Code Before & After

**Before:**
```tsx
export default function HomePage() {
  return (
    <div>
      <h1>Welcome to our app</h1>
      <p>This is a great product</p>
      <button>Get Started</button>
    </div>
  );
}
```

**After:**
```tsx
import { useTranslation } from 'react-i18next';

export default function HomePage() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t("home.welcome")}</h1>
      <p>{t("home.description")}</p>
      <button>{t("button.getStarted")}</button>
    </div>
  );
}
```

## 🎯 Supported Languages

22+ languages including:
- 🇬🇧 English
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇩🇪 German (Deutsch)
- 🇮🇹 Italian (Italiano)
- 🇵🇹 Portuguese (Português)
- 🇳🇱 Dutch (Nederlands)
- 🇷🇺 Russian (Русский)
- 🇨🇳 Chinese (中文)
- 🇯🇵 Japanese (日本語)
- 🇰🇷 Korean (한국어)
- 🇦🇪 Arabic (العربية)
- And more!

## 💾 Backups & Safety

### Automatic Backups
All backups are stored in the tool directory (portable with the app):
```
i18n-tools/
├── .backups/
│   └── 20251225_143022/    # Timestamped backup
│       ├── HomePage.tsx
│       ├── Nav.tsx
│       └── ...
└── .temp/                  # Temporary files
```

### Settings Persistence
Your preferences are saved:
```
i18n-tools/
└── user_settings.json      # Last project, language selections
```

## 🔧 Requirements

- Python 3.8 or higher
- `tkinter` (usually included with Python)
- `deep-translator` (auto-installed on first run)

## 🚀 Installation

### No Installation Required!

Just:
1. Download or copy the `i18n-tools` folder
2. Run `python i18n_manager.py`
3. Done!

### Optional: Install Dependencies Manually

```bash
pip install deep-translator
```

## 🆘 Troubleshooting

### "No i18n configured" message

**Solution:** Click "Yes" when prompted to run the setup wizard.

### Dependencies not installing

**Solution:** Manually install:
```bash
pip install deep-translator
```

### Translation fails

**Solutions:**
- Check internet connection (needs Google Translate API)
- Try translating fewer languages at once
- Wait a moment and retry

### Can't find source directory

**Solution:**
- Make sure your project has a `src/` or `app/` folder
- Manually specify the source directory in project settings

## 📝 Notes

### What Gets Detected

The tool detects user-facing text in:
- JSX text nodes: `<div>Text here</div>`
- Button text: `<button>Click me</button>`
- Form placeholders: `<input placeholder="Enter name" />`
- Image alt text: `<img alt="Description" />`
- Title attributes: `<div title="Tooltip">...</div>`

### What Gets Skipped

Smart filtering excludes:
- CSS classes and styling
- Variable names and code
- Existing translation calls `t("key")`
- Technical text and error messages
- File paths and URLs

## 🎉 Benefits

### For Developers
- ⏱️ **Save hours** of manual work
- 🎯 **No mistakes** in key generation
- 🔄 **Consistent** translation structure
- 📦 **Portable** - works anywhere

### For Projects
- 🌍 **22+ languages** instantly
- 📊 **Organized** translation files
- 🛡️ **Safe** with automatic backups
- 🚀 **Fast** complete workflow

## 📜 License

MIT License - Free to use for any project

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the progress panel for specific errors
3. Check backups in `.backups/` folder

## 🔄 Updates

**Version 3.0** (Current)
- Complete rewrite - fully standalone
- No CLI dependencies
- Modern GUI interface
- i18n setup wizard
- Embedded all functionality
- Improved error handling
- Better visual design

**Version 2.0**
- GUI with CLI backend
- Subprocess-based execution

**Version 1.0**
- Pure CLI scripts

---

**Made with ❤️ for the developer community**

Transform your React app into a multilingual masterpiece in minutes! 🚀
