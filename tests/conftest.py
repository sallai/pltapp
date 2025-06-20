"""Test configuration and fixtures."""

import pytest

from src.app import root_page
from src.app.app import App


@pytest.fixture(scope="function")
def app():
    """Create a test application instance."""
    # Reset root_page module variables to initial state
    root_page.dark_mode = False
    root_page.public_ip_label = None
    root_page.about_dialog = None
    root_page.config_dialog = None

    # Create and setup the app
    test_app = App()

    yield test_app

    # Reset root_page module variables after test
    root_page.dark_mode = False
    root_page.public_ip_label = None
    root_page.about_dialog = None
    root_page.config_dialog = None
