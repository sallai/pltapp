"""
GTK-based window manager implementation (Linux).
"""

import signal
import platform
from typing import Any, Callable, Dict
from .base import WindowManagerInterface

try:
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.0')
    from gi.repository import Gtk, WebKit2, GLib, Gdk
    GTK_AVAILABLE = True
except (ImportError, ValueError):
    GTK_AVAILABLE = False
    # Define dummy classes to prevent NameError
    class Gtk:
        class Application: pass
        class ApplicationWindow: pass
        class MenuBar: pass
        class Menu: pass
        class MenuItem: pass
        class VBox: pass
        class WindowPosition:
            CENTER = None
        @staticmethod
        def events_pending(): return False
        @staticmethod
        def main_iteration(): pass
    class WebKit2:
        class WebView: pass


class GTKWindowManager(WindowManagerInterface):
    """GTK-based window manager for Linux."""
    
    def __init__(self):
        if not GTK_AVAILABLE:
            raise ImportError("GTK3 and WebKit2GTK are not available")
        self._app = None
        self._main_loop = None
    
    def create_application(self, app_name: str) -> Gtk.Application:
        """Create GTK application."""
        self._app = Gtk.Application(application_id=f"com.example.{app_name.lower()}")
        return self._app
    
    def create_main_window(self, config: Dict[str, Any]) -> Gtk.ApplicationWindow:
        """Create main window."""
        window = Gtk.ApplicationWindow(application=self._app)
        return window
    
    def create_web_view(self) -> WebKit2.WebView:
        """Create WebKit2 WebView."""
        web_view = WebKit2.WebView()
        # Configure web view settings
        settings = web_view.get_settings()
        settings.set_property('enable-javascript', True)
        settings.set_property('enable-html5-database', True)
        settings.set_property('enable-html5-local-storage', True)
        return web_view
    
    def set_web_view_content(self, web_view: WebKit2.WebView, content: str) -> None:
        """Set HTML content in web view."""
        web_view.load_html(content, None)
    
    def set_web_view_url(self, web_view: WebKit2.WebView, url: str) -> None:
        """Set URL in web view."""
        web_view.load_uri(url)
    
    def stop_web_view(self, web_view: WebKit2.WebView) -> None:
        """Stop web view loading."""
        web_view.stop_loading()
    
    def setup_window_properties(self, window: Gtk.ApplicationWindow, config: Dict[str, Any]) -> None:
        """Configure window properties."""
        window_config = config.get('window', {})
        
        window.set_title(config.get('app', {}).get('title', 'Application'))
        
        width = window_config.get('width', 800)
        height = window_config.get('height', 600)
        window.set_default_size(width, height)
        
        # Set minimum size if specified
        min_width = window_config.get('min_width', 0)
        min_height = window_config.get('min_height', 0)
        if min_width > 0 or min_height > 0:
            window.set_size_request(min_width, min_height)
        
        # Center window
        window.set_position(Gtk.WindowPosition.CENTER)
    
    def setup_menu_bar(self, window: Gtk.ApplicationWindow, quit_callback: Callable) -> None:
        """Set up menu bar."""
        try:
            # Create menu bar
            menubar = Gtk.MenuBar()
            
            # Create application menu
            app_menu = Gtk.Menu()
            app_menu_item = Gtk.MenuItem(label="Application")
            app_menu_item.set_submenu(app_menu)
            
            # Add quit item
            quit_item = Gtk.MenuItem(label="Quit")
            quit_item.connect("activate", lambda w: quit_callback())
            app_menu.append(quit_item)
            
            menubar.append(app_menu_item)
            
            # Add menubar to window
            vbox = Gtk.VBox()
            vbox.pack_start(menubar, False, False, 0)
            
            # This would need to be integrated with the main window layout
            # For now, just set up the callback
            window.connect("delete-event", lambda w, e: quit_callback())
            
        except Exception:
            pass  # Menu setup is optional
    
    def show_window(self, window: Gtk.ApplicationWindow) -> None:
        """Show the window."""
        window.show_all()
    
    def setup_signal_handlers(self, signal_callback: Callable) -> None:
        """Set up signal handlers."""
        def gtk_signal_handler(signum, frame):
            signal_callback(signum, frame)
            Gtk.main_quit()
        
        signal.signal(signal.SIGINT, gtk_signal_handler)
        signal.signal(signal.SIGTERM, gtk_signal_handler)
    
    def run_event_loop(self, app: Gtk.Application) -> int:
        """Run GTK event loop."""
        try:
            return app.run([])
        except KeyboardInterrupt:
            return 0
    
    def process_events(self, app: Gtk.Application) -> None:
        """Process GTK events."""
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    def quit_application(self, app: Gtk.Application) -> None:
        """Quit GTK application."""
        app.quit()
    
    def cleanup_web_view(self, web_view: WebKit2.WebView) -> None:
        """Perform WebKit2 cleanup."""
        try:
            # Stop loading
            web_view.stop_loading()
            
            # Load blank page
            web_view.load_html("", None)
            
            # Process events
            while Gtk.events_pending():
                Gtk.main_iteration()
                
        except Exception:
            pass  # Cleanup is best-effort
    
    def get_platform_info(self) -> Dict[str, str]:
        """Return GTK platform information."""
        gtk_version = f"{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}"
        return {
            'toolkit': 'GTK3',
            'platform': platform.system(),
            'architecture': platform.machine(),
            'toolkit_version': gtk_version
        }