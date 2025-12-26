#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Standalone Desktop Application
A modern, portable tool for managing translations in React/TypeScript projects
Completely self-contained - no CLI dependencies, fully portable
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import re
import shutil
from pathlib import Path
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import sys

# Auto-install dependencies if needed
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class I18nManagerApp:
    """Modern, standalone i18n Manager application"""
    
    # Modern color scheme
    COLORS = {
        'primary': '#2563eb',
        'primary_hover': '#1d4ed8',
        'success': '#10b981',
        'success_hover': '#059669',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'bg_dark': '#1f2937',
        'bg_light': '#f9fafb',
        'text_dark': '#111827',
        'text_light': '#6b7280'
    }
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'nl': 'Dutch (Nederlands)',
        'de': 'German (Deutsch)',
        'fr': 'French (Français)',
        'es': 'Spanish (Español)',
        'it': 'Italian (Italiano)',
        'pt': 'Portuguese (Português)',
        'ro': 'Romanian (Română)',
        'ru': 'Russian (Русский)',
        'cs': 'Czech (Čeština)',
        'pl': 'Polish (Polski)',
        'el': 'Greek (Ελληνικά)',
        'tr': 'Turkish (Türkçe)',
        'ar': 'Arabic (العربية)',
        'ja': 'Japanese (日本語)',
        'ko': 'Korean (한국어)',
        'zh': 'Chinese (中文)',
        'hi': 'Hindi (हिन्दी)',
        'sv': 'Swedish (Svenska)',
        'da': 'Danish (Dansk)',
        'no': 'Norwegian (Norsk)',
        'fi': 'Finnish (Suomi)',
    }
    
    # Safe detection contexts (whitelist)
    SAFE_CONTEXTS = {
        'jsx_text_node': r'>([A-Z][^<>{}]*?)<',
        'title_attr': r'title=["\'](.*?)["\']',
        'alt_attr': r'alt=["\'](.*?)["\']',
        'placeholder_attr': r'placeholder=["\'](.*?)["\']',
        'label_text': r'<label[^>]*>([^<]+)</label>',
        'button_text': r'<[Bb]utton[^>]*>([^<]+)</[Bb]utton>',
    }
    
    # Technical patterns to exclude
    TECHNICAL_PATTERNS = [
        r'^[a-z_]+$', r'^[A-Z_]+$', r'^[a-z][a-zA-Z0-9]*$',
        r'^/[a-zA-Z0-9/_-]*$', r'^\./|\.\./', r'className=',
        r'^(text|bg|border|flex|grid|gap|p|m|w|h|rounded|shadow)-',
        r'\.(jpg|jpeg|png|gif|svg|webp|mp4|pdf|json|xml|csv|tsx|jsx|ts|js|css|html)$',
        r'^https?://', r'^#[0-9a-fA-F]{3,8}$', r't\(["\']',
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("i18n Manager - Universal Translation Tool")
        self.root.geometry("1000x750")
        
        # Tool directory (portable)
        self.tool_dir = Path(__file__).parent
        self.backups_dir = self.tool_dir / '.backups'
        self.temp_dir = self.tool_dir / '.temp'
        self.settings_file = self.tool_dir / 'user_settings.json'
        
        # Create directories
        self.backups_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Project configuration (selected at runtime)
        self.project_path: Optional[Path] = None
        self.src_dir: Optional[Path] = None
        self.locales_dir: Optional[Path] = None
        self.selected_languages: List[str] = ['en']
        
        # Runtime state
        self.detected_strings: List[Dict] = []
        self.generated_keys: Dict[str, str] = {}
        self.has_i18n_setup = False
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.center_window()
        self.load_settings()
    
    def setup_styles(self):
        """Configure modern styles"""
        style = ttk.Style()
        
        # Try modern theme if available
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Custom button styles
        style.configure('Modern.TButton',
                       padding=10,
                       relief='flat',
                       font=('Segoe UI', 9))
        
        style.configure('Primary.TButton',
                       background=self.COLORS['primary'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', self.COLORS['primary_hover'])])
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create modern UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header with title and logo
        header_frame = tk.Frame(main_frame, bg=self.COLORS['primary'], height=80)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.grid_propagate(False)
        
        tk.Label(header_frame, text="🌍 i18n Manager",
                font=('Segoe UI', 20, 'bold'),
                bg=self.COLORS['primary'],
                fg='white').pack(side=tk.LEFT, padx=20, pady=15)
        
        tk.Label(header_frame, text="Universal Translation Tool",
                font=('Segoe UI', 10),
                bg=self.COLORS['primary'],
                fg='white').pack(side=tk.LEFT, pady=15)
        
        # Project section
        self.create_project_section(main_frame, row=1)
        
        # Languages section
        self.create_languages_section(main_frame, row=2)
        
        # Actions section
        self.create_actions_section(main_frame, row=3)
        
        # Progress section
        self.create_progress_section(main_frame, row=4)
        
        # Configure weights
        main_frame.rowconfigure(4, weight=1)
    
    def create_project_section(self, parent, row):
        """Modern project selection UI"""
        frame = ttk.LabelFrame(parent, text="📁 Project Configuration", padding="15")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Project path
        ttk.Label(frame, text="Project Folder:", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.project_path_var = tk.StringVar(value="No project selected")
        path_label = ttk.Label(frame, textvariable=self.project_path_var,
                              foreground=self.COLORS['primary'],
                              font=('Segoe UI', 9))
        path_label.grid(row=0, column=1, sticky=tk.W)
        
        browse_btn = ttk.Button(frame, text="📂 Browse",
                               command=self.select_project,
                               style='Primary.TButton')
        browse_btn.grid(row=0, column=2, padx=(10, 0))
        
        # i18n Status indicator
        self.i18n_status_var = tk.StringVar(value="")
        status_label = ttk.Label(frame, textvariable=self.i18n_status_var,
                                font=('Segoe UI', 8))
        status_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))
    
    def create_languages_section(self, parent, row):
        """Modern language selection UI"""
        frame = ttk.LabelFrame(parent, text="🌍 Languages", padding="15")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        
        # Instructions
        ttk.Label(frame,
                 text="Select languages (English is always included as source):",
                 font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Scrollable language grid
        canvas_frame = tk.Frame(frame)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        canvas = tk.Canvas(canvas_frame, height=120, bg='white')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        lang_frame = tk.Frame(canvas, bg='white')
        
        lang_frame.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=lang_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Language checkboxes in grid
        self.language_vars = {}
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        
        row_idx = 0
        col_idx = 0
        for code, name in sorted_langs:
            var = tk.BooleanVar(value=(code == 'en'))
            
            cb_frame = tk.Frame(lang_frame, bg='white')
            cb_frame.grid(row=row_idx, column=col_idx, sticky=tk.W, padx=10, pady=3)
            
            cb = ttk.Checkbutton(cb_frame,
                                text=f"{name} ({code})",
                                variable=var,
                                state='disabled' if code == 'en' else 'normal',
                                command=self.update_selected_languages)
            cb.pack(side=tk.LEFT)
            
            self.language_vars[code] = var
            
            col_idx += 1
            if col_idx >= 3:
                col_idx = 0
                row_idx += 1
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        
        # Selected count
        self.selected_langs_var = tk.StringVar(value="Selected: English (en)")
        ttk.Label(frame, textvariable=self.selected_langs_var,
                 foreground=self.COLORS['success'],
                 font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
    
    def create_actions_section(self, parent, row):
        """Modern action buttons"""
        frame = ttk.LabelFrame(parent, text="⚡ Actions", padding="15")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button grid
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        # Main workflow button (prominent)
        self.workflow_btn = tk.Button(btn_frame,
                                     text="🚀 Run Complete Workflow",
                                     command=self.run_complete_workflow,
                                     bg=self.COLORS['primary'],
                                     fg='white',
                                     font=('Segoe UI', 11, 'bold'),
                                     relief='flat',
                                     padx=30,
                                     pady=15,
                                     cursor='hand2',
                                     state='disabled')
        self.workflow_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Bind hover effects
        self.workflow_btn.bind('<Enter>', lambda e: self.workflow_btn.config(
            bg=self.COLORS['primary_hover']) if self.workflow_btn['state'] != 'disabled' else None)
        self.workflow_btn.bind('<Leave>', lambda e: self.workflow_btn.config(
            bg=self.COLORS['primary']) if self.workflow_btn['state'] != 'disabled' else None)
        
        # Individual steps
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text="Or run individual steps:",
                 foreground=self.COLORS['text_light'],
                 font=('Segoe UI', 8)).pack(anchor=tk.W, pady=(0, 5))
        
        steps_frame = tk.Frame(frame)
        steps_frame.pack(fill=tk.X)
        
        self.detect_btn = self.create_step_button(steps_frame, "1️⃣ Detect Text",
                                                  self.run_detect, 0, 'disabled')
        self.generate_btn = self.create_step_button(steps_frame, "2️⃣ Generate Keys",
                                                    self.run_generate, 1, 'disabled')
        self.translate_btn = self.create_step_button(steps_frame, "3️⃣ Translate",
                                                     self.run_translate, 2, 'disabled')
        self.replace_btn = self.create_step_button(steps_frame, "4️⃣ Replace Code",
                                                   self.run_replace, 3, 'disabled')
    
    def create_step_button(self, parent, text, command, col, state):
        """Create a step button with modern styling"""
        btn = ttk.Button(parent, text=text, command=command,
                        state=state, width=18)
        btn.grid(row=0, column=col, padx=3)
        return btn
    
    def create_progress_section(self, parent, row):
        """Modern progress display"""
        frame = ttk.LabelFrame(parent, text="📊 Progress & Output", padding="15")
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var,
                                           mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output area with custom styling
        output_frame = tk.Frame(frame, bg='white', relief='solid', borderwidth=1)
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.output_text = scrolledtext.ScrolledText(output_frame,
                                                     height=12,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 9),
                                                     bg='#f8f9fa',
                                                     relief='flat')
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Text tags for colored output
        self.output_text.tag_config('success', foreground=self.COLORS['success'], font=('Consolas', 9, 'bold'))
        self.output_text.tag_config('error', foreground=self.COLORS['danger'], font=('Consolas', 9, 'bold'))
        self.output_text.tag_config('warning', foreground=self.COLORS['warning'])
        self.output_text.tag_config('info', foreground=self.COLORS['primary'])
        self.output_text.tag_config('header', font=('Consolas', 10, 'bold'))
        
        self.log("🎉 Welcome to i18n Manager!", 'header')
        self.log("Select a React/TypeScript project to begin.\n", 'info')
    
    # ===== Core Functionality (All Embedded) =====
    
    def select_project(self):
        """Select project and detect setup"""
        folder = filedialog.askdirectory(title="Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_path_var.set(str(self.project_path.name))
        
        self.log(f"\n📁 Project: {self.project_path}", 'info')
        
        # Detect project structure
        self.detect_project_setup()
    
    def detect_project_setup(self):
        """Detect if project has i18n setup"""
        # Detect source directory
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = self.project_path / src_name
            if src_path.exists():
                self.src_dir = src_path
                self.log(f"  ✓ Found source: {src_name}/", 'success')
                break
        
        if not self.src_dir:
            self.log("  ⚠ No source directory found", 'warning')
            self.i18n_status_var.set("❌ No src/ directory found")
            return
        
        # Check for i18n setup
        i18n_status = {
            'has_package_json': (self.project_path / 'package.json').exists(),
            'has_i18n_config': (self.src_dir / 'i18n' / 'config.ts').exists(),
            'has_locales_dir': (self.src_dir / 'i18n' / 'locales').exists(),
        }
        
        self.has_i18n_setup = all([
            i18n_status['has_i18n_config'],
            i18n_status['has_locales_dir']
        ])
        
        if self.has_i18n_setup:
            self.locales_dir = self.src_dir / 'i18n' / 'locales'
            self.log("  ✓ i18n is configured", 'success')
            self.i18n_status_var.set("✅ i18n configured - Ready to use")
            
            # Detect existing languages
            self.detect_existing_languages()
            
            # Enable workflow
            self.workflow_btn['state'] = 'normal'
            self.detect_btn['state'] = 'normal'
        else:
            self.log("  ⚠ i18n not configured", 'warning')
            self.i18n_status_var.set("⚠️ i18n not configured")
            
            # Offer setup
            self.offer_i18n_setup()
    
    def detect_existing_languages(self):
        """Detect existing language files"""
        if not self.locales_dir or not self.locales_dir.exists():
            return
        
        existing = []
        for file in self.locales_dir.glob('*.json'):
            if file.stem not in ('index', 'config'):
                existing.append(file.stem)
        
        if existing:
            self.log(f"  ✓ Found languages: {', '.join(existing)}", 'success')
            for lang in existing:
                if lang in self.language_vars:
                    self.language_vars[lang].set(True)
            self.update_selected_languages()
    
    def offer_i18n_setup(self):
        """Offer to setup i18n for project"""
        response = messagebox.askyesno(
            "Setup i18n?",
            "This project doesn't have i18n configured.\n\n"
            "Would you like to set it up now?\n\n"
            "This will:\n"
            "• Install react-i18next dependencies\n"
            "• Create i18n configuration files\n"
            "• Generate initial translation files"
        )
        
        if response:
            self.run_i18n_setup_wizard()
    
    def run_i18n_setup_wizard(self):
        """Setup i18n from scratch"""
        wizard = tk.Toplevel(self.root)
        wizard.title("i18n Setup Wizard")
        wizard.geometry("600x500")
        wizard.transient(self.root)
        wizard.grab_set()
        
        # Center dialog
        wizard.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (wizard.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (wizard.winfo_height() // 2)
        wizard.geometry(f"+{x}+{y}")
        
        # Content
        content = tk.Frame(wizard, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text="🔧 i18n Setup Wizard",
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Step 1: Dependencies
        step1 = tk.LabelFrame(content, text="Step 1: Install Dependencies", padding=10)
        step1.pack(fill=tk.X, pady=5)
        
        tk.Label(step1, text="Add to package.json and run:",
                font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        dep_text = tk.Text(step1, height=3, font=('Consolas', 8), bg='#f5f5f5')
        dep_text.pack(fill=tk.X, pady=5)
        dep_text.insert('1.0', 'npm install react-i18next i18next\n# or\nyarn add react-i18next i18next')
        dep_text.config(state='disabled')
        
        # Step 2: Files to create
        step2 = tk.LabelFrame(content, text="Step 2: Files Created", padding=10)
        step2.pack(fill=tk.X, pady=5)
        
        files_text = tk.Text(step2, height=6, font=('Consolas', 8), bg='#f5f5f5')
        files_text.pack(fill=tk.X)
        files_text.insert('1.0',
            'src/i18n/\n'
            '  ├── config.ts          # i18n configuration\n'
            '  ├── locales/\n'
            '  │   ├── en.json        # English\n'
            '  │   └── [other langs]\n'
            '  └── index.ts           # Exports')
        files_text.config(state='disabled')
        
        # Action buttons
        btn_frame = tk.Frame(content)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Cancel",
                  command=wizard.destroy).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="Create Setup",
                  command=lambda: self.create_i18n_files(wizard),
                  style='Primary.TButton').pack(side=tk.RIGHT)
    
    def create_i18n_files(self, wizard_window):
        """Create i18n configuration files"""
        try:
            i18n_dir = self.src_dir / 'i18n'
            locales_dir = i18n_dir / 'locales'
            
            # Create directories
            locales_dir.mkdir(parents=True, exist_ok=True)
            
            # Create config.ts
            config_content = '''import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import en from './locales/en.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en }
    },
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
'''
            (i18n_dir / 'config.ts').write_text(config_content, encoding='utf-8')
            
            # Create initial locale files
            initial_structure = {
                "common": {},
                "nav": {},
                "button": {},
                "form": {},
                "message": {}
            }
            
            for lang in self.selected_languages:
                lang_file = locales_dir / f'{lang}.json'
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_structure, f, indent=2, ensure_ascii=False)
            
            # Create index.ts
            index_content = "export { default } from './config';\n"
            (i18n_dir / 'index.ts').write_text(index_content, encoding='utf-8')
            
            wizard_window.destroy()
            
            self.log("\n✅ i18n setup complete!", 'success')
            self.log(f"  Created: {i18n_dir}", 'info')
            
            # Update status
            self.has_i18n_setup = True
            self.locales_dir = locales_dir
            self.i18n_status_var.set("✅ i18n configured - Ready to use")
            self.workflow_btn['state'] = 'normal'
            self.detect_btn['state'] = 'normal'
            
            # Show next steps
            messagebox.showinfo(
                "Setup Complete!",
                "i18n has been configured!\n\n"
                "Next steps:\n"
                "1. Run 'npm install' to install dependencies\n"
                "2. Import i18n in your App.tsx:\n"
                "   import './i18n'\n"
                "3. Use the workflow to detect and translate text"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create i18n files:\n{str(e)}")
    
    def update_selected_languages(self):
        """Update language selection"""
        self.selected_languages = ['en']
        for code, var in self.language_vars.items():
            if var.get() and code != 'en':
                self.selected_languages.append(code)
        
        lang_names = [f"{self.SUPPORTED_LANGUAGES[code]} ({code})"
                     for code in self.selected_languages]
        self.selected_langs_var.set(
            f"Selected ({len(self.selected_languages)}): {', '.join(lang_names)}")
    
    # ===== Detection (Embedded) =====
    
    def detect_hardcoded_text(self, source_dir: Path) -> List[Dict]:
        """Detect hardcoded strings in source code"""
        findings = []
        
        for tsx_file in source_dir.rglob('*.tsx'):
            if any(excluded in tsx_file.parts
                  for excluded in ['node_modules', 'dist', 'build', '.git']):
                continue
            
            try:
                content = tsx_file.read_text(encoding='utf-8')
                file_findings = self._scan_file_for_strings(content, tsx_file)
                findings.extend(file_findings)
            except Exception as e:
                self.log(f"  ⚠ Could not read {tsx_file.name}: {e}", 'warning')
        
        return findings
    
    def _scan_file_for_strings(self, content: str, filepath: Path) -> List[Dict]:
        """Scan single file for hardcoded strings"""
        findings = []
        
        # Check if file already uses translation
        existing_keys = set(re.findall(r't\(["\']([^"\']+)["\']\)', content))
        
        for context_name, pattern in self.SAFE_CONTEXTS.items():
            for match in re.finditer(pattern, content):
                text = match.group(1).strip()
                
                if not text or text in existing_keys:
                    continue
                
                # Check if it's user-facing
                if self._is_user_facing_text(text):
                    line_num = content[:match.start()].count('\n') + 1
                    findings.append({
                        'file': str(filepath),
                        'line': line_num,
                        'text': text,
                        'context': context_name
                    })
        
        return findings
    
    def _is_user_facing_text(self, text: str) -> bool:
        """Check if text is user-facing"""
        # Length check
        if len(text) < 4 or len(text) > 150:
            return False
        
        # Technical pattern check
        for pattern in self.TECHNICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Must start with capital letter
        if not text[0].isupper():
            return False
        
        # Must be mostly letters
        alpha_chars = sum(c.isalpha() for c in text)
        if alpha_chars < len(text) * 0.5:
            return False
        
        return True
    
    # ===== Key Generation (Embedded) =====
    
    def generate_translation_keys(self, strings: List[Dict]) -> Dict[str, Dict]:
        """Generate translation keys from detected strings"""
        mapping = {}
        used_keys = set()
        
        for string_info in strings:
            text = string_info['text']
            filepath = Path(string_info['file'])
            context = string_info['context']
            
            # Determine section from file path
            section = self._determine_section(filepath)
            
            # Generate key name
            words = re.findall(r'\b[A-Z][a-z]+', text)
            key_base = ''.join(word.lower() for word in words[:3])
            
            if not key_base:
                key_base = 'text'
            
            # Ensure uniqueness
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
                'context': context,
                'section': section,
                'key_name': key_name
            }
        
        return mapping
    
    def _determine_section(self, filepath: Path) -> str:
        """Determine section from file path"""
        path_lower = str(filepath).lower()
        
        if 'nav' in path_lower:
            return 'nav'
        elif 'footer' in path_lower:
            return 'footer'
        elif 'home' in path_lower:
            return 'home'
        elif 'about' in path_lower:
            return 'about'
        elif 'contact' in path_lower:
            return 'contact'
        elif 'auth' in path_lower or 'login' in path_lower:
            return 'auth'
        elif 'form' in path_lower:
            return 'form'
        elif 'button' in path_lower:
            return 'button'
        else:
            return 'common'
    
    # ===== Translation (Embedded) =====
    
    def translate_keys_to_languages(self, keys_mapping: Dict, languages: List[str]):
        """Translate keys to multiple languages"""
        # Update locale files
        for lang in languages:
            lang_file = self.locales_dir / f'{lang}.json'
            
            # Load existing
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Add new keys
            for full_key, info in keys_mapping.items():
                section, key_name = full_key.split('.', 1)
                text = info['text']
                
                if section not in data:
                    data[section] = {}
                
                if lang == 'en':
                    data[section][key_name] = text
                else:
                    # Add with marker for translation
                    data[section][key_name] = f'[EN] {text}'
            
            # Save
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Now translate marked strings
        for lang in languages:
            if lang == 'en':
                continue
            
            self.log(f"  🌍 Translating to {self.SUPPORTED_LANGUAGES[lang]}...", 'info')
            self._translate_file(self.locales_dir / f'{lang}.json', lang)
    
    def _translate_file(self, filepath: Path, target_lang: str):
        """Translate a single language file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated_data = self._translate_nested_dict(data, target_lang)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, indent=2, ensure_ascii=False)
    
    def _translate_nested_dict(self, data: dict, target_lang: str) -> dict:
        """Recursively translate nested dictionary"""
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self._translate_nested_dict(value, target_lang)
            elif isinstance(value, str) and value.startswith('[EN] '):
                original = value[5:]
                try:
                    translator = GoogleTranslator(source='en', target=target_lang)
                    translated = translator.translate(original)
                    result[key] = translated
                except Exception as e:
                    self.log(f"    ⚠ Translation failed for '{original[:30]}...': {e}", 'warning')
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    # ===== Code Replacement (Embedded) =====
    
    def replace_in_source_code(self, keys_mapping: Dict):
        """Replace hardcoded strings in source files"""
        # Create backup
        backup_dir = self.backups_dir / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Group by file
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
            
            # Backup
            shutil.copy2(filepath, backup_dir / filepath.name)
            
            # Read content
            content = filepath.read_text(encoding='utf-8')
            modified_content = content
            
            # Add import if needed
            if 'useTranslation' not in content:
                modified_content = self._add_i18n_import(modified_content)
            
            # Apply replacements
            for repl in replacements:
                modified_content = self._apply_replacement(
                    modified_content,
                    repl['text'],
                    repl['key'],
                    repl['context']
                )
            
            # Write back
            if modified_content != content:
                filepath.write_text(modified_content, encoding='utf-8')
                modified_count += 1
        
        self.log(f"  ✓ Modified {modified_count} files", 'success')
        self.log(f"  📁 Backups: {backup_dir}", 'info')
    
    def _add_i18n_import(self, content: str) -> str:
        """Add useTranslation import"""
        # Find where to insert
        import_pattern = r"(import\s+.*from\s+['\"]react['\"];?\n)"
        match = re.search(import_pattern, content)
        
        import_line = "import { useTranslation } from 'react-i18next';\n"
        
        if match:
            pos = match.end()
            content = content[:pos] + import_line + content[pos:]
        else:
            # Add at top
            content = import_line + '\n' + content
        
        # Add hook usage if not present
        if '{ t }' not in content:
            component_pattern = r'(export\s+default\s+function\s+\w+\s*\([^)]*\)\s*\{)'
            match = re.search(component_pattern, content)
            
            if match:
                pos = match.end()
                hook_line = '\n  const { t } = useTranslation();\n'
                content = content[:pos] + hook_line + content[pos:]
        
        return content
    
    def _apply_replacement(self, content: str, text: str, key: str, context: str) -> str:
        """Apply a single replacement"""
        # Escape special regex characters
        text_escaped = re.escape(text)
        
        replacements = {
            'jsx_text_node': (
                f'>{text_escaped}<',
                f'>{{t("{key}")}}<'
            ),
            'title_attr': (
                f'title=["\']({text_escaped})["\']',
                f'title={{t("{key}")}}'
            ),
            'placeholder_attr': (
                f'placeholder=["\']({text_escaped})["\']',
                f'placeholder={{t("{key}")}}'
            ),
        }
        
        if context in replacements:
            pattern, replacement = replacements[context]
            content = re.sub(pattern, replacement, content)
        
        return content
    
    # ===== Workflow Methods =====
    
    def run_detect(self):
        """Run detection step"""
        if not self.validate_project():
            return
        
        self.log("\n" + "="*60, 'header')
        self.log("🔍 Step 1: Detecting hardcoded text...", 'info')
        self.progress_bar.start()
        self.detect_btn['state'] = 'disabled'
        
        def detect_worker():
            try:
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                
                self.log(f"✅ Found {len(strings)} hardcoded strings", 'success')
                
                if strings:
                    self.generate_btn['state'] = 'normal'
                    
                    # Show preview
                    self.log("\nPreview (first 10):", 'info')
                    for i, s in enumerate(strings[:10], 1):
                        file_name = Path(s['file']).name
                        self.log(f"  {i}. {file_name}:{s['line']} - \"{s['text'][:50]}\"")
                else:
                    self.log("No hardcoded text detected.", 'info')
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}", 'error')
            finally:
                self.progress_bar.stop()
                self.detect_btn['state'] = 'normal'
        
        threading.Thread(target=detect_worker, daemon=True).start()
    
    def run_generate(self):
        """Run key generation step"""
        if not self.detected_strings:
            messagebox.showwarning("No Data", "Please run detection first!")
            return
        
        self.log("\n" + "="*60, 'header')
        self.log("🔑 Step 2: Generating translation keys...", 'info')
        self.progress_bar.start()
        self.generate_btn['state'] = 'disabled'
        
        def generate_worker():
            try:
                mapping = self.generate_translation_keys(self.detected_strings)
                self.generated_keys = mapping
                
                self.log(f"✅ Generated {len(mapping)} translation keys", 'success')
                
                # Group by section
                sections = defaultdict(int)
                for key in mapping.keys():
                    section = key.split('.')[0]
                    sections[section] += 1
                
                self.log("\nKeys by section:", 'info')
                for section, count in sorted(sections.items()):
                    self.log(f"  • {section}: {count} keys")
                
                self.translate_btn['state'] = 'normal'
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}", 'error')
            finally:
                self.progress_bar.stop()
                self.generate_btn['state'] = 'normal'
        
        threading.Thread(target=generate_worker, daemon=True).start()
    
    def run_translate(self):
        """Run translation step"""
        if not self.generated_keys:
            messagebox.showwarning("No Data", "Please run key generation first!")
            return
        
        self.log("\n" + "="*60, 'header')
        self.log("🌍 Step 3: Translating to languages...", 'info')
        self.log("⏳ This may take a few minutes...", 'warning')
        self.progress_bar.start()
        self.translate_btn['state'] = 'disabled'
        
        def translate_worker():
            try:
                self.translate_keys_to_languages(
                    self.generated_keys,
                    self.selected_languages
                )
                
                self.log(f"✅ Translated to {len(self.selected_languages)} languages", 'success')
                self.replace_btn['state'] = 'normal'
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}", 'error')
            finally:
                self.progress_bar.stop()
                self.translate_btn['state'] = 'normal'
        
        threading.Thread(target=translate_worker, daemon=True).start()
    
    def run_replace(self):
        """Run replacement step"""
        if not self.generated_keys:
            messagebox.showwarning("No Data", "Please run previous steps first!")
            return
        
        response = messagebox.askyesno(
            "Confirm Changes",
            f"This will modify {len(set(info['file'] for info in self.generated_keys.values()))} source files.\n\n"
            "Backups will be created automatically.\n\n"
            "Continue?"
        )
        
        if not response:
            return
        
        self.log("\n" + "="*60, 'header')
        self.log("✏️ Step 4: Replacing hardcoded text...", 'info')
        self.progress_bar.start()
        self.replace_btn['state'] = 'disabled'
        
        def replace_worker():
            try:
                self.replace_in_source_code(self.generated_keys)
                
                self.log("✅ Code replacement complete!", 'success')
                
                messagebox.showinfo(
                    "Complete!",
                    "i18n workflow finished! 🎉\n\n"
                    f"• {len(self.detected_strings)} strings detected\n"
                    f"• {len(self.generated_keys)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    "Your code now uses i18n translations!"
                )
                
            except Exception as e:
                self.log(f"❌ Error: {str(e)}", 'error')
            finally:
                self.progress_bar.stop()
                self.replace_btn['state'] = 'normal'
        
        threading.Thread(target=replace_worker, daemon=True).start()
    
    def run_complete_workflow(self):
        """Run all steps in sequence"""
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
        
        self.log("\n" + "="*60, 'header')
        self.log("🚀 Running complete workflow...", 'header')
        self.log("="*60, 'header')
        
        # Disable buttons
        self.workflow_btn['state'] = 'disabled'
        self.detect_btn['state'] = 'disabled'
        self.generate_btn['state'] = 'disabled'
        self.translate_btn['state'] = 'disabled'
        self.replace_btn['state'] = 'disabled'
        
        def workflow_worker():
            try:
                self.progress_bar.start()
                
                # Step 1: Detect
                self.log("\n🔍 Step 1/4: Detecting...", 'info')
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                self.log(f"  ✓ Found {len(strings)} strings", 'success')
                
                if not strings:
                    self.log("No hardcoded text to process.", 'info')
                    return
                
                # Step 2: Generate
                self.log("\n🔑 Step 2/4: Generating keys...", 'info')
                mapping = self.generate_translation_keys(strings)
                self.generated_keys = mapping
                self.log(f"  ✓ Generated {len(mapping)} keys", 'success')
                
                # Step 3: Translate
                self.log("\n🌍 Step 3/4: Translating...", 'info')
                self.translate_keys_to_languages(mapping, self.selected_languages)
                self.log(f"  ✓ Translated to {len(self.selected_languages)} languages", 'success')
                
                # Step 4: Replace
                self.log("\n✏️ Step 4/4: Updating code...", 'info')
                self.replace_in_source_code(mapping)
                self.log("  ✓ Code updated", 'success')
                
                self.log("\n" + "="*60, 'header')
                self.log("🎉 Workflow complete!", 'success')
                self.log("="*60, 'header')
                
                messagebox.showinfo(
                    "Success!",
                    f"Complete workflow finished! 🎉\n\n"
                    f"• {len(strings)} strings detected\n"
                    f"• {len(mapping)} keys generated\n"
                    f"• {len(self.selected_languages)} languages\n\n"
                    f"Your project is now fully internationalized!"
                )
                
            except Exception as e:
                self.log(f"\n❌ Workflow failed: {str(e)}", 'error')
                messagebox.showerror("Error", f"Workflow failed:\n{str(e)}")
            finally:
                self.progress_bar.stop()
                self.workflow_btn['state'] = 'normal'
                self.detect_btn['state'] = 'normal'
        
        threading.Thread(target=workflow_worker, daemon=True).start()
    
    # ===== Helper Methods =====
    
    def validate_project(self):
        """Validate project is selected and configured"""
        if not self.project_path:
            messagebox.showerror("Error", "Please select a project first!")
            return False
        
        if not self.has_i18n_setup:
            messagebox.showerror("Error", "Please setup i18n first!")
            return False
        
        return True
    
    def log(self, message, tag=None):
        """Add message to output"""
        self.output_text.insert(tk.END, message + '\n', tag)
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def load_settings(self):
        """Load saved settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Restore last project if exists
                if 'last_project' in settings and Path(settings['last_project']).exists():
                    # Auto-load not implemented for cleaner UX
                    pass
                
                # Restore language selections
                if 'languages' in settings:
                    for lang in settings['languages']:
                        if lang in self.language_vars:
                            self.language_vars[lang].set(True)
                    self.update_selected_languages()
                    
            except:
                pass
    
    def save_settings(self):
        """Save current settings"""
        settings = {
            'last_project': str(self.project_path) if self.project_path else None,
            'languages': self.selected_languages
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Setup window icon and styling
    try:
        root.iconbitmap(default='')  # Remove default icon
    except:
        pass
    
    app = I18nManagerApp(root)
    
    # Save settings on close
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
