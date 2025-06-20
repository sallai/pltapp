# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a technology demonstration showing a NiceGUI UI application with a couple of UI controls in a native window, packaged into a native executable using PyInstaller. The project is kept as simple as possible, focusing on easy comprehensibility by humans, with proper inline documentation and markers indicating where additional functionality would be added should the developer want to turn this into a full-blown project.

## Current Project Status

**Status**: Foundation Complete - Ready for Core Implementation
- ✅ Development environment and tooling configured
- ✅ Project structure established with automation scripts
- ✅ Dependencies defined and virtual environment ready
- ❌ Main application implementation pending (main.py commented out)
- ❌ NiceGUI native mode integration needed
- ❌ PyInstaller packaging validation required

## 3-Stage Development Plan

### Stage 1: Core Application Implementation
**Goal**: Get basic NiceGUI application running with UI components

#### Tasks:
1. **Activate Main Application** (`nicegui_desktop_app.py:1-54`)
   - Uncomment and implement the basic NiceGUI UI
   - Add text input, button, and result display components
   - Implement text processing functionality
   - Add shutdown capability

2. **Test Development Mode**
   - Run application in development: `python nicegui_desktop_app.py`
   - Verify UI components work correctly
   - Test input/output functionality
   - Validate shutdown mechanism

3. **Code Quality Validation**
   - Run linting: `ruff check .`
   - Run formatting: `black --check .`
   - Run type checking: `mypy .`
   - Fix any issues found

#### Deliverables:
- Working NiceGUI application in development mode
- All code quality checks passing
- Basic UI functionality verified

### Stage 2: Native Integration & Packaging
**Goal**: Integrate native window mode and create distributable executable

#### Tasks:
1. **NiceGUI Native Mode Setup**
   - Research NiceGUI native mode implementation
   - Implement chosen native window solution
   - Test native window functionality
   - Ensure proper window management

2. **PyInstaller Configuration**
   - Update build script (`scripts/build_executable.py`)
   - Configure .spec file for native dependencies
   - Handle NiceGUI static assets bundling
   - Test executable creation process

3. **Build Validation**
   - Create executable: `python scripts/build_executable.py`
   - Test executable functionality
   - Verify all dependencies included
   - Test on clean system (if possible)

#### Deliverables:
- Standalone executable that runs without Python installation
- Native window integration working
- Build process documented and automated

### Stage 3: Polish & Distribution
**Goal**: Finalize packaging, testing, and documentation

#### Tasks:
1. **Cross-Platform Testing**
   - Test on target platforms (macOS/Windows/Linux)
   - Validate executable behavior consistency
   - Handle platform-specific issues
   - Optimize executable size if needed

2. **Error Handling & Robustness**
   - Add proper exception handling
   - Implement graceful degradation
   - Add logging for debugging
   - Test edge cases and error scenarios

3. **Documentation & Cleanup**
   - Update IMPLEMENTATION_STATUS.md with final state
   - Clean up build artifacts: `python scripts/cleanup_artifacts.py`
   - Document any platform-specific requirements
   - Create distribution notes

#### Deliverables:
- Production-ready executable
- Complete documentation
- Validated cross-platform compatibility
- Clean, maintainable codebase

## Implementation Notes

### Key Decision Points:
- **NiceGUI Native Mode**: Use `ui.run(native=True)` for desktop windows
- **Asset Bundling**: Ensure NiceGUI static files included in PyInstaller build
- **Window Management**: Proper shutdown and window lifecycle handling

### Critical Success Factors:
- Main application must work in both development and packaged modes
- Executable must be truly standalone (no external dependencies)
- UI must be responsive and professional
- Build process must be repeatable and automated

## Tech Stack

- **NiceGUI**: Web-based Python UI framework
- **NiceGUI Native Mode**: Built-in desktop window functionality
- **PyInstaller**: Packages Python applications into standalone executables

## Quick Start Commands

Basic commands for this project:

```bash
# Automated development environment setup
python scripts/setup_development_environment.py

# Manual setup (alternative)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt

# Run the application in development
python nicegui_desktop_app.py

# Build executable with PyInstaller
python scripts/build_executable.py
```

## Architecture

The application follows a simple architecture pattern:
- NiceGUI handles the web UI components and server
- NiceGUI native mode creates a desktop window container
- PyInstaller bundles everything into a distributable executable

## Development Guidelines

### Code Style and Standards

#### Python Code Style
- **PEP 8**: Follow Python Enhancement Proposal 8 for code formatting
- **Type Hints**: Use type annotations for all function parameters and return values
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Import Organization**: Use isort with Black-compatible settings

#### Naming Conventions
- **Classes**: PascalCase 
- **Functions/Methods**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private Members**: Leading underscore
- **UI Elements**: Descriptive names with type suffix

### Error Handling
- **Errors**: Display user-friendly error messages in the display
- **Input Validation**: Prevent invalid operations before they occur
- **Logging**: Use Python's logging module for debugging and error tracking
- **Exception Handling**: Catch and handle UI related exceptions gracefully

### Testing Strategy
- **Unit Tests**: pytest for individual component testing
- **Integration Tests**: Test operations end-to-end
- **UI Tests**: Automated testing of user interactions
- **Coverage Target**: Minimum 80% code coverage
- **Continuous Integration**: Automated testing on all target platforms

## Project Tooling

### Development Environment
- **Python Version**: 3.11+ (for better performance and typing features)
- **Virtual Environment**: Use venv for dependency isolation (created automatically by setup script)
- **IDE Configuration**: VS Code settings provided for consistent development
- **Configuration Management**: pyproject.toml for tool configurations and project metadata
- **Settings**: JSON-based configuration files in config/ directory

### Dependency Management
- **Base Dependencies**: requirements/base.txt (production dependencies)
- **Development Dependencies**: requirements/dev.txt (includes code quality tools and testing)
- **Test Dependencies**: requirements/test.txt (testing framework and utilities)
- **Main Requirements**: requirements.txt (symlinked to base.txt for compatibility)
- **Reproducible Builds**: pip-tools available for dependency locking

### Code Quality Tools
- **Formatter**: Black (88 character line length) - configured in pyproject.toml
- **Linter**: Ruff (fast Python linter with extensive rule set) - configured in pyproject.toml
- **Type Checker**: MyPy (strict mode enabled) - configured in pyproject.toml
- **Import Sorter**: isort (Black-compatible profile) - configured in pyproject.toml
- **Security Scanner**: Bandit for security vulnerability detection - configured in pyproject.toml

### Testing Framework
- **Test Runner**: pytest with coverage reporting
- **Coverage**: pytest-cov for test coverage analysis
- **Mocking**: pytest-mock for test mocking capabilities
- **Configuration**: pytest settings in pyproject.toml

### Build and Packaging
- **Build Scripts**: Automated build script in scripts/build.py
- **Packaging**: PyInstaller for creating standalone executables
- **Build Configuration**: YAML-based build configuration in config/build.yaml
- **Cross-Platform Building**: Support for Windows, macOS, and Linux builds
- **Distribution**: Platform-specific executable generation

### Development Scripts
- **Setup Script**: scripts/setup_development_environment.py - automated development environment setup
- **Build Script**: scripts/build_executable.py - PyInstaller executable creation
- **Cleanup Script**: scripts/cleanup_artifacts.py - removes build artifacts and cache files
- **All scripts**: Made executable and include proper error handling

### Extended Development Commands
Quick setup and common development tasks:
```bash
# Automated development environment setup
python scripts/setup_development_environment.py

# Manual setup (alternative)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/dev.txt

# Code quality checks (run from project root)
ruff check .
black --check .
mypy .
bandit -r .

# Code formatting
black .
isort .

# Testing with coverage
pytest tests/ --cov=. --cov-report=html
pytest tests/ --cov=. --cov-report=term-missing

# Build application
python scripts/build_executable.py

# Clean build artifacts and cache
python scripts/cleanup_artifacts.py

# Run application (current simple structure)
python nicegui_desktop_app.py
```

### Pre-commit Hooks
Pre-commit framework installed and ready for configuration:
- Black formatting
- Ruff linting  
- MyPy type checking
- Tests on changed files
- Bandit security scanning

### Configuration Files
- **pyproject.toml**: Central configuration for all tools and project metadata
- **config/settings.json**: Application runtime settings
- **config/logging.conf**: Logging configuration
- **config/build.yaml**: Build process configuration

## Project Structure

### Current Simple Structure
For the technology demonstration, the minimal structure is:
```
ww/
├── nicegui_desktop_app.py           # Entry point and application setup
├── pyproject.toml                   # Project configuration and dependencies
├── requirements/                    # Split dependency management
│   ├── base.txt                    # Production dependencies
│   ├── dev.txt                     # Development dependencies
│   └── test.txt                    # Testing dependencies
├── scripts/                         # Development automation
│   ├── setup_development_environment.py  # Dev env setup
│   ├── build_executable.py              # PyInstaller build
│   └── cleanup_artifacts.py             # Cleanup script
├── CLAUDE.md                       # This file - Claude Code guidance
├── IMPLEMENTATION_PLAN.md          # Project roadmap
├── IMPLEMENTATION_STATUS.md        # Current status tracking
└── *.spec                          # PyInstaller configuration (when generated)
```

### Proposed Extended Structure
If expanding into a full project, the recommended structure would be:

```
ww/
├── src/                    # Source code directory
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── ui/                # UI components and layouts
│   │   ├── __init__.py
│   │   ├── components/    # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── buttons.py
│   │   │   ├── forms.py
│   │   │   └── dialogs.py
│   │   ├── pages/         # Main application pages/views
│   │   │   ├── __init__.py
│   │   │   ├── main_page.py
│   │   │   └── settings_page.py
│   │   └── styles/        # CSS and styling
│   │       ├── main.css
│   │       └── themes.css
│   ├── core/              # Core application logic
│   │   ├── __init__.py
│   │   ├── app.py         # Main application class
│   │   ├── config.py      # Configuration management
│   │   └── events.py      # Event handling
│   ├── services/          # Business logic and services
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── file_service.py
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_ui/
│   │   ├── __init__.py
│   │   └── test_components.py
│   ├── test_core/
│   │   ├── __init__.py
│   │   └── test_app.py
│   └── fixtures/          # Test data and fixtures
│       └── sample_data.json
├── assets/                 # Static assets
│   ├── icons/
│   │   ├── app.ico
│   │   └── app.png
│   ├── images/
│   └── fonts/
├── scripts/                # Build and utility scripts
│   ├── build.py           # PyInstaller build script
│   ├── setup_dev.py       # Development environment setup
│   └── clean.py           # Cleanup script
├── requirements/           # Dependency management
│   ├── base.txt           # Base dependencies
│   ├── dev.txt            # Development dependencies
│   └── test.txt           # Testing dependencies
├── config/                 # Configuration files
│   ├── settings.json      # Application settings
│   ├── logging.conf       # Logging configuration
│   └── build.yaml         # Build configuration
├── docs/                   # Documentation (only if needed)
│   ├── api.md
│   └── deployment.md
├── .github/                # GitHub workflows (if using GitHub)
│   └── workflows/
│       ├── ci.yml
│       └── build.yml
├── dist/                   # Built executables (generated)
├── build/                  # Build artifacts (generated)
├── .gitignore             # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pyproject.toml         # Project metadata and tool configuration
├── requirements.txt       # Main dependencies (symlink to requirements/base.txt)
├── CLAUDE.md              # This file - Claude Code guidance
└── README.md              # Project documentation (only if requested)
```

### Directory Guidelines

- **src/**: All source code lives here for better organization
- **ui/**: Separate UI concerns from business logic
- **core/**: Central application logic and configuration
- **services/**: Business logic and data handling
- **utils/**: Reusable utility functions
- **tests/**: Mirror the src/ structure for test organization
- **assets/**: Static files like icons, images, fonts
- **scripts/**: Automation and build scripts
- **requirements/**: Split dependencies by environment
- **config/**: External configuration files
- **Generated directories**: dist/, build/, __pycache__/ should be in .gitignore

## Project Management Files

### IMPLEMENTATION_PLAN.md
Contains the detailed implementation plan broken down into phases with actionable tasks. This file serves as the project roadmap.

### IMPLEMENTATION_STATUS.md
**CRITICAL**: When executing tasks from IMPLEMENTATION_PLAN.md, ALWAYS update this file after completing tasks. This file must contain:
- Current project status and progress
- Completed tasks with timestamps
- Architectural decisions made during implementation
- Tooling choices and rationale
- Current directory structure
- Dependencies installed and versions
- Any deviations from the original plan
- Next steps and current blockers
- Configuration decisions and settings

## important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
ALWAYS prefer simple solutions.
IF a NiceGUI UI container (like a ui.dialog, ui.card, or ui.row) needs to appear and disappear, THEN you must instantiate it during the initial page load.
NEVER write container creation like "with ui.dialog()" or "my_card = ui.card()" inside an on_click handler.
When working with NiceGUI ALWAYS use event handlers to call methods like .open(), .close(), or .set_visibility() on component references that were created outside the handler.