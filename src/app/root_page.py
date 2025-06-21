#!/usr/bin/env python3
"""
Root page components and event handlers for the sensor visualization application.
"""

import datetime
from typing import TYPE_CHECKING, Any, Optional

from nicegui import app, ui

# Import our sensor modules
from ..data_generator import generate_sensor_data
from ..plotting import (
    create_frequency_bandwidth_plot,
    create_scanner_plot,
    update_frequency_bandwidth_plot,
    update_scanner_plot,
    PlotDataBuffer
)

if TYPE_CHECKING:
    from .app import App

# Module-level variables for the root page
dark_mode_enabled = False
dark_mode_element: ui.dark_mode | None = None
about_dialog: ui.dialog | None = None
config_dialog: ui.dialog | None = None

# Sensor application state
is_generating = False
packets_per_second = 75
data_buffer = PlotDataBuffer(max_size=300)
timer: Optional[ui.timer] = None
freq_bw_plot_element: Optional[ui.plotly] = None
scanner_plot_element: Optional[ui.plotly] = None
status_label: Optional[ui.label] = None
packets_slider: Optional[ui.slider] = None

# Selection state storage for both plots
freq_bw_selection_state = None
freq_bw_selected_points = None
scanner_selection_state = None
scanner_selected_points = None


def setup_root_page(app: "App") -> None:
    """Setup the root page (/) with sensor visualization components."""

    @ui.page("/")
    def main_page() -> None:
        """Main sensor visualization application page."""

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
                ui.label("2.4GHz Sensor Visualization").style("font-size: 24px; font-weight: bold; margin-bottom: 10px")
                ui.label("Version 1.0.0").style("font-size: 16px; color: #666; margin-bottom: 20px")

                ui.separator().style("margin: 20px 0")

                # Technical details
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("🔧 Built with:").style("font-weight: bold; margin-bottom: 5px")
                    ui.label("• NiceGUI - Modern Python UI framework")
                    ui.label("• Plotly - Interactive plotting library")
                    ui.label("• PyInstaller - Python to executable packaging")
                    ui.label("• NumPy - Numerical computing")

                ui.separator().style("margin: 20px 0")

                # Features
                with ui.column().style("gap: 8px; margin-bottom: 20px"):
                    ui.label("✨ Features:").style("font-weight: bold; margin-bottom: 5px")
                    ui.label("• Real-time 2.4GHz band visualization")
                    ui.label("• WiFi and Bluetooth signal simulation")
                    ui.label("• Frequency vs Bandwidth analysis")
                    ui.label("• Spectrum scanner display")

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
                ui.label("2.4GHz Sensor Visualization").classes("text-h6 text-weight-bold")

                ui.space()

        # Main content area with sensor visualization
        with ui.element("div").style("min-height: calc(100vh - 120px); padding: 20px"):
            with ui.column().style("width: 100%; gap: 20px"):

                # Control panel
                _setup_control_panel()

                # Plots section
                _setup_plots_section()


def _setup_control_panel() -> None:
    """Setup the sensor control panel."""
    global status_label, packets_slider
    
    with ui.card().classes("q-pa-md").style("width: 100%"):
        ui.label("📡 Sensor Control Panel").classes("text-h6 text-weight-bold q-mb-md")
        
        # Status and controls row
        with ui.row().style("width: 100%; align-items: center; gap: 20px; margin-bottom: 20px"):
            # Status display
            status_label = ui.label("Status: Stopped").classes("text-body1 text-weight-bold")
            
            ui.space()
            
            # Start/Stop controls
            with ui.row().style("gap: 10px"):
                ui.button("▶️ Start", on_click=start_generation).props("color=positive")
                ui.button("⏹️ Stop", on_click=stop_generation).props("color=negative")
                ui.button("🗑️ Clear", on_click=clear_plots).props("color=grey")
        
        # Packets per second control
        with ui.row().style("width: 100%; align-items: center; gap: 20px"):
            ui.label("Packets/Second:").style("min-width: 120px")
            packets_slider = ui.slider(
                min=10, max=5000, step=5, value=packets_per_second
            ).style("flex-grow: 1")
            packets_value_label = ui.label(f"{packets_per_second}")
            
            def on_packets_change(value: float) -> None:
                global packets_per_second
                packets_per_second = int(value)
                packets_value_label.text = str(packets_per_second)
                log_action("Packets Changed", f"New rate: {packets_per_second} packets/sec")
            
            packets_slider.on('update:model-value', lambda e: on_packets_change(e.args))


def _setup_plots_section() -> None:
    """Setup the plots display section."""
    global freq_bw_plot_element, scanner_plot_element
    
    # Create initial plots with sample data to ensure proper initialization
    initial_data = generate_sensor_data(10)  # Small sample for initialization
    initial_freq_bw = create_frequency_bandwidth_plot(initial_data)
    initial_scanner = create_scanner_plot(initial_data)
    
    log_action("Plot Setup", f"Initialized plots with {len(initial_data)} sample points")
    
    with ui.row().style("width: 100%; gap: 20px"):
        # Left plot - Frequency vs Bandwidth
        with ui.card().style("flex: 1; min-width: 500px"):
            ui.label("Frequency vs. Bandwidth").classes("text-h6 text-weight-bold q-pa-md")
            freq_bw_plot_element = ui.plotly(initial_freq_bw).style("height: 400px; width: 100%")
            
            # Add selection event handler for frequency vs bandwidth plot
            freq_bw_plot_element.on('plotly_selected', lambda e: handle_freq_bw_selection(e.args))
        
        # Right plot - Scanner
        with ui.card().style("flex: 1; min-width: 500px"):
            ui.label("Spectrum Scanner").classes("text-h6 text-weight-bold q-pa-md")
            scanner_plot_element = ui.plotly(initial_scanner).style("height: 400px; width: 100%")
            
            # Add selection event handler for scanner plot
            scanner_plot_element.on('plotly_selected', lambda e: handle_scanner_selection(e.args))
    
    log_action("Plot Elements", f"freq_bw_plot_element: {freq_bw_plot_element is not None}, scanner_plot_element: {scanner_plot_element is not None}")


def start_generation() -> None:
    """Start sensor data generation."""
    global is_generating, timer, status_label
    
    if is_generating:
        return
    
    is_generating = True
    if status_label:
        status_label.text = "Status: Running"
        status_label.classes("text-positive")
    
    # Start timer for 1Hz updates
    timer = ui.timer(1.0, update_sensor_data)
    timer.active = True
    
    log_action("Generation Started", f"Started at {packets_per_second} packets/sec")


def stop_generation() -> None:
    """Stop sensor data generation."""
    global is_generating, timer, status_label
    
    if not is_generating:
        return
    
    is_generating = False
    if status_label:
        status_label.text = "Status: Stopped"
        status_label.classes("text-grey")
    
    # Stop timer
    if timer:
        timer.active = False
        timer = None
    
    log_action("Generation Stopped", "Data generation stopped")


def clear_plots() -> None:
    """Clear all plots and reset data buffer."""
    global data_buffer, freq_bw_plot_element, scanner_plot_element
    global freq_bw_selection_state, freq_bw_selected_points, scanner_selection_state, scanner_selected_points
    
    # Clear data buffer
    data_buffer.clear()
    
    # Clear selection states
    freq_bw_selection_state = None
    freq_bw_selected_points = None
    scanner_selection_state = None
    scanner_selected_points = None
    
    # Clear plots using direct data assignment
    if freq_bw_plot_element:
        freq_bw_plot_element.figure.data[0].x = []
        freq_bw_plot_element.figure.data[0].y = []
        freq_bw_plot_element.figure.data[0].marker.color = []
        freq_bw_plot_element.figure.data[0].selectedpoints = None
        freq_bw_plot_element.figure.update_layout(shapes=[])
        freq_bw_plot_element.update()
        log_action("Plot Cleared", "Frequency vs Bandwidth plot data cleared directly")
    else:
        log_action("Plot Error", "freq_bw_plot_element is None during clear")
    
    if scanner_plot_element:
        scanner_plot_element.figure.data[0].x = []
        scanner_plot_element.figure.data[0].y = []
        scanner_plot_element.figure.data[0].marker.color = []
        scanner_plot_element.figure.data[0].marker.size = []
        scanner_plot_element.figure.data[0].selectedpoints = None
        scanner_plot_element.figure.update_layout(shapes=[])
        scanner_plot_element.update()
        log_action("Plot Cleared", "Scanner plot data cleared directly")
    else:
        log_action("Plot Error", "scanner_plot_element is None during clear")
    
    log_action("Plots Cleared", "All plots and data cleared using direct assignment")


def update_sensor_data() -> None:
    """Timer callback to generate and display new sensor data."""
    global data_buffer, freq_bw_plot_element, scanner_plot_element, packets_per_second
    
    if not is_generating:
        log_action("Update Skipped", "Generation not active")
        return
    
    try:
        # Generate new sensor data (replacing previous data, not accumulating)
        new_data = generate_sensor_data(packets_per_second)
        log_action("Data Generated", f"Generated {len(new_data)} data points at {packets_per_second} packets/sec")
        
        # Replace data in buffer (not add to it for real-time replacement)
        data_buffer.clear()
        data_buffer.add_data(new_data)
        
        # Get current data from buffer
        current_data = data_buffer.get_data()
        log_action("Data Buffered", f"Buffer contains {len(current_data)} data points")
        
        # Update plots with new data using direct data assignment and preserve selections
        if freq_bw_plot_element and current_data:
            # Extract data for frequency vs bandwidth plot
            frequencies = [freq for _, freq, _, _ in current_data]
            bandwidths = [bw for _, _, bw, _ in current_data]
            powers = [pwr for _, _, _, pwr in current_data]
            
            # Update plot data directly
            freq_bw_plot_element.figure.data[0].x = frequencies
            freq_bw_plot_element.figure.data[0].y = bandwidths
            freq_bw_plot_element.figure.data[0].marker.color = powers
            
            # Restore selection if it exists
            if freq_bw_selection_state:
                # Create selection shape
                selection_shape = {
                    'type': 'rect',
                    'x0': freq_bw_selection_state['x0'],
                    'x1': freq_bw_selection_state['x1'],
                    'y0': freq_bw_selection_state['y0'],
                    'y1': freq_bw_selection_state['y1'],
                    'line': {'color': 'blue', 'width': 2, 'dash': 'dash'},
                    'fillcolor': 'rgba(0, 0, 255, 0.1)',
                    'layer': 'above'
                }
                
                # Update layout with selection
                freq_bw_plot_element.figure.update_layout(shapes=[selection_shape])
                
                # Mark selected points
                if freq_bw_selected_points:
                    selected_indices = [i for i in freq_bw_selected_points 
                                      if i < len(frequencies)]
                    if selected_indices:
                        freq_bw_plot_element.figure.data[0].selectedpoints = selected_indices
            else:
                # Clear any existing shapes if no selection
                freq_bw_plot_element.figure.update_layout(shapes=[])
                freq_bw_plot_element.figure.data[0].selectedpoints = None
            
            freq_bw_plot_element.update()
            
            log_action("Plot Updated", f"Frequency vs Bandwidth plot data updated directly with {len(current_data)} points")
        elif freq_bw_plot_element and not current_data:
            # Clear plot data
            freq_bw_plot_element.figure.data[0].x = []
            freq_bw_plot_element.figure.data[0].y = []
            freq_bw_plot_element.figure.data[0].marker.color = []
            freq_bw_plot_element.figure.data[0].selectedpoints = None
            freq_bw_plot_element.figure.update_layout(shapes=[])
            freq_bw_plot_element.update()
            log_action("Plot Cleared", "Frequency vs Bandwidth plot data cleared")
        else:
            log_action("Plot Error", "freq_bw_plot_element is None")
        
        if scanner_plot_element and current_data:
            # Extract data for scanner plot
            frequencies = [freq for _, freq, _, _ in current_data]
            powers = [pwr for _, _, _, pwr in current_data]
            bandwidths = [bw for _, _, bw, _ in current_data]
            
            # Update plot data directly
            scanner_plot_element.figure.data[0].x = frequencies
            scanner_plot_element.figure.data[0].y = powers
            scanner_plot_element.figure.data[0].marker.color = bandwidths
            scanner_plot_element.figure.data[0].marker.size = [max(4, min(15, bw/4)) for bw in bandwidths]
            
            # Restore selection if it exists
            if scanner_selection_state:
                # Create selection shape
                selection_shape = {
                    'type': 'rect',
                    'x0': scanner_selection_state['x0'],
                    'x1': scanner_selection_state['x1'],
                    'y0': scanner_selection_state['y0'],
                    'y1': scanner_selection_state['y1'],
                    'line': {'color': 'blue', 'width': 2, 'dash': 'dash'},
                    'fillcolor': 'rgba(0, 0, 255, 0.1)',
                    'layer': 'above'
                }
                
                # Update layout with selection
                scanner_plot_element.figure.update_layout(shapes=[selection_shape])
                
                # Mark selected points
                if scanner_selected_points:
                    selected_indices = [i for i in scanner_selected_points 
                                      if i < len(frequencies)]
                    if selected_indices:
                        scanner_plot_element.figure.data[0].selectedpoints = selected_indices
            else:
                # Clear any existing shapes if no selection
                scanner_plot_element.figure.update_layout(shapes=[])
                scanner_plot_element.figure.data[0].selectedpoints = None
            
            scanner_plot_element.update()
            
            log_action("Plot Updated", f"Scanner plot data updated directly with {len(current_data)} points")
        elif scanner_plot_element and not current_data:
            # Clear plot data
            scanner_plot_element.figure.data[0].x = []
            scanner_plot_element.figure.data[0].y = []
            scanner_plot_element.figure.data[0].marker.color = []
            scanner_plot_element.figure.data[0].marker.size = []
            scanner_plot_element.figure.data[0].selectedpoints = None
            scanner_plot_element.figure.update_layout(shapes=[])
            scanner_plot_element.update()
            log_action("Plot Cleared", "Scanner plot data cleared")
        else:
            log_action("Plot Error", "scanner_plot_element is None")
            
        # Log sample data for debugging
        if current_data:
            sample = current_data[0]
            log_action("Sample Data", f"First point: freq={sample[1]:.1f}MHz, bw={sample[2]:.1f}MHz, power={sample[3]:.1f}dBm")
            
    except Exception as e:
        log_action("Update Error", f"Error updating sensor data: {e}")
        print(f"Error in update_sensor_data: {e}")
        import traceback
        traceback.print_exc()


def handle_freq_bw_selection(selection_data) -> None:
    """Handle rectangular selection on frequency vs bandwidth plot."""
    global freq_bw_selection_state, freq_bw_selected_points
    
    try:
        if selection_data:
            # Check if we have range data (preferred)
            if 'range' in selection_data:
                # Store the selection box coordinates from range
                freq_bw_selection_state = {
                    'x0': selection_data['range']['x'][0],
                    'x1': selection_data['range']['x'][1],
                    'y0': selection_data['range']['y'][0],
                    'y1': selection_data['range']['y'][1]
                }
            elif 'points' in selection_data and selection_data['points']:
                # Fallback: calculate range from selected points
                points = selection_data['points']
                frequencies = [point['x'] for point in points]
                bandwidths = [point['y'] for point in points]
                
                freq_bw_selection_state = {
                    'x0': min(frequencies),
                    'x1': max(frequencies),
                    'y0': min(bandwidths),
                    'y1': max(bandwidths)
                }
            else:
                freq_bw_selection_state = None
            
            # Store selected point indices
            if 'points' in selection_data and selection_data['points']:
                freq_bw_selected_points = [p['pointIndex'] for p in selection_data['points']]
                
                # Extract selection bounds for logging
                points = selection_data['points']
                frequencies = [point['x'] for point in points]
                bandwidths = [point['y'] for point in points]
                
                freq_min, freq_max = min(frequencies), max(frequencies)
                bw_min, bw_max = min(bandwidths), max(bandwidths)
                
                log_action("Freq/BW Selection", 
                          f"Selected {len(points)} points: "
                          f"freq={freq_min:.1f}-{freq_max:.1f}MHz, "
                          f"bw={bw_min:.1f}-{bw_max:.1f}MHz")
            else:
                freq_bw_selected_points = None
                if freq_bw_selection_state is None:
                    log_action("Freq/BW Selection", "Selection cleared")
        else:
            freq_bw_selection_state = None
            freq_bw_selected_points = None
            log_action("Freq/BW Selection", "Selection cleared")
    except Exception as e:
        log_action("Selection Error", f"Error handling freq/bw selection: {e}")


def handle_scanner_selection(selection_data) -> None:
    """Handle rectangular selection on scanner plot."""
    global scanner_selection_state, scanner_selected_points
    
    try:
        if selection_data:
            # Check if we have range data (preferred)
            if 'range' in selection_data:
                # Store the selection box coordinates from range
                scanner_selection_state = {
                    'x0': selection_data['range']['x'][0],
                    'x1': selection_data['range']['x'][1],
                    'y0': selection_data['range']['y'][0],
                    'y1': selection_data['range']['y'][1]
                }
            elif 'points' in selection_data and selection_data['points']:
                # Fallback: calculate range from selected points
                points = selection_data['points']
                frequencies = [point['x'] for point in points]
                powers = [point['y'] for point in points]
                
                scanner_selection_state = {
                    'x0': min(frequencies),
                    'x1': max(frequencies),
                    'y0': min(powers),
                    'y1': max(powers)
                }
            else:
                scanner_selection_state = None
            
            # Store selected point indices
            if 'points' in selection_data and selection_data['points']:
                scanner_selected_points = [p['pointIndex'] for p in selection_data['points']]
                
                # Extract selection bounds for logging
                points = selection_data['points']
                frequencies = [point['x'] for point in points]
                powers = [point['y'] for point in points]
                
                freq_min, freq_max = min(frequencies), max(frequencies)
                power_min, power_max = min(powers), max(powers)
                
                log_action("Scanner Selection", 
                          f"Selected {len(points)} points: "
                          f"freq={freq_min:.1f}-{freq_max:.1f}MHz, "
                          f"power={power_min:.1f}-{power_max:.1f}dBm")
            else:
                scanner_selected_points = None
                if scanner_selection_state is None:
                    log_action("Scanner Selection", "Selection cleared")
        else:
            scanner_selection_state = None
            scanner_selected_points = None
            log_action("Scanner Selection", "Selection cleared")
    except Exception as e:
        log_action("Selection Error", f"Error handling scanner selection: {e}")


def on_sensor_shutdown() -> None:
    """Handle application shutdown - stop timers."""
    global timer
    if timer:
        timer.active = False
        timer = None
    log_action("Sensor Shutdown", "Sensor timers stopped")


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
    global timer
    # Stop sensor timers before quitting
    if timer:
        timer.active = False
        timer = None
    log_action("Application Quit", "User requested quit from menu")
    app.shutdown()
    