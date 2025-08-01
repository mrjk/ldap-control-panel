#!/usr/bin/env python3
"""
LDAP Control Panel
"""

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8
    from importlib_metadata import version, PackageNotFoundError

# Guess version from package
__PACKAGE_NAME__ = 'ldap_idp'
try:
    __version__ = version(__PACKAGE_NAME__)
except PackageNotFoundError:
    __version__ = "unknown"

