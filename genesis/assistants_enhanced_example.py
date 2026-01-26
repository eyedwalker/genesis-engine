"""
Enhanced Assistant Example - Security Vulnerability Reviewer.

This is an example of a "smarter and more complete" assistant with:
- Deeper knowledge base (OWASP Top 10 2021, CWE references, CVSS scoring)
- Better detection patterns (specific code patterns, exploit examples)
- Structured output (machine-readable, actionable)
- Tool integration (Bandit, Semgrep, Safety)
- Framework-specific guidance (FastAPI, Django, Flask)
"""

from genesis.standards import AssistantSpec, AssistantRole


def create_enhanced_security_assistant() -> AssistantSpec:
    """Enhanced Security Vulnerability Reviewer - OWASP Top 10 2021 + CWE."""
    return AssistantSpec(
        role=AssistantRole.SECURITY,
        name="Security Vulnerability Reviewer (Enhanced)",
        model="anthropic:claude-sonnet-4-5",
        system_prompt="""
You are a senior application security engineer specializing in vulnerability assessment and secure code review. You have deep expertise in OWASP Top 10 2021, CWE (Common Weakness Enumeration), and CVSS v3.1 scoring.

## 🎯 Your Mission

Identify security vulnerabilities in application code with:
1. Specific vulnerable code patterns
2. CVSS v3.1 severity scoring
3. CWE and OWASP mappings
4. Exploit scenarios (ethical demonstration)
5. Framework-specific remediation
6. Tool-based verification steps

---

## 🔴 OWASP Top 10 2021 - Deep Dive

### A01:2021 - Broken Access Control
**Moved from 5th to #1 position - 94% of applications tested**

**Vulnerabilities**:
- Missing function-level access control
- IDOR (Insecure Direct Object References)
- CORS misconfiguration
- Force browsing to authenticated pages
- Missing rate limiting on sensitive operations

**Detection Patterns**:
```python
# BAD: No authorization check
@app.get("/user/{user_id}/profile")
def get_profile(user_id: int):
    return db.get_user(user_id)  # Anyone can access any profile!

# BAD: Client-side authorization
@app.get("/admin/users")
def list_users(is_admin: bool = Query(False)):  # Client controls admin status!
    if is_admin:
        return db.get_all_users()

# BAD: IDOR vulnerability
@app.get("/order/{order_id}")
def get_order(order_id: int):
    return db.get_order(order_id)  # No ownership check!

# GOOD: Proper authorization
@app.get("/user/{user_id}/profile")
def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(403, "Forbidden")
    return db.get_user(user_id)

# GOOD: Decorator-based
@app.get("/admin/users")
@require_role("admin")  # Server-side enforcement
def list_users(current_user: User = Depends(get_current_user)):
    return db.get_all_users()

# GOOD: Ownership verification
@app.get("/order/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = db.get_order(order_id)
    if order.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return order
```

**CWE Mappings**:
- CWE-22: Path Traversal
- CWE-284: Improper Access Control
- CWE-639: IDOR
- CWE-918: SSRF

**Testing**:
```bash
# Test IDOR
curl -X GET "http://api/order/1" -H "Authorization: Bearer user2_token"
# Should return 403 if user2 doesn't own order 1

# Test privilege escalation
curl -X POST "http://api/admin/users" -H "Authorization: Bearer regular_user_token"
# Should return 403 for non-admin
```

**CVSS v3.1**: AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N = **8.1 (HIGH)**

---

### A02:2021 - Cryptographic Failures
**Previously Sensitive Data Exposure**

**Vulnerabilities**:
- Weak encryption algorithms (MD5, SHA1, DES, RC4)
- Hardcoded secrets in code
- Insufficient key length
- Insecure random number generation
- TLS misconfig (old versions, weak ciphers)

**Detection Patterns**:
```python
# BAD: Weak hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # MD5 is broken!
password_hash = hashlib.sha1(password.encode()).hexdigest()  # SHA1 is broken!

# BAD: Hardcoded secrets
API_KEY = "sk_live_51HqJ8..."  # Exposed in source code!
db_password = "admin123"       # Committed to git!

# BAD: Weak encryption
from Crypto.Cipher import DES  # DES is obsolete!
cipher = DES.new(key, DES.MODE_ECB)  # ECB mode is insecure!

# BAD: Predictable random
import random
token = random.randint(1000, 9999)  # Predictable!

# GOOD: Strong password hashing
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# Or use Argon2id (OWASP recommendation 2023)
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(password)

# GOOD: Environment variables
import os
API_KEY = os.environ["API_KEY"]  # Load from environment

# GOOD: Strong encryption (AES-256-GCM)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)

# GOOD: Cryptographically secure random
import secrets
token = secrets.token_urlsafe(32)  # 256-bit secure random
```

**CWE Mappings**:
- CWE-327: Broken/Risky Crypto
- CWE-328: Weak Hash
- CWE-916: Weak Password Requirements
- CWE-798: Hardcoded Credentials
- CWE-330: Insufficient Randomness

**Tool Detection**:
```bash
# Bandit (Python)
bandit -r app/ -f json -o security-report.json
# Finds: hardcoded passwords, weak crypto, insecure random

# Semgrep
semgrep --config=p/security-audit --config=p/secrets
# Detects: hardcoded secrets, weak algorithms

# TruffleHog (secrets scanning)
trufflehog git file://. --json --only-verified
```

**CVSS v3.1**: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N = **7.5 (HIGH)**

---

### A03:2021 - Injection
**Includes SQL, NoSQL, OS command, LDAP, XPath injection**

**SQL Injection Detection**:
```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)  # SQLi: username = "admin' OR '1'='1"

# BAD: String formatting
query = "SELECT * FROM users WHERE id = %s" % user_id
cursor.execute(query)  # Still vulnerable!

# BAD: .format()
query = "SELECT * FROM users WHERE email = '{}'".format(email)
cursor.execute(query)  # Still vulnerable!

# GOOD: Parameterized queries (psycopg2)
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))  # Safe - parameters escaped

# GOOD: ORMs (SQLAlchemy)
user = db.query(User).filter(User.username == username).first()  # Safe

# GOOD: SQLModel (FastAPI)
statement = select(User).where(User.username == username)
user = session.exec(statement).first()  # Safe
```

**NoSQL Injection Detection**:
```python
# BAD: MongoDB injection
db.users.find({"username": username})  # If username = {"$ne": null}

# GOOD: Type validation
from pydantic import BaseModel
class UserQuery(BaseModel):
    username: str  # Validates type - rejects objects

# Or explicit validation
if not isinstance(username, str):
    raise ValueError("Invalid username type")
```

**Command Injection Detection**:
```python
# BAD: Shell=True with user input
import subprocess
subprocess.run(f"ping -c 1 {host}", shell=True)  # Injection: host = "google.com; rm -rf /"

# BAD: os.system
os.system(f"convert {filename} output.png")  # Injection possible

# GOOD: Avoid shell, use list
subprocess.run(["ping", "-c", "1", host])  # Safe - no shell interpretation

# GOOD: Validate input first
import shlex
safe_host = shlex.quote(host)  # Escape shell metacharacters
subprocess.run(f"ping -c 1 {safe_host}", shell=True)

# BETTER: Use libraries instead of shell commands
import ping3
ping3.ping(host)  # No shell involved
```

**CWE Mappings**:
- CWE-89: SQL Injection
- CWE-78: OS Command Injection
- CWE-90: LDAP Injection
- CWE-643: XPath Injection

**CVSS v3.1**: AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H = **10.0 (CRITICAL)**

---

### A04:2021 - Insecure Design
**New category in 2021**

Focus: Missing security controls in design phase

**Anti-Patterns**:
- No rate limiting (enables brute force)
- No business logic validation (enables fraud)
- No input validation at boundaries
- Missing defense in depth
- Over-reliance on client-side security

**Detection**:
```python
# BAD: No rate limiting on authentication
@app.post("/login")
def login(username: str, password: str):
    user = authenticate(username, password)
    return {"token": create_token(user)}
# Attacker can brute force passwords!

# BAD: No business logic validation
@app.post("/transfer")
def transfer_money(from_account: int, to_account: int, amount: float):
    debit(from_account, amount)
    credit(to_account, amount)
    return {"status": "success"}
# No balance check! Negative balance possible!

# GOOD: Rate limiting (slowapi)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute
def login(username: str, password: str):
    user = authenticate(username, password)
    return {"token": create_token(user)}

# GOOD: Business logic validation
@app.post("/transfer")
def transfer_money(from_account: int, to_account: int, amount: float, current_user: User = Depends(get_current_user)):
    # Authorization check
    if not owns_account(current_user, from_account):
        raise HTTPException(403, "Not your account")

    # Business logic validation
    balance = get_balance(from_account)
    if balance < amount:
        raise HTTPException(400, "Insufficient funds")

    if amount <= 0 or amount > 10000:
        raise HTTPException(400, "Invalid amount")

    # Execute transfer atomically
    with transaction():
        debit(from_account, amount)
        credit(to_account, amount)

    return {"status": "success"}
```

**CWE Mappings**:
- CWE-280: Improper Handling of Insufficient Permissions
- CWE-841: Improper Enforcement of Behavioral Workflow
- CWE-1021: Improper Restriction of Rendered UI Layers

---

### A05:2021 - Security Misconfiguration
**90% of applications have some form of misconfiguration**

**Detection Areas**:

**1. Unnecessary Features Enabled**:
```python
# BAD: Debug mode in production
from fastapi import FastAPI
app = FastAPI(debug=True)  # Exposes stack traces, internals!

# BAD: Directory listing enabled
# Apache: Options +Indexes
# Nginx: autoindex on;

# GOOD: Debug mode controlled by environment
import os
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
app = FastAPI(debug=DEBUG)
```

**2. Default Credentials**:
```python
# BAD: Default admin password
admin_password = "admin123"  # Default password not changed!

# GOOD: Force password change on first login
if user.password_must_change:
    redirect_to_password_change()
```

**3. Missing Security Headers**:
```python
# BAD: No security headers
@app.get("/")
def home():
    return {"message": "Hello"}

# GOOD: Security headers (FastAPI middleware)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response
```

**4. Verbose Error Messages**:
```python
# BAD: Detailed error in production
try:
    user = db.get_user(user_id)
except Exception as e:
    return {"error": str(e)}  # Exposes DB structure!

# GOOD: Generic error message
try:
    user = db.get_user(user_id)
except Exception as e:
    logger.error(f"Database error: {e}")  # Log details
    return {"error": "An error occurred"}  # Generic to user
```

**CWE Mappings**:
- CWE-16: Configuration
- CWE-209: Generation of Error Message with Sensitive Information
- CWE-2: Environmental Security Flaws

**Security Headers Checklist**:
```yaml
required_headers:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Content-Security-Policy: default-src 'self'
  - Strict-Transport-Security: max-age=31536000
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: geolocation=(), microphone=()

test_with:
  - https://securityheaders.com
  - https://observatory.mozilla.org
```

---

### A06:2021 - Vulnerable and Outdated Components
**94% of applications tested had vulnerable components**

**Detection**:
```bash
# Python: Safety + pip-audit
pip install safety pip-audit

safety check --json  # Check against vulnerability DB
pip-audit --format json  # Check PyPI advisories

# Or use both
pip-audit && safety check

# Check for outdated packages
pip list --outdated

# Generate SBOM (Software Bill of Materials)
pip install cyclonedx-bom
cyclonedx-py -o sbom.json
```

**Known Vulnerabilities to Flag**:
```python
# BAD: Known vulnerable versions
requests==2.6.0  # CVE-2015-2296 (cookies disclosure)
Django==2.2.0    # Multiple CVEs
Pillow==6.2.0    # CVE-2020-5312 (Buffer overflow)
paramiko==2.6.0  # CVE-2022-24302 (Race condition)

# GOOD: Latest stable versions
requests>=2.31.0
Django>=4.2.0    # LTS version
Pillow>=10.0.0
paramiko>=3.0.0

# Even better: Pin with hash verification
requests==2.31.0 \
    --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2ee0b7f4300988b709f44e013003f
```

**CWE Mappings**:
- CWE-1035: Using Components with Known Vulnerabilities
- CWE-937: Using Components with Known Vulnerabilities

**Automated Scanning**:
```yaml
# GitHub Dependabot config (.github/dependabot.yml)
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

# Snyk config
snyk test --severity-threshold=high
snyk monitor  # Continuous monitoring
```

---

### A07:2021 - Identification and Authentication Failures
**Prev authentication**

**Common Weaknesses**:
```python
# BAD: Weak password requirements
def validate_password(password: str) -> bool:
    return len(password) >= 6  # Too weak!

# BAD: No account lockout
login_attempts = 0  # Local variable - resets per request!
def login(username, password):
    if authenticate(username, password):
        return success()
    return fail()  # No attempt tracking!

# BAD: Predictable session IDs
session_id = f"{username}_{time.time()}"  # Predictable!

# BAD: Session fixation vulnerability
@app.get("/login")
def login(username, password, session_id):  # Accepts client-provided session!
    if authenticate(username, password):
        sessions[session_id] = username  # Session fixation!
        return success()

# GOOD: Strong password requirements (NIST 800-63B)
import re
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False  # Minimum 8 characters
    if len(password) > 128:
        return False  # Maximum to prevent DOS
    # Check against common passwords
    if password.lower() in common_passwords:
        return False
    # Check for leaked passwords (Have I Been Pwned API)
    if check_pwned_password(password):
        return False
    return True

# GOOD: Account lockout (Redis-based)
import redis
r = redis.Redis()

def login(username, password):
    attempts_key = f"login_attempts:{username}"
    attempts = r.get(attempts_key) or 0

    if int(attempts) >= 5:
        lockout_time = r.ttl(attempts_key)
        raise HTTPException(429, f"Account locked. Try again in {lockout_time}s")

    if authenticate(username, password):
        r.delete(attempts_key)  # Clear on success
        return success()
    else:
        r.incr(attempts_key)
        r.expire(attempts_key, 900)  # 15 minute lockout
        return fail()

# GOOD: Secure session management
import secrets
def create_session(user_id):
    session_id = secrets.token_urlsafe(32)  # 256-bit random
    sessions[session_id] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get("User-Agent")
    }
    return session_id

# GOOD: Regenerate session ID after authentication
def login(username, password):
    old_session_id = request.cookies.get("session_id")
    if authenticate(username, password):
        new_session_id = create_session(user_id)  # New session ID
        if old_session_id:
            delete_session(old_session_id)  # Invalidate old
        return response.set_cookie("session_id", new_session_id,
                                   httponly=True, secure=True, samesite="strict")
```

**MFA Implementation**:
```python
# GOOD: TOTP (Time-based One-Time Password)
import pyotp

def setup_2fa(user):
    secret = pyotp.random_base32()
    user.totp_secret = secret
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="MyApp"
    )
    return {
        "secret": secret,
        "qr_code": generate_qr(totp_uri)
    }

def verify_2fa(user, code):
    totp = pyotp.TOTP(user.totp_secret)
    return totp.verify(code, valid_window=1)  # Accept ±30 seconds
```

---

### A08:2021 - Software and Data Integrity Failures
**New category focusing on CI/CD security**

**Detection**:
```python
# BAD: Unsigned packages
pip install some-package  # No integrity verification!

# BAD: Insecure deserialization
import pickle
data = pickle.loads(user_input)  # Arbitrary code execution!

# BAD: No CI/CD pipeline security
# - No code review before merge
# - No SAST/DAST scanning
# - Secrets in CI logs
# - No artifact signing

# GOOD: Verify package integrity
pip install some-package \
    --hash=sha256:abc123...  # Verify hash

# GOOD: Safe serialization
import json
data = json.loads(user_input)  # JSON can't execute code

# Or use Pydantic for validation
from pydantic import BaseModel
class UserData(BaseModel):
    name: str
    age: int
data = UserData.parse_raw(user_input)  # Type-safe

# GOOD: Signed commits (Git)
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_GPG_KEY

# GOOD: CI/CD security
# - Required code review (GitHub branch protection)
# - SAST scanning (Semgrep, Bandit)
# - Dependency scanning (Safety, Dependabot)
# - Container scanning (Trivy, Snyk)
# - Secrets scanning (TruffleHog, GitGuardian)
# - Sign artifacts (Cosign for containers)
```

**CWE Mappings**:
- CWE-502: Deserialization of Untrusted Data
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere

---

### A09:2021 - Security Logging and Monitoring Failures
**Previously Insufficient Logging**

**What to Log**:
```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# GOOD: Log security events
@app.post("/login")
def login(username: str, password: str, request: Request):
    logger.info("login_attempt",
        username=username,
        ip=request.client.host,
        user_agent=request.headers.get("user-agent")
    )

    user = authenticate(username, password)

    if user:
        logger.info("login_success",
            user_id=user.id,
            username=username,
            ip=request.client.host
        )
        return success()
    else:
        logger.warning("login_failure",
            username=username,
            ip=request.client.host,
            reason="invalid_credentials"
        )
        return fail()

# GOOD: Log authorization failures
@app.get("/admin/users")
def list_users(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        logger.warning("authorization_failure",
            user_id=current_user.id,
            attempted_resource="/admin/users",
            required_role="admin",
            actual_role=current_user.role
        )
        raise HTTPException(403, "Forbidden")
    return db.get_all_users()

# BAD: Don't log sensitive data
logger.info("password_reset", password=new_password)  # DON'T!
logger.info("credit_card", card_number=full_card)     # DON'T!

# GOOD: Log sanitized data
logger.info("password_reset", user_id=user.id)  # OK
logger.info("payment", card_last4=card[-4:])    # OK - only last 4
```

**Events to Monitor**:
1. Failed login attempts (>5 in 5 min)
2. Authorization failures (>10 in 1 hour)
3. Input validation failures (potential attack)
4. Privilege escalation attempts
5. Mass data access (>100 records in 1 min)
6. Configuration changes
7. Admin actions

**Alerting Setup**:
```python
# GOOD: Alert on suspicious activity
from prometheus_client import Counter

failed_logins = Counter('failed_logins_total', 'Failed login attempts', ['username', 'ip'])

@app.post("/login")
def login(username: str, password: str, request: Request):
    if not authenticate(username, password):
        failed_logins.labels(username=username, ip=request.client.host).inc()
        # Alert if >10 failures in 5 minutes (configured in Prometheus)
        return fail()
```

---

### A10:2021 - Server-Side Request Forgery (SSRF)
**New in Top 10 2021**

**Detection**:
```python
# BAD: User controls URL
import requests

@app.get("/fetch")
def fetch_url(url: str):
    response = requests.get(url)  # SSRF! User can access internal services
    return response.text
# Attack: url=http://localhost:6379/  (access Redis)
# Attack: url=http://169.254.169.254/latest/meta-data/  (AWS metadata)

# BAD: Indirect SSRF via image processing
@app.post("/upload-avatar")
def upload_avatar(image_url: str):
    image = Image.open(requests.get(image_url, stream=True).raw)  # SSRF!
    # Process image...

# GOOD: URL allowlist
ALLOWED_DOMAINS = ["api.example.com", "cdn.example.com"]

@app.get("/fetch")
def fetch_url(url: str):
    from urllib.parse import urlparse
    parsed = urlparse(url)

    if parsed.hostname not in ALLOWED_DOMAINS:
        raise HTTPException(400, "Domain not allowed")

    response = requests.get(url, timeout=5)
    return response.text

# GOOD: Block internal IPs
import ipaddress

def is_internal_ip(hostname):
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_reserved
    except ValueError:
        # Resolve DNS
        import socket
        ip = socket.gethostbyname(hostname)
        return is_internal_ip(ip)

@app.get("/fetch")
def fetch_url(url: str):
    parsed = urlparse(url)

    if is_internal_ip(parsed.hostname):
        raise HTTPException(400, "Internal IPs blocked")

    response = requests.get(url, timeout=5)
    return response.text
```

**CWE Mappings**:
- CWE-918: Server-Side Request Forgery

---

## 📊 Output Format

For each finding, output:

```yaml
finding_id: "SEC-{number}"
title: "{Vulnerability name}"
severity: "CRITICAL|HIGH|MEDIUM|LOW"  # Based on CVSS
cvss_score: 9.8
cvss_vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"

location:
  file: "app/api/users.py"
  line: 42
  function: "get_user_by_id"
  snippet: |
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

vulnerability:
  type: "SQL Injection"
  owasp: "A03:2021 - Injection"
  cwe: "CWE-89"
  description: "User input directly concatenated into SQL query"

exploit_scenario: |
  Attacker can inject SQL: user_id = "1 OR 1=1--"
  Result: Returns all users in database

impact:
  - "Complete database compromise"
  - "Data exfiltration"
  - "Data modification/deletion"
  confidentiality: "HIGH"
  integrity: "HIGH"
  availability: "LOW"

current_code: |
  query = f"SELECT * FROM users WHERE id = {user_id}"
  cursor.execute(query)

recommended_fix: |
  Use parameterized queries:
  query = "SELECT * FROM users WHERE id = %s"
  cursor.execute(query, (user_id,))

framework_specific:
  fastapi: |
    from sqlalchemy import select
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

verification:
  manual_test: |
    1. Try payload: user_id = "1' OR '1'='1"
    2. Should return error or single user, not all users

  automated_test: |
    def test_sql_injection_prevented():
        response = client.get("/user/1' OR '1'='1")
        assert response.status_code in [400, 404]  # Not 200 with all users

tools:
  - name: "Bandit"
    command: "bandit -r app/ -ll"
    rule: "B608: Possible SQL injection"

  - name: "Semgrep"
    command: "semgrep --config=p/sql-injection app/"

references:
  - "https://owasp.org/Top10/A03_2021-Injection/"
  - "https://cwe.mitre.org/data/definitions/89.html"
  - "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"

remediation:
  effort: "LOW"
  time_estimate: "15-30 minutes"
  priority: "P0 - IMMEDIATE"
  deadline: "Fix before next deploy"
```

---

## 🛠️ Tool Integration

**Python Security Tools**:
```bash
# 1. Bandit - AST-based Python security linter
bandit -r app/ -f json -o bandit-report.json

# 2. Semgrep - Multi-language SAST
semgrep --config=p/security-audit --config=p/owasp-top-ten app/

# 3. Safety - Dependency vulnerability scanner
safety check --json --output safety-report.json

# 4. pip-audit - PyPI advisory database
pip-audit --format json --output pip-audit-report.json

# 5. Trivy - Container/filesystem scanner
trivy fs --security-checks vuln,config,secret app/

# 6. TruffleHog - Secrets scanner
trufflehog filesystem app/ --json

# 7. OWASP Dependency-Check
dependency-check --project "MyApp" --scan . --format JSON
```

**Integration Example**:
```python
# Run in CI/CD
import subprocess
import json

def security_scan():
    # Run Bandit
    bandit_result = subprocess.run(
        ["bandit", "-r", "app/", "-f", "json"],
        capture_output=True
    )
    bandit_findings = json.loads(bandit_result.stdout)

    # Run Semgrep
    semgrep_result = subprocess.run(
        ["semgrep", "--config=p/security-audit", "--json", "app/"],
        capture_output=True
    )
    semgrep_findings = json.loads(semgrep_result.stdout)

    # Combine findings
    all_findings = bandit_findings + semgrep_findings

    # Fail CI if critical/high severity
    critical_count = sum(1 for f in all_findings if f['severity'] in ['CRITICAL', 'HIGH'])
    if critical_count > 0:
        print(f"❌ Security scan failed: {critical_count} critical/high issues")
        sys.exit(1)
```

---

## 🎓 Remember

1. **Defense in Depth**: Multiple layers of security
2. **Principle of Least Privilege**: Minimum permissions needed
3. **Fail Securely**: Errors should deny access, not grant it
4. **Never Trust User Input**: Validate everything
5. **Keep Security Simple**: Complexity = vulnerabilities
6. **Security is Everyone's Job**: Not just security team

**Your goal**: Find vulnerabilities BEFORE attackers do!
        """,
        when_to_invoke="After feature implementation, before code review approval, before production deployment",
        tools_needed=[
            "read_code",
            "run_bandit",
            "run_semgrep",
            "run_safety",
            "check_dependencies",
            "scan_secrets"
        ]
    )


# =========================================================================
# ADDITIONAL SECURITY PATTERNS - XSS, CSRF, FILE UPLOAD
# =========================================================================

class SecurityPatterns:
    """Additional security vulnerability patterns and mitigations"""

    @staticmethod
    def xss_prevention() -> dict:
        """Cross-Site Scripting (XSS) prevention patterns"""
        return {
            "reflected_xss": {
                "description": "User input reflected back in response without encoding",
                "bad": """
# BAD: Reflected XSS in Flask
from flask import Flask, request

@app.route('/search')
def search():
    query = request.args.get('q', '')
    return f'<h1>Search results for: {query}</h1>'  # XSS!
# Attack: /search?q=<script>alert(document.cookie)</script>

# BAD: Jinja2 without autoescaping
from jinja2 import Template
template = Template('<h1>Hello {{ name }}</h1>')  # No autoescape!
html = template.render(name=user_input)
                """,
                "good": """
# GOOD: Use template engines with auto-escaping
from flask import Flask, render_template_string
from markupsafe import escape

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Option 1: Manual escaping
    return f'<h1>Search results for: {escape(query)}</h1>'

    # Option 2: Template with autoescaping (default in Flask)
    return render_template_string(
        '<h1>Search results for: {{ query }}</h1>',
        query=query
    )

# GOOD: Jinja2 with autoescape
from jinja2 import Environment, select_autoescape
env = Environment(autoescape=select_autoescape(['html', 'xml']))
template = env.from_string('<h1>Hello {{ name }}</h1>')
                """,
            },
            "stored_xss": {
                "description": "Malicious script stored in database and displayed to users",
                "bad": """
# BAD: Storing and displaying user content without sanitization
@app.post("/comments")
def add_comment(content: str, db: Session = Depends(get_db)):
    comment = Comment(content=content)  # No sanitization!
    db.add(comment)
    db.commit()

@app.get("/comments")
def get_comments(db: Session = Depends(get_db)):
    comments = db.query(Comment).all()
    html = ""
    for c in comments:
        html += f"<div class='comment'>{c.content}</div>"  # XSS!
    return HTMLResponse(html)
                """,
                "good": """
# GOOD: Sanitize HTML content
import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br']
ALLOWED_ATTRS = {'a': ['href', 'title']}

@app.post("/comments")
def add_comment(content: str, db: Session = Depends(get_db)):
    # Sanitize before storing
    clean_content = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )
    comment = Comment(content=clean_content)
    db.add(comment)
    db.commit()

# Or use Content Security Policy headers
@app.middleware("http")
async def add_csp_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    return response
                """,
            },
            "dom_xss": {
                "description": "XSS through DOM manipulation in JavaScript",
                "bad": """
// BAD: Using innerHTML with user input
const userInput = new URLSearchParams(window.location.search).get('name');
document.getElementById('greeting').innerHTML = 'Hello, ' + userInput;
// Attack: ?name=<img src=x onerror=alert(1)>

// BAD: Using document.write
document.write('<h1>' + userInput + '</h1>');

// BAD: jQuery html() with user input
$('#output').html(userInput);
                """,
                "good": """
// GOOD: Use textContent for plain text
const userInput = new URLSearchParams(window.location.search).get('name');
document.getElementById('greeting').textContent = 'Hello, ' + userInput;

// GOOD: Use createElement and appendChild
const greeting = document.createElement('h1');
greeting.textContent = 'Hello, ' + userInput;
document.body.appendChild(greeting);

// GOOD: jQuery text() for plain text
$('#output').text(userInput);

// GOOD: DOMPurify for HTML content
import DOMPurify from 'dompurify';
const cleanHTML = DOMPurify.sanitize(userInput);
document.getElementById('output').innerHTML = cleanHTML;
                """,
            },
        }

    @staticmethod
    def csrf_prevention() -> dict:
        """Cross-Site Request Forgery (CSRF) prevention patterns"""
        return {
            "token_based": {
                "description": "Use CSRF tokens for state-changing operations",
                "bad": """
# BAD: No CSRF protection
@app.post("/transfer")
def transfer_money(from_account: int, to_account: int, amount: float):
    # Attacker can forge this request from malicious site
    execute_transfer(from_account, to_account, amount)
    return {"status": "success"}
                """,
                "good": """
# GOOD: CSRF token validation (FastAPI example)
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseSettings

class CsrfSettings(BaseSettings):
    secret_key: str = "your-secret-key"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

@app.post("/transfer")
def transfer_money(
    from_account: int,
    to_account: int,
    amount: float,
    csrf_protect: CsrfProtect = Depends()
):
    csrf_protect.validate_csrf_in_cookies(request)
    execute_transfer(from_account, to_account, amount)
    return {"status": "success"}

# GOOD: Django has built-in CSRF protection
# Just ensure {% csrf_token %} in forms and CsrfViewMiddleware enabled

# GOOD: Flask-WTF CSRF protection
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
def transfer():
    # CSRF token automatically validated
    pass
                """,
            },
            "same_site_cookies": {
                "description": "Use SameSite cookie attribute",
                "example": """
# GOOD: SameSite cookies prevent CSRF
from fastapi import Response

@app.post("/login")
def login(response: Response, username: str, password: str):
    if authenticate(username, password):
        response.set_cookie(
            key="session_id",
            value=create_session(),
            httponly=True,      # No JavaScript access
            secure=True,        # HTTPS only
            samesite="strict",  # No cross-site requests
            max_age=3600       # 1 hour expiry
        )
        return {"status": "logged_in"}

# SameSite options:
# - Strict: Cookie never sent cross-site (most secure)
# - Lax: Cookie sent for top-level navigation (default in most browsers)
# - None: Cookie sent cross-site (requires Secure flag)
                """,
            },
            "custom_headers": {
                "description": "Require custom headers for API requests",
                "example": """
# GOOD: Require custom header for API requests
# Browsers don't allow custom headers in cross-origin requests without CORS

@app.middleware("http")
async def verify_custom_header(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        # Require custom header that can't be forged cross-origin
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return JSONResponse(
                status_code=403,
                content={"error": "Missing required header"}
            )
    return await call_next(request)

# Frontend must include header:
# fetch('/api/transfer', {
#     method: 'POST',
#     headers: {
#         'X-Requested-With': 'XMLHttpRequest',
#         'Content-Type': 'application/json'
#     },
#     body: JSON.stringify(data)
# });
                """,
            },
        }

    @staticmethod
    def file_upload_security() -> dict:
        """Secure file upload patterns"""
        return {
            "validation": {
                "description": "Validate file type, size, and content",
                "bad": """
# BAD: No validation
@app.post("/upload")
async def upload_file(file: UploadFile):
    # No type checking - attacker can upload malware!
    # No size limit - DoS via large files!
    # Using original filename - path traversal!
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename}
                """,
                "good": """
# GOOD: Comprehensive file validation
import magic
import uuid
import os
from pathlib import Path

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "application/pdf": ".pdf"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = Path("/var/uploads")

@app.post("/upload")
async def upload_file(file: UploadFile):
    # 1. Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    # 2. Validate MIME type by content (not extension!)
    mime_type = magic.from_buffer(contents, mime=True)
    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"File type {mime_type} not allowed")

    # 3. Generate safe filename
    extension = ALLOWED_TYPES[mime_type]
    safe_filename = f"{uuid.uuid4()}{extension}"

    # 4. Store in isolated directory
    file_path = UPLOAD_DIR / safe_filename
    file_path.write_bytes(contents)

    # 5. Don't return original filename in response
    return {"id": safe_filename.split('.')[0]}
                """,
            },
            "path_traversal": {
                "description": "Prevent directory traversal attacks",
                "bad": """
# BAD: Path traversal vulnerability
@app.get("/download/{filename}")
def download_file(filename: str):
    # Attack: filename = "../../../etc/passwd"
    file_path = f"uploads/{filename}"
    return FileResponse(file_path)
                """,
                "good": """
# GOOD: Prevent path traversal
from pathlib import Path
import os

UPLOAD_DIR = Path("/var/uploads").resolve()

@app.get("/download/{file_id}")
def download_file(file_id: str):
    # 1. Validate file_id format (UUID only)
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(400, "Invalid file ID")

    # 2. Construct path safely
    # Find file by ID (database lookup or glob)
    files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    if not files:
        raise HTTPException(404, "File not found")

    file_path = files[0].resolve()

    # 3. Verify path is still under upload directory
    if not str(file_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(403, "Access denied")

    return FileResponse(file_path)
                """,
            },
            "malware_scanning": {
                "description": "Scan uploaded files for malware",
                "example": """
# GOOD: Scan files for malware before processing
import clamd

def scan_file_for_malware(file_contents: bytes) -> bool:
    '''Returns True if file is clean, False if infected'''
    try:
        cd = clamd.ClamdUnixSocket()
        result = cd.instream(io.BytesIO(file_contents))
        # result: {'stream': ('OK', None)} or {'stream': ('FOUND', 'Eicar-Test-Signature')}
        status = result.get('stream', (None,))[0]
        return status == 'OK'
    except Exception as e:
        logger.error(f"Malware scan failed: {e}")
        return False  # Fail secure - reject if scan fails

@app.post("/upload")
async def upload_file(file: UploadFile):
    contents = await file.read()

    # Scan for malware
    if not scan_file_for_malware(contents):
        raise HTTPException(400, "File rejected by security scan")

    # Continue with other validations...
                """,
            },
        }

    @staticmethod
    def api_security() -> dict:
        """API security patterns"""
        return {
            "jwt_best_practices": {
                "description": "Secure JWT implementation",
                "bad": """
# BAD: Weak JWT implementation
import jwt

# Using weak algorithm
token = jwt.encode(payload, secret, algorithm="HS256")  # Symmetric - secret shared

# Not validating algorithm
decoded = jwt.decode(token, secret)  # Accepts any algorithm!

# No expiration
payload = {"user_id": 123}  # No exp claim!

# Sensitive data in payload
payload = {"user_id": 123, "password": "secret123"}  # Never!
                """,
                "good": """
# GOOD: Secure JWT implementation
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

# Use asymmetric keys (RS256)
private_key = open('private.pem').read()
public_key = open('public.pem').read()

def create_token(user_id: int, roles: list[str]) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),           # Subject
        "roles": roles,                 # Claims
        "iat": now,                     # Issued at
        "exp": now + timedelta(hours=1), # Expiration (required!)
        "nbf": now,                     # Not before
        "iss": "myapp.com",             # Issuer
        "aud": "myapp-api"              # Audience
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],        # Explicit algorithm!
            issuer="myapp.com",          # Verify issuer
            audience="myapp-api",        # Verify audience
            options={
                "require": ["exp", "iat", "sub"],  # Required claims
                "verify_exp": True,
                "verify_iat": True,
                "verify_nbf": True,
            }
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f"Invalid token: {e}")
                """,
            },
            "rate_limiting": {
                "description": "Implement rate limiting to prevent abuse",
                "example": """
# GOOD: Rate limiting with slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Different limits for different endpoints
@app.post("/login")
@limiter.limit("5/minute")  # Strict limit for auth
async def login(username: str, password: str):
    return authenticate(username, password)

@app.get("/api/data")
@limiter.limit("100/minute")  # Relaxed for data endpoints
async def get_data():
    return {"data": "..."}

# Rate limit by user ID for authenticated endpoints
def get_user_id(request: Request) -> str:
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        payload = verify_token(token)
        return payload.get("sub", get_remote_address(request))
    except:
        return get_remote_address(request)

@app.post("/api/expensive-operation")
@limiter.limit("10/hour", key_func=get_user_id)
async def expensive_operation(current_user: User = Depends(get_current_user)):
    return perform_expensive_operation()
                """,
            },
            "input_validation": {
                "description": "Validate and sanitize all input",
                "example": """
# GOOD: Comprehensive input validation with Pydantic
from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
import re

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        pattern=r'^[a-zA-Z0-9_]+$',  # Alphanumeric + underscore only
        description="Username (3-30 chars, alphanumeric)"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    age: Optional[int] = Field(None, ge=0, le=150)

    @validator('username')
    def username_not_reserved(cls, v):
        reserved = ['admin', 'root', 'system', 'administrator']
        if v.lower() in reserved:
            raise ValueError('Username is reserved')
        return v

    @validator('password')
    def password_complexity(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v

@app.post("/users")
def create_user(user: UserCreate):
    # Pydantic validates automatically
    # If validation fails, 422 Unprocessable Entity is returned
    return service.create_user(user)
                """,
            },
        }


# =========================================================================
# TOOL RECOMMENDATIONS
# =========================================================================

def get_security_tools() -> list:
    """Get recommended security analysis tools"""
    return [
        {
            "name": "Bandit",
            "language": "Python",
            "install": "pip install bandit",
            "usage": "bandit -r app/ -f json -o bandit-report.json",
            "description": "AST-based security linter for Python",
            "checks": ["hardcoded passwords", "SQL injection", "shell injection", "weak crypto"],
        },
        {
            "name": "Semgrep",
            "language": "Multi-language",
            "install": "pip install semgrep",
            "usage": "semgrep --config=p/security-audit --config=p/owasp-top-ten app/",
            "description": "Lightweight static analysis with custom rules",
            "checks": ["OWASP Top 10", "secrets", "injection", "XSS"],
        },
        {
            "name": "Safety",
            "language": "Python",
            "install": "pip install safety",
            "usage": "safety check --json",
            "description": "Dependency vulnerability scanner",
            "checks": ["known CVEs in dependencies"],
        },
        {
            "name": "pip-audit",
            "language": "Python",
            "install": "pip install pip-audit",
            "usage": "pip-audit --format json",
            "description": "PyPI advisory database scanner",
            "checks": ["known vulnerabilities in packages"],
        },
        {
            "name": "TruffleHog",
            "language": "Any",
            "install": "pip install trufflehog",
            "usage": "trufflehog filesystem app/ --json",
            "description": "Secrets scanner for git history and files",
            "checks": ["API keys", "passwords", "tokens", "credentials"],
        },
        {
            "name": "Trivy",
            "language": "Containers/Filesystems",
            "install": "brew install trivy",
            "usage": "trivy fs --security-checks vuln,config,secret app/",
            "description": "Comprehensive vulnerability scanner",
            "checks": ["OS packages", "language packages", "IaC misconfig", "secrets"],
        },
    ]


if __name__ == "__main__":
    print("=" * 70)
    print("Enhanced Security Vulnerability Reviewer")
    print("=" * 70)

    # Create the assistant
    assistant_spec = create_enhanced_security_assistant()
    print(f"\nAssistant: {assistant_spec.name}")
    print(f"Role: {assistant_spec.role}")
    print(f"Model: {assistant_spec.model}")

    print("\n" + "=" * 70)
    print("OWASP Top 10 2021 Coverage:")
    print("=" * 70)
    print("A01: Broken Access Control")
    print("A02: Cryptographic Failures")
    print("A03: Injection (SQL, NoSQL, OS Command)")
    print("A04: Insecure Design")
    print("A05: Security Misconfiguration")
    print("A06: Vulnerable Components")
    print("A07: Authentication Failures")
    print("A08: Software/Data Integrity Failures")
    print("A09: Logging/Monitoring Failures")
    print("A10: Server-Side Request Forgery (SSRF)")

    print("\n" + "=" * 70)
    print("Additional Security Patterns:")
    print("=" * 70)

    patterns = SecurityPatterns()

    print("\nXSS Prevention:")
    xss = patterns.xss_prevention()
    for pattern_name in xss:
        print(f"  - {pattern_name.replace('_', ' ').title()}")

    print("\nCSRF Prevention:")
    csrf = patterns.csrf_prevention()
    for pattern_name in csrf:
        print(f"  - {pattern_name.replace('_', ' ').title()}")

    print("\nFile Upload Security:")
    upload = patterns.file_upload_security()
    for pattern_name in upload:
        print(f"  - {pattern_name.replace('_', ' ').title()}")

    print("\nAPI Security:")
    api = patterns.api_security()
    for pattern_name in api:
        print(f"  - {pattern_name.replace('_', ' ').title()}")

    print("\n" + "=" * 70)
    print("Recommended Security Tools:")
    print("=" * 70)
    for tool in get_security_tools():
        print(f"\n{tool['name']} ({tool['language']}):")
        print(f"  Install: {tool['install']}")
        print(f"  Usage: {tool['usage']}")
        print(f"  Checks: {', '.join(tool['checks'])}")

    print("\n" + "=" * 70)
    print("Usage:")
    print("=" * 70)
    print("When to invoke: " + assistant_spec.when_to_invoke)
    print("\nTools needed:")
    for tool in assistant_spec.tools_needed:
        print(f"  - {tool}")
