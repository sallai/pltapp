"""
Sensor data generation module for 2.4-2.5GHz band simulation.

This module provides functions to generate synthetic sensor data that emulates
incoming packets in the 2400-2500MHz frequency band, commonly used by WiFi,
Bluetooth, and other wireless protocols.
"""

import random
import time
from typing import List, Tuple

# Type alias for sensor data tuples
SensorData = Tuple[float, float, float, float]  # (time, frequency, bandwidth, power)

# Configuration constants
FREQ_MIN = 2400.0  # MHz
FREQ_MAX = 2500.0  # MHz
POWER_MIN = -100.0  # dBm
POWER_MAX = -30.0   # dBm
BANDWIDTH_MIN = 1.0  # MHz
BANDWIDTH_MAX = 80.0  # MHz

# Common WiFi channel frequencies in 2.4GHz band
WIFI_CHANNELS = [2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447, 2452, 2457, 2462, 2467, 2472]

# Common Bluetooth frequencies (hops across the band)
BLUETOOTH_BASE = 2402.0  # MHz, Bluetooth starts at 2402 MHz with 1 MHz spacing


def generate_sensor_data(packets_per_second: int = 75) -> List[SensorData]:
    """
    Generate synthetic sensor data for the 2.4-2.5GHz band.
    
    Simulates N incoming packets per second with realistic frequency distributions
    that include WiFi channels, Bluetooth hopping, and other ISM band devices.
    
    Args:
        packets_per_second: Number of packets to generate (default: 75)
        
    Returns:
        List of tuples containing (timestamp, frequency, bandwidth, received_power)
        
    Example:
        >>> data = generate_sensor_data(50)
        >>> len(data)
        50
        >>> isinstance(data[0], tuple)
        True
        >>> len(data[0])
        4
    """
    current_time = time.time()
    sensor_data = []
    
    for i in range(packets_per_second):
        # Generate timestamp with some jitter to simulate real packet arrivals
        timestamp = current_time + random.uniform(-0.1, 0.1)
        
        # Generate frequency based on realistic distributions
        frequency = _generate_realistic_frequency()
        
        # Generate bandwidth based on protocol type implied by frequency
        bandwidth = _generate_realistic_bandwidth(frequency)
        
        # Generate received power with realistic variation
        power = _generate_realistic_power(frequency)
        
        sensor_data.append((timestamp, frequency, bandwidth, power))
    
    return sensor_data


def _generate_realistic_frequency() -> float:
    """
    Generate realistic frequency values based on actual 2.4GHz band usage.
    
    Weights the frequency generation to favor:
    - WiFi channels (most common)
    - Bluetooth frequencies
    - Other ISM band devices
    
    Returns:
        Frequency in MHz
    """
    # 60% chance of WiFi channel, 30% Bluetooth, 10% other
    rand = random.random()
    
    if rand < 0.6:
        # WiFi channel with some frequency offset due to channel width
        base_channel = random.choice(WIFI_CHANNELS)
        # Add small offset for channel edges and interference
        offset = random.uniform(-11.0, 11.0)  # 22MHz channel width
        return max(FREQ_MIN, min(FREQ_MAX, base_channel + offset))
    
    elif rand < 0.9:
        # Bluetooth frequency hopping
        hop_channel = random.randint(0, 78)  # 79 channels, 0-78
        bluetooth_freq = BLUETOOTH_BASE + hop_channel
        return min(FREQ_MAX, bluetooth_freq)
    
    else:
        # Other ISM band devices (microwave ovens, industrial devices, etc.)
        return random.uniform(FREQ_MIN, FREQ_MAX)


def _generate_realistic_bandwidth(frequency: float) -> float:
    """
    Generate realistic bandwidth based on the frequency and implied protocol.
    
    Args:
        frequency: The center frequency in MHz
        
    Returns:
        Bandwidth in MHz
    """
    # Check if frequency is close to a WiFi channel
    for wifi_freq in WIFI_CHANNELS:
        if abs(frequency - wifi_freq) < 15:
            # WiFi: 20MHz (802.11n/g) or 40MHz (802.11n) most common
            return random.choice([20.0, 40.0]) if random.random() < 0.8 else random.choice([5.0, 10.0, 80.0])
    
    # Check if it's in Bluetooth range
    if BLUETOOTH_BASE <= frequency <= BLUETOOTH_BASE + 78:
        # Bluetooth Classic: ~1MHz, BLE: ~2MHz, Enhanced: up to 2MHz
        return random.choice([1.0, 1.0, 1.0, 2.0])  # Favor 1MHz
    
    # Other devices - wider range
    return random.uniform(BANDWIDTH_MIN, 20.0)


def _generate_realistic_power(frequency: float) -> float:
    """
    Generate realistic received power levels.
    
    Power levels depend on:
    - Distance from transmitter
    - Transmission power
    - Path loss
    - Interference
    
    Args:
        frequency: The center frequency in MHz
        
    Returns:
        Received power in dBm
    """
    # Base power level with distance/path loss variation
    base_power = random.uniform(-85.0, -45.0)
    
    # Add noise and fading
    noise = random.gauss(0, 3.0)  # 3dB standard deviation
    
    # Occasional strong signals (close transmitters)
    if random.random() < 0.05:  # 5% chance
        base_power = random.uniform(-40.0, -30.0)
    
    # Occasional very weak signals (distant transmitters)
    if random.random() < 0.1:  # 10% chance
        base_power = random.uniform(-95.0, -85.0)
    
    final_power = base_power + noise
    return max(POWER_MIN, min(POWER_MAX, final_power))


def get_sensor_config() -> dict:
    """
    Get current sensor configuration parameters.
    
    Returns:
        Dictionary containing configuration parameters
    """
    return {
        'freq_min': FREQ_MIN,
        'freq_max': FREQ_MAX,
        'power_min': POWER_MIN,
        'power_max': POWER_MAX,
        'bandwidth_min': BANDWIDTH_MIN,
        'bandwidth_max': BANDWIDTH_MAX,
        'wifi_channels': WIFI_CHANNELS,
        'bluetooth_base': BLUETOOTH_BASE
    }


def validate_sensor_data(data: List[SensorData]) -> bool:
    """
    Validate that sensor data meets expected constraints.
    
    Args:
        data: List of sensor data tuples
        
    Returns:
        True if data is valid, False otherwise
    """
    if not data:
        return False
    
    for timestamp, frequency, bandwidth, power in data:
        # Check timestamp is reasonable
        if not isinstance(timestamp, (int, float)) or timestamp <= 0:
            return False
        
        # Check frequency is in valid range
        if not (FREQ_MIN <= frequency <= FREQ_MAX):
            return False
        
        # Check bandwidth is positive and reasonable
        if not (BANDWIDTH_MIN <= bandwidth <= BANDWIDTH_MAX):
            return False
        
        # Check power is in valid range
        if not (POWER_MIN <= power <= POWER_MAX):
            return False
    
    return True