"""
Enhanced Docker Optimization Assistant

Comprehensive Docker best practices covering:
- Multi-stage builds
- Distroless and minimal base images
- BuildKit features (cache mounts, secrets)
- Image signing (Docker Content Trust, Cosign)
- SBOM generation (Syft, Trivy)
- Security scanning pipelines
- Layer optimization
- Non-root containers

References:
- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Distroless: https://github.com/GoogleContainerTools/distroless
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class DockerFinding(BaseModel):
    """Structured Docker finding output"""

    finding_id: str = Field(..., description="Unique identifier (DOCKER-001, etc.)")
    title: str = Field(..., description="Brief title of the issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Security/Size/Performance/BestPractice")

    dockerfile_line: int = Field(default=0, description="Line number in Dockerfile")
    current_instruction: str = Field(default="", description="Current Dockerfile instruction")
    improved_instruction: str = Field(default="", description="Improved instruction")

    size_impact: str = Field(default="", description="Impact on image size")
    security_impact: str = Field(default="", description="Security implications")

    tools: List[Dict[str, str]] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedDockerAssistant:
    """Enhanced Docker Optimization Assistant"""

    def __init__(self):
        self.name = "Enhanced Docker Optimization"
        self.version = "2.0.0"
        self.standards = ["OCI", "CIS Docker Benchmark", "SLSA"]

    # =========================================================================
    # MULTI-STAGE BUILDS
    # =========================================================================

    @staticmethod
    def multi_stage_builds() -> Dict[str, Any]:
        """Multi-stage build patterns"""
        return {
            "bad": """
# BAD: Single stage with build tools in final image (1.2GB)
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
# Contains: node, npm, build tools, source code, node_modules
            """,
            "good": """
# GOOD: Multi-stage build (250MB)
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine AS production
WORKDIR /app
# Copy only what's needed
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
            """,
            "python_example": """
# Python multi-stage with distroless
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install --user pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system

# Stage 2: Production with distroless
FROM gcr.io/distroless/python3-debian11
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app .
CMD ["app.py"]
            """,
            "go_example": """
# Go: Build static binary, use scratch/distroless
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/main

# Scratch = smallest possible (just the binary)
FROM scratch
COPY --from=builder /app/main /main
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
USER 1000:1000
ENTRYPOINT ["/main"]
# Final image: ~10-15MB
            """,
        }

    # =========================================================================
    # SECURITY BEST PRACTICES
    # =========================================================================

    @staticmethod
    def security_practices() -> Dict[str, Any]:
        """Docker security best practices"""
        return {
            "non_root": {
                "bad": """
# BAD: Running as root (default)
FROM nginx:latest
COPY nginx.conf /etc/nginx/nginx.conf
# Runs as root!
                """,
                "good": """
# GOOD: Non-root user
FROM nginx:latest

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Change ownership and switch user
COPY --chown=appuser:appgroup nginx.conf /etc/nginx/nginx.conf
RUN chown -R appuser:appgroup /var/cache/nginx /var/log/nginx

USER appuser:appgroup
                """,
            },
            "no_secrets": {
                "bad": """
# BAD: Secrets in Dockerfile (leaked in layers!)
FROM python:3.11
ENV DATABASE_PASSWORD=supersecret123
RUN pip install --extra-index-url https://user:token@private.pypi.org/simple package
                """,
                "good": """
# GOOD: Use BuildKit secrets (not stored in layers)
# syntax=docker/dockerfile:1.4
FROM python:3.11

# Secret available only during build, not in final image
RUN --mount=type=secret,id=pip_token \\
    pip install --extra-index-url https://user:$(cat /run/secrets/pip_token)@private.pypi.org/simple package

# Build with: docker build --secret id=pip_token,src=./token.txt .
                """,
            },
            "minimal_packages": """
# GOOD: Only install what you need
FROM python:3.11-slim

# Don't install recommends, clean up cache
RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        libpq5 \\
    && rm -rf /var/lib/apt/lists/*
            """,
            "read_only_filesystem": """
# GOOD: Read-only root filesystem
# docker run --read-only --tmpfs /tmp myimage

# In Kubernetes:
# securityContext:
#   readOnlyRootFilesystem: true
            """,
        }

    # =========================================================================
    # IMAGE OPTIMIZATION
    # =========================================================================

    @staticmethod
    def image_optimization() -> Dict[str, Any]:
        """Image size and layer optimization"""
        return {
            "layer_caching": {
                "bad": """
# BAD: Copy all files before installing dependencies
FROM node:18-alpine
COPY . .
RUN npm install  # Cache invalidated on ANY file change!
                """,
                "good": """
# GOOD: Copy dependency files first
FROM node:18-alpine
WORKDIR /app

# Copy only dependency files first
COPY package.json package-lock.json ./
RUN npm ci

# Then copy source (changes more frequently)
COPY . .
RUN npm run build
                """,
            },
            "combine_commands": {
                "bad": """
# BAD: Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*
                """,
                "good": """
# GOOD: Single layer, cleanup in same layer
RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        curl \\
        git \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean
                """,
            },
            "use_specific_tags": {
                "bad": "FROM python:latest  # Unpredictable!",
                "good": "FROM python:3.11.6-slim-bookworm  # Reproducible",
            },
        }

    # =========================================================================
    # SCANNING AND SBOM
    # =========================================================================

    @staticmethod
    def scanning_sbom() -> Dict[str, Any]:
        """Security scanning and SBOM generation"""
        return {
            "trivy": """
# Scan image for vulnerabilities
trivy image myapp:latest

# Scan with severity filter
trivy image --severity CRITICAL,HIGH myapp:latest

# Generate SBOM
trivy image --format spdx-json --output sbom.json myapp:latest

# In CI/CD
trivy image --exit-code 1 --severity CRITICAL myapp:latest
            """,
            "syft": """
# Generate SBOM with Syft
syft myapp:latest -o spdx-json > sbom.json
syft myapp:latest -o cyclonedx-json > sbom-cyclonedx.json
            """,
            "hadolint": """
# Lint Dockerfile
hadolint Dockerfile

# In CI
hadolint --failure-threshold warning Dockerfile
            """,
            "ci_pipeline": """
# GitHub Actions example
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Build image
      run: docker build -t myapp:${{ github.sha }} .

    - name: Lint Dockerfile
      uses: hadolint/hadolint-action@v3.1.0

    - name: Scan for vulnerabilities
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: myapp:${{ github.sha }}
        exit-code: '1'
        severity: 'CRITICAL,HIGH'

    - name: Generate SBOM
      uses: anchore/sbom-action@v0
      with:
        image: myapp:${{ github.sha }}
            """,
        }

    # =========================================================================
    # BUILDKIT FEATURES
    # =========================================================================

    @staticmethod
    def buildkit_features() -> Dict[str, Any]:
        """BuildKit advanced features"""
        return {
            "cache_mounts": {
                "description": "Cache dependencies across builds",
                "bad": '''
# BAD: Download dependencies every build
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt  # Downloads every time
                ''',
                "good": '''
# GOOD: Cache pip downloads
# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

# Cache pip downloads between builds
RUN --mount=type=cache,target=/root/.cache/pip \\
    pip install -r requirements.txt

# Node.js: Cache npm
FROM node:18-alpine
RUN --mount=type=cache,target=/root/.npm \\
    npm ci

# Go: Cache go modules
FROM golang:1.21-alpine
RUN --mount=type=cache,target=/go/pkg/mod \\
    go mod download
                ''',
            },
            "secret_mounts": {
                "description": "Use secrets without storing in layers",
                "bad": '''
# BAD: Secrets in environment or COPY
FROM python:3.11
# Secrets visible in image layers!
ENV GITHUB_TOKEN=ghp_xxxx
COPY .npmrc /root/.npmrc
                ''',
                "good": '''
# GOOD: Secret mounts - never stored in image
# syntax=docker/dockerfile:1.4
FROM python:3.11

# Secret only available during this RUN, not in final image
RUN --mount=type=secret,id=github_token \\
    pip install git+https://$(cat /run/secrets/github_token)@github.com/private/repo.git

# Build with: docker build --secret id=github_token,src=./token.txt .

# NPM private registry
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \\
    npm ci
                ''',
            },
            "ssh_mounts": {
                "description": "Use SSH keys for private repos",
                "good": '''
# syntax=docker/dockerfile:1.4
FROM python:3.11

# SSH mount for private git repos
RUN --mount=type=ssh \\
    pip install git+ssh://git@github.com/private/repo.git

# Build with: docker build --ssh default .
# Or with specific key: docker build --ssh default=$SSH_AUTH_SOCK .
                ''',
            },
            "heredocs": {
                "description": "Multi-line scripts in Dockerfile",
                "good": '''
# syntax=docker/dockerfile:1.4
FROM python:3.11

# Here-doc for multi-line scripts
RUN <<EOF
set -e
apt-get update
apt-get install -y --no-install-recommends curl
rm -rf /var/lib/apt/lists/*
EOF

# Here-doc for creating config files
COPY <<EOF /app/config.py
DEBUG = False
DATABASE_URL = "postgresql://db:5432/app"
REDIS_URL = "redis://redis:6379"
EOF
                ''',
            },
            "parallel_builds": '''
# BuildKit builds stages in parallel when possible
# syntax=docker/dockerfile:1.4

# These two stages build in parallel
FROM python:3.11-slim AS python-deps
RUN pip install --user -r requirements.txt

FROM node:18-alpine AS js-deps
RUN npm ci

# Final stage combines both
FROM python:3.11-slim
COPY --from=python-deps /root/.local /root/.local
COPY --from=js-deps /app/node_modules /app/node_modules
            ''',
        }

    # =========================================================================
    # IMAGE SIGNING AND VERIFICATION
    # =========================================================================

    @staticmethod
    def image_signing() -> Dict[str, Any]:
        """Docker image signing and verification"""
        return {
            "cosign": {
                "description": "Sign and verify images with Cosign",
                "signing": '''
# Install cosign
brew install cosign  # or download from GitHub

# Generate key pair
cosign generate-key-pair
# Creates cosign.key (private) and cosign.pub (public)

# Sign image
cosign sign --key cosign.key myregistry.io/myapp:v1.0.0

# Keyless signing (recommended) - uses OIDC
cosign sign myregistry.io/myapp:v1.0.0
# Opens browser for OIDC authentication (GitHub, Google, etc.)

# Sign with GitHub Actions (keyless)
# .github/workflows/build.yml
jobs:
  build:
    permissions:
      id-token: write  # Required for keyless signing
      contents: read
    steps:
    - uses: sigstore/cosign-installer@main

    - name: Sign image
      run: cosign sign myregistry.io/myapp:${{ github.sha }}
      env:
        COSIGN_EXPERIMENTAL: 1
                ''',
                "verification": '''
# Verify signature with public key
cosign verify --key cosign.pub myregistry.io/myapp:v1.0.0

# Keyless verification
cosign verify myregistry.io/myapp:v1.0.0 \\
  --certificate-identity user@example.com \\
  --certificate-oidc-issuer https://accounts.google.com

# Verify in Kubernetes with Kyverno policy
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-cosign-signature
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: verify-signature
    match:
      resources:
        kinds:
        - Pod
    verifyImages:
    - image: "myregistry.io/*"
      key: |-
        -----BEGIN PUBLIC KEY-----
        MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
        -----END PUBLIC KEY-----
                ''',
            },
            "docker_content_trust": '''
# Docker Content Trust (DCT) - built-in signing

# Enable DCT
export DOCKER_CONTENT_TRUST=1

# Push signed image
docker push myregistry.io/myapp:v1.0.0
# First time: creates root key and repository key
# Prompts for passphrases

# Pull with verification
docker pull myregistry.io/myapp:v1.0.0
# Fails if image not signed or signature invalid

# List signed images
docker trust inspect myregistry.io/myapp

# Add signer
docker trust signer add --key cert.pem signer_name myregistry.io/myapp
            ''',
            "notary": '''
# Notary v2 (next-gen signing, OCI-native)

# Sign with notation
notation sign myregistry.io/myapp:v1.0.0

# Verify
notation verify myregistry.io/myapp:v1.0.0

# List signatures
notation list myregistry.io/myapp:v1.0.0
            ''',
        }

    # =========================================================================
    # DISTROLESS AND MINIMAL IMAGES
    # =========================================================================

    @staticmethod
    def minimal_base_images() -> Dict[str, Any]:
        """Minimal and distroless base images"""
        return {
            "distroless": {
                "description": "Google's distroless images - no shell, no package manager",
                "examples": '''
# Python distroless
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt
COPY . .

FROM gcr.io/distroless/python3-debian11
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app .
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages
CMD ["app.py"]
# Result: ~50MB, no shell, minimal attack surface

# Java distroless
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM gcr.io/distroless/java17-debian11
COPY --from=builder /app/target/app.jar /app.jar
EXPOSE 8080
CMD ["app.jar"]
# Result: ~200MB vs 400MB+ for full JDK image

# Node.js distroless
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM gcr.io/distroless/nodejs18-debian11
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["dist/index.js"]
                ''',
            },
            "chainguard": {
                "description": "Chainguard Images - distroless with SBOM and signatures",
                "examples": '''
# Chainguard Python
FROM cgr.dev/chainguard/python:latest AS builder
# ...

FROM cgr.dev/chainguard/python:latest-dev
# Dev variant has shell for debugging

# Benefits:
# - Zero known CVEs at build time
# - Signed with Sigstore
# - SBOM included
# - glibc-based for compatibility

# Check image provenance
cosign verify cgr.dev/chainguard/python:latest \\
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
                ''',
            },
            "alpine": {
                "description": "Alpine Linux - small but with shell",
                "examples": '''
# Alpine vs Debian comparison
# python:3.11-alpine  ~50MB
# python:3.11-slim    ~130MB
# python:3.11         ~900MB

# Alpine gotchas
FROM python:3.11-alpine

# May need build deps for some packages
RUN apk add --no-cache \\
    gcc \\
    musl-dev \\
    libffi-dev \\
  && pip install cryptography \\
  && apk del gcc musl-dev libffi-dev

# Note: Alpine uses musl libc, not glibc
# Some Python packages may have compatibility issues
                ''',
            },
            "scratch": {
                "description": "Empty base image - for statically compiled binaries",
                "examples": '''
# Go with scratch (smallest possible)
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
# Static binary with no external dependencies
RUN CGO_ENABLED=0 GOOS=linux go build \\
    -ldflags="-s -w" \\
    -o /app/main .

FROM scratch
# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
# Copy timezone data if needed
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
# Copy the binary
COPY --from=builder /app/main /main
USER 1000:1000
ENTRYPOINT ["/main"]
# Result: ~10-15MB total

# Rust with scratch
FROM rust:1.70 AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM scratch
COPY --from=builder /app/target/release/myapp /myapp
ENTRYPOINT ["/myapp"]
                ''',
            },
        }

    # =========================================================================
    # DOCKER COMPOSE BEST PRACTICES
    # =========================================================================

    @staticmethod
    def compose_best_practices() -> Dict[str, Any]:
        """Docker Compose best practices"""
        return {
            "healthchecks": {
                "bad": '''
# BAD: No health checks
services:
  api:
    image: myapi:latest
    ports:
      - "8080:8080"
                ''',
                "good": '''
# GOOD: Health checks for all services
services:
  api:
    image: myapi:latest
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
                ''',
            },
            "resource_limits": '''
# GOOD: Resource limits
services:
  api:
    image: myapi:latest
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
            ''',
            "secrets_management": '''
# GOOD: Use Docker secrets (not env vars for sensitive data)
services:
  api:
    image: myapi:latest
    secrets:
      - db_password
      - api_key
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password
      API_KEY_FILE: /run/secrets/api_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt

# Or external secrets (Docker Swarm)
secrets:
  db_password:
    external: true
            ''',
            "profiles": '''
# GOOD: Use profiles for optional services
services:
  api:
    image: myapi:latest
    # Always starts

  db:
    image: postgres:15
    # Always starts

  # Debug tools - only with profile
  adminer:
    image: adminer
    profiles:
      - debug
    ports:
      - "8081:8080"

  mailhog:
    image: mailhog/mailhog
    profiles:
      - debug
    ports:
      - "1025:1025"
      - "8025:8025"

# Start without debug: docker compose up
# Start with debug:    docker compose --profile debug up
            ''',
            "networking": '''
# GOOD: Explicit networks
services:
  frontend:
    image: nginx:alpine
    networks:
      - frontend

  api:
    image: myapi:latest
    networks:
      - frontend
      - backend

  db:
    image: postgres:15
    networks:
      - backend  # Not accessible from frontend!

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
            ''',
        }

    # =========================================================================
    # RUNTIME SECURITY
    # =========================================================================

    @staticmethod
    def runtime_security() -> Dict[str, Any]:
        """Container runtime security"""
        return {
            "seccomp": {
                "description": "Limit syscalls",
                "good": '''
# Run with seccomp profile
docker run --security-opt seccomp=default.json myapp:latest

# Default Docker seccomp blocks dangerous syscalls like:
# - mount, umount
# - reboot
# - module loading
# - many others

# Custom seccomp profile
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "stat", "fstat", ...],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
                ''',
            },
            "apparmor": {
                "description": "Mandatory Access Control",
                "good": '''
# Run with AppArmor profile
docker run --security-opt apparmor=myprofile myapp:latest

# Example AppArmor profile
#include <tunables/global>

profile myapp flags=(attach_disconnected) {
  #include <abstractions/base>

  # Allow read-only access to /etc
  /etc/** r,

  # Allow read-write to app directory
  /app/** rw,

  # Deny access to sensitive paths
  deny /proc/** w,
  deny /sys/** w,

  # Network permissions
  network inet tcp,
  network inet udp,
}
                ''',
            },
            "capabilities": {
                "description": "Drop unnecessary Linux capabilities",
                "bad": '''
# BAD: Running with all capabilities
docker run --privileged myapp:latest
                ''',
                "good": '''
# GOOD: Drop all capabilities, add only needed
docker run \\
  --cap-drop ALL \\
  --cap-add NET_BIND_SERVICE \\  # Only if binding to ports < 1024
  myapp:latest

# Common capabilities to drop (and keep only if needed):
# - NET_RAW: Raw sockets (ping, packet capture)
# - SYS_ADMIN: Many admin operations
# - SYS_PTRACE: Process tracing
# - NET_ADMIN: Network configuration
# - SYS_MODULE: Load kernel modules

# In Dockerfile - don't need NET_BIND_SERVICE if using high port
EXPOSE 8080  # Use 8080 instead of 80
                ''',
            },
            "read_only_filesystem": '''
# GOOD: Read-only root filesystem
docker run \\
  --read-only \\
  --tmpfs /tmp \\
  --tmpfs /var/run \\
  myapp:latest

# In Kubernetes
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    securityContext:
      readOnlyRootFilesystem: true
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: var-run
      mountPath: /var/run
  volumes:
  - name: tmp
    emptyDir: {}
  - name: var-run
    emptyDir: {}
            ''',
            "no_new_privileges": '''
# GOOD: Prevent privilege escalation
docker run \\
  --security-opt no-new-privileges \\
  myapp:latest

# Prevents setuid/setgid binaries from elevating privileges
# Essential security measure
            ''',
        }

    # =========================================================================
    # LOGGING AND MONITORING
    # =========================================================================

    @staticmethod
    def logging_monitoring() -> Dict[str, Any]:
        """Container logging and monitoring best practices"""
        return {
            "logging_drivers": '''
# Available logging drivers
docker run --log-driver json-file myapp:latest  # Default
docker run --log-driver syslog myapp:latest
docker run --log-driver journald myapp:latest
docker run --log-driver fluentd myapp:latest
docker run --log-driver awslogs myapp:latest
docker run --log-driver gcplogs myapp:latest

# JSON file with rotation
docker run \\
  --log-driver json-file \\
  --log-opt max-size=10m \\
  --log-opt max-file=3 \\
  myapp:latest

# Fluentd for centralized logging
docker run \\
  --log-driver fluentd \\
  --log-opt fluentd-address=fluentd.example.com:24224 \\
  --log-opt tag="docker.{{.Name}}" \\
  myapp:latest
            ''',
            "application_logging": '''
# GOOD: Log to stdout/stderr (12-factor app)
# Python
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Node.js
console.log(JSON.stringify({
    level: 'info',
    message: 'Application started',
    timestamp: new Date().toISOString()
}));

# Don't log to files inside container
# BAD: logging to /var/log/app.log
            ''',
            "metrics_export": '''
# Expose Prometheus metrics
FROM python:3.11-slim
RUN pip install prometheus-client

# app.py
from prometheus_client import start_http_server, Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Docker Compose with Prometheus
services:
  app:
    image: myapp:latest
    ports:
      - "8080:8080"
      - "9090:9090"  # Metrics port

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9091:9090"

# prometheus.yml
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['app:9090']
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        current_instruction: str,
        improved_instruction: str,
        size_impact: str = "",
        security_impact: str = "",
    ) -> DockerFinding:
        """Generate a structured finding"""
        return DockerFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            current_instruction=current_instruction,
            improved_instruction=improved_instruction,
            size_impact=size_impact,
            security_impact=security_impact,
            tools=self.get_tool_recommendations(),
            remediation={
                "effort": "LOW" if severity in ["LOW", "MEDIUM"] else "MEDIUM",
                "priority": severity
            },
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for Docker optimization"""
        return [
            {
                "name": "hadolint",
                "command": "hadolint Dockerfile",
                "description": "Dockerfile linter with best practice rules"
            },
            {
                "name": "Trivy",
                "command": "trivy image --severity CRITICAL,HIGH myapp:latest",
                "description": "Vulnerability scanner for container images"
            },
            {
                "name": "Dive",
                "command": "dive myapp:latest",
                "description": "Analyze image layers and size efficiency"
            },
            {
                "name": "Cosign",
                "command": "cosign sign myregistry.io/myapp:latest",
                "description": "Sign and verify container images"
            },
            {
                "name": "Syft",
                "command": "syft myapp:latest -o spdx-json > sbom.json",
                "description": "Generate SBOM for container images"
            },
            {
                "name": "Dockle",
                "command": "dockle myapp:latest",
                "description": "Container image linter for security"
            },
        ]


def create_enhanced_docker_assistant():
    """Factory function to create Enhanced Docker Optimization Assistant"""
    return {
        "name": "Enhanced Docker Optimization Assistant",
        "version": "2.0.0",
        "system_prompt": """You are an expert Docker optimization and security advisor with comprehensive
knowledge of container best practices. Your expertise covers:

IMAGE OPTIMIZATION:
- Multi-stage builds for smaller final images
- Layer caching strategies and optimization
- Base image selection (distroless, alpine, scratch, chainguard)
- Build cache maximization
- Image size reduction techniques

BUILDKIT FEATURES:
- Cache mounts for dependency caching
- Secret mounts for sensitive build data
- SSH mounts for private repository access
- Heredocs for inline file creation
- Parallel stage building

SECURITY:
- Non-root container execution
- Capability dropping and seccomp profiles
- Read-only root filesystem
- Image signing (Cosign, DCT, Notary)
- Vulnerability scanning (Trivy, Grype)
- SBOM generation (Syft, Trivy)
- CIS Docker Benchmark compliance

RUNTIME BEST PRACTICES:
- Health checks configuration
- Resource limits (CPU, memory)
- Logging drivers and configuration
- Network security and isolation
- Secret management

COMPOSE AND ORCHESTRATION:
- Docker Compose best practices
- Service dependencies and health checks
- Network isolation
- Volume management
- Profiles for optional services

Analyze Dockerfiles and container configurations for security issues and optimization opportunities.
Provide before/after examples with size and security impact measurements.

Format findings with severity levels and specific remediation steps.""",
        "assistant_class": EnhancedDockerAssistant,
        "finding_model": DockerFinding,
        "domain": "devops",
        "subdomain": "docker",
        "tags": ["docker", "containers", "security", "optimization", "devops", "buildkit"],
        "tools": EnhancedDockerAssistant.get_tool_recommendations(),
        "capabilities": [
            "dockerfile_optimization",
            "multi_stage_builds",
            "security_scanning",
            "image_signing",
            "sbom_generation",
            "compose_configuration",
            "runtime_security"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedDockerAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate multi-stage builds
    print("--- Multi-Stage Builds ---")
    msb = assistant.multi_stage_builds()
    print("Node.js: 1.2GB -> 250MB with multi-stage")
    print("Go: Full image -> ~10-15MB with scratch")
    print("Python: Use distroless for minimal attack surface")

    # Demonstrate security practices
    print("\n--- Security Best Practices ---")
    sec = assistant.security_practices()
    print("Non-root user: Always run as non-root")
    print("No secrets: Use BuildKit secret mounts")
    print("Minimal packages: Install only what's needed")
    print("Read-only filesystem: Prevent runtime modifications")

    # Show image optimization
    print("\n--- Image Optimization ---")
    opt = assistant.image_optimization()
    print("Layer caching: Copy dependency files first")
    print("Combine commands: Single RUN with cleanup")
    print("Specific tags: Avoid :latest for reproducibility")

    # Show scanning and SBOM
    print("\n--- Scanning and SBOM ---")
    scan = assistant.scanning_sbom()
    print("Trivy: Vulnerability scanning with severity filter")
    print("Syft: SBOM generation in SPDX/CycloneDX format")
    print("Hadolint: Dockerfile linting")

    # Show BuildKit features
    print("\n--- BuildKit Features ---")
    bk = assistant.buildkit_features()
    print("Cache mounts: Cache pip/npm between builds")
    print("Secret mounts: Use secrets without storing in layers")
    print("SSH mounts: Clone private repos securely")
    print("Heredocs: Multi-line scripts in Dockerfile")

    # Show image signing
    print("\n--- Image Signing ---")
    sign = assistant.image_signing()
    print("Cosign: Keyless signing with OIDC")
    print("DCT: Docker Content Trust built-in")
    print("Kyverno: Enforce signatures in Kubernetes")

    # Show minimal images
    print("\n--- Minimal Base Images ---")
    minimal = assistant.minimal_base_images()
    print("Distroless: No shell, minimal attack surface")
    print("Chainguard: Zero CVEs, signed, SBOM included")
    print("Alpine: Small but has shell (~50MB)")
    print("Scratch: Empty, for static binaries (~10MB)")

    # Show compose best practices
    print("\n--- Docker Compose Best Practices ---")
    compose = assistant.compose_best_practices()
    print("Health checks: Proper dependency ordering")
    print("Resource limits: Prevent resource exhaustion")
    print("Secrets: Use Docker secrets, not env vars")
    print("Networks: Isolate frontend from backend")

    # Show runtime security
    print("\n--- Runtime Security ---")
    runtime = assistant.runtime_security()
    print("Seccomp: Limit syscalls")
    print("AppArmor: Mandatory Access Control")
    print("Capabilities: Drop all, add only needed")
    print("no-new-privileges: Prevent escalation")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="DOCKER-001",
        title="Running Container as Root",
        severity="HIGH",
        category="Security",
        current_instruction="FROM nginx:latest\\n# No USER directive",
        improved_instruction="FROM nginx:latest\\nUSER nginx:nginx",
        size_impact="None",
        security_impact="Reduces attack surface by not running as root"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Security Impact: {finding.security_impact}")
    print(f"Remediation: {finding.remediation}")

    # Show tool recommendations
    print("\n--- Tool Recommendations ---")
    tools = assistant.get_tool_recommendations()
    for tool in tools[:4]:
        print(f"\n{tool['name']}:")
        print(f"  Command: {tool['command']}")
        print(f"  Description: {tool['description']}")

    # Show factory function output
    print("\n--- Factory Function ---")
    config = create_enhanced_docker_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
