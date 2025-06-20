"""Selenium-based UI tests for hamburger menu and modal dialogs."""

import pytest

from src.app.app import App


@pytest.mark.ui
def test_hamburger_menu_about_dialog_selenium(screen):
    """Test hamburger menu -> about dialog flow using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Click the hamburger menu button
    screen.click('button[aria-label="menu"]')

    # Wait for menu to open
    screen.wait(0.5)

    # Click the "About" menu item
    screen.click('text="ℹ️ About"')

    # Wait for dialog to open
    screen.wait(0.5)

    # Verify the about dialog content is displayed
    screen.should_contain('NiceGUI Desktop Demo')
    screen.should_contain('Version 1.0.0')
    screen.should_contain('Built with:')
    screen.should_contain('NiceGUI - Modern Python UI framework')

    # Close the dialog
    screen.click('button:has(i:contains("close"))')

    # Wait for dialog to close
    screen.wait(0.5)


@pytest.mark.ui
def test_hamburger_menu_config_dialog_selenium(screen):
    """Test hamburger menu -> config dialog flow using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Click the hamburger menu button
    screen.click('button[aria-label="menu"]')

    # Wait for menu to open
    screen.wait(0.5)

    # Click the "Configuration" menu item
    screen.click('text="⚙️ Configuration"')

    # Wait for dialog to open
    screen.wait(0.5)

    # Verify the config dialog content is displayed
    screen.should_contain('Configuration')
    screen.should_contain('Theme:')
    screen.should_contain('Dark Mode')

    # Test theme toggle
    screen.click('input[type="checkbox"]')
    screen.wait(0.5)

    # Click reset button
    screen.click('text="Reset to Default"')
    screen.wait(0.5)

    # Close the dialog
    screen.click('text="Close"')

    # Wait for dialog to close
    screen.wait(0.5)


@pytest.mark.ui
def test_text_processing_functionality_selenium(screen):
    """Test text processing functionality using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Find the text input field
    screen.click('input[placeholder="Enter some text here..."]')

    # Type some text
    test_text = "Hello NiceGUI!"
    screen.type(test_text)

    # Click the "Process Text" button
    screen.click('text="Process Text"')

    # Wait for processing
    screen.wait(0.5)

    # Verify the result appears
    screen.should_contain(f"You typed: '{test_text}'")
    screen.should_contain(f"Length: {len(test_text)} chars")

    # Test clear functionality
    screen.click('text="Clear"')
    screen.wait(0.5)

    # Verify text is cleared
    screen.should_contain("Result will appear here")


@pytest.mark.ui
def test_counter_functionality_selenium(screen):
    """Test counter functionality using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Test increment
    screen.click('text="+ Increment"')
    screen.wait(0.5)
    screen.should_contain('Count: 1')

    # Test increment again
    screen.click('text="+ Increment"')
    screen.wait(0.5)
    screen.should_contain('Count: 2')

    # Test decrement
    screen.click('text="- Decrement"')
    screen.wait(0.5)
    screen.should_contain('Count: 1')

    # Test reset
    screen.click('text="Reset"')
    screen.wait(0.5)
    screen.should_contain('Count: 0')


@pytest.mark.ui
def test_network_functionality_selenium(screen):
    """Test network functionality using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Click the "Get Public IP" button
    screen.click('text="🔍 Get Public IP"')

    # Wait for network request (timeout after 15 seconds)
    screen.wait(2)

    # The result should either show an IP address or an error
    # We can't predict the exact outcome, but something should change
    try:
        screen.should_contain('Public IP:')
    except:
        # If no IP found, should show some error or fetching state
        try:
            screen.should_contain('Error:')
        except:
            screen.should_contain('Fetching IP...')

    # Test clear functionality
    screen.click('button:contains("Clear")')
    screen.wait(0.5)
    screen.should_contain('Click button to fetch IP address')


@pytest.mark.ui
def test_quit_menu_selenium(screen):
    """Test quit menu item using selenium screen fixture."""
    app = App()

    # Navigate to the main page
    screen.open('/')

    # Wait for page to load
    screen.wait(1)

    # Click the hamburger menu button
    screen.click('button[aria-label="menu"]')

    # Wait for menu to open
    screen.wait(0.5)

    # Verify quit menu item exists (but don't click it as it would stop the app)
    screen.should_contain('🚪 Quit')


@pytest.mark.ui
def test_complete_user_journey_selenium(screen):
    """Test complete user journey: menu navigation -> dialog interaction -> functionality testing."""
    app = App()

    # Navigate to the main page
    screen.open('/')
    screen.wait(1)

    # 1. Test hamburger menu navigation to about dialog
    screen.click('button[aria-label="menu"]')
    screen.wait(0.5)
    screen.click('text="ℹ️ About"')
    screen.wait(0.5)
    screen.should_contain('NiceGUI Desktop Demo')
    screen.click('button:has(i:contains("close"))')
    screen.wait(0.5)

    # 2. Test configuration dialog
    screen.click('button[aria-label="menu"]')
    screen.wait(0.5)
    screen.click('text="⚙️ Configuration"')
    screen.wait(0.5)
    screen.should_contain('Theme:')
    screen.click('text="Close"')
    screen.wait(0.5)

    # 3. Test text processing
    screen.click('input[placeholder="Enter some text here..."]')
    screen.type('Integration test')
    screen.click('text="Process Text"')
    screen.wait(0.5)
    screen.should_contain('You typed: \'Integration test\'')

    # 4. Test counter
    screen.click('text="+ Increment"')
    screen.wait(0.5)
    screen.should_contain('Count: 1')

    # 5. Test quit menu availability (but don't click it)
    screen.click('button[aria-label="menu"]')
    screen.wait(0.5)
    screen.should_contain('🚪 Quit')

    # Complete journey successful
