"""Basic unit tests for desktop application functionality."""

from unittest.mock import Mock, patch

import pytest

from src.app.desktop_app import DesktopApp


def test_desktop_app_initialization():
    """Test that DesktopApp initializes correctly."""
    app = DesktopApp()

    # Check initial state
    assert app.dark_mode is False
    assert app.clock_label is None
    assert app.clock_task is None
    assert app.public_ip_label is None


def test_port_checking():
    """Test port availability checking functionality."""
    app = DesktopApp()

    # Test that is_port_free works for obviously free/used ports
    # Note: We can't test specific ports reliably in CI, but we can test the method exists
    assert hasattr(app, 'is_port_free')
    assert hasattr(app, 'find_free_port')

    # Test that find_free_port returns an integer
    with patch.object(app, 'is_port_free', return_value=True):
        port = app.find_free_port(start_port=8000, max_attempts=1)
        assert isinstance(port, int)
        assert port == 8000


def test_port_finding_failure():
    """Test that find_free_port raises error when no ports available."""
    app = DesktopApp()

    # Mock all ports as unavailable
    with patch.object(app, 'is_port_free', return_value=False):
        with pytest.raises(RuntimeError, match="No free port found"):
            app.find_free_port(start_port=8000, max_attempts=3)


def test_log_action():
    """Test that log_action prints correctly formatted messages."""
    app = DesktopApp()

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


def test_theme_toggle():
    """Test theme toggle functionality."""
    app = DesktopApp()

    # Initial state should be light mode
    assert app.dark_mode is False

    # Mock the UI query to avoid actual DOM manipulation
    with patch('src.app.desktop_app.ui.query') as mock_query:
        mock_element = Mock()
        mock_query.return_value = mock_element

        # Toggle to dark mode
        app.toggle_theme()
        assert app.dark_mode is True

        # Verify UI updates were called
        assert mock_query.called

        # Toggle back to light mode
        app.toggle_theme()
        assert app.dark_mode is False


@pytest.mark.asyncio
async def test_get_public_ip_success():
    """Test successful public IP retrieval."""
    app = DesktopApp()

    # Mock the public IP label
    mock_label = Mock()
    app.public_ip_label = mock_label

    # Mock httpx client
    with patch('src.app.desktop_app.httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.text = "192.168.1.1"
        mock_response.raise_for_status.return_value = None

        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await app.get_public_ip()

        # Verify the label was updated with success
        assert "Public IP: 192.168.1.1" in mock_label.text
        mock_label.style.assert_called_with("color: #4caf50")


@pytest.mark.asyncio
async def test_get_public_ip_timeout():
    """Test public IP retrieval timeout handling."""
    app = DesktopApp()

    # Mock the public IP label
    mock_label = Mock()
    app.public_ip_label = mock_label

    # Mock httpx client to raise timeout
    with patch('src.app.desktop_app.httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("timeout")

        await app.get_public_ip()

        # Verify error handling
        assert "Error:" in mock_label.text
        mock_label.style.assert_called_with("color: #d32f2f")


def test_setup_shutdown_handler():
    """Test that shutdown handler is properly configured."""
    with patch('src.app.desktop_app.app') as mock_app:
        DesktopApp()

        # Verify that on_shutdown was called
        mock_app.on_shutdown.assert_called_once()


def test_modal_dialog_methods_exist():
    """Test that modal dialog methods exist and are callable."""
    app = DesktopApp()

    # Check that dialog methods exist
    assert hasattr(app, 'show_config_dialog')
    assert hasattr(app, 'show_about_dialog')
    assert callable(app.show_config_dialog)
    assert callable(app.show_about_dialog)
