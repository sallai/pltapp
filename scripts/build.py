#!/usr/bin/env python3
"""Build script for creating standalone executable using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_build_dirs():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")

def build_executable():
    """Build the executable using PyInstaller."""
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', 'ww',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        print("Executable available in dist/")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)

def main():
    """Main build process."""
    print("Starting build process...")
    clean_build_dirs()
    build_executable()

if __name__ == '__main__':
    main()