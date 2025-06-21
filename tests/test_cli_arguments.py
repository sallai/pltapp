#!/usr/bin/env python3
"""
Tests for command line argument parsing functionality.
"""

import sys
import os
import subprocess
import pytest

# Add the project root to the Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import parse_arguments


class TestCLIArguments:
    """Test command line argument parsing."""
    
    def test_default_arguments(self, monkeypatch):
        """Test default behavior (no arguments)."""
        # Simulate no command line arguments
        monkeypatch.setattr(sys, 'argv', ['main.py'])
        
        args = parse_arguments()
        
        # Default should be native mode (browser=False)
        assert args.browser is False
    
    def test_browser_argument(self, monkeypatch):
        """Test --browser argument."""
        # Simulate --browser argument
        monkeypatch.setattr(sys, 'argv', ['main.py', '--browser'])
        
        args = parse_arguments()
        
        # Should enable browser mode
        assert args.browser is True
    
    def test_pyinstaller_detection(self):
        """Test PyInstaller bundle detection."""
        from main import is_pyinstaller_bundle
        
        # Should return False when running normally
        assert is_pyinstaller_bundle() is False
    
    def test_pyinstaller_argument_filtering(self):
        """Test filtering of PyInstaller-specific arguments."""
        from main import filter_pyinstaller_args
        
        # Test with PyInstaller arguments
        pyinstaller_args = [
            '--multiprocessing-fork', 'tracker_fd=8', 'pipe_handle=18',
            '-OO', '-B', '-S', '-I', '-c',
            'from multiprocessing.resource_tracker import main;main(7)'
        ]
        
        filtered = filter_pyinstaller_args(pyinstaller_args)
        
        # All PyInstaller arguments should be filtered out
        assert len(filtered) == 0
        
        # Test with mixed arguments
        mixed_args = ['--browser'] + pyinstaller_args + ['--help']
        filtered_mixed = filter_pyinstaller_args(mixed_args)
        
        # Only valid arguments should remain
        assert '--browser' in filtered_mixed
        assert '--help' in filtered_mixed
        assert len(filtered_mixed) == 2
    
    def test_pyinstaller_environment_simulation(self, monkeypatch):
        """Test argument parsing in simulated PyInstaller environment."""
        # Simulate PyInstaller environment by patching the detection function
        from main import is_pyinstaller_bundle
        monkeypatch.setattr('main.is_pyinstaller_bundle', lambda: True)
        monkeypatch.setattr(sys, 'argv', ['main.exe', '--multiprocessing-fork', 'tracker_fd=8'])
        
        args = parse_arguments()
        
        # Should default to native mode in PyInstaller
        assert args.browser is False
    
    def test_help_argument_via_subprocess(self):
        """Test --help argument via subprocess."""
        # Use subprocess to test --help since it calls sys.exit()
        result = subprocess.run(
            [sys.executable, 'main.py', '--help'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        # Help should exit with code 0
        assert result.returncode == 0
        
        # Should contain help text
        assert '2.4GHz Sensor Visualization Application' in result.stdout
        assert '--browser' in result.stdout
        assert 'Run the application in browser mode' in result.stdout
        assert 'Examples:' in result.stdout
    
    def test_version_argument_via_subprocess(self):
        """Test --version argument via subprocess."""
        # Use subprocess to test --version since it calls sys.exit()
        result = subprocess.run(
            [sys.executable, 'main.py', '--version'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        # Version should exit with code 0
        assert result.returncode == 0
        
        # Should contain version information
        assert '2.4GHz Sensor Visualization v1.0.0' in result.stdout
    
    def test_invalid_argument_via_subprocess(self):
        """Test invalid argument via subprocess."""
        # Use subprocess to test invalid argument
        result = subprocess.run(
            [sys.executable, 'main.py', '--invalid'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        
        # Invalid argument should exit with error code
        assert result.returncode != 0
        
        # Should contain error message
        assert 'unrecognized arguments' in result.stderr or 'invalid' in result.stderr.lower()


class TestApplicationModes:
    """Test application initialization with different modes."""
    
    def test_native_mode_initialization(self):
        """Test that native mode App initializes correctly."""
        from src.app.app import App
        
        app = App(browser_mode=False)
        
        assert app.browser_mode is False
        assert hasattr(app, 'setup_pages')
        assert hasattr(app, 'run')
    
    def test_browser_mode_initialization(self):
        """Test that browser mode App initializes correctly."""
        from src.app.app import App
        
        app = App(browser_mode=True)
        
        assert app.browser_mode is True
        assert hasattr(app, 'setup_pages')
        assert hasattr(app, 'run')


if __name__ == "__main__":
    # Run the tests when executed directly
    pytest.main([__file__, "-v"])