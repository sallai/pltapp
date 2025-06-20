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
