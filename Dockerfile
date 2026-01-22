# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Set environment variables to optimize Python behavior
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies (gcc is often required for some python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment and install dependencies
COPY requirements.txt .
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Stage 2: Runner
FROM python:3.11-slim AS runner

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Add virtual environment to PATH
ENV PATH="/app/venv/bin:$PATH"

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /app/venv /app/venv

# Copy application code
COPY --chown=appuser:appgroup ./app /app/app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["python", "app/main.py"]
