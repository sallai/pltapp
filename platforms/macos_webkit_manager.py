"""
macOS native WebKit window manager implementation.
"""

import time
import signal
import platform
import logging
from typing import Any, Callable, Dict
from .base import WindowManagerInterface

# Check if we're on macOS
if platform.system() != 'Darwin':
    MACOS_WEBKIT_AVAILABLE = False
    # Define dummy classes to prevent NameError
    NSObject = NSApplication = NSWindow = WKWebView = object
else:
    try:
        import objc
        from Foundation import NSObject, NSURL, NSString
        from AppKit import NSApplication, NSWindow, NSMenu, NSMenuItem
        from WebKit import WKWebView, WKWebViewConfiguration
        MACOS_WEBKIT_AVAILABLE = True
    except ImportError:
        MACOS_WEBKIT_AVAILABLE = False
        # Define dummy classes to prevent NameError
        NSObject = NSApplication = NSWindow = WKWebView = object


class MacOSWebKitDelegate(NSObject):
    """Delegate for macOS WebKit window and WebView."""
    
    def init(self):
        self = objc.super(MacOSWebKitDelegate, self).init()
        if self is None:
            return None
        self.quit_callback = None
        return self
    
    def setQuitCallback_(self, callback):
        """Set the quit callback."""
        self.quit_callback = callback
    
    def windowShouldClose_(self, window):
        """Handle window close."""
        logging.info("Window should close")
        if self.quit_callback:
            self.quit_callback()
        return True
    
    def applicationShouldTerminate_(self, app):
        """Handle application termination."""
        logging.info("Application should terminate")
        if self.quit_callback:
            self.quit_callback()
        return True
    
    # WebView delegate methods
    def webView_didStartProvisionalNavigation_(self, webView, navigation):
        """WebView started loading."""
        logging.info("WebView started loading")
    
    def webView_didFinishNavigation_(self, webView, navigation):
        """WebView finished loading."""
        logging.info("WebView finished loading")
    
    def webView_didFailNavigation_withError_(self, webView, navigation, error):
        """WebView failed to load."""
        logging.error(f"WebView failed to load: {error}")
    
    def webView_didFailProvisionalNavigation_withError_(self, webView, navigation, error):
        """WebView failed provisional navigation."""
        logging.error(f"WebView failed provisional navigation: {error}")


class MacOSWebKitWindowManager(WindowManagerInterface):
    """macOS native WebKit window manager."""
    
    def __init__(self):
        if not MACOS_WEBKIT_AVAILABLE:
            raise ImportError("macOS WebKit frameworks are not available")
        if platform.system() != 'Darwin':
            raise RuntimeError("macOS WebKit manager can only run on macOS")
        
        self.delegate = None
        self._signal_handlers = []
    
    def create_application(self, app_name: str) -> NSApplication:
        """Create NSApplication."""
        app = NSApplication.sharedApplication()
        app.setActivationPolicy_(0)  # NSApplicationActivationPolicyRegular
        return app
    
    def create_main_window(self, config: Dict[str, Any]) -> NSWindow:
        """Create NSWindow."""
        window_config = config.get('window', {})
        
        # Window frame: ((x, y), (width, height))
        x, y = 100, 100
        width = window_config.get('width', 800)
        height = window_config.get('height', 600)
        
        window_frame = ((x, y), (width, height))
        
        # Create window with standard style
        style_mask = 15  # Titled | Closable | Miniaturizable | Resizable
        backing = 2      # NSBackingStoreBuffered
        
        window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            window_frame, style_mask, backing, False
        )
        
        # Set minimum size if specified
        min_width = window_config.get('min_width', 0)
        min_height = window_config.get('min_height', 0)
        if min_width > 0 and min_height > 0:
            window.setContentMinSize_((min_width, min_height))
        
        return window
    
    def create_web_view(self) -> WKWebView:
        """Create WKWebView."""
        # Create configuration
        config = WKWebViewConfiguration.alloc().init()
        
        # Enable developer extras
        config.preferences().setValue_forKey_(True, "developerExtrasEnabled")
        
        # Create web view with default frame (will be resized when added to window)
        web_frame = ((0, 0), (800, 600))
        webview = WKWebView.alloc().initWithFrame_configuration_(web_frame, config)
        
        # Set navigation delegate to track loading
        if not hasattr(self, '_webview_delegate'):
            self._webview_delegate = MacOSWebKitDelegate.alloc().init()
        webview.setNavigationDelegate_(self._webview_delegate)
        
        return webview
    
    def set_web_view_content(self, web_view: WKWebView, content: str) -> None:
        """Set HTML content in web view."""
        html_string = NSString.stringWithString_(content)
        base_url = NSURL.URLWithString_("about:blank")
        web_view.loadHTMLString_baseURL_(html_string, base_url)
    
    def set_web_view_url(self, web_view: WKWebView, url: str) -> None:
        """Set URL in web view."""
        logging.info(f"Loading URL in WebKit: {url}")
        nsurl = NSURL.URLWithString_(url)
        if nsurl is None:
            logging.error(f"Failed to create NSURL from: {url}")
            return
        
        request = objc.lookUpClass("NSURLRequest").requestWithURL_(nsurl)
        web_view.loadRequest_(request)
        logging.info("URL load request sent to WebKit")
    
    def stop_web_view(self, web_view: WKWebView) -> None:
        """Stop web view loading."""
        web_view.stopLoading()
    
    def setup_window_properties(self, window: NSWindow, config: Dict[str, Any]) -> None:
        """Configure window properties."""
        app_config = config.get('app', {})
        title = app_config.get('title', 'Application')
        
        window.setTitle_(title)
        window.center()
        
        # Create and set delegate
        self.delegate = MacOSWebKitDelegate.alloc().init()
        window.setDelegate_(self.delegate)
    
    def setup_menu_bar(self, window: NSWindow, quit_callback: Callable) -> None:
        """Set up macOS menu bar."""
        try:
            # Set quit callback on delegate
            if self.delegate:
                self.delegate.setQuitCallback_(quit_callback)
            
            # Create main menu
            main_menu = NSMenu.alloc().init()
            
            # Create application menu
            app_menu_item = NSMenuItem.alloc().init()
            app_menu = NSMenu.alloc().init()
            app_menu_item.setSubmenu_(app_menu)
            main_menu.addItem_(app_menu_item)
            
            # Add quit menu item
            quit_title = f"Quit {window.title()}"
            quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                quit_title, "terminate:", "q"
            )
            app_menu.addItem_(quit_item)
            
            # Set as main menu
            NSApplication.sharedApplication().setMainMenu_(main_menu)
            
        except Exception as e:
            logging.warning(f"Could not set up menu bar: {e}")
    
    def add_web_view_to_window(self, window: NSWindow, web_view: WKWebView) -> None:
        """Add web view to window (macOS-specific integration)."""
        content_view = window.contentView()
        
        # Resize web view to match window content
        content_frame = content_view.frame()
        web_view.setFrame_(content_frame)
        
        # Add to window
        content_view.addSubview_(web_view)
        
        # Store reference for cleanup
        self._current_webview = web_view
    
    def show_window(self, window: NSWindow) -> None:
        """Show the window."""
        window.makeKeyAndOrderFront_(None)
        app = NSApplication.sharedApplication()
        app.activateIgnoringOtherApps_(True)
    
    def setup_signal_handlers(self, signal_callback: Callable) -> None:
        """Set up signal handlers."""
        def macos_signal_handler(signum, frame):
            signal_callback(signum, frame)
            NSApplication.sharedApplication().terminate_(None)
        
        signal.signal(signal.SIGINT, macos_signal_handler)
        signal.signal(signal.SIGTERM, macos_signal_handler)
        self._signal_handlers = [macos_signal_handler]
    
    def run_event_loop(self, app: NSApplication) -> int:
        """Run NSApplication event loop."""
        try:
            # Set up application delegate to handle termination
            if self.delegate:
                app.setDelegate_(self.delegate)
            
            app.run()
            return 0
        except KeyboardInterrupt:
            logging.info("Interrupted, terminating...")
            app.terminate_(None)
            return 0
        except Exception as e:
            logging.error(f"Event loop error: {e}")
            return 1
    
    def process_events(self, app: NSApplication) -> None:
        """Process Cocoa events."""
        # Process pending events
        from AppKit import NSDefaultRunLoopMode
        from Foundation import NSRunLoop, NSDate
        
        run_loop = NSRunLoop.currentRunLoop()
        run_loop.runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.01))
    
    def quit_application(self, app: NSApplication) -> None:
        """Quit NSApplication."""
        app.terminate_(None)
    
    def cleanup_web_view(self, web_view: WKWebView) -> None:
        """Perform WebKit cleanup."""
        try:
            # Stop loading
            web_view.stopLoading()
            
            # Load blank page
            blank_url = NSURL.URLWithString_("about:blank")
            request = objc.lookUpClass("NSURLRequest").requestWithURL_(blank_url)
            web_view.loadRequest_(request)
            
            # Remove from superview
            web_view.removeFromSuperview()
            
            # Process events briefly
            app = NSApplication.sharedApplication()
            self.process_events(app)
            time.sleep(0.05)
            self.process_events(app)
            
        except Exception as e:
            logging.warning(f"Error during WebKit cleanup: {e}")
    
    def get_platform_info(self) -> Dict[str, str]:
        """Return macOS WebKit platform information."""
        # Get macOS version
        import subprocess
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True)
            macos_version = result.stdout.strip() if result.returncode == 0 else 'Unknown'
        except:
            macos_version = 'Unknown'
        
        return {
            'toolkit': 'macOS WebKit',
            'platform': 'Darwin',
            'architecture': platform.machine(),
            'toolkit_version': macos_version
        }
    
    # Store reference to current web view for window integration
    def _set_current_webview(self, webview):
        """Internal method to track current web view."""
        self._current_webview = webview