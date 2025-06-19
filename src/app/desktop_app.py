#!/usr/bin/env python3
"""
NiceGUI Desktop Application

A simple technology demonstration showing NiceGUI UI components
in a native window, ready for PyInstaller packaging.
"""

import asyncio
import datetime
import socket
from typing import Any

from nicegui import app, ui


class DesktopApp:
    """Main desktop application class."""

    def __init__(self) -> None:
        """Initialize the desktop application."""
        self.dark_mode = False  # Configuration state
        self.clock_label: ui.label | None = None
        self.clock_task: asyncio.Task | None = None
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

    async def update_clock(self) -> None:
        """Periodically update the clock display."""
        while True:
            if self.clock_label:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                self.clock_label.text = f"Current Time: {current_time}"
            await asyncio.sleep(1)

    def log_action(self, action: str, details: str = "") -> None:
        """Log UI actions to console with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] UI Action: {action}"
        if details:
            log_message += f" - {details}"
        print(log_message)

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        theme = "dark" if self.dark_mode else "light"

        self.log_action("Theme Toggle", f"Switched to {theme} mode")

        # Apply theme by updating CSS
        if self.dark_mode:
            ui.query("body").style("background-color: #121212; color: #ffffff")
            ui.query(".nicegui-content").style("background-color: #121212")
        else:
            ui.query("body").style("background-color: #ffffff; color: #000000")
            ui.query(".nicegui-content").style("background-color: #ffffff")

    def show_config_dialog(self) -> None:
        """Show configuration dialog."""
        self.log_action("Config Dialog", "Opened configuration dialog")

        with ui.dialog() as dialog, ui.card():
            ui.label("Configuration").style(
                "font-size: 18px; font-weight: bold; margin-bottom: 15px"
            )

            with ui.row().style("align-items: center; margin-bottom: 10px"):
                ui.label("Theme:")
                theme_switch = ui.switch("Dark Mode", value=self.dark_mode)

                def on_theme_change(event: Any) -> None:
                    new_value = (
                        event.args
                        if isinstance(event.args, bool)
                        else event.args[0] if event.args else False
                    )
                    if new_value != self.dark_mode:
                        self.toggle_theme()
                        self.log_action("Theme Changed", f"Dark mode: {new_value}")

                theme_switch.on("update:model-value", on_theme_change)

            with ui.row().style("margin-top: 20px"):
                ui.button("Close", on_click=dialog.close).style("margin-right: 10px")

                def reset_settings() -> None:
                    self.dark_mode = False
                    theme_switch.value = False
                    self.toggle_theme()
                    self.log_action("Settings Reset", "Reset to default theme")

                ui.button("Reset to Default", on_click=reset_settings).style(
                    "background-color: #ff9800"
                )

        dialog.open()

    def setup_pages(self) -> None:
        """Setup application pages and UI components."""

        @ui.page("/")
        def main_page() -> None:
            """Main application page with enhanced UI components."""
            # Menu bar
            with ui.header().style("background-color: #1976d2; padding: 10px"):
                ui.label("NiceGUI Desktop Demo").style(
                    "font-size: 20px; font-weight: bold; color: white"
                )
                ui.space()
                ui.button("⚙️ Config", on_click=self.show_config_dialog).style(
                    "background-color: transparent; color: white; border: 1px solid white"
                )

            # Main content area
            with ui.column().style("padding: 20px; max-width: 600px; margin: 0 auto"):
                # Clock display (periodic async updates)
                self.clock_label = ui.label("Loading time...").style(
                    "font-size: 24px; font-weight: bold; color: #1976d2; margin-bottom: 20px; text-align: center"
                )

                # Start the clock update task
                if not self.clock_task or self.clock_task.done():
                    self.clock_task = asyncio.create_task(self.update_clock())

                ui.separator().style("margin: 20px 0")

                # Text input section
                ui.label("Text Processing Demo:").style(
                    "font-size: 18px; margin-bottom: 10px"
                )

                text_input = ui.input("Enter some text here...").style(
                    "margin-bottom: 10px; width: 100%"
                )
                result_label = ui.label("Result will appear here").style(
                    "font-weight: bold; color: #1976d2; margin-bottom: 10px; min-height: 24px"
                )

                def on_text_change() -> None:
                    """Process text input and update result display."""
                    input_text = text_input.value or ""
                    if input_text:
                        result_text = f"✓ You typed: '{input_text}' (Length: {len(input_text)} chars)"
                        result_label.style("color: #4caf50")
                    else:
                        result_text = "⚠️ No text entered"
                        result_label.style("color: #ff9800")

                    result_label.text = result_text
                    self.log_action(
                        "Text Processing",
                        f"Input: '{input_text}', Length: {len(input_text)}",
                    )

                def clear_text() -> None:
                    """Clear text input and result."""
                    text_input.value = ""
                    result_label.text = "Result will appear here"
                    result_label.style("color: #1976d2")
                    self.log_action("Text Cleared", "Input field and result cleared")

                with ui.row().style("margin: 10px 0; gap: 10px"):
                    ui.button("Process Text", on_click=on_text_change).style(
                        "background-color: #4caf50"
                    )
                    ui.button("Clear", on_click=clear_text).style(
                        "background-color: #ff9800"
                    )

                ui.separator().style("margin: 20px 0")

                # Counter demo (UI actions affecting Python state)
                ui.label("Counter Demo:").style("font-size: 18px; margin-bottom: 10px")

                counter_value = 0
                counter_label = ui.label(f"Count: {counter_value}").style(
                    "font-size: 16px; font-weight: bold; margin-bottom: 10px"
                )

                def increment() -> None:
                    nonlocal counter_value
                    counter_value += 1
                    counter_label.text = f"Count: {counter_value}"
                    self.log_action("Counter Increment", f"New value: {counter_value}")

                def decrement() -> None:
                    nonlocal counter_value
                    counter_value -= 1
                    counter_label.text = f"Count: {counter_value}"
                    self.log_action("Counter Decrement", f"New value: {counter_value}")

                def reset_counter() -> None:
                    nonlocal counter_value
                    old_value = counter_value
                    counter_value = 0
                    counter_label.text = f"Count: {counter_value}"
                    self.log_action("Counter Reset", f"Reset from {old_value} to 0")

                with ui.row().style("gap: 10px; margin-bottom: 20px"):
                    ui.button("+ Increment", on_click=increment).style(
                        "background-color: #4caf50"
                    )
                    ui.button("- Decrement", on_click=decrement).style(
                        "background-color: #ff9800"
                    )
                    ui.button("Reset", on_click=reset_counter).style(
                        "background-color: #9e9e9e"
                    )

                ui.separator().style("margin: 20px 0")

                # App controls
                def shutdown_app() -> None:
                    """Shutdown the application gracefully."""
                    self.log_action("Application Shutdown", "User requested shutdown")
                    if self.clock_task and not self.clock_task.done():
                        self.clock_task.cancel()
                    app.shutdown()

                ui.button("🔴 Shutdown Application", on_click=shutdown_app).style(
                    "background-color: #d32f2f; color: white; margin-top: 10px"
                )

    def setup_shutdown_handler(self) -> None:
        """Setup application shutdown event handler."""

        @app.on_shutdown
        def shutdown() -> None:
            """Handle application shutdown event."""
            if self.clock_task and not self.clock_task.done():
                self.clock_task.cancel()
            self.log_action("Application Shutdown", "Cleanup completed")
            print(f"Application shutdown: {datetime.datetime.now()}")

    def run(self) -> None:
        """Run the desktop application."""
        print(f"Application starting: {datetime.datetime.now()}")
        self.log_action("Application Startup", "NiceGUI desktop app initialized")

        # Find a free port (starting from 8000, avoiding common ports like 8001)
        try:
            free_port = self.find_free_port(start_port=8000)
            print(f"Starting NiceGUI server on port {free_port}")
            self.log_action(
                "Server Start", f"NiceGUI server starting on port {free_port}"
            )
            ui.run(native=True, reload=False, show=False, port=free_port)
        except RuntimeError as e:
            print(f"Error finding free port: {e}")
            print("Falling back to automatic port selection (port=0)")
            self.log_action("Port Fallback", "Using automatic port selection")
            # Fallback to letting the system choose a port
            ui.run(native=True, reload=False, show=False, port=0)


def main() -> None:
    """Application entry point."""
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
