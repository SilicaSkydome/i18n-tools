# i18n-tools Copilot Instructions

## Project Overview

This is a **fully standalone desktop application** for automating internationalization (i18n) in React/TypeScript projects. It's completely self-contained with a modern GUI interface - no CLI dependencies. The tool can detect hardcoded strings, generate translation keys, auto-translate content, and replace code with `t()` calls. It's **100% portable** - copy the folder to any computer and it works immediately on any project.

## Architecture Philosophy

### GUI-First Design
- **Single Entry Point**: Everything runs through [`i18n_manager.py`](../i18n_manager.py) - no separate CLI tools
- **Embedded Logic**: All automation logic lives in the GUI application itself as internal methods
- **No Subprocess Calls**: Direct Python function calls instead of spawning child processes
- **Portable State**: All temporary files and state stored relative to the tool's location, never in the target project

### Standalone Requirements
```python
# CORRECT: Portable, works anywhere
tool_dir = Path(__file__).parent
temp_dir = tool_dir / '.temp'
config_file = tool_dir / 'user_settings.json'

# WRONG: Assumes project structure or absolute paths
config_file = Path.home() / '.i18n-manager' / 'config.json'  # ❌ Not portable
```

## Core Architecture

### Main Application Structure

```python
# i18n_manager.py - Single file containing everything
class I18nManagerApp:
    def __init__(self):
        self.selected_project = None  # User-selected external project
        self.project_config = None     # Detected/created i18n config
        
    # Project detection & initialization
    def detect_project_structure(self) -> ProjectInfo
    def initialize_i18n_setup(self) -> bool
    
    # Core automation (embedded, no subprocess)
    def detect_hardcoded_text(self) -> List[HardcodedString]
    def generate_translation_keys(self) -> Dict[str, str]
    def translate_to_languages(self) -> bool
    def replace_in_source_code(self) -> bool
```

### Data Flow (All In-Memory)

```
User Selects Project → Detect Structure → Initialize i18n (if needed)
                     ↓
              Scan Source Files → Extract Strings → Generate Keys
                     ↓
              Update JSON Files → Auto-Translate → Replace Code
                     ↓
              Show Results in GUI (no external files)
```

### 1. Project Initialization Detection

The app must detect if a project has i18n setup and offer to configure it:

```python
def detect_i18n_setup(self, project_path: Path) -> dict:
    """Returns status of i18n configuration"""
    return {
        'has_react_i18next': self._check_package_json(project_path),
        'has_i18n_config': (project_path / 'src/i18n/config.ts').exists(),
        'has_locales_dir': (project_path / 'src/i18n/locales').exists(),
        'existing_languages': self._scan_existing_locales(project_path)
    }

def offer_i18n_setup(self):
    """Show setup wizard if project has no i18n"""
    response = messagebox.askyesno(
        "Setup i18n?",
        "This project doesn't have i18n configured.\n"
        "Would you like to set it up now?"
    )
    if response:
        self.run_i18n_setup_wizard()
```

**Critical**: Always check before assuming i18n exists. Offer guided setup for new projects.

### 2. Safety-First Architecture

Every file modification follows this pattern (all in GUI thread with progress updates):

```python
def modify_source_files(self):
    # 1. Create in-tool backup directory
    backup_dir = Path(__file__).parent / '.backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Preview changes in GUI
    preview = self.generate_diff_preview()
    if not self.show_preview_dialog(preview):
        return False  # User cancelled
    
    # 3. Backup files
    for file in files_to_modify:
        shutil.copy(file, backup_dir / file.name)
    
    # 4. Apply with progress bar
    self.progress_bar.start()
    for file in files_to_modify:
        self.apply_changes(file)
        self.update_progress()
```

**Never modify files without**: GUI preview dialog, user confirmation, and backups in tool directory.

### 3. Modern GUI Design Patterns

Use these Tkinter patterns for a modern, appealing interface:

```python
# Modern color scheme
COLORS = {
    'primary': '#2563eb',      # Blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Orange
    'danger': '#ef4444',       # Red
    'bg_dark': '#1f2937',      # Dark gray
    'bg_light': '#f9fafb',     # Light gray
    'text_dark': '#111827',
    'text_light': '#6b7280'
}

# Custom styled widgets
def create_modern_button(parent, text, command, style='primary'):
    btn = tk.Button(
        parent, 
        text=text,
        command=command,
        bg=COLORS[style],
        fg='white',
        font=('Segoe UI', 10, 'bold'),
        relief='flat',
        padx=20,
        pady=10,
        cursor='hand2'
    )
    # Hover effect
    btn.bind('<Enter>', lambda e: btn.config(bg=self._darken_color(COLORS[style])))
    btn.bind('<Leave>', lambda e: btn.config(bg=COLORS[style]))
    return btn

# Progress indication with smooth animations
def show_processing_dialog(self, title, message):
    dialog = tk.Toplevel(self.root)
    dialog.title(title)
    # Add spinner animation, progress bar, and cancel button
    # Center on parent window
    dialog.transient(self.root)
    dialog.grab_set()
```

**UI Guidelines**: 
- Use ttk widgets where possible (native look)
- Implement hover effects on all interactive elements
- Show real-time progress with animated spinners
- Use icons/emojis for visual hierarchy (🔍 📝 🌍 ✅)
- Provide immediate feedback for all actions

### 4. Whitelist-Only Detection (Embedded Method)

Detection logic lives in the GUI class as a method:

```python
class I18nManagerApp:
    SAFE_CONTEXTS = {
        'jsx_text_node': r'>([A-Z][^<>{}]*?)<',
        'title_attr': r'title=["\'](.*?)["\']',
        'placeholder_attr': r'placeholder=["\'](.*?)["\']',
    }
    
    TECHNICAL_PATTERNS = [
        r'^[a-z_]+$',  # snake_case
        r'className=',  # CSS classes
        r't\(["\']',    # Existing t() calls
    ]
    
    def detect_hardcoded_strings(self, source_dir: Path) -> List[dict]:
        """Embedded detection - no external scripts"""
        findings = []
        for tsx_file in source_dir.rglob('*.tsx'):
            findings.extend(self._scan_file(tsx_file))
        return findings
```

**Key insight**: All regex patterns are class constants, not in separate files.

### 5. Key Generation Strategy (In-Memory)

Keys generated directly in GUI with live preview:

```python
class I18nManagerApp:
    def generate_translation_key(self, text: str, file_path: Path) -> str:
        """Generate semantic key from text and context"""
        # Determine section from file path
        section = self._determine_section(file_path)  # e.g., 'nav', 'auth', 'home'
        
        # Extract meaningful words
        words = re.findall(r'\b[A-Z][a-z]+', text)
        key_name = ''.join(word.lower() for word in words[:3])
        
        # Ensure uniqueness in memory
        full_key = f'{section}.{key_name}'
        counter = 1
        while full_key in self.generated_keys:
            full_key = f'{section}.{key_name}{counter}'
            counter += 1
        
        self.generated_keys[full_key] = text
        return full_key
    
    def show_key_preview(self):
        """Show live preview of all generated keys before applying"""
        preview_window = tk.Toplevel(self.root)
        tree = ttk.Treeview(preview_window, columns=('Key', 'Text', 'File'))
        for key, text in self.generated_keys.items():
            the Application

```bash
# Double-click launcher (Windows)
launch-i18n-manager.bat

# Or direct Python
python i18n_manager.py

# Everything runs from GUI - no CLI commands needed
```

### Testing Changes

```python
# Add test mode to GUI for development
class I18nManagerApp:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode  # Enables debug panels, verbose logging
        
    def run_tests(self):
        """Built-in test suite accessible from Help menu"""
        self.test_detection_patterns()
        self.test_key_generation()
        self.test_translation_api()
        self.show_test_results()

# Run with test mode
if __name__ == '__main__':
    app = I18nManagerApp(test_mode='--test' in sys.argv)
```

### Portable Installation

```bash
# Just copy the entire folder - that's it!
cp -r i18n-tools /path/to/usb-drive/
# Or zip and email, or put in Dropbox

# Requirements automatically installed on first run
python i18n_manager.py  # Auto-installs dependencies if missing
```

## Configuration System (Standalone)

All config stored in tool directory, never in user's project:

```python
class I18nManagerApp:
    def __init__(self):
        # Tool's own directory
        self.tool_dir = Path(__file__).parent
        
        # Persistent settings (portable with tool)
        self.settings_file = self.tool_dir / 'user_settings.json'
        self.backups_dir = self.tool_dir / '.backups'
        self.temp_dir = self.tool_dir / '.temp'
        
        # Current session only (user-selected project)
        self.current_project = None  # Set by file dialog
        self.project_src = None
        self.project_locales = None
    
    def load_settings(self):
        """Load user preferences (last project, languages, theme)"""
        if self.settings_file.exists():
            with open(self.settings_file) as f:
                return json.load(f)
        return self.default_settings()
    
    def detect_project_locales_dir(self, project_path: Path) -> Path:
        """Auto-detect or suggest locales location"""
        common_paths = [
            project_path / 'src/i18n/locales',
            project_path / 'src/locales',
            project_path / 'public/locales',
            project_path / 'locales'
        ]
   i18n Setup Wizard (For New Projects)

When a project has no i18n configuration, show setup wizard:

```python
def run_i18n_setup_wizard(self):
    """Interactive wizard to configure i18n from scratch"""
    wizard = tk.Toplevel(self.root)
    wizard.title("i18n Setup Wizard")
    
    # Step 1: Install dependencies
    self.wizard_step_dependencies(wizard)
    # - Add react-i18next to package.json
    # - Show npm install command
    
    # Step 2: Create directory structure
    self.wizard_step_directories(wizard)
    # - Create src/i18n/locales/
    # - Create src/i18n/config.ts
    
    # Step 3: Generate config files
    self.wizard_step_config(wizard)
    # - i18n config with selected languages
    # - Create initial en.json
    
    # Step 4: Add to App.tsx
    self.wizard_step_integration(wizard)
    # - Show code snippet to add I18nextProvider
    # - Offer to apply automatically with preview
```

**Output Files Created**:
```
src/i18n/
  ├── config.ts          # i18n configuration
  ├── locales/
  │   ├── en.json        # English (source)
  │   ├── es.json        # Spanish
  │   └── ...
  └── index.ts           # Exports
```

## Translation File Management

The tool creates and manages nested JSON structures:

```python
def create_initial_locale_files(self, languages: List[str]):
    """Initialize locale files with empty structure"""
    structure = {
        "common": {},
        "nav": {},
        "auth": {},
        "form": {},
        "button": {},
        "message": {}
    }
    
    for lang in languages:
        file_path = self.project_locales / f'{lang}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
```

**File Format**:
```json
{
  "nav": {
    "home": "Home",
    "login": "Log in"
  },
  "button": {
    "save": "Save Changes"
  }
}
```

## Error Handling Patterns (GUI-Friendly)

All operations show user-friendly errors in GUI:

```python
def safe_operation(self, operation_name: str, operation_func):
    """Wrapper for all operations with GUI error handling"""
    try:
        self.show_progress(operation_name)
   Cross-Platform GUI Best Practices

```python
class I18nManagerApp:
    def __init__(self):
        # Modern font selection (cross-platform)
        self.fonts = {
            'heading': ('Segoe UI', 14, 'bold') if sys.platform == 'win32' 
                       else ('SF Pro Display', 14, 'bold') if sys.platform == 'darwin'
                       else ('Ubuntu', 14, 'bold'),
            'body': ('Segoe UI', 10) if sys.platform == 'win32'
                    else ('SF Pro Text', 10) if sys.platform == 'darwin' 
                    else ('Ubuntu', 10),
        }
        
        # High DPI scaling
        if sys.platform == 'win32':
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
    def safe_text_display(self, text: str) -> str:
        """Handle Unicode in GUI labels"""
        try:
            return text
        except UnicodeEncodeError:
            return text.encode('ascii', 'replace').decode('ascii')
```

## File Structure (Simplified)

```
i18n-tools/                    # Portable application folder
├── i18n_manager.py           # ⭐ Single entry point (contains all logic)
├── launch-i18n-manager.bat   # Windows launcher
├── launch-i18n-manager.sh    # macOS/Linux launcher
├── requirements.txt          # Dependencies (auto-installed)
├── user_settings.json        # Persistent settings (created on first run)
├── .backups/                 # Backup storage (portable with tool)
│   └── 20251225_143022/      # Timestamped backups
├── .temp/                    # Temporary files (cleaned on exit)
└── README.md                 # User documentation
```

**No More**: Separate CLI scripts, API wrappers, config files, or test scripts in main distribution.

## Common Pitfalls

1. **Never hardcode paths** - Always use file dialogs for project selection; store in session only
   ```python
   # ✅ GOOD
   project = filedialog.askdirectory()
   if project:
       self.current_project = Path(project)
   
   # ❌ BAD
   project = Path.cwd().parent / 'src'  # Assumes location
   ```

2. **Check i18n setup first** - Detect if project is configured before any operations
   ```python
   # ✅ GOOD
   if not self.detect_i18n_setup(project)['has_i18n_config']:
       self.offer_i18n_setup()
   
   # ❌ BAD
   locales = project / 'src/i18n/locales'  # Assumes exists
   ```

3. **All state in memory** - Don't create temp files in project; use tool's .temp directory
   ```python
   # ✅ GOOD
   self.detected_strings = []  # In-memory list
   
   # ❌ BAD
   with open(project / 'hardcoded_report.json', 'w') as f:  # Pollutes project
   ```

4. **GUI responsiveness** - Use threading for long operations with progress updates
   ```python
   # ✅ GOOD
   def translate_in_background(self):
       thread = threading.Thread(target=self._translate_worker)
       thread.daemon = True
       thread.start()
   
   # ❌ BAD
   self.translate_all()  # Freezes GUI for minutes
   ```

5. **Match detection/replacement patterns** - Keep regex patterns in sync as class constants
   ```python
   # ✅ GOOD - Both use same class constant
   class I18nManagerApp:
       SAFE_CONTEXTS = {'jsx_text': r'>([A-Z].*?)<'}
       
       def detect(self): 
           re.search(self.SAFE_CONTEXTS['jsx_text'], ...)
       def replace(self):
           re.sub(self.SAFE_CONTEXTS['jsx_text'], ...)
   ```

## Extension Points

To add new features to the GUI:

1. **New language support** - Add to `SUPPORTED_LANGUAGES` dict in `I18nManagerApp.__init__`
2. **New detection context** - Add pattern to `SAFE_CONTEXTS` class constant
3. **Custom themes** - Modify `COLORS` dict and apply in `setup_styles()`
4. **Export formats** - Add method `export_to_csv()` or `export_to_xlsx()` in main class

All extensions are single-file modifications to `i18n_manager.py`.

```python
PROJECT_ROOT = Path(__file__).parent.parent  # Assumes parent has src/
SRC_DIR = PROJECT_ROOT / 'src'
LOCALES_DIR = SRC_DIR / 'i18n' / 'locales'

# Auto-discovers languages from existing .json files
AVAILABLE_LANGUAGES = get_available_languages()  # Scans locales/*.json
```

**Convention**: English (`en`) is always the source language; others are targets.

## Translation File Format

JSON files in `locales/` use nested structure:

```json
{
  "nav": {
    "home": "Home",
    "login": "Log in"
  },
  "button": {
    "save": "Save Changes"
  }
}
```

Keys use dot notation: `t("nav.home")`, `t("button.save")`

## Error Handling Patterns

All scripts follow this structure:

```python
try:
    result = subprocess.run([...], capture_output=True, text=True)
    if result.returncode != 0:
        log_error(result.stderr)
        return False
except Exception as e:
    log_error(str(e))
    rollback_changes()
    return False
```

Logs are written to: `workflow_log.json`, `replacement_log.json`

## Windows Compatibility

Special handling for encoding issues:

```python
def safe_print(text: str):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))
```

Batch files (`.bat`) and shell scripts (`.sh`) provided for cross-platform launchers.

## Key Files Reference

- **Entry Points**: [`i18n_manager.py`](../i18n_manager.py), [`i18n_master_v2.py`](../i18n_master_v2.py), [`launch-i18n-manager.bat`](../launch-i18n-manager.bat)
- **Core Logic**: [`detect_hardcoded_v2.py`](../detect_hardcoded_v2.py), [`replace_hardcoded_v2.py`](../replace_hardcoded_v2.py), [`translate_keys.py`](../translate_keys.py)
- **Supporting**: [`sync_translation_keys.py`](../sync_translation_keys.py), [`extract_and_generate_keys_v2.py`](../extract_and_generate_keys_v2.py)
- **Testing**: [`test_i18n_tools.py`](../test_i18n_tools.py)
- **Config**: [`CONFIG.py`](../CONFIG.py), [`setup.py`](../setup.py)

## Common Pitfalls

1. **Don't assume project structure** - GUI mode operates on user-selected folders; validate paths exist
2. **Always use subprocess.run with cwd** - Scripts must find each other and write to correct directories
3. **Match detection and replacement patterns** - [`detect_hardcoded_v2.py`](../detect_hardcoded_v2.py) and [`replace_hardcoded_v2.py`](../replace_hardcoded_v2.py) must use identical regexes
4. **Handle Google Translate rate limits** - [`translate_keys.py`](../translate_keys.py) includes retry logic with exponential backoff
5. **Preserve nested JSON structure** - When syncing keys, maintain object hierarchy from English file

## Extension Points

To add new detection contexts, update BOTH:
- [`detect_hardcoded_v2.py`](../detect_hardcoded_v2.py): `SAFE_CONTEXTS` dict
- [`replace_hardcoded_v2.py`](../replace_hardcoded_v2.py): `REPLACEMENT_PATTERNS` dict

To support new languages, add to [`CONFIG.py`](../CONFIG.py): `LANGUAGE_NAMES` dict
