#!/usr/bin/env python3
"""
Development environment setup script.

Automates the creation of virtual environment and installation of dependencies
for the NiceGUI desktop application project.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """
    Run a shell command and return success status.

    Args:
        command: Command to run as list of strings
        description: Human-readable description of the command

    Returns:
        True if command succeeded, False otherwise
    """
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description} failed")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def setup_virtual_environment() -> bool:
    """Create and activate virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print("Virtual environment already exists, skipping creation")
        return True

    print("Creating virtual environment...")
    if not run_command(
        [sys.executable, "-m", "venv", "venv"], "Create virtual environment"
    ):
        return False

    print("Virtual environment created successfully")
    return True


def install_dependencies() -> bool:
    """Install project dependencies."""
    # Determine the correct pip path for the virtual environment
    if os.name == "nt":  # Windows
        pip_path = Path("venv/Scripts/pip")
    else:  # Unix-like (macOS, Linux)
        pip_path = Path("venv/bin/pip")

    if not pip_path.exists():
        print(f"Error: pip not found at {pip_path}")
        return False

    # Install development dependencies
    requirements_file = Path("requirements/dev.txt")
    if not requirements_file.exists():
        print(f"Error: Requirements file not found at {requirements_file}")
        return False

    print("Installing dependencies...")
    if not run_command(
        [str(pip_path), "install", "-r", str(requirements_file)],
        "Install development dependencies",
    ):
        return False

    print("Dependencies installed successfully")
    return True


def verify_installation() -> bool:
    """Verify that key packages are installed correctly."""
    # Determine the correct python path for the virtual environment
    if os.name == "nt":  # Windows
        python_path = Path("venv/Scripts/python")
    else:  # Unix-like (macOS, Linux)
        python_path = Path("venv/bin/python")

    if not python_path.exists():
        print(f"Error: Python not found at {python_path}")
        return False

    # Test import of key packages
    test_imports = [
        "nicegui",
        "fastapi",
        "uvicorn",
        "plotly",
        "numpy",
        "webview",
        "ruff",
        "black",
        "mypy",
        "pytest",
    ]

    print("Verifying package installations...")
    for package in test_imports:
        if not run_command(
            [str(python_path), "-c", f"import {package}"], f"Test import {package}"
        ):
            print(f"Warning: Package {package} may not be installed correctly")
            return False

    print("All packages verified successfully")
    return True


def main() -> None:
    """Main setup process."""
    print("Setting up development environment for NiceGUI Desktop App...")
    print("=" * 60)

    success = True

    # Step 1: Create virtual environment
    if not setup_virtual_environment():
        success = False

    # Step 2: Install dependencies
    if success and not install_dependencies():
        success = False

    # Step 3: Verify installation
    if success and not verify_installation():
        success = False

    print("=" * 60)
    if success:
        print("✅ Development environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate the virtual environment:")
        if os.name == "nt":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Run the application:")
        print("   python nicegui_desktop_app.py")
        print("3. Build executable:")
        print("   python scripts/build_executable.py")
    else:
        print("❌ Development environment setup failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
