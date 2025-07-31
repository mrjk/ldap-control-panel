# syntax=docker/dockerfile:1.2

# =================================================================
# Build image
# =================================================================
FROM python:3.12-slim AS builder-image

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libldap2-dev \
    libsasl2-dev \
    libldap-2.5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv

# Install dependencies
RUN --mount=type=cache,mode=0755,target=/root/.cache \
    pip install --no-cache-dir poetry
    
# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pyproject.toml poetry.lock* README.md ./

RUN poetry config virtualenvs.create false && \
    poetry install --only=main --no-root

# Copy application code
COPY . .

# Install the application
RUN poetry install 


# =================================================================
# Production stage
# =================================================================
FROM python:3.12-slim AS runner-image

# Install runtime dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
    libldap-2.5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder-image /opt/venv /opt/venv

# Copy application code
COPY --from=builder-image /app /app

# Set working directory
WORKDIR /app

# Activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port for web interface
EXPOSE 8000

# Default command (can be overridden)
# CMD ["python", "-m", "ldap_idp.main"]
CMD ["python", "-m", "ldap_idp.serve", "--host", "0.0.0.0", "--port", "8000", "--debug"]