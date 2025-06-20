#!/usr/bin/env python3
"""Enhanced build script for creating standalone executable."""

import os
import platform
import subprocess
import sys
from pathlib import Path

import nicegui


def get_platform_specific_args() -> list:
    """Get platform-specific PyInstaller arguments."""
    args = []

    if platform.system() == "Darwin":  # macOS
        args.extend([
            "--osx-bundle-identifier", "com.nicegui.desktop.demo",
        ])
    elif platform.system() == "Windows":
        args.extend([
            "--icon", "resources/icon.ico",  # Windows icon
        ])

    return args


def build_executable() -> None:
    """Build the standalone executable."""

    # Get paths
    project_root = Path(__file__).parent.parent
    nicegui_dir = os.path.dirname(nicegui.__file__)

    print(f"Building for platform: {platform.system()}")
    print(f"Project root: {project_root}")
    print(f"NiceGUI directory: {nicegui_dir}")

    cmd = [
        "python", "-m", "PyInstaller",
        "main.py",
        "--name", "NiceGUI-Desktop-App",
        "--onedir",  # Directory mode for better compatibility
        "--windowed",  # No console window
        "--clean",  # Clean build artifacts
        "--noconfirm",  # Overwrite without confirmation
        "--optimize", "2",  # Optimize Python bytecode

        # NiceGUI specific
        "--add-data", f"{nicegui_dir}{os.pathsep}nicegui",

        # Hidden imports for common issues
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",

        # Exclude development/test packages to reduce size
        "--exclude-module", "pytest",
        "--exclude-module", "black",
        "--exclude-module", "ruff",
        "--exclude-module", "mypy",
        "--exclude-module", "coverage",
        "--exclude-module", "selenium",
        "--exclude-module", "setuptools",
        "--exclude-module", "pip",
        "--exclude-module", "wheel",
        "--exclude-module", "distutils",
        "--exclude-module", "unittest",
        "--exclude-module", "test",
        "--exclude-module", "pydoc",
        "--exclude-module", "doctest",
        "--exclude-module", "tkinter",
        "--exclude-module", "tkinter.ttk",
        "--exclude-module", "tkinter.tix",
        "--exclude-module", "turtle",
        "--exclude-module", "pdb",

        # Performance optimizations
        "--strip",  # Strip debug symbols
        "--upx-exclude", "vcruntime140.dll",  # Exclude problematic files from UPX
        "--noupx",  # Disable UPX compression for now (can cause issues)
    ]

    # Add platform-specific arguments
    cmd.extend(get_platform_specific_args())

    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=True, text=True)
        print("Build completed successfully!")

        # Check what was created
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            print(f"\nFiles created in {dist_dir}:")
            for item in dist_dir.iterdir():
                print(f"  - {item.name}")

        if platform.system() == "Darwin":
            app_bundle = dist_dir / "NiceGUI-Desktop-App.app"
            if app_bundle.exists():
                print(f"\n✅ macOS app bundle created: {app_bundle}")
            else:
                executable = dist_dir / "NiceGUI-Desktop-App"
                if executable.exists():
                    print(f"\n✅ Executable created: {executable}")
        else:
            executable = dist_dir / "NiceGUI-Desktop-App"
            if executable.exists():
                print(f"\n✅ Executable created: {executable}")

    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build_executable()
