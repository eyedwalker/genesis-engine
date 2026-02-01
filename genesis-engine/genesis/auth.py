"""
Genesis Engine - Authentication & Authorization
JWT-based auth with API key support for programmatic access.
"""

import os
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Use PyJWT (lightweight) instead of python-jose
import jwt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JWT_SECRET = os.environ.get("JWT_SECRET", secrets.token_hex(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))
REFRESH_TOKEN_DAYS = int(os.environ.get("REFRESH_TOKEN_DAYS", "30"))

security = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Password hashing (using hashlib - no extra deps)
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password with PBKDF2-HMAC-SHA256"""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        iterations=100_000
    ).hex()
    return hashed, salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash"""
    check, _ = _hash_password(password, salt)
    return secrets.compare_digest(check, hashed)


# ---------------------------------------------------------------------------
# JWT Token Management
# ---------------------------------------------------------------------------

def create_access_token(user_id: str, tenant_id: str, role: str = "member") -> str:
    """Create a JWT access token"""
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str, tenant_id: str) -> str:
    """Create a long-lived refresh token"""
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "type": "refresh",
        "jti": uuid.uuid4().hex,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------------------------------------------------------------------
# API Key Management
# ---------------------------------------------------------------------------

def generate_api_key() -> tuple[str, str]:
    """Generate an API key pair (key, hashed_key)"""
    key = f"ge_{secrets.token_hex(24)}"
    hashed = hashlib.sha256(key.encode()).hexdigest()
    return key, hashed


def hash_api_key(key: str) -> str:
    """Hash an API key for storage lookup"""
    return hashlib.sha256(key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# User Registration & Login (uses database module)
# ---------------------------------------------------------------------------

def register_user(
    email: str,
    password: str,
    name: str,
    tenant_name: str = None,
) -> Dict[str, Any]:
    """Register a new user and optionally create a tenant"""
    from genesis.database import get_db, USE_POSTGRES

    hashed_pw, salt = _hash_password(password)
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    tenant_id = f"tenant-{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    with get_db() as conn:
        cursor = conn.cursor()
        p = "%s" if USE_POSTGRES else "?"

        # Check if email already exists
        cursor.execute(
            f"SELECT id FROM users WHERE email = {p}", (email,)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Email already registered")

        # Create tenant
        t_name = tenant_name or f"{name}'s Workspace"
        cursor.execute(f"""
            INSERT INTO tenants (id, name, plan, created_at)
            VALUES ({p}, {p}, {p}, {p})
        """, (tenant_id, t_name, "free", now))

        # Create user
        cursor.execute(f"""
            INSERT INTO users (id, tenant_id, email, password_hash, password_salt, name, role, created_at)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """, (user_id, tenant_id, email, hashed_pw, salt, name, "owner", now))

        conn.commit()

    access_token = create_access_token(user_id, tenant_id, "owner")
    refresh_token = create_refresh_token(user_id, tenant_id)

    return {
        "user": {
            "id": user_id,
            "email": email,
            "name": name,
            "role": "owner",
            "tenant_id": tenant_id,
        },
        "tenant": {
            "id": tenant_id,
            "name": t_name,
            "plan": "free",
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate user and return tokens"""
    from genesis.database import get_db, USE_POSTGRES, _row_to_dict

    with get_db() as conn:
        cursor = conn.cursor()
        p = "%s" if USE_POSTGRES else "?"

        cursor.execute(f"""
            SELECT u.id, u.tenant_id, u.email, u.password_hash, u.password_salt,
                   u.name, u.role, t.name as tenant_name, t.plan
            FROM users u JOIN tenants t ON u.tenant_id = t.id
            WHERE u.email = {p}
        """, (email,))

        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user = _row_to_dict(row, cursor)

    if not verify_password(password, user["password_hash"], user["password_salt"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user["id"], user["tenant_id"], user["role"])
    refresh_token = create_refresh_token(user["id"], user["tenant_id"])

    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
        },
        "tenant": {
            "id": user["tenant_id"],
            "name": user["tenant_name"],
            "plan": user["plan"],
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token_str: str) -> Dict[str, Any]:
    """Use a refresh token to get a new access token"""
    payload = decode_token(refresh_token_str)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token(
        payload["sub"], payload["tenant_id"]
    )
    return {
        "access_token": new_access,
        "token_type": "bearer",
    }


# ---------------------------------------------------------------------------
# FastAPI Dependencies (for protecting routes)
# ---------------------------------------------------------------------------

class AuthUser:
    """Authenticated user context"""
    def __init__(self, user_id: str, tenant_id: str, role: str = "member"):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> AuthUser:
    """
    Extract authenticated user from:
    1. Bearer JWT token
    2. API key in X-API-Key header
    3. Allow unauthenticated for backward compatibility (returns default tenant)
    """
    from genesis.database import get_db, USE_POSTGRES, _row_to_dict

    # Try Bearer token first
    if credentials and credentials.credentials:
        payload = decode_token(credentials.credentials)
        return AuthUser(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload.get("role", "member"),
        )

    # Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        hashed = hash_api_key(api_key)
        with get_db() as conn:
            cursor = conn.cursor()
            p = "%s" if USE_POSTGRES else "?"
            cursor.execute(f"""
                SELECT user_id, tenant_id FROM api_keys
                WHERE key_hash = {p} AND is_active = true
            """, (hashed,))
            row = cursor.fetchone()
            if row:
                result = _row_to_dict(row, cursor)
                return AuthUser(
                    user_id=result["user_id"],
                    tenant_id=result["tenant_id"],
                    role="api",
                )

        raise HTTPException(status_code=401, detail="Invalid API key")

    # No auth provided - return default tenant for backward compatibility
    return AuthUser(user_id="system", tenant_id="default", role="owner")


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(security),
    request: Request = None,
) -> AuthUser:
    """Strict auth - requires valid token or API key"""
    if not credentials or not credentials.credentials:
        api_key = request.headers.get("X-API-Key") if request else None
        if not api_key:
            raise HTTPException(status_code=401, detail="Authentication required")

    return await get_current_user(request, credentials)


async def require_owner(user: AuthUser = Depends(require_auth)) -> AuthUser:
    """Require owner role"""
    if user.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Owner access required")
    return user
