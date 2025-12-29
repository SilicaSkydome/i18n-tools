#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Material Design 3 Edition
Beautiful, modern UI with NavigationRail and proper theming
"""

import flet as ft
from pathlib import Path
import json
import re
import shutil
from datetime import datetime
from collections import defaultdict
import threading
from typing import List, Dict, Optional
import sys
import ctypes
import os

# Auto-install dependencies
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class I18nManager:
    """Business logic for i18n automation"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'nl': 'Dutch', 'de': 'German', 'fr': 'French',
        'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese', 'ro': 'Romanian',
        'ru': 'Russian', 'cs': 'Czech', 'pl': 'Polish', 'el': 'Greek',
        'tr': 'Turkish', 'ar': 'Arabic', 'ja': 'Japanese', 'ko': 'Korean',
        'zh': 'Chinese', 'hi': 'Hindi', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish',
    }
    
    SAFE_CONTEXTS = {
        # JSX Text: >Text<
        'jsx_text': r'>([^<>{}\n]+)<',
        
        # Attributes: title="Text", alt="Text", etc.
        'jsx_attr': r'(?:title|alt|placeholder|aria-label|label|description|tooltip|caption|text|error|success|warning|info|help)\s*=\s*["\']([^"\']+)["\']',
        
        # Object Properties (common text fields): label: "Text", message: "Text"
        'obj_property': r'(?:label|title|description|message|error|header|content|tooltip|text|name|caption|body|footer)\s*:\s*["\']([^"\']+)["\']',
    }
    
    TECHNICAL_PATTERNS = [
        r'^[a-z_]+$', r'^[A-Z_]+$', r'^[a-z][a-zA-Z0-9]*$',
        r'^/[a-zA-Z0-9/_-]*$', r'^\./|\.\./', r'className=',
        r'^(text|bg|border|flex|grid|gap|p|m|w|h|rounded|shadow)-',
        r'\.(jpg|jpeg|png|gif|svg|webp|mp4|pdf|json|xml|csv|tsx|jsx|ts|js|css|html)$',
        r'^https?://', r'^#[0-9a-fA-F]{3,8}$', r't\(["\']',
        r'^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$',
        r'^(auto|inherit|initial|unset|none|block|inline|flex|grid|hidden)$',
        r'^(px|rem|em|vh|vw|%)$',
    ]
    
    def __init__(self):
        self.tool_dir = Path(__file__).parent
        self.backups_dir = self.tool_dir / '.backups'
        self.temp_dir = self.tool_dir / '.temp'
        self.backups_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        self.project_path: Optional[Path] = None
        self.src_dir: Optional[Path] = None
        self.locales_dir: Optional[Path] = None
        self.selected_languages: List[str] = ['en']
        self.source_language: str = 'en'
        self.detected_strings: List[Dict] = []
        self.generated_keys: Dict[str, str] = {}
        self.has_i18n_setup = False
        self.on_progress = None
    
    def detect_hardcoded_text(self, source_dir: Path) -> List[Dict]:
        """Detect hardcoded strings"""
        findings = []
        # Scan .tsx, .ts, .jsx, .js files
        extensions = ['*.tsx', '*.ts', '*.jsx', '*.js']
        files = []
        for ext in extensions:
            files.extend(list(source_dir.rglob(ext)))
        
        # Exclude node_modules, dist, build, .git, and .d.ts files
        files = [f for f in files if not any(ex in f.parts for ex in 
                ['node_modules', 'dist', 'build', '.git', 'i18n']) and not f.name.endswith('.d.ts')]
        
        for idx, tsx_file in enumerate(files, 1):
            try:
                content = tsx_file.read_text(encoding='utf-8')
                file_findings = self._scan_file(content, tsx_file)
                findings.extend(file_findings)
                
                if self.on_progress:
                    self.on_progress(idx / len(files))
            except:
                pass
        
        return findings
    
    def _scan_file(self, content: str, filepath: Path) -> List[Dict]:
        """Scan file for strings"""
        findings = []
        existing_keys = set(re.findall(r't\(["\']([^"\']+)["\']\)', content))
        
        for context_name, pattern in self.SAFE_CONTEXTS.items():
            for match in re.finditer(pattern, content):
                text = match.group(1).strip()
                if text and text not in existing_keys and self._is_user_facing(text):
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        'file': str(filepath),
                        'line': line_num,
                        'text': text,
                        'context': context_name
                    })
        
        return findings
    
    def _is_user_facing(self, text: str) -> bool:
        """Check if text is user-facing"""
        # Basic length check
        if len(text) < 2 or len(text) > 500:
            return False
            
        # Ignore if it looks like a variable or constant (camelCase or ALL_CAPS)
        # But allow if it contains spaces (likely a sentence)
        if ' ' not in text:
            if text.isupper(): # CONSTANT_VALUE
                return False
            if text[0].islower() and any(c.isupper() for c in text): # camelCase
                return False
            if '_' in text or '-' in text: # snake_case or kebab-case
                return False
        
        # Ignore technical patterns
        for pattern in self.TECHNICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Must contain at least some letters
        alpha_chars = sum(c.isalpha() for c in text)
        if alpha_chars < len(text) * 0.4: # Allow some numbers/symbols
            return False
            
        return True
    
    def generate_translation_keys(self, strings: List[Dict]) -> Dict[str, Dict]:
        """Generate keys from strings"""
        mapping = {}
        used_keys = set()
        
        for idx, string_info in enumerate(strings, 1):
            text = string_info['text']
            filepath = Path(string_info['file'])
            section = self._determine_section(filepath)
            
            words = re.findall(r'\b[A-Z][a-z]+', text)
            key_base = ''.join(word.lower() for word in words[:3]) or 'text'
            
            key_name = key_base
            counter = 1
            while f'{section}.{key_name}' in used_keys:
                key_name = f'{key_base}{counter}'
                counter += 1
            
            full_key = f'{section}.{key_name}'
            used_keys.add(full_key)
            
            mapping[full_key] = {
                'text': text,
                'file': str(filepath),
                'context': string_info['context'],
                'section': section,
                'key_name': key_name
            }
            
            if self.on_progress and idx % 10 == 0:
                self.on_progress(idx / len(strings))
        
        return mapping
    
    def _determine_section(self, filepath: Path) -> str:
        """Determine section from path"""
        path_lower = str(filepath).lower()
        
        sections = {
            'nav': 'nav', 'footer': 'footer', 'home': 'home', 'about': 'about',
            'contact': 'contact', 'auth': 'auth', 'login': 'auth', 'form': 'form',
            'button': 'button'
        }
        
        for key, section in sections.items():
            if key in path_lower:
                return section
        
        return 'common'
    
    def sync_translation_keys(self):
        """Sync keys across all languages"""
        if not self.locales_dir or not self.locales_dir.exists():
            return
        
        base_lang = self.source_language or 'en'
        base_file = self.locales_dir / f'{base_lang}.json'
        if not base_file.exists():
            return
        
        with open(base_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        for lang_file in self.locales_dir.glob('*.json'):
            if lang_file.stem == base_lang:
                continue
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            synced = self._sync_nested_dict(base_data, lang_data, lang_file.stem)
            
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(synced, f, indent=2, ensure_ascii=False)
    
    def _sync_nested_dict(self, source: dict, target: dict, lang: str) -> dict:
        """Sync nested dictionaries"""
        result = {}
        
        for key, value in source.items():
            if isinstance(value, dict):
                target_value = target.get(key, {})
                result[key] = self._sync_nested_dict(value, target_value, lang)
            else:
                result[key] = target.get(key, f'[SRC] {value}')
        
        return result
    
    def translate_to_languages(self, keys_mapping: Dict, languages: List[str]):
        """Translate to languages"""
        marker = '[SRC] '
        source_lang = self.source_language or 'en'

        for lang in languages:
            lang_file = self.locales_dir / f'{lang}.json'
            
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            for full_key, info in keys_mapping.items():
                section, key_name = full_key.split('.', 1)
                text = info['text']
                
                if section not in data:
                    data[section] = {}
                
                if lang == source_lang:
                    data[section][key_name] = text
                else:
                    data[section][key_name] = f'{marker}{text}'
            
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Auto-translate
        targets = [l for l in languages if l != source_lang]
        for lang in targets:
            self._translate_file(self.locales_dir / f'{lang}.json', lang, source_lang, marker)
    
    def _translate_file(self, filepath: Path, target_lang: str, source_lang: str, marker: str):
        """Translate file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated = self._translate_dict(data, target_lang, source_lang, marker)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translated, f, indent=2, ensure_ascii=False)
    
    def _translate_dict(self, data: dict, target_lang: str, source_lang: str, marker: str) -> dict:
        """Recursively translate dict"""
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._translate_dict(value, target_lang, source_lang, marker)
            elif isinstance(value, str) and value.startswith(marker):
                original = value[len(marker):]
                try:
                    translator = GoogleTranslator(source=source_lang, target=target_lang)
                    result[key] = translator.translate(original)
                except:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def replace_in_source_code(self, keys_mapping: Dict):
        """Replace hardcoded text in code"""
        backup_dir = self.backups_dir / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_map = defaultdict(list)
        for full_key, info in keys_mapping.items():
            files_map[info['file']].append({
                'key': full_key,
                'text': info['text'],
                'context': info['context']
            })
        
        for filepath, replacements in files_map.items():
            filepath = Path(filepath)
            
            shutil.copy2(filepath, backup_dir / filepath.name)
            
            content = filepath.read_text(encoding='utf-8')
            modified_content = content
            
            if 'useTranslation' not in content:
                modified_content = self._add_i18n_import(modified_content)
            
            for repl in replacements:
                modified_content = self._apply_replacement(
                    modified_content,
                    repl['text'],
                    repl['key'],
                    repl['context']
                )
            
            filepath.write_text(modified_content, encoding='utf-8')
    
    def _add_i18n_import(self, content: str) -> str:
        """Add import and hook"""
        import_line = "import { useTranslation } from 'react-i18next';\n"
        
        if 'from "react"' in content or "from 'react'" in content:
            content = re.sub(
                r'(import.*from ["\']react["\'];?\n)',
                r'\1' + import_line,
                content,
                count=1
            )
        else:
            content = import_line + '\n' + content
        
        if '{ t }' not in content:
            component_pattern = r'(export\s+default\s+function\s+\w+\s*\([^)]*\)\s*\{)'
            match = re.search(component_pattern, content)
            
            if match:
                pos = match.end()
                hook_line = '\n  const { t } = useTranslation();\n'
                content = content[:pos] + hook_line + content[pos:]
        
        return content
    
    def _apply_replacement(self, content: str, text: str, key: str, context: str) -> str:
        """Apply replacement"""
        text_escaped = re.escape(text)
        
        # Define replacements based on context
        replacements = {}
        
        # JSX Text: >Text< -> >{t('key')}<
        replacements['jsx_text'] = (f'>{text_escaped}<', f'>{{t("{key}")}}<')
        
        # Attributes: title="Text" -> title={t('key')}
        # We need to match the attribute name to preserve it
        # This is tricky with simple replace, so we use regex sub with a function or specific pattern
        # For now, we'll try to match the specific instance
        
        if context == 'jsx_attr':
            # Find the attribute that contains this text
            # Pattern: attr="Text"
            pattern = r'([a-zA-Z0-9_-]+)\s*=\s*["\']' + text_escaped + r'["\']'
            replacement = r'\1={t("' + key + r'")}'
            content = re.sub(pattern, replacement, content)
            
        elif context == 'obj_property':
            # Object property: label: "Text" -> label: t('key')
            pattern = r'([a-zA-Z0-9_-]+)\s*:\s*["\']' + text_escaped + r'["\']'
            replacement = r'\1: t("' + key + r'")'
            content = re.sub(pattern, replacement, content)
            
        elif context in replacements:
            pattern, replacement = replacements[context]
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def validate_translations(self) -> Dict:
        """Validate translation completeness"""
        if not self.locales_dir or not self.locales_dir.exists():
            return {'error': 'No locales directory'}
        
        base_lang = self.source_language or 'en'
        base_file = self.locales_dir / f'{base_lang}.json'
        if not base_file.exists():
            return {'error': f'No base reference file: {base_lang}.json'}
        
        with open(base_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        results = {}
        
        for lang_file in self.locales_dir.glob('*.json'):
            if lang_file.stem == base_lang:
                continue
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            missing = self._find_missing_keys(base_data, lang_data)
            results[lang_file.stem] = {
                'missing': missing,
                'total': self._count_keys(base_data)
            }
        
        return results
    
    def _find_missing_keys(self, source: dict, target: dict, prefix: str = '') -> List[str]:
        """Find missing keys"""
        missing = []
        
        for key, value in source.items():
            full_key = f'{prefix}.{key}' if prefix else key
            
            if isinstance(value, dict):
                target_value = target.get(key, {})
                missing.extend(self._find_missing_keys(value, target_value, full_key))
            else:
                if key not in target or (isinstance(target.get(key), str) and target[key].startswith('[EN] ')):
                    missing.append(full_key)
        
        return missing
    
    def _count_keys(self, data: dict) -> int:
        """Count total keys"""
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_keys(value)
            else:
                count += 1
        return count


def main(page: ft.Page):
    """Main application"""
    
    # Fix taskbar icon on Windows
    try:
        # Unique ID to ensure taskbar grouping works correctly
        myappid = 'uniteddutchcompany.i18ntools.modern.v1.2'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    
    # Configure page - Material Design 3
    page.title = "i18n-tools"
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = False
    
    # Set window icon
    icon_path = None
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        # Try icon.ico first (root), then img/favicon.png
        check_paths = [
            os.path.join(sys._MEIPASS, "icon.ico"),
            os.path.join(sys._MEIPASS, "img", "favicon.png")
        ]
    else:
        # Running as script
        check_paths = [
            os.path.join(os.path.dirname(__file__), "icon.ico"),
            os.path.join(os.path.dirname(__file__), "img", "favicon.png")
        ]
    
    for path in check_paths:
        if os.path.exists(path):
            icon_path = path
            break
            
    if icon_path:
        page.window.icon = icon_path
    page.update()

    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True
    )
    page.padding = 0
    page.window.width = 1400
    page.window.height = 800
    page.window.min_width = 1200
    page.window.min_height = 700
    
    # Manager instance
    manager = I18nManager()
    
    # State
    selected_languages = ['en']
    source_language = 'en'
    project_selected = False
    
    # UI Elements
    project_path_text = ft.Text("No project selected", color="onSurfaceVariant")
    status_text = ft.Text("Select a project to begin", color="onSurfaceVariant")
    
    # Status cards column
    status_cards = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=8, expand=True)
    
    # Progress bar
    progress_bar = ft.ProgressBar(visible=False, color="primary")
    progress_text = ft.Text("", size=12, color="onSurfaceVariant")
    
    def add_status_card(icon_name: str, title: str, subtitle: str = "", status: str = "info"):
        """Add a status card with Material Design 3 styling"""
        colors_map = {
            'info': "secondaryContainer",
            'success': "tertiaryContainer",
            'warning': "errorContainer",
            'running': "primaryContainer"
        }
        
        card = ft.Card(
            elevation=1,
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(
                        icon_name,
                        size=24,
                        color="onSurfaceVariant"
                    ),
                    ft.Column([
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500, color="onSurface"),
                        ft.Text(subtitle, size=12, color="onSurfaceVariant") if subtitle else ft.Container(),
                    ], spacing=2, expand=True),
                ], spacing=12),
                padding=16,
                bgcolor=colors_map.get(status, "surface"),
            )
        )
        status_cards.controls.insert(0, card)
        page.update()
        return card
    
    def update_progress(value: float, text: str = ""):
        """Update progress bar"""
        progress_bar.value = value
        progress_bar.visible = value < 1.0
        progress_text.value = text
        page.update()
    
    # Language selection
    language_checks = {}
    language_chips_row = ft.Row(wrap=True, spacing=8)

    def refresh_language_controls():
        """Refresh language UI controls based on current source_language and selection."""
        # Ensure source language is always selected
        if source_language not in selected_languages:
            selected_languages.append(source_language)

        for code, cb in language_checks.items():
            cb.disabled = (not project_selected) or (code == source_language)
            cb.value = (code in selected_languages)

        update_language_chips()
    
    def update_language_chips():
        """Update selected language chips"""
        language_chips_row.controls.clear()
        # Source chip
        language_chips_row.controls.append(
            ft.Chip(
                label=ft.Text(f"{manager.SUPPORTED_LANGUAGES.get(source_language, source_language)} (source)"),
                disabled=True,
                bgcolor="surfaceVariant",
            )
        )

        # Target chips
        for lang in selected_languages:
            if lang != source_language:
                chip = ft.Chip(
                    label=ft.Text(manager.SUPPORTED_LANGUAGES[lang]),
                    on_delete=lambda e, l=lang: remove_language(l),
                    delete_icon=ft.Icons.CLOSE,
                    bgcolor="secondaryContainer",
                )
                language_chips_row.controls.append(chip)

        page.update()
    
    def remove_language(lang: str):
        """Remove language"""
        if lang == source_language:
            return
        if lang in selected_languages:
            selected_languages.remove(lang)
            language_checks[lang].value = False
            update_language_chips()
    
    def toggle_language(lang: str, checked: bool):
        """Toggle language selection"""
        if lang == source_language:
            # Source language is always selected
            language_checks[lang].value = True
            return
        if checked and lang not in selected_languages:
            selected_languages.append(lang)
        elif not checked and lang in selected_languages:
            selected_languages.remove(lang)
        update_language_chips()
    
    # Create language checkboxes
    lang_column = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO)
    for code, name in sorted(manager.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1]):
        cb = ft.Checkbox(
            label=name,
            value=(code in selected_languages),
            disabled=True,
            on_change=lambda e, c=code: toggle_language(c, e.control.value)
        )
        language_checks[code] = cb
        lang_column.controls.append(cb)

    def on_source_language_change(e):
        nonlocal source_language
        if not project_selected:
            return
        new_lang = e.control.value
        if not new_lang:
            return
        source_language = new_lang
        manager.source_language = source_language
        refresh_language_controls()

    source_language_dd = ft.Dropdown(
        label="Source language",
        value=source_language,
        options=[ft.dropdown.Option(code, name) for code, name in sorted(manager.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])],
        on_select=on_source_language_change,
        disabled=True,
        width=260,
    )
    
    # Project selection
    async def select_project(e):
        """Select project folder"""
        dialog = ft.FilePicker()
        page.overlay.append(dialog)
        page.update()

        selected_path = dialog.get_directory_path(dialog_title="Select React/TypeScript Project")
        if not selected_path:
            return

        on_folder_selected(selected_path)
    
    def on_folder_selected(selected_path: str):
        """Handle folder selection"""
        nonlocal project_selected
        if not selected_path:
            return

        manager.project_path = Path(selected_path)
        project_path_text.value = str(manager.project_path)
        
        # Detect project setup
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = manager.project_path / src_name
            if src_path.exists():
                manager.src_dir = src_path
                break
        
        if not manager.src_dir:
            add_status_card(ft.Icons.ERROR, "No src/ directory found", status="warning")
            status_text.value = "❌ No src/ directory"
            page.update()
            return

        project_selected = True
        source_language_dd.disabled = False
        
        # Check i18n setup
        i18n_config = manager.src_dir / 'i18n' / 'config.ts'
        locales_dir = manager.src_dir / 'i18n' / 'locales'
        
        manager.has_i18n_setup = i18n_config.exists() and locales_dir.exists()
        
        if manager.has_i18n_setup:
            manager.locales_dir = locales_dir
            
            # Detect languages
            existing = [f.stem for f in locales_dir.glob('*.json') 
                       if f.stem not in ('index', 'config')]
            if existing:
                selected_languages.clear()
                selected_languages.extend(existing)
                for lang in existing:
                    if lang in language_checks:
                        language_checks[lang].value = True

                # Pick source language from existing locales if possible
                # Prefer English if present, otherwise first locale
                nonlocal source_language
                if 'en' in existing:
                    source_language = 'en'
                else:
                    source_language = existing[0]
                manager.source_language = source_language
                source_language_dd.value = source_language
                refresh_language_controls()
            else:
                manager.source_language = source_language
                refresh_language_controls()
            
            add_status_card(ft.Icons.CHECK_CIRCLE, f"i18n configured", f"{len(existing)} languages", "success")
            status_text.value = "✅ Ready to process"
            if hasattr(manager, 'setup_card_ref'):
                manager.setup_card_ref.visible = False
        else:
            add_status_card(ft.Icons.WARNING, "i18n not configured", "Setup required", "warning")
            status_text.value = "⚠️ Setup required"
            if hasattr(manager, 'setup_card_ref'):
                manager.setup_card_ref.visible = True
            # Let the user choose source language / targets first, then click "Initialize i18n"
        
        page.update()
    
    def show_setup_dialog():
        """Show setup dialog"""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def create_setup(e):
            dialog.open = False
            page.update()
            run_setup()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Setup i18n?"),
            content=ft.Text("This project doesn't have i18n configured.\n\nWould you like to set it up now?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Setup", on_click=create_setup),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def run_setup():
        """Create i18n setup"""
        try:
            i18n_dir = manager.src_dir / 'i18n'
            locales_dir = i18n_dir / 'locales'
            locales_dir.mkdir(parents=True, exist_ok=True)
            
            # Config file
            base_lang = manager.source_language or 'en'
            config_content = f"""import i18n from 'i18next';
import {{ initReactI18next }} from 'react-i18next';
import source from './locales/{base_lang}.json';

i18n.use(initReactI18next).init({{
    resources: {{ '{base_lang}': {{ translation: source }} }},
    lng: '{base_lang}',
    fallbackLng: '{base_lang}',
    interpolation: {{ escapeValue: false }}
}});

export default i18n;
"""
            (i18n_dir / 'config.ts').write_text(config_content, encoding='utf-8')
            
            # Initial locale files
            structure = {"common": {}, "nav": {}, "button": {}, "form": {}, "message": {}}
            for lang in selected_languages:
                with open(locales_dir / f'{lang}.json', 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=2, ensure_ascii=False)
            
            # Index file
            (i18n_dir / 'index.ts').write_text("export { default } from './config';\n", encoding='utf-8')
            
            manager.has_i18n_setup = True
            manager.locales_dir = locales_dir
            status_text.value = "✅ Ready to process"
            
            add_status_card(ft.Icons.CHECK_CIRCLE, "i18n setup complete!", status="success")
            
            # Show info dialog
            info_dialog = ft.AlertDialog(
                title=ft.Text("Setup Complete!"),
                content=ft.Text("i18n configured successfully!\n\nNext steps:\n1. Run 'npm install react-i18next i18next'\n2. Import './i18n' in your App.tsx"),
                actions=[ft.TextButton("OK", on_click=lambda e: close_info_dialog())],
            )
            
            def close_info_dialog():
                info_dialog.open = False
                page.update()
            
            page.overlay.append(info_dialog)
            info_dialog.open = True
            page.update()
        except Exception as ex:
            add_status_card(ft.Icons.ERROR, "Setup failed", str(ex), "warning")
    
    # Workflow actions
    def run_detect(e):
        """Run detection"""
        if not manager.project_path or not manager.has_i18n_setup:
            add_status_card(ft.Icons.ERROR, "Please select a project with i18n setup first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.SEARCH, "Detecting hardcoded text...", status="running")
                manager.on_progress = update_progress
                
                strings = manager.detect_hardcoded_text(manager.src_dir)
                manager.detected_strings = strings
                
                add_status_card(ft.Icons.CHECK_CIRCLE, f"Found {len(strings)} hardcoded strings", status="success")
                update_progress(1.0)
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Detection failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_generate(e):
        """Generate keys"""
        if not manager.detected_strings:
            add_status_card(ft.Icons.ERROR, "No detected strings. Run 'Detect Text' first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.KEY, "Generating translation keys...", status="running")
                manager.on_progress = update_progress
                
                mapping = manager.generate_translation_keys(manager.detected_strings)
                manager.generated_keys = mapping
                
                add_status_card(ft.Icons.CHECK_CIRCLE, f"Generated {len(mapping)} keys", status="success")
                update_progress(1.0)
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Key generation failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_sync(e):
        """Sync keys"""
        if not manager.project_path or not manager.has_i18n_setup:
            add_status_card(ft.Icons.ERROR, "Please select a project with i18n setup first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.SYNC, "Synchronizing translation keys...", status="running")
                
                manager.sync_translation_keys()
                
                add_status_card(ft.Icons.CHECK_CIRCLE, f"Synced keys across {len(selected_languages)} languages", status="success")
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Sync failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_translate(e):
        """Run translation"""
        if not manager.generated_keys:
            add_status_card(ft.Icons.ERROR, "No generated keys. Run 'Generate Keys' first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.TRANSLATE, f"Translating to {len(selected_languages)} languages...", status="running")
                
                manager.selected_languages = selected_languages
                manager.source_language = source_language
                manager.translate_to_languages(manager.generated_keys, selected_languages)
                
                add_status_card(ft.Icons.CHECK_CIRCLE, f"Translated to {len(selected_languages)} languages", status="success")
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Translation failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_replace(e):
        """Run code replacement"""
        if not manager.generated_keys:
            add_status_card(ft.Icons.ERROR, "No generated keys. Run 'Generate Keys' first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.EDIT, "Updating source code...", status="running")
                
                manager.replace_in_source_code(manager.generated_keys)
                
                add_status_card(ft.Icons.CHECK_CIRCLE, "Code replacement complete!", status="success")
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Replacement failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_validate(e):
        """Run validation"""
        if not manager.project_path or not manager.has_i18n_setup:
            add_status_card(ft.Icons.ERROR, "Please select a project with i18n setup first", status="warning")
            return
        
        def worker():
            try:
                add_status_card(ft.Icons.VERIFIED, "Validating translations...", status="running")
                
                results = manager.validate_translations()
                
                if 'error' in results:
                    add_status_card(ft.Icons.ERROR, results['error'], status="warning")
                else:
                    total_missing = sum(len(r['missing']) for r in results.values())
                    if total_missing == 0:
                        add_status_card(ft.Icons.CHECK_CIRCLE, "All translations complete!", status="success")
                    else:
                        add_status_card(ft.Icons.WARNING, f"{total_missing} missing translations", status="warning")
                        for lang, data in results.items():
                            if data['missing']:
                                add_status_card(
                                    ft.Icons.WARNING,
                                    f"{manager.SUPPORTED_LANGUAGES[lang]}: {len(data['missing'])} missing",
                                    status="warning"
                                )
            except Exception as ex:
                add_status_card(ft.Icons.ERROR, f"Validation failed: {str(ex)}", status="warning")
        
        threading.Thread(target=worker, daemon=True).start()
    
    # Navigation rail with Material Design 3 icons
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        bgcolor="surface",
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.FOLDER_OUTLINED,
                selected_icon=ft.Icons.FOLDER,
                label="Project"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SEARCH_OUTLINED,
                selected_icon=ft.Icons.SEARCH,
                label="Detect"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.KEY_OUTLINED,
                selected_icon=ft.Icons.KEY,
                label="Generate"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SYNC_OUTLINED,
                selected_icon=ft.Icons.SYNC,
                label="Sync"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TRANSLATE_OUTLINED,
                selected_icon=ft.Icons.TRANSLATE,
                label="Translate"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.EDIT_OUTLINED,
                selected_icon=ft.Icons.EDIT,
                label="Replace"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.VERIFIED_OUTLINED,
                selected_icon=ft.Icons.VERIFIED,
                label="Validate"
            ),
        ],
        on_change=lambda e: switch_view(e.control.selected_index)
    )
    
    # Content views
    content_area = ft.Container(expand=True, padding=24, bgcolor="surfaceVariant")
    
    def switch_view(index: int):
        """Switch content view"""
        if index != 0 and not manager.project_path:
            add_status_card(ft.Icons.INFO, "Select a project first", "Project selection is required before using tools.", "info")
            rail.selected_index = 0
            content_area.content = create_project_view()
            page.update()
            return
        rail.selected_index = index
        
        views = [
            create_project_view(),
            create_action_view("Detect Hardcoded Text", "Scan your TypeScript/React files for hardcoded user-facing text that should be translated.", ft.Icons.SEARCH, run_detect),
            create_action_view("Generate Translation Keys", "Generate semantic translation keys for all detected strings.", ft.Icons.KEY, run_generate),
            create_action_view("Sync Translation Keys", "Synchronize translation keys across all language files.", ft.Icons.SYNC, run_sync),
            create_action_view("Auto-Translate", "Automatically translate all keys to selected languages using Google Translate.", ft.Icons.TRANSLATE, run_translate),
            create_action_view("Update Source Code", "Replace hardcoded text in your source code with t() function calls.", ft.Icons.EDIT, run_replace),
            create_action_view("Validate Translations", "Check translation completeness and find missing translations.", ft.Icons.VERIFIED, run_validate),
        ]
        
        content_area.content = views[index]
        page.update()
    
    def create_project_view():
        """Project configuration view"""
        
        # Action Card Component
        def create_action_card(title, description, icon, on_click, color="primaryContainer"):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color="primary"),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="onSurface"),
                    ft.Text(description, size=12, color="onSurfaceVariant", no_wrap=False, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Container(expand=True), # Spacer
                    ft.FilledButton("Run", icon=ft.Icons.PLAY_ARROW, on_click=on_click, width=float("inf"), disabled=not project_selected)
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=16,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 4),
                ),
                animate=ft.Animation(300, "easeOut"),
                on_hover=lambda e: highlight_card(e),
                col={"sm": 12, "md": 6, "xl": 4}, # Responsive grid
                height=240,
            )

        def highlight_card(e):
            e.control.shadow.blur_radius = 20 if e.data == "true" else 10
            e.control.shadow.spread_radius = 2 if e.data == "true" else 1
            e.control.update()

        # Grid of actions
        actions_grid = ft.ResponsiveRow([
            create_action_card("Detect Text", "Scan project for hardcoded strings.", ft.Icons.SEARCH, run_detect),
            create_action_card("Generate Keys", "Create semantic translation keys.", ft.Icons.KEY, run_generate),
            create_action_card("Sync Keys", "Sync keys across all languages.", ft.Icons.SYNC, run_sync),
            create_action_card("Translate", "Auto-translate using Google Translate.", ft.Icons.TRANSLATE, run_translate),
            create_action_card("Replace Code", "Update source code with t() calls.", ft.Icons.EDIT, run_replace),
            create_action_card("Validate", "Check for missing translations.", ft.Icons.VERIFIED, run_validate),
        ], spacing=20, run_spacing=20)

        # Setup Card (Conditional)
        setup_card = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color="error", size=40),
                ft.Column([
                    ft.Text("i18n Not Configured", size=18, weight=ft.FontWeight.BOLD, color="error"),
                    ft.Text("This project needs i18n setup to work.", color="onSurfaceVariant"),
                ], expand=True),
                ft.FilledButton("Initialize i18n", icon=ft.Icons.BUILD, on_click=lambda e: show_setup_dialog(), style=ft.ButtonStyle(bgcolor="error"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=20,
            bgcolor="errorContainer",
            border_radius=12,
            visible=False # Hidden by default
        )
        
        # Store reference to update visibility later
        manager.setup_card_ref = setup_card

        return ft.ListView([
            ft.Text("Project Dashboard", size=32, weight=ft.FontWeight.BOLD, color="onSurface"),
            ft.Divider(height=20, color="transparent"),
            
            # Project Selection Card
            ft.Card(
                elevation=0,
                variant=ft.CardVariant.OUTLINED,
                content=ft.Container(
                    bgcolor="surface",
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER, size=32, color="primary"),
                        ft.Column([
                            ft.Text("Current Project", size=12, color="onSurfaceVariant"),
                            project_path_text,
                        ], expand=True),
                        ft.OutlinedButton("Change", icon=ft.Icons.FOLDER_OPEN, on_click=select_project)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20,
                )
            ),
            
            ft.Divider(height=20, color="transparent"),
            setup_card,
            ft.Divider(height=20, color="transparent"),
            
            ft.Text("Target Languages", size=20, weight=ft.FontWeight.BOLD, color="onSurface"),
            ft.Container(content=source_language_dd, padding=ft.padding.only(bottom=10)),
            ft.Container(content=language_chips_row, padding=10),
            ft.ExpansionTile(
                title=ft.Text("Manage Languages"),
                subtitle=ft.Text("Add or remove supported languages"),
                controls=[ft.Container(content=lang_column, height=200, padding=10)]
            ),
            
            ft.Divider(height=30, color="transparent"),
            ft.Text("Actions", size=20, weight=ft.FontWeight.BOLD, color="onSurface"),
            ft.Divider(height=10, color="transparent"),
            actions_grid,
            
        ], expand=True, spacing=10, padding=20)
    
    def create_action_view(title: str, description: str, icon_name: str, action):
        """Create action view"""
        return ft.Column([
            ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color="onSurface"),
            
            ft.Card(
                elevation=3,
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(icon_name, size=48, color="primary"),
                        ft.Text(description, size=14, color="onSurface"),
                        ft.FilledButton(
                            title,
                            icon=icon_name,
                            on_click=action,
                            height=48,
                            disabled=not project_selected,
                        ),
                    ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    bgcolor="surface",
                    border_radius=12,
                )
            ),
        ], spacing=16, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Status panel
    status_panel = ft.Container(
        content=ft.Column([
            ft.Text("Live Status", size=20, weight=ft.FontWeight.BOLD, color="onSurface"),
            progress_bar,
            progress_text,
            ft.Divider(),
            status_cards,
        ], spacing=12),
        padding=24,
        expand=True,
        bgcolor="surface",
    )
    
    # Initialize
    update_language_chips()
    refresh_language_controls()
    content_area.content = create_project_view()
    
    # Welcome cards
    add_status_card(ft.Icons.CELEBRATION, "Welcome to i18n Manager", "Material Design 3 Edition", "success")
    add_status_card(ft.Icons.INFO, "Select a React/TypeScript project to begin", status="info")
    
    async def close_app(e):
        await page.window.close()

    # Layout with AppBar
    # Custom Window Drag Area
    drag_area = ft.WindowDragArea(
        ft.Container(
            ft.AppBar(
                leading=ft.Icon(ft.Icons.TRANSLATE, color="onPrimary"),
                title=ft.Text("i18n-tools", color="onPrimary"),
                center_title=False,
                bgcolor="primary",
                actions=[
                    ft.IconButton(
                        ft.Icons.BRIGHTNESS_6,
                        icon_color="onPrimary",
                        on_click=lambda e: toggle_theme(),
                        tooltip="Toggle theme"
                    ),
                    ft.IconButton(
                        ft.Icons.CLOSE,
                        icon_color="onPrimary",
                        on_click=close_app,
                        tooltip="Close"
                    ),
                ],
            ),
        ),
    )

    page.add(
        ft.Column([
            drag_area,
            ft.Container(
                content=ft.Row([
                    rail,
                    ft.VerticalDivider(width=1),
                    content_area,
                    ft.VerticalDivider(width=1),
                    ft.Container(content=status_panel, width=400),
                ], expand=True, spacing=0),
                expand=True,
            )
        ], spacing=0, expand=True)
    )
    
    def toggle_theme():
        """Toggle light/dark theme"""
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()


if __name__ == '__main__':
    ft.app(main, assets_dir=".")
