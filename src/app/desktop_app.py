#!/usr/bin/env python3
"""
NiceGUI Desktop Application

A simple technology demonstration showing NiceGUI UI components
in a native window, ready for PyInstaller packaging.
"""

import datetime

from nicegui import app, ui


class DesktopApp:
    """Main desktop application class."""

    def __init__(self) -> None:
        """Initialize the desktop application."""
        self.setup_pages()
        self.setup_shutdown_handler()

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

        ui.run(native=True, reload=False, show=False, port=0)


def main() -> None:
    """Application entry point."""
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
