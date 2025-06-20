#!/usr/bin/env python3
"""
NiceGUI Desktop Application

A simple technology demonstration showing NiceGUI UI components
in a native window, ready for PyInstaller packaging.
"""

import datetime
import socket

from nicegui import app, ui

from .root_page import setup_root_page


class App:
    """Main application class."""

    def __init__(self) -> None:
        """Initialize the desktop application."""
        self.setup_pages()
        self.setup_shutdown_handler()

    def find_free_port(self, start_port: int = 8000, max_attempts: int = 100) -> int:
        """Find a free port starting from the given port.

        Args:
            start_port: Port to start searching from
            max_attempts: Maximum number of ports to try

        Returns:
            Available port number

        Raises:
            RuntimeError: If no free port is found within max_attempts
        """
        for port in range(start_port, start_port + max_attempts):
            if self.is_port_free(port):
                print(f"Found free port: {port}")
                return port

        raise RuntimeError(
            f"No free port found in range {start_port}-{start_port + max_attempts}"
        )

    def is_port_free(self, port: int) -> bool:
        """Check if a port is free.

        Args:
            port: Port number to check

        Returns:
            True if port is free, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Don't set SO_REUSEADDR to get accurate port availability
                sock.settimeout(1)  # Quick timeout for testing
                result = sock.connect_ex(("127.0.0.1", port))
                if result == 0:
                    # Port is in use (connection succeeded)
                    return False
                else:
                    # Port appears free, try to bind to be sure
                    try:
                        with socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM
                        ) as test_sock:
                            test_sock.bind(("127.0.0.1", port))
                            return True
                    except OSError:
                        return False
        except Exception:
            return False



    def log_action(self, action: str, details: str = "") -> None:
        """Log UI actions to console with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] UI Action: {action}"
        if details:
            log_message += f" - {details}"
        print(log_message)



    def setup_pages(self) -> None:
        """Setup application pages and UI components."""
        setup_root_page(self)



    def setup_shutdown_handler(self) -> None:
        """Setup application shutdown event handler."""

        @app.on_shutdown
        def shutdown() -> None:
            """Handle application shutdown event."""
            self.log_action("Application Shutdown", "Cleanup completed")
            print(f"Application shutdown: {datetime.datetime.now()}")

    def run(self) -> None:
        """Run the desktop application with comprehensive error handling."""
        try:
            print(f"Application starting: {datetime.datetime.now()}")
            self.log_action("Application Startup", "NiceGUI desktop app initialized")

            # Find a free port (starting from 8000, avoiding common ports like 8001)
            try:
                free_port = self.find_free_port(start_port=8000)
                print(f"Starting NiceGUI server on port {free_port}")
                self.log_action(
                    "Server Start", f"NiceGUI server starting on port {free_port}"
                )
                ui.run(
                    native=True, 
                    reload=False, 
                    show=False, 
                    port=free_port,
                    title="NiceGUI Desktop Demo",
                    window_size=(1000, 700),
                    fullscreen=False
                )
            except RuntimeError as e:
                print(f"Error finding free port: {e}")
                print("Falling back to automatic port selection (port=0)")
                self.log_action("Port Fallback", "Using automatic port selection")
                # Fallback to letting the system choose a port
                ui.run(
                    native=True, 
                    reload=False, 
                    show=False, 
                    port=0,
                    title="NiceGUI Desktop Demo",
                    window_size=(1000, 700),
                    fullscreen=False
                )
        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Shutting down gracefully...")
            self.log_action("Application Shutdown", "Interrupted by user")
        except Exception as e:
            print(f"Unexpected error during application startup: {e}")
            self.log_action("Application Error", f"Startup failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Application shutdown complete.")
            self.log_action("Application Cleanup", "Application terminated")


def main() -> None:
    """Application entry point."""
    app_instance = App()
    app_instance.run()


if __name__ == "__main__":
    main()
