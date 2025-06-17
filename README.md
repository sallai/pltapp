# WW - NiceGUI Desktop Application with Platform Abstraction

**Advanced cross-platform desktop application demonstrating NiceGUI web UI in native windows with pluggable platform abstraction layer.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform Support](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)](#platform-support)
[![UI Toolkits](https://img.shields.io/badge/toolkits-PySide6%20%7C%20PyQt6%20%7C%20WebKit%20%7C%20GTK-green.svg)](#supported-toolkits)
[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](#production-readiness)

## 🚀 Quick Start

```bash
# Clone and setup
git clone git@github.com:sallai/ww.git
cd ww
python scripts/setup_dev.py

# Run with auto-detection (recommended)
python main.py

# Run with specific toolkit
python main.py pyside6        # Qt (recommended)
python main.py macos_webkit   # Native macOS WebKit
python main.py pyqt6         # Alternative Qt (separate env required)
python main.py gtk           # Linux GTK
```

## ✨ Features

### 🎯 Production-Ready Stability
- **✅ Zero Segmentation Faults**: Enhanced Qt WebEngine cleanup eliminates crashes
- **✅ Cross-Platform**: Runs natively on macOS, Windows, and Linux
- **✅ Robust Error Handling**: Comprehensive fallback mechanisms and resource management

### 🔧 Platform Abstraction
- **Multiple UI Toolkits**: PySide6, PyQt6, native macOS WebKit, GTK
- **Auto-Detection**: Intelligent toolkit selection based on platform and availability
- **Unified API**: Same application code works across all platforms
- **Native Integration**: Platform-specific optimizations and behaviors

### 🎨 Modern UI
- **NiceGUI Integration**: Full web-based UI with modern design
- **Interactive Components**: Text processing, validation, real-time feedback
- **Professional Styling**: Custom CSS with gradients and animations
- **Responsive Design**: Works well at different screen sizes

### 🛠️ Developer Experience
- **Automated Setup**: One-command development environment setup
- **Code Quality Tools**: Ruff, Black, MyPy, Bandit, pytest
- **Build Automation**: PyInstaller with platform detection
- **Comprehensive Documentation**: Clear setup and usage instructions

## 📋 Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Windows, or Linux
- **Memory**: Minimum 512MB RAM
- **Storage**: ~200MB for full development environment

## 🛠️ Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone git@github.com:sallai/ww.git
cd ww

# Setup development environment (PySide6)
python scripts/setup_dev.py

# Activate environment and run
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
python main.py
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Option 3: Alternative Toolkit (PyQt6)

```bash
# Setup PyQt6 environment (separate from PySide6)
python scripts/setup_dev.py pyqt6

# Note: PyQt6 and PySide6 cannot coexist in same environment
```

## 🖥️ Platform Support

### Supported Toolkits

| Platform | Primary | Secondary | Native |
|----------|---------|-----------|--------|
| **macOS** | PySide6 ✅ | PyQt6 ⚠️ | WebKit ✅ |
| **Windows** | PyQt6 ✅ | PySide6 ✅ | - |
| **Linux** | GTK ✅ | PySide6 ✅ | PyQt6 ⚠️ |

**Legend:**
- ✅ Production Ready
- ⚠️ Requires separate environment or additional setup

### Auto-Detection Priority

The application automatically selects the best available toolkit:

- **macOS**: `macos_webkit` → `pyside6` → `pyqt6`
- **Windows**: `pyqt6` → `pyside6`
- **Linux**: `gtk` → `pyside6` → `pyqt6`

## 🎛️ Usage

### Basic Usage

```bash
# Auto-detect best toolkit (recommended)
python main.py

# Check available toolkits on your system
python -c "from platforms import get_available_toolkits; import pprint; pprint.pprint(get_available_toolkits())"
```

### Toolkit-Specific Usage

```bash
# PySide6 (recommended for production)
python main.py pyside6

# Native macOS WebKit (minimal dependencies)
python main.py macos_webkit

# PyQt6 (alternative Qt, requires separate environment)
python main.py pyqt6

# GTK (Linux native)
python main.py gtk
```

### Development Commands

```bash
# Code quality checks
ruff check .          # Fast Python linting
black --check .       # Code formatting check  
mypy .               # Type checking
bandit -r .          # Security scanning

# Testing
pytest tests/        # Run test suite

# Build executable
python scripts/build.py

# Clean build artifacts
python scripts/clean.py
```

## 🏗️ Architecture

### Platform Abstraction Layer

The application features a sophisticated platform abstraction system:

```
Application Layer (main.py)
    ↓
Platform Factory (platforms/factory.py)
    ↓
Window Manager Interface (platforms/base.py)
    ↓
Platform Implementations:
├── PySide6Manager (Qt WebEngine)
├── PyQt6Manager (Qt WebEngine) 
├── MacOSWebKitManager (Native WebKit)
└── GTKManager (WebKit2GTK)
```

### Key Components

- **Unified Interface**: `WindowManagerInterface` provides consistent API
- **Intelligent Detection**: Factory pattern with platform-specific preferences
- **Graceful Fallbacks**: Automatic toolkit selection if preferred option unavailable
- **Resource Management**: Enhanced cleanup preventing memory leaks and crashes

## 🔧 Technical Achievements

### ✅ Segmentation Fault Resolution

**Problem**: Qt WebEngine caused segmentation faults during shutdown on macOS.

**Solution**: Enhanced cleanup sequence with proper event processing:

```python
def cleanup_web_view(self, web_view):
    # 1. Stop active loading
    web_view.stop()
    
    # 2. Load blank page to reset state
    web_view.setUrl(QUrl("about:blank"))
    
    # 3. Process events with critical timing
    app.processEvents()
    time.sleep(0.1)  # Allows WebEngine internal cleanup
    app.processEvents()
```

**Result**: ✅ Zero segmentation faults in production

### ✅ Qt Toolkit Conflict Resolution

**Problem**: PyQt6 and PySide6 cannot coexist due to Qt library symbol conflicts.

**Solution**: Separate requirement files and environment management:
- `requirements/pyside6.txt` - Default production environment
- `requirements/pyqt6.txt` - Alternative environment for specific use cases

### ✅ Native Platform Integration

**Innovation**: Direct macOS WebKit integration using PyObjC, bypassing Qt entirely for minimal dependencies and native platform integration.

## 📂 Project Structure

```
ww/
├── platforms/                    # Platform abstraction layer
│   ├── base.py                  # Abstract interface
│   ├── factory.py               # Auto-detection and creation
│   ├── pyside6_manager.py       # PySide6 (enhanced, production-ready)
│   ├── pyqt6_manager.py         # PyQt6 (alternative)
│   ├── macos_webkit_manager.py  # Native macOS WebKit
│   └── gtk_manager.py           # Linux GTK
├── requirements/                 # Organized dependency management
│   ├── base.txt                 # Default (points to pyside6.txt)
│   ├── pyside6.txt              # PySide6 environment
│   ├── pyqt6.txt                # PyQt6 environment (separate)
│   ├── base_qt_common.txt       # Common dependencies
│   ├── dev.txt                  # Development tools
│   └── test.txt                 # Testing framework
├── scripts/                      # Development automation
│   ├── setup_dev.py             # Environment setup with toolkit choice
│   ├── build.py                 # PyInstaller build automation
│   └── clean.py                 # Cleanup script
├── config/                       # Configuration
│   ├── settings.json            # Runtime settings
│   ├── logging.conf             # Logging configuration
│   └── build.yaml              # Build configuration
├── main.py                      # Main application with platform abstraction
├── pyproject.toml              # Tool configurations
├── CLAUDE.md                   # Development guidance
└── docs/                       # Documentation
    ├── IMPLEMENTATION_STATUS.md
    ├── PLATFORM_ARCHITECTURE.md
    └── SHUTDOWN_ANALYSIS.md
```

## 🚀 Production Readiness

### ✅ Stable for Production

- **PySide6**: Enhanced with segfault-free shutdown, recommended
- **Platform Abstraction**: Robust auto-detection with comprehensive error handling
- **Build System**: Automated PyInstaller with platform detection
- **Code Quality**: Comprehensive linting, formatting, type checking, security scanning

### 🎯 Deployment Recommendations

| Use Case | Recommended Stack | Notes |
|----------|------------------|-------|
| **Production** | PySide6 | Enhanced, segfault-free, cross-platform |
| **macOS Native** | macOS WebKit | Minimal dependencies, App Store compatible |
| **Windows** | PyQt6 or PySide6 | PyQt6 preferred, both work well |
| **Linux** | GTK + PySide6 fallback | Native integration preferred |

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone
git clone git@github.com:yourusername/ww.git
cd ww

# Setup development environment
python scripts/setup_dev.py

# Run code quality checks
ruff check .
black --check .
mypy .
bandit -r .

# Run tests
pytest tests/
```

### Code Standards

- **Formatting**: Black (88 character line length)
- **Linting**: Ruff (comprehensive rule set)
- **Type Checking**: MyPy (strict mode)
- **Security**: Bandit scanning
- **Testing**: pytest with coverage

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **NiceGUI**: Web-based Python UI framework
- **Qt Project**: Cross-platform UI toolkit (PySide6/PyQt6)
- **Apple**: macOS WebKit framework
- **GNOME**: GTK toolkit for Linux
- **PyInstaller**: Python application packaging

---

**Built with ❤️ using Python and modern UI technologies**