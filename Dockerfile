# CRM SAAS - Dockerfile
# Optimized Dockerfile for CRM SAAS Application

FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies (bookworm is stable, should work better)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# Add retry logic and trusted hosts for SSL issues
RUN pip install --no-cache-dir --upgrade \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    (sleep 5 && pip install --no-cache-dir --upgrade \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt)

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p data frontend/js frontend/css guides && \
    chmod -R 755 /app

# Note: Running as root for volume compatibility
# For production, consider using non-root user with proper volume permissions
# USER appuser

# Expose port
EXPOSE 8000

# Health check - check if the application is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

