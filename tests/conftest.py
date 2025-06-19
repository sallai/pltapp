"""Test configuration and fixtures."""

import pytest
from nicegui import ui

from src.app.desktop_app import DesktopApp


@pytest.fixture(scope="function")
def app():
    """Create a test application instance."""
    # Clear any existing UI state
    ui.clear()

    # Create and setup the app
    test_app = DesktopApp()

    yield test_app

    # Cleanup after test
    ui.clear()
