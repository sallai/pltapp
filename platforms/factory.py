"""
Factory for creating platform-specific window managers.
"""

import platform
import logging
from typing import Optional
from .base import WindowManagerInterface


def create_window_manager(toolkit: Optional[str] = None) -> WindowManagerInterface:
    """
    Create a platform-appropriate window manager.
    
    Args:
        toolkit: Specific toolkit to use ('pyside6', 'pyqt6', 'gtk').
                If None, auto-detect based on platform and availability.
    
    Returns:
        WindowManagerInterface implementation.
        
    Raises:
        ImportError: If no suitable toolkit is available.
    """
    current_platform = platform.system()
    
    if toolkit:
        # User specified a toolkit
        return _create_specific_manager(toolkit)
    
    # Auto-detect based on platform and availability
    if current_platform == 'Darwin':  # macOS
        # Prefer native WebKit on macOS, fallback to Qt
        managers_to_try = ['macos_webkit', 'pyside6', 'pyqt6']
    elif current_platform == 'Windows':
        # Prefer PyQt6 on Windows (as specified in requirements)
        managers_to_try = ['pyqt6', 'pyside6']
    elif current_platform == 'Linux':
        # Prefer GTK on Linux, fallback to Qt
        managers_to_try = ['gtk', 'pyside6', 'pyqt6']
    else:
        # Unknown platform, try Qt variants
        managers_to_try = ['pyside6', 'pyqt6']
    
    last_error = None
    for manager_type in managers_to_try:
        try:
            manager = _create_specific_manager(manager_type)
            logging.info(f"Using {manager_type} window manager on {current_platform}")
            return manager
        except ImportError as e:
            last_error = e
            logging.debug(f"Failed to create {manager_type} manager: {e}")
            continue
    
    # If we get here, no manager could be created
    raise ImportError(
        f"No suitable window manager available for {current_platform}. "
        f"Last error: {last_error}"
    )


def _create_specific_manager(toolkit: str) -> WindowManagerInterface:
    """Create a specific window manager type."""
    if toolkit.lower() == 'pyside6':
        from .pyside6_manager import PySide6WindowManager
        return PySide6WindowManager()
    elif toolkit.lower() == 'pyqt6':
        from .pyqt6_manager import PyQt6WindowManager
        return PyQt6WindowManager()
    elif toolkit.lower() == 'gtk':
        from .gtk_manager import GTKWindowManager
        return GTKWindowManager()
    elif toolkit.lower() == 'macos_webkit':
        from .macos_webkit_manager import MacOSWebKitWindowManager
        return MacOSWebKitWindowManager()
    else:
        raise ValueError(f"Unknown toolkit: {toolkit}")


def get_available_toolkits() -> dict:
    """
    Get information about available toolkits on the current platform.
    
    Returns:
        Dict mapping toolkit names to availability status and info.
    """
    toolkits = {}
    
    # Check PySide6
    try:
        from .pyside6_manager import PySide6WindowManager
        manager = PySide6WindowManager()
        toolkits['pyside6'] = {
            'available': True,
            'info': manager.get_platform_info()
        }
    except ImportError as e:
        toolkits['pyside6'] = {
            'available': False,
            'error': str(e)
        }
    
    # Check PyQt6
    try:
        from .pyqt6_manager import PyQt6WindowManager
        manager = PyQt6WindowManager()
        toolkits['pyqt6'] = {
            'available': True,
            'info': manager.get_platform_info()
        }
    except ImportError as e:
        toolkits['pyqt6'] = {
            'available': False,
            'error': str(e)
        }
    
    # Check GTK (Linux only)
    if platform.system() == 'Linux':
        try:
            from .gtk_manager import GTKWindowManager
            manager = GTKWindowManager()
            toolkits['gtk'] = {
                'available': True,
                'info': manager.get_platform_info()
            }
        except ImportError as e:
            toolkits['gtk'] = {
                'available': False,
                'error': str(e)
            }
    
    # Check macOS WebKit (macOS only)
    if platform.system() == 'Darwin':
        try:
            from .macos_webkit_manager import MacOSWebKitWindowManager
            manager = MacOSWebKitWindowManager()
            toolkits['macos_webkit'] = {
                'available': True,
                'info': manager.get_platform_info()
            }
        except ImportError as e:
            toolkits['macos_webkit'] = {
                'available': False,
                'error': str(e)
            }
    
    return toolkits