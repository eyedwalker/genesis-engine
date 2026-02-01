"""
Genesis Engine - Middleware
PII Redaction, Request Logging, Rate Limiting
"""

import re
import time
import uuid
import json
import logging
from typing import Dict, List, Callable
from collections import defaultdict
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("genesis.middleware")


# ---------------------------------------------------------------------------
# PII Redaction Patterns
# ---------------------------------------------------------------------------

PII_PATTERNS: List[tuple[str, str]] = [
    # API keys and secrets
    (r'(?i)(sk-[a-zA-Z0-9]{20,})', '[REDACTED_API_KEY]'),
    (r'(?i)(api[_-]?key\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})', r'\1[REDACTED]'),
    (r'(?i)(secret\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{16,})', r'\1[REDACTED]'),
    (r'(?i)(password\s*[:=]\s*["\']?)([^\s"\']{8,})', r'\1[REDACTED]'),
    (r'(?i)(token\s*[:=]\s*["\']?)([a-zA-Z0-9_\-\.]{20,})', r'\1[REDACTED]'),

    # AWS keys
    (r'(AKIA[A-Z0-9]{16})', '[REDACTED_AWS_KEY]'),
    (r'(?i)(aws_secret_access_key\s*[:=]\s*["\']?)([a-zA-Z0-9/+=]{40})', r'\1[REDACTED]'),

    # Credit card numbers (basic patterns)
    (r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b', '[REDACTED_CARD]'),

    # SSN
    (r'\b(\d{3}-\d{2}-\d{4})\b', '[REDACTED_SSN]'),

    # Email addresses in code (not in user profile fields)
    (r'(?i)(?:password|secret|key).*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', '[REDACTED_EMAIL]'),

    # JWT tokens
    (r'(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})', '[REDACTED_JWT]'),

    # Private keys
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC )?PRIVATE KEY-----', '[REDACTED_PRIVATE_KEY]'),

    # Connection strings
    (r'(?i)((?:postgres|mysql|mongodb|redis)://)[^\s"\']+', r'\1[REDACTED_CONNECTION_STRING]'),
]


def redact_pii(text: str) -> str:
    """Redact PII from text before sending to LLM"""
    if not text:
        return text

    result = text
    for pattern, replacement in PII_PATTERNS:
        result = re.sub(pattern, replacement, result)

    return result


def redact_dict(data: Dict) -> Dict:
    """Recursively redact PII from dictionary values"""
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = redact_pii(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value)
        elif isinstance(value, list):
            result[key] = [
                redact_dict(item) if isinstance(item, dict)
                else redact_pii(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value

    return result


# ---------------------------------------------------------------------------
# PII Redaction Middleware
# ---------------------------------------------------------------------------

class PIIRedactionMiddleware(BaseHTTPMiddleware):
    """Middleware to redact PII from request/response bodies for LLM endpoints"""

    LLM_ENDPOINTS = {"/api/review/ai", "/api/fix", "/api/factories/plan"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only intercept LLM-bound requests
        if request.url.path in self.LLM_ENDPOINTS and request.method == "POST":
            # Read and redact request body
            body = await request.body()
            if body:
                try:
                    data = json.loads(body)
                    redacted = redact_dict(data)
                    # Store redacted body for the endpoint to use
                    request.state.redacted_body = redacted
                except (json.JSONDecodeError, AttributeError):
                    pass

        response = await call_next(request)
        return response


# ---------------------------------------------------------------------------
# Request Logging Middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing for usage metering"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = uuid.uuid4().hex[:8]
        start_time = time.time()

        # Extract tenant info if available
        tenant_id = "unknown"
        if hasattr(request.state, 'user'):
            tenant_id = getattr(request.state.user, 'tenant_id', 'unknown')

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({duration_ms:.1f}ms) "
            f"tenant={tenant_id}"
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        return response


# ---------------------------------------------------------------------------
# Rate Limiting Middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter per tenant/IP"""

    # Requests per minute by plan
    PLAN_LIMITS = {
        "free": 60,
        "pro": 300,
        "enterprise": 1000,
    }

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks and static assets
        if request.url.path in ("/health", "/", "/docs", "/openapi.json"):
            return await call_next(request)

        # Identify the caller
        client_ip = request.client.host if request.client else "unknown"
        tenant_id = "default"

        # Get plan limit (default to free)
        limit = self.PLAN_LIMITS["free"]

        key = f"{tenant_id}:{client_ip}"
        now = time.time()
        window = 60.0  # 1 minute window

        # Clean old entries
        self.requests[key] = [
            t for t in self.requests[key] if now - t < window
        ]

        if len(self.requests[key]) >= limit:
            return Response(
                content=json.dumps({"detail": "Rate limit exceeded. Try again shortly."}),
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                }
            )

        self.requests[key].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - len(self.requests[key]))

        return response
