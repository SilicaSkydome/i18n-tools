# i18n-tools Copilot Instructions

## Project Overview

This is a **standalone desktop application** for automating internationalization (i18n) in React/TypeScript projects.
It is built with **Python** and **Flet** (Flutter for Python), providing a modern, responsive Material Design 3 interface.
The application is designed to be compiled into a single executable (`.exe`) using **PyInstaller**, making it 100% portable.

## Core Architecture

### 1. Technology Stack
- **Language**: Python 3.10+
- **UI Framework**: [Flet](https://flet.dev/) (Material Design 3)
- **Translation**: `deep-translator` (Google Translate API)
- **Packaging**: `PyInstaller` (One-file mode)

### 2. File Structure
- `i18n_manager_modern.py`: **The Single Source of Truth**. Contains ALL application logic and UI code.
- `dist/i18n-tools.exe`: The compiled standalone executable.
- `img/`: Contains assets like `favicon.png`.
- `icon.ico`: Windows application icon.

### 3. Key Classes
- **`I18nManager`**: Handles all business logic (scanning files, generating keys, translating).
  - `detect_hardcoded_text(path)`: Scans `.tsx` files using regex.
  - `generate_translation_keys()`: Creates semantic keys (e.g., `nav.home`).
  - `translate_to_languages()`: Calls Google Translate API.
  - `replace_in_source_code()`: Modifies files safely.
- **`main(page: ft.Page)`**: The Flet entry point. Defines the UI layout, state management, and event handlers.

## Development Guidelines

### UI Design (Flet)
- **Theme**: Use `page.theme_mode = ft.ThemeMode.LIGHT` (or DARK).
- **Layout**: Use `ft.Row` and `ft.Column` for layout. Use `ft.NavigationRail` for the sidebar.
- **Async**: UI event handlers should be `async` (e.g., `async def select_project(e):`) to prevent freezing.
- **Feedback**: Always show progress using `ft.ProgressBar` and `ft.SnackBar` or status cards.

### Windows Integration
- **Taskbar Icon**: The app uses `ctypes` to set a unique `AppUserModelID` so the taskbar icon works correctly.
- **Asset Paths**: When accessing files (like images), ALWAYS check for `sys._MEIPASS` to support PyInstaller:
  ```python
  if hasattr(sys, '_MEIPASS'):
      base_path = sys._MEIPASS
  else:
      base_path = os.path.dirname(__file__)
  ```

### Safety Mechanisms
- **Backups**: Before ANY file modification, the app must create a backup in `.backups/`.
- **Preview**: Show the user what will happen before applying changes.
- **Validation**: Check if `src/` and `i18n/` exist before proceeding.

## Build Process

To compile the application, use the following command:
```bash
python -m PyInstaller --noconfirm --onefile --windowed --icon "icon.ico" --name "i18n-tools" --add-data "img;img" --add-data "icon.ico;." --hidden-import "flet" --hidden-import "deep_translator" i18n_manager_modern.py
```

## Common Tasks

### Adding a New Language
1. Update `SUPPORTED_LANGUAGES` dictionary in `I18nManager` class.
2. The UI will automatically render the new checkbox.

### Improving Detection
1. Update `SAFE_CONTEXTS` regex patterns in `I18nManager`.
2. Ensure the pattern captures the text content in group 1.

### UI Updates
1. Modify the `main` function in `i18n_manager_modern.py`.
2. Use Flet controls (`ft.Container`, `ft.Card`, `ft.Text`, etc.).
3. Run the script to test: `python i18n_manager_modern.py`.
