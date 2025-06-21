"""Basic unit tests for desktop application functionality."""

from unittest.mock import Mock, patch

import pytest

from src.app import root_page
from src.app.app import App


@pytest.mark.unit
def test_app_initialization():
    """Test that App initializes correctly."""
    app = App()

    # Check that app instance exists
    assert app is not None

    # Check initial state of root_page variables
    assert root_page.dark_mode is False
    assert root_page.public_ip_label is None


@pytest.mark.unit
def test_port_checking():
    """Test port availability checking functionality."""
    app = App()

    # Test that is_port_free works for obviously free/used ports
    # Note: We can't test specific ports reliably in CI, but we can test the method exists
    assert hasattr(app, 'is_port_free')
    assert hasattr(app, 'find_free_port')

    # Test that find_free_port returns an integer
    with patch.object(app, 'is_port_free', return_value=True):
        port = app.find_free_port(start_port=8000, max_attempts=1)
        assert isinstance(port, int)
        assert port == 8000


@pytest.mark.unit
def test_port_finding_failure():
    """Test that find_free_port raises error when no ports available."""
    app = App()

    # Mock all ports as unavailable
    with patch.object(app, 'is_port_free', return_value=False):
        with pytest.raises(RuntimeError, match="No free port found"):
            app.find_free_port(start_port=8000, max_attempts=3)


@pytest.mark.unit
def test_log_action():
    """Test that log_action prints correctly formatted messages."""
    app = App()

    # Mock print to capture output
    with patch('builtins.print') as mock_print:
        app.log_action("Test Action", "Test details")

        # Verify print was called
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]

        # Check log format
        assert "UI Action: Test Action" in call_args
        assert "Test details" in call_args
        assert "[" in call_args  # Should have timestamp


@pytest.mark.unit
def test_theme_toggle():
    """Test theme toggle functionality."""
    app = App()

    # Initial state should be light mode
    assert root_page.dark_mode is False

    # Mock the UI query to avoid actual DOM manipulation
    with patch('src.app.root_page.ui.query') as mock_query:
        mock_element = Mock()
        mock_query.return_value = mock_element

        # Toggle to dark mode
        root_page.toggle_theme()
        assert root_page.dark_mode is True

        # Verify UI updates were called
        assert mock_query.called

        # Toggle back to light mode
        root_page.toggle_theme()
        assert root_page.dark_mode is False


@pytest.mark.unit
def test_get_public_ip_success():
    """Test successful public IP retrieval."""
    app = App()

    # Mock the public IP label
    mock_label = Mock()
    root_page.public_ip_label = mock_label

    # Mock requests
    with patch('src.app.root_page.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "192.168.1.1"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        root_page.get_public_ip()

        # Verify the label was updated with success
        assert "Public IP: 192.168.1.1" in mock_label.text
        mock_label.style.assert_called_with("color: #4caf50")


@pytest.mark.unit
def test_get_public_ip_timeout():
    """Test public IP retrieval timeout handling."""
    app = App()

    # Mock the public IP label
    mock_label = Mock()
    root_page.public_ip_label = mock_label

    # Mock requests to raise timeout
    with patch('src.app.root_page.requests.get') as mock_get:
        mock_get.side_effect = Exception("timeout")

        root_page.get_public_ip()

        # Verify error handling (updated for new error message format)
        assert "error" in mock_label.text.lower()
        mock_label.style.assert_called_with("color: #d32f2f")


@pytest.mark.unit
def test_setup_shutdown_handler():
    """Test that shutdown handler is properly configured."""
    with patch('src.app.app.app') as mock_app:
        App()

        # Verify that on_shutdown was called
        mock_app.on_shutdown.assert_called_once()


@pytest.mark.unit
def test_modal_dialog_methods_exist():
    """Test that modal dialog methods exist and are callable."""
    app = App()

    # Check that dialog methods exist in root_page module
    assert hasattr(root_page, 'show_config_dialog')
    assert hasattr(root_page, 'show_about_dialog')
    assert callable(root_page.show_config_dialog)
    assert callable(root_page.show_about_dialog)


@pytest.mark.unit
def test_quit_application_method():
    """Test that quit application method exists and is callable."""
    app = App()

    # Check that quit method exists in root_page module
    assert hasattr(root_page, 'quit_application')
    assert callable(root_page.quit_application)

    # Test that quit method calls app.shutdown
    with patch('src.app.root_page.app') as mock_app:
        root_page.quit_application()
        mock_app.shutdown.assert_called_once()


@pytest.mark.unit  
def test_plots_use_valid_selectdirection():
    """Regression test: ensure plots use valid selectdirection values."""
    from src.data_generator import generate_sensor_data
    from src.plotting import create_frequency_bandwidth_plot, create_scanner_plot
    
    # This should not raise a selectdirection ValueError
    data = generate_sensor_data(5)
    freq_plot = create_frequency_bandwidth_plot(data)
    scanner_plot = create_scanner_plot(data)
    
    # Verify they use valid selectdirection (the bug was using 'diagonal' instead of 'd')
    assert freq_plot.layout.selectdirection == 'd'
    assert scanner_plot.layout.selectdirection == 'd'


@pytest.mark.unit
def test_direct_plot_data_assignment():
    """Test that plots support direct data assignment for updates."""
    from src.data_generator import generate_sensor_data
    from src.plotting import create_frequency_bandwidth_plot, create_scanner_plot
    
    # Create initial plots
    initial_data = generate_sensor_data(5)
    freq_plot = create_frequency_bandwidth_plot(initial_data)
    scanner_plot = create_scanner_plot(initial_data)
    
    # Verify initial data
    assert len(freq_plot.data[0].x) == 5
    assert len(scanner_plot.data[0].x) == 5
    
    # Generate new data for direct assignment
    new_data = generate_sensor_data(10)
    frequencies = [freq for _, freq, _, _ in new_data]
    bandwidths = [bw for _, _, bw, _ in new_data]
    powers = [pwr for _, _, _, pwr in new_data]
    
    # Test direct assignment on frequency vs bandwidth plot
    freq_plot.data[0].x = frequencies
    freq_plot.data[0].y = bandwidths
    freq_plot.data[0].marker.color = powers
    
    # Verify update
    assert len(freq_plot.data[0].x) == 10
    assert len(freq_plot.data[0].y) == 10
    assert len(freq_plot.data[0].marker.color) == 10
    
    # Test direct assignment on scanner plot
    scanner_plot.data[0].x = frequencies
    scanner_plot.data[0].y = powers
    scanner_plot.data[0].marker.color = bandwidths
    scanner_plot.data[0].marker.size = [max(4, min(15, bw/4)) for bw in bandwidths]
    
    # Verify update
    assert len(scanner_plot.data[0].x) == 10
    assert len(scanner_plot.data[0].y) == 10
    assert len(scanner_plot.data[0].marker.color) == 10
    assert len(scanner_plot.data[0].marker.size) == 10
    
    # Test clearing with direct assignment
    freq_plot.data[0].x = []
    freq_plot.data[0].y = []
    freq_plot.data[0].marker.color = []
    
    assert len(freq_plot.data[0].x) == 0
    assert len(freq_plot.data[0].y) == 0
    assert len(freq_plot.data[0].marker.color) == 0


@pytest.mark.unit
def test_app_browser_mode_initialization():
    """Test that App can be initialized in browser mode."""
    app_native = App(browser_mode=False)
    app_browser = App(browser_mode=True)
    
    # Check that browser mode is properly set
    assert app_native.browser_mode is False
    assert app_browser.browser_mode is True
    
    # Check that both apps initialize correctly
    assert app_native is not None
    assert app_browser is not None


@pytest.mark.unit
def test_data_size_calculation():
    """Test data size calculation function."""
    from src.app.root_page import calculate_data_size
    
    # Test known values
    # Each packet = 32 bytes (4 floats * 8 bytes each)
    # 1 KB = 1024 bytes
    
    # 1 packet = 32 bytes = 32/1024 KB
    assert abs(calculate_data_size(1) - (32/1024)) < 0.001
    
    # 10 packets = 320 bytes = 320/1024 KB
    assert abs(calculate_data_size(10) - (320/1024)) < 0.001
    
    # 1000 packets = 32000 bytes = 32000/1024 KB
    assert abs(calculate_data_size(1000) - (32000/1024)) < 0.001
    
    # Test zero packets
    assert calculate_data_size(0) == 0.0


@pytest.mark.unit  
def test_update_rate_slider_range():
    """Test that update rate slider has correct range."""
    # Import the module to check default values
    from src.app import root_page
    
    # Test default update rate
    assert root_page.update_rate == 1.0
    
    # Test that update rate is within expected range
    assert 0.1 <= root_page.update_rate <= 5.0


@pytest.mark.unit
def test_efficient_plot_update_functions():
    """Test the efficient plot update functions."""
    from src.app.root_page import efficient_update_plot_data, efficient_clear_plot_data
    from src.data_generator import generate_sensor_data
    from src.plotting import create_frequency_bandwidth_plot
    from unittest.mock import Mock
    
    # Create a mock plot element
    mock_plot = Mock()
    mock_trace = Mock()
    mock_trace.marker = Mock()
    mock_plot.figure.data = [mock_trace]
    
    # Test efficient update with valid data
    test_data = generate_sensor_data(5)
    frequencies = [freq for _, freq, _, _ in test_data]
    bandwidths = [bw for _, _, bw, _ in test_data]
    powers = [pwr for _, _, _, pwr in test_data]
    
    # Call efficient update
    efficient_update_plot_data(
        mock_plot,
        trace_index=0,
        x_data=frequencies,
        y_data=bandwidths,
        colors=powers
    )
    
    # Verify the mock was called correctly
    assert mock_trace.x == frequencies
    assert mock_trace.y == bandwidths
    assert mock_trace.marker.color == powers
    mock_plot.update.assert_called_once()
    
    # Test efficient clear
    mock_plot.reset_mock()
    mock_trace.reset_mock()
    
    efficient_clear_plot_data(mock_plot, trace_index=0)
    
    # Verify clear was called correctly
    assert mock_trace.x == []
    assert mock_trace.y == []
    assert mock_trace.marker.color == []
    assert mock_trace.selectedpoints is None
    mock_plot.update.assert_called_once()


@pytest.mark.unit
def test_efficient_update_with_none_plot():
    """Test efficient update functions handle None plot elements gracefully."""
    from src.app.root_page import efficient_update_plot_data, efficient_clear_plot_data
    
    # These should not raise exceptions
    efficient_update_plot_data(None, 0, [1, 2, 3], [4, 5, 6])
    efficient_clear_plot_data(None, 0)
    
    # Test with plot element that has no figure attribute
    mock_plot_no_figure = Mock()
    del mock_plot_no_figure.figure
    
    efficient_update_plot_data(mock_plot_no_figure, 0, [1, 2, 3], [4, 5, 6])
    efficient_clear_plot_data(mock_plot_no_figure, 0)
