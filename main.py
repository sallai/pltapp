#!/usr/bin/env python3
"""
NiceGUI Desktop Application Entry Point

Minimal entry point that imports and runs the main application.
"""

from src.app import App


def main() -> None:
    """Application entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
