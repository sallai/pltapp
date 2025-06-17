#!/usr/bin/env python3
"""Enhanced build script for creating standalone executable with platform abstraction support."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

def get_platform_info():
    """Get current platform information."""
    system = platform.system()
    machine = platform.machine()
    return {
        'system': system,
        'machine': machine,
        'platform_name': f"{system.lower()}_{machine.lower()}"
    }

def clean_build_dirs():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__', '*.spec']
    
    for pattern in dirs_to_clean:
        if pattern.endswith('.spec'):
            # Remove spec files
            for spec_file in Path('.').glob('*.spec'):
                spec_file.unlink()
                print(f"Removed {spec_file}")
        else:
            # Remove directories
            if os.path.exists(pattern):
                shutil.rmtree(pattern)
                print(f"Cleaned {pattern}/")

def detect_available_toolkits():
    """Detect which UI toolkits are available for inclusion."""
    available = []
    
    try:
        import PySide6
        available.append('pyside6')
        print("✓ PySide6 detected")
    except ImportError:
        print("✗ PySide6 not available")
    
    try:
        import PyQt6
        available.append('pyqt6')
        print("✓ PyQt6 detected")
    except ImportError:
        print("✗ PyQt6 not available")
    
    current_platform = platform.system()
    if current_platform == 'Darwin':
        try:
            import objc
            import Foundation
            import AppKit
            import WebKit
            available.append('macos_webkit')
            print("✓ macOS WebKit frameworks detected")
        except ImportError:
            print("✗ macOS WebKit frameworks not available")
    
    if current_platform == 'Linux':
        try:
            import gi
            available.append('gtk')
            print("✓ GTK detected")
        except ImportError:
            print("✗ GTK not available")
    
    return available

def create_pyinstaller_spec(toolkit: Optional[str] = None):
    """Create enhanced PyInstaller spec file for platform abstraction."""
    platform_info = get_platform_info()
    available_toolkits = detect_available_toolkits()
    
    # Determine target toolkit
    if toolkit and toolkit in available_toolkits:
        target_toolkit = toolkit
    elif available_toolkits:
        # Use auto-detection logic
        if platform_info['system'] == 'Darwin':
            target_toolkit = next((t for t in ['macos_webkit', 'pyside6', 'pyqt6'] if t in available_toolkits), available_toolkits[0])
        elif platform_info['system'] == 'Windows':
            target_toolkit = next((t for t in ['pyqt6', 'pyside6'] if t in available_toolkits), available_toolkits[0])
        else:  # Linux
            target_toolkit = next((t for t in ['gtk', 'pyside6', 'pyqt6'] if t in available_toolkits), available_toolkits[0])
    else:
        raise RuntimeError("No UI toolkits available for packaging")
    
    print(f"Target toolkit for packaging: {target_toolkit}")
    
    # Build hidden imports based on target toolkit only
    hidden_imports = [
        'platforms',
        'platforms.base',
        'platforms.factory',
    ]
    
    # Only include the target toolkit to avoid Qt conflicts
    if target_toolkit == 'pyside6':
        hidden_imports.extend([
            'platforms.pyside6_manager',
            'PySide6.QtCore',
            'PySide6.QtWidgets', 
            'PySide6.QtWebEngineWidgets',
            'PySide6.QtWebEngineCore',
        ])
    elif target_toolkit == 'pyqt6':
        hidden_imports.extend([
            'platforms.pyqt6_manager',
            'PyQt6.QtCore',
            'PyQt6.QtWidgets',
            'PyQt6.QtWebEngineWidgets',
        ])
    elif target_toolkit == 'macos_webkit':
        hidden_imports.extend([
            'platforms.macos_webkit_manager',
            'objc',
            'Foundation',
            'AppKit',
            'WebKit',
        ])
    elif target_toolkit == 'gtk':
        hidden_imports.extend([
            'platforms.gtk_manager',
            'gi',
            'gi.repository.Gtk',
            'gi.repository.WebKit2',
        ])
    
    # NiceGUI and web dependencies
    hidden_imports.extend([
        'nicegui',
        'fastapi',
        'uvicorn',
        'starlette',
        'jinja2',
    ])
    
    return {
        'target_toolkit': target_toolkit,
        'hidden_imports': hidden_imports,
        'platform_info': platform_info
    }

def build_executable(toolkit: Optional[str] = None, debug: bool = False):
    """Build the executable using PyInstaller with enhanced configuration."""
    spec_info = create_pyinstaller_spec(toolkit)
    platform_info = spec_info['platform_info']
    
    # Base PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', f"ww_{platform_info['platform_name']}",
        '--clean',
    ]
    
    # Add hidden imports
    for import_name in spec_info['hidden_imports']:
        cmd.extend(['--hidden-import', import_name])
    
    # Add data files (config directory)
    cmd.extend(['--add-data', 'config:config'])
    
    # Add NiceGUI static assets
    import nicegui
    nicegui_path = nicegui.__file__.replace('__init__.py', '')
    static_path = f"{nicegui_path}static"
    templates_path = f"{nicegui_path}templates"
    
    if os.path.exists(static_path):
        cmd.extend(['--add-data', f'{static_path}:nicegui/static'])
    if os.path.exists(templates_path):
        cmd.extend(['--add-data', f'{templates_path}:nicegui/templates'])
    
    # Platform-specific configurations
    if platform_info['system'] == 'Darwin':
        # macOS specific
        cmd.extend([
            '--target-arch', platform_info['machine'],
            '--osx-bundle-identifier', 'com.sallai.ww'
        ])
    elif platform_info['system'] == 'Windows':
        # Windows specific
        cmd.extend([
            '--disable-windowed-traceback'
        ])
    
    # Debug mode
    if debug:
        cmd.extend(['--debug=all', '--console'])
        cmd.remove('--windowed')  # Remove windowed for debug
    
    # Exclude unnecessary modules to reduce size
    exclusions = [
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        '_tkinter',
    ]
    
    # Exclude conflicting Qt toolkits
    if spec_info['target_toolkit'] != 'pyside6':
        exclusions.extend(['PySide6', 'shiboken6'])
    if spec_info['target_toolkit'] != 'pyqt6':
        exclusions.extend(['PyQt6', 'PyQt6.sip'])
    
    for exclusion in exclusions:
        cmd.extend(['--exclude-module', exclusion])
    
    # Add main script
    cmd.append('main.py')
    
    print(f"PyInstaller command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        executable_name = f"ww_{platform_info['platform_name']}"
        if platform_info['system'] == 'Windows':
            executable_name += '.exe'
        
        print("✅ Build completed successfully!")
        print(f"📦 Executable: dist/{executable_name}")
        print(f"🔧 Target toolkit: {spec_info['target_toolkit']}")
        print(f"💻 Platform: {platform_info['system']} ({platform_info['machine']})")
        
        return f"dist/{executable_name}"
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def test_executable(executable_path: str):
    """Test the built executable."""
    if not os.path.exists(executable_path):
        print(f"❌ Executable not found: {executable_path}")
        return False
    
    print(f"🧪 Testing executable: {executable_path}")
    
    # Get file size
    size_mb = os.path.getsize(executable_path) / (1024 * 1024)
    print(f"📏 Size: {size_mb:.1f} MB")
    
    # Test execution (brief)
    print("⚡ Running quick test (will timeout after 5 seconds)...")
    try:
        # Run with timeout to avoid hanging
        result = subprocess.run(
            [executable_path, '--help'], 
            timeout=5, 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            print("✅ Executable runs successfully")
        else:
            print(f"⚠️ Executable exit code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out (expected for GUI application)")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """Main build process with enhanced options."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build WW application executable')
    parser.add_argument('--toolkit', choices=['pyside6', 'pyqt6', 'macos_webkit', 'gtk'],
                       help='Force specific UI toolkit')
    parser.add_argument('--debug', action='store_true',
                       help='Build in debug mode with console')
    parser.add_argument('--test', action='store_true', default=True,
                       help='Test executable after build (default: True)')
    parser.add_argument('--clean-only', action='store_true',
                       help='Only clean build directories')
    
    args = parser.parse_args()
    
    if args.clean_only:
        print("🧹 Cleaning build directories...")
        clean_build_dirs()
        print("✅ Cleanup completed")
        return
    
    print("🚀 Starting enhanced build process...")
    print(f"Platform: {platform.system()} ({platform.machine()})")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    clean_build_dirs()
    
    # Detect available toolkits
    print("🔍 Detecting available UI toolkits...")
    available = detect_available_toolkits()
    if not available:
        print("❌ No UI toolkits available!")
        sys.exit(1)
    
    # Build executable
    executable_path = build_executable(args.toolkit, args.debug)
    
    # Test executable
    if args.test and not args.debug:
        test_executable(executable_path)
    
    print("🎉 Build process completed!")

if __name__ == '__main__':
    main()