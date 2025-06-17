"""
Base interface for platform-specific window managers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any


class WindowManagerInterface(ABC):
    """Abstract base class for platform-specific window managers."""
    
    @abstractmethod
    def create_application(self, app_name: str) -> Any:
        """Create and return the native application object."""
        pass
    
    @abstractmethod
    def create_main_window(self, config: Dict[str, Any]) -> Any:
        """Create and return the main window object."""
        pass
    
    @abstractmethod
    def create_web_view(self) -> Any:
        """Create and return a web view widget."""
        pass
    
    @abstractmethod
    def set_web_view_content(self, web_view: Any, content: str) -> None:
        """Set HTML content in the web view."""
        pass
    
    @abstractmethod
    def set_web_view_url(self, web_view: Any, url: str) -> None:
        """Set URL in the web view."""
        pass
    
    @abstractmethod
    def stop_web_view(self, web_view: Any) -> None:
        """Stop web view loading."""
        pass
    
    @abstractmethod
    def setup_window_properties(self, window: Any, config: Dict[str, Any]) -> None:
        """Configure window properties (size, title, etc.)."""
        pass
    
    @abstractmethod
    def setup_menu_bar(self, window: Any, quit_callback: Callable) -> None:
        """Set up platform-specific menu bar."""
        pass
    
    @abstractmethod
    def show_window(self, window: Any) -> None:
        """Show the window."""
        pass
    
    @abstractmethod
    def setup_signal_handlers(self, signal_callback: Callable) -> None:
        """Set up signal handlers for the platform."""
        pass
    
    @abstractmethod
    def run_event_loop(self, app: Any) -> int:
        """Run the main event loop and return exit code."""
        pass
    
    @abstractmethod
    def process_events(self, app: Any) -> None:
        """Process pending events."""
        pass
    
    @abstractmethod
    def quit_application(self, app: Any) -> None:
        """Quit the application gracefully."""
        pass
    
    @abstractmethod
    def cleanup_web_view(self, web_view: Any) -> None:
        """Perform platform-specific web view cleanup."""
        pass
    
    @abstractmethod
    def get_platform_info(self) -> Dict[str, str]:
        """Return platform-specific information."""
        pass