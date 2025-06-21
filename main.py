#!/usr/bin/env python3
"""
NiceGUI Desktop Application Entry Point

Minimal entry point that imports and runs the main application.
"""

import argparse
import sys
from src.app import App


def is_pyinstaller_bundle() -> bool:
    """Check if we're running in a PyInstaller bundle."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def filter_pyinstaller_args(args: list) -> list:
    """Filter out PyInstaller-specific arguments."""
    filtered_args = []
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        # Skip PyInstaller multiprocessing arguments
        if (arg.startswith('--multiprocessing-fork') or 
            arg.startswith('-OO') or 
            arg.startswith('-B') or 
            arg.startswith('-S') or 
            arg.startswith('-I') or
            'multiprocessing.resource_tracker' in arg or
            'tracker_fd=' in arg or
            'pipe_handle=' in arg):
            continue
            
        # Skip Python flags that PyInstaller might pass
        if arg in ['-c']:
            skip_next = True  # Skip the next argument too (the command)
            continue
            
        filtered_args.append(arg)
    
    return filtered_args


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="2.4GHz Sensor Visualization Application",
        prog="sensor-app",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                # Run in native desktop window (default)
  python main.py --browser      # Run in browser mode
  python main.py --help         # Show this help message

The application visualizes simulated 2.4GHz band sensor data including
WiFi and Bluetooth signals in real-time interactive plots.
        """
    )
    
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Run the application in browser mode instead of native desktop window"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="2.4GHz Sensor Visualization v1.0.0"
    )
    
    # If running in PyInstaller bundle, filter out PyInstaller-specific arguments
    if is_pyinstaller_bundle():
        # In PyInstaller, just use defaults (native mode)
        return argparse.Namespace(browser=False)
    else:
        # Filter command line arguments to remove PyInstaller artifacts
        filtered_argv = filter_pyinstaller_args(sys.argv[1:])
        return parser.parse_args(filtered_argv)


def main() -> None:
    """Application entry point."""
    args = parse_arguments()
    
    # Create and run the application with specified mode
    app = App(browser_mode=args.browser)
    app.run()


if __name__ == "__main__":
    main()
