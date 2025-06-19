#!/usr/bin/env python3
"""
NiceGUI Desktop Application

A simple technology demonstration showing NiceGUI UI components
in a native window, ready for PyInstaller packaging.
"""

import datetime
import socket

from nicegui import app, ui


class DesktopApp:
    """Main desktop application class."""

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

    def setup_pages(self) -> None:
        """Setup application pages and UI components."""

        @ui.page("/")
        def main_page() -> None:
            """Main application page with UI components."""
            ui.label("Enter some text:").style("font-size: 18px; margin-bottom: 10px")

            text_input = ui.input("Enter some text").style("margin-bottom: 10px")
            result_label = ui.label("-").style("font-weight: bold; color: #1976d2")

            def on_text_change() -> None:
                """Process text input and update result display."""
                input_text = text_input.value or ""
                result_text = (
                    f"You typed: {input_text}" if input_text else "No text entered"
                )
                result_label.text = result_text
                print(f"Text processed: {input_text}")

            ui.button("Process Text", on_click=on_text_change).style("margin: 10px 0")

            def shutdown_app() -> None:
                """Shutdown the application gracefully."""
                print("Shutdown requested by user")
                app.shutdown()

            with ui.row():
                ui.button("Shutdown", on_click=shutdown_app).style(
                    "background-color: #d32f2f"
                )

    def setup_shutdown_handler(self) -> None:
        """Setup application shutdown event handler."""

        @app.on_shutdown
        def shutdown() -> None:
            """Handle application shutdown event."""
            print(f"Application shutdown: {datetime.datetime.now()}")

    def run(self) -> None:
        """Run the desktop application."""
        print(f"Application starting: {datetime.datetime.now()}")

        # Find a free port (starting from 8000, avoiding common ports like 8001)
        try:
            free_port = self.find_free_port(start_port=8000)
            print(f"Starting NiceGUI server on port {free_port}")
            ui.run(native=True, reload=False, show=False, port=free_port)
        except RuntimeError as e:
            print(f"Error finding free port: {e}")
            print("Falling back to automatic port selection (port=0)")
            # Fallback to letting the system choose a port
            ui.run(native=True, reload=False, show=False, port=0)


def main() -> None:
    """Application entry point."""
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
