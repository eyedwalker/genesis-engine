# Genesis Engine API - Production Dockerfile
# Multi-stage build for smaller final image

# ---- Build Stage ----
FROM python:3.11-slim as builder

WORKDIR /build

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements-minimal.txt

# ---- Runtime Stage ----
FROM python:3.11-slim

WORKDIR /app

# Runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY genesis/ genesis/
COPY requirements-minimal.txt .

# Create non-root user
RUN groupadd -r genesis && useradd -r -g genesis -d /app genesis && \
    chown -R genesis:genesis /app

USER genesis

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "genesis.api.server:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--limit-concurrency", "100"]
