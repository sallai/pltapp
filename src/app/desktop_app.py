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

import httpx
from nicegui import app, ui


class DesktopApp:
    """Main desktop application class."""

    def __init__(self) -> None:
        """Initialize the desktop application."""
        self.dark_mode = False  # Configuration state
        self.clock_label: ui.label | None = None
        self.clock_task: asyncio.Task | None = None
        self.public_ip_label: ui.label | None = None
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
                self.clock_label.text = current_time
            await asyncio.sleep(1)

    async def get_public_ip(self) -> None:
        """Retrieve public IP address from ipify.org API."""
        if not self.public_ip_label:
            return

        self.log_action("Network Request", "Fetching public IP from api.ipify.org")

        # Show loading state
        self.public_ip_label.text = "Fetching IP..."
        self.public_ip_label.style("color: #ff9800")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://api.ipify.org?format=text")
                response.raise_for_status()
                public_ip = response.text.strip()

                self.public_ip_label.text = f"Public IP: {public_ip}"
                self.public_ip_label.style("color: #4caf50")
                self.log_action("Network Success", f"Retrieved public IP: {public_ip}")

        except httpx.TimeoutException:
            self.public_ip_label.text = "Request timed out"
            self.public_ip_label.style("color: #d32f2f")
            self.log_action("Network Error", "Request timed out")

        except httpx.HTTPStatusError as e:
            self.public_ip_label.text = f"HTTP Error: {e.response.status_code}"
            self.public_ip_label.style("color: #d32f2f")
            self.log_action("Network Error", f"HTTP {e.response.status_code}")

        except Exception as e:
            self.public_ip_label.text = f"Error: {str(e)[:50]}..."
            self.public_ip_label.style("color: #d32f2f")
            self.log_action("Network Error", f"Exception: {type(e).__name__}")

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
        """Show configuration dialog as a centered modal."""
        self.log_action("Config Dialog", "Opened configuration dialog")

        with ui.dialog().props("persistent") as dialog:
            with ui.card().style("min-width: 400px; padding: 20px"):
                # Header
                with ui.row().style(
                    "width: 100%; align-items: center; margin-bottom: 20px"
                ):
                    ui.label("⚙️ Configuration").style(
                        "font-size: 20px; font-weight: bold"
                    )
                    ui.space()
                    ui.button(icon="close", on_click=dialog.close).props(
                        "flat round"
                    ).style("margin: -8px")

                # Theme setting
                with ui.row().style(
                    "align-items: center; margin-bottom: 20px; gap: 10px"
                ):
                    ui.label("Theme:").style("min-width: 80px")
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

                ui.separator().style("margin: 20px 0")

                # Action buttons
                with ui.row().style(
                    "justify-content: flex-end; gap: 10px; width: 100%"
                ):

                    def reset_settings() -> None:
                        self.dark_mode = False
                        theme_switch.value = False
                        self.toggle_theme()
                        self.log_action("Settings Reset", "Reset to default theme")

                    ui.button("Reset to Default", on_click=reset_settings).style(
                        "background-color: #ff9800"
                    )
                    ui.button("Close", on_click=dialog.close).style(
                        "background-color: #1976d2"
                    )

            dialog.open()


    def show_about_dialog(self) -> None:
        """Show about dialog as a centered modal."""

        self.log_action("About Dialog", "Opened about dialog")

        with ui.dialog().props("persistent") as dialog:
            with ui.card().style(
                "min-width: 400px; padding: 20px; text-align: center"
            ):
                # Header
                with ui.row().style(
                    "width: 100%; align-items: center; margin-bottom: 20px"
                ):
                    ui.label("ℹ️ About").style("font-size: 20px; font-weight: bold")
                    ui.space()
                    ui.button(icon="close", on_click=dialog.close).props(
                        "flat round"
                    ).style("margin: -8px")

                # App info
                ui.label("NiceGUI Desktop Demo").style(
                    "font-size: 24px; font-weight: bold; margin-bottom: 10px"
                )
                ui.label("Version 1.0.0").style(
                    "font-size: 16px; color: #666; margin-bottom: 20px"
                )

                ui.separator().style("margin: 20px 0")

                # Technical details
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("🔧 Built with:").style(
                        "font-weight: bold; margin-bottom: 5px"
                    )
                    ui.label("• NiceGUI - Modern Python UI framework")
                    ui.label("• PyInstaller - Python to executable packaging")
                    ui.label("• httpx - Async HTTP client")
                    ui.label("• asyncio - Asynchronous programming")

                ui.separator().style("margin: 20px 0")

                # Features
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("✨ Features:").style(
                        "font-weight: bold; margin-bottom: 5px"
                    )
                    ui.label("• Real-time clock updates")
                    ui.label("• Network communications demo")
                    ui.label("• Light/Dark theme switching")
                    ui.label("• Professional desktop UI")

                # Close button
                ui.button("Close", on_click=dialog.close).style(
                    "background-color: #1976d2; margin-top: 10px"
                )

        dialog.open()


    def setup_pages(self) -> None:
        """Setup application pages and UI components."""

        @ui.page("/")
        def main_page() -> None:
            """Main application page with enhanced UI components."""
            # Header with hamburger menu
            with ui.header().style(
                "background-color: #1976d2; padding: 10px; height: 60px"
            ):
                with ui.row().style("width: 100%; align-items: center"):
                    # Hamburger menu
                    with ui.button(icon="menu").style(
                        "background-color: transparent; color: white"
                    ):
                        with ui.menu():
                            ui.menu_item(
                                "⚙️ Configuration", on_click=self.show_config_dialog
                            )
                            ui.menu_item("ℹ️ About", on_click=self.show_about_dialog)

                    ui.space()

                    # App title
                    ui.label("NiceGUI Desktop Demo").style(
                        "font-size: 20px; font-weight: bold; color: white"
                    )

                    ui.space()

            # Main content area with proper layout
            with ui.element("div").style(
                "min-height: calc(100vh - 120px); padding: 20px"
            ):
                with ui.column().style("max-width: 700px; margin: 0 auto; gap: 20px"):

                    # Text input section
                    with ui.card().style("padding: 20px"):
                        ui.label("📝 Text Processing Demo").style(
                            "font-size: 18px; font-weight: bold; margin-bottom: 15px"
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
                            self.log_action(
                                "Text Cleared", "Input field and result cleared"
                            )

                        with ui.row().style("gap: 10px"):
                            ui.button("Process Text", on_click=on_text_change).style(
                                "background-color: #4caf50"
                            )
                            ui.button("Clear", on_click=clear_text).style(
                                "background-color: #ff9800"
                            )

                    # Counter demo
                    with ui.card().style("padding: 20px"):
                        ui.label("🔢 Counter Demo").style(
                            "font-size: 18px; font-weight: bold; margin-bottom: 15px"
                        )

                        counter_value = 0
                        counter_label = ui.label(f"Count: {counter_value}").style(
                            "font-size: 16px; font-weight: bold; margin-bottom: 10px"
                        )

                        def increment() -> None:
                            nonlocal counter_value
                            counter_value += 1
                            counter_label.text = f"Count: {counter_value}"
                            self.log_action(
                                "Counter Increment", f"New value: {counter_value}"
                            )

                        def decrement() -> None:
                            nonlocal counter_value
                            counter_value -= 1
                            counter_label.text = f"Count: {counter_value}"
                            self.log_action(
                                "Counter Decrement", f"New value: {counter_value}"
                            )

                        def reset_counter() -> None:
                            nonlocal counter_value
                            old_value = counter_value
                            counter_value = 0
                            counter_label.text = f"Count: {counter_value}"
                            self.log_action(
                                "Counter Reset", f"Reset from {old_value} to 0"
                            )

                        with ui.row().style("gap: 10px"):
                            ui.button("+ Increment", on_click=increment).style(
                                "background-color: #4caf50"
                            )
                            ui.button("- Decrement", on_click=decrement).style(
                                "background-color: #ff9800"
                            )
                            ui.button("Reset", on_click=reset_counter).style(
                                "background-color: #9e9e9e"
                            )

                    # Network communications demo
                    with ui.card().style("padding: 20px"):
                        ui.label("🌐 Network Communications Demo").style(
                            "font-size: 18px; font-weight: bold; margin-bottom: 15px"
                        )

                        ui.label(
                            "Retrieve your public IP address from api.ipify.org"
                        ).style("margin-bottom: 10px; color: #666")

                        self.public_ip_label = ui.label(
                            "Click button to fetch IP address"
                        ).style(
                            "font-weight: bold; color: #1976d2; margin-bottom: 10px; min-height: 24px"
                        )

                        def fetch_ip() -> None:
                            """Trigger public IP fetch."""
                            asyncio.create_task(self.get_public_ip())

                        with ui.row().style("gap: 10px"):
                            ui.button("🔍 Get Public IP", on_click=fetch_ip).style(
                                "background-color: #2196f3"
                            )

                            def clear_ip() -> None:
                                """Clear IP display."""
                                if self.public_ip_label:
                                    self.public_ip_label.text = (
                                        "Click button to fetch IP address"
                                    )
                                    self.public_ip_label.style("color: #1976d2")
                                    self.log_action("IP Cleared", "IP display cleared")

                            ui.button("Clear", on_click=clear_ip).style(
                                "background-color: #9e9e9e"
                            )

                    # App controls
                    with ui.card().style("padding: 20px"):
                        ui.label("🎛️ Application Controls").style(
                            "font-size: 18px; font-weight: bold; margin-bottom: 15px"
                        )

                        def shutdown_app() -> None:
                            """Shutdown the application gracefully."""
                            self.log_action(
                                "Application Shutdown", "User requested shutdown"
                            )
                            if self.clock_task and not self.clock_task.done():
                                self.clock_task.cancel()
                            app.shutdown()

                        ui.button(
                            "🔴 Shutdown Application", on_click=shutdown_app
                        ).style("background-color: #d32f2f; color: white")

            # Status bar at bottom
            with ui.footer().style(
                "background-color: #f5f5f5; padding: 10px; height: 40px; border-top: 1px solid #ddd"
            ):
                with ui.row().style(
                    "width: 100%; align-items: center; justify-content: space-between"
                ):
                    ui.label("Ready").style("color: #666; font-size: 14px")

                    # Clock in bottom right
                    self.clock_label = ui.label("Loading...").style(
                        "color: #666; font-size: 14px; font-family: monospace"
                    )

            # Start the clock update task
            if not self.clock_task or self.clock_task.done():
                self.clock_task = asyncio.create_task(self.update_clock())

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
