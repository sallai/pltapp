"""UI component tests using NiceGUI testing framework."""

from unittest.mock import patch

import pytest

from src.app.desktop_app import DesktopApp


def test_modal_dialog_creation():
    """Test that modal dialog methods create proper UI components."""
    with patch('src.app.desktop_app.ui.timer') as mock_timer:
        app = DesktopApp()

        # Test config dialog creation
        app.show_config_dialog()

        # Verify timer was called for delayed dialog creation
        mock_timer.assert_called_once()
        args, kwargs = mock_timer.call_args
        assert args[0] == 0.1  # 0.1 second delay
        assert kwargs.get('once') is True

        # Verify the callback function exists
        callback = args[1]
        assert callable(callback)


def test_about_dialog_creation():
    """Test that about dialog method creates proper UI components."""
    with patch('src.app.desktop_app.ui.timer') as mock_timer:
        app = DesktopApp()

        # Test about dialog creation
        app.show_about_dialog()

        # Verify timer was called for delayed dialog creation
        mock_timer.assert_called_once()
        args, kwargs = mock_timer.call_args
        assert args[0] == 0.1  # 0.1 second delay
        assert kwargs.get('once') is True

        # Verify the callback function exists
        callback = args[1]
        assert callable(callback)


def test_ui_pages_setup():
    """Test that setup_pages method configures the UI properly."""
    app = DesktopApp()

    # Mock UI components to track what gets created
    with patch('src.app.desktop_app.ui.page') as mock_page:
        # setup_pages is called in __init__, so we need to call it again
        # to test with our mocked components
        app.setup_pages()

        # Verify a page decorator was used
        mock_page.assert_called_with("/")


def test_modal_dialog_timing_mechanism():
    """Test that the timing mechanism works correctly for modal dialogs."""
    app = DesktopApp()

    with patch('src.app.desktop_app.ui.timer') as mock_timer:
        # Call show_config_dialog
        app.show_config_dialog()

        # Verify timer was called with correct parameters
        mock_timer.assert_called_once()
        args, kwargs = mock_timer.call_args

        # Check timing parameters
        assert args[0] == 0.1  # 0.1 second delay
        assert kwargs.get('once') is True

        # Verify the callback function exists and is callable
        callback_function = args[1]
        assert callable(callback_function)

        # We can't easily test the full dialog creation without complex mocking
        # but we've verified the timing mechanism is set up correctly


def test_public_ip_label_initialization():
    """Test that public IP label is properly initialized."""
    app = DesktopApp()

    # Initially should be None
    assert app.public_ip_label is None

    # After setup_pages, it should be set (though we can't easily test the full setup)
    # This test verifies the attribute exists and starts as None


def test_clock_label_initialization():
    """Test that clock label is properly initialized."""
    app = DesktopApp()

    # Initially should be None
    assert app.clock_label is None

    # After setup_pages, it should be set (though we can't easily test the full setup)
    # This test verifies the attribute exists and starts as None


@pytest.mark.integration
def test_hamburger_menu_dialog_integration():
    """Integration test for hamburger menu modal dialog functionality."""
    # This would be a full integration test that requires browser automation
    # For now, we'll test the basic integration without actual UI rendering

    app = DesktopApp()

    # Test that both dialog methods exist and can be called
    with patch('src.app.desktop_app.ui.timer'):
        # Should not raise any exceptions
        app.show_config_dialog()
        app.show_about_dialog()

    # Test log actions are called for dialogs
    with patch.object(app, 'log_action') as mock_log:
        with patch('src.app.desktop_app.ui.timer'):
            app.show_config_dialog()
            mock_log.assert_called_with("Config Dialog", "Opened configuration dialog")

            app.show_about_dialog()
            mock_log.assert_called_with("About Dialog", "Opened about dialog")


def test_ui_component_existence():
    """Test that expected UI components are properly structured."""
    # This test verifies the basic structure without full rendering
    app = DesktopApp()

    # Check that the app has the expected attributes for UI components
    assert hasattr(app, 'dark_mode')
    assert hasattr(app, 'clock_label')
    assert hasattr(app, 'public_ip_label')
    assert hasattr(app, 'setup_pages')
    assert hasattr(app, 'show_config_dialog')
    assert hasattr(app, 'show_about_dialog')

    # Test initial states
    assert app.dark_mode is False
    assert app.clock_label is None
    assert app.public_ip_label is None
