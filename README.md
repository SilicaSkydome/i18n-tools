# 🌍 i18n Manager - Standalone Translation Tool

**Version 3.0 - Modern Edition**

A powerful, standalone desktop application designed to automate the internationalization (i18n) process for React and TypeScript projects. Built with Python and Flet, it offers a beautiful Material Design 3 interface and requires no installation.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

---

## ✨ Key Features

### 🎨 Modern User Interface
- **Material Design 3**: Clean, responsive, and intuitive UI.
- **Dark/Light Mode**: Toggle between themes to suit your preference.
- **Real-time Feedback**: Progress bars, status cards, and live logs keep you informed.

### 🚀 100% Standalone & Portable
- **Single Executable**: The entire app is compiled into one `.exe` file.
- **No Dependencies**: No need to install Python, Node.js, or any libraries on the target machine.
- **Portable**: Run it from a USB drive, network share, or anywhere on your disk.

### 🤖 Automated Workflow
1.  **🔍 Detect**: Scans your `src` folder for hardcoded strings in `.tsx` files.
    -   *Smart Detection*: Ignores technical strings (classNames, URLs, IDs) and focuses on user-facing text.
2.  **🔑 Generate**: Automatically creates semantic translation keys (e.g., `home.welcome_message`).
3.  **🌍 Translate**: Uses Google Translate to auto-translate your keys into **20+ languages**.
4.  **📝 Replace**: Safely replaces the hardcoded text in your source code with `t('key')` calls.

### 🛡️ Safety First
- **Automatic Backups**: Creates a full backup of your modified files in `.backups/` before every operation.
- **Non-Destructive**: You can review changes before they are applied.
- **Smart Context**: Only targets safe contexts like JSX text nodes, `title` attributes, and `placeholder` attributes.

---

## 🚀 Quick Start Guide

### Option 1: Run the Executable (Recommended)

This is the easiest way to use the tool.

1.  Navigate to the **`dist`** folder in this repository.
2.  Double-click **`i18n-tools.exe`**.
3.  The application will launch immediately.

### Option 2: Run from Source Code

If you are a developer and want to modify the tool:

1.  **Install Python 3.10+**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Script**:
    ```bash
    python i18n_manager_modern.py
    ```

---

## 📖 Usage Instructions

### Step 1: Select Your Project
1.  Click **"Select Project"** in the sidebar.
2.  Choose the root folder of your React/TypeScript project.
3.  The tool will automatically detect your `src` directory and check for existing i18n configuration.

### Step 2: Setup i18n (If needed)
If your project doesn't have `i18n` configured, the tool will offer to set it up for you.
-   It will create `src/i18n/config.ts`.
-   It will create `src/i18n/locales/en.json`.
-   It will provide code snippets to add to your `main.tsx`.

### Step 3: Detect & Translate
1.  Go to the **"Detect & Translate"** tab.
2.  Select the target languages you want to support (e.g., Spanish, French, German).
3.  Click **"Start Automation"**.
4.  The tool will:
    -   Scan all `.tsx` files.
    -   Extract hardcoded text.
    -   Generate keys in `en.json`.
    -   Translate those keys to all selected languages.
    -   Update your source code to use `t()` function.

### Step 4: Verify
1.  Check the **"Status"** tab to see a summary of the operation.
2.  Open your project in VS Code and verify the changes.
3.  If something went wrong, check the `.backups` folder to restore your files.

---

## 🛠️ Development & Building

### Project Structure
-   **`i18n_manager_modern.py`**: The main application file containing all logic and UI.
-   **`dist/`**: Contains the compiled `.exe` file.
-   **`img/`**: Assets (icons, images).
-   **`icon.ico`**: The Windows application icon.

### How to Build the Executable
To compile the Python script into a standalone `.exe`, run the following command in your terminal:

```bash
python -m PyInstaller --noconfirm --onefile --windowed --icon "icon.ico" --name "i18n-tools" --add-data "img;img" --add-data "icon.ico;." --hidden-import "flet" --hidden-import "deep_translator" i18n_manager_modern.py
```

This will generate `dist/i18n-tools.exe`.

---

## ❓ Troubleshooting

**Q: The taskbar icon is generic.**
A: This is usually a Windows caching issue. The app sets a specific `AppUserModelID` to fix this. Try unpinning the app and restarting it.

**Q: It's not detecting my text.**
A: The tool uses regex patterns defined in `SAFE_CONTEXTS`. It currently supports JSX text nodes (`>Text<`), `title`, `alt`, `placeholder`, and `label`. Complex nested expressions might be skipped for safety.

**Q: Can I add more languages?**
A: Yes! Edit `i18n_manager_modern.py` and add the language code to the `SUPPORTED_LANGUAGES` dictionary.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
