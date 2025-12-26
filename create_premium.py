#!/usr/bin/env python3
"""Create premium i18n manager"""

from pathlib import Path

# Read old version to get all the core methods
old_file = Path('i18n_manager_before_premium.py')
content = old_file.read_text(encoding='utf-8')

# Extract the core functionality methods (everything after the UI creation)
# We'll replace just the UI parts with new premium UI

# Find where the core methods start (after create_right_panel)
core_start = content.find('def create_section_header(self, parent, icon, text):')

if core_start == -1:
    core_start = content.find('def update_selected_languages(self):')

core_methods = content[core_start:]

# New premium header and UI
premium_ui = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Premium Windows 11 Edition
Custom window borders, taskbar icon, beautiful status cards
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
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

# Premium dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Auto-install dependencies
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class StatusCard(ctk.CTkFrame):
    """Beautiful status card widget - read-only"""
    def __init__(self, parent, icon, title, status="pending", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            corner_radius=10,
            fg_color=("#f0f0f0", "#1c2128"),
            border_width=1,
            border_color=("#d0d0d0", "#30363d")
        )
        
        # Content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        # Icon + Title
        self.icon_label = ctk.CTkLabel(
            content,
            text=icon,
            font=ctk.CTkFont(size=20),
            width=30
        )
        self.icon_label.pack(side="left", padx=(0, 10))
        
        self.title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            content,
            text="●",
            font=ctk.CTkFont(size=16),
            width=20
        )
        self.status_label.pack(side="right", padx=(10, 0))
        
        self.set_status(status)
    
    def set_status(self, status):
        """Update status (pending, running, success, error)"""
        colors = {
            'pending': ("#999", "#666"),
            'running': ("#0078d4", "#0078d4"),
            'success': ("#3fb950", "#3fb950"),
            'error': ("#f85149", "#f85149")
        }
        
        self.status_label.configure(text_color=colors.get(status, colors['pending']))
        
        if status == 'running':
            self.configure(border_color=("#0078d4", "#0078d4"), border_width=2)
        else:
            self.configure(border_color=("#d0d0d0", "#30363d"), border_width=1)


class I18nManagerApp:
    """Premium Windows 11-style i18n Manager"""
    
    # Premium color palette
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
        # Main window - borderless
        self.root = ctk.CTk()
        self.root.title("i18n Manager")
        self.root.geometry("1500x800")
        self.root.configure(fg_color=self.COLORS['bg_app'])
        
        # Remove default border
        self.root.overrideredirect(True)
        
        # Set app icon for taskbar
        try:
            icon_path = Path(__file__).parent / 'icon.ico'
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
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
        
        # Status cards
        self.status_cards: List[StatusCard] = []
        
        # Window drag
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Build UI
        self.create_ui()
        self.center_window()
        self.load_settings()
    
    def center_window(self):
        """Center window"""
        self.root.update_idletasks()
        width = 1500
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create premium UI with custom titlebar"""
        # Main container with border
        container = ctk.CTkFrame(
            self.root,
            corner_radius=12,
            border_width=1,
            border_color=self.COLORS['border'],
            fg_color=self.COLORS['bg_surface']
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Custom titlebar
        self.create_titlebar(container)
        
        # Content
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Split panels (35% left, 65% right)
        left_panel = ctk.CTkFrame(
            content,
            corner_radius=10,
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border']
        )
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        right_panel = ctk.CTkFrame(
            content,
            corner_radius=10,
            fg_color=self.COLORS['bg_card'],
            border_width=1,
            border_color=self.COLORS['border']
        )
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
    
    def create_titlebar(self, parent):
        """Custom Windows 11-style titlebar"""
        titlebar = ctk.CTkFrame(
            parent,
            height=45,
            corner_radius=0,
            fg_color=self.COLORS['bg_card']
        )
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)
        
        # Draggable
        titlebar.bind('<Button-1>', self.start_drag)
        titlebar.bind('<B1-Motion>', self.on_drag)
        
        # Icon + title
        title_frame = ctk.CTkFrame(titlebar, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=15)
        title_frame.bind('<Button-1>', self.start_drag)
        title_frame.bind('<B1-Motion>', self.on_drag)
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text="🌍",
            font=ctk.CTkFont(size=18)
        )
        icon_label.pack(side="left", padx=(0, 8))
        icon_label.bind('<Button-1>', self.start_drag)
        icon_label.bind('<B1-Motion>', self.on_drag)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="i18n Manager",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLORS['text']
        )
        title_label.pack(side="left")
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.on_drag)
        
        # Window controls
        controls = ctk.CTkFrame(titlebar, fg_color="transparent")
        controls.pack(side="right", padx=5)
        
        min_btn = ctk.CTkButton(
            controls,
            text="−",
            width=45,
            height=35,
            corner_radius=6,
            fg_color="transparent",
            hover_color=self.COLORS['bg_surface'],
            font=ctk.CTkFont(size=18),
            command=self.minimize_window
        )
        min_btn.pack(side="left", padx=2)
        
        close_btn = ctk.CTkButton(
            controls,
            text="✕",
            width=45,
            height=35,
            corner_radius=6,
            fg_color="transparent",
            hover_color=self.COLORS['error'],
            font=ctk.CTkFont(size=14),
            command=self.close_window
        )
        close_btn.pack(side="left", padx=2)
    
    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_drag(self, event):
        x = self.root.winfo_x() + event.x - self.drag_start_x
        y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f'+{x}+{y}')
    
    def minimize_window(self):
        self.root.iconify()
    
    def close_window(self):
        self.save_settings()
        self.root.destroy()
    
    def create_left_panel(self, parent):
        """Left control panel"""
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['accent'],
            scrollbar_button_hover_color=self.COLORS['accent_hover']
        )
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        
        # PROJECT
        self.create_section_header(scroll, "📁", "Project")
        
        self.project_label = ctk.CTkLabel(
            scroll,
            text="No project selected",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['text_muted'],
            anchor="w"
        )
        self.project_label.pack(fill="x", pady=(0, 8))
        
        browse_btn = ctk.CTkButton(
            scroll,
            text="📂  Browse Project",
            command=self.select_project,
            height=38,
            corner_radius=8,
            fg_color=self.COLORS['accent'],
            hover_color=self.COLORS['accent_hover'],
            font=ctk.CTkFont(size=12, weight="bold")
        )
        browse_btn.pack(fill="x", pady=(0, 5))
        
        self.status_label = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_muted']
        )
        self.status_label.pack(fill="x", pady=(0, 20))
        
        # LANGUAGES
        self.create_section_header(scroll, "🌍", "Languages")
        
        hint = ctk.CTkLabel(
            scroll,
            text="English is the source language",
            font=ctk.CTkFont(size=9),
            text_color=self.COLORS['text_muted']
        )
        hint.pack(anchor="w", pady=(0, 8))
        
        lang_frame = ctk.CTkFrame(scroll, fg_color=self.COLORS['bg_surface'], corner_radius=8)
        lang_frame.pack(fill="x", pady=(0, 5))
        
        self.language_vars = {}
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        
        row, col = 0, 0
        for code, name in sorted_langs:
            var = ctk.BooleanVar(value=(code == 'en'))
            
            cb = ctk.CTkCheckBox(
                lang_frame,
                text=name,
                variable=var,
                command=self.update_selected_languages,
                font=ctk.CTkFont(size=10),
                checkbox_width=18,
                checkbox_height=18,
                corner_radius=4,
                fg_color=self.COLORS['accent'],
                hover_color=self.COLORS['accent_hover']
            )
            cb.grid(row=row, column=col, padx=6, pady=3, sticky="w")
            
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
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.COLORS['success']
        )
        self.lang_count_label.pack(anchor="w", pady=(5, 20))
        
        # ACTIONS
        self.create_section_header(scroll, "⚡", "Actions")
        
        self.workflow_btn = ctk.CTkButton(
            scroll,
            text="🚀  Run Complete Workflow",
            command=self.run_complete_workflow,
            height=48,
            corner_radius=10,
            fg_color=self.COLORS['accent'],
            hover_color=self.COLORS['accent_hover'],
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.workflow_btn.pack(fill="x", pady=(0, 12))
        
        sep = ctk.CTkFrame(scroll, height=1, fg_color=self.COLORS['border'])
        sep.pack(fill="x", pady=8)
        
        step_label = ctk.CTkLabel(
            scroll,
            text="Individual steps:",
            font=ctk.CTkFont(size=10),
            text_color=self.COLORS['text_muted']
        )
        step_label.pack(anchor="w", pady=(0, 6))
        
        self.detect_btn = self.create_step_btn(scroll, "1️⃣  Detect", self.run_detect)
        self.generate_btn = self.create_step_btn(scroll, "2️⃣  Generate", self.run_generate)
        self.translate_btn = self.create_step_btn(scroll, "3️⃣  Translate", self.run_translate)
        self.replace_btn = self.create_step_btn(scroll, "4️⃣  Replace", self.run_replace)
    
    def create_right_panel(self, parent):
        """Right status panel with cards"""
        # Header
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(12, 10))
        
        header = ctk.CTkLabel(
            header_frame,
            text="📊  Live Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLORS['text']
        )
        header.pack(side="left")
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            parent,
            height=6,
            corner_radius=3,
            progress_color=self.COLORS['accent']
        )
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            parent,
            text="Ready",
            font=ctk.CTkFont(size=11),
            text_color=self.COLORS['text_muted']
        )
        self.progress_label.pack(anchor="e", padx=15, pady=(0, 8))
        
        # Status cards container (scrollable, read-only)
        self.status_container = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS['accent'],
            scrollbar_button_hover_color=self.COLORS['accent_hover']
        )
        self.status_container.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        # Welcome card
        welcome = StatusCard(
            self.status_container,
            icon="👋",
            title="Welcome to i18n Manager!",
            status="success"
        )
        welcome.pack(fill="x", pady=3)
        
        info = StatusCard(
            self.status_container,
            icon="💡",
            title="Select a project to begin",
            status="pending"
        )
        info.pack(fill="x", pady=3)
    
    def create_section_header(self, parent, icon, text):
        """Section header"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 8))
        
        label = ctk.CTkLabel(
            frame,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.COLORS['text']
        )
        label.pack(side="left")
    
    def create_step_btn(self, parent, text, command):
        """Step button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=34,
            corner_radius=7,
            fg_color=self.COLORS['bg_surface'],
            hover_color=self.COLORS['border'],
            border_width=1,
            border_color=self.COLORS['border'],
            font=ctk.CTkFont(size=11),
            state="disabled"
        )
        btn.pack(fill="x", pady=2)
        return btn
    
    # ===== Status Updates =====
    
    def add_status_card(self, icon, title, status="running"):
        """Add new status card - read-only"""
        card = StatusCard(
            self.status_container,
            icon=icon,
            title=title,
            status=status
        )
        card.pack(fill="x", pady=3)
        self.status_cards.append(card)
        self.root.update()
        return card
    
    def update_progress(self, value: float, text: str = None):
        """Update progress bar"""
        self.progress_bar.set(value)
        if text:
            self.progress_label.configure(text=text)
        self.root.update()
    
    def clear_status_cards(self):
        """Clear all status cards"""
        for card in self.status_cards:
            card.destroy()
        self.status_cards.clear()
    
    # ===== Core Functionality =====
    
    def select_project(self):
        """Select project"""
        folder = filedialog.askdirectory(title="Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_label.configure(
            text=str(self.project_path.name),
            text_color=self.COLORS['accent']
        )
        
        self.clear_status_cards()
        card = self.add_status_card("📁", f"Opened: {self.project_path.name}", "success")
        
        self.update_progress(0.1, "Scanning project...")
        self.detect_project_setup()
    
    '''

# Write the complete file
output_file = Path('i18n_manager.py')
output_file.write_text(premium_ui + core_methods, encoding='utf-8')

print("✅ Created premium i18n_manager.py")
print(f"   File size: {len(premium_ui + core_methods):,} bytes")
