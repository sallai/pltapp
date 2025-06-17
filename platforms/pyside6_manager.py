"""
PySide6-based window manager implementation.
"""

import time
import signal
import platform
from typing import Any, Callable, Dict
from .base import WindowManagerInterface

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtCore import QUrl, QTimer, Qt
    from PySide6.QtGui import QAction
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


class PySide6WindowManager(WindowManagerInterface):
    """PySide6-based window manager."""
    
    def __init__(self):
        if not PYSIDE6_AVAILABLE:
            raise ImportError("PySide6 is not available")
        self._signal_timer = None
    
    def create_application(self, app_name: str) -> QApplication:
        """Create PySide6 application."""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        app.setApplicationName(app_name)
        return app
    
    def create_main_window(self, config: Dict[str, Any]) -> QMainWindow:
        """Create main window."""
        window = QMainWindow()
        return window
    
    def create_web_view(self) -> QWebEngineView:
        """Create QWebEngineView."""
        return QWebEngineView()
    
    def set_web_view_content(self, web_view: QWebEngineView, content: str) -> None:
        """Set HTML content in web view."""
        web_view.setHtml(content)
    
    def set_web_view_url(self, web_view: QWebEngineView, url: str) -> None:
        """Set URL in web view."""
        web_view.setUrl(QUrl(url))
    
    def stop_web_view(self, web_view: QWebEngineView) -> None:
        """Stop web view loading."""
        web_view.stop()
    
    def setup_window_properties(self, window: QMainWindow, config: Dict[str, Any]) -> None:
        """Configure window properties."""
        window_config = config.get('window', {})
        
        window.setWindowTitle(config.get('app', {}).get('title', 'Application'))
        
        width = window_config.get('width', 800)
        height = window_config.get('height', 600)
        window.setGeometry(100, 100, width, height)
        
        min_width = window_config.get('min_width', 600)
        min_height = window_config.get('min_height', 500)
        window.setMinimumSize(min_width, min_height)
        
        # Center window on screen
        self._center_window(window)
    
    def _center_window(self, window: QMainWindow) -> None:
        """Center window on screen."""
        try:
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            window_geometry = window.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            window.move(window_geometry.topLeft())
        except Exception:
            pass  # Fallback to default position
    
    def setup_menu_bar(self, window: QMainWindow, quit_callback: Callable) -> None:
        """Set up menu bar (macOS specific)."""
        try:
            if platform.system() == 'Darwin':  # macOS
                menubar = window.menuBar()
                app_menu = menubar.addMenu(window.windowTitle())
                
                quit_action = QAction('Quit', window)
                quit_action.setShortcut('Cmd+Q')
                quit_action.triggered.connect(quit_callback)
                app_menu.addAction(quit_action)
        except Exception:
            pass  # Menu setup is optional
    
    def show_window(self, window: QMainWindow) -> None:
        """Show the window."""
        window.show()
    
    def setup_signal_handlers(self, signal_callback: Callable) -> None:
        """Set up signal handlers."""
        signal.signal(signal.SIGINT, signal_callback)
        signal.signal(signal.SIGTERM, signal_callback)
        
        # Qt timer for signal processing
        app = QApplication.instance()
        if app:
            self._signal_timer = QTimer()
            self._signal_timer.timeout.connect(lambda: None)
            self._signal_timer.start(100)
    
    def run_event_loop(self, app: QApplication) -> int:
        """Run Qt event loop."""
        return app.exec()
    
    def process_events(self, app: QApplication) -> None:
        """Process Qt events."""
        app.processEvents()
    
    def quit_application(self, app: QApplication) -> None:
        """Quit Qt application."""
        app.quit()
    
    def cleanup_web_view(self, web_view: QWebEngineView) -> None:
        """Perform Qt WebEngine cleanup."""
        try:
            # Stop any ongoing loading
            web_view.stop()
            
            # Set blank page to help cleanup
            web_view.setUrl(QUrl("about:blank"))
            
            # Process events to allow WebEngine cleanup
            app = QApplication.instance()
            if app:
                app.processEvents()
                time.sleep(0.1)  # Brief pause for WebEngine
                app.processEvents()
                
        except Exception:
            pass  # Cleanup is best-effort
    
    def get_platform_info(self) -> Dict[str, str]:
        """Return PySide6 platform information."""
        return {
            'toolkit': 'PySide6',
            'platform': platform.system(),
            'architecture': platform.machine(),
            'toolkit_version': getattr(QApplication, 'applicationVersion', lambda: 'Unknown')()
        }