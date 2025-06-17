#!/usr/bin/env python3
"""
Refactored main application using platform abstraction layer.

This version uses the pluggable platform architecture to support
different UI toolkits (PySide6, PyQt6, GTK) across platforms.
"""

import sys
import time
import signal
import logging
import threading
import atexit
from typing import Optional, Dict, Any

from platforms import create_window_manager, get_available_toolkits
from nicegui import ui, app

# Application Configuration
CONFIG = {
    'app': {
        'title': 'NiceGUI + Platform Abstraction Demo',
        'port': 8080,
        'host': '127.0.0.1',
        'show_browser': False,
        'debug': False
    },
    'window': {
        'width': 900,
        'height': 700,
        'min_width': 600,
        'min_height': 500,
    }
}

# Global state
window_manager = None
main_app = None
main_window = None
web_view = None
server_thread = None
shutdown_requested = False


class BackendServerThread(threading.Thread):
    """Thread for running the NiceGUI backend server."""
    
    def __init__(self):
        super().__init__(daemon=True)
        self._shutdown_requested = False
        self._server_ready = threading.Event()
        self.server_url = None
    
    def run(self):
        """Start the NiceGUI server."""
        try:
            logging.info("Starting NiceGUI server...")
            
            # Set up the UI
            setup_ui()
            
            # Signal that server is ready
            self.server_url = f"http://{CONFIG['app']['host']}:{CONFIG['app']['port']}"
            self._server_ready.set()
            
            # Start the server (blocks until shutdown)
            ui.run(
                title=CONFIG['app']['title'],
                port=CONFIG['app']['port'],
                host=CONFIG['app']['host'],
                show=CONFIG['app']['show_browser'],
                reload=CONFIG['app']['debug'],
                native=False,
                uvicorn_logging_level='warning',
            )
            
        except Exception as e:
            logging.error(f"Error in backend server: {e}")
    
    def wait_for_ready(self, timeout: float = 10.0) -> bool:
        """Wait for server to be ready."""
        return self._server_ready.wait(timeout)
    
    def stop(self):
        """Request server shutdown."""
        self._shutdown_requested = True
        try:
            app.shutdown()
        except Exception as e:
            logging.warning(f"Error shutting down NiceGUI: {e}")


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def setup_ui():
    """Set up the NiceGUI interface."""
    with ui.header():
        ui.label(CONFIG['app']['title']).style(
            'font-size: 1.5em; font-weight: bold; color: white'
        )
    
    with ui.column().style('padding: 20px; gap: 20px; max-width: 700px; margin: 0 auto'):
        ui.label('Platform Abstraction Demo').style(
            'font-size: 1.8em; font-weight: bold; text-align: center; color: #1976d2'
        )
        
        ui.label(
            'This application demonstrates the platform abstraction layer, '
            'allowing the same code to run with different UI toolkits.'
        ).style('text-align: center; color: #666; margin-bottom: 30px; line-height: 1.4')
        
        # Show platform info
        if window_manager:
            platform_info = window_manager.get_platform_info()
            ui.label(f"Platform: {platform_info.get('platform', 'Unknown')}").style('font-weight: bold')
            ui.label(f"Toolkit: {platform_info.get('toolkit', 'Unknown')}").style('font-weight: bold')
            ui.label(f"Architecture: {platform_info.get('architecture', 'Unknown')}")
        
        ui.separator()
        
        # Simple interactive element
        text_input = ui.input('Enter some text', placeholder='Type here...')
        result_label = ui.label('')
        
        def on_text_change():
            result_label.text = f"You typed: {text_input.value}"
            logging.info(f"You typed: {text_input.value}")

        
        ui.button('Process Text', on_click=on_text_change, color='primary')


def start_backend_server() -> bool:
    """Start the backend server in a separate thread."""
    global server_thread
    
    try:
        server_thread = BackendServerThread()
        server_thread.start()
        
        if server_thread.wait_for_ready():
            logging.info(f"Backend server ready at {server_thread.server_url}")
            return True
        else:
            logging.error("Backend server failed to start within timeout")
            return False
            
    except Exception as e:
        logging.error(f"Error starting backend server: {e}")
        return False


def load_web_content():
    """Load the web content into the web view."""
    global web_view
    
    if not web_view or not server_thread:
        return False
    
    try:
        window_manager.set_web_view_url(web_view, server_thread.server_url)
        logging.info("Web content loaded")
        return True
    except Exception as e:
        logging.error(f"Error loading web content: {e}")
        return False


def cleanup_application():
    """Clean up application resources."""
    global shutdown_requested, server_thread, web_view, main_app
    
    if shutdown_requested:
        return
    
    shutdown_requested = True
    logging.info("Starting application cleanup...")
    
    try:
        # Step 1: Stop web view
        if web_view and window_manager:
            logging.info("Cleaning up web view...")
            window_manager.cleanup_web_view(web_view)
        
        # Step 2: Stop backend server
        if server_thread:
            logging.info("Stopping backend server...")
            server_thread.stop()
            server_thread.join(timeout=3.0)
        
        # Step 3: Process final events
        if main_app and window_manager:
            logging.info("Processing final events...")
            window_manager.process_events(main_app)
            time.sleep(0.1)
            window_manager.process_events(main_app)
        
        # Step 4: Quit application
        if main_app and window_manager:
            logging.info("Quitting application...")
            window_manager.quit_application(main_app)
        
        logging.info("Cleanup completed")
        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """Handle system signals."""
    logging.info(f"Received signal {signum}")
    cleanup_application()
    sys.exit(0)


def on_window_close():
    """Handle window close event."""
    logging.info("Window close requested")
    cleanup_application()


def main(toolkit: Optional[str] = None):
    """Main application entry point."""
    global window_manager, main_app, main_window, web_view
    
    try:
        # Setup logging
        setup_logging()
        logging.info("Starting platform-abstracted application")
        
        # Show available toolkits
        available = get_available_toolkits()
        logging.info("Available toolkits:")
        for name, info in available.items():
            if info['available']:
                toolkit_info = info['info']
                logging.info(f"  {name}: {toolkit_info.get('toolkit', 'Unknown')} on {toolkit_info.get('platform', 'Unknown')}")
            else:
                logging.info(f"  {name}: Not available ({info.get('error', 'Unknown error')})")
        
        # Create window manager
        window_manager = create_window_manager(toolkit)
        platform_info = window_manager.get_platform_info()
        logging.info(f"Using {platform_info['toolkit']} on {platform_info['platform']}")
        
        # Set up signal handling
        window_manager.setup_signal_handlers(signal_handler)
        atexit.register(cleanup_application)
        
        # Create application
        main_app = window_manager.create_application(CONFIG['app']['title'])
        
        # Create main window
        main_window = window_manager.create_main_window(CONFIG)
        window_manager.setup_window_properties(main_window, CONFIG)
        window_manager.setup_menu_bar(main_window, on_window_close)
        
        # Create web view and set it as central widget
        web_view = window_manager.create_web_view()
        
        # For Qt-based managers, set web view as central widget
        if hasattr(main_window, 'setCentralWidget'):
            main_window.setCentralWidget(web_view)
        # For macOS WebKit, add web view to window
        elif hasattr(window_manager, 'add_web_view_to_window'):
            window_manager.add_web_view_to_window(main_window, web_view)
        
        # Start backend server
        if not start_backend_server():
            logging.error("Failed to start backend server")
            return 1
        
        # Load web content
        if not load_web_content():
            logging.error("Failed to load web content")
            return 1
        
        # Show window
        window_manager.show_window(main_window)
        
        # Run event loop
        logging.info("Starting event loop...")
        exit_code = window_manager.run_event_loop(main_app)
        logging.info(f"Application exited with code: {exit_code}")
        
        return exit_code
        
    except KeyboardInterrupt:
        logging.info("Application interrupted")
        cleanup_application()
        return 0
    except Exception as e:
        logging.error(f"Application error: {e}")
        cleanup_application()
        return 1


if __name__ == "__main__":
    # Allow toolkit selection via command line
    toolkit = None
    if len(sys.argv) > 1:
        toolkit = sys.argv[1].lower()
        if toolkit not in ['pyside6', 'pyqt6', 'gtk', 'macos_webkit']:
            print(f"Unknown toolkit: {toolkit}")
            print("Available options: pyside6, pyqt6, gtk, macos_webkit")
            sys.exit(1)
    
    sys.exit(main(toolkit))