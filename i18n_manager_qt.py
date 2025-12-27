#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - PyQt6 Premium Edition
Professional UI with custom titlebar and taskbar support
"""

import sys
import json
import re
import shutil
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QProgressBar, QScrollArea,
    QFileDialog, QMessageBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPainter

# Auto-install dependencies
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class WorkerSignals(QObject):
    """Signals for worker thread communication"""
    progress = pyqtSignal(float, str)  # (progress_value, status_text)
    add_card = pyqtSignal(str, str, str)  # (icon, text, status)
    update_card = pyqtSignal(int, str, str)  # (card_index, text, status)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class StatusCard(QFrame):
    """Modern status card widget"""
    def __init__(self, icon: str, title: str, status: str = "pending", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #1c2128;
                border: 1px solid #30363d;
                border-radius: 10px;
                padding: 12px 15px;
            }
        """)
        self.setMinimumHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI", 16))
        self.icon_label.setFixedWidth(30)
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #ffffff; border: none;")
        layout.addWidget(self.title_label, 1)
        
        # Status indicator
        self.status_label = QLabel("●")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setFixedWidth(20)
        layout.addWidget(self.status_label)
        
        self.set_status(status)
    
    def set_status(self, status: str):
        """Update status color"""
        colors = {
            'pending': '#666',
            'running': '#0078d4',
            'success': '#3fb950',
            'error': '#f85149'
        }
        color = colors.get(status, colors['pending'])
        self.status_label.setStyleSheet(f"color: {color}; border: none;")
        
        if status == 'running':
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: #1c2128;
                    border: 2px solid {color};
                    border-radius: 10px;
                    padding: 12px 15px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1c2128;
                    border: 1px solid #30363d;
                    border-radius: 10px;
                    padding: 12px 15px;
                }
            """)


class CustomTitleBar(QWidget):
    """Custom draggable titlebar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_pos = QPoint()
        
        self.setFixedHeight(45)
        self.setStyleSheet("background-color: #1c2128;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(0)
        
        # Icon and title
        icon = QLabel("🌍")
        icon.setFont(QFont("Segoe UI", 16))
        layout.addWidget(icon)
        
        title = QLabel("i18n Manager")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-left: 8px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Minimize button
        min_btn = QPushButton("−")
        min_btn.setFixedSize(45, 35)
        min_btn.setFont(QFont("Segoe UI", 16))
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #161b22;
            }
        """)
        min_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(min_btn)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(45, 35)
        close_btn.setFont(QFont("Segoe UI", 12))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #f85149;
            }
        """)
        close_btn.clicked.connect(parent.close)
        layout.addWidget(close_btn)
    
    def mousePressEvent(self, event):
        """Start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Drag window"""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_pos)


class I18nManagerQt(QMainWindow):
    """PyQt6 i18n Manager with custom titlebar"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English', 'nl': 'Dutch', 'de': 'German', 'fr': 'French',
        'es': 'Spanish', 'it': 'Italian', 'pt': 'Portuguese', 'ro': 'Romanian',
        'ru': 'Russian', 'cs': 'Czech', 'pl': 'Polish', 'el': 'Greek',
        'tr': 'Turkish', 'ar': 'Arabic', 'ja': 'Japanese', 'ko': 'Korean',
        'zh': 'Chinese', 'hi': 'Hindi', 'sv': 'Swedish', 'da': 'Danish',
        'no': 'Norwegian', 'fi': 'Finnish',
    }
    
    SAFE_CONTEXTS = {
        # JSX content
        'jsx_text_node': r'>([A-Z][^<>{}]*?)<',
        'jsx_text_lowercase': r'>([a-z][^<>{}]{3,}?)<',
        
        # HTML attributes
        'title_attr': r'title=["\'](.*?)["\']',
        'alt_attr': r'alt=["\'](.*?)["\']',
        'placeholder_attr': r'placeholder=["\'](.*?)["\']',
        'aria_label': r'aria-label=["\'](.*?)["\']',
        
        # Common component props (text content)
        'text_prop': r'text=["\'](.*?)["\']',
        'label_prop': r'label=["\'](.*?)["\']',
        'heading_prop': r'heading=["\'](.*?)["\']',
        'title_prop': r'title=["\'](.*?)["\']',
        'subtitle_prop': r'subtitle=["\'](.*?)["\']',
        'description_prop': r'description=["\'](.*?)["\']',
        'content_prop': r'content=["\'](.*?)["\']',
        'message_prop': r'message=["\'](.*?)["\']',
        'value_prop': r'value=["\'](.*?)["\']',
        'name_prop': r'name=["\'](.*?)["\']',
        
        # JSX elements
        'label_text': r'<label[^>]*>([^<]+)</label>',
        'button_text': r'<[Bb]utton[^>]*>([^<]+)</[Bb]utton>',
        'link_text': r'<a[^>]*>([^<]+)</a>',
        'span_text': r'<span[^>]*>([^<]+)</span>',
        'div_text': r'<div[^>]*>\s*([^<>]+?)\s*</div>',
        'p_text': r'<p[^>]*>([^<]+)</p>',
        'h1_text': r'<h1[^>]*>([^<]+)</h1>',
        'h2_text': r'<h2[^>]*>([^<]+)</h2>',
        'h3_text': r'<h3[^>]*>([^<]+)</h3>',
        'h4_text': r'<h4[^>]*>([^<]+)</h4>',
        'li_text': r'<li[^>]*>([^<]+)</li>',
        
        # Object/Array string literals (common in data structures)
        'object_title': r'title:\s*["\']([^"\']+)["\']',
        'object_description': r'description:\s*["\']([^"\']+)["\']',
        'object_text': r'text:\s*["\']([^"\']+)["\']',
        'object_label': r'label:\s*["\']([^"\']+)["\']',
        'object_name': r'name:\s*["\']([^"\']+)["\']',
        'object_heading': r'heading:\s*["\']([^"\']+)["\']',
        'object_content': r'content:\s*["\']([^"\']+)["\']',
        'object_message': r'message:\s*["\']([^"\']+)["\']',
        'object_value': r'value:\s*["\']([^"\']+)["\']',
        
        # Template literals (backticks)
        'template_literal': r'`([A-Z][^`]*?)`',
    }
    
    TECHNICAL_PATTERNS = [
        # Variable/function naming patterns
        r'^[a-z_]+$',  # snake_case
        r'^[A-Z_]+$',  # CONSTANTS
        r'^[a-z][a-zA-Z0-9]*$',  # Single camelCase word (onClick, useState, etc.)
        r'^[a-z]+[A-Z]',  # camelCase with capitals (handleClick, getUserData)
        r'^[A-Z][a-z]+[A-Z]',  # PascalCase (MyComponent, UserProfile)
        r'^on[A-Z]',  # Event handlers (onClick, onSubmit)
        r'^handle[A-Z]',  # Handler functions (handleClick, handleChange)
        r'^is[A-Z]',  # Boolean checks (isActive, isLoading)
        r'^has[A-Z]',  # Boolean checks (hasAccess, hasPermission)
        r'^get[A-Z]',  # Getter functions (getData, getUserInfo)
        r'^set[A-Z]',  # Setter functions (setData, setUser)
        r'^use[A-Z]',  # React hooks (useState, useEffect, useCustomHook)
        r'^fetch[A-Z]',  # Fetch functions
        r'^create[A-Z]',  # Create functions
        r'^update[A-Z]',  # Update functions
        r'^delete[A-Z]',  # Delete functions
        
        # Paths and URLs
        r'^/[a-zA-Z0-9/_-]*$',  # URLs/paths
        r'^\./|\.\./',  # Relative paths
        r'^https?://',  # URLs
        
        # CSS and styling
        r'^(text|bg|border|flex|grid|gap|p|m|w|h|rounded|shadow|hover|focus|active|disabled)-',  # Tailwind
        r'^#[0-9a-fA-F]{3,8}$',  # Hex colors
        r'^rgb\(|^rgba\(',  # RGB colors
        r'^[0-9]+\s*(px|rem|em|%|vh|vw|pt|cm|mm|in)$',  # CSS units
        
        # File extensions and technical strings
        r'\.(jpg|jpeg|png|gif|svg|webp|mp4|pdf|json|xml|csv|tsx|jsx|ts|js|css|html|woff|woff2|ttf|eot|ico)$',
        r'^\d+$',  # Pure numbers
        
        # Already translated
        r't\(["\']',  # t() calls
        
        # React/JS specific
        r'useState|useEffect|useCallback|useMemo|useRef|useContext|useReducer',  # React hooks
        r'^React\.',  # React namespace
        r'className|onClick|onChange|onSubmit|onFocus|onBlur',  # Common props
        
        # Common code patterns
        r'^\w+\(\)$',  # Function calls like "doSomething()"
        r'^\w+\.\w+',  # Object property access like "user.name"
        r'=>',  # Arrow functions
        r'const |let |var |function ',  # Variable declarations
        
        # Single technical words that might appear
        r'^(div|span|button|input|form|label|img|svg|path|rect|circle|line)$',  # HTML/SVG elements
        r'^(true|false|null|undefined|NaN|Infinity)$',  # JS keywords
        r'^(import|export|default|from|as|type|interface|class|extends|implements)$',  # JS/TS keywords
    ]
    
    def __init__(self):
        super().__init__()
        
        # Remove default titlebar but keep taskbar presence
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        
        # Set icon
        icon_path = Path(__file__).parent / 'icon.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setWindowTitle("i18n Manager")
        self.resize(1400, 750)
        
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
        self.status_cards: List[StatusCard] = []
        self.language_checkboxes: Dict[str, QCheckBox] = {}
        
        # Worker signals
        self.signals = WorkerSignals()
        self.signals.progress.connect(self._update_progress_slot)
        self.signals.add_card.connect(self._add_status_card_slot)
        self.signals.update_card.connect(self._update_status_card_slot)
        
        self.setup_ui()
        self.center_window()
        self.load_settings()
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def setup_ui(self):
        """Create the UI"""
        # Main container
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: #0d1117;")
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)
        
        # Custom titlebar
        titlebar = CustomTitleBar(self)
        main_layout.addWidget(titlebar)
        
        # Content container
        content = QFrame()
        content.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
        """)
        main_layout.addWidget(content)
        
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(8)
        
        # Left panel (40%)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 40)
        
        # Right panel (60%)
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 60)
    
    def create_left_panel(self):
        """Create left control panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1c2128;
                border: 1px solid #30363d;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #0078d4;
                border-radius: 4px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # === PROJECT SECTION ===
        scroll_layout.addWidget(self.create_section_header("📁", "Project"))
        
        self.project_label = QLabel("No project selected")
        self.project_label.setStyleSheet("color: #8b949e; font-size: 11px;")
        self.project_label.setWordWrap(True)
        scroll_layout.addWidget(self.project_label)
        
        browse_btn = QPushButton("📂  Browse Project Folder")
        browse_btn.setFixedHeight(40)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        browse_btn.clicked.connect(self.select_project)
        scroll_layout.addWidget(browse_btn)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8b949e; font-size: 10px;")
        scroll_layout.addWidget(self.status_label)
        
        # === LANGUAGES SECTION ===
        scroll_layout.addWidget(self.create_section_header("🌍", "Target Languages"))
        
        hint = QLabel("English is always included as source")
        hint.setStyleSheet("color: #8b949e; font-size: 9px;")
        scroll_layout.addWidget(hint)
        
        # Language grid
        lang_container = QFrame()
        lang_container.setStyleSheet("""
            QFrame {
                background-color: #1c2128;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        lang_grid = QGridLayout(lang_container)
        lang_grid.setSpacing(4)
        
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        
        row, col = 0, 0
        for code, name in sorted_langs:
            cb = QCheckBox(name)
            cb.setChecked(code == 'en')
            cb.setEnabled(code != 'en')
            cb.setStyleSheet("""
                QCheckBox {
                    color: #ffffff;
                    font-size: 10px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 1px solid #30363d;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078d4;
                    border-color: #0078d4;
                }
            """)
            cb.stateChanged.connect(self.update_selected_languages)
            self.language_checkboxes[code] = cb
            
            lang_grid.addWidget(cb, row, col)
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        scroll_layout.addWidget(lang_container)
        
        self.lang_count_label = QLabel("Selected: 1 language")
        self.lang_count_label.setStyleSheet("color: #3fb950; font-size: 10px; font-weight: bold;")
        scroll_layout.addWidget(self.lang_count_label)
        
        # === ACTIONS SECTION ===
        scroll_layout.addWidget(self.create_section_header("⚡", "Actions"))
        
        # Main workflow button
        self.workflow_btn = QPushButton("🚀  Run Complete Workflow")
        self.workflow_btn.setFixedHeight(50)
        self.workflow_btn.setEnabled(False)
        self.workflow_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #30363d;
                color: #666;
            }
        """)
        self.workflow_btn.clicked.connect(self.run_complete_workflow)
        scroll_layout.addWidget(self.workflow_btn)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #30363d;")
        sep.setFixedHeight(1)
        scroll_layout.addWidget(sep)
        
        step_label = QLabel("Or run individual steps:")
        step_label.setStyleSheet("color: #8b949e; font-size: 10px;")
        scroll_layout.addWidget(step_label)
        
        # Step buttons
        self.detect_btn = self.create_step_btn("1️⃣  Detect Text", self.run_detect)
        self.generate_btn = self.create_step_btn("2️⃣  Generate Keys", self.run_generate)
        self.translate_btn = self.create_step_btn("3️⃣  Auto-Translate", self.run_translate)
        self.replace_btn = self.create_step_btn("4️⃣  Update Code", self.run_replace)
        self.validate_btn = self.create_step_btn("5️⃣  Validate Translations", self.run_validate)
        
        scroll_layout.addWidget(self.detect_btn)
        scroll_layout.addWidget(self.generate_btn)
        scroll_layout.addWidget(self.translate_btn)
        scroll_layout.addWidget(self.replace_btn)
        scroll_layout.addWidget(self.validate_btn)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return panel
    
    def create_right_panel(self):
        """Create right status panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1c2128;
                border: 1px solid #30363d;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("📊  Live Status")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #30363d;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Progress percentage
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.progress_label.setStyleSheet("color: #8b949e; font-size: 9px; font-weight: bold;")
        layout.addWidget(self.progress_label)
        
        # Status cards scroll area
        self.status_scroll = QScrollArea()
        self.status_scroll.setWidgetResizable(True)
        self.status_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #0078d4;
                border-radius: 4px;
            }
        """)
        
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setSpacing(3)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.addStretch()
        
        self.status_scroll.setWidget(self.status_container)
        layout.addWidget(self.status_scroll)
        
        # Welcome cards
        self.add_status_card("🎉", "Welcome to i18n Manager", "success")
        self.add_status_card("ℹ️", "Select a React/TypeScript project to begin", "pending")
        
        return panel
    
    def create_section_header(self, icon: str, text: str):
        """Create section header"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(f"{icon}  {text}")
        label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff;")
        layout.addWidget(label)
        layout.addStretch()
        
        return container
    
    def create_step_btn(self, text: str, callback):
        """Create step button"""
        btn = QPushButton(text)
        btn.setFixedHeight(36)
        btn.setEnabled(False)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #1c2128;
                color: #ffffff;
                border: 1px solid #30363d;
                border-radius: 8px;
                font-size: 11px;
                text-align: left;
                padding-left: 10px;
            }
            QPushButton:hover:enabled {
                background-color: #30363d;
            }
            QPushButton:disabled {
                color: #666;
            }
        """)
        btn.clicked.connect(callback)
        return btn
    
    def add_status_card(self, icon: str, text: str, status: str = "pending") -> int:
        """Add status card - thread-safe via signal. Returns card index."""
        self.signals.add_card.emit(icon, text, status)
        return 0  # Always returns 0 since cards are inserted at top
    
    def _add_status_card_slot(self, icon: str, text: str, status: str):
        """SLOT: Actually add card (runs in main thread)"""
        card = StatusCard(icon, text, status)
        self.status_layout.insertWidget(0, card)
        self.status_cards.insert(0, card)
        QApplication.processEvents()
    
    def update_status_card(self, card_index: int, text: str, status: str):
        """Update status card - thread-safe via signal"""
        self.signals.update_card.emit(card_index, text, status)
    
    def _update_status_card_slot(self, card_index: int, text: str, status: str):
        """SLOT: Actually update card (runs in main thread)"""
        if 0 <= card_index < len(self.status_cards):
            card = self.status_cards[card_index]
            card.title_label.setText(text)
            card.set_status(status)
            QApplication.processEvents()
    
    def update_progress(self, value: float, text: str = None):
        """Update progress - thread-safe via signal"""
        self.signals.progress.emit(value, text or "")
    
    def _update_progress_slot(self, value: float, text: str):
        """SLOT: Actually update progress (runs in main thread)"""
        self.progress_bar.setValue(int(value * 100))
        self.progress_label.setText(f"{int(value * 100)}%")
        if text and self.status_cards:
            self.status_cards[0].title_label.setText(text)
        QApplication.processEvents()
        self.progress_label.setText(f"{int(value * 100)}%")
        if text and self.status_cards:
            self.status_cards[0].title_label.setText(text)
        QApplication.processEvents()
    
    # === Project Management ===
    
    def select_project(self):
        """Select project folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_label.setText(str(self.project_path))
        self.project_label.setStyleSheet("color: #0078d4; font-size: 11px;")
        
        card_idx = self.add_status_card("📁", f"Opened: {self.project_path.name}", "running")
        QApplication.processEvents()  # Let signal process
        self.update_progress(0.1)
        self.detect_project_setup()
        self.update_status_card(card_idx, f"Opened: {self.project_path.name}", "success")
    
    def detect_project_setup(self):
        """Detect i18n configuration"""
        card_idx = self.add_status_card("🔍", "Scanning project structure...", "running")
        QApplication.processEvents()  # Let signal process
        
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = self.project_path / src_name
            if src_path.exists():
                self.src_dir = src_path
                break
        
        if not self.src_dir:
            self.update_status_card(card_idx, "❌ No src/ directory found", "error")
            self.status_label.setText("❌ No src/ directory")
            self.status_label.setStyleSheet("color: #f85149; font-size: 10px;")
            return
        
        # Check i18n setup
        i18n_config = self.src_dir / 'i18n' / 'config.ts'
        locales_dir = self.src_dir / 'i18n' / 'locales'
        
        self.has_i18n_setup = i18n_config.exists() and locales_dir.exists()
        
        if self.has_i18n_setup:
            self.locales_dir = locales_dir
            
            # Detect languages
            existing = [f.stem for f in locales_dir.glob('*.json') 
                       if f.stem not in ('index', 'config')]
            if existing:
                for lang in existing:
                    if lang in self.language_checkboxes:
                        self.language_checkboxes[lang].setChecked(True)
                self.update_selected_languages()
            
            self.update_status_card(card_idx, f"✓ i18n configured ({len(existing)} languages)", "success")
            self.status_label.setText("✅ Ready to process")
            self.status_label.setStyleSheet("color: #3fb950; font-size: 10px;")
            self.workflow_btn.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.validate_btn.setEnabled(True)
            self.update_progress(1.0)
        else:
            self.update_status_card(card_idx, "⚠️ i18n not configured", "pending")
            self.status_label.setText("⚠️ Setup required")
            self.status_label.setStyleSheet("color: #d29922; font-size: 10px;")
            self.offer_i18n_setup()
    
    def offer_i18n_setup(self):
        """Offer setup wizard"""
        # Auto-setup without dialog to avoid crashes
        self.add_status_card("⚠️", "i18n not configured - setting up automatically...", "running")
        time.sleep(0.1)
        self.create_i18n_setup()
    
    def create_i18n_setup(self):
        """Create i18n files"""
        try:
            card_idx = self.add_status_card("🔧", "Setting up i18n...", "running")
            QApplication.processEvents()  # Let signal process
            
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
            
            self.update_status_card(card_idx, "✅ i18n setup complete!", "success")
            self.update_progress(1.0)
            
            self.has_i18n_setup = True
            self.locales_dir = locales_dir
            self.status_label.setText("✅ Ready to process")
            self.status_label.setStyleSheet("color: #3fb950; font-size: 10px;")
            self.workflow_btn.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.validate_btn.setEnabled(True)
            
            self.add_status_card("✅", "i18n setup complete! Run: npm install react-i18next i18next", "success")
        except Exception as e:
            self.add_status_card("❌", f"Setup failed: {str(e)}", "error")
    
    def update_selected_languages(self):
        """Update language selection"""
        self.selected_languages = ['en']
        for code, cb in self.language_checkboxes.items():
            if cb.isChecked() and code != 'en':
                self.selected_languages.append(code)
        
        count = len(self.selected_languages)
        self.lang_count_label.setText(f"Selected: {count} language(s)")
    
    # === Detection (keep all the existing business logic from Tkinter version) ===
    
    def detect_hardcoded_text(self, source_dir: Path) -> List[Dict]:
        """Detect hardcoded strings with throttled updates"""
        findings = []
        files = list(source_dir.rglob('*.tsx'))
        files.extend(list(source_dir.rglob('*.jsx')))  # Also scan .jsx
        files = [f for f in files if not any(ex in f.parts for ex in 
                ['node_modules', 'dist', 'build', '.git', 'coverage', 'test', '__tests__'])]
        
        total = len(files)
        last_update_time = time.time()
        
        for idx, tsx_file in enumerate(files, 1):
            try:
                content = tsx_file.read_text(encoding='utf-8')
                
                # Skip very large files (> 100KB)
                if len(content) > 100000:
                    continue
                
                file_findings = self._scan_file(content, tsx_file)
                findings.extend(file_findings)
                
                # Throttle updates: only update every 0.1 seconds or every 10 files
                current_time = time.time()
                if (current_time - last_update_time > 0.1) or (idx % 10 == 0) or (idx == total):
                    progress = idx / total
                    self.update_progress(progress, f"Scanned {idx}/{total} files")
                    last_update_time = current_time
                    time.sleep(0.01)  # Small delay to let UI update
                
            except Exception as e:
                continue
        
        return findings
    
    def _scan_file(self, content: str, filepath: Path) -> List[Dict]:
        """Scan file for strings - optimized version"""
        findings = []
        seen_texts = set()
        
        # Find existing t() calls to skip
        existing_keys = set(re.findall(r't\(["\']([^"\']+)["\']\)', content))
        
        # Fast scan: Find all quoted strings first
        all_strings = []
        
        # Pattern 1: Object properties (most common for data)
        # title: "...", description: "...", etc.
        for match in re.finditer(r'(title|description|text|label|name|heading|content|message|value):\s*["\']([^"\']{2,})["\']', content):
            context = f'object_{match.group(1)}'
            text = match.group(2).strip()
            all_strings.append((text, context, match.start()))
        
        # Pattern 2: JSX text content
        # >Text here<
        for match in re.finditer(r'>([^<>{}\n]{2,}?)<', content):
            text = match.group(1).strip()
            if text and not text.startswith('{'):
                all_strings.append((text, 'jsx_text', match.start()))
        
        # Pattern 3: Common HTML attributes
        for attr in ['title', 'alt', 'placeholder', 'aria-label']:
            for match in re.finditer(f'{attr}=["\']([^"\']+)["\']', content):
                text = match.group(1).strip()
                all_strings.append((text, f'{attr}_attr', match.start()))
        
        # Pattern 4: Component props
        for prop in ['text', 'label', 'heading', 'subtitle', 'description']:
            for match in re.finditer(f'{prop}=["\']([^"\']+)["\']', content):
                text = match.group(1).strip()
                all_strings.append((text, f'{prop}_prop', match.start()))
        
        # Process all found strings
        for text, context, pos in all_strings:
            # Skip if already processed or already translated
            if text in seen_texts or text in existing_keys:
                continue
            
            # Validate if user-facing
            if self._is_user_facing(text):
                line_num = content[:pos].count('\n') + 1
                findings.append({
                    'file': str(filepath),
                    'line': line_num,
                    'text': text,
                    'context': context
                })
                seen_texts.add(text)
        
        return findings
    
    def _is_user_facing(self, text: str) -> bool:
        """Check if text is user-facing - VERY LENIENT but smart"""
        # More lenient length check - even single meaningful words
        if len(text) < 2 or len(text) > 500:
            return False
        
        # Skip if it's purely whitespace
        if not text.strip():
            return False
        
        # Skip if it contains parentheses (likely function call)
        if '(' in text or ')' in text:
            return False
        
        # Skip if it contains equals sign (likely assignment)
        if '=' in text and not text.startswith('='):
            return False
        
        # Skip if it looks like a variable assignment or object destructuring
        if re.match(r'^(const|let|var)\s+', text):
            return False
        
        # Skip if it's a single camelCase or PascalCase word (likely variable/function)
        if re.match(r'^[a-z]+[A-Z][a-zA-Z]*$', text) or re.match(r'^[A-Z][a-z]+[A-Z][a-zA-Z]*$', text):
            return False
        
        # Check technical patterns
        for pattern in self.TECHNICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Very lenient - allow if at least 20% is letters (was 50%, then 30%)
        # This catches things like "How It Works", "Key Benefits", etc.
        alpha_chars = sum(c.isalpha() for c in text)
        if alpha_chars < len(text) * 0.2:
            return False
        
        # Accept if it contains at least one word of 2+ letters
        words = re.findall(r'[a-zA-Z]{2,}', text)
        if len(words) < 1:
            return False
        
        # Reject if it's a single word that's all lowercase (likely variable)
        if len(words) == 1 and words[0].islower() and len(words[0]) < 8:
            return False
        
        return True
    
    # === Key Generation ===
    
    def generate_translation_keys(self, strings: List[Dict]) -> Dict[str, Dict]:
        """Generate keys from strings with throttled updates"""
        mapping = {}
        used_keys = set()
        
        total = len(strings)
        last_update_time = time.time()
        
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
            
            # Throttle updates
            current_time = time.time()
            if (current_time - last_update_time > 0.1) or (idx % 20 == 0) or (idx == total):
                progress = idx / total
                self.update_progress(progress, f"Generated {idx}/{total} keys")
                last_update_time = current_time
                time.sleep(0.01)
        
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
    
    # === Translation ===
    
    def translate_keys_to_languages(self, keys_mapping: Dict, languages: List[str]):
        """Translate to languages"""
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
        
        # Synchronize keys across all languages (ensure all have same structure)
        self.update_progress(0.9, "Synchronizing keys across languages...")
        self._synchronize_translation_keys(languages)
        
        # Translate non-English
        non_en = [l for l in languages if l != 'en']
        if non_en:
            for idx, lang in enumerate(non_en, 1):
                self.update_progress(idx / len(non_en), 
                                   f"Translating to {self.SUPPORTED_LANGUAGES[lang]}")
                self._translate_file(self.locales_dir / f'{lang}.json', lang)
        
        # Final synchronization after translation
        self.update_progress(0.95, "Final synchronization...")
        self._synchronize_translation_keys(languages)
    
    def _synchronize_translation_keys(self, languages: List[str]):
        """Synchronize keys across all language files - merge all keys from all files"""
        if not self.locales_dir.exists():
            return
        
        # Step 1: Collect all unique keys from all language files
        all_keys_structure = {}
        
        for lang in languages:
            lang_file = self.locales_dir / f'{lang}.json'
            if not lang_file.exists():
                continue
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            # Merge this file's structure into master structure
            all_keys_structure = self._merge_dict_keys(all_keys_structure, lang_data, keep_values=(lang == 'en'))
        
        # Step 2: Apply master structure to all language files
        for lang in languages:
            lang_file = self.locales_dir / f'{lang}.json'
            
            # Load existing data or create empty
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    lang_data = json.load(f)
            else:
                lang_data = {}
            
            # Sync with master structure
            synced_data = self._apply_master_structure(all_keys_structure, lang_data, is_english=(lang == 'en'))
            
            # Write back
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(synced_data, f, indent=2, ensure_ascii=False)
    
    def _merge_dict_keys(self, master: dict, source: dict, keep_values: bool = False) -> dict:
        """Merge keys from source into master structure"""
        result = master.copy()
        
        for key, value in source.items():
            if isinstance(value, dict):
                # Nested object - recurse
                if key not in result:
                    result[key] = {}
                elif not isinstance(result[key], dict):
                    result[key] = {}
                result[key] = self._merge_dict_keys(result.get(key, {}), value, keep_values)
            else:
                # String value - only store if we're keeping values (English file)
                if keep_values or key not in result:
                    result[key] = value
        
        return result
    
    def _apply_master_structure(self, master: dict, target: dict, is_english: bool = False) -> dict:
        """Apply master key structure to target, preserving existing translations"""
        result = {}
        
        for key, value in master.items():
            if isinstance(value, dict):
                # Nested object - recurse
                target_value = target.get(key, {})
                if not isinstance(target_value, dict):
                    target_value = {}
                result[key] = self._apply_master_structure(value, target_value, is_english)
            else:
                # String value
                if key in target and isinstance(target[key], str) and not target[key].startswith('[EN]'):
                    # Keep existing translation
                    result[key] = target[key]
                elif is_english:
                    # For English, use the value from master
                    result[key] = value
                else:
                    # Missing translation - mark for translation using English value
                    result[key] = f'[EN] {value}'
        
        return result
    
    def _translate_file(self, filepath: Path, target_lang: str):
        """Translate file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        translated = self._translate_dict(data, target_lang)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(translated, f, indent=2, ensure_ascii=False)
    
    def _translate_dict(self, data: dict, target_lang: str, parent_key: str = '', counter: list = None) -> dict:
        """Recursively translate dict with throttled updates"""
        result = {}
        
        if counter is None:
            counter = [0, self._count_translatable_keys(data), time.time()]  # Add last_update_time
        
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            if isinstance(value, dict):
                result[key] = self._translate_dict(value, target_lang, full_key, counter)
            elif isinstance(value, str) and value.startswith('[EN] '):
                original = value[5:]
                counter[0] += 1
                
                # Throttle UI updates - only every 0.2 seconds or every 5 items
                current_time = time.time()
                if (current_time - counter[2] > 0.2) or (counter[0] % 5 == 0):
                    progress_pct = int((counter[0] / counter[1] * 100)) if counter[1] > 0 else 0
                    self.update_progress(counter[0] / counter[1], f"Translating: {progress_pct}% ({counter[0]}/{counter[1]})")
                    counter[2] = current_time
                
                try:
                    translator = GoogleTranslator(source='en', target=target_lang)
                    result[key] = translator.translate(original)
                    time.sleep(0.05)  # Reduced from 0.1
                except:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def _count_translatable_keys(self, data: dict) -> int:
        """Count keys that need translation"""
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_translatable_keys(value)
            elif isinstance(value, str) and value.startswith('[EN] '):
                count += 1
        return count
    
    # === Code Replacement ===
    
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
            # JSX content
            'jsx_text_node': (f'>{text_escaped}<', f'>{{t("{key}")}}<'),
            'jsx_text_lowercase': (f'>{text_escaped}<', f'>{{t("{key}")}}<'),
            
            # HTML attributes
            'title_attr': (f'title=["\']({text_escaped})["\']', f'title={{t("{key}")}}'),
            'alt_attr': (f'alt=["\']({text_escaped})["\']', f'alt={{t("{key}")}}'),
            'placeholder_attr': (f'placeholder=["\']({text_escaped})["\']', f'placeholder={{t("{key}")}}'),
            'aria_label': (f'aria-label=["\']({text_escaped})["\']', f'aria-label={{t("{key}")}}'),
            
            # Component props
            'text_prop': (f'text=["\']({text_escaped})["\']', f'text={{t("{key}")}}'),
            'label_prop': (f'label=["\']({text_escaped})["\']', f'label={{t("{key}")}}'),
            'heading_prop': (f'heading=["\']({text_escaped})["\']', f'heading={{t("{key}")}}'),
            'title_prop': (f'title=["\']({text_escaped})["\']', f'title={{t("{key}")}}'),
            'subtitle_prop': (f'subtitle=["\']({text_escaped})["\']', f'subtitle={{t("{key}")}}'),
            'description_prop': (f'description=["\']({text_escaped})["\']', f'description={{t("{key}")}}'),
            'content_prop': (f'content=["\']({text_escaped})["\']', f'content={{t("{key}")}}'),
            'message_prop': (f'message=["\']({text_escaped})["\']', f'message={{t("{key}")}}'),
            'value_prop': (f'value=["\']({text_escaped})["\']', f'value={{t("{key}")}}'),
            'name_prop': (f'name=["\']({text_escaped})["\']', f'name={{t("{key}")}}'),
            
            # JSX elements
            'label_text': (f'<label[^>]*>{text_escaped}</label>', f'<label>{{t("{key}")}}</label>'),
            'button_text': (f'<[Bb]utton[^>]*>{text_escaped}</[Bb]utton>', f'<Button>{{t("{key}")}}</Button>'),
            'link_text': (f'<a[^>]*>{text_escaped}</a>', f'<a>{{t("{key}")}}</a>'),
            'span_text': (f'<span[^>]*>{text_escaped}</span>', f'<span>{{t("{key}")}}</span>'),
            'div_text': (f'<div[^>]*>\\s*{text_escaped}\\s*</div>', f'<div>{{t("{key}")}}</div>'),
            'p_text': (f'<p[^>]*>{text_escaped}</p>', f'<p>{{t("{key}")}}</p>'),
            'h1_text': (f'<h1[^>]*>{text_escaped}</h1>', f'<h1>{{t("{key}")}}</h1>'),
            'h2_text': (f'<h2[^>]*>{text_escaped}</h2>', f'<h2>{{t("{key}")}}</h2>'),
            'h3_text': (f'<h3[^>]*>{text_escaped}</h3>', f'<h3>{{t("{key}")}}</h3>'),
            'h4_text': (f'<h4[^>]*>{text_escaped}</h4>', f'<h4>{{t("{key}")}}</h4>'),
            'li_text': (f'<li[^>]*>{text_escaped}</li>', f'<li>{{t("{key}")}}</li>'),
            
            # Object/Array literals - keep as strings with t() call
            'object_title': (f'title:\\s*["\']({text_escaped})["\']', f'title: t("{key}")'),
            'object_description': (f'description:\\s*["\']({text_escaped})["\']', f'description: t("{key}")'),
            'object_text': (f'text:\\s*["\']({text_escaped})["\']', f'text: t("{key}")'),
            'object_label': (f'label:\\s*["\']({text_escaped})["\']', f'label: t("{key}")'),
            'object_name': (f'name:\\s*["\']({text_escaped})["\']', f'name: t("{key}")'),
            'object_heading': (f'heading:\\s*["\']({text_escaped})["\']', f'heading: t("{key}")'),
            'object_content': (f'content:\\s*["\']({text_escaped})["\']', f'content: t("{key}")'),
            'object_message': (f'message:\\s*["\']({text_escaped})["\']', f'message: t("{key}")'),
            'object_value': (f'value:\\s*["\']({text_escaped})["\']', f'value: t("{key}")'),
            
            # Template literals
            'template_literal': (f'`{text_escaped}`', f't("{key}")'),
        }
        
        if context in replacements:
            pattern, replacement = replacements[context]
            content = re.sub(pattern, replacement, content)
        
        return content
    
    # === Workflow Actions ===
    
    def run_detect(self):
        """Run detection in thread"""
        if not self.validate_project():
            return
        
        self.detect_btn.setEnabled(False)
        
        def worker():
            try:
                card_idx = self.add_status_card("🔍", "Detecting hardcoded text...", "running")
                time.sleep(0.1)  # Let signal process
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                self.update_status_card(card_idx, f"✓ Found {len(strings)} hardcoded strings", "success")
                if strings:
                    self.generate_btn.setEnabled(True)
                self.update_progress(1.0)
            except Exception as e:
                self.add_status_card("❌", f"Detection error: {str(e)}", "error")
            finally:
                self.detect_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_generate(self):
        """Run key generation"""
        if not self.detected_strings:
            return
        
        self.generate_btn.setEnabled(False)
        
        def worker():
            try:
                card_idx = self.add_status_card("🔑", "Generating translation keys...", "running")
                time.sleep(0.1)  # Let signal process
                mapping = self.generate_translation_keys(self.detected_strings)
                self.generated_keys = mapping
                self.update_status_card(card_idx, f"✓ Generated {len(mapping)} keys", "success")
                self.translate_btn.setEnabled(True)
                self.update_progress(1.0)
            except Exception as e:
                self.add_status_card("❌", f"Key generation error: {str(e)}", "error")
            finally:
                self.generate_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_translate(self):
        """Run translation"""
        if not self.generated_keys:
            return
        
        self.translate_btn.setEnabled(False)
        
        def worker():
            try:
                card_idx = self.add_status_card("🌍", f"Translating to {len(self.selected_languages)} languages...", "running")
                time.sleep(0.1)  # Let signal process
                self.translate_keys_to_languages(self.generated_keys, self.selected_languages)
                self.update_status_card(card_idx, f"✓ Translated to {len(self.selected_languages)} languages", "success")
                self.replace_btn.setEnabled(True)
                self.update_progress(1.0)
            except Exception as e:
                self.add_status_card("❌", f"Translation error: {str(e)}", "error")
            finally:
                self.translate_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_replace(self):
        """Run code replacement"""
        if not self.generated_keys:
            return
        
        file_count = len(set(info['file'] for info in self.generated_keys.values()))
        self.add_status_card("📝", f"Starting code replacement in {file_count} files...", "running")
        time.sleep(0.1)
        
        self.replace_btn.setEnabled(False)
        
        def worker():
            try:
                card_idx = self.add_status_card("✏️", "Updating source code...", "running")
                time.sleep(0.1)  # Let signal process
                self.replace_in_source_code(self.generated_keys)
                self.update_status_card(card_idx, "✅ Code replacement complete!", "success")
                self.update_progress(1.0)
                self.add_status_card("🎉", f"Done! {len(self.detected_strings)} strings, {len(self.generated_keys)} keys, {len(self.selected_languages)} languages", "success")
            except Exception as e:
                self.add_status_card("❌", f"Replacement error: {str(e)}", "error")
            finally:
                self.replace_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_complete_workflow(self):
        """Run complete workflow"""
        if not self.validate_project():
            return
        
        self.add_status_card("🚀", f"Starting complete workflow for {len(self.selected_languages)} languages...", "running")
        time.sleep(0.1)
        
        self.workflow_btn.setEnabled(False)
        for btn in [self.detect_btn, self.generate_btn, self.translate_btn, self.replace_btn]:
            btn.setEnabled(False)
        
        def worker():
            try:
                c1 = self.add_status_card("1️⃣", "Detecting text...", "running")
                time.sleep(0.1)
                strings = self.detect_hardcoded_text(self.src_dir)
                self.detected_strings = strings
                self.update_status_card(c1, f"✓ Found {len(strings)} strings", "success")
                
                if not strings:
                    self.update_progress(1.0)
                    return
                
                c2 = self.add_status_card("2️⃣", "Generating keys...", "running")
                time.sleep(0.1)
                mapping = self.generate_translation_keys(strings)
                self.generated_keys = mapping
                self.update_status_card(c2, f"✓ Generated {len(mapping)} keys", "success")
                
                c3 = self.add_status_card("3️⃣", "Translating...", "running")
                time.sleep(0.1)
                self.translate_keys_to_languages(mapping, self.selected_languages)
                self.update_status_card(c3, f"✓ Translated to {len(self.selected_languages)} languages", "success")
                
                c4 = self.add_status_card("4️⃣", "Updating code...", "running")
                time.sleep(0.1)
                self.replace_in_source_code(mapping)
                self.update_status_card(c4, "✅ Complete!", "success")
                self.update_progress(1.0)
                
                self.add_status_card("🎉", f"Complete! {len(strings)} strings, {len(mapping)} keys, {len(self.selected_languages)} languages", "success")
            except Exception as e:
                self.add_status_card("❌", f"Workflow error: {str(e)}", "error")
            finally:
                self.workflow_btn.setEnabled(True)
                self.detect_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def validate_project(self):
        """Validate project setup"""
        if not self.project_path:
            QMessageBox.critical(self, "Error", "Select a project first!")
            return False
        
        if not self.has_i18n_setup:
            QMessageBox.critical(self, "Error", "Setup i18n first!")
            return False
        
        return True
    
    # === Settings ===
    
    def load_settings(self):
        """Load saved settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                if 'languages' in settings:
                    for lang in settings['languages']:
                        if lang in self.language_checkboxes:
                            self.language_checkboxes[lang].setChecked(True)
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
    
    def run_validate(self):
        """Validate translation completeness"""
        if not self.has_i18n_setup or not self.locales_dir:
            self.add_status_card("⚠️", "No i18n setup found - cannot validate", "error")
            return
        
        self.validate_btn.setEnabled(False)
        
        def worker():
            try:
                # Use English as reference language
                reference_lang = 'en'
                card_idx = self.add_status_card("🔍", f"Validating translations against {reference_lang.upper()}...", "running")
                time.sleep(0.1)
                
                # Validate all languages
                results = self._validate_translations(reference_lang, self.selected_languages)
                
                # Show results
                if results['all_valid']:
                    self.update_status_card(card_idx, "✅ All translations are complete!", "success")
                else:
                    self.update_status_card(card_idx, f"⚠️ Found {results['total_issues']} validation issues", "pending")
                
                # Show detailed results for each language
                for lang_result in results['languages']:
                    lang = lang_result['lang']
                    if lang == reference_lang:
                        continue
                    
                    if lang_result['is_valid']:
                        self.add_status_card("✅", f"{self.SUPPORTED_LANGUAGES.get(lang, lang)}: Complete", "success")
                    else:
                        missing = lang_result['missing_keys']
                        untranslated = lang_result['untranslated_keys']
                        
                        status_text = f"{self.SUPPORTED_LANGUAGES.get(lang, lang)}: "
                        issues = []
                        if missing:
                            issues.append(f"{len(missing)} missing")
                        if untranslated:
                            issues.append(f"{len(untranslated)} untranslated")
                        status_text += ", ".join(issues)
                        
                        self.add_status_card("⚠️", status_text, "error")
                        
                        # Show sample of issues
                        if missing and len(missing) <= 5:
                            self.add_status_card("📋", f"Missing: {', '.join(missing[:5])}", "pending")
                        if untranslated and len(untranslated) <= 5:
                            self.add_status_card("📋", f"Untranslated: {', '.join(untranslated[:5])}", "pending")
                
                self.update_progress(1.0)
            except Exception as e:
                self.add_status_card("❌", f"Validation error: {str(e)}", "error")
            finally:
                self.validate_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _validate_translations(self, reference_lang: str, languages: List[str]) -> Dict:
        """Validate all translations against reference language"""
        # Load reference language
        ref_file = self.locales_dir / f'{reference_lang}.json'
        if not ref_file.exists():
            return {'all_valid': False, 'total_issues': 0, 'languages': []}
        
        with open(ref_file, 'r', encoding='utf-8') as f:
            ref_data = json.load(f)
        
        # Get all keys from reference
        ref_keys = self._get_all_keys(ref_data)
        
        results = {
            'all_valid': True,
            'total_issues': 0,
            'languages': []
        }
        
        for lang in languages:
            if lang == reference_lang:
                continue
            
            lang_file = self.locales_dir / f'{lang}.json'
            
            # Check if file exists
            if not lang_file.exists():
                results['all_valid'] = False
                results['total_issues'] += len(ref_keys)
                results['languages'].append({
                    'lang': lang,
                    'is_valid': False,
                    'missing_keys': list(ref_keys),
                    'untranslated_keys': []
                })
                continue
            
            # Load language file
            with open(lang_file, 'r', encoding='utf-8') as f:
                lang_data = json.load(f)
            
            # Get all keys from this language
            lang_keys = self._get_all_keys(lang_data)
            
            # Find missing keys
            missing_keys = ref_keys - lang_keys
            
            # Find untranslated keys (marked with [EN])
            untranslated_keys = self._find_untranslated_keys(lang_data)
            
            is_valid = len(missing_keys) == 0 and len(untranslated_keys) == 0
            
            if not is_valid:
                results['all_valid'] = False
                results['total_issues'] += len(missing_keys) + len(untranslated_keys)
            
            results['languages'].append({
                'lang': lang,
                'is_valid': is_valid,
                'missing_keys': sorted(list(missing_keys)),
                'untranslated_keys': sorted(list(untranslated_keys))
            })
        
        return results
    
    def _get_all_keys(self, data: dict, prefix: str = '') -> set:
        """Recursively get all keys from nested dict"""
        keys = set()
        
        for key, value in data.items():
            full_key = f'{prefix}.{key}' if prefix else key
            
            if isinstance(value, dict):
                keys.update(self._get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        
        return keys
    
    def _find_untranslated_keys(self, data: dict, prefix: str = '') -> set:
        """Find all keys marked with [EN] prefix"""
        untranslated = set()
        
        for key, value in data.items():
            full_key = f'{prefix}.{key}' if prefix else key
            
            if isinstance(value, dict):
                untranslated.update(self._find_untranslated_keys(value, full_key))
            elif isinstance(value, str) and value.startswith('[EN]'):
                untranslated.add(full_key)
        
        return untranslated
    
    def closeEvent(self, event):
        """Handle window close"""
        self.save_settings()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(13, 17, 23))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(28, 33, 40))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(22, 27, 34))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(28, 33, 40))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = I18nManagerQt()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
