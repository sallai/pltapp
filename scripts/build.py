#!/usr/bin/env python3
"""Enhanced build script for creating standalone executable with splash screen."""

import os
import subprocess
import sys
from pathlib import Path

import nicegui


def build_executable() -> None:
    """Build the standalone executable."""

    # Get paths
    project_root = Path(__file__).parent.parent
    nicegui_dir = os.path.dirname(nicegui.__file__)

    print(f"NiceGUI directory: {nicegui_dir}")

    # Build command - using onedir for better macOS compatibility
    cmd = [
        "python",
        "-m",
        "PyInstaller",
        "main.py",  # your main file with ui.run()
        "--name",
        "NiceGUI-Desktop-App",  # name of your app
        "--onedir",  # directory mode (better for macOS .app bundles)
        "--windowed",  # prevent console appearing
        "--add-data",
        f"{nicegui_dir}{os.pathsep}nicegui",  # include NiceGUI files
        "--clean",  # clean build artifacts
        "--noconfirm",  # overwrite without confirmation
        "--optimize",
        "2",  # optimize Python bytecode
    ]

    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, cwd=project_root, check=True)
        print("Build completed successfully!")
        print("Executable created: dist/NiceGUI-Desktop-App")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
