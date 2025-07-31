# Development Guide

## Overview

This guide covers development setup, architecture, and contribution guidelines for LDAP Control Panel.

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry
- Git
- LDAP server for testing

### Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd ldap-idp

# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell

# Install pre-commit hooks
poetry run pre-commit install
```

### Development Tools

```bash
# Run with development tools
poetry run textual dev ldap_idp.main

# Run tests
poetry run pytest

# Format code
poetry run black ldap_idp/
poetry run isort ldap_idp/

# Type checking
poetry run mypy ldap_idp/
```

## Project Structure

```
ldap-idp/
├── ldap_idp/                    # Main package
│   ├── main.py                  # Application entry point
│   ├── serve.py                 # Web server
│   ├── config.py                # Configuration management
│   ├── settings.yaml            # Default settings
│   ├── ldap_backend.py          # LDAP connection handling
│   ├── subapps/                 # Application modules
│   │   ├── browser/             # Browser application
│   │   └── viewer/              # Viewer application
│   └── lib_textual/             # Shared UI components
├── docs/                        # Documentation
├── tests/                       # Test suite
├── pyproject.toml               # Project configuration
└── README.md                    # Project overview
```

## Architecture

### Core Components

#### Application Framework

- **Textual**: Modern terminal UI framework
- **Dynaconf**: Configuration management
- **python-ldap**: LDAP client library

#### Modular Design

```python
# Main application structure
class BigApp(WrappedAppBase):
    """Main container with tabbed interface."""
    
    def compose(self) -> ComposeResult:
        with TabbedContent():
            yield BrowserApp()
            yield ViewerApp()

# Sub-applications
class SubAppWidget(WrappedAppBase):
    """Base class for sub-applications."""
    
    def compose(self) -> ComposeResult:
        with LayoutUI1():
            yield TreeView()      # Left pane
            yield ContentView()   # Right pane
```

#### LDAP Backend

```python
class LDAPConnectionImproved:
    """Enhanced LDAP connection with filtering."""
    
    def __init__(self, config, filter_config=None):
        self.config = config
        self.filter_config = filter_config
    
    def connect(self):
        """Establish LDAP connection."""
    
    def search(self, base_dn, filter_str, attrs=None):
        """Search LDAP with filtering."""
```

### Configuration System

```python
# Configuration loading
settings = Dynaconf(
    envvar_prefix="LDAPCP_",
    settings_files=[
        'ldap_idp/settings.yaml',
        'ldap_idp/.secrets.yaml'
    ]
)

# Usage in code
ldap_uri = settings.authldap.uri
bind_dn = settings.authldap.bind_dn
```

## Adding New Applications

### 1. Create Application Module

```bash
mkdir ldap_idp/subapps/newapp
touch ldap_idp/subapps/newapp/__init__.py
touch ldap_idp/subapps/newapp/main.py
touch ldap_idp/subapps/newapp/app_menu.py
touch ldap_idp/subapps/newapp/app_content.py
```

### 2. Implement Application

```python
# ldap_idp/subapps/newapp/main.py
from ldap_idp.lib_textual.app_base import WrappedAppBase
from ldap_idp.lib_textual.layouts import LayoutUI1

class SubAppWidget(WrappedAppBase):
    """New application widget."""
    
    DEFAULT_ID = "subapp-newapp"
    
    def compose(self) -> ComposeResult:
        with LayoutUI1():
            yield TreeView()
            yield ContentView()
```

### 3. Register Application

```python
# ldap_idp/main.py
from ldap_idp.subapps.newapp.main import SubAppWidget as NewApp

APP_LIST = [
    BrowserApp(app_name="Browser"),
    ViewerApp(app_name="Viewer"),
    NewApp(app_name="New App"),  # Add here
]
```

## Testing

### Test Structure

```
tests/
├── conftest.py              # Test configuration
├── test_ldap_backend.py     # LDAP backend tests
├── test_config.py           # Configuration tests
└── test_apps/               # Application tests
    ├── test_browser.py
    └── test_viewer.py
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_ldap_backend.py

# Run with coverage
poetry run pytest --cov=ldap_idp

# Run with verbose output
poetry run pytest -v
```

### Test Configuration

```python
# tests/conftest.py
import pytest
from ldap_idp.config import settings

@pytest.fixture
def mock_ldap_config():
    """Mock LDAP configuration for testing."""
    return {
        'uri': 'ldap://localhost:389',
        'bind_dn': 'cn=admin,dc=example,dc=com',
        'bind_pass': 'admin'
    }

@pytest.fixture
def mock_ldap_connection(mock_ldap_config):
    """Mock LDAP connection."""
    # Implementation here
    pass
```

## Code Style

### Python Style Guide

- Follow PEP 8 with Black formatting
- Use type hints for all functions
- Maximum line length: 88 characters
- Use absolute imports over relative imports

### Naming Conventions

- **Classes**: PascalCase (`SubAppWidget`)
- **Functions/Variables**: snake_case (`load_ldap_session`)
- **Constants**: UPPER_CASE (`DEFAULT_ID`)
- **Files**: snake_case (`app_content.py`)

### Documentation

```python
def load_ldap_session(self) -> None:
    """Load data from the LDAP server.
    
    Establishes connection and loads initial data for the application.
    Handles connection errors and displays appropriate messages.
    """
    # Implementation
```

## Debugging

### Development Mode

```bash
# Run with development tools
poetry run textual dev ldap_idp.main

# Enable debug logging
export LDAPCP_LOGGING__LEVEL="DEBUG"
ldapcp-tui
```

### Common Issues

#### LDAP Connection Problems

```python
# Test LDAP connection
import ldap
conn = ldap.initialize('ldap://localhost:389')
conn.simple_bind_s('cn=admin,dc=example,dc=com', 'admin')
```

#### Textual Display Issues

```bash
# Check terminal capabilities
poetry run textual diagnose

# Test with different terminal
TERM=xterm-256color ldapcp-tui
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use in code
logger.debug("Connecting to LDAP server")
logger.error("Connection failed: %s", error)
```

## Performance Optimization

### LDAP Operations

- Use specific search filters to limit results
- Implement connection pooling
- Cache frequently accessed data
- Use async operations for non-blocking UI

### Memory Management

- Lazy load tree nodes
- Implement pagination for large result sets
- Clean up unused connections
- Monitor memory usage

### UI Responsiveness

- Use `@work` decorator for async operations
- Implement progress indicators
- Handle long-running operations gracefully
- Provide user feedback for all operations

## Contributing

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes
4. **Test** thoroughly
5. **Format** code with Black and isort
6. **Submit** a pull request

### Pull Request Guidelines

- Include tests for new features
- Update documentation as needed
- Follow existing code style
- Provide clear commit messages
- Reference issues in commit messages

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is adequate
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered

## Release Process

### Version Management

```bash
# Update version in pyproject.toml
poetry version patch  # or minor/major

# Build and publish
poetry build
poetry publish
```

### Release Checklist

- [ ] Update version number
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Publish to PyPI 