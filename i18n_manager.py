#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Windows 11 Glass Edition
Stunning liquid glass design with real-time progress
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
import time

# Windows 11 Acrylic theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Auto-install dependencies
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class I18nManagerApp:
    """Windows 11 Glass-style i18n Manager with real-time progress"""
    
    # Windows 11 Blue Glass Theme
    COLORS = {
        'bg_app': '#0d1117',
        'bg_surface': '#161b22',
        'bg_card': '#1c2128',
        'accent': '#0078d4',
        'accent_hover': '#106ebe',
        'border': '#30363d',
        'text': '#ffffff',
        'text_muted': '#8b949e',
        'success': '#3fb950',
        'warning': '#d29922',
        'error': '#f85149',
    }
    
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'nl': 'Dutch', 'de': 'German', 'fr': 'French',
        'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese', 'ro': 'Romanian',
        'ru': 'Russian', 'cs': 'Czech', 'pl': 'Polish', 'el': 'Greek',
        'tr': 'Turkish', 'ar': 'Arabic', 'ja': 'Japanese', 'ko': 'Korean',
        'zh': 'Chinese', 'hi': 'Hindi', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish',
    }
    
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
        # Main window - Horizontal layout
        self.root = ctk.CTk()
        self.root.title("i18n Manager")
        self.root.geometry("1400x750")  # Wider, less tall
        
        # Configure colors
        self.root.configure(fg_color=self.COLORS['bg_app'])
        
        # Tool directory
        self.tool_dir = Path(__file__).parent
        self.backups_dir = self.tool_dir / '.backups'
        self.temp_dir = self.tool_dir / '.temp'
        self.settings_file = self.tool_dir / 'user_settings.json'
        
        self.backups_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # State
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
        width = 1400
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create Windows 11 Glass UI - Horizontal Layout"""
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === TOP: Glass Title Bar ===
        title_bar = ctk.CTkFrame(
            main_container,
            height=70,
            corner_radius=15,
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border']
        )
        title_bar.pack(fill="x", pady=(0, 12))
        title_bar.pack_propagate(False)
        
        # Title with icon
        title_label = ctk.CTkLabel(
            title_bar,
            text="🌍  i18n Manager",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.COLORS['text']
        )
        title_label.pack(side="left", padx=25, pady=15)
        
        subtitle = ctk.CTkLabel(
            title_bar,
            text="Universal Translation Automation",
            font=ctk.CTkFont(size=13),
            text_color=self.COLORS['text_muted']
        )
        subtitle.pack(side="left", pady=15)
        
        # === MIDDLE: Horizontal Split (Left: Controls, Right: Console) ===
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # LEFT PANEL: Controls (40% width)
        left_panel = ctk.CTkFrame(
            content_frame,
            corner_radius=15,
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border']
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        # RIGHT PANEL: Console & Progress (60% width)
        right_panel = ctk.CTkFrame(
            content_frame,
            corner_radius=15,
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border']
        )
        right_panel.pack(side="right", fill="both", expand=True, padx=(8, 0))
        
        # Build left panel (Project, Languages, Actions)
        self.create_left_panel(left_panel)
        
        # Build right panel (Console, Progress)
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """Left panel with controls"""
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['accent'],
            scrollbar_button_hover_color=self.COLORS['accent_hover']
        )
        scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # === PROJECT SECTION ===
        self.create_section_header(scroll, "📁", "Project")
        
        self.project_label = ctk.CTkLabel(
            scroll,
            text="No project selected",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS['text_muted'],
            anchor="w"
        )
        self.project_label.pack(fill="x", pady=(0, 8))
        
        browse_btn = ctk.CTkButton(
            scroll,
            text="📂  Browse Project Folder",
            command=self.select_project,
            height=40,
            corner_radius=10,
            fg_color=self.COLORS['accent'],
            hover_color=self.COLORS['accent_hover'],
            font=ctk.CTkFont(size=13, weight="bold")
        )
        browse_btn.pack(fill="x", pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['text_muted']
        )
        self.status_label.pack(fill="x", pady=(0, 20))
        
        # === LANGUAGES SECTION ===
        self.create_section_header(scroll, "🌍", "Target Languages")
        
        hint = ctk.CTkLabel(
            scroll,
            text="English is always included as source",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_muted']
        )
        hint.pack(anchor="w", pady=(0, 8))
        
        # Language grid in scrollable sub-frame
        lang_frame = ctk.CTkFrame(scroll, fg_color=self.COLORS['bg_card'], corner_radius=8)
        lang_frame.pack(fill="x", pady=(0, 5))
        
        self.language_vars = {}
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        
        row, col = 0, 0
        for code, name in sorted_langs:
            var = ctk.BooleanVar(value=(code == 'en'))
            
            cb = ctk.CTkCheckBox(
                lang_frame,
                text=f"{name}",
                variable=var,
                command=self.update_selected_languages,
                font=ctk.CTkFont(size=11),
                checkbox_width=20,
                checkbox_height=20,
                corner_radius=5,
                fg_color=self.COLORS['accent'],
                hover_color=self.COLORS['accent_hover']
            )
            cb.grid(row=row, column=col, padx=8, pady=4, sticky="w")
            
            if code == 'en':
                cb.configure(state="disabled")
            
            self.language_vars[code] = var
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        self.lang_count_label = ctk.CTkLabel(
            scroll,
            text="Selected: 1 language",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.COLORS['success']
        )
        self.lang_count_label.pack(anchor="w", pady=(5, 20))
        
        # === ACTIONS SECTION ===
        self.create_section_header(scroll, "⚡", "Actions")
        
        # Main workflow button
        self.workflow_btn = ctk.CTkButton(
            scroll,
            text="🚀  Run Complete Workflow",
            command=self.run_complete_workflow,
            height=50,
            corner_radius=10,
            fg_color=self.COLORS['accent'],
            hover_color=self.COLORS['accent_hover'],
            font=ctk.CTkFont(size=15, weight="bold"),
            state="disabled"
        )
        self.workflow_btn.pack(fill="x", pady=(0, 15))
        
        # Separator
        sep = ctk.CTkFrame(scroll, height=1, fg_color=self.COLORS['border'])
        sep.pack(fill="x", pady=10)
        
        step_label = ctk.CTkLabel(
            scroll,
            text="Or run individual steps:",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['text_muted']
        )
        step_label.pack(anchor="w", pady=(0, 8))
        
        # Step buttons
        self.detect_btn = self.create_step_btn(scroll, "1️⃣  Detect Text", self.run_detect)
        self.generate_btn = self.create_step_btn(scroll, "2️⃣  Generate Keys", self.run_generate)
        self.translate_btn = self.create_step_btn(scroll, "3️⃣  Auto-Translate", self.run_translate)
        self.replace_btn = self.create_step_btn(scroll, "4️⃣  Update Code", self.run_replace)
    
    def create_right_panel(self, parent):
        """Right panel with console and progress"""
        # Header
        header = ctk.CTkLabel(
            parent,
            text="📊  Live Console & Progress",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS['text']
        )
        header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Current operation label
        self.current_operation = ctk.CTkLabel(
            parent,
            text="Ready to start",
            font=ctk.CTkFont(size=12),
            text_color=self.COLORS['text_muted']
        )
        self.current_operation.pack(anchor="w", padx=20, pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            parent,
            height=8,
            corner_radius=4,
            progress_color=self.COLORS['accent']
        )
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress percentage
        self.progress_label = ctk.CTkLabel(
            parent,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.COLORS['text_muted']
        )
        self.progress_label.pack(anchor="e", padx=20, pady=(0, 10))
        
        # Console output
        self.output_text = ctk.CTkTextbox(
            parent,
            corner_radius=10,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border'],
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Welcome message
        self.log("🎉 Welcome to i18n Manager!\n")
        self.log("═" * 50 + "\n")
        self.log("Select a React/TypeScript project to begin.\n\n")
        self.log("💡 Tip: The console will show real-time progress\n")
        self.log("   as operations are performed.\n")
    
    def create_section_header(self, parent, icon, text):
        """Create a section header"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))
        
        label = ctk.CTkLabel(
            frame,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLORS['text']
        )
        label.pack(side="left")
    
    def create_step_btn(self, parent, text, command):
        """Create a step button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=36,
            corner_radius=8,
            fg_color=self.COLORS['bg_card'],
            hover_color=self.COLORS['border'],
            border_width=1,
            border_color=self.COLORS['border'],
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        btn.pack(fill="x", pady=3)
        return btn
    
    # ===== UI Helpers =====
    
    def update_progress(self, value: float, operation: str = None):
        """Update progress bar with percentage"""
        self.progress_bar.set(value)
        self.progress_label.configure(text=f"{int(value * 100)}%")
        if operation:
            self.current_operation.configure(text=operation)
        self.root.update()
    
    def log(self, message: str, level: str = "info"):
        """Log message with color coding"""
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.root.update()
    
    # ===== Core Functionality =====
    
    def select_project(self):
        """Select project folder"""
        folder = filedialog.askdirectory(title="Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_label.configure(
            text=str(self.project_path),
            text_color=self.COLORS['accent']
        )
        
        self.log(f"\n{'═' * 50}\n")
        self.log(f"📁 PROJECT SELECTED\n")
        self.log(f"{'═' * 50}\n")
        self.log(f"Path: {self.project_path}\n\n")
        
        self.update_progress(0.1, "Detecting project structure...")
        self.detect_project_setup()
    
    def detect_project_setup(self):
        """Detect i18n configuration"""
        # Find source directory
        self.log("🔍 Scanning project structure...\n")
        
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = self.project_path / src_name
            if src_path.exists():
                self.src_dir = src_path
                self.log(f"  ✓ Found source directory: {src_name}/\n")
                break
        
        if not self.src_dir:
            self.log("  ❌ No source directory found\n", "error")
            self.status_label.configure(
                text="❌ No src/ directory",
                text_color=self.COLORS['error']
            )
            self.update_progress(0, "Error: No source directory")
            return
        
        # Check i18n setup
        i18n_config = self.src_dir / 'i18n' / 'config.ts'
        locales_dir = self.src_dir / 'i18n' / 'locales'
        
        self.has_i18n_setup = i18n_config.exists() and locales_dir.exists()
        
        if self.has_i18n_setup:
            self.locales_dir = locales_dir
            self.log("  ✓ i18n is configured\n")
            self.status_label.configure(
                text="✅ Ready to process",
                text_color=self.COLORS['success']
            )
            
            # Detect languages
            existing = [f.stem for f in locales_dir.glob('*.json') 
                       if f.stem not in ('index', 'config')]
            if existing:
                self.log(f"  ✓ Found {len(existing)} languages: {', '.join(existing)}\n")
                for lang in existing:
                    if lang in self.language_vars:
                        self.language_vars[lang].set(True)
                self.update_selected_languages()
            
            self.workflow_btn.configure(state="normal")
            self.detect_btn.configure(state="normal")
            self.update_progress(1.0, "Ready to start workflow")
        else:
            self.log("  ⚠️ i18n not configured\n")
            self.status_label.configure(
                text="⚠️ Setup required",
                text_color=self.COLORS['warning']
            )
            self.update_progress(0.5, "Needs i18n setup")
            self.offer_i18n_setup()
    
    def offer_i18n_setup(self):
        """Offer setup wizard"""
        response = messagebox.askyesno(
            "Setup i18n?",
            "This project doesn't have i18n configured.\n\n"
            "Would you like to set it up now?"
        )
        
        if response:
            self.create_i18n_setup()
    
    def create_i18n_setup(self):
        """Create i18n files"""
        try:
            self.log("\n🔧 Setting up i18n...\n")
            self.update_progress(0.3, "Creating i18n structure...")
            
            i18n_dir = self.src_dir / 'i18n'
            locales_dir = i18n_dir / 'locales'
            locales_dir.mkdir(parents=True, exist_ok=True)
            
            self.log("  ✓ Created directories\n")
            self.update_progress(0.5, "Creating config files...")
            
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
            self.log("  ✓ Created config.ts\n")
            
            self.update_progress(0.7, "Creating language files...")
            
            # Initial locale files
            structure = {"common": {}, "nav": {}, "button": {}, "form": {}, "message": {}}
            for lang in self.selected_languages:
                with open(locales_dir / f'{lang}.json', 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=2, ensure_ascii=False)
            
            self.log(f"  ✓ Created {len(self.selected_languages)} language file(s)\n")
            
            # Index file
            (i18n_dir / 'index.ts').write_text("export { default } from './config';\n", encoding='utf-8')
            
            self.update_progress(1.0, "Setup complete!")
            self.log("✅ i18n setup complete!\n\n")
            
            self.has_i18n_setup = True
            self.locales_dir = locales_dir
            self.status_label.configure(
                text="✅ Ready to process",
                text_color=self.COLORS['success']
            )
            self.workflow_btn.configure(state="normal")
            self.detect_btn.configure(state="normal")
            
            messagebox.showinfo(
                "Setup Complete!",
                "i18n configured successfully!\n\n"
                "Next steps:\n"
                "1. Run 'npm install react-i18next i18next'\n"
                "2. Import './i18n' in your App.tsx"
            )
        except Exception as e:
            self.log(f"❌ Setup failed: {str(e)}\n")
            self.update_progress(0, "Setup failed")
            messagebox.showerror("Error", f"Setup failed:\n{str(e)}")
    
    def update_selected_languages(self):
        """Update language selection"""
        self.selected_languages = ['en']
        for code, var in self.language_vars.items():
            if var.get() and code != 'en':
                self.selected_languages.append(code)
        
        count = len(self.selected_languages)
        self.lang_count_label.configure(text=f"Selected: {count} language(s)")
    
    # ===== Detection =====
    
    def detect_hardcoded_text(self, source_dir: Path) -> List[Dict]:
        """Detect hardcoded strings with progress"""
        findings = []
        files = list(source_dir.rglob('*.tsx'))
        files = [f for f in files if not any(ex in f.parts for ex in 
                ['node_modules', 'dist', 'build', '.git'])]
        
        total = len(files)
        self.log(f"  Scanning {total} files...\n")
        
        for idx, tsx_file in enumerate(files, 1):
            try:
                content = tsx_file.read_text(encoding='utf-8')
                file_findings = self._scan_file(content, tsx_file)
                findings.extend(file_findings)
                
                # Update progress
                progress = idx / total
                self.update_progress(progress, f"Scanning file {idx}/{total}...")
                
                if file_findings:
                    self.log(f"  ✓ {tsx_file.name}: {len(file_findings)} strings\n")
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
        """Generate keys from strings with progress"""
        mapping = {}
        used_keys = set()
        
        total = len(strings)
        self.log(f"  Generating {total} translation keys...\n")
        
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
            
            # Update progress every 10 keys
            if idx % 10 == 0 or idx == total:
                progress = idx / total
                self.update_progress(progress, f"Generating keys: {idx}/{total}")
        
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
        """Translate to languages with progress"""
        total_langs = len(languages)
        
        for idx, lang in enumerate(languages, 1):
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
            
            progress = idx / total_langs
            self.update_progress(progress, f"Processing language {idx}/{total_langs}")
        
        # Translate non-English
        non_en = [l for l in languages if l != 'en']
        if non_en:
            self.log(f"\n🌍 Translating to {len(non_en)} language(s)...\n")
            
            for idx, lang in enumerate(non_en, 1):
                self.log(f"  → {self.SUPPORTED_LANGUAGES[lang]}...\n")
                self.update_progress(idx / len(non_en), 
                                   f"Translating to {self.SUPPORTED_LANGUAGES[lang]}")
                self._translate_file(self.locales_dir / f'{lang}.json', lang)
                self.log(f"    ✓ Complete\n")
    
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
                    time.sleep(0.1)  # Rate limiting
                except:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    # ===== Code Replacement =====
    
    def replace_in_source_code(self, keys_mapping: Dict):
        """Replace hardcoded text in code with progress"""
        backup_dir = self.backups_dir / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"📁 Creating backups in: {backup_dir.name}\n")
        
        files_map = defaultdict(list)
        for full_key, info in keys_mapping.items():
            files_map[info['file']].append({
                'key': full_key,
                'text': info['text'],
                'context': info['context']
            })
        
        total = len(files_map)
        modified_count = 0
        
        for idx, (filepath, replacements) in enumerate(files_map.items(), 1):
            filepath = Path(filepath)
            
            self.update_progress(idx / total, f"Updating file {idx}/{total}...")
            
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
                self.log(f"  ✓ {filepath.name}\n")
        
        self.log(f"\n✅ Modified {modified_count} file(s)\n")
    
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
        
        self.log("\n" + "═"*50 + "\n")
        self.log("STEP 1: DETECTING HARDCODED TEXT\n")
        self.log("═"*50 + "\n")
        self.detect_btn.configure(state="disabled")
        
        def worker():
            try:
                self.update_progress(0.1, "Starting detection...")
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                
                self.log(f"\n✅ Found {len(strings)} hardcoded strings\n\n")
                
                if strings:
                    self.generate_btn.configure(state="normal")
                    self.log("Preview (first 5):\n")
                    for i, s in enumerate(strings[:5], 1):
                        file_name = Path(s['file']).name
                        self.log(f"  {i}. {file_name}:{s['line']}\n")
                        self.log(f"     \"{s['text'][:60]}...\"\n")
                else:
                    self.log("ℹ️  No hardcoded text detected.\n")
                
                self.update_progress(1.0, "Detection complete")
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n")
                self.update_progress(0, "Error occurred")
            finally:
                self.detect_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_generate(self):
        """Generate keys step"""
        if not self.detected_strings:
            messagebox.showwarning("No Data", "Run detection first!")
            return
        
        self.log("\n" + "═"*50 + "\n")
        self.log("STEP 2: GENERATING TRANSLATION KEYS\n")
        self.log("═"*50 + "\n")
        self.generate_btn.configure(state="disabled")
        
        def worker():
            try:
                self.update_progress(0.1, "Starting key generation...")
                mapping = self.generate_translation_keys(self.detected_strings)
                self.generated_keys = mapping
                
                self.log(f"\n✅ Generated {len(mapping)} keys\n\n")
                
                sections = defaultdict(int)
                for key in mapping.keys():
                    section = key.split('.')[0]
                    sections[section] += 1
                
                self.log("Keys by section:\n")
                for section, count in sorted(sections.items()):
                    self.log(f"  • {section}: {count} keys\n")
                
                self.translate_btn.configure(state="normal")
                self.update_progress(1.0, "Key generation complete")
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n")
                self.update_progress(0, "Error occurred")
            finally:
                self.generate_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_translate(self):
        """Translate step"""
        if not self.generated_keys:
            messagebox.showwarning("No Data", "Run key generation first!")
            return
        
        self.log("\n" + "═"*50 + "\n")
        self.log("STEP 3: AUTO-TRANSLATING\n")
        self.log("═"*50 + "\n")
        self.log("⏳ This may take a few minutes...\n\n")
        self.translate_btn.configure(state="disabled")
        
        def worker():
            try:
                self.update_progress(0.1, "Starting translation...")
                self.translate_keys_to_languages(
                    self.generated_keys,
                    self.selected_languages
                )
                
                self.log(f"\n✅ Translated to {len(self.selected_languages)} language(s)\n")
                self.replace_btn.configure(state="normal")
                self.update_progress(1.0, "Translation complete")
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n")
                self.update_progress(0, "Error occurred")
            finally:
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
        
        self.log("\n" + "═"*50 + "\n")
        self.log("STEP 4: UPDATING SOURCE CODE\n")
        self.log("═"*50 + "\n")
        self.replace_btn.configure(state="disabled")
        
        def worker():
            try:
                self.update_progress(0.1, "Starting code updates...")
                self.replace_in_source_code(self.generated_keys)
                
                self.log("\n✅ Code replacement complete!\n")
                self.update_progress(1.0, "All done!")
                
                messagebox.showinfo(
                    "Complete!",
                    f"Workflow finished! 🎉\n\n"
                    f"• {len(self.detected_strings)} strings detected\n"
                    f"• {len(self.generated_keys)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    "Your code now uses i18n!"
                )
            except Exception as e:
                self.log(f"❌ Error: {str(e)}\n")
                self.update_progress(0, "Error occurred")
            finally:
                self.replace_btn.configure(state="normal")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_complete_workflow(self):
        """Run all steps with real-time progress"""
        if not self.validate_project():
            return
        
        response = messagebox.askyesno(
            "Run Complete Workflow",
            f"This will:\n"
            f"1. Detect all hardcoded text\n"
            f"2. Generate translation keys\n"
            f"3. Translate to {len(self.selected_languages)} languages\n"
            f"4. Update your source code\n\n"
            "Backups will be created.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        self.log("\n" + "═"*50 + "\n")
        self.log("🚀 COMPLETE WORKFLOW STARTING\n")
        self.log("═"*50 + "\n\n")
        
        # Disable all buttons
        self.workflow_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self.generate_btn.configure(state="disabled")
        self.translate_btn.configure(state="disabled")
        self.replace_btn.configure(state="disabled")
        
        def worker():
            try:
                # Step 1
                self.log("STEP 1/4: DETECTING TEXT\n")
                self.log("─" * 50 + "\n")
                self.update_progress(0.1, "Step 1/4: Detecting...")
                
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                self.log(f"✓ Found {len(strings)} strings\n\n")
                
                if not strings:
                    self.log("ℹ️  No hardcoded text to process.\n")
                    self.update_progress(1.0, "Nothing to process")
                    return
                
                # Step 2
                self.log("STEP 2/4: GENERATING KEYS\n")
                self.log("─" * 50 + "\n")
                self.update_progress(0.3, "Step 2/4: Generating keys...")
                
                mapping = self.generate_translation_keys(strings)
                self.generated_keys = mapping
                self.log(f"✓ Generated {len(mapping)} keys\n\n")
                
                # Step 3
                self.log("STEP 3/4: TRANSLATING\n")
                self.log("─" * 50 + "\n")
                self.update_progress(0.5, "Step 3/4: Translating...")
                
                self.translate_keys_to_languages(mapping, self.selected_languages)
                self.log(f"✓ Translated to {len(self.selected_languages)} languages\n\n")
                
                # Step 4
                self.log("STEP 4/4: UPDATING CODE\n")
                self.log("─" * 50 + "\n")
                self.update_progress(0.8, "Step 4/4: Updating code...")
                
                self.replace_in_source_code(mapping)
                self.log("✓ Code updated\n\n")
                
                self.log("═" * 50 + "\n")
                self.log("🎉 WORKFLOW COMPLETE!\n")
                self.log("═" * 50 + "\n")
                
                self.update_progress(1.0, "Workflow complete!")
                
                messagebox.showinfo(
                    "Success!",
                    f"Complete workflow finished! 🎉\n\n"
                    f"• {len(strings)} strings detected\n"
                    f"• {len(mapping)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    "Your project is now internationalized!"
                )
            except Exception as e:
                self.log(f"\n❌ Workflow failed: {str(e)}\n")
                self.update_progress(0, "Workflow failed")
                messagebox.showerror("Error", f"Workflow failed:\n{str(e)}")
            finally:
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
