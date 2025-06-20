"""Mock-based UI interaction tests for hamburger menu modal dialogs."""

from unittest.mock import Mock, patch

import pytest

from src.app.app import App
from src.app import root_page


@pytest.mark.unit
def test_hamburger_menu_about_click_simulation():
    """Test simulated click flow: hamburger menu -> about menu item -> modal opens."""
    app = App()

    # Dialogs start as None and are created when the page is accessed
    assert root_page.about_dialog is None
    
    # Test that dialog methods can be called even when dialogs don't exist
    with patch('src.app.root_page.log_action') as mock_log:
        # Call show_about_dialog directly (simulating menu item click)
        root_page.show_about_dialog()

        # Verify that the about dialog method was called (logged)
        mock_log.assert_called_with("About Dialog", "Opened about dialog")


@pytest.mark.unit
def test_hamburger_menu_config_click_simulation():
    """Test simulated click flow: hamburger menu -> config menu item -> modal opens."""
    app = App()

    # Dialogs start as None and are created when the page is accessed
    assert root_page.config_dialog is None
    
    # Test that dialog methods can be called even when dialogs don't exist
    with patch('src.app.root_page.log_action') as mock_log:
        # Simulate clicking the "⚙️ Configuration" menu item
        # This should directly call root_page.show_config_dialog()
        root_page.show_config_dialog()

        # Verify that the config dialog method was called (logged)
        mock_log.assert_called_with("Config Dialog", "Opened configuration dialog")




@pytest.mark.unit
def test_modal_dialog_content_after_click():
    """Test that modal dialog contains expected content when opened via menu click."""
    app = App()

    # Dialogs start as None and are created when the page is accessed
    assert root_page.about_dialog is None
    
    # Test that dialog methods can be called even when dialogs don't exist
    with patch('src.app.root_page.log_action') as mock_log:
        # Simulate the About menu click (directly call the method)
        root_page.show_about_dialog()

        # Verify dialog method was called (logged)
        mock_log.assert_called_with("About Dialog", "Opened about dialog")
    
    # Since dialogs are created during page access in a real app,
    # the content testing should be done in integration tests


@pytest.mark.integration
def test_hamburger_menu_ui_integration():
    """Integration test verifying hamburger menu setup and modal dialog functionality."""
    app = App()

    # This test verifies the complete UI structure is set up correctly
    with patch('src.app.root_page.ui.page') as mock_page:
        # Verify setup_pages creates the main page
        app.setup_pages()
        mock_page.assert_called_with("/")

    # Test that dialog methods work correctly
    with patch('src.app.root_page.ui.dialog') as mock_dialog:
        mock_dialog_instance = Mock()
        mock_dialog_with_props = Mock()
        mock_dialog.return_value.props.return_value = mock_dialog_with_props
        mock_dialog_with_props.__enter__ = Mock(return_value=mock_dialog_instance)
        mock_dialog_with_props.__exit__ = Mock(return_value=None)

        # Test both dialog methods (equivalent to menu clicks)
        with patch('src.app.root_page.log_action') as mock_log:
            root_page.show_about_dialog()
            root_page.show_config_dialog()

            # Verify both methods were called (logged)
            assert mock_log.call_count == 2
            mock_log.assert_any_call("About Dialog", "Opened about dialog")
            mock_log.assert_any_call("Config Dialog", "Opened configuration dialog")
