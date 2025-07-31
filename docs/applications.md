# Applications Guide

## Overview

LDAP Control Panel consists of multiple applications, each designed for specific LDAP management tasks. All applications share the same LDAP connection and configuration.

## Browser Application

The Browser application provides general LDAP directory navigation and exploration.

### Features

- **Tree Navigation**: Hierarchical view of LDAP directory structure
- **Entry Details**: View and edit LDAP entry attributes
- **Multiple Views**: Table and JSON formats for data display
- **Search & Filter**: Find entries using LDAP filters
- **Real-time Updates**: Live data refresh and connection monitoring

### Interface

```
┌─────────────────────────────────────────────────────────┐
│ LDAP Control Panel - Browser                          │
├─────────────────┬─────────────────────────────────────┤
│ Directory Tree  │ Entry Details                      │
│                 │                                     │
│ dc=example,dc=  │ DN: cn=user1,ou=users,dc=example, │
│ ├─ ou=users     │     dc=com                         │
│ │  ├─ cn=user1  │                                     │
│ │  └─ cn=user2  │ cn: user1                          │
│ └─ ou=groups    │ uid: user1                         │
│    ├─ cn=admins │ mail: user1@example.com            │
│    └─ cn=users  │                                     │
└─────────────────┴─────────────────────────────────────┘
```

### Navigation

- **Arrow Keys**: Navigate tree structure
- **Enter/Space**: Expand/collapse nodes
- **Tab**: Switch between tree and details
- **v**: Cycle through view modes (table/JSON)

### Configuration

Browser-specific settings in `settings.yaml`:

```yaml
browser:
  default_view: table
  containers_first: true
  display_mode: full
  auto_expand: true
  oc_silented: [top]
  attr_silented: [userPassword]
```

## Viewer Application

The Viewer application provides specialized views for common LDAP management tasks.

### Features

- **Entity Views**: Predefined views for users, groups, and OUs
- **Profile System**: Custom attribute sets for different use cases
- **Quick Filters**: Common LDAP filters for typical operations
- **Data Export**: Export data in various formats
- **Bulk Operations**: Manage multiple entries simultaneously

### Entity Types

#### Users

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
        attr: [DN, cn, uid, mail]
      
      posix:
        desc: Show posix users
        ldap_filter: '(objectclass=posixAccount)'
        attr: [uid, uidNumber, gidNumber, DN]
```

#### Groups

```yaml
viewer_entities:
  groups:
    name: Groups
    desc: Manage groups
    icon: 👥
    ldap_filter: '(|(objectClass=groupOfUniqueNames)(objectClass=groupOfNames))'
    
    profiles:
      overview:
        desc: Show all groups
        attr: [DN, cn, gidNumber, description]
      
      admin:
        desc: Show admin groups
        ldap_filter: '(&(objectClass=groupOfUniqueNames)(cn=*admin*))'
        attr: [cn, uniqueMember, description]
```

#### Organizational Units

```yaml
viewer_entities:
  ou:
    name: Org
    desc: Show organizational units
    icon: 📁
    ldap_filter: '(objectClass=organizationalUnit)'
    
    profiles:
      overview:
        desc: Show organizational units
        attr: [DN, ou, description]
      
      structure:
        desc: Show OU structure
        attr: [ou, description]
```

### Interface

```
┌─────────────────────────────────────────────────────────┐
│ LDAP Control Panel - Viewer                           │
├─────────────────┬─────────────────────────────────────┤
│ Entity Tree     │ Entry List                          │
│                 │                                     │
│ 👤 Users        │ DN: cn=user1,ou=users,dc=example,  │
│ ├─ Overview     │     dc=com                          │
│ ├─ Posix        │ cn: user1                           │
│ └─ Members      │ uid: user1                          │
│ 👥 Groups       │ mail: user1@example.com             │
│ ├─ Overview     │                                     │
│ ├─ Admin        │                                     │
│ └─ Posix        │                                     │
│ 📁 Org          │                                     │
└─────────────────┴─────────────────────────────────────┘
```

### Navigation

- **Arrow Keys**: Navigate entity tree and entry list
- **Enter**: Select entity or profile
- **Tab**: Switch between tree and list
- **v**: Cycle through view modes

## Web Interface

Both applications are available through the web interface using textual-serve.

### Access

```bash
# Start web server
ldapcp-serve --host 0.0.0.0 --port 8000

# Access in browser
http://localhost:8000
```

### Features

- **Browser Access**: Use any modern web browser
- **Responsive Design**: Works on desktop and mobile
- **Same Functionality**: All TUI features available
- **Multi-user Support**: Multiple users can connect simultaneously

## Keyboard Shortcuts

### Global Shortcuts

- `q` or `Ctrl+C`: Quit application
- `Tab`: Switch between panes
- `F1`: Show help
- `Ctrl+R`: Refresh data

### Browser Shortcuts

- `v`: Cycle view modes (table/JSON)
- `Enter/Space`: Expand/collapse tree nodes
- `Arrow Keys`: Navigate tree and forms

### Viewer Shortcuts

- `v`: Cycle view modes
- `Enter`: Select entity or profile
- `Arrow Keys`: Navigate entity tree and entry list

## Data Views

### Table View

Displays LDAP attributes in a formatted table:

```
┌─────────┬─────────────────────────────────────────────┐
│ Attribute│ Value                                      │
├─────────┼─────────────────────────────────────────────┤
│ DN      │ cn=user1,ou=users,dc=example,dc=com       │
│ cn      │ user1                                      │
│ uid     │ user1                                      │
│ mail    │ user1@example.com                          │
│ memberOf│ cn=users,ou=groups,dc=example,dc=com      │
└─────────┴─────────────────────────────────────────────┘
```

### JSON View

Displays LDAP entries in JSON format:

```json
{
  "dn": "cn=user1,ou=users,dc=example,dc=com",
  "attributes": {
    "cn": ["user1"],
    "uid": ["user1"],
    "mail": ["user1@example.com"],
    "memberOf": ["cn=users,ou=groups,dc=example,dc=com"]
  }
}
```

### Best Practices

- Use specific LDAP filters to limit results
- Configure attribute filtering to hide unnecessary data
- Enable caching for frequently accessed data
- Monitor memory usage with large directories 