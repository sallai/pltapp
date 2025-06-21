#!/usr/bin/env python3
"""
Regression test for selectdirection bug.

This test ensures that the plot layout configuration uses valid Plotly
selectdirection values and prevents the ValueError that occurred when
'diagonal' was used instead of 'd'.

Bug: ValueError: Invalid value of type 'builtins.str' received for the 
'selectdirection' property of layout. Received value: 'diagonal'

Valid values are: ['h', 'v', 'd', 'any']
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from data_generator import generate_sensor_data
from plotting import create_frequency_bandwidth_plot, create_scanner_plot
import plotly.graph_objects as go


class TestSelectDirectionRegression:
    """Regression tests for the selectdirection configuration bug."""
    
    def test_frequency_bandwidth_plot_selectdirection_valid(self):
        """Test that frequency vs bandwidth plot uses valid selectdirection value."""
        # Generate test data
        data = generate_sensor_data(10)
        
        # Create the plot - this should not raise a ValueError
        fig = create_frequency_bandwidth_plot(data)
        
        # Verify the plot was created successfully
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        # Check that selectdirection is set to a valid value
        layout = fig.layout
        assert hasattr(layout, 'selectdirection')
        assert layout.selectdirection in ['h', 'v', 'd', 'any']
        
        # Verify it's specifically set to 'd' (diagonal)
        assert layout.selectdirection == 'd'
    
    def test_scanner_plot_selectdirection_valid(self):
        """Test that scanner plot uses valid selectdirection value."""
        # Generate test data
        data = generate_sensor_data(10)
        
        # Create the plot - this should not raise a ValueError
        fig = create_scanner_plot(data)
        
        # Verify the plot was created successfully
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
        # Check that selectdirection is set to a valid value
        layout = fig.layout
        assert hasattr(layout, 'selectdirection')
        assert layout.selectdirection in ['h', 'v', 'd', 'any']
        
        # Verify it's specifically set to 'd' (diagonal)
        assert layout.selectdirection == 'd'
    
    def test_empty_plots_selectdirection_valid(self):
        """Test that empty plots also use valid selectdirection value."""
        # Test with empty data
        empty_freq_bw = create_frequency_bandwidth_plot([])
        empty_scanner = create_scanner_plot([])
        
        # Both should be valid figures
        assert isinstance(empty_freq_bw, go.Figure)
        assert isinstance(empty_scanner, go.Figure)
        
        # Both should have valid selectdirection
        assert empty_freq_bw.layout.selectdirection == 'd'
        assert empty_scanner.layout.selectdirection == 'd'
    
    def test_selectdirection_invalid_value_regression(self):
        """Test that demonstrates the original bug would fail."""
        # This test verifies that the invalid value 'diagonal' would indeed cause an error
        
        # Create a minimal test figure with the invalid value
        fig = go.Figure()
        
        # This should raise a ValueError containing both 'selectdirection' and 'diagonal'
        with pytest.raises(ValueError) as exc_info:
            fig.update_layout(selectdirection='diagonal')
        
        error_message = str(exc_info.value)
        assert 'selectdirection' in error_message
        assert 'diagonal' in error_message
        assert "Invalid value" in error_message
    
    def test_all_valid_selectdirection_values(self):
        """Test that all valid selectdirection values work."""
        valid_values = ['h', 'v', 'd', 'any']
        
        for value in valid_values:
            fig = go.Figure()
            # This should not raise any exception
            fig.update_layout(selectdirection=value)
            assert fig.layout.selectdirection == value
    
    def test_plot_configuration_consistency(self):
        """Test that both plots have consistent selection configuration."""
        data = generate_sensor_data(5)
        
        freq_bw_plot = create_frequency_bandwidth_plot(data)
        scanner_plot = create_scanner_plot(data)
        
        # Both plots should have the same selection configuration
        assert freq_bw_plot.layout.dragmode == 'select'
        assert scanner_plot.layout.dragmode == 'select'
        
        assert freq_bw_plot.layout.selectdirection == 'd'
        assert scanner_plot.layout.selectdirection == 'd'
        
        # Both should have the selection mode enabled
        assert freq_bw_plot.layout.dragmode in ['select', 'lasso']
        assert scanner_plot.layout.dragmode in ['select', 'lasso']


class TestPlotlyLayoutValidation:
    """Additional tests for Plotly layout validation."""
    
    def test_plotly_selectdirection_enumeration(self):
        """Test Plotly's selectdirection enumeration values."""
        # Test all documented valid values
        valid_selectdirection_values = ['h', 'v', 'd', 'any']
        
        for value in valid_selectdirection_values:
            fig = go.Figure()
            fig.update_layout(selectdirection=value)
            assert fig.layout.selectdirection == value
    
    def test_plotly_selectdirection_invalid_values(self):
        """Test that invalid selectdirection values raise appropriate errors."""
        invalid_values = ['diagonal', 'horizontal', 'vertical', 'diag', 'all', '']
        
        for invalid_value in invalid_values:
            fig = go.Figure()
            with pytest.raises(ValueError, match="Invalid value.*selectdirection"):
                fig.update_layout(selectdirection=invalid_value)


def test_application_startup_no_selectdirection_error():
    """Integration test: ensure application startup doesn't fail with selectdirection error."""
    # This test simulates the application startup sequence that was failing
    
    # Generate initial data (as done in _setup_plots_section)
    initial_data = generate_sensor_data(10)
    
    # Create plots (this was where the error occurred)
    try:
        freq_bw_plot = create_frequency_bandwidth_plot(initial_data)
        scanner_plot = create_scanner_plot(initial_data)
        
        # If we get here, the bug is fixed
        assert isinstance(freq_bw_plot, go.Figure)
        assert isinstance(scanner_plot, go.Figure)
        
    except ValueError as e:
        if "selectdirection" in str(e) and "diagonal" in str(e):
            pytest.fail(f"Selectdirection regression detected: {e}")
        else:
            # Re-raise if it's a different ValueError
            raise


if __name__ == "__main__":
    # Run the tests when executed directly
    pytest.main([__file__, "-v"])