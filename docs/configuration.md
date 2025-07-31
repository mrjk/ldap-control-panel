# Configuration Guide

## Overview

LDAP Control Panel uses YAML-based configuration with Dynaconf for flexible settings management. Configuration files are loaded in order with later files overriding earlier ones.

## Configuration Files

- `ldap_idp/settings.yaml` - Main configuration
- `ldap_idp/.secrets.yaml` - Sensitive data (not in version control)
- Environment variables with `LDAPCP_` prefix

## LDAP Authentication

```yaml
authldap:
  uri: "ldap://localhost:389"           # LDAP server URI
  base_dn: ""                           # Base DN for searches
  bind_dn: "cn=admin,dc=example,dc=com" # Bind DN for authentication
  bind_pass: "admin"                    # Bind password
```

### URI Formats

- `ldap://server:389` - Standard LDAP
- `ldaps://server:636` - LDAP over SSL
- `ldap://server:389/dc=example,dc=com` - With base DN

## Browser Application

### Display Settings

```yaml
browser:
  default_view: table                    # Default view: table, json
  containers_first: true                 # Show containers first
  display_mode: full                     # Display mode: simple, full
  auto_expand: true                      # Auto-expand tree on startup
```

### Attribute Filtering

```yaml
browser:
  # Hide object classes from display
  oc_silented:
    - top
    - organizationalPerson
  
  # Preferred object class order
  oc_order:
    - inetOrgPerson
    - posixAccount
  
  # Hide sensitive attributes
  attr_silented:
    - userPassword
    - userCertificate
  
  # Preferred attribute display order
  attr_order:
    - objectClass
    - cn
    - uid
    - mail
    - memberOf
```

## Viewer Application

### General Settings

```yaml
viewer:
  default_view: default                  # Default view mode
  missing_value_placeholder: "-"        # Placeholder for missing values
```

### Entity Definitions

Define custom views for different LDAP object types:

```yaml
viewer_entities:
  users:
    name: Users
    desc: Manage users
    icon: 👤
    ldap_filter: '(objectclass=inetOrgPerson)'
    
    profiles:
      overview:
        desc: Show all users
        ldap_filter: '(objectclass=inetOrgPerson)'
        attr:
          - DN
          - cn
          - uid
          - mail
      
      posix:
        desc: Show posix users
        ldap_filter: '(objectclass=posixAccount)'
        attr:
          - uid
          - uidNumber
          - gidNumber
          - DN
```

## Environment Variables

Override settings with environment variables:

```bash
export LDAPCP_AUTHLDAP__URI="ldap://ldap.example.com:389"
export LDAPCP_AUTHLDAP__BIND_DN="cn=admin,dc=example,dc=com"
export LDAPCP_AUTHLDAP__BIND_PASS="secret"
```

## Security Considerations

### Sensitive Data

Store passwords and sensitive data in `.secrets.yaml`:

```yaml
# ldap_idp/.secrets.yaml
authldap:
  bind_pass: "your-secret-password"
```

### File Permissions

```bash
# Secure the secrets file
chmod 600 ldap_idp/.secrets.yaml
```

## Advanced Configuration

### Custom Filters

Create complex LDAP filters:

```yaml
viewer_entities:
  active_users:
    ldap_filter: '(&(objectClass=inetOrgPerson)(!(accountStatus=disabled)))'
  
  admin_groups:
    ldap_filter: '(&(objectClass=groupOfUniqueNames)(cn=*admin*))'
```

### Multiple LDAP Servers

Use environment variables to switch configurations:

```bash
# Development
export LDAPCP_AUTHLDAP__URI="ldap://dev-ldap:389"

# Production  
export LDAPCP_AUTHLDAP__URI="ldaps://prod-ldap:636"
```

### Debug Mode

Enable debug logging:

```bash
export LDAPCP_LOGGING__LEVEL="DEBUG"
ldapcp-tui
``` 