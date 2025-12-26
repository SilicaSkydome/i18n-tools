#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Modern Desktop Application
Beautiful Discord-like UI with CustomTkinter
Completely self-contained - fully portable standalone app
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import re
import shutil
from pathlib import Path
import threading
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import sys

# Modern dark theme configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Auto-install dependencies if needed
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class I18nManagerApp:
    """Modern i18n Manager with Discord-like UI"""
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'nl': 'Dutch', 'de': 'German', 'fr': 'French',
        'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese', 'ro': 'Romanian',
        'ru': 'Russian', 'cs': 'Czech', 'pl': 'Polish', 'el': 'Greek',
        'tr': 'Turkish', 'ar': 'Arabic', 'ja': 'Japanese', 'ko': 'Korean',
        'zh': 'Chinese', 'hi': 'Hindi', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish',
    }
    
    # Detection patterns
    SAFE_CONTEXTS = {
        'jsx_text_node': r'>([A-Z][^<>{}]*?)<',
        'title_attr': r'title=["\'](.*?)["\']',
        'alt_attr': r'alt=["\'](.*?)["\']',
        'placeholder_attr': r'placeholder=["\'](.*?)["\']',
        'label_text': r'<label[^>]*>([^<]+)</label>',
        'button_text': r'<[Bb]utton[^>]*>([^<]+)</[Bb]utton>',
    }
    
    TECHNICAL_PATTERNS = [
        r'^[a-z_]+$', r'^[A-Z_]+$', r'^[a-z][a-zA-Z0-9]*$',
        r'^/[a-zA-Z0-9/_-]*$', r'^\./|\.\./', r'className=',
        r'^(text|bg|border|flex|grid|gap|p|m|w|h|rounded|shadow)-',
        r'\.(jpg|jpeg|png|gif|svg|webp|mp4|pdf|json|xml|csv|tsx|jsx|ts|js|css|html)$',
        r'^https?://', r'^#[0-9a-fA-F]{3,8}$', r't\(["\']',
    ]
    
    def __init__(self):
        # Main window
        self.root = ctk.CTk()
        self.root.title("i18n Manager")
        self.root.geometry("1200x850")
        
        # Tool directory (portable)
        self.tool_dir = Path(__file__).parent
        self.backups_dir = self.tool_dir / '.backups'
        self.temp_dir = self.tool_dir / '.temp'
        self.settings_file = self.tool_dir / 'user_settings.json'
        
        # Create directories
        self.backups_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Project state
        self.project_path: Optional[Path] = None
        self.src_dir: Optional[Path] = None
        self.locales_dir: Optional[Path] = None
        self.selected_languages: List[str] = ['en']
        self.detected_strings: List[Dict] = []
        self.generated_keys: Dict[str, str] = {}
        self.has_i18n_setup = False
        
        # Build UI
        self.create_ui()
        self.center_window()
        self.load_settings()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = 1200
        height = 850
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create modern Discord-like interface"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title bar with gradient effect
        title_frame = ctk.CTkFrame(main_container, height=100, corner_radius=15)
        title_frame.pack(fill="x", pady=(0, 15))
        title_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🌍  i18n Manager",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left", padx=30, pady=25)
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Universal Translation Tool",
            font=ctk.CTkFont(size=14),
            text_color=("gray60", "gray50")
        )
        subtitle_label.pack(side="left", pady=25)
        
        # Project section
        self.create_project_section(main_container)
        
        # Languages section
        self.create_languages_section(main_container)
        
        # Actions section
        self.create_actions_section(main_container)
        
        # Output section
        self.create_output_section(main_container)
    
    def create_project_section(self, parent):
        """Project selection with modern cards"""
        section = ctk.CTkFrame(parent, corner_radius=15)
        section.pack(fill="x", pady=(0, 15))
        
        # Header
        header = ctk.CTkLabel(
            section,
            text="📁  Project Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Content frame
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 15))
        
        # Project path display
        self.project_label = ctk.CTkLabel(
            content,
            text="No project selected",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        )
        self.project_label.pack(side="left", padx=(0, 15))
        
        # Browse button with hover effect
        browse_btn = ctk.CTkButton(
            content,
            text="📂  Browse Project",
            command=self.select_project,
            width=180,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        browse_btn.pack(side="left")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            section,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 15))
    
    def create_languages_section(self, parent):
        """Modern language selection grid"""
        section = ctk.CTkFrame(parent, corner_radius=15)
        section.pack(fill="both", expand=True, pady=(0, 15))
        
        # Header
        header = ctk.CTkLabel(
            section,
            text="🌍  Target Languages",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(15, 5))
        
        hint = ctk.CTkLabel(
            section,
            text="English is the source language (always included)",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        hint.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Scrollable language grid
        scroll_frame = ctk.CTkScrollableFrame(section, height=200)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Configure grid
        self.language_vars = {}
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        
        row, col = 0, 0
        for code, name in sorted_langs:
            var = ctk.BooleanVar(value=(code == 'en'))
            
            # Modern checkbox with icon
            cb = ctk.CTkCheckBox(
                scroll_frame,
                text=f"{name}  ({code})",
                variable=var,
                command=self.update_selected_languages,
                font=ctk.CTkFont(size=12),
                checkbox_width=22,
                checkbox_height=22,
                corner_radius=6
            )
            cb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            
            if code == 'en':
                cb.configure(state="disabled")
            
            self.language_vars[code] = var
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Selection counter
        self.lang_count_label = ctk.CTkLabel(
            section,
            text="Selected: 1 language (English)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#3b82f6", "#60a5fa")
        )
        self.lang_count_label.pack(anchor="w", padx=20, pady=(0, 15))
    
    def create_actions_section(self, parent):
        """Action buttons with modern styling"""
        section = ctk.CTkFrame(parent, corner_radius=15)
        section.pack(fill="x", pady=(0, 15))
        
        # Header
        header = ctk.CTkLabel(
            section,
            text="⚡  Actions",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Main workflow button (large, prominent)
        self.workflow_btn = ctk.CTkButton(
            section,
            text="🚀  Run Complete Workflow",
            command=self.run_complete_workflow,
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#2563eb", "#1d4ed8"),
            state="disabled"
        )
        self.workflow_btn.pack(fill="x", padx=20, pady=(0, 15))
        
        # Divider
        divider = ctk.CTkFrame(section, height=2, fg_color=("gray80", "gray30"))
        divider.pack(fill="x", padx=20, pady=10)
        
        # Individual steps label
        steps_label = ctk.CTkLabel(
            section,
            text="Or run individual steps:",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        steps_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Steps grid
        steps_frame = ctk.CTkFrame(section, fg_color="transparent")
        steps_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.detect_btn = ctk.CTkButton(
            steps_frame,
            text="1️⃣  Detect Text",
            command=self.run_detect,
            width=280,
            height=38,
            corner_radius=8,
            state="disabled"
        )
        self.detect_btn.grid(row=0, column=0, padx=5, pady=2)
        
        self.generate_btn = ctk.CTkButton(
            steps_frame,
            text="2️⃣  Generate Keys",
            command=self.run_generate,
            width=280,
            height=38,
            corner_radius=8,
            state="disabled"
        )
        self.generate_btn.grid(row=0, column=1, padx=5, pady=2)
        
        self.translate_btn = ctk.CTkButton(
            steps_frame,
            text="3️⃣  Translate",
            command=self.run_translate,
            width=280,
            height=38,
            corner_radius=8,
            state="disabled"
        )
        self.translate_btn.grid(row=1, column=0, padx=5, pady=2)
        
        self.replace_btn = ctk.CTkButton(
            steps_frame,
            text="4️⃣  Replace Code",
            command=self.run_replace,
            width=280,
            height=38,
            corner_radius=8,
            state="disabled"
        )
        self.replace_btn.grid(row=1, column=1, padx=5, pady=2)
    
    def create_output_section(self, parent):
        """Modern output console"""
        section = ctk.CTkFrame(parent, corner_radius=15)
        section.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkLabel(
            section,
            text="📊  Console Output",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(section, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Output text box
        self.output_text = ctk.CTkTextbox(
            section,
            height=250,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=("#f8f9fa", "#1a1a1a"),
            border_width=2,
            border_color=("gray70", "gray35")
        )
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Welcome message
        self.log("🎉 Welcome to i18n Manager!\n")
        self.log("Select a React/TypeScript project to begin.\n", "info")
    
    # ===== Core Functionality =====
    
    def select_project(self):
        """Select project folder"""
        folder = filedialog.askdirectory(title="Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_label.configure(text=str(self.project_path), text_color=("#3b82f6", "#60a5fa"))
        
        self.log(f"\n📁 Selected project: {self.project_path.name}\n", "header")
        self.detect_project_setup()
    
    def detect_project_setup(self):
        """Detect i18n configuration"""
        # Find source directory
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = self.project_path / src_name
            if src_path.exists():
                self.src_dir = src_path
                self.log(f"✓ Found source: {src_name}/\n", "success")
                break
        
        if not self.src_dir:
            self.log("⚠ No source directory found\n", "warning")
            self.status_label.configure(text="❌ No src/ directory found", text_color="#ef4444")
            return
        
        # Check i18n setup
        i18n_config = self.src_dir / 'i18n' / 'config.ts'
        locales_dir = self.src_dir / 'i18n' / 'locales'
        
        self.has_i18n_setup = i18n_config.exists() and locales_dir.exists()
        
        if self.has_i18n_setup:
            self.locales_dir = locales_dir
            self.log("✓ i18n is configured\n", "success")
            self.status_label.configure(text="✅ Ready to use", text_color="#10b981")
            
            # Detect languages
            existing = [f.stem for f in locales_dir.glob('*.json') if f.stem not in ('index', 'config')]
            if existing:
                self.log(f"✓ Found languages: {', '.join(existing)}\n", "success")
                for lang in existing:
                    if lang in self.language_vars:
                        self.language_vars[lang].set(True)
                self.update_selected_languages()
            
            # Enable buttons
            self.workflow_btn.configure(state="normal")
            self.detect_btn.configure(state="normal")
        else:
            self.log("⚠ i18n not configured\n", "warning")
            self.status_label.configure(text="⚠️ Needs setup", text_color="#f59e0b")
            self.offer_i18n_setup()
    
    def offer_i18n_setup(self):
        """Offer setup wizard"""
        response = messagebox.askyesno(
            "Setup i18n?",
            "This project doesn't have i18n configured.\n\n"
            "Would you like to set it up now?\n\n"
            "This will create:\n"
            "• i18n configuration files\n"
            "• Translation directory structure\n"
            "• Initial language files"
        )
        
        if response:
            self.create_i18n_setup()
    
    def create_i18n_setup(self):
        """Create i18n files"""
        try:
            i18n_dir = self.src_dir / 'i18n'
            locales_dir = i18n_dir / 'locales'
            locales_dir.mkdir(parents=True, exist_ok=True)
            
            # Config file
            config_content = '''import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';

i18n.use(initReactI18next).init({
  resources: { en: { translation: en } },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }
});

export default i18n;
'''
            (i18n_dir / 'config.ts').write_text(config_content, encoding='utf-8')
            
            # Initial locale files
            structure = {"common": {}, "nav": {}, "button": {}, "form": {}, "message": {}}
            for lang in self.selected_languages:
                with open(locales_dir / f'{lang}.json', 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=2, ensure_ascii=False)
            
            # Index file
            (i18n_dir / 'index.ts').write_text("export { default } from './config';\n", encoding='utf-8')
            
            self.log("✅ i18n setup complete!\n", "success")
            self.has_i18n_setup = True
            self.locales_dir = locales_dir
            self.status_label.configure(text="✅ Ready to use", text_color="#10b981")
            self.workflow_btn.configure(state="normal")
            self.detect_btn.configure(state="normal")
            
            messagebox.showinfo(
                "Setup Complete!",
                "i18n configured successfully!\n\n"
                "Next steps:\n"
                "1. Run 'npm install react-i18next i18next'\n"
                "2. Import './i18n' in your App.tsx\n"
                "3. Use the workflow to detect text"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Setup failed:\n{str(e)}")
    
    def update_selected_languages(self):
        """Update language selection"""
        self.selected_languages = ['en']
        for code, var in self.language_vars.items():
            if var.get() and code != 'en':
                self.selected_languages.append(code)
        
        count = len(self.selected_languages)
        langs_text = ', '.join([self.SUPPORTED_LANGUAGES[code] for code in self.selected_languages[:3]])
        if count > 3:
            langs_text += f", +{count-3} more"
        
        self.lang_count_label.configure(text=f"Selected: {count} language{'s' if count > 1 else ''} ({langs_text})")
    
    # ===== Detection =====
    
    def detect_hardcoded_text(self, source_dir: Path) -> List[Dict]:
        """Detect hardcoded strings"""
        findings = []
        for tsx_file in source_dir.rglob('*.tsx'):
            if any(ex in tsx_file.parts for ex in ['node_modules', 'dist', 'build', '.git']):
                continue
            
            try:
                content = tsx_file.read_text(encoding='utf-8')
                findings.extend(self._scan_file(content, tsx_file))
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
        if len(text) < 4 or len(text) > 150 or not text[0].isupper():
            return False
        
        for pattern in self.TECHNICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        alpha_chars = sum(c.isalpha() for c in text)
        return alpha_chars >= len(text) * 0.5
    
    # ===== Key Generation =====
    
    def generate_translation_keys(self, strings: List[Dict]) -> Dict[str, Dict]:
        """Generate keys from strings"""
        mapping = {}
        used_keys = set()
        
        for string_info in strings:
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
    
    # ===== Translation =====
    
    def translate_keys_to_languages(self, keys_mapping: Dict, languages: List[str]):
        """Translate to languages"""
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
                
                if lang == 'en':
                    data[section][key_name] = text
                else:
                    data[section][key_name] = f'[EN] {text}'
            
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Translate non-English
        for lang in languages:
            if lang != 'en':
                self.log(f"  🌍 Translating to {self.SUPPORTED_LANGUAGES[lang]}...\n", "info")
                self._translate_file(self.locales_dir / f'{lang}.json', lang)
    
    def _translate_file(self, filepath: Path, target_lang: str):
        """Translate file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated = self._translate_dict(data, target_lang)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translated, f, indent=2, ensure_ascii=False)
    
    def _translate_dict(self, data: dict, target_lang: str) -> dict:
        """Recursively translate dict"""
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._translate_dict(value, target_lang)
            elif isinstance(value, str) and value.startswith('[EN] '):
                original = value[5:]
                try:
                    translator = GoogleTranslator(source='en', target=target_lang)
                    result[key] = translator.translate(original)
                except:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    # ===== Code Replacement =====
    
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
        
        modified_count = 0
        
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
            
            if modified_content != content:
                filepath.write_text(modified_content, encoding='utf-8')
                modified_count += 1
        
        self.log(f"✓ Modified {modified_count} files\n", "success")
        self.log(f"📁 Backups: {backup_dir}\n", "info")
    
    def _add_i18n_import(self, content: str) -> str:
        """Add import and hook"""
        import_pattern = r"(import\s+.*from\s+['\"]react['\"];?\n)"
        match = re.search(import_pattern, content)
        
        import_line = "import { useTranslation } from 'react-i18next';\n"
        
        if match:
            pos = match.end()
            content = content[:pos] + import_line + content[pos:]
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
        
        replacements = {
            'jsx_text_node': (f'>{text_escaped}<', f'>{{t("{key}")}}<'),
            'title_attr': (f'title=["\']({text_escaped})["\']', f'title={{t("{key}")}}'),
            'placeholder_attr': (f'placeholder=["\']({text_escaped})["\']', f'placeholder={{t("{key}")}}'),
        }
        
        if context in replacements:
            pattern, replacement = replacements[context]
            content = re.sub(pattern, replacement, content)
        
        return content
    
    # ===== Workflow Actions =====
    
    def run_detect(self):
        """Detect step"""
        if not self.validate_project():
            return
        
        self.log("\n" + "="*60 + "\n", "header")
        self.log("🔍 Step 1: Detecting hardcoded text...\n", "info")
        self.progress_bar.start()
        self.detect_btn.configure(state="disabled")
        
        def worker():
            try:
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                
                self.log(f"✅ Found {len(strings)} hardcoded strings\n", "success")
                
                if strings:
                    self.generate_btn.configure(state="normal")
                    self.log("\nPreview (first 10):\n", "info")
                    for i, s in enumerate(strings[:10], 1):
                        file_name = Path(s['file']).name
                        self.log(f"  {i}. {file_name}:{s['line']} - \"{s['text'][:50]}\"\n")
                else:
                    self.log("No hardcoded text detected.\n", "info")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n", "error")
            finally:
                self.progress_bar.stop()
                self.detect_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_generate(self):
        """Generate keys step"""
        if not self.detected_strings:
            messagebox.showwarning("No Data", "Run detection first!")
            return
        
        self.log("\n" + "="*60 + "\n", "header")
        self.log("🔑 Step 2: Generating translation keys...\n", "info")
        self.progress_bar.start()
        self.generate_btn.configure(state="disabled")
        
        def worker():
            try:
                mapping = self.generate_translation_keys(self.detected_strings)
                self.generated_keys = mapping
                
                self.log(f"✅ Generated {len(mapping)} translation keys\n", "success")
                
                sections = defaultdict(int)
                for key in mapping.keys():
                    section = key.split('.')[0]
                    sections[section] += 1
                
                self.log("\nKeys by section:\n", "info")
                for section, count in sorted(sections.items()):
                    self.log(f"  • {section}: {count} keys\n")
                
                self.translate_btn.configure(state="normal")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n", "error")
            finally:
                self.progress_bar.stop()
                self.generate_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_translate(self):
        """Translate step"""
        if not self.generated_keys:
            messagebox.showwarning("No Data", "Run key generation first!")
            return
        
        self.log("\n" + "="*60 + "\n", "header")
        self.log("🌍 Step 3: Translating to languages...\n", "info")
        self.log("⏳ This may take a few minutes...\n", "warning")
        self.progress_bar.start()
        self.translate_btn.configure(state="disabled")
        
        def worker():
            try:
                self.translate_keys_to_languages(
                    self.generated_keys,
                    self.selected_languages
                )
                
                self.log(f"✅ Translated to {len(self.selected_languages)} languages\n", "success")
                self.replace_btn.configure(state="normal")
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n", "error")
            finally:
                self.progress_bar.stop()
                self.translate_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_replace(self):
        """Replace step"""
        if not self.generated_keys:
            messagebox.showwarning("No Data", "Run previous steps first!")
            return
        
        file_count = len(set(info['file'] for info in self.generated_keys.values()))
        response = messagebox.askyesno(
            "Confirm Changes",
            f"This will modify {file_count} source files.\n\n"
            "Backups will be created automatically.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        self.log("\n" + "="*60 + "\n", "header")
        self.log("✏️ Step 4: Replacing hardcoded text...\n", "info")
        self.progress_bar.start()
        self.replace_btn.configure(state="disabled")
        
        def worker():
            try:
                self.replace_in_source_code(self.generated_keys)
                
                self.log("✅ Code replacement complete!\n", "success")
                
                messagebox.showinfo(
                    "Complete!",
                    f"Workflow finished! 🎉\n\n"
                    f"• {len(self.detected_strings)} strings detected\n"
                    f"• {len(self.generated_keys)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    "Your code now uses i18n!"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n", "error")
            finally:
                self.progress_bar.stop()
                self.replace_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_complete_workflow(self):
        """Run all steps"""
        if not self.validate_project():
            return
        
        response = messagebox.askyesno(
            "Run Complete Workflow",
            f"This will:\n"
            f"1. Detect all hardcoded text\n"
            f"2. Generate translation keys\n"
            f"3. Translate to {len(self.selected_languages)} languages\n"
            f"4. Update your source code\n\n"
            f"Backups will be created.\n"
            f"This may take several minutes.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        self.log("\n" + "="*60 + "\n", "header")
        self.log("🚀 Running complete workflow...\n", "header")
        self.log("="*60 + "\n", "header")
        
        # Disable all buttons
        self.workflow_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self.generate_btn.configure(state="disabled")
        self.translate_btn.configure(state="disabled")
        self.replace_btn.configure(state="disabled")
        
        def worker():
            try:
                self.progress_bar.start()
                
                # Step 1
                self.log("\n🔍 Step 1/4: Detecting...\n", "info")
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                self.log(f"  ✓ Found {len(strings)} strings\n", "success")
                
                if not strings:
                    self.log("No hardcoded text to process.\n", "info")
                    return
                
                # Step 2
                self.log("\n🔑 Step 2/4: Generating keys...\n", "info")
                mapping = self.generate_translation_keys(strings)
                self.generated_keys = mapping
                self.log(f"  ✓ Generated {len(mapping)} keys\n", "success")
                
                # Step 3
                self.log("\n🌍 Step 3/4: Translating...\n", "info")
                self.translate_keys_to_languages(mapping, self.selected_languages)
                self.log(f"  ✓ Translated to {len(self.selected_languages)} languages\n", "success")
                
                # Step 4
                self.log("\n✏️ Step 4/4: Updating code...\n", "info")
                self.replace_in_source_code(mapping)
                self.log("  ✓ Code updated\n", "success")
                
                self.log("\n" + "="*60 + "\n", "header")
                self.log("🎉 Workflow complete!\n", "success")
                self.log("="*60 + "\n", "header")
                
                messagebox.showinfo(
                    "Success!",
                    f"Complete workflow finished! 🎉\n\n"
                    f"• {len(strings)} strings detected\n"
                    f"• {len(mapping)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    f"Your project is now internationalized!"
                )
                
            except Exception as e:
                self.log(f"\n❌ Workflow failed: {str(e)}\n", "error")
                messagebox.showerror("Error", f"Workflow failed:\n{str(e)}")
            finally:
                self.progress_bar.stop()
                self.workflow_btn.configure(state="normal")
                self.detect_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    # ===== Helpers =====
    
    def validate_project(self):
        """Validate project setup"""
        if not self.project_path:
            messagebox.showerror("Error", "Select a project first!")
            return False
        
        if not self.has_i18n_setup:
            messagebox.showerror("Error", "Setup i18n first!")
            return False
        
        return True
    
    def log(self, message, tag=None):
        """Add message to console"""
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.root.update()
    
    def load_settings(self):
        """Load saved settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                if 'languages' in settings:
                    for lang in settings['languages']:
                        if lang in self.language_vars:
                            self.language_vars[lang].set(True)
                    self.update_selected_languages()
            except:
                pass
    
    def save_settings(self):
        """Save settings"""
        settings = {
            'last_project': str(self.project_path) if self.project_path else None,
            'languages': self.selected_languages
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def run(self):
        """Start application"""
        def on_closing():
            self.save_settings()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()


def main():
    """Main entry point"""
    app = I18nManagerApp()
    app.run()


if __name__ == '__main__':
    main()
