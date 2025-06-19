"""UI component tests using NiceGUI testing framework."""

from unittest.mock import Mock, patch

import pytest

from src.app.desktop_app import DesktopApp


def test_modal_dialog_creation():
    """Test that modal dialog methods create proper UI components."""
    with patch('src.app.desktop_app.ui.dialog') as mock_dialog, \
         patch('src.app.desktop_app.ui.card'), \
         patch('src.app.desktop_app.ui.row'), \
         patch('src.app.desktop_app.ui.label'), \
         patch('src.app.desktop_app.ui.space'), \
         patch('src.app.desktop_app.ui.button'), \
         patch('src.app.desktop_app.ui.switch'), \
         patch('src.app.desktop_app.ui.separator'):

        app = DesktopApp()

        # Mock the dialog with method chaining and context manager support
        mock_dialog_instance = Mock()
        mock_dialog_with_props = Mock()

        # Set up the chaining: ui.dialog().props("persistent")
        mock_dialog.return_value.props.return_value = mock_dialog_with_props

        # Set up context manager protocol
        mock_dialog_with_props.__enter__ = Mock(return_value=mock_dialog_instance)
        mock_dialog_with_props.__exit__ = Mock(return_value=None)

        # Test config dialog creation
        app.show_config_dialog()

        # Verify dialog was created and opened immediately
        mock_dialog.assert_called_once()
        mock_dialog_instance.open.assert_called_once()


def test_about_dialog_creation():
    """Test that about dialog method creates proper UI components."""
    with patch('src.app.desktop_app.ui.dialog') as mock_dialog, \
         patch('src.app.desktop_app.ui.card'), \
         patch('src.app.desktop_app.ui.row'), \
         patch('src.app.desktop_app.ui.label'), \
         patch('src.app.desktop_app.ui.space'), \
         patch('src.app.desktop_app.ui.button'), \
         patch('src.app.desktop_app.ui.separator'), \
         patch('src.app.desktop_app.ui.column'):

        app = DesktopApp()

        # Mock the dialog with method chaining and context manager support
        mock_dialog_instance = Mock()
        mock_dialog_with_props = Mock()

        # Set up the chaining: ui.dialog().props("persistent")
        mock_dialog.return_value.props.return_value = mock_dialog_with_props

        # Set up context manager protocol
        mock_dialog_with_props.__enter__ = Mock(return_value=mock_dialog_instance)
        mock_dialog_with_props.__exit__ = Mock(return_value=None)

        # Test about dialog creation
        app.show_about_dialog()

        # Verify dialog was created and opened immediately
        mock_dialog.assert_called_once()
        mock_dialog_instance.open.assert_called_once()


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


def test_dialog_methods_exist_and_callable():
    """Test that dialog methods exist and can be called without timing mechanisms."""
    app = DesktopApp()

    # Test that both dialog methods exist and can be called
    with patch('src.app.desktop_app.ui.dialog'):
        # Should not raise any exceptions
        app.show_config_dialog()
        app.show_about_dialog()

    # Test log actions are called for dialogs
    with patch.object(app, 'log_action') as mock_log:
        with patch('src.app.desktop_app.ui.dialog'):
            app.show_config_dialog()
            mock_log.assert_called_with("Config Dialog", "Opened configuration dialog")

            app.show_about_dialog()
            mock_log.assert_called_with("About Dialog", "Opened about dialog")


def test_modal_dialogs_open_immediately():
    """Test that modal dialogs open immediately without timer delays."""
    app = DesktopApp()

    # Mock log_action to verify behavior
    with patch.object(app, 'log_action') as mock_log:
        with patch('src.app.desktop_app.ui.dialog'):
            # Call both dialog methods
            app.show_config_dialog()
            app.show_about_dialog()

            # Verify both methods were logged (indicating they executed)
            assert mock_log.call_count == 2
            mock_log.assert_any_call("Config Dialog", "Opened configuration dialog")
            mock_log.assert_any_call("About Dialog", "Opened about dialog")


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
    with patch('src.app.desktop_app.ui.dialog'):
        # Should not raise any exceptions
        app.show_config_dialog()
        app.show_about_dialog()

    # Test log actions are called for dialogs
    with patch.object(app, 'log_action') as mock_log:
        with patch('src.app.desktop_app.ui.dialog'):
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
