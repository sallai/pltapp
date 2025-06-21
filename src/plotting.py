"""
Plotting module for sensor data visualization.

This module provides functions to create and update scatter plots for
2.4-2.5GHz band sensor data using Plotly and NiceGUI integration.
"""

from typing import List, Tuple, Optional
from collections import deque
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Type alias for sensor data tuples
SensorData = Tuple[float, float, float, float]  # (time, frequency, bandwidth, power)

# Plot styling constants
PLOT_HEIGHT = 400
PLOT_MARGIN = dict(l=60, r=30, t=50, b=50)
POINT_SIZE = 6
OPACITY = 0.7

# Color schemes
FREQ_BW_COLORS = px.colors.qualitative.Set3
SCANNER_COLORSCALE = 'Viridis'


class PlotDataBuffer:
    """
    Manages rolling buffer of sensor data for efficient plot updates.
    
    Maintains a fixed-size buffer to prevent memory growth while
    providing smooth real-time updates.
    """
    
    def __init__(self, max_size: int = 300):
        """
        Initialize the data buffer.
        
        Args:
            max_size: Maximum number of data points to retain
        """
        self.max_size = max_size
        self.data_buffer: deque = deque(maxlen=max_size)
    
    def add_data(self, new_data: List[SensorData]) -> None:
        """
        Add new data points to the buffer.
        
        Args:
            new_data: List of new sensor data tuples
        """
        self.data_buffer.extend(new_data)
    
    def get_data(self) -> List[SensorData]:
        """
        Get current data in the buffer.
        
        Returns:
            List of sensor data tuples
        """
        return list(self.data_buffer)
    
    def clear(self) -> None:
        """Clear all data from the buffer."""
        self.data_buffer.clear()
    
    def get_size(self) -> int:
        """Get current buffer size."""
        return len(self.data_buffer)


def create_frequency_bandwidth_plot(data: List[SensorData]) -> go.Figure:
    """
    Create scatter plot showing frequency vs. bandwidth.
    
    This plot helps visualize the relationship between frequency and
    bandwidth usage across different protocols in the 2.4GHz band.
    
    Args:
        data: List of sensor data tuples (time, frequency, bandwidth, power)
        
    Returns:
        Plotly Figure object
        
    Example:
        >>> data = [(time.time(), 2450.0, 20.0, -65.0)]
        >>> fig = create_frequency_bandwidth_plot(data)
        >>> isinstance(fig, go.Figure)
        True
    """
    if not data:
        # Create empty plot with proper axes
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[], y=[], mode='markers',
            name='No Data',
            marker=dict(size=POINT_SIZE, opacity=OPACITY)
        ))
    else:
        # Extract data arrays
        frequencies = [freq for _, freq, _, _ in data]
        bandwidths = [bw for _, _, bw, _ in data]
        powers = [pwr for _, _, _, pwr in data]
        
        # Create color mapping based on power levels for visual insight
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=frequencies,
            y=bandwidths,
            mode='markers',
            name='Sensor Data',
            marker=dict(
                size=POINT_SIZE,
                color=powers,
                colorscale=SCANNER_COLORSCALE,
                opacity=OPACITY,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Power (dBm)", side="right"),
                    x=1.02
                )
            ),
            hovertemplate=(
                'Frequency: %{x:.1f} MHz<br>'
                'Bandwidth: %{y:.1f} MHz<br>'
                'Power: %{marker.color:.1f} dBm<br>'
                '<extra></extra>'
            )
        ))
    
    # Configure layout with rectangular selection
    fig.update_layout(
        title='Frequency vs. Bandwidth Distribution',
        xaxis_title='Frequency (MHz)',
        yaxis_title='Bandwidth (MHz)',
        height=PLOT_HEIGHT,
        margin=PLOT_MARGIN,
        xaxis=dict(
            range=[2390, 2510],
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            range=[0, 85],
            gridcolor='lightgray',
            showgrid=True
        ),
        plot_bgcolor='white',
        showlegend=False,
        dragmode='select',  # Enable rectangular selection
        selectdirection='d'  # Allow diagonal selection
    )
    
    return fig


def create_scanner_plot(data: List[SensorData]) -> go.Figure:
    """
    Create scanner plot showing frequency vs. received power.
    
    This plot resembles a spectrum analyzer display, showing signal
    strength across the frequency spectrum.
    
    Args:
        data: List of sensor data tuples (time, frequency, bandwidth, power)
        
    Returns:
        Plotly Figure object
        
    Example:
        >>> data = [(time.time(), 2450.0, 20.0, -65.0)]
        >>> fig = create_scanner_plot(data)
        >>> isinstance(fig, go.Figure)
        True
    """
    if not data:
        # Create empty plot with proper axes
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[], y=[], mode='markers',
            name='No Data',
            marker=dict(size=POINT_SIZE, opacity=OPACITY)
        ))
    else:
        # Extract data arrays
        frequencies = [freq for _, freq, _, _ in data]
        powers = [pwr for _, _, _, pwr in data]
        bandwidths = [bw for _, _, bw, _ in data]
        
        # Create scatter plot with bandwidth-based sizing
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=frequencies,
            y=powers,
            mode='markers',
            name='Signal Detections',
            marker=dict(
                size=[max(4, min(15, bw/4)) for bw in bandwidths],  # Size based on bandwidth
                color=bandwidths,
                colorscale='Plasma',
                opacity=OPACITY,
                showscale=True,
                colorbar=dict(
                    title=dict(text="Bandwidth (MHz)", side="right"),
                    x=1.02
                )
            ),
            hovertemplate=(
                'Frequency: %{x:.1f} MHz<br>'
                'Power: %{y:.1f} dBm<br>'
                'Bandwidth: %{marker.color:.1f} MHz<br>'
                '<extra></extra>'
            )
        ))
    
    # Add WiFi channel markers for reference
    wifi_channels = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462]
    for i, channel in enumerate(wifi_channels):
        fig.add_vline(
            x=channel,
            line=dict(color="lightblue", width=1, dash="dot"),
            opacity=0.3
        )
        # Add channel numbers at the top
        if i % 2 == 0:  # Only label every other channel to avoid crowding
            fig.add_annotation(
                x=channel,
                y=-25,
                text=f"Ch{i+1}",
                showarrow=False,
                font=dict(size=8, color="lightblue"),
                textangle=-90
            )
    
    # Configure layout with rectangular selection
    fig.update_layout(
        title='Spectrum Scanner - Frequency vs. Signal Strength',
        xaxis_title='Frequency (MHz)',
        yaxis_title='Received Power (dBm)',
        height=PLOT_HEIGHT,
        margin=PLOT_MARGIN,
        xaxis=dict(
            range=[2390, 2510],
            gridcolor='lightgray',
            showgrid=True
        ),
        yaxis=dict(
            range=[-105, -25],
            gridcolor='lightgray',
            showgrid=True
        ),
        plot_bgcolor='white',
        showlegend=False,
        dragmode='select',  # Enable rectangular selection
        selectdirection='d'  # Allow diagonal selection
    )
    
    return fig


def update_frequency_bandwidth_plot(fig: go.Figure, data: List[SensorData]) -> go.Figure:
    """
    Update existing frequency vs. bandwidth plot with new data.
    
    Args:
        fig: Existing Plotly figure to update
        data: New sensor data to display
        
    Returns:
        Updated Plotly Figure object
    """
    if not data:
        # Clear the plot but maintain structure
        fig.data[0].x = []
        fig.data[0].y = []
        if hasattr(fig.data[0].marker, 'color'):
            fig.data[0].marker.color = []
        return fig
    
    # Extract new data
    frequencies = [freq for _, freq, _, _ in data]
    bandwidths = [bw for _, _, bw, _ in data]
    powers = [pwr for _, _, _, pwr in data]
    
    # Update trace data
    fig.data[0].x = frequencies
    fig.data[0].y = bandwidths
    fig.data[0].marker.color = powers
    
    return fig


def update_scanner_plot(fig: go.Figure, data: List[SensorData]) -> go.Figure:
    """
    Update existing scanner plot with new data.
    
    Args:
        fig: Existing Plotly figure to update
        data: New sensor data to display
        
    Returns:
        Updated Plotly Figure object
    """
    if not data:
        # Clear the plot but maintain structure
        fig.data[0].x = []
        fig.data[0].y = []
        if hasattr(fig.data[0].marker, 'color'):
            fig.data[0].marker.color = []
        if hasattr(fig.data[0].marker, 'size'):
            fig.data[0].marker.size = []
        return fig
    
    # Extract new data
    frequencies = [freq for _, freq, _, _ in data]
    powers = [pwr for _, _, _, pwr in data]
    bandwidths = [bw for _, _, bw, _ in data]
    
    # Update trace data
    fig.data[0].x = frequencies
    fig.data[0].y = powers
    fig.data[0].marker.color = bandwidths
    fig.data[0].marker.size = [max(4, min(15, bw/4)) for bw in bandwidths]
    
    return fig


def create_empty_plots() -> Tuple[go.Figure, go.Figure]:
    """
    Create empty plot figures for initialization.
    
    Returns:
        Tuple of (frequency_bandwidth_plot, scanner_plot)
    """
    freq_bw_plot = create_frequency_bandwidth_plot([])
    scanner_plot = create_scanner_plot([])
    
    return freq_bw_plot, scanner_plot


def validate_plot_data(data: List[SensorData]) -> bool:
    """
    Validate data before plotting to prevent errors.
    
    Args:
        data: Sensor data to validate
        
    Returns:
        True if data is valid for plotting, False otherwise
    """
    if not isinstance(data, list):
        return False
    
    for item in data:
        if not isinstance(item, tuple) or len(item) != 4:
            return False
        
        timestamp, frequency, bandwidth, power = item
        
        # Check for valid numeric types
        if not all(isinstance(x, (int, float)) for x in [timestamp, frequency, bandwidth, power]):
            return False
        
        # Check for reasonable ranges (not NaN or infinite)
        if not all(np.isfinite(x) for x in [timestamp, frequency, bandwidth, power]):
            return False
    
    return True