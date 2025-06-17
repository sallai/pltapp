#!/usr/bin/env python3
"""Development environment setup script."""

import os
import subprocess
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+."""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11+ is required")
        sys.exit(1)
    print(f"Python version: {sys.version}")

def create_venv():
    """Create virtual environment if it doesn't exist."""
    if not Path('venv').exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    else:
        print("Virtual environment already exists")

def install_dependencies(qt_toolkit='pyside6'):
    """Install development dependencies with specified Qt toolkit."""
    pip_path = 'venv/bin/pip' if os.name != 'nt' else 'venv\\Scripts\\pip.exe'
    
    print(f"Installing development dependencies with {qt_toolkit.upper()}...")
    
    # Install base dependencies first
    if qt_toolkit.lower() == 'pyqt6':
        subprocess.run([pip_path, 'install', '-r', 'requirements/pyqt6.txt'], check=True)
    else:
        subprocess.run([pip_path, 'install', '-r', 'requirements/pyside6.txt'], check=True)
    
    # Install dev dependencies
    subprocess.run([pip_path, 'install', '-r', 'requirements/dev.txt'], check=True)

def setup_pre_commit():
    """Setup pre-commit hooks."""
    python_path = 'venv/bin/python' if os.name != 'nt' else 'venv\\Scripts\\python.exe'
    
    print("Setting up pre-commit hooks...")
    subprocess.run([python_path, '-m', 'pre_commit', 'install'], check=True)

def main():
    """Main setup process."""
    qt_toolkit = 'pyside6'  # Default
    if len(sys.argv) > 1:
        toolkit_arg = sys.argv[1].lower()
        if toolkit_arg in ['pyside6', 'pyqt6']:
            qt_toolkit = toolkit_arg
        else:
            print(f"Unknown toolkit: {toolkit_arg}")
            print("Available options: pyside6, pyqt6")
            sys.exit(1)
    
    print(f"Setting up development environment with {qt_toolkit.upper()}...")
    check_python_version()
    create_venv()
    install_dependencies(qt_toolkit)
    
    try:
        setup_pre_commit()
    except subprocess.CalledProcessError:
        print("Pre-commit setup skipped (pre-commit config not found)")
    
    print(f"\nDevelopment environment setup complete with {qt_toolkit.upper()}!")
    print("\nTo activate the environment:")
    if os.name != 'nt':
        print("  source venv/bin/activate")
    else:
        print("  venv\\Scripts\\activate")
    
    print(f"\nNote: This environment uses {qt_toolkit.upper()}. PyQt6 and PySide6 cannot coexist.")
    print("To switch toolkits, create a new environment or run setup again with the other toolkit.")

if __name__ == '__main__':
    main()