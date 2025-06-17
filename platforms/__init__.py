"""
Platform abstraction layer for cross-platform UI toolkit support.

This module provides a unified interface for different UI toolkits
(PySide6, PyQt6, GTK) across different platforms (macOS, Windows, Linux).
"""

from .base import WindowManagerInterface
from .factory import create_window_manager, get_available_toolkits

__all__ = ['WindowManagerInterface', 'create_window_manager', 'get_available_toolkits']