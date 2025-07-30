# Multi-stage Dockerfile for MLOps Best Practices
# Stage 1: Base image with Python and system dependencies
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mlops && useradd -r -g mlops mlops

# Stage 2: Dependencies
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Development dependencies (for testing)
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    pytest-mock \
    black \
    isort \
    flake8 \
    mypy \
    bandit \
    safety

# Stage 4: Production build
FROM base as production

# Set working directory
WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/
COPY models/ ./models/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p logs models data

# Set ownership to non-root user
RUN chown -R mlops:mlops /app

# Switch to non-root user
USER mlops

# Expose ports
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "src/serving/app.py"]

# Stage 5: Monitoring build
FROM production as monitoring

# Install monitoring dependencies
USER root
RUN pip install --no-cache-dir psutil

# Copy monitoring configuration
COPY monitoring/ ./monitoring/

# Switch back to non-root user
USER mlops

# Expose monitoring port
EXPOSE 8002

# Monitoring command
CMD ["python", "src/monitoring/monitor.py", "--daemon"]

# Stage 6: Testing build
FROM development as testing

# Copy test files
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Copy application code
COPY src/ ./src/
COPY configs/ ./configs/

# Set test environment
ENV PYTHONPATH=/app
ENV TESTING=true

# Default test command
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=html"]

# Stage 7: CI/CD build
FROM testing as ci

# Install additional CI tools
RUN pip install --no-cache-dir \
    coverage \
    codecov

# Copy CI scripts
COPY .github/ ./.github/
COPY scripts/ci/ ./scripts/ci/

# CI command
CMD ["python", "scripts/ci/run_tests.py"]