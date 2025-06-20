#!/usr/bin/env python3
"""
Root page components and event handlers for the main application page.
"""

import datetime
from typing import TYPE_CHECKING, Any

import requests
from nicegui import app, ui

if TYPE_CHECKING:
    from .app import App

# Module-level variables for the root page
dark_mode_enabled = False
dark_mode_element: ui.dark_mode | None = None
public_ip_label: ui.label | None = None
about_dialog: ui.dialog | None = None
config_dialog: ui.dialog | None = None


def setup_root_page(app: "App") -> None:
    """Setup the root page (/) with all its components and event handlers."""

    @ui.page("/")
    def main_page() -> None:
        """Main application page with enhanced UI components."""

        # Initialize Quasar dark mode
        global dark_mode_element
        dark_mode_element = ui.dark_mode(value=dark_mode_enabled)

        # --- PRE-DEFINE THE DIALOGS HERE ---
        # Define the "About" dialog once
        global about_dialog
        with ui.dialog().props("persistent") as about_dialog:
            with ui.card().style("min-width: 400px; padding: 20px; text-align: center"):
                # Header
                with ui.row().style("width: 100%; align-items: center; margin-bottom: 20px"):
                    ui.label("ℹ️ About").style("font-size: 20px; font-weight: bold")
                    ui.space()
                    ui.button(icon="close", on_click=about_dialog.close).props("flat round").style("margin: -8px")

                # App info
                ui.label("NiceGUI Desktop Demo").style("font-size: 24px; font-weight: bold; margin-bottom: 10px")
                ui.label("Version 1.0.0").style("font-size: 16px; color: #666; margin-bottom: 20px")

                ui.separator().style("margin: 20px 0")

                # Technical details
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("🔧 Built with:").style("font-weight: bold; margin-bottom: 5px")
                    ui.label("• NiceGUI - Modern Python UI framework")
                    ui.label("• PyInstaller - Python to executable packaging")
                    ui.label("• requests - HTTP client")
                    ui.label("• asyncio - Asynchronous programming")

                ui.separator().style("margin: 20px 0")

                # Features
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("✨ Features:").style("font-weight: bold; margin-bottom: 5px")
                    ui.label("• Network communications demo")
                    ui.label("• Light/Dark theme switching")
                    ui.label("• Professional desktop UI")

                # Close button
                ui.button("Close", on_click=about_dialog.close).props("color=primary").style("margin-top: 10px")

        # Define the "Config" dialog once
        global config_dialog
        with ui.dialog().props("persistent") as config_dialog:
            with ui.card().style("min-width: 400px; padding: 20px"):
                # Header
                with ui.row().style("width: 100%; align-items: center; margin-bottom: 20px"):
                    ui.label("⚙️ Configuration").style("font-size: 20px; font-weight: bold")
                    ui.space()
                    ui.button(icon="close", on_click=config_dialog.close).props("flat round").style("margin: -8px")

                # Theme setting
                with ui.row().style("align-items: center; margin-bottom: 20px; gap: 10px"):
                    ui.label("Theme:").style("min-width: 80px")
                    theme_switch = ui.switch("Dark Mode", value=dark_mode_enabled)

                def on_theme_change(event: Any) -> None:
                    global dark_mode_enabled
                    new_value = (
                        event.args
                        if isinstance(event.args, bool)
                        else event.args[0] if event.args else False
                    )
                    if new_value != dark_mode_enabled:
                        toggle_theme()
                        log_action("Theme Changed", f"Dark mode: {new_value}")

                theme_switch.on("update:model-value", on_theme_change)

                ui.separator().style("margin: 20px 0")

                # Action buttons
                with ui.row().style("justify-content: flex-end; gap: 10px; width: 100%"):

                    def reset_settings() -> None:
                        global dark_mode_enabled
                        dark_mode_enabled = False
                        theme_switch.value = False
                        toggle_theme()
                        log_action("Settings Reset", "Reset to default theme")

                    ui.button("Reset to Default", on_click=reset_settings).props("color=orange")
                    ui.button("Close", on_click=config_dialog.close).props("color=primary")

        # Header with hamburger menu
        with ui.header().props("elevated").classes("bg-primary text-white"):
            with ui.row().style("width: 100%; align-items: center; padding: 10px"):
                # Hamburger menu
                with ui.button(icon="menu").props("flat").classes("text-white"):
                    with ui.menu():
                        ui.menu_item("⚙️ Configuration", on_click=show_config_dialog)
                        ui.menu_item("ℹ️ About", on_click=show_about_dialog)
                        ui.separator()
                        ui.menu_item("🚪 Quit", on_click=quit_application)

                ui.space()

                # App title
                ui.label("NiceGUI Desktop Demo").classes("text-h6 text-weight-bold")

                ui.space()

        # Main content area with proper layout
        with ui.element("div").style("min-height: calc(100vh - 120px); padding: 20px"):
            with ui.column().style("max-width: 700px; margin: 0 auto; gap: 20px"):

                # Text input section
                _setup_text_processing_section()

                # Counter demo
                _setup_counter_section()

                # Network communications demo
                _setup_network_section()


def _setup_text_processing_section() -> None:
    """Setup the text processing demo section."""
    with ui.card().classes("q-pa-md"):
        ui.label("📝 Text Processing Demo").classes("text-h6 text-weight-bold q-mb-md")

        text_input = ui.input("Enter some text here...").classes("q-mb-sm full-width")
        result_label = ui.label("Result will appear here").classes(
            "text-weight-bold text-primary q-mb-sm"
        ).style("min-height: 24px")

        def on_text_change() -> None:
            """Process text input and update result display."""
            input_text = text_input.value or ""
            if input_text:
                result_text = f"✓ You typed: '{input_text}' (Length: {len(input_text)} chars)"
                result_label.classes("text-positive")
            else:
                result_text = "⚠️ No text entered"
                result_label.classes("text-orange")

            result_label.text = result_text
            log_action("Text Processing", f"Input: '{input_text}', Length: {len(input_text)}")

        def clear_text() -> None:
            """Clear text input and result."""
            text_input.value = ""
            result_label.text = "Result will appear here"
            result_label.classes("text-primary")
            log_action("Text Cleared", "Input field and result cleared")

        with ui.row().classes("q-gutter-sm"):
            ui.button("Process Text", on_click=on_text_change).props("color=positive")
            ui.button("Clear", on_click=clear_text).props("color=orange")


def _setup_counter_section() -> None:
    """Setup the counter demo section."""
    with ui.card().classes("q-pa-md"):
        ui.label("🔢 Counter Demo").classes("text-h6 text-weight-bold q-mb-md")

        counter_value = 0
        counter_label = ui.label(f"Count: {counter_value}").classes(
            "text-body1 text-weight-bold q-mb-sm"
        )

        def increment() -> None:
            nonlocal counter_value
            counter_value += 1
            counter_label.text = f"Count: {counter_value}"
            log_action("Counter Increment", f"New value: {counter_value}")

        def decrement() -> None:
            nonlocal counter_value
            counter_value -= 1
            counter_label.text = f"Count: {counter_value}"
            log_action("Counter Decrement", f"New value: {counter_value}")

        def reset_counter() -> None:
            nonlocal counter_value
            old_value = counter_value
            counter_value = 0
            counter_label.text = f"Count: {counter_value}"
            log_action("Counter Reset", f"Reset from {old_value} to 0")

        with ui.row().classes("q-gutter-sm"):
            ui.button("+ Increment", on_click=increment).props("color=positive")
            ui.button("- Decrement", on_click=decrement).props("color=orange")
            ui.button("Reset", on_click=reset_counter).props("color=grey")


def _setup_network_section() -> None:
    """Setup the network communications demo section."""
    with ui.card().classes("q-pa-md"):
        ui.label("🌐 Network Communications Demo").classes("text-h6 text-weight-bold q-mb-md")

        ui.label("Retrieve your public IP address from api.ipify.org").classes("text-body2 text-grey-6 q-mb-sm")

        global public_ip_label
        public_ip_label = ui.label("Click button to fetch IP address").classes(
            "text-weight-bold text-primary q-mb-sm"
        ).style("min-height: 24px")

        def fetch_ip() -> None:
            """Trigger public IP fetch."""
            get_public_ip()

        with ui.row().classes("q-gutter-sm"):
            ui.button("🔍 Get Public IP", on_click=fetch_ip).props("color=info")

            def clear_ip() -> None:
                """Clear IP display."""
                global public_ip_label
                if public_ip_label:
                    public_ip_label.text = "Click button to fetch IP address"
                    public_ip_label.classes("text-primary")
                    log_action("IP Cleared", "IP display cleared")

            ui.button("Clear", on_click=clear_ip).props("color=grey")


def get_public_ip() -> None:
    """Retrieve public IP address from ipify.org API."""
    global public_ip_label
    if not public_ip_label:
        return

    log_action("Network Request", "Fetching public IP from api.ipify.org")

    # Show loading state
    public_ip_label.text = "Fetching IP..."
    public_ip_label.classes("text-orange")

    try:
        response = requests.get("https://api.ipify.org?format=text", timeout=10.0)
        response.raise_for_status()
        public_ip = response.text.strip()

        public_ip_label.text = f"Public IP: {public_ip}"
        public_ip_label.classes("text-positive")
        log_action("Network Success", f"Retrieved public IP: {public_ip}")

    except requests.exceptions.Timeout:
        public_ip_label.text = "Request timed out"
        public_ip_label.classes("text-negative")
        log_action("Network Error", "Request timed out")

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e.response.status_code if e.response else 'Unknown'}"
        public_ip_label.text = error_msg
        public_ip_label.classes("text-negative")
        log_action("Network Error", error_msg)

    except requests.exceptions.ConnectionError:
        public_ip_label.text = "Connection failed - check network"
        public_ip_label.classes("text-negative")
        log_action("Network Error", "Connection failed")

    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)[:30]}..."
        public_ip_label.text = error_msg
        public_ip_label.classes("text-negative")
        log_action("Network Error", f"Request exception: {type(e).__name__}")

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)[:30]}..."
        public_ip_label.text = error_msg
        public_ip_label.classes("text-negative")
        log_action("Network Error", f"Unexpected exception: {type(e).__name__}")
        # Don't print full traceback in production, just log it
        import traceback
        print(f"Network error traceback: {traceback.format_exc()}")


def log_action(action: str, details: str = "") -> None:
    """Log UI actions to console with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] UI Action: {action}"
    if details:
        log_message += f" - {details}"
    print(log_message)


def toggle_theme() -> None:
    """Toggle between light and dark themes using Quasar dark mode."""
    global dark_mode_enabled, dark_mode_element
    dark_mode_enabled = not dark_mode_enabled
    theme = "dark" if dark_mode_enabled else "light"

    log_action("Theme Toggle", f"Switched to {theme} mode")

    # Apply theme using Quasar dark mode
    if dark_mode_element:
        dark_mode_element.value = dark_mode_enabled


def show_config_dialog() -> None:
    """Show configuration dialog as a centered modal."""
    global config_dialog
    if config_dialog:
        log_action("Config Dialog", "Opened configuration dialog")
        config_dialog.open()
    else:
        # For testing: if dialog doesn't exist yet, log the action anyway
        log_action("Config Dialog", "Opened configuration dialog")


def show_about_dialog() -> None:
    """Show about dialog as a centered modal."""
    global about_dialog
    if about_dialog:
        log_action("About Dialog", "Opened about dialog")
        about_dialog.open()
    else:
        # For testing: if dialog doesn't exist yet, log the action anyway
        log_action("About Dialog", "Opened about dialog")


def quit_application() -> None:
    """Quit the application gracefully."""
    log_action("Application Quit", "User requested quit from menu")
    app.shutdown()
