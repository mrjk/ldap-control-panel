# LDAP Browser

A Python Textual application for browsing LDAP directories with a modern terminal-based interface.

## Features

- **CLI Interface**: Command-line input for LDAP connection parameters
- **Tree View**: Browse LDAP directory structure in a hierarchical tree
- **Record Details**: View full LDAP record attributes in a formatted table
- **Real-time Navigation**: Expand/collapse tree nodes to explore the directory
- **Modern UI**: Clean, responsive terminal interface with header and footer

## Installation

1. Make sure you have Python 3.12+ installed
2. Install dependencies using Poetry:

```bash
poetry install
```

Or using pip:

```bash
pip install textual python-ldap
```

## Usage

### Command Line Interface

The application accepts the following command-line arguments:

```bash
python ldap_idp/poc1/main.py \
    --ldap-uri "ldap://localhost:389" \
    --bind-dn "cn=admin,dc=example,dc=com" \
    --bind-password "your_password"
```

### Parameters

- `--ldap-uri`: LDAP server URI (e.g., `ldap://localhost:389` or `ldaps://ldap.example.com:636`)
- `--bind-dn`: Distinguished Name for authentication
- `--bind-password`: Password for authentication

### Quick Start

1. Modify the parameters in `test.py` to match your LDAP server configuration
2. Run the test script:

```bash
python test.py
```

## Interface

### Main Window Layout

- **Header**: Application title and status
- **Left Pane (40%)**: LDAP directory tree view
- **Right Pane (60%)**: Record details form
- **Footer**: Navigation hints and status

### Navigation

- **Tree Navigation**: Use arrow keys to navigate the LDAP tree
- **Expand/Collapse**: Press Enter or Space to expand/collapse tree nodes
- **Select Entry**: Click or use arrow keys to select an entry
- **View Details**: Selected entries show their attributes in the right pane

### Keyboard Shortcuts

- `q` or `Ctrl+C`: Quit the application
- `Tab`: Switch between panes
- `Enter`/`Space`: Expand/collapse tree nodes
- Arrow keys: Navigate tree and form

## Features

### LDAP Tree View

- Hierarchical display of LDAP directory structure
- Lazy loading of child entries (only loads when expanded)
- Clear visual indicators for expandable nodes
- Error handling for connection issues

### Record Details Form

- Tabular display of LDAP attributes
- Automatic conversion of binary data to readable format
- Support for multi-valued attributes
- Real-time updates when selecting different entries

### Connection Management

- Secure LDAP connection handling
- Error reporting for connection failures
- Support for both LDAP and LDAPS protocols
- Proper cleanup of connections

## Example Usage

### Connecting to a Local LDAP Server

```bash
python ldap_idp/poc1/main.py \
    --ldap-uri "ldap://localhost:389" \
    --bind-dn "cn=admin,dc=example,dc=com" \
    --bind-password "admin123"
```

### Connecting to an LDAPS Server

```bash
python ldap_idp/poc1/main.py \
    --ldap-uri "ldaps://ldap.example.com:636" \
    --bind-dn "uid=user,ou=people,dc=example,dc=com" \
    --bind-password "user_password"
```

## Development

### Project Structure

```
ldap-idp/
├── ldap_idp/
│   └── poc1/
│       └── main.py          # Main application
├── test.py                  # Test runner script
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

### Dependencies

- `textual`: Modern terminal UI framework
- `python-ldap`: LDAP client library

### Running in Development Mode

```bash
# Install development dependencies
poetry install --with dev

# Run with development tools
poetry run textual dev ldap_idp/poc1/main.py -- --ldap-uri "ldap://localhost:389" --bind-dn "cn=admin,dc=example,dc=com" --bind-password "admin123"
```

## Troubleshooting

### Connection Issues

- Verify LDAP server is running and accessible
- Check URI format and port number
- Ensure bind DN and password are correct
- For LDAPS, verify SSL certificate configuration

### Display Issues

- Ensure terminal supports Unicode characters
- Check terminal size (minimum 80x24 recommended)
- Verify Textual compatibility with your terminal

### Performance

- Large directories may take time to load
- Consider using more specific search filters
- Monitor memory usage with very large LDAP trees

## License

GPLv3 - See LICENSE file for details. 