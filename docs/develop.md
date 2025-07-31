# Development Guide

## Quick Start

### Local Development

```bash
# Install dependencies
poetry install --with dev

# Run with development tools
poetry run textual dev ldap_idp.main

# Run tests
poetry run pytest
```

### Docker Development

```bash
# Build Docker image
docker compose build

# Run with Docker Compose
docker compose up

# Run interactive container
docker run --rm -ti ldap-idp:latest /bin/bash

# Run as root (for debugging)
docker run -u 0 --rm -ti ldap-idp:latest /bin/bash
```

## Docker Commands

### Basic Usage

```bash
# Run with environment variables
docker run --rm -ti \
  -e "LDAPCP__AUTHLDAP__uri=ldap://IP:PORT" \
  -e "LDAPCP__AUTHLDAP__bind_dn=cn=admin,BASE_DN" \
  -e "LDAPCP__AUTHLDAP__bind_pass=PASS" \
  ldap-idp:latest ldapcp-tui
```

### Example Configurations

```bash
# Development environment
docker run --rm -ti \
  -e LDAPCP__AUTHLDAP__uri=ldap://localhost:389 \
  -e LDAPCP__AUTHLDAP__bind_dn=cn=admin,dc=example,dc=com \
  -e LDAPCP__AUTHLDAP__bind_pass=admin \
  ldap-idp:latest ldapcp-tui

# Production environment
docker run --rm -ti \
  -e LDAPCP__AUTHLDAP__uri=ldap://ldap.example.com:389 \
  -e LDAPCP__AUTHLDAP__bind_dn=cn=admin,dc=example,dc=com \
  -e LDAPCP__AUTHLDAP__bind_pass=${LDAP_PASSWORD} \
  ldap-idp:latest ldapcp-tui
```

### Using Environment Variables

```bash
# Set environment variables
export LDAPCP__AUTHLDAP__uri=ldap://your-ldap-server:389
export LDAPCP__AUTHLDAP__bind_dn=cn=admin,dc=example,dc=com
export LDAPCP__AUTHLDAP__bind_pass=your-password

# Run with environment variables
docker run --rm -ti \
  -e LDAPCP__AUTHLDAP__uri=${LDAPCP__AUTHLDAP__uri} \
  -e LDAPCP__AUTHLDAP__bind_dn=${LDAPCP__AUTHLDAP__bind_dn} \
  -e LDAPCP__AUTHLDAP__bind_pass=${LDAPCP__AUTHLDAP__bind_pass} \
  ldap-idp:latest ldapcp-tui
```

## Docker Compose

### Development Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  ldap-idp:
    build: .
    environment:
      - LDAPCP__AUTHLDAP__uri=ldap://ldap-server:389
      - LDAPCP__AUTHLDAP__bind_dn=cn=admin,dc=example,dc=com
      - LDAPCP__AUTHLDAP__bind_pass=admin
    volumes:
      - ./ldap_idp:/app/ldap_idp
    ports:
      - "8000:8000"
```

### Commands

```bash
# Build and run
docker compose up

# Build with progress
docker compose --progress plain build

# Run in background
docker compose up -d

# View logs
docker compose logs -f
```

## Development Workflow

### Code Quality

```bash
# Format code
poetry run black ldap_idp/
poetry run isort ldap_idp/

# Type checking
poetry run mypy ldap_idp/

# Linting
poetry run flake8 ldap_idp/
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=ldap_idp

# Run specific test
poetry run pytest tests/test_ldap_backend.py
```

### Debugging

```bash
# Enable debug logging
export LDAPCP__LOGGING__LEVEL="DEBUG"

# Run with development tools
poetry run textual dev ldap_idp.main

# Check terminal capabilities
poetry run textual diagnose
```

## Environment Variables

### Configuration Override

All settings can be overridden with environment variables:

```bash
# LDAP Connection
export LDAPCP__AUTHLDAP__uri="ldap://localhost:389"
export LDAPCP__AUTHLDAP__bind_dn="cn=admin,dc=example,dc=com"
export LDAPCP__AUTHLDAP__bind_pass="admin"

# Application Settings
export LDAPCP__BROWSER__default_view="table"
export LDAPCP__BROWSER__auto_expand="true"

# Logging
export LDAPCP__LOGGING__level="DEBUG"
```

### Docker Environment

```bash
# Run with custom configuration
docker run --rm -ti \
  -e LDAPCP__AUTHLDAP__uri=ldap://ldap.example.com:389 \
  -e LDAPCP__BROWSER__default_view=json \
  -e LDAPCP__LOGGING__level=DEBUG \
  ldap-idp:latest ldapcp-tui
```

## Troubleshooting

### Common Issues

**Docker Connection Problems**
```bash
# Test LDAP connectivity from container
docker run --rm -ti ldap-idp:latest \
  python -c "import ldap; print('LDAP module available')"
```

**Permission Issues**
```bash
# Run container as root for debugging
docker run -u 0 --rm -ti ldap-idp:latest /bin/bash
```

**Display Issues**
```bash
# Check terminal capabilities
docker run --rm -ti ldap-idp:latest textual diagnose
```

### Debug Commands

```bash
# Interactive debugging
docker run --rm -ti ldap-idp:latest /bin/bash

# Check application logs
docker logs <container_id>

# Inspect container
docker inspect <container_id>
```
