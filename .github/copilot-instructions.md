# i18n-tools Copilot Instructions

## Project Overview

A **standalone desktop application** for automating JavaScript framework i18n workflows (React, Next.js, Vue, Angular, Svelte, etc.). Built with **Python + Flet** (Material Design 3), compiles to a portable `.exe` via **PyInstaller**. Zero dependencies on target machine.

**Core Workflow**: Scan source files → Detect hardcoded UI strings → Generate semantic keys → Auto-translate (Google) → Replace in source with `t('key')` calls → Validate & clean up duplicates/unused keys.

## Architecture

### Single-File Design
- **`i18n_manager_modern.py`**: ALL logic + UI (2000+ lines). No separate modules.
- **`I18nManager` class**: Business logic (scanning, translation, code modification, validation).
- **`main(page: ft.Page)` function**: Flet UI definition + event handlers.

### Technology Stack
- **Python 3.10+** | **Flet** (Material Design 3) | **deep-translator** (Google Translate) | **PyInstaller** (one-file `.exe`)
- **Truly Standalone**: No runtime installations, all dependencies bundled (~84 MB .exe)

### Key Classes & Methods
```python
class I18nManager:
    SUPPORTED_LANGUAGES = {'en': 'English', 'nl': 'Dutch', ...}  # 22+ languages
    SAFE_CONTEXTS = {  # Regex patterns for extracting translatable strings (JSX-only, strict)
        'jsx_text': r'>\s*([A-Z][a-zA-Z0-9\s!?.,;:\'"()-]+|[A-Za-z]...',  # Capital start OR multi-word
        'jsx_attr': r'<[^>]*?\s(?:title|alt|placeholder|aria-label|tooltip)=...',  # 5 specific attrs
    }
    
    # Core workflow methods
    detect_hardcoded_text(source_dir) -> List[Dict]  # Scans .tsx/.ts/.jsx/.js
    generate_translation_keys(strings) -> Dict  # Creates keys like "nav.home", auto-deduplicates
    translate_to_languages(keys_mapping, languages)  # Calls Google Translate API
    replace_in_source_code(keys_mapping)  # Injects t() calls + useTranslation import
    
    # Validation & cleanup methods (NEW)
    detect_framework() -> Dict[str, str]  # Detects React/Next.js/Vue/Angular/etc from package.json
    validate_locale_files() -> Dict  # Checks for duplicate keys (same text, different keys)
    remove_duplicate_keys_from_locales() -> int  # Cleans up duplicates, keeps first occurrence
    extract_used_translation_keys() -> set  # Scans code for all t('key') calls
    find_unused_translation_keys() -> Dict  # Finds keys in locales not used in code
    archive_unused_keys(unused_by_lang) -> int  # Moves unused keys to i18n/archived_keys/
```

## Critical Workflows

### Building the Executable
**Two methods** (both produce `dist/i18n-tools.exe`):

1. **PyInstaller** (recommended):
   ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --icon "icon.ico" \
     --name "i18n-tools" --add-data "img;img" --add-data "icon.ico;." \
     --hidden-import "flet" --hidden-import "flet.core" --hidden-import "flet.controls" \
     --hidden-import "deep_translator" i18n_manager_modern.py
   ```

2. **Flet Pack** (alternative):
   ```bash
   flet pack i18n_manager_modern.py -y -D -n "i18n-tools" -i "icon.ico" \
     --add-data "img:img" --add-data "icon.ico:."
   ```

**Note**: Use `;` separator for `--add-data` on Windows, `:` on Linux/macOS.

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Run directly (for testing)
python i18n_manager_modern.py

# Quick build (recommended)
build.bat  # Windows
./build.sh # Linux/macOS
```

**Critical**: Never add runtime dependency installation (e.g., `subprocess.check_call([sys.executable, '-m', 'pip', 'install', ...])`) - it breaks standalone builds. All dependencies must be bundled via PyInstaller.

## Project-Specific Patterns

### Asset Path Resolution
**Always** use `sys._MEIPASS` for PyInstaller compatibility:
```python
if hasattr(sys, '_MEIPASS'):
    icon_path = os.path.join(sys._MEIPASS, "icon.ico")
else:
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
```

### File Picker Pattern
Uses **native OS dialogs** via `tkinter.filedialog` (not Flet's `FilePicker`) to avoid packaging mismatches:
```python
def _pick_directory_native(dialog_title: str) -> Optional[str]:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # Keep above Flet window
    path = filedialog.askdirectory(title=dialog_title)
    root.destroy()
    return path or None
```

### Safety-First Code Modification
Before ANY file modification:
1. **Backup**: Creates timestamped backup in `.backups/{YYYYMMDD_HHMMSS}/`
2. **Atomic Replace**: Uses `filepath.read_text()` → modify → `filepath.write_text()`
3. **Smart Detection**: Skips files in `node_modules`, `dist`, `build`, `.git`, `i18n/`

Example from `replace_in_source_code()`:
```python
backup_dir = self.backups_dir / datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(filepath, backup_dir / filepath.name)
# ... modify content ...
filepath.write_text(modified_content, encoding='utf-8')
```

### String Detection Logic
**User-facing text filter** (`_is_user_facing()`):
- **Reject**: `camelCase`, `ALL_CAPS`, `snake_case`, `kebab-case`, URLs, file extensions, CSS classes, hex colors, code operators
- **Reject Code Patterns**: `===`, `!==`, `case`, `const`, `.map`, `?.`, `typeof`, and 40+ other code indicators
- **Accept**: Natural language sentences (spaces + letters > 40% of text)
- **Multi-word OR Capital Start**: JSX text must start with uppercase OR contain multiple words

Defined in `TECHNICAL_PATTERNS` (50+ patterns):
```python
r'^[a-z_]+$',  # lowercase_identifiers
r'^/[a-zA-Z0-9/_-]*$',  # /paths/like/this
r'className=',  # CSS class attributes
r'\.(jpg|png|svg|tsx|jsx|json|css)$',  # file extensions
r'^https?://',  # URLs
r't\(["\']',  # Already translated: t('key')
r'===|!==',  # JavaScript operators
```

**Code Rejection Keywords** (in `_is_user_facing()`):
- JavaScript operators: `===`, `!==`, `&&`, `||`, `?.`, `??`
- Control flow: `case `, `switch`, `typeof`, `instanceof`
- Functions: `.map`, `.filter`, `.reduce`, `.forEach`, `.includes`
- Common code patterns: `const `, `let `, `var `, `function`, `return`

## Validation & Cleanup Features

### Duplicate Key Detection (NEW)
- **Problem**: Same text appears multiple times with different keys → bloated locale files (4000+ lines instead of 1000)
- **Solution**: 
  - `_deduplicate_strings()` - Removes duplicates BEFORE key generation
  - `validate_locale_files()` - Scans existing locales for duplicate values
  - `remove_duplicate_keys_from_locales()` - Cleans up, keeps first occurrence
- **UI**: "Validate" button shows duplicate stats, "Remove Duplicates" button cleans them up

### Unused Key Detection (NEW)
- **Problem**: Old translations accumulate as code evolves, never cleaned up
- **Solution**:
  - `extract_used_translation_keys()` - Scans all source files for `t('key')` calls
  - `find_unused_translation_keys()` - Compares locale files vs actual code usage
  - `archive_unused_keys()` - Moves unused keys to `i18n/archived_keys/{lang}_unused_{timestamp}.json`
  - Automatically adds `i18n/archived_keys/` to `.gitignore`
- **UI**: "Validate" reports unused keys, "Archive Unused Keys" moves them to timestamped files for manual review

### Framework Detection (NEW)
- **Purpose**: Display which framework the project uses (React, Next.js, Vue, Angular, Svelte, etc.)
- **Implementation**: 
  - `detect_framework()` - Parses `package.json` dependencies in priority order
  - Checks for: Next.js → React → Vue → Angular → Svelte → Solid → Preact → Qwik
  - Extracts version from dependency string
- **UI**: Shows "Framework: React v18.2.0" (or similar) in project selection card

## Dashboard Actions

The app provides 8 main actions (in order of typical workflow):

1. **Detect Text** - Scans project for hardcoded UI strings
2. **Generate Keys** - Creates semantic translation keys (auto-deduplicates)
3. **Sync Keys** - Synchronizes keys across all language files
4. **Translate** - Auto-translates using Google Translate
5. **Replace Code** - Updates source code with `t()` calls
6. **Validate** - Checks for duplicates, unused keys, and missing translations
7. **Remove Duplicates** - Cleans up duplicate keys in locale files
8. **Archive Unused Keys** - Moves unused translations to archive folder

## Flet UI Conventions

### State Management
- **Global flags**: `project_selected`, `busy` control UI enablement
- **Update pattern**: Modify state → call `page.update()` or `control.update()`
- **Async handlers**: All UI event handlers are `async def` to prevent blocking

### Progress Feedback
Status cards use **Material color tokens**:
```python
def add_status_card(icon, title, subtitle, status):
    colors = {
        'info': "secondaryContainer",
        'success': "tertiaryContainer",
        'warning': "errorContainer",
        'running': "primaryContainer"
    }
    # ... creates ft.Card with bgcolor=colors[status]
```

### Windows-Specific Setup
```python
# Fix taskbar icon grouping (Windows only)
myappid = 'uniteddutchcompany.i18ntools.modern.v1.2'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Hidden title bar with custom AppBar
page.window.title_bar_hidden = True
page.window.title_bar_buttons_hidden = False
```

## Common Modifications

### Adding a Language
1. Update `I18nManager.SUPPORTED_LANGUAGES`:
   ```python
   SUPPORTED_LANGUAGES = {..., 'uk': 'Ukrainian', 'vi': 'Vietnamese'}
   ```
2. No UI changes needed—checkboxes auto-generate from dict.

### Improving String Detection
1. Add pattern to `SAFE_CONTEXTS` (extraction) or `TECHNICAL_PATTERNS` (exclusion)
2. Ensure regex captures text in **group 1**: `r'pattern-with-(capture)'`
3. Test with: `python i18n_manager_modern.py` → select test project

### UI Layout Changes
- **Sidebar**: `ft.NavigationRail` with destinations (Project, Detect, Generate, etc.)
- **Main area**: `content_area.content = create_xyz_view()` (swaps views)
- **Right panel**: `status_panel` (progress bar + status cards)
- Example: Adding a new tab → add `ft.NavigationRailDestination` + create view function

## File References
- [i18n_manager_modern.py](i18n_manager_modern.py#L1-L100) - Entry point + imports
- [i18n_manager_modern.py](i18n_manager_modern.py#L100-L250) - `I18nManager` class (regex patterns, detection logic)
- [i18n_manager_modern.py](i18n_manager_modern.py#L250-L450) - Translation + code replacement methods
- [i18n_manager_modern.py](i18n_manager_modern.py#L500-L1500) - `main()` function (entire Flet UI)
- [requirements.txt](requirements.txt) - Dependencies (deep-translator, flet implied)
- [i18n-tools.spec](i18n-tools.spec) - PyInstaller build configuration
