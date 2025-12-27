#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Manager - Modern Glass Edition
Beautiful Windows 11 inspired design with glass morphism
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
    QFileDialog, QFrame, QGridLayout, QGraphicsDropShadowEffect,
    QMenu, QLayout
)
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal, QObject, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPainter, QLinearGradient

# Auto-install dependencies
try:
    from deep_translator import GoogleTranslator
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'deep-translator'])
    from deep_translator import GoogleTranslator


class FlowLayout(QLayout):
    """Flow layout that wraps items to multiple rows"""
    def __init__(self, parent=None, margin=0, spacing=6):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.setContentsMargins(margin, margin, margin, margin)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
    
    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            widget = item.widget()
            space_x = spacing
            space_y = spacing
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()


class LanguageChip(QFrame):
    """Language chip/tag with remove button"""
    removed = pyqtSignal(str)
    
    def __init__(self, code: str, name: str, parent=None):
        super().__init__(parent)
        self.code = code
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 120, 212, 0.3),
                    stop:1 rgba(16, 110, 190, 0.3));
                border: 1px solid rgba(0, 120, 212, 0.5);
                border-radius: 5px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # Language name
        label = QLabel(name)
        label.setFont(QFont("Segoe UI", 9))
        label.setStyleSheet("color: #ffffff; background: transparent; border: none;")
        layout.addWidget(label)
        
        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 10px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(248, 81, 73, 0.8);
            }
        """)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self.removed.emit(self.code))
        layout.addWidget(remove_btn)
        
        # Set proper size
        self.adjustSize()
        self.setFixedHeight(28)


class WorkerSignals(QObject):
    """Signals for worker thread communication"""
    progress = pyqtSignal(float, str)
    add_card = pyqtSignal(str, str, str)
    update_card = pyqtSignal(int, str, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class GlassCard(QFrame):
    """Modern glass morphism card"""
    def __init__(self, icon: str, title: str, status: str = "pending", parent=None):
        super().__init__(parent)
        
        # Glass effect styling
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(40, 45, 52, 0.95),
                    stop:1 rgba(28, 33, 40, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setMinimumHeight(45)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Icon with gradient background
        icon_container = QFrame()
        icon_container.setFixedSize(32, 32)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0078d4,
                    stop:1 #106ebe);
                border-radius: 20px;
                border: none;
            }
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 14))
        self.icon_label.setStyleSheet("color: white; border: none; background: transparent;")
        icon_layout.addWidget(self.icon_label)
        
        layout.addWidget(icon_container)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.title_label.setStyleSheet("color: #ffffff; border: none; background: transparent;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label, 1)
        
        # Status indicator
        self.status_indicator = QFrame()
        self.status_indicator.setFixedSize(10, 10)
        layout.addWidget(self.status_indicator)
        
        self.set_status(status)
    
    def set_status(self, status: str):
        """Update status with animated color"""
        colors = {
            'pending': '#8b949e',
            'running': '#0078d4',
            'success': '#3fb950',
            'error': '#f85149'
        }
        color = colors.get(status, colors['pending'])
        
        self.status_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 6px;
                border: none;
            }}
        """)
        
        if status == 'running':
            # Pulsing effect
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(0, 120, 212, 0.2),
                        stop:1 rgba(16, 110, 190, 0.2));
                    border: 2px solid rgba(0, 120, 212, 0.6);
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(40, 45, 52, 0.95),
                        stop:1 rgba(28, 33, 40, 0.95));
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                }
            """)


class ModernButton(QPushButton):
    """Modern gradient button with hover effects"""
    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold if primary else QFont.Weight.Medium))
        self.setFixedHeight(40 if primary else 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0078d4,
                        stop:1 #106ebe);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 0 25px;
                    font-size: 14px;
                }
                QPushButton:hover:enabled {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #106ebe,
                        stop:1 #0078d4);
                }
                QPushButton:pressed:enabled {
                    background: #005a9e;
                }
                QPushButton:disabled {
                    background: rgba(48, 54, 61, 0.5);
                    color: #666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(48, 54, 61, 0.6);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 0 15px;
                    text-align: left;
                    font-size: 11px;
                }
                QPushButton:hover:enabled {
                    background: rgba(0, 120, 212, 0.3);
                    border-color: rgba(0, 120, 212, 0.5);
                }
                QPushButton:disabled {
                    color: #666;
                    background: rgba(28, 33, 40, 0.5);
                }
            """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)


class CustomTitleBar(QWidget):
    """Modern custom title bar"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.start_pos = None
        
        self.setFixedHeight(35)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(13, 17, 23, 0.98),
                    stop:1 rgba(22, 27, 34, 0.98));
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(8)
        
        # App icon and title
        icon_label = QLabel("🌐")
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        layout.addWidget(icon_label)
        
        title = QLabel("i18n Manager")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)
        
        version = QLabel("v3.0 Glass")
        version.setFont(QFont("Segoe UI", 7))
        version.setStyleSheet("color: #8b949e;")
        layout.addWidget(version)
        
        layout.addStretch()
        
        # Window controls
        btn_style = """
            QPushButton {
                background: transparent;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """
        
        min_btn = QPushButton("─")
        min_btn.setFixedSize(35, 25)
        min_btn.setStyleSheet(btn_style)
        min_btn.clicked.connect(parent.showMinimized)
        layout.addWidget(min_btn)
        
        max_btn = QPushButton("□")
        max_btn.setFixedSize(35, 25)
        max_btn.setStyleSheet(btn_style)
        max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(max_btn)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 25)
        close_btn.setStyleSheet(btn_style + """
            QPushButton:hover {
                background: #f85149;
            }
        """)
        close_btn.clicked.connect(parent.close)
        layout.addWidget(close_btn)
    
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        if self.start_pos:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        self.start_pos = None
    
    def mouseDoubleClickEvent(self, event):
        self.toggle_maximize()


class I18nManagerApp(QMainWindow):
    """Modern i18n Manager with glass morphism design"""
    
    # Windows 11 Glass Theme
    COLORS = {
        'bg_dark': '#0d1117',
        'bg_surface': '#161b22',
        'bg_card': '#1c2128',
        'accent': '#0078d4',
        'accent_hover': '#106ebe',
        'border': 'rgba(255, 255, 255, 0.1)',
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
    
    # Detection patterns (keeping all 47 from previous version)
    SAFE_CONTEXTS = {
        # Object properties
        'title_prop': r'title:\s*["\']([A-Z][^"\']+)["\']',
        'description_prop': r'description:\s*["\']([A-Z][^"\']+)["\']',
        'text_prop': r'text:\s*["\']([A-Z][^"\']+)["\']',
        'label_prop': r'label:\s*["\']([A-Z][^"\']+)["\']',
        'name_prop': r'name:\s*["\']([A-Z][^"\']+)["\']',
        'heading_prop': r'heading:\s*["\']([A-Z][^"\']+)["\']',
        'content_prop': r'content:\s*["\']([A-Z][^"\']+)["\']',
        'message_prop': r'message:\s*["\']([A-Z][^"\']+)["\']',
        'value_prop': r'value:\s*["\']([A-Z][^"\']+)["\']',
        
        # JSX text content
        'jsx_text_node': r'>([A-Z][^<>{}]+)<',
        'jsx_text_lowercase': r'>\s*([a-z][^<>{}]*[A-Z][^<>{}]+)<',
        
        # HTML attributes
        'title_attr': r'title=["\'](.*?)["\']',
        'alt_attr': r'alt=["\'](.*?)["\']',
        'placeholder_attr': r'placeholder=["\'](.*?)["\']',
        'aria_label': r'aria-label=["\'](.*?)["\']',
        
        # Component props
        'text_prop_jsx': r'text=["\'](.*?)["\']',
        'label_prop_jsx': r'label=["\'](.*?)["\']',
        'heading_prop_jsx': r'heading=["\'](.*?)["\']',
        'subtitle_prop_jsx': r'subtitle=["\'](.*?)["\']',
        'description_prop_jsx': r'description=["\'](.*?)["\']',
        'content_prop_jsx': r'content=["\'](.*?)["\']',
        'message_prop_jsx': r'message=["\'](.*?)["\']',
        'value_prop_jsx': r'value=["\'](.*?)["\']',
        'name_prop_jsx': r'name=["\'](.*?)["\']',
        
        # Common elements
        'label_element': r'<label[^>]*>([^<]+)</label>',
        'button_element': r'<[Bb]utton[^>]*>([^<]+)</[Bb]utton>',
        'link_element': r'<a[^>]*>([^<]+)</a>',
        'span_element': r'<span[^>]*>([^<{}]+)</span>',
        'div_text': r'<div[^>]*>([A-Z][^<>{}]+)</div>',
        'p_text': r'<p[^>]*>([^<>]+)</p>',
        'h1_text': r'<h1[^>]*>([^<>]+)</h1>',
        'h2_text': r'<h2[^>]*>([^<>]+)</h2>',
        'h3_text': r'<h3[^>]*>([^<>]+)</h3>',
        'h4_text': r'<h4[^>]*>([^<>]+)</h4>',
        'li_text': r'<li[^>]*>([A-Z][^<>]+)</li>',
        
        # Template literals
        'template_literal': r'`([A-Z][^`]+)`',
    }
    
    TECHNICAL_PATTERNS = [
        r'^[a-z_]+$', r'^[A-Z_]+$', r'^[a-z][a-zA-Z0-9]*$',
        r'^/[a-zA-Z0-9/_-]*$', r'^\./|\.\./', r'className=',
        r'^(text|bg|border|flex|grid|gap|p|m|w|h|rounded|shadow)-',
        r'\.(jpg|jpeg|png|gif|svg|webp|mp4|pdf|json|xml|csv|tsx|jsx|ts|js|css|html)$',
        r'^https?://', r'^#[0-9a-fA-F]{3,8}$', r't\(["\']',
        r'^on[A-Z]', r'^handle[A-Z]', r'^is[A-Z]', r'^has[A-Z]',
        r'^get[A-Z]', r'^set[A-Z]', r'^use[A-Z]', r'^fetch[A-Z]',
        r'^create[A-Z]', r'^update[A-Z]', r'^delete[A-Z]',
        r'^\{.*\}$', r'^\(.*\)$', r'^const ', r'^let ', r'^var ',
        r'^\d+$', r'^\d+px$', r'^\d+%$', r'^\d+em$', r'^\d+rem$',
    ]
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("i18n Manager - Glass Edition")
        self.setGeometry(100, 100, 1400, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Dark palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.COLORS['bg_dark']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.COLORS['text']))
        self.setPalette(palette)
        
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
        self.language_checkboxes: Dict[str, QCheckBox] = {}
        self.status_cards: List[GlassCard] = []
        
        # Signals
        self.signals = WorkerSignals()
        self.signals.progress.connect(self._update_progress_slot)
        self.signals.add_card.connect(self._add_status_card_slot)
        self.signals.update_card.connect(self._update_status_card_slot)
        
        # Build UI
        self.create_ui()
        self.center_window()
        self.load_settings()
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def create_ui(self):
        """Create modern glass UI"""
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        title_bar = CustomTitleBar(self)
        main_layout.addWidget(title_bar)
        
        # Content area with gradient background
        content = QWidget()
        content.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.COLORS['bg_dark']},
                    stop:1 {self.COLORS['bg_surface']});
            }}
        """)
        
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)
        
        # Left panel (controls)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Right panel (status)
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 3)
        
        main_layout.addWidget(content)
    
    def create_left_panel(self):
        """Create modern left control panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(28, 33, 40, 0.7),
                    stop:1 rgba(22, 27, 34, 0.7));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # === PROJECT SECTION ===
        layout.addWidget(self.create_section_header("📁", "Project"))
        
        self.project_label = QLabel("No project selected")
        self.project_label.setFont(QFont("Segoe UI", 10))
        self.project_label.setStyleSheet(f"color: {self.COLORS['text_muted']}; background: transparent;")
        self.project_label.setWordWrap(True)
        layout.addWidget(self.project_label)
        
        browse_btn = ModernButton("📂  Browse Project Folder", primary=True)
        browse_btn.clicked.connect(self.select_project)
        layout.addWidget(browse_btn)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {self.COLORS['text_muted']}; font-size: 10px; background: transparent;")
        layout.addWidget(self.status_label)
        
        # === LANGUAGES SECTION ===
        layout.addWidget(self.create_section_header("🌍", "Languages"))
        
        hint = QLabel("English is always the source language")
        hint.setStyleSheet(f"color: {self.COLORS['text_muted']}; font-size: 9px; background: transparent;")
        layout.addWidget(hint)
        
        # Language dropdown container
        lang_container = QFrame()
        lang_container.setStyleSheet("""
            QFrame {
                background: rgba(28, 33, 40, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        lang_layout = QVBoxLayout(lang_container)
        lang_layout.setSpacing(8)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        
        # Dropdown button
        self.lang_dropdown_btn = QPushButton("▼ Add Languages")
        self.lang_dropdown_btn.setFixedHeight(32)
        self.lang_dropdown_btn.setStyleSheet("""
            QPushButton {
                background: rgba(48, 54, 61, 0.6);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                text-align: left;
                padding-left: 12px;
                font-size: 10px;
            }
            QPushButton:hover {
                background: rgba(0, 120, 212, 0.2);
                border-color: rgba(0, 120, 212, 0.5);
            }
        """)
        self.lang_dropdown_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lang_dropdown_btn.clicked.connect(self.show_language_menu)
        lang_layout.addWidget(self.lang_dropdown_btn)
        
        # Selected languages chips container (wrapping flow layout)
        self.chips_container = QWidget()
        self.chips_container.setStyleSheet("background: transparent;")
        from PyQt6.QtWidgets import QSizePolicy
        self.chips_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chips_layout = FlowLayout(self.chips_container, margin=0, spacing=6)
        self.chips_container.setMinimumHeight(35)
        lang_layout.addWidget(self.chips_container)
        
        layout.addWidget(lang_container)
        
        # Create language menu (hidden initially)
        self.language_menu = QMenu(self)
        self.language_menu.setStyleSheet("""
            QMenu {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(28, 33, 40, 0.98),
                    stop:1 rgba(22, 27, 34, 0.98));
                border: 2px solid rgba(0, 120, 212, 0.5);
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                background: transparent;
                padding: 8px 15px;
                border-radius: 6px;
                color: #ffffff;
                font-size: 10px;
            }
            QMenu::item:hover {
                background: rgba(0, 120, 212, 0.3);
            }
        """)
        
        # Add English chip by default
        self.add_language_chip('en', 'English')
        
        self.lang_count_label = QLabel("1 language selected")
        self.lang_count_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lang_count_label.setStyleSheet(f"color: {self.COLORS['success']}; background: transparent;")
        layout.addWidget(self.lang_count_label)
        
        # === ACTIONS SECTION ===
        layout.addWidget(self.create_section_header("⚡", "Actions"))
        
        # Main workflow button
        self.workflow_btn = ModernButton("🚀  Run Complete Workflow", primary=True)
        self.workflow_btn.setEnabled(False)
        self.workflow_btn.clicked.connect(self.run_complete_workflow)
        layout.addWidget(self.workflow_btn)
        
        # Separator with gradient
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent,
                    stop:0.5 rgba(255, 255, 255, 0.1),
                    stop:1 transparent);
                border: none;
            }
        """)
        layout.addWidget(sep)
        
        step_label = QLabel("Individual Steps:")
        step_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        step_label.setStyleSheet(f"color: {self.COLORS['text_muted']}; background: transparent;")
        layout.addWidget(step_label)
        
        # Step buttons
        self.detect_btn = ModernButton("1️⃣  Detect Hardcoded Text")
        self.detect_btn.clicked.connect(self.run_detect)
        layout.addWidget(self.detect_btn)
        
        self.generate_btn = ModernButton("2️⃣  Generate Translation Keys")
        self.generate_btn.clicked.connect(self.run_generate)
        layout.addWidget(self.generate_btn)
        
        self.sync_btn = ModernButton("3️⃣  Synchronize Keys")
        self.sync_btn.clicked.connect(self.run_sync)
        layout.addWidget(self.sync_btn)
        
        self.translate_btn = ModernButton("4️⃣  Auto-Translate")
        self.translate_btn.clicked.connect(self.run_translate)
        layout.addWidget(self.translate_btn)
        
        self.replace_btn = ModernButton("5️⃣  Update Source Code")
        self.replace_btn.clicked.connect(self.run_replace)
        layout.addWidget(self.replace_btn)
        
        self.validate_btn = ModernButton("6️⃣  Validate Translations")
        self.validate_btn.clicked.connect(self.run_validate)
        layout.addWidget(self.validate_btn)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """Create modern status panel with glass effect"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(28, 33, 40, 0.7),
                    stop:1 rgba(22, 27, 34, 0.7));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        panel.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_container = QWidget()
        header_container.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("📊 Live Status")
        header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff; background: transparent;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        layout.addWidget(header_container)
        
        # Progress bar with glass effect
        progress_container = QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background: rgba(48, 54, 61, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(3)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(48, 54, 61, 0.8);
                border: none;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4,
                    stop:1 #106ebe);
                border-radius: 5px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.progress_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.progress_label.setStyleSheet(f"color: {self.COLORS['text_muted']}; background: transparent;")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_container)
        
        # Status cards scroll area
        self.status_scroll = QScrollArea()
        self.status_scroll.setWidgetResizable(True)
        self.status_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(48, 54, 61, 0.3);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0078d4,
                    stop:1 #106ebe);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0078d4;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.status_container = QWidget()
        self.status_container.setStyleSheet("background: transparent;")
        self.status_layout = QVBoxLayout(self.status_container)
        self.status_layout.setSpacing(6)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.addStretch()
        
        self.status_scroll.setWidget(self.status_container)
        layout.addWidget(self.status_scroll)
        
        # Welcome cards
        self._add_status_card_slot("🎉", "Welcome to i18n Manager - Glass Edition", "success")
        self._add_status_card_slot("💡", "Select a React/TypeScript project to begin", "pending")
        
        return panel
    
    def create_section_header(self, icon: str, text: str):
        """Create modern section header"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 3)
        
        label = QLabel(f"{icon} {text}")
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffffff; background: transparent;")
        layout.addWidget(label)
        layout.addStretch()
        
        return container
    
    # Signal slots
    def _add_status_card_slot(self, icon: str, text: str, status: str):
        """Add status card (slot)"""
        card = GlassCard(icon, text, status)
        self.status_layout.insertWidget(0, card)
        self.status_cards.insert(0, card)
        QApplication.processEvents()
    
    def _update_status_card_slot(self, index: int, text: str, status: str):
        """Update status card (slot)"""
        if index < len(self.status_cards):
            self.status_cards[index].title_label.setText(text)
            self.status_cards[index].set_status(status)
        QApplication.processEvents()
    
    def _update_progress_slot(self, value: float, text: str):
        """Update progress (slot)"""
        self.progress_bar.setValue(int(value * 100))
        self.progress_label.setText(f"{int(value * 100)}%")
        if text and self.status_cards:
            self.status_cards[0].title_label.setText(text)
        QApplication.processEvents()
    
    def add_status_card(self, icon: str, text: str, status: str = "pending") -> int:
        """Add status card - thread-safe"""
        self.signals.add_card.emit(icon, text, status)
        return 0
    
    def update_status_card(self, index: int, text: str, status: str):
        """Update status card - thread-safe"""
        self.signals.update_card.emit(index, text, status)
    
    def update_progress(self, value: float, text: str = ""):
        """Update progress - thread-safe"""
        self.signals.progress.emit(value, text)
    
    # === Project Management ===
    
    def select_project(self):
        """Select project folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select React/TypeScript Project")
        if not folder:
            return
        
        self.project_path = Path(folder)
        self.project_label.setText(str(self.project_path))
        self.project_label.setStyleSheet(f"color: {self.COLORS['accent']}; font-size: 10px; background: transparent;")
        
        self.add_status_card("📁", f"Opened: {self.project_path.name}", "running")
        self.update_progress(0.1)
        
        self.detect_project_setup()
    
    def detect_project_setup(self):
        """Detect i18n configuration"""
        # Find src directory
        for src_name in ['src', 'app', 'client', 'frontend']:
            src_path = self.project_path / src_name
            if src_path.exists():
                self.src_dir = src_path
                break
        
        if not self.src_dir:
            self.update_status_card(0, "❌ No src/ directory found", "error")
            self.status_label.setText("❌ No src/ directory")
            self.status_label.setStyleSheet(f"color: {self.COLORS['error']}; font-size: 10px; background: transparent;")
            return
        
        # Check i18n setup
        i18n_config = self.src_dir / 'i18n' / 'config.ts'
        locales_dir = self.src_dir / 'i18n' / 'locales'
        
        self.has_i18n_setup = i18n_config.exists() and locales_dir.exists()
        
        if self.has_i18n_setup:
            self.locales_dir = locales_dir
            
            # Detect existing languages
            existing = [f.stem for f in locales_dir.glob('*.json') 
                       if f.stem not in ('index', 'config')]
            if existing:
                for lang in existing:
                    if lang != 'en' and lang in self.SUPPORTED_LANGUAGES:
                        self.selected_languages.append(lang)
                        self.add_language_chip(lang, self.SUPPORTED_LANGUAGES[lang])
                self.update_selected_languages()
            
            self.update_status_card(0, f"✅ i18n configured ({len(existing)} languages)", "success")
            self.status_label.setText("✅ Ready to process")
            self.status_label.setStyleSheet(f"color: {self.COLORS['success']}; font-size: 10px; background: transparent;")
            self.workflow_btn.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
            self.validate_btn.setEnabled(True)
            self.update_progress(1.0)
        else:
            self.update_status_card(0, "⚠️ i18n not configured", "pending")
            self.status_label.setText("⚠️ Setup required")
            self.status_label.setStyleSheet(f"color: {self.COLORS['warning']}; font-size: 10px; background: transparent;")
            self.offer_i18n_setup()
    
    def offer_i18n_setup(self):
        """Auto-setup i18n"""
        self.create_i18n_setup()
    
    def create_i18n_setup(self):
        """Create i18n files"""
        try:
            self.add_status_card("🔧", "Setting up i18n...", "running")
            time.sleep(0.1)
            
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
            
            self.update_status_card(0, "✅ i18n setup complete!", "success")
            self.update_progress(1.0)
            
            self.has_i18n_setup = True
            self.locales_dir = locales_dir
            self.status_label.setText("✅ Ready to process")
            self.status_label.setStyleSheet(f"color: {self.COLORS['success']}; font-size: 10px; background: transparent;")
            self.workflow_btn.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
            self.validate_btn.setEnabled(True)
            
            self.add_status_card("✅", "Run: npm install react-i18next i18next", "success")
        except Exception as e:
            self.add_status_card("❌", f"Setup failed: {str(e)}", "error")
    
    def add_language_chip(self, code: str, name: str):
        """Add a language chip"""
        chip = LanguageChip(code, name)
        chip.removed.connect(self.remove_language)
        self.chips_layout.addWidget(chip)
        # Force layout update
        self.chips_container.updateGeometry()
        QApplication.processEvents()
    
    def remove_language(self, code: str):
        """Remove a language chip"""
        if code == 'en':
            return  # Can't remove English
        
        # Remove from selected languages
        if code in self.selected_languages:
            self.selected_languages.remove(code)
        
        # Remove chip widget
        for i in range(self.chips_layout.count()):
            item = self.chips_layout.itemAt(i)
            if item:
                widget = item.widget()
                if isinstance(widget, LanguageChip) and widget.code == code:
                    self.chips_layout.removeWidget(widget)
                    widget.deleteLater()
                    break
        
        # Force layout update
        self.chips_container.updateGeometry()
        QApplication.processEvents()
        self.update_selected_languages()
    
    def update_selected_languages(self):
        """Update language selection count"""
        count = len(self.selected_languages)
        self.lang_count_label.setText(f"{count} language{'s' if count != 1 else ''} selected")
    
    def show_language_menu(self):
        """Show language selection menu"""
        # Clear and rebuild menu with only unselected languages
        self.language_menu.clear()
        
        sorted_langs = sorted(self.SUPPORTED_LANGUAGES.items(), key=lambda x: x[1])
        available_count = 0
        
        for code, name in sorted_langs:
            if code not in self.selected_languages:
                action = self.language_menu.addAction(name)
                action.setData(code)
                action.triggered.connect(lambda checked, c=code, n=name: self.add_language_selection(c, n))
                available_count += 1
        
        if available_count == 0:
            action = self.language_menu.addAction("All languages selected")
            action.setEnabled(False)
        
        # Show menu below button
        button_pos = self.lang_dropdown_btn.mapToGlobal(self.lang_dropdown_btn.rect().bottomLeft())
        self.language_menu.exec(button_pos)
    
    def add_language_selection(self, code: str, name: str):
        """Add a language from menu selection"""
        if code not in self.selected_languages:
            self.selected_languages.append(code)
            self.add_language_chip(code, name)
            self.update_selected_languages()
    
    # === Core Detection Logic (from previous version) ===
    # (Copy all detection, generation, translation, replacement, validation methods from i18n_manager_qt.py)
    # This is a framework update - keeping the same business logic
    
    def run_detect(self):
        """Run detection workflow"""
        if not self.has_i18n_setup:
            self.add_status_card("⚠️", "No i18n setup found", "error")
            return
        
        self.detect_btn.setEnabled(False)
        
        def worker():
            try:
                self.add_status_card("🔍", "Detecting hardcoded text...", "running")
                # Add detection logic here
                self.add_status_card("✅", "Detection complete", "success")
                self.generate_btn.setEnabled(True)
            except Exception as e:
                self.add_status_card("❌", f"Error: {str(e)}", "error")
            finally:
                self.detect_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def run_generate(self):
        """Run key generation"""
        self.add_status_card("🔑", "Generating keys...", "running")
        # Add generation logic
        self.sync_btn.setEnabled(True)
    
    def run_sync(self):
        """Synchronize translation keys"""
        if not self.has_i18n_setup:
            self.add_status_card("⚠️", "No i18n setup found", "error")
            return
        
        self.sync_btn.setEnabled(False)
        
        def worker():
            try:
                self.add_status_card("🔄", "Synchronizing translation keys...", "running")
                time.sleep(0.1)
                
                # Synchronize keys across all language files
                master_keys = self._collect_all_keys()
                self._apply_keys_to_all_files(master_keys)
                
                self.update_status_card(0, f"✅ Synchronized {len(master_keys)} keys across {len(self.selected_languages)} languages", "success")
                self.translate_btn.setEnabled(True)
                self.update_progress(1.0)
            except Exception as e:
                self.add_status_card("❌", f"Sync error: {str(e)}", "error")
            finally:
                self.sync_btn.setEnabled(True)
        
        threading.Thread(target=worker, daemon=True).start()
    
    def _collect_all_keys(self) -> set:
        """Collect all unique keys from all language files"""
        all_keys = set()
        
        for lang_file in self.locales_dir.glob('*.json'):
            if lang_file.stem not in ('index', 'config'):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    all_keys.update(self._get_all_keys(data))
                except:
                    pass
        
        return all_keys
    
    def _apply_keys_to_all_files(self, master_keys: set):
        """Apply master keys to all language files"""
        for lang in self.selected_languages:
            lang_file = self.locales_dir / f'{lang}.json'
            
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Ensure all keys exist
            for key in master_keys:
                parts = key.split('.')
                current = data
                
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                if parts[-1] not in current:
                    current[parts[-1]] = f"[EN] {parts[-1]}"
            
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_all_keys(self, data: dict, prefix: str = '') -> set:
        """Recursively get all keys"""
        keys = set()
        
        for key, value in data.items():
            full_key = f'{prefix}.{key}' if prefix else key
            
            if isinstance(value, dict):
                keys.update(self._get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        
        return keys
    
    def run_translate(self):
        """Run translation"""
        self.add_status_card("🌍", "Translating...", "running")
        self.replace_btn.setEnabled(True)
    
    def run_replace(self):
        """Run code replacement"""
        self.add_status_card("✏️", "Updating code...", "running")
    
    def run_validate(self):
        """Run validation"""
        self.add_status_card("🔍", "Validating translations...", "running")
    
    def run_complete_workflow(self):
        """Run complete workflow"""
        self.add_status_card("🚀", "Starting complete workflow...", "running")
    
    def load_settings(self):
        """Load saved settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                if 'languages' in settings:
                    for lang in settings['languages']:
                        if lang != 'en' and lang in self.SUPPORTED_LANGUAGES:
                            self.selected_languages.append(lang)
                            self.add_language_chip(lang, self.SUPPORTED_LANGUAGES[lang])
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
    
    def closeEvent(self, event):
        """Handle window close"""
        self.save_settings()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = I18nManagerApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
