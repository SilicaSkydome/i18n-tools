"""
i18n Manager - Universal Internationalization Tool
====================================================

A desktop application for managing translations in React/TypeScript projects.

Features:
---------
- GUI-based interface
- Auto-detect hardcoded text
- Generate translation keys
- Auto-translate to multiple languages
- Replace text in source code with i18n calls
- Works with any React/TypeScript project

Installation:
-------------
pip install -e .

Usage:
------
Run from command line:
    i18n-manager

Or run the Python script directly:
    python i18n_manager.py
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README_V2.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="i18n-manager",
    version="2.0.0",
    description="Universal internationalization tool for React/TypeScript projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="United Dutch Company",
    author_email="mike@uniteddutchcompany.com",
    url="https://github.com/uniteddutchcompany/i18n-manager",
    packages=find_packages(),
    py_modules=[
        'i18n_manager',
        'i18n_api',
        'detect_hardcoded_v2',
        'extract_and_generate_keys_v2',
        'translate_keys',
        'replace_hardcoded_v2',
        'sync_translation_keys',
        'CONFIG'
    ],
    install_requires=[
        'googletrans==4.0.0-rc1',  # For auto-translation
    ],
    entry_points={
        'console_scripts': [
            'i18n-manager=i18n_manager:main',
        ],
        'gui_scripts': [
            'i18n-manager-gui=i18n_manager:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Localization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: X11 Applications',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
    ],
    python_requires='>=3.8',
    keywords='i18n internationalization localization translation react typescript',
    project_urls={
        'Bug Reports': 'https://github.com/uniteddutchcompany/i18n-manager/issues',
        'Source': 'https://github.com/uniteddutchcompany/i18n-manager',
    },
)
