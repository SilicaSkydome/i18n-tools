# -*- coding: utf-8 -*-
"""
Configuration for Dutch Delight i18n Automation
Auto-detects project structure and languages
"""

from pathlib import Path
import json

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / 'src'
LOCALES_DIR = SRC_DIR / 'i18n' / 'locales'
I18N_CONFIG = SRC_DIR / 'i18n' / 'config.ts'

# Auto-detect languages from locales folder
def get_available_languages():
    """Auto-detect available languages from locales folder"""
    if not LOCALES_DIR.exists():
        return ['en']  # Default fallback
    
    languages = []
    for file in LOCALES_DIR.glob('*.json'):
        if file.stem not in ('index', 'config'):
            languages.append(file.stem)
    
    # Ensure 'en' is always first (source language)
    if 'en' in languages:
        languages.remove('en')
        languages.insert(0, 'en')
    
    return languages

AVAILABLE_LANGUAGES = get_available_languages()
SOURCE_LANGUAGE = 'en'
TARGET_LANGUAGES = [lang for lang in AVAILABLE_LANGUAGES if lang != SOURCE_LANGUAGE]

# Language names for display
LANGUAGE_NAMES = {
    'en': 'English',
    'nl': 'Dutch',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ro': 'Romanian',
    'ru': 'Russian',
    'cs': 'Czech',
    'pl': 'Polish',
    'el': 'Greek',
    'tl': 'Filipino (Tagalog)',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
}

# Scan settings
FILE_EXTENSIONS = ['.tsx', '.jsx']
EXCLUDE_DIRS = ['node_modules', 'dist', 'build', '.git', 'coverage', 'i18n-tools']
MIN_CONFIDENCE_SCORE = 70  # Only process high-confidence strings

# Report configuration
def print_config():
    """Print current configuration"""
    print("\n" + "="*70)
    print("DUTCH DELIGHT i18n AUTOMATION - Configuration")
    print("="*70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Source dir: {SRC_DIR}")
    print(f"Locales dir: {LOCALES_DIR}")
    print(f"\nSource language: {SOURCE_LANGUAGE} ({LANGUAGE_NAMES.get(SOURCE_LANGUAGE, SOURCE_LANGUAGE)})")
    print(f"Target languages: {', '.join([f'{lang} ({LANGUAGE_NAMES.get(lang, lang)})' for lang in TARGET_LANGUAGES])}")
    print(f"Total languages: {len(AVAILABLE_LANGUAGES)}")
    print(f"\nMin confidence score: {MIN_CONFIDENCE_SCORE}")
    print(f"File extensions: {', '.join(FILE_EXTENSIONS)}")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_config()
