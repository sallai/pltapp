#!/usr/bin/env python3
"""
NiceGUI Desktop Application Entry Point

Minimal entry point that imports and runs the main application.
"""

from src.app import DesktopApp


def main() -> None:
    """Application entry point."""
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
