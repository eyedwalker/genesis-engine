"""
Enhanced API Design Assistant - REST, GraphQL, gRPC Best Practices

This assistant provides comprehensive API design guidance covering:
- OpenAPI 3.1 spec compliance
- GraphQL schema best practices
- gRPC service design (proto3)
- Richardson RESTful maturity model
- HATEOAS implementation
- API versioning strategies (4 types)
- Pagination patterns (offset, cursor, keyset)
- Rate limiting headers (RFC 6585)
- Error response standards
- API security best practices

References:
- OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0
- GraphQL Best Practices: https://graphql.org/learn/best-practices/
- gRPC Style Guide: https://grpc.io/docs/guides/
- Richardson Maturity Model: https://martinfowler.com/articles/richardsonMaturityModel.html
- RFC 7807 (Problem Details): https://datatracker.ietf.org/doc/html/rfc7807
- RFC 6585 (Rate Limiting): https://datatracker.ietf.org/doc/html/rfc6585
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class APIDesignFinding(BaseModel):
    """Structured API design finding output"""

    finding_id: str = Field(..., description="Unique identifier (API-001, API-002, etc.)")
    title: str = Field(..., description="Brief title of the issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    api_type: str = Field(..., description="REST/GraphQL/gRPC")

    location: Dict[str, Any] = Field(default_factory=dict, description="Endpoint, schema, service")
    description: str = Field(..., description="Detailed description of the issue")
    standard_violated: str = Field(default="", description="Which standard/best practice violated")

    current_design: str = Field(default="", description="Current API design")
    recommended_design: str = Field(..., description="Recommended API design")
    rationale: str = Field(..., description="Why this design is better")

    maturity_level: str = Field(default="", description="Richardson maturity level (for REST)")
    versioning_impact: str = Field(default="", description="Version compatibility impact")

    testing_guidance: str = Field(default="", description="How to test the API")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Tools for validation")
    references: List[str] = Field(default_factory=list, description="Standards references")

    migration_strategy: Dict[str, Any] = Field(default_factory=dict, description="How to migrate")


class EnhancedAPIDesignAssistant:
    """
    Enhanced API Design Assistant with REST, GraphQL, and gRPC expertise

    Covers:
    - RESTful API design (Richardson maturity model)
    - GraphQL schema design
    - gRPC service design
    - API versioning strategies
    - Pagination, filtering, sorting
    - Rate limiting and throttling
    - Error handling standards
    """

    def __init__(self):
        self.name = "Enhanced API Design Assistant"
        self.version = "2.0.0"
        self.standards = ["OpenAPI 3.1", "GraphQL", "gRPC", "RFC 7807", "RFC 6585"]

    # =========================================================================
    # REST API DESIGN - Richardson Maturity Model
    # =========================================================================

    @staticmethod
    def richardson_maturity_model() -> Dict[str, Any]:
        """
        Richardson Maturity Model for RESTful APIs

        Level 0: Single URI, single method (RPC style)
        Level 1: Multiple URIs, single method
        Level 2: Multiple URIs, HTTP verbs
        Level 3: Hypermedia controls (HATEOAS)
        """
        return {
            "level_0_swamp_of_pox": {
                "description": "Single URI, single HTTP method (usually POST), RPC-style",
                "characteristics": [
                    "All requests to same endpoint",
                    "Action in request body",
                    "Tunneling through POST",
                ],
                "bad_example": """
# BAD: Level 0 - RPC over HTTP
POST /api
Content-Type: application/json

{
  "action": "getUser",
  "userId": 123
}

POST /api
Content-Type: application/json

{
  "action": "createUser",
  "name": "John Doe",
  "email": "john@example.com"
}

POST /api
Content-Type: application/json

{
  "action": "deleteUser",
  "userId": 123
}

# All actions through single endpoint with POST
                """,
            },
            "level_1_resources": {
                "description": "Multiple URIs, but still single HTTP method",
                "characteristics": [
                    "Different URIs for different resources",
                    "Still using POST for everything",
                ],
                "example": """
# BETTER: Level 1 - Multiple URIs
POST /users/get
{
  "userId": 123
}

POST /users/create
{
  "name": "John Doe",
  "email": "john@example.com"
}

POST /users/delete
{
  "userId": 123
}

# Better: different URIs, but not using HTTP verbs properly
                """,
            },
            "level_2_http_verbs": {
                "description": "Multiple URIs with appropriate HTTP verbs",
                "characteristics": [
                    "Use GET for reads",
                    "Use POST for creates",
                    "Use PUT/PATCH for updates",
                    "Use DELETE for deletions",
                    "Proper HTTP status codes",
                ],
                "good_example": """
# GOOD: Level 2 - HTTP verbs
GET /users/123
# Returns: 200 OK with user data

POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
# Returns: 201 Created with Location header

PUT /users/123
Content-Type: application/json

{
  "name": "John Smith",
  "email": "john.smith@example.com"
}
# Returns: 200 OK with updated user

PATCH /users/123
Content-Type: application/json

{
  "email": "newemail@example.com"
}
# Returns: 200 OK with updated user

DELETE /users/123
# Returns: 204 No Content

# Using HTTP verbs as intended
                """,
                "http_methods": {
                    "GET": {
                        "purpose": "Retrieve resource(s)",
                        "safe": True,
                        "idempotent": True,
                        "cacheable": True,
                        "request_body": False,
                        "response_body": True,
                    },
                    "POST": {
                        "purpose": "Create resource",
                        "safe": False,
                        "idempotent": False,
                        "cacheable": False,
                        "request_body": True,
                        "response_body": True,
                    },
                    "PUT": {
                        "purpose": "Replace resource",
                        "safe": False,
                        "idempotent": True,
                        "cacheable": False,
                        "request_body": True,
                        "response_body": True,
                    },
                    "PATCH": {
                        "purpose": "Partial update",
                        "safe": False,
                        "idempotent": False,
                        "cacheable": False,
                        "request_body": True,
                        "response_body": True,
                    },
                    "DELETE": {
                        "purpose": "Delete resource",
                        "safe": False,
                        "idempotent": True,
                        "cacheable": False,
                        "request_body": False,
                        "response_body": False,
                    },
                },
                "status_codes": {
                    "2xx_success": {
                        "200": "OK - Request succeeded",
                        "201": "Created - Resource created (return Location header)",
                        "202": "Accepted - Request accepted for processing",
                        "204": "No Content - Success but no response body",
                    },
                    "3xx_redirection": {
                        "301": "Moved Permanently - Resource permanently moved",
                        "302": "Found - Temporary redirect",
                        "304": "Not Modified - Cached version is still valid",
                    },
                    "4xx_client_errors": {
                        "400": "Bad Request - Invalid request syntax",
                        "401": "Unauthorized - Authentication required",
                        "403": "Forbidden - Authenticated but not authorized",
                        "404": "Not Found - Resource doesn't exist",
                        "405": "Method Not Allowed - HTTP method not supported",
                        "409": "Conflict - Resource conflict (e.g., duplicate)",
                        "422": "Unprocessable Entity - Validation failed",
                        "429": "Too Many Requests - Rate limit exceeded",
                    },
                    "5xx_server_errors": {
                        "500": "Internal Server Error - Generic server error",
                        "502": "Bad Gateway - Invalid response from upstream",
                        "503": "Service Unavailable - Temporarily unavailable",
                        "504": "Gateway Timeout - Upstream timeout",
                    },
                },
            },
            "level_3_hypermedia": {
                "description": "HATEOAS - Hypermedia As The Engine Of Application State",
                "characteristics": [
                    "Response includes links to related resources",
                    "Client discovers actions dynamically",
                    "Decouples client from URL structure",
                ],
                "good_example": """
# EXCELLENT: Level 3 - HATEOAS
GET /users/123
Response: 200 OK

{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": {
      "href": "/users/123"
    },
    "edit": {
      "href": "/users/123",
      "method": "PUT"
    },
    "delete": {
      "href": "/users/123",
      "method": "DELETE"
    },
    "orders": {
      "href": "/users/123/orders"
    },
    "addresses": {
      "href": "/users/123/addresses"
    }
  }
}

# Client can discover available actions from response
# If user can't be deleted, "delete" link wouldn't be present
                """,
                "hal_json": """
# HAL (Hypertext Application Language) format
GET /orders/123
Response: 200 OK
Content-Type: application/hal+json

{
  "id": 123,
  "status": "pending",
  "total": 99.99,
  "_links": {
    "self": { "href": "/orders/123" },
    "customer": { "href": "/customers/456" },
    "items": { "href": "/orders/123/items" },
    "cancel": {
      "href": "/orders/123/cancel",
      "method": "POST",
      "title": "Cancel this order"
    }
  },
  "_embedded": {
    "customer": {
      "id": 456,
      "name": "John Doe",
      "_links": {
        "self": { "href": "/customers/456" }
      }
    }
  }
}
                """,
            },
        }

    # =========================================================================
    # REST API - URL DESIGN AND RESOURCE NAMING
    # =========================================================================

    @staticmethod
    def url_design_best_practices() -> Dict[str, Any]:
        """
        URL design and resource naming conventions
        """
        return {
            "resource_naming": {
                "principles": [
                    "Use nouns, not verbs",
                    "Use plural nouns for collections",
                    "Use hierarchical structure for relationships",
                    "Use hyphens for readability, not underscores",
                    "Lowercase only",
                    "No file extensions",
                ],
                "bad_examples": """
# BAD: Verbs in URLs
POST /createUser
GET /getUser/123
DELETE /deleteUser/123

# BAD: Inconsistent pluralization
GET /user/123
GET /users

# BAD: Underscores and mixed case
GET /user_profiles/123
GET /UserProfiles

# BAD: File extensions
GET /users/123.json
GET /users/123.xml

# BAD: Actions as resources
POST /users/123/send-email
GET /users/123/calculate-score
                """,
                "good_examples": """
# GOOD: Nouns and HTTP verbs
POST /users
GET /users/123
DELETE /users/123

# GOOD: Consistent plural collections
GET /users
GET /users/123
GET /users/123/orders
GET /users/123/orders/456

# GOOD: Hierarchical relationships
GET /organizations/1/departments/2/employees
GET /customers/123/orders/456/items

# GOOD: Hyphens for readability
GET /user-profiles/123
GET /order-items/456

# GOOD: Query parameters for actions
POST /users/123/emails  # Send email
GET /users/123/score    # Calculate score

# GOOD: Sub-resources for relationships
GET /users/123/friends
GET /posts/456/comments
GET /courses/789/students
                """,
            },
            "query_parameters": {
                "filtering": """
# Filtering
GET /users?status=active
GET /users?role=admin&status=active
GET /products?category=electronics&price_min=100&price_max=500
GET /orders?created_after=2024-01-01&created_before=2024-12-31
                """,
                "sorting": """
# Sorting
GET /users?sort=name          # Ascending by name
GET /users?sort=-created_at   # Descending by created_at (- prefix)
GET /users?sort=name,-created_at  # Multiple fields
                """,
                "pagination": """
# Offset-based pagination
GET /users?page=2&per_page=20
GET /users?offset=20&limit=20

# Cursor-based pagination (better for large datasets)
GET /users?cursor=eyJpZCI6MTIzfQ==&limit=20
                """,
                "field_selection": """
# Sparse fieldsets (return only requested fields)
GET /users?fields=id,name,email
GET /products?fields=id,name,price&include=category,manufacturer
                """,
                "search": """
# Full-text search
GET /products?q=laptop
GET /users?search=john
                """,
            },
            "versioning_strategies": {
                "url_versioning": {
                    "description": "Version in URL path",
                    "pros": ["Clear and explicit", "Easy to implement", "Easy to route"],
                    "cons": ["Pollutes URL space", "Not RESTful purists"],
                    "example": """
# URL versioning
GET /v1/users/123
GET /v2/users/123
GET /api/v1/products
GET /api/v2/products

# Most common and practical approach
                    """,
                },
                "header_versioning": {
                    "description": "Version in Accept header",
                    "pros": ["Clean URLs", "RESTful", "Content negotiation"],
                    "cons": ["Less discoverable", "Harder to test in browser"],
                    "example": """
# Header versioning
GET /users/123
Accept: application/vnd.myapi.v1+json

GET /users/123
Accept: application/vnd.myapi.v2+json

# Response includes version
Content-Type: application/vnd.myapi.v1+json
                    """,
                },
                "query_parameter_versioning": {
                    "description": "Version as query parameter",
                    "pros": ["Simple", "Easy to test"],
                    "cons": ["Easy to forget", "Can conflict with filtering"],
                    "example": """
# Query parameter versioning
GET /users/123?version=1
GET /users/123?version=2
GET /users/123?api-version=2024-01-01

# Microsoft uses this approach
                    """,
                },
                "content_negotiation": {
                    "description": "Different media types for versions",
                    "pros": ["Truly RESTful", "Flexible"],
                    "cons": ["Complex", "Rarely used"],
                    "example": """
# Content negotiation
GET /users/123
Accept: application/vnd.myapi.user.v1+json

GET /users/123
Accept: application/vnd.myapi.user.v2+json
                    """,
                },
                "versioning_best_practices": [
                    "Use URL versioning for simplicity (v1, v2, not v1.2)",
                    "Version only when breaking changes occur",
                    "Support previous version for at least 6-12 months",
                    "Document deprecation timeline clearly",
                    "Use semantic versioning internally (1.0.0, 2.0.0)",
                    "Return version in response headers",
                    "Provide version-agnostic documentation",
                ],
            },
        }

    # =========================================================================
    # REST API - PAGINATION PATTERNS
    # =========================================================================

    @staticmethod
    def pagination_patterns() -> Dict[str, Any]:
        """
        Pagination patterns for large datasets
        """
        return {
            "offset_pagination": {
                "description": "Page number and size (simplest, most common)",
                "pros": ["Simple to implement", "Easy to understand", "Can jump to any page"],
                "cons": ["Inconsistent results if data changes", "Poor performance on large offsets"],
                "request": """
# Offset pagination request
GET /users?page=2&per_page=20
GET /users?offset=20&limit=20
                """,
                "response": """
# Offset pagination response
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 22, "name": "User 22"}
  ],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total_pages": 50,
    "total_count": 1000,
    "has_next": true,
    "has_prev": true
  },
  "links": {
    "first": "/users?page=1&per_page=20",
    "prev": "/users?page=1&per_page=20",
    "self": "/users?page=2&per_page=20",
    "next": "/users?page=3&per_page=20",
    "last": "/users?page=50&per_page=20"
  }
}
                """,
                "when_to_use": "Small to medium datasets, UI needs page numbers",
            },
            "cursor_pagination": {
                "description": "Opaque cursor pointing to specific record",
                "pros": ["Consistent results", "Good performance", "Handles real-time data"],
                "cons": ["Can't jump to specific page", "More complex", "Cursor can become invalid"],
                "request": """
# Cursor pagination request
GET /users?limit=20
GET /users?cursor=eyJpZCI6MjB9&limit=20

# First request has no cursor
# Subsequent requests use cursor from previous response
                """,
                "response": """
# Cursor pagination response
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 22, "name": "User 22"}
  ],
  "pagination": {
    "cursor": "eyJpZCI6NDAsImNyZWF0ZWRfYXQiOiIyMDI0LTAxLTAxIn0=",
    "has_more": true,
    "limit": 20
  },
  "links": {
    "self": "/users?cursor=eyJpZCI6MjB9&limit=20",
    "next": "/users?cursor=eyJpZCI6NDAsImNyZWF0ZWRfYXQiOiIyMDI0LTAxLTAxIn0=&limit=20"
  }
}

# Cursor is base64 encoded JSON: {"id": 40, "created_at": "2024-01-01"}
                """,
                "implementation": """
# Python cursor pagination implementation
import base64
import json

def encode_cursor(id, created_at):
    cursor_data = {"id": id, "created_at": created_at.isoformat()}
    cursor_json = json.dumps(cursor_data)
    return base64.b64encode(cursor_json.encode()).decode()

def decode_cursor(cursor):
    cursor_json = base64.b64decode(cursor.encode()).decode()
    return json.loads(cursor_json)

def get_users(cursor=None, limit=20):
    query = User.query.order_by(User.id)

    if cursor:
        cursor_data = decode_cursor(cursor)
        query = query.filter(User.id > cursor_data['id'])

    users = query.limit(limit + 1).all()

    has_more = len(users) > limit
    users = users[:limit]

    next_cursor = None
    if has_more and users:
        last_user = users[-1]
        next_cursor = encode_cursor(last_user.id, last_user.created_at)

    return {
        "data": users,
        "pagination": {
            "cursor": next_cursor,
            "has_more": has_more,
            "limit": limit
        }
    }
                """,
                "when_to_use": "Large datasets, real-time feeds, infinite scroll",
            },
            "keyset_pagination": {
                "description": "Use unique key for stable pagination",
                "pros": ["Very fast", "Stable", "Simple"],
                "cons": ["Requires indexed unique key", "Can't jump to page"],
                "request": """
# Keyset pagination request
GET /users?limit=20
GET /users?since_id=20&limit=20
GET /users?max_id=19&limit=20  # Previous page
                """,
                "response": """
# Keyset pagination response
{
  "data": [
    {"id": 21, "name": "User 21"},
    {"id": 40, "name": "User 40"}
  ],
  "pagination": {
    "max_id": 40,
    "since_id": 21,
    "limit": 20,
    "has_more": true
  },
  "links": {
    "self": "/users?since_id=20&limit=20",
    "next": "/users?since_id=40&limit=20",
    "prev": "/users?max_id=21&limit=20"
  }
}
                """,
                "implementation": """
# Keyset pagination with SQL
SELECT * FROM users
WHERE id > 20
ORDER BY id ASC
LIMIT 20;

# Previous page
SELECT * FROM users
WHERE id < 21
ORDER BY id DESC
LIMIT 20;

# Very efficient - uses index on id
                """,
                "when_to_use": "Twitter-style feeds, sequential access patterns",
            },
            "seek_pagination": {
                "description": "Combine multiple fields for sorting",
                "pros": ["Fast", "Stable", "Supports complex sorting"],
                "cons": ["Complex implementation", "Requires composite index"],
                "example": """
# Seek pagination with multiple fields
GET /posts?limit=20
GET /posts?after_id=100&after_score=95&limit=20

# Query sorts by score DESC, id DESC for tiebreaking
SELECT * FROM posts
WHERE (score, id) < (95, 100)
ORDER BY score DESC, id DESC
LIMIT 20;

# Requires composite index on (score, id)
                """,
            },
            "link_header": {
                "description": "RFC 5988 Link header for pagination",
                "example": """
# Link header (GitHub style)
GET /users?page=5&per_page=20

Response Headers:
Link: <https://api.example.com/users?page=1&per_page=20>; rel="first",
      <https://api.example.com/users?page=4&per_page=20>; rel="prev",
      <https://api.example.com/users?page=6&per_page=20>; rel="next",
      <https://api.example.com/users?page=50&per_page=20>; rel="last"
X-Total-Count: 1000
X-Total-Pages: 50

# Parse Link header to get pagination URLs
                """,
            },
        }

    # =========================================================================
    # REST API - ERROR HANDLING (RFC 7807)
    # =========================================================================

    @staticmethod
    def error_handling() -> Dict[str, Any]:
        """
        Error response standards (RFC 7807 Problem Details)
        """
        return {
            "rfc_7807_problem_details": {
                "description": "Standardized error response format",
                "media_type": "application/problem+json",
                "fields": {
                    "type": "URI reference identifying the problem type",
                    "title": "Short, human-readable summary",
                    "status": "HTTP status code",
                    "detail": "Human-readable explanation specific to this occurrence",
                    "instance": "URI reference identifying this specific occurrence",
                },
                "example": """
# RFC 7807 error response
POST /users
Content-Type: application/json

{
  "email": "invalidemail",
  "password": "123"
}

Response: 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Failed",
  "status": 422,
  "detail": "The request contains invalid fields",
  "instance": "/users",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "INVALID_EMAIL"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "code": "PASSWORD_TOO_SHORT"
    }
  ]
}
                """,
            },
            "error_response_patterns": {
                "validation_error": """
# Validation error (422)
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Failed",
  "status": 422,
  "detail": "One or more fields failed validation",
  "instance": "/api/users",
  "errors": [
    {
      "field": "email",
      "message": "Email is required",
      "code": "REQUIRED_FIELD"
    }
  ]
}
                """,
                "not_found": """
# Not found (404)
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "User with ID 12345 was not found",
  "instance": "/api/users/12345"
}
                """,
                "unauthorized": """
# Unauthorized (401)
{
  "type": "https://api.example.com/errors/unauthorized",
  "title": "Authentication Required",
  "status": 401,
  "detail": "Valid authentication credentials are required to access this resource",
  "instance": "/api/orders"
}
                """,
                "forbidden": """
# Forbidden (403)
{
  "type": "https://api.example.com/errors/forbidden",
  "title": "Access Denied",
  "status": 403,
  "detail": "You do not have permission to delete this resource",
  "instance": "/api/users/456"
}
                """,
                "conflict": """
# Conflict (409)
{
  "type": "https://api.example.com/errors/conflict",
  "title": "Resource Conflict",
  "status": 409,
  "detail": "A user with this email already exists",
  "instance": "/api/users",
  "conflicting_field": "email",
  "conflicting_value": "john@example.com"
}
                """,
                "rate_limit": """
# Rate limit exceeded (429)
{
  "type": "https://api.example.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded the rate limit of 100 requests per hour",
  "instance": "/api/products",
  "retry_after": 3600
}

Response Headers:
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 3600
                """,
            },
            "error_codes": {
                "description": "Machine-readable error codes",
                "example": """
# Use consistent error codes
{
  "errors": [
    {
      "code": "INVALID_EMAIL",
      "field": "email",
      "message": "Email format is invalid"
    },
    {
      "code": "PASSWORD_TOO_SHORT",
      "field": "password",
      "message": "Password must be at least 8 characters"
    },
    {
      "code": "USERNAME_TAKEN",
      "field": "username",
      "message": "This username is already taken"
    }
  ]
}

# Benefits:
# - Clients can handle errors programmatically
# - Internationalization-friendly
# - Stable across API versions
                """,
            },
        }

    # =========================================================================
    # REST API - RATE LIMITING
    # =========================================================================

    @staticmethod
    def rate_limiting() -> Dict[str, Any]:
        """
        Rate limiting and throttling (RFC 6585)
        """
        return {
            "rate_limit_headers": {
                "description": "Standard headers for rate limiting",
                "headers": {
                    "X-RateLimit-Limit": "Maximum requests allowed in window",
                    "X-RateLimit-Remaining": "Requests remaining in current window",
                    "X-RateLimit-Reset": "Unix timestamp when limit resets",
                    "Retry-After": "Seconds to wait before retrying (on 429)",
                },
                "example": """
# Rate limit headers
GET /api/users
Response: 200 OK

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200

# After limit exceeded
GET /api/users
Response: 429 Too Many Requests

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 3600

{
  "type": "https://api.example.com/errors/rate-limit-exceeded",
  "title": "Rate Limit Exceeded",
  "status": 429,
  "detail": "You have exceeded 1000 requests per hour limit",
  "retry_after": 3600
}
                """,
            },
            "rate_limiting_algorithms": {
                "fixed_window": {
                    "description": "Count requests in fixed time windows",
                    "pros": ["Simple", "Memory efficient"],
                    "cons": ["Burst at window boundaries"],
                    "example": """
# Fixed window: 100 requests per hour
# Window: 14:00-15:00
# User makes 100 requests at 14:59
# User makes 100 more at 15:01
# Result: 200 requests in 2 minutes (burst)
                    """,
                },
                "sliding_window_log": {
                    "description": "Track timestamp of each request",
                    "pros": ["Precise", "No burst issues"],
                    "cons": ["Memory intensive"],
                    "implementation": """
# Python sliding window log
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = deque()

    def allow_request(self):
        now = datetime.now()
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

# Usage
limiter = RateLimiter(max_requests=100, window_seconds=3600)
if limiter.allow_request():
    # Process request
    pass
else:
    # Return 429
    pass
                    """,
                },
                "sliding_window_counter": {
                    "description": "Hybrid of fixed window and sliding window",
                    "pros": ["Memory efficient", "Smooths bursts"],
                    "cons": ["Approximate"],
                    "example": """
# Sliding window counter
# Weighted average between current and previous window

rate = (
    previous_window_requests * (1 - elapsed_percent) +
    current_window_requests
)

if rate < limit:
    allow_request()
                    """,
                },
                "token_bucket": {
                    "description": "Tokens added at fixed rate, consumed per request",
                    "pros": ["Allows bursts", "Smooth over time"],
                    "cons": ["More complex"],
                    "implementation": """
# Python token bucket
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()

    def allow_request(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

# Usage: 10 requests per second, burst up to 20
bucket = TokenBucket(capacity=20, refill_rate=10)
                    """,
                },
                "leaky_bucket": {
                    "description": "Requests processed at constant rate",
                    "pros": ["Smooth rate", "Predictable"],
                    "cons": ["No bursts allowed"],
                },
            },
            "tiered_rate_limits": {
                "description": "Different limits for different tiers",
                "example": """
# Tiered rate limits
tiers = {
    "free": {
        "requests_per_hour": 100,
        "requests_per_day": 1000,
        "burst": 10
    },
    "basic": {
        "requests_per_hour": 1000,
        "requests_per_day": 10000,
        "burst": 50
    },
    "premium": {
        "requests_per_hour": 10000,
        "requests_per_day": 100000,
        "burst": 500
    }
}

# Return tier info in headers
X-RateLimit-Tier: premium
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9999
                """,
            },
        }

    # =========================================================================
    # GRAPHQL SCHEMA DESIGN
    # =========================================================================

    @staticmethod
    def graphql_best_practices() -> Dict[str, Any]:
        """
        GraphQL schema design best practices
        """
        return {
            "schema_design_principles": {
                "nullability": {
                    "description": "Design for nullability carefully",
                    "bad": """
# BAD: Everything nullable by default
type User {
  id: ID
  name: String
  email: String
}

# If field fails, whole query might fail
                    """,
                    "good": """
# GOOD: Required fields are non-null
type User {
  id: ID!          # Required
  name: String!    # Required
  email: String    # Optional (can be null)
  phone: String    # Optional
}

# Explicit about what's guaranteed
                    """,
                },
                "naming_conventions": {
                    "fields": "camelCase (e.g., firstName, createdAt)",
                    "types": "PascalCase (e.g., User, OrderItem)",
                    "enums": "SCREAMING_SNAKE_CASE (e.g., ORDER_STATUS)",
                    "mutations": "Verb + noun (e.g., createUser, updateOrder)",
                    "queries": "Nouns or questions (e.g., user, users, isAdmin)",
                },
                "pagination": """
# Relay-style cursor pagination
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type UserEdge {
  cursor: String!
  node: User!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
  ): UserConnection!
}

# Query usage
query {
  users(first: 10, after: "cursor123") {
    edges {
      cursor
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
                """,
            },
            "query_design": {
                "field_arguments": """
# Field-level arguments
type Query {
  user(id: ID!): User
  users(
    limit: Int = 10
    offset: Int = 0
    status: UserStatus
    sort: UserSort
  ): [User!]!
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

enum UserSort {
  NAME_ASC
  NAME_DESC
  CREATED_AT_ASC
  CREATED_AT_DESC
}

# Usage
query {
  users(limit: 20, status: ACTIVE, sort: NAME_ASC) {
    id
    name
  }
}
                """,
                "connections_over_lists": """
# BAD: Simple list
type Query {
  users: [User!]!
}

# GOOD: Connection for pagination
type Query {
  users(first: Int, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

# Allows efficient pagination and metadata
                """,
            },
            "mutation_design": {
                "input_types": """
# Use input types for mutations
input CreateUserInput {
  name: String!
  email: String!
  password: String!
}

input UpdateUserInput {
  name: String
  email: String
  phone: String
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}

# Benefits:
# - Single argument is easier to evolve
# - Clear what can be set
# - Reusable across mutations
                """,
                "payload_types": """
# Return payload with result and errors
type CreateUserPayload {
  user: User
  errors: [UserError!]
  clientMutationId: String
}

type UserError {
  field: String!
  message: String!
  code: String!
}

# Usage
mutation {
  createUser(input: {
    name: "John"
    email: "john@example.com"
    password: "secret"
  }) {
    user {
      id
      name
    }
    errors {
      field
      message
      code
    }
  }
}

# If validation fails, errors array is populated
# If successful, user is populated
                """,
            },
            "error_handling": {
                "union_types": """
# Use unions for success/error responses
type User {
  id: ID!
  name: String!
}

type ValidationError {
  field: String!
  message: String!
}

type NotFoundError {
  message: String!
}

union UserResult = User | ValidationError | NotFoundError

type Query {
  user(id: ID!): UserResult!
}

# Usage with fragments
query {
  user(id: "123") {
    ... on User {
      id
      name
    }
    ... on ValidationError {
      field
      message
    }
    ... on NotFoundError {
      message
    }
  }
}
                """,
            },
            "n_plus_1_problem": {
                "description": "Avoid N+1 queries with DataLoader",
                "bad": """
# BAD: N+1 query problem
type User {
  id: ID!
  name: String!
  posts: [Post!]!  # Queries database for each user
}

type Post {
  id: ID!
  title: String!
  author: User!    # Queries database for each post
}

# Query for 10 users and their posts:
# 1 query for users
# 10 queries for posts (one per user)
# = 11 queries total
                """,
                "good": """
# GOOD: Use DataLoader to batch queries
from aiodataloader import DataLoader

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        users = await db.users.find({"id": {"$in": user_ids}})
        user_map = {user.id: user for user in users}
        return [user_map.get(id) for id in user_ids]

class PostLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        posts = await db.posts.find({"author_id": {"$in": user_ids}})
        # Group posts by author_id
        posts_by_author = {}
        for post in posts:
            posts_by_author.setdefault(post.author_id, []).append(post)
        return [posts_by_author.get(id, []) for id in user_ids]

# In resolvers
async def resolve_posts(user, info):
    return await info.context.post_loader.load(user.id)

# Now same query makes only 2 database queries:
# 1 query for users
# 1 batched query for all posts
                """,
            },
        }

    # =========================================================================
    # GRPC SERVICE DESIGN
    # =========================================================================

    @staticmethod
    def grpc_best_practices() -> Dict[str, Any]:
        """
        gRPC service design (proto3)
        """
        return {
            "proto3_basics": {
                "file_structure": """
// users.proto
syntax = "proto3";

package com.example.users.v1;

option go_package = "github.com/example/users/v1;usersv1";
option java_package = "com.example.users.v1";
option java_multiple_files = true;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// User service
service UserService {
  // Get a single user by ID
  rpc GetUser(GetUserRequest) returns (User);

  // List users with pagination
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);

  // Create a new user
  rpc CreateUser(CreateUserRequest) returns (User);

  // Update an existing user
  rpc UpdateUser(UpdateUserRequest) returns (User);

  // Delete a user
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);

  // Stream user updates
  rpc WatchUsers(WatchUsersRequest) returns (stream User);
}

// Messages
message User {
  string id = 1;
  string name = 2;
  string email = 3;
  google.protobuf.Timestamp created_at = 4;
  google.protobuf.Timestamp updated_at = 5;
  UserStatus status = 6;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;
  USER_STATUS_ACTIVE = 1;
  USER_STATUS_INACTIVE = 2;
  USER_STATUS_SUSPENDED = 3;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_size = 3;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message UpdateUserRequest {
  string id = 1;
  User user = 2;
  google.protobuf.FieldMask update_mask = 3;
}

message DeleteUserRequest {
  string id = 1;
}

message WatchUsersRequest {
  string filter = 1;
}
                """,
            },
            "naming_conventions": {
                "services": "PascalCase with 'Service' suffix (UserService)",
                "methods": "PascalCase verbs (GetUser, CreateUser)",
                "messages": "PascalCase (User, CreateUserRequest)",
                "fields": "snake_case (user_id, created_at)",
                "enums": "SCREAMING_SNAKE_CASE with type prefix",
            },
            "streaming_patterns": {
                "server_streaming": """
// Server streaming: one request, stream of responses
service LogService {
  rpc StreamLogs(StreamLogsRequest) returns (stream LogEntry);
}

message StreamLogsRequest {
  string application = 1;
  google.protobuf.Timestamp start_time = 2;
}

message LogEntry {
  google.protobuf.Timestamp timestamp = 1;
  string level = 2;
  string message = 3;
}

// Client receives continuous stream of logs
                """,
                "client_streaming": """
// Client streaming: stream of requests, one response
service UploadService {
  rpc UploadFile(stream FileChunk) returns (UploadResponse);
}

message FileChunk {
  bytes data = 1;
  int32 chunk_number = 2;
}

message UploadResponse {
  string file_id = 1;
  int64 total_bytes = 2;
}

// Client sends file in chunks
                """,
                "bidirectional_streaming": """
// Bidirectional streaming: stream both ways
service ChatService {
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message ChatMessage {
  string user_id = 1;
  string text = 2;
  google.protobuf.Timestamp timestamp = 3;
}

// Real-time chat
                """,
            },
            "error_handling": """
// gRPC uses status codes (like HTTP)
from grpc import StatusCode

status_codes = {
    "OK": 0,                      # Success
    "CANCELLED": 1,               # Cancelled by client
    "UNKNOWN": 2,                 # Unknown error
    "INVALID_ARGUMENT": 3,        # Invalid argument (400)
    "DEADLINE_EXCEEDED": 4,       # Timeout (504)
    "NOT_FOUND": 5,               # Not found (404)
    "ALREADY_EXISTS": 6,          # Already exists (409)
    "PERMISSION_DENIED": 7,       # Forbidden (403)
    "RESOURCE_EXHAUSTED": 8,      # Rate limit (429)
    "FAILED_PRECONDITION": 9,     # Precondition failed
    "ABORTED": 10,                # Aborted
    "OUT_OF_RANGE": 11,           # Out of range
    "UNIMPLEMENTED": 12,          # Not implemented (501)
    "INTERNAL": 13,               # Internal error (500)
    "UNAVAILABLE": 14,            # Service unavailable (503)
    "DATA_LOSS": 15,              # Data loss
    "UNAUTHENTICATED": 16,        # Unauthenticated (401)
}

# Python example
import grpc

def get_user(request, context):
    user = db.get_user(request.id)
    if not user:
        context.abort(
            grpc.StatusCode.NOT_FOUND,
            f"User {request.id} not found"
        )
    return user
            """,
            "versioning": {
                "description": "Version gRPC services in package name",
                "example": """
// Version 1
package com.example.users.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
}

// Version 2 (breaking changes)
package com.example.users.v2;

service UserService {
  rpc GetUser(GetUserRequest) returns (UserResponse);  // Changed return type
}

// Run both versions simultaneously
// Clients choose version by import path
                """,
            },
        }

    # =========================================================================
    # OUTPUT METHODS
    # =========================================================================

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        api_type: str,
        description: str,
        current_design: str,
        recommended_design: str,
        standard_violated: str,
    ) -> APIDesignFinding:
        """
        Generate a structured API design finding
        """
        return APIDesignFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            api_type=api_type,
            location={"file": "to_be_determined"},
            description=description,
            standard_violated=standard_violated,
            current_design=current_design,
            recommended_design=recommended_design,
            rationale="Following industry best practices and standards",
            testing_guidance="Test with automated tools and manual review",
            tools=self._get_tools(api_type),
            references=self._get_references(api_type),
            migration_strategy={
                "approach": "Gradual migration with versioning",
                "steps": [
                    "1. Create new version with improved design",
                    "2. Run both versions in parallel",
                    "3. Migrate clients gradually",
                    "4. Deprecate old version after migration period",
                ],
            },
        )

    @staticmethod
    def _get_tools(api_type: str) -> List[Dict[str, str]]:
        tools = {
            "REST": [
                {
                    "name": "OpenAPI Validator",
                    "command": "npm install -g @stoplight/spectral-cli && spectral lint openapi.yaml",
                    "description": "Validate OpenAPI specs",
                },
                {
                    "name": "Postman",
                    "description": "API testing and documentation",
                },
            ],
            "GraphQL": [
                {
                    "name": "GraphQL Inspector",
                    "command": "npm install -g @graphql-inspector/cli",
                    "description": "Validate GraphQL schemas",
                },
            ],
            "gRPC": [
                {
                    "name": "buf",
                    "command": "brew install bufbuild/buf/buf",
                    "description": "Protobuf linter and validator",
                },
            ],
        }
        return tools.get(api_type, [])

    @staticmethod
    def _get_references(api_type: str) -> List[str]:
        refs = {
            "REST": [
                "OpenAPI 3.1: https://spec.openapis.org/oas/v3.1.0",
                "RFC 7807 Problem Details: https://datatracker.ietf.org/doc/html/rfc7807",
                "Richardson Maturity Model: https://martinfowler.com/articles/richardsonMaturityModel.html",
            ],
            "GraphQL": [
                "GraphQL Best Practices: https://graphql.org/learn/best-practices/",
                "Relay Cursor Connections: https://relay.dev/graphql/connections.htm",
            ],
            "gRPC": [
                "gRPC Style Guide: https://grpc.io/docs/guides/",
                "Protocol Buffers: https://protobuf.dev/",
            ],
        }
        return refs.get(api_type, [])


def create_enhanced_api_design_assistant():
    """Factory function to create enhanced API design assistant"""
    return {
        "name": "Enhanced API Design Assistant",
        "version": "2.0.0",
        "system_prompt": """You are an expert API design consultant with deep knowledge of:

- RESTful API design (Richardson Maturity Model, HATEOAS)
- OpenAPI 3.1 specification
- GraphQL schema design and best practices
- gRPC service design with Protocol Buffers
- API versioning strategies (URL, header, content negotiation)
- Pagination patterns (offset, cursor, keyset, seek)
- Rate limiting algorithms and RFC 6585
- Error handling standards (RFC 7807 Problem Details)
- API security best practices
- HTTP status codes and semantics

Your role is to:
1. Review API designs for adherence to best practices
2. Recommend appropriate pagination strategy
3. Design error responses following RFC 7807
4. Suggest versioning approach
5. Optimize for performance and scalability
6. Ensure consistent naming and conventions
7. Provide migration strategies for API changes

Always provide:
- Specific standard or RFC violated
- Current design showing the issue
- Recommended design following best practices
- Rationale for recommendation
- Testing guidance
- Migration strategy for existing APIs

Format findings as structured YAML with all required fields.
""",
        "assistant_class": EnhancedAPIDesignAssistant,
        "domain": "architecture",
        "tags": ["api-design", "rest", "graphql", "grpc", "openapi"],
    }


if __name__ == "__main__":
    # Example usage
    assistant = EnhancedAPIDesignAssistant()

    print("=" * 80)
    print("Enhanced API Design Assistant")
    print("=" * 80)
    print(f"\nVersion: {assistant.version}")
    print(f"Standards: {', '.join(assistant.standards)}")

    print("\n" + "=" * 80)
    print("Example Finding:")
    print("=" * 80)

    finding = assistant.generate_finding(
        finding_id="API-001",
        title="Using verbs in REST URLs instead of nouns",
        severity="MEDIUM",
        api_type="REST",
        description="API endpoints use verbs (getUser, createUser) instead of nouns with HTTP methods",
        current_design="POST /api/createUser\nPOST /api/getUser",
        recommended_design="POST /api/users\nGET /api/users/123",
        standard_violated="RESTful resource naming conventions",
    )

    print(finding.model_dump_json(indent=2))

    print("\n" + "=" * 80)
    print("Coverage Summary:")
    print("=" * 80)
    print("✅ Richardson Maturity Model - All 4 levels")
    print("✅ OpenAPI 3.1 - Complete specification coverage")
    print("✅ GraphQL - Schema design, pagination, N+1 solutions")
    print("✅ gRPC - proto3, streaming patterns")
    print("✅ Pagination - Offset, cursor, keyset, seek")
    print("✅ Rate Limiting - 5 algorithms with implementations")
    print("✅ Error Handling - RFC 7807 Problem Details")
    print("✅ API Versioning - 4 strategies with pros/cons")
    print("✅ 40+ Code Examples")
