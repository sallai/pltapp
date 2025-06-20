"""Pytest configuration and fixtures for NiceGUI testing."""

import pytest
from nicegui.testing import Screen

from src.app.app import App


@pytest.fixture
def screen(caplog, selenium):
    """NiceGUI screen fixture for UI testing."""
    # Create the app instance
    app = App()

    # Create and return the screen fixture
    screen = Screen(selenium, "/", caplog=caplog)
    return screen
