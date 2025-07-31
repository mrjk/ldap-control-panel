# LDAP Control Panel Documentation

A modern LDAP management tool with terminal and web interfaces.

## Overview

LDAP Control Panel is a Python application built with Textual that provides both terminal and web interfaces for LDAP directory management. It features a modular architecture with separate applications for different LDAP operations.

## Quick Links

- [Installation Guide](installation.md)
- [Configuration](configuration.md)
- [Applications](applications.md)
- [Development](development.md)
- [Screenshots](screenshots/)

## Features

### Multi-Interface Support
- **Terminal UI**: Rich TUI with tree navigation and data views
- **Web Interface**: Browser-based access via textual-serve

### Applications
- **Browser**: General LDAP directory navigation
- **Viewer**: Custom views for users, groups, and OUs

### Key Capabilities
- Tree-based LDAP navigation
- Multiple data view formats (table, JSON)
- Configurable attribute display
- Custom filters and profiles
- Real-time data updates

## Architecture

```
ldap_idp/
├── main.py              # Main application entry point
├── serve.py             # Web interface server
├── subapps/             # Application modules
│   ├── browser/         # LDAP browser application
│   └── viewer/          # LDAP viewer application
├── lib_textual/         # Shared UI components
├── config.py            # Configuration management
└── settings.yaml        # Application settings
```

## Getting Started

1. **Install**: `poetry install`
2. **Configure**: Edit `ldap_idp/settings.yaml`
3. **Run TUI**: `ldapcp-tui`
4. **Run Web**: `ldapcp-serve`

## Screenshots

See the [screenshots directory](screenshots/) for examples of the application interface. 