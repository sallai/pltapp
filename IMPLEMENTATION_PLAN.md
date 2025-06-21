# Implementation Plan

## Overview
This document outlines the implementation plan for adding sensor data generation and visualization features to the NiceGUI desktop application. The application will simulate 2.4-2.5GHz band sensor data and display it in real-time scatter plots.

## Feature Requirements

### 1. Sensor Data Generation
- Function to generate synthetic sensor data for 2400-2500MHz band
- Emulate N incoming packets per second
- Return N tuples of (time, frequency, bandwidth, received_power)
- Called at 1Hz rate

### 2. Data Visualization
- Two scatter plots using NiceGUI and Plotly:
  1. Frequency vs. Bandwidth plot
  2. Scanner plot: Frequency vs. Received Power
- Real-time data updates at 1Hz

### 3. Application Integration
- Timer-based data generation and plot updates
- Main application loop with NiceGUI native mode

## Implementation Phases

### Phase 1: Core Data Generation
**Objective**: Implement synthetic sensor data generation function

**Tasks**:
1. Create `generate_sensor_data(packets_per_second: int) -> List[Tuple[float, float, float, float]]`
   - Generate realistic frequency values in 2400-2500MHz range
   - Generate bandwidth values (typical WiFi/Bluetooth ranges)
   - Generate received power values in dBm
   - Include current timestamp for each packet
   - Add realistic noise and variation to data

2. Add configuration parameters:
   - Configurable packets per second (default: 50-100)
   - Frequency band limits (2400-2500MHz)
   - Power range (-100 to -30 dBm typical)
   - Bandwidth ranges (1-80MHz typical)

### Phase 2: Plotting Infrastructure
**Objective**: Set up NiceGUI with Plotly integration

**Tasks**:
1. Install and configure Plotly dependency
   - Add `plotly` to requirements/base.txt
   - Verify NiceGUI Plotly integration

2. Create base plotting functions:
   - `create_frequency_bandwidth_plot(data: List[Tuple]) -> plotly.Figure`
   - `create_scanner_plot(data: List[Tuple]) -> plotly.Figure`
   - Configure plot styling and axes labels

3. Implement plot update mechanisms:
   - Functions to update existing plots with new data
   - Proper data buffering (keep last N seconds of data)

### Phase 3: Main Application Integration
**Objective**: Integrate data generation with UI and implement real-time updates

**Tasks**:
1. Modify main.py to include:
   - NiceGUI page setup with two plot containers
   - Timer setup for 1Hz data generation
   - Plot initialization and update handlers

2. Implement real-time update loop:
   - Timer callback to generate new sensor data
   - Update both scatter plots with new data (replacing the existing data in the current plots)

3. Add basic UI controls:
   - Start/stop data generation
   - Adjust packets per second parameter
   - Clear/reset plots

### Phase 4: Polish and Optimization
**Objective**: Improve performance and user experience

**Tasks**:
1. Performance optimization:
   - Efficient data structure management
   - Plot update optimization
   - Memory usage monitoring

2. UI enhancements:
   - Professional styling
   - Responsive layout
   - Status indicators

3. Error handling and validation:
   - Graceful handling of plot update errors
   - Input validation for parameters
   - Proper cleanup on application exit

## Technical Implementation Details

### Data Structure
```python
# Sensor data tuple format
SensorData = Tuple[float, float, float, float]  # (time, frequency, bandwidth, power)

# Example data point
data_point = (1640995200.0, 2450.5, 20.0, -65.2)
```

### Key Functions
```python
def generate_sensor_data(packets_per_second: int) -> List[SensorData]:
    """Generate synthetic sensor data for 2.4-2.5GHz band"""
    
def create_frequency_bandwidth_plot(data: List[SensorData]) -> plotly.Figure:
    """Create scatter plot of frequency vs bandwidth"""
    
def create_scanner_plot(data: List[SensorData]) -> plotly.Figure:
    """Create scanner plot of frequency vs received power"""
    
def update_plots(new_data: List[SensorData]) -> None:
    """Update both plots with new sensor data"""
```

### NiceGUI Integration
- Use `ui.plotly()` components for plot display
- Implement `ui.timer()` for 1Hz data generation
- Use `ui.run(native=True)` for desktop window

## Dependencies
- `plotly` - For plot generation and visualization
- `numpy` - For efficient data generation and manipulation
- `nicegui` - Already included for UI framework

## Success Criteria
1. Application generates realistic sensor data at 1Hz
2. Two scatter plots update in real-time
3. Application runs as standalone desktop app
4. Executable builds successfully with PyInstaller
5. Professional UI with responsive updates
6. Memory usage remains stable during extended operation

## File Structure Changes
```
├── main.py                          # Updated main application
├── src/                             # New source directory
│   ├── data_generator.py           # Sensor data generation
│   ├── plotting.py                 # Plot creation and updates
│   └── ui_components.py            # NiceGUI UI components
├── requirements/
│   └── base.txt                    # Add plotly dependency
└── config/
    └── sensor_config.json          # Sensor parameters
```

## Risk Mitigation
1. **Performance**: Implement data buffering and efficient plot updates
2. **Memory leaks**: Proper cleanup of old data points
3. **Build issues**: Test PyInstaller compatibility with Plotly
4. **UI responsiveness**: Optimize timer intervals and data processing

## Next Steps
Begin with Phase 1 implementation, focusing on core data generation functionality before moving to visualization components.

