# Installation Guide

## Requirements

- Python 3.12 or higher
- Poetry (recommended) or pip
- LDAP server access

## Installation Methods

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ldap-idp

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Install from PyPI (when available)
pip install ldap-idp

# Or install from source
git clone <repository-url>
cd ldap-idp
pip install -e .
```

### Using Docker

Docker provides a containerized environment that isolates the application and its dependencies.

#### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd ldap-idp

# Build the Docker image
docker build -t ldap-idp .

# Run the web interface
docker run -p 8000:8000 ldap-idp python -m ldap_idp.serve --host 0.0.0.0 --port 8000

# Run the CLI application
docker run -it ldap-idp python -m ldap_idp.main
```

#### Using Docker Compose (Recommended for Production)

Docker Compose provides better orchestration and is ideal for production deployments.

```bash
# Clone the repository
git clone <repository-url>
cd ldap-idp

# Set up environment variables (create .env file)
cp .env.example .env
# Edit .env with your LDAP configuration

# Start the web service
docker-compose up ldap-idp-web

# Start the CLI service
docker-compose --profile cli run ldap-idp-cli

# Start development mode with hot reload
docker-compose --profile dev up ldap-idp-web-dev
```

## Installation Method Comparison

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Poetry** | Development, local testing | Full control, easy debugging, fast iteration | Requires Python setup, dependency management |
| **Docker** | Quick testing, isolated environment | Consistent environment, no local Python setup | Larger disk usage, slower startup |
| **Docker Compose** | Production, multi-service deployments | Easy orchestration, environment management, scaling | More complex setup, requires Docker knowledge |

### When to Use Each Method

- **Poetry**: Best for development, debugging, and when you need full control over the environment
- **Docker**: Good for quick testing, CI/CD pipelines, and when you want isolation
- **Docker Compose**: Ideal for production deployments, when you need to manage multiple services, or when you want easy environment variable management

## Development Setup

```bash
# Install with development dependencies
poetry install --with dev

# Install pre-commit hooks (optional)
poetry run pre-commit install
```

## Verification

After installation, verify the setup:

```bash
# Check if the application runs
ldapcp-tui --help

# Check web server
ldapcp-serve --help
```

## Configuration

Before running the application, configure your LDAP connection:

1. Copy the example configuration:
   ```bash
   cp ldap_idp/settings.yaml.example ldap_idp/settings.yaml
   ```

2. Edit `ldap_idp/settings.yaml` with your LDAP server details:
   ```yaml
   authldap:
     uri: "ldap://your-ldap-server:389"
     bind_dn: "cn=admin,dc=example,dc=com"
     bind_pass: "your-password"
   ```

### Getting Help

- Check the [Configuration](configuration.md) guide
- Review [Development](development.md) for debugging tips
- Open an issue on the project repository 