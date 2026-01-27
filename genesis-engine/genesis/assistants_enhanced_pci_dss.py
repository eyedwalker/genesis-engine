"""
Enhanced PCI-DSS Compliance Reviewer

Comprehensive PCI-DSS v4.0 compliance covering:
- 12 Requirements overview
- SAQ types (A, A-EP, B, C, D)
- Cardholder Data Environment (CDE) scoping
- Tokenization vs encryption
- Key management
- Network segmentation
- Logging requirements (10.x)

References:
- PCI DSS v4.0: https://www.pcisecuritystandards.org/
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class PCIDSSFinding(BaseModel):
    finding_id: str = Field(...)
    title: str = Field(...)
    severity: str = Field(...)
    requirement: str = Field(default="", description="PCI-DSS Requirement (1-12)")
    sub_requirement: str = Field(default="")
    current_state: str = Field(default="")
    compliant_state: str = Field(default="")
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedPCIDSSAssistant:
    """Enhanced PCI-DSS Compliance Reviewer"""

    def __init__(self):
        self.name = "Enhanced PCI-DSS Compliance Reviewer"
        self.version = "2.0.0"
        self.standards = ["PCI-DSS v4.0"]

    @staticmethod
    def requirements_overview() -> Dict[str, Any]:
        """PCI-DSS 12 Requirements"""
        return {
            "build_secure_network": {
                "1": "Install and maintain network security controls",
                "2": "Apply secure configurations to all system components",
            },
            "protect_account_data": {
                "3": "Protect stored account data",
                "4": "Protect cardholder data with strong cryptography during transmission",
            },
            "maintain_vulnerability_program": {
                "5": "Protect all systems and networks from malicious software",
                "6": "Develop and maintain secure systems and software",
            },
            "access_control": {
                "7": "Restrict access to system components and cardholder data by business need to know",
                "8": "Identify users and authenticate access to system components",
                "9": "Restrict physical access to cardholder data",
            },
            "monitoring_testing": {
                "10": "Log and monitor all access to system components and cardholder data",
                "11": "Test security of systems and networks regularly",
            },
            "information_security": {
                "12": "Support information security with organizational policies and programs",
            },
        }

    @staticmethod
    def tokenization() -> Dict[str, Any]:
        """Tokenization vs encryption"""
        return {
            "tokenization": """
# Tokenization: Replace PAN with non-sensitive token
# Original: 4111-1111-1111-1111
# Token: tok_abc123xyz

# Benefits:
# - Token has no mathematical relationship to PAN
# - Reduces PCI scope (tokenized systems out of scope)
# - Can't reverse without token vault

# Implementation
def store_card(card_number: str) -> str:
    # Send to tokenization service (in PCI scope)
    token = tokenization_service.create_token(card_number)

    # Store only the token (out of PCI scope)
    db.execute("INSERT INTO payments (token) VALUES (?)", token)

    return token

def charge_card(token: str, amount: Decimal):
    # Payment processor handles detokenization
    return payment_gateway.charge(token=token, amount=amount)
            """,
            "encryption": """
# Encryption: Mathematically transform PAN
# Requires key management (still in PCI scope)

# BAD: Storing PAN directly
card_number = "4111111111111111"

# GOOD: Encrypt with approved algorithm
from cryptography.fernet import Fernet

key = load_encryption_key()  # Stored securely
cipher = Fernet(key)
encrypted_pan = cipher.encrypt(card_number.encode())

# Store encrypted, never plaintext
db.execute("INSERT INTO cards (encrypted_pan) VALUES (?)", encrypted_pan)
            """,
        }

    @staticmethod
    def logging_requirements() -> Dict[str, Any]:
        """Requirement 10: Logging"""
        return {
            "10.2": """
# 10.2 - Audit logs must capture:
# - User access to cardholder data
# - Actions by admin users
# - Access to audit logs
# - Invalid access attempts
# - Changes to authentication mechanisms
# - Initialization of audit logs
# - Creation/deletion of system objects

def log_pci_event(event_type: str, user_id: str, resource: str, details: dict):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "source_ip": request.remote_addr,
        "resource_accessed": resource,
        "outcome": details.get("outcome"),
        "details": details,
    }
    # Write to tamper-evident log
    audit_logger.info(json.dumps(log_entry))
            """,
            "retention": "Logs must be retained for at least 1 year, with 3 months immediately available",
        }

    @staticmethod
    def network_segmentation() -> Dict[str, Any]:
        """Network segmentation to reduce scope"""
        return {
            "cde_isolation": """
# Cardholder Data Environment (CDE) must be isolated

# BAD: Flat network
[All Servers] <---> [Internet]
# Everything in PCI scope!

# GOOD: Segmented network
[Internet]
    |
[DMZ - Web Servers]  <- Not in CDE
    |
[Firewall]
    |
[Internal Network]
    |
[Firewall]  <- Strict rules
    |
[CDE Network]  <- PCI scope
    - Payment processing
    - Card storage
    - Tokenization service
            """,
        }

    # =========================================================================
    # REQUIREMENT 1: NETWORK SECURITY CONTROLS
    # =========================================================================

    @staticmethod
    def requirement_1_network_security() -> Dict[str, Any]:
        """PCI-DSS Requirement 1: Install and maintain network security controls"""
        return {
            "1_2_firewall_configuration": {
                "description": "Network security controls restrict traffic to CDE",
                "bad": '''
# BAD: Overly permissive firewall rules
# Allow all inbound traffic to CDE
iptables -A INPUT -j ACCEPT
iptables -A FORWARD -j ACCEPT

# BAD: No outbound restrictions
iptables -A OUTPUT -j ACCEPT
                ''',
                "good": '''
# GOOD: Restrictive firewall configuration
from dataclasses import dataclass
from enum import Enum
from typing import List

class Protocol(Enum):
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"

@dataclass
class FirewallRule:
    rule_id: str
    description: str
    source: str
    destination: str
    port: int | str
    protocol: Protocol
    action: str  # allow, deny
    business_justification: str  # Required for PCI DSS

class CDEFirewallPolicy:
    """CDE Firewall policy with least privilege"""

    def __init__(self):
        self.rules: List[FirewallRule] = []

    def create_default_deny_policy(self):
        """Start with deny all, then allow specific traffic"""
        # Default deny all inbound
        self.rules.append(FirewallRule(
            rule_id="DENY-ALL-IN",
            description="Default deny all inbound traffic",
            source="0.0.0.0/0",
            destination="CDE",
            port="*",
            protocol=Protocol.TCP,
            action="deny",
            business_justification="PCI DSS 1.2.1 - Default deny"
        ))

        # Default deny all outbound
        self.rules.append(FirewallRule(
            rule_id="DENY-ALL-OUT",
            description="Default deny all outbound traffic",
            source="CDE",
            destination="0.0.0.0/0",
            port="*",
            protocol=Protocol.TCP,
            action="deny",
            business_justification="PCI DSS 1.2.1 - Default deny"
        ))

    def allow_payment_gateway(self):
        """Allow specific traffic to payment gateway"""
        self.rules.append(FirewallRule(
            rule_id="ALLOW-PAYMENT-GW",
            description="Allow HTTPS to payment gateway",
            source="payment-processor.internal",
            destination="payment-gateway.provider.com",
            port=443,
            protocol=Protocol.TCP,
            action="allow",
            business_justification="Required for payment processing per contract #12345"
        ))

    def allow_web_to_cde(self):
        """Allow web tier to communicate with CDE"""
        self.rules.append(FirewallRule(
            rule_id="ALLOW-WEB-CDE",
            description="Allow web tier to payment API",
            source="web-tier.internal",
            destination="payment-api.cde.internal",
            port=8443,
            protocol=Protocol.TCP,
            action="allow",
            business_justification="Web checkout requires payment API access"
        ))

    def export_iptables(self) -> str:
        """Export rules as iptables commands"""
        commands = ["# PCI DSS Compliant Firewall Rules"]
        commands.append("# Flush existing rules")
        commands.append("iptables -F")
        commands.append("iptables -X")
        commands.append("")
        commands.append("# Default policies")
        commands.append("iptables -P INPUT DROP")
        commands.append("iptables -P FORWARD DROP")
        commands.append("iptables -P OUTPUT DROP")
        commands.append("")
        commands.append("# Allow established connections")
        commands.append("iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
        commands.append("iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
        commands.append("")

        for rule in self.rules:
            if rule.action == "allow":
                cmd = f"iptables -A FORWARD -s {rule.source} -d {rule.destination} "
                cmd += f"-p {rule.protocol.value} --dport {rule.port} -j ACCEPT"
                commands.append(f"# {rule.description}")
                commands.append(f"# Justification: {rule.business_justification}")
                commands.append(cmd)
                commands.append("")

        return "\\n".join(commands)
                ''',
            },
            "1_4_connections_review": {
                "description": "Review connections to and from CDE at least every 6 months",
                "good": '''
# GOOD: Automated connection review
class ConnectionReviewService:
    REVIEW_FREQUENCY_DAYS = 180  # Every 6 months

    def conduct_review(self) -> dict:
        """Conduct semi-annual connection review"""
        review = {
            "review_id": f"CR-{datetime.now().strftime('%Y%m%d')}",
            "review_date": datetime.utcnow().isoformat(),
            "reviewer": current_user.id,
            "connections": [],
            "findings": []
        }

        # Get all firewall rules allowing CDE traffic
        cde_rules = firewall.get_rules(destination="CDE")

        for rule in cde_rules:
            connection = {
                "rule_id": rule.id,
                "source": rule.source,
                "destination": rule.destination,
                "port": rule.port,
                "business_justification": rule.business_justification,
                "last_traffic": self._get_last_traffic(rule),
                "still_needed": None  # To be filled by reviewer
            }
            review["connections"].append(connection)

            # Flag rules with no recent traffic
            if connection["last_traffic"] is None:
                review["findings"].append({
                    "type": "no_traffic",
                    "rule_id": rule.id,
                    "recommendation": "Review if connection still needed"
                })

            # Flag rules without justification
            if not rule.business_justification:
                review["findings"].append({
                    "type": "missing_justification",
                    "rule_id": rule.id,
                    "recommendation": "Document business justification"
                })

        db.save(ConnectionReview(**review))

        # Audit log
        audit_log.info(
            "CDE connection review completed",
            review_id=review["review_id"],
            connections_reviewed=len(review["connections"]),
            findings=len(review["findings"])
        )

        return review
                ''',
            },
        }

    # =========================================================================
    # REQUIREMENT 3: PROTECT STORED ACCOUNT DATA
    # =========================================================================

    @staticmethod
    def requirement_3_protect_stored_data() -> Dict[str, Any]:
        """PCI-DSS Requirement 3: Protect stored account data"""
        return {
            "3_2_do_not_store_sensitive_auth": {
                "description": "Do not store sensitive authentication data after authorization",
                "bad": '''
# BAD: Storing CVV (NEVER allowed!)
def store_payment(card_number, cvv, expiry):
    payment = Payment(
        card_number=card_number,
        cvv=cvv,  # CRITICAL VIOLATION!
        expiry=expiry
    )
    db.save(payment)

# BAD: Storing full track data
def process_swipe(track_data):
    transaction = Transaction(
        track1_data=track_data,  # CRITICAL VIOLATION!
    )
    db.save(transaction)

# BAD: Storing PIN or PIN block
def store_pin(encrypted_pin_block):
    db.execute("INSERT INTO pins (pin_block) VALUES (?)", encrypted_pin_block)
                ''',
                "good": '''
# GOOD: Never store sensitive authentication data
class PaymentProcessor:
    """PCI-compliant payment processor"""

    # Sensitive auth data that MUST NEVER be stored
    PROHIBITED_DATA = [
        "cvv", "cvc", "cvv2", "cvc2",  # Card verification codes
        "pin", "pin_block",             # PIN data
        "track1", "track2", "track_data" # Full magnetic stripe data
    ]

    def process_payment(self, payment_data: dict) -> dict:
        """Process payment without storing prohibited data"""
        # Validate no prohibited data in storage request
        for field in self.PROHIBITED_DATA:
            if field in payment_data:
                # Log security event
                audit_log.critical(
                    "Attempted to store prohibited data",
                    field=field,
                    source=request.remote_addr
                )
                raise SecurityError(f"Cannot store {field} per PCI DSS 3.2")

        # Use tokenization instead of storing PAN
        token = tokenization_service.tokenize(payment_data["card_number"])

        # Only store token and necessary data
        transaction = Transaction(
            token=token,
            last_four=payment_data["card_number"][-4:],
            card_brand=self._detect_brand(payment_data["card_number"]),
            expiry_month=payment_data["expiry_month"],
            expiry_year=payment_data["expiry_year"],
            amount=payment_data["amount"]
        )
        db.save(transaction)

        # Send to payment gateway with full data (in memory only)
        result = payment_gateway.authorize(
            card_number=payment_data["card_number"],
            cvv=payment_data["cvv"],  # Used for auth, never stored
            expiry=f"{payment_data['expiry_month']}/{payment_data['expiry_year']}",
            amount=payment_data["amount"]
        )

        return {
            "transaction_id": transaction.id,
            "token": token,
            "status": result.status
        }
                ''',
            },
            "3_4_render_pan_unreadable": {
                "description": "Render PAN unreadable wherever stored using strong cryptography",
                "good": '''
# GOOD: Strong encryption for PAN storage
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class PANEncryptionService:
    """AES-256-GCM encryption for PAN storage (PCI DSS 3.4)"""

    ALGORITHM = "AES-256-GCM"
    KEY_LENGTH = 32  # 256 bits
    NONCE_LENGTH = 12

    def __init__(self):
        self.key_service = KeyManagementService()

    def encrypt_pan(self, pan: str) -> dict:
        """Encrypt PAN with AES-256-GCM"""
        # Validate PAN format
        if not self._validate_pan(pan):
            raise ValueError("Invalid PAN format")

        # Get current encryption key from HSM/KMS
        key_id, key = self.key_service.get_current_key()

        # Generate random nonce
        nonce = os.urandom(self.NONCE_LENGTH)

        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, pan.encode(), None)

        # Return encrypted data with metadata
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "key_id": key_id,
            "algorithm": self.ALGORITHM
        }

    def decrypt_pan(self, encrypted_data: dict) -> str:
        """Decrypt PAN (requires proper authorization)"""
        # Verify caller has authorization
        if not self._check_decryption_auth():
            audit_log.warning(
                "Unauthorized PAN decryption attempt",
                user=current_user.id
            )
            raise PermissionError("Not authorized for PAN decryption")

        # Get key
        key = self.key_service.get_key(encrypted_data["key_id"])

        # Decrypt
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        nonce = base64.b64decode(encrypted_data["nonce"])

        aesgcm = AESGCM(key)
        pan = aesgcm.decrypt(nonce, ciphertext, None).decode()

        # Audit decryption
        audit_log.info(
            "PAN decrypted",
            user=current_user.id,
            key_id=encrypted_data["key_id"],
            purpose=request.headers.get("X-Decryption-Purpose")
        )

        return pan

    def _validate_pan(self, pan: str) -> bool:
        """Validate PAN with Luhn algorithm"""
        digits = [int(d) for d in pan if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False

        # Luhn algorithm
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0
                ''',
            },
            "3_5_key_management": {
                "description": "Protect cryptographic keys used to protect stored account data",
                "good": '''
# GOOD: PCI-compliant key management
from enum import Enum
from datetime import datetime, timedelta

class KeyType(Enum):
    KEK = "key_encryption_key"  # Master key
    DEK = "data_encryption_key"  # Data encryption key

class KeyStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"  # Can decrypt, cannot encrypt
    DESTROYED = "destroyed"

class KeyManagementService:
    """PCI DSS 3.5/3.6 compliant key management"""

    KEY_ROTATION_DAYS = 365  # Annual rotation per 3.6.4

    def __init__(self):
        # Production: Use HSM or Cloud KMS
        self.hsm = HSMClient(config.HSM_ADDRESS)

    def generate_dek(self) -> dict:
        """Generate new Data Encryption Key"""
        # Generate key in HSM (never leaves HSM in plaintext)
        key_id = self.hsm.generate_key(
            key_type="AES",
            key_length=256,
            extractable=False  # Key cannot be exported
        )

        key_record = {
            "key_id": key_id,
            "key_type": KeyType.DEK.value,
            "status": KeyStatus.ACTIVE.value,
            "created_at": datetime.utcnow(),
            "created_by": current_user.id,
            "expires_at": datetime.utcnow() + timedelta(days=self.KEY_ROTATION_DAYS),
            "rotation_due": datetime.utcnow() + timedelta(days=self.KEY_ROTATION_DAYS)
        }
        db.save(CryptoKey(**key_record))

        # Audit key generation
        audit_log.info(
            "DEK generated",
            key_id=key_id,
            created_by=current_user.id
        )

        return key_record

    def rotate_keys(self):
        """Rotate keys that are due (PCI DSS 3.6.4)"""
        due_keys = db.query(CryptoKey).filter(
            CryptoKey.status == KeyStatus.ACTIVE.value,
            CryptoKey.rotation_due <= datetime.utcnow()
        ).all()

        for old_key in due_keys:
            # Generate new key
            new_key = self.generate_dek()

            # Mark old key as deprecated (can still decrypt)
            old_key.status = KeyStatus.DEPRECATED.value
            old_key.deprecated_at = datetime.utcnow()
            old_key.replaced_by = new_key["key_id"]
            db.save(old_key)

            # Schedule re-encryption of data encrypted with old key
            self._schedule_reencryption(old_key.key_id, new_key["key_id"])

            audit_log.info(
                "Key rotated",
                old_key_id=old_key.key_id,
                new_key_id=new_key["key_id"]
            )

    def destroy_key(self, key_id: str):
        """Securely destroy key (PCI DSS 3.6.5)"""
        key = db.query(CryptoKey).get(key_id)

        # Verify no data still encrypted with this key
        if self._has_encrypted_data(key_id):
            raise ValueError("Cannot destroy key with active encrypted data")

        # Destroy in HSM (cryptographic erasure)
        self.hsm.destroy_key(key_id)

        # Update record
        key.status = KeyStatus.DESTROYED.value
        key.destroyed_at = datetime.utcnow()
        key.destroyed_by = current_user.id
        db.save(key)

        audit_log.info(
            "Key destroyed",
            key_id=key_id,
            destroyed_by=current_user.id
        )

    def split_key_knowledge(self, key_id: str, num_custodians: int = 3, threshold: int = 2):
        """Implement split knowledge (PCI DSS 3.6.6)"""
        # Split key using Shamir's Secret Sharing
        shares = shamir.split(
            self.hsm.export_key_for_backup(key_id),
            num_shares=num_custodians,
            threshold=threshold
        )

        # Each custodian gets one share
        for i, share in enumerate(shares):
            custodian = key_custodians[i]
            # Encrypt share for custodian
            encrypted_share = self._encrypt_for_custodian(share, custodian)

            db.save(KeyShare(
                key_id=key_id,
                custodian_id=custodian.id,
                share_index=i,
                encrypted_share=encrypted_share
            ))

            # Notify custodian
            notification_service.send(
                to=custodian.email,
                template="key_share_assigned",
                data={"key_id": key_id}
            )

        audit_log.info(
            "Key split among custodians",
            key_id=key_id,
            num_custodians=num_custodians,
            threshold=threshold
        )
                ''',
            },
        }

    # =========================================================================
    # REQUIREMENT 6: DEVELOP SECURE SYSTEMS
    # =========================================================================

    @staticmethod
    def requirement_6_secure_development() -> Dict[str, Any]:
        """PCI-DSS Requirement 6: Develop and maintain secure systems and software"""
        return {
            "6_2_security_patches": {
                "description": "Apply security patches within one month of release",
                "good": '''
# GOOD: Patch management process
class PatchManagementService:
    CRITICAL_PATCH_SLA_DAYS = 7
    HIGH_PATCH_SLA_DAYS = 14
    MEDIUM_PATCH_SLA_DAYS = 30
    LOW_PATCH_SLA_DAYS = 90

    def scan_for_patches(self) -> list:
        """Scan systems for missing security patches"""
        findings = []

        for system in infrastructure.get_all_systems():
            # Check for OS patches
            os_patches = self._check_os_patches(system)
            for patch in os_patches:
                finding = {
                    "system_id": system.id,
                    "patch_id": patch.id,
                    "severity": patch.severity,
                    "published_date": patch.published_date,
                    "sla_days": self._get_sla(patch.severity),
                    "due_date": patch.published_date + timedelta(
                        days=self._get_sla(patch.severity)
                    ),
                    "overdue": datetime.utcnow() > patch.published_date + timedelta(
                        days=self._get_sla(patch.severity)
                    )
                }
                findings.append(finding)

            # Check for application patches
            app_patches = self._check_application_patches(system)
            findings.extend(app_patches)

        # Create remediation tickets for overdue patches
        for finding in findings:
            if finding["overdue"]:
                ticket_service.create_ticket(
                    title=f"Overdue patch: {finding['patch_id']}",
                    severity="HIGH",
                    description=f"Patch {finding['patch_id']} is overdue on {finding['system_id']}",
                    compliance_requirement="PCI DSS 6.2"
                )

                # Alert security team
                alert_service.send(
                    severity="high",
                    title=f"Overdue security patch",
                    details=finding
                )

        return findings

    def _get_sla(self, severity: str) -> int:
        return {
            "CRITICAL": self.CRITICAL_PATCH_SLA_DAYS,
            "HIGH": self.HIGH_PATCH_SLA_DAYS,
            "MEDIUM": self.MEDIUM_PATCH_SLA_DAYS,
            "LOW": self.LOW_PATCH_SLA_DAYS
        }.get(severity, self.MEDIUM_PATCH_SLA_DAYS)
                ''',
            },
            "6_3_secure_coding": {
                "description": "Develop software securely following industry standards",
                "good": '''
# GOOD: Secure coding practices
from dataclasses import dataclass
from typing import Optional

# OWASP Top 10 Prevention

# 1. Injection Prevention
class SecureQueryBuilder:
    """Prevent SQL Injection"""

    def get_transaction(self, transaction_id: str) -> Optional[dict]:
        # BAD: String concatenation
        # query = f"SELECT * FROM transactions WHERE id = '{transaction_id}'"

        # GOOD: Parameterized queries
        return db.execute(
            "SELECT * FROM transactions WHERE id = %s",
            (transaction_id,)
        ).fetchone()

    def search_transactions(self, filters: dict) -> list:
        """Safe dynamic query building"""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if "amount_min" in filters:
            query += " AND amount >= %s"
            params.append(filters["amount_min"])

        if "amount_max" in filters:
            query += " AND amount <= %s"
            params.append(filters["amount_max"])

        if "status" in filters:
            query += " AND status = %s"
            params.append(filters["status"])

        return db.execute(query, tuple(params)).fetchall()

# 2. XSS Prevention
from markupsafe import escape
from bleach import clean

class SecureOutput:
    """Prevent Cross-Site Scripting"""

    @staticmethod
    def escape_html(content: str) -> str:
        """Escape HTML entities"""
        return escape(content)

    @staticmethod
    def sanitize_html(content: str, allowed_tags: list = None) -> str:
        """Sanitize HTML, allowing only safe tags"""
        allowed_tags = allowed_tags or ["p", "br", "strong", "em"]
        return clean(content, tags=allowed_tags, strip=True)

# 3. Broken Authentication Prevention
from secrets import compare_digest
import bcrypt

class SecureAuth:
    """Prevent authentication vulnerabilities"""

    MIN_PASSWORD_LENGTH = 12
    BCRYPT_ROUNDS = 12
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

    def hash_password(self, password: str) -> str:
        """Securely hash password"""
        return bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt(self.BCRYPT_ROUNDS)
        ).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Timing-safe password verification"""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def check_rate_limit(self, user_id: str) -> bool:
        """Check for brute force attempts"""
        attempts = redis.get(f"login_attempts:{user_id}")

        if attempts and int(attempts) >= self.MAX_LOGIN_ATTEMPTS:
            lockout_ttl = redis.ttl(f"login_attempts:{user_id}")
            raise RateLimitError(
                f"Account locked. Try again in {lockout_ttl} seconds"
            )
        return True

    def record_failed_attempt(self, user_id: str):
        """Record failed login attempt"""
        key = f"login_attempts:{user_id}"
        redis.incr(key)
        redis.expire(key, self.LOCKOUT_DURATION_MINUTES * 60)

# 4. CSRF Prevention
from secrets import token_urlsafe

class CSRFProtection:
    """Prevent Cross-Site Request Forgery"""

    TOKEN_LENGTH = 32

    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        token = token_urlsafe(self.TOKEN_LENGTH)
        redis.setex(
            f"csrf:{session_id}",
            3600,  # 1 hour expiry
            token
        )
        return token

    def validate_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token"""
        stored_token = redis.get(f"csrf:{session_id}")

        if not stored_token:
            return False

        # Timing-safe comparison
        return compare_digest(stored_token, token)
                ''',
            },
            "6_4_change_control": {
                "description": "Follow change control processes for system changes",
                "good": '''
# GOOD: PCI-compliant change control
class PCIChangeControl:
    """Change control for PCI DSS 6.4"""

    def submit_change(
        self,
        description: str,
        change_type: str,
        affected_systems: list[str],
        testing_plan: str,
        rollback_plan: str,
        submitter_id: str
    ) -> dict:
        """Submit change request"""
        # Determine if CDE systems affected
        cde_affected = any(
            system in self._get_cde_systems()
            for system in affected_systems
        )

        change = {
            "id": f"CHG-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            "description": description,
            "change_type": change_type,
            "affected_systems": affected_systems,
            "cde_affected": cde_affected,
            "testing_plan": testing_plan,
            "rollback_plan": rollback_plan,
            "submitter_id": submitter_id,
            "status": "pending_review",
            "created_at": datetime.utcnow(),
            "approvals_required": self._get_required_approvals(cde_affected),
            "approvals_received": []
        }
        db.save(ChangeRequest(**change))

        # Changes affecting CDE require additional security review
        if cde_affected:
            security_review_service.create_review(
                subject_type="change_request",
                subject_id=change["id"],
                priority="high"
            )

        return change

    def approve_change(
        self,
        change_id: str,
        approver_id: str,
        approval_type: str  # technical, security, management
    ):
        """Approve change request"""
        change = db.query(ChangeRequest).get(change_id)
        approver = db.query(User).get(approver_id)

        # Verify approver authorization
        if not self._can_approve(approver, approval_type, change.cde_affected):
            raise PermissionError(f"Not authorized for {approval_type} approval")

        # Submitter cannot approve own change
        if change.submitter_id == approver_id:
            raise PermissionError("Cannot approve own change request")

        change.approvals_received.append({
            "type": approval_type,
            "approver_id": approver_id,
            "approved_at": datetime.utcnow().isoformat()
        })

        # Check if all required approvals received
        if self._all_approvals_received(change):
            change.status = "approved"

        db.save(change)

        # Audit trail
        audit_log.info(
            "Change approved",
            change_id=change_id,
            approver=approver_id,
            approval_type=approval_type
        )

    def verify_separation_of_duties(self, change_id: str) -> bool:
        """Verify development/production separation (PCI DSS 6.4.2)"""
        change = db.query(ChangeRequest).get(change_id)

        # Developer should not have production access
        developer = db.query(User).get(change.submitter_id)

        if "production_access" in developer.permissions:
            audit_log.warning(
                "Separation of duties violation",
                change_id=change_id,
                developer=developer.id
            )
            return False

        # Deployer should not be the developer
        deployer = change.deployed_by
        if deployer == change.submitter_id:
            audit_log.warning(
                "Same person developed and deployed",
                change_id=change_id,
                user=deployer
            )
            return False

        return True
                ''',
            },
        }

    # =========================================================================
    # REQUIREMENT 8: IDENTIFY AND AUTHENTICATE ACCESS
    # =========================================================================

    @staticmethod
    def requirement_8_authentication() -> Dict[str, Any]:
        """PCI-DSS Requirement 8: Identify users and authenticate access"""
        return {
            "8_2_user_identification": {
                "description": "Assign unique ID to each person with computer access",
                "bad": '''
# BAD: Shared accounts
def authenticate_service():
    # Using shared service account for multiple users
    return connect_database(
        user="shared_service_account",
        password="ServicePass123"
    )

# BAD: Generic admin accounts
admin_user = "admin"
admin_password = get_env("ADMIN_PASSWORD")
                ''',
                "good": '''
# GOOD: Unique identification for all users
class UserIdentityService:
    """PCI DSS 8.2 compliant user identification"""

    def create_user(self, user_data: dict) -> User:
        """Create user with unique identifier"""
        # Generate unique user ID
        user_id = self._generate_unique_id(user_data["email"])

        user = User(
            id=user_id,
            email=user_data["email"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            department=user_data["department"],
            manager_id=user_data["manager_id"],
            created_at=datetime.utcnow(),
            created_by=current_user.id
        )
        db.save(user)

        # Audit user creation
        audit_log.info(
            "User created",
            user_id=user_id,
            created_by=current_user.id
        )

        return user

    def create_service_account(
        self,
        service_name: str,
        owner_id: str,
        justification: str
    ) -> ServiceAccount:
        """Create service account with individual ownership"""
        service_account = ServiceAccount(
            id=f"svc-{service_name}-{generate_uuid()[:8]}",
            service_name=service_name,
            owner_id=owner_id,  # Individual owner required
            justification=justification,
            created_at=datetime.utcnow(),
            review_due=datetime.utcnow() + timedelta(days=90)
        )
        db.save(service_account)

        # Service accounts require quarterly review
        schedule_task(
            "review_service_account",
            service_account.id,
            schedule=timedelta(days=90)
        )

        audit_log.info(
            "Service account created",
            account_id=service_account.id,
            owner=owner_id
        )

        return service_account
                ''',
            },
            "8_3_mfa_for_cde": {
                "description": "Implement MFA for all access into CDE",
                "good": '''
# GOOD: MFA for CDE access
class CDEAccessControl:
    """MFA required for all CDE access (PCI DSS 8.3)"""

    def authenticate_cde_access(
        self,
        user_id: str,
        password: str,
        mfa_code: str
    ) -> dict:
        """Authenticate user for CDE access"""
        user = db.query(User).get(user_id)

        # Step 1: Verify password
        if not verify_password(password, user.password_hash):
            self._record_failed_attempt(user_id, "password")
            raise AuthenticationError("Invalid credentials")

        # Step 2: Verify MFA (REQUIRED for CDE)
        if not mfa_service.verify(user_id, mfa_code):
            self._record_failed_attempt(user_id, "mfa")
            raise AuthenticationError("Invalid MFA code")

        # Step 3: Check user is authorized for CDE access
        if not self._has_cde_access(user_id):
            audit_log.warning(
                "Unauthorized CDE access attempt",
                user_id=user_id
            )
            raise AuthorizationError("Not authorized for CDE access")

        # Create session with CDE flag
        session = create_session(
            user_id=user_id,
            cde_access=True,
            expires_in=3600  # 1 hour for CDE sessions
        )

        audit_log.info(
            "CDE access granted",
            user_id=user_id,
            session_id=session.id,
            mfa_method=user.mfa_method
        )

        return {
            "session_id": session.id,
            "expires_at": session.expires_at
        }

    def _has_cde_access(self, user_id: str) -> bool:
        """Check if user is authorized for CDE access"""
        user = db.query(User).get(user_id)

        # Must have explicit CDE role
        cde_roles = ["cde_admin", "cde_operator", "cde_support"]
        return any(role.name in cde_roles for role in user.roles)
                ''',
            },
            "8_6_password_policy": {
                "description": "Set password requirements",
                "good": '''
# GOOD: PCI-compliant password policy
class PCIPasswordPolicy:
    """Password policy per PCI DSS 8.3.6"""

    MIN_LENGTH = 12  # PCI DSS 4.0 recommends 12+
    REQUIRE_COMPLEXITY = True
    MAX_AGE_DAYS = 90
    HISTORY_COUNT = 4  # Cannot reuse last 4 passwords
    LOCKOUT_THRESHOLD = 6
    LOCKOUT_DURATION_MINUTES = 30
    SESSION_IDLE_TIMEOUT_MINUTES = 15

    def validate_password(self, password: str, user_id: str = None) -> tuple[bool, list]:
        """Validate password against policy"""
        errors = []

        # Length check
        if len(password) < self.MIN_LENGTH:
            errors.append(f"Password must be at least {self.MIN_LENGTH} characters")

        # Complexity check
        if self.REQUIRE_COMPLEXITY:
            if not re.search(r'[A-Z]', password):
                errors.append("Must contain uppercase letter")
            if not re.search(r'[a-z]', password):
                errors.append("Must contain lowercase letter")
            if not re.search(r'\d', password):
                errors.append("Must contain number")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                errors.append("Must contain special character")

        # Check password history
        if user_id:
            if self._in_password_history(user_id, password):
                errors.append(f"Cannot reuse last {self.HISTORY_COUNT} passwords")

        return len(errors) == 0, errors

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ):
        """Change password with policy enforcement"""
        user = db.query(User).get(user_id)

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password incorrect")

        # Validate new password
        valid, errors = self.validate_password(new_password, user_id)
        if not valid:
            raise ValidationError(errors)

        # Hash and store new password
        new_hash = hash_password(new_password)

        # Add to password history
        self._add_to_history(user_id, user.password_hash)

        # Update password
        user.password_hash = new_hash
        user.password_changed_at = datetime.utcnow()
        user.must_change_password = False
        db.save(user)

        # Audit log
        audit_log.info(
            "Password changed",
            user_id=user_id
        )

    def enforce_password_expiry(self):
        """Force password change for expired passwords"""
        cutoff = datetime.utcnow() - timedelta(days=self.MAX_AGE_DAYS)

        expired_users = db.query(User).filter(
            User.password_changed_at < cutoff,
            User.is_active == True
        ).all()

        for user in expired_users:
            user.must_change_password = True
            db.save(user)

            notification_service.send(
                to=user.email,
                template="password_expired",
                data={"user": user}
            )
                ''',
            },
        }

    # =========================================================================
    # REQUIREMENT 10: LOGGING AND MONITORING
    # =========================================================================

    @staticmethod
    def requirement_10_logging() -> Dict[str, Any]:
        """PCI-DSS Requirement 10: Log and monitor all access"""
        return {
            "10_2_audit_events": {
                "description": "Implement automated audit trails for all system components",
                "good": '''
# GOOD: Comprehensive audit logging for PCI DSS 10.2
class PCIAuditLogger:
    """Audit logging per PCI DSS 10.2"""

    REQUIRED_EVENTS = [
        "user_access_cardholder_data",      # 10.2.1
        "admin_action",                      # 10.2.2
        "audit_log_access",                  # 10.2.3
        "invalid_access_attempt",            # 10.2.4
        "auth_mechanism_change",             # 10.2.5
        "audit_log_init_stop",              # 10.2.6
        "system_object_create_delete",      # 10.2.7
    ]

    def log_cardholder_data_access(
        self,
        user_id: str,
        action: str,  # read, create, update, delete
        resource: str,
        record_ids: list[str]
    ):
        """10.2.1 - Log all individual user accesses to cardholder data"""
        self._log_event(
            event_type="user_access_cardholder_data",
            user_id=user_id,
            action=action,
            resource=resource,
            details={
                "record_count": len(record_ids),
                "record_ids": record_ids[:10]  # Log first 10 IDs
            }
        )

    def log_admin_action(
        self,
        user_id: str,
        action: str,
        target: str,
        details: dict
    ):
        """10.2.2 - Log all actions taken by admin users"""
        self._log_event(
            event_type="admin_action",
            user_id=user_id,
            action=action,
            resource=target,
            details=details
        )

    def log_invalid_access(
        self,
        user_id: str,
        resource: str,
        reason: str
    ):
        """10.2.4 - Log invalid logical access attempts"""
        self._log_event(
            event_type="invalid_access_attempt",
            user_id=user_id,
            action="access_denied",
            resource=resource,
            details={"reason": reason}
        )

    def _log_event(
        self,
        event_type: str,
        user_id: str,
        action: str,
        resource: str,
        details: dict = None
    ):
        """Create audit log entry with required fields"""
        event = {
            # 10.3.1 - User identification
            "user_id": user_id,
            # 10.3.2 - Type of event
            "event_type": event_type,
            # 10.3.3 - Date and time
            "timestamp": datetime.utcnow().isoformat(),
            # 10.3.4 - Success/failure indication
            "success": action != "access_denied",
            # 10.3.5 - Origination of event
            "source_ip": request.remote_addr if request else None,
            "source_hostname": socket.gethostname(),
            # 10.3.6 - Identity/name of affected data
            "resource": resource,
            "action": action,
            "details": details or {},
            # Additional context
            "session_id": get_session_id(),
            "request_id": get_request_id()
        }

        # Write to secure, tamper-evident log
        secure_logger.info(json.dumps(event))

        # Also send to SIEM for real-time monitoring
        siem.send_event(event)
                ''',
            },
            "10_4_time_sync": {
                "description": "Synchronize all critical system clocks",
                "good": '''
# GOOD: Time synchronization (PCI DSS 10.4)
class TimeSyncService:
    """NTP configuration for PCI DSS 10.4"""

    NTP_SERVERS = [
        "0.pool.ntp.org",
        "1.pool.ntp.org",
        "time.google.com"
    ]

    def configure_ntp(self):
        """Configure NTP on all systems"""
        ntp_config = """
# /etc/ntp.conf - PCI DSS 10.4 compliant
# Use multiple NTP sources for redundancy
server 0.pool.ntp.org iburst
server 1.pool.ntp.org iburst
server time.google.com iburst

# Restrict access
restrict default nomodify notrap nopeer noquery
restrict 127.0.0.1
restrict ::1

# Enable logging
logfile /var/log/ntpd.log
statsdir /var/log/ntpstats/
"""
        return ntp_config

    def verify_time_sync(self) -> dict:
        """Verify all systems are time-synchronized"""
        results = {
            "checked_at": datetime.utcnow().isoformat(),
            "systems": [],
            "out_of_sync": []
        }

        reference_time = datetime.utcnow()

        for system in infrastructure.get_all_systems():
            system_time = system.get_current_time()
            drift_seconds = abs((system_time - reference_time).total_seconds())

            system_result = {
                "system_id": system.id,
                "system_time": system_time.isoformat(),
                "drift_seconds": drift_seconds,
                "in_sync": drift_seconds < 1  # Within 1 second
            }
            results["systems"].append(system_result)

            if not system_result["in_sync"]:
                results["out_of_sync"].append(system.id)

                # Alert on time drift
                alert_service.send(
                    severity="high",
                    title=f"Time sync drift detected: {system.id}",
                    details=system_result
                )

        # Audit log
        audit_log.info(
            "Time sync verification",
            systems_checked=len(results["systems"]),
            out_of_sync=len(results["out_of_sync"])
        )

        return results
                ''',
            },
            "10_7_log_retention": {
                "description": "Retain audit trail history for at least one year",
                "good": '''
# GOOD: Log retention policy (PCI DSS 10.7)
class LogRetentionService:
    """Log retention per PCI DSS 10.7"""

    IMMEDIATE_ACCESS_DAYS = 90  # 3 months immediately available
    TOTAL_RETENTION_DAYS = 365  # 1 year total retention

    def archive_logs(self):
        """Archive logs older than immediate access period"""
        cutoff = datetime.utcnow() - timedelta(days=self.IMMEDIATE_ACCESS_DAYS)

        logs_to_archive = db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff,
            AuditLog.archived == False
        ).all()

        for batch in chunk(logs_to_archive, 10000):
            # Create compressed archive
            archive_path = self._create_archive(batch)

            # Calculate hash for integrity
            archive_hash = self._calculate_hash(archive_path)

            # Upload to secure, immutable storage
            storage_location = archive_storage.upload(
                archive_path,
                bucket=config.LOG_ARCHIVE_BUCKET,
                storage_class="STANDARD_IA"  # Infrequent access
            )

            # Record archive metadata
            archive_record = {
                "id": generate_uuid(),
                "start_date": min(l.timestamp for l in batch).isoformat(),
                "end_date": max(l.timestamp for l in batch).isoformat(),
                "record_count": len(batch),
                "storage_location": storage_location,
                "hash": archive_hash,
                "archived_at": datetime.utcnow()
            }
            db.save(LogArchive(**archive_record))

            # Mark logs as archived
            for log in batch:
                log.archived = True
                log.archive_id = archive_record["id"]
            db.commit()

        audit_log.info(
            "Logs archived",
            count=len(logs_to_archive)
        )

    def verify_log_integrity(self):
        """Verify archived log integrity (10.5.5)"""
        archives = db.query(LogArchive).filter(
            LogArchive.last_verified < datetime.utcnow() - timedelta(days=30)
        ).all()

        for archive in archives:
            # Download and verify hash
            archive_data = archive_storage.download(archive.storage_location)
            current_hash = self._calculate_hash(archive_data)

            if current_hash != archive.hash:
                # CRITICAL: Log tampering detected
                alert_service.send(
                    severity="critical",
                    title="Log archive integrity violation",
                    details={
                        "archive_id": archive.id,
                        "expected_hash": archive.hash,
                        "actual_hash": current_hash
                    }
                )
            else:
                archive.last_verified = datetime.utcnow()
                db.save(archive)
                ''',
            },
        }

    # =========================================================================
    # SAQ TYPES
    # =========================================================================

    @staticmethod
    def saq_types() -> Dict[str, Any]:
        """Self-Assessment Questionnaire types"""
        return {
            "saq_a": {
                "description": "Card-not-present merchants, all cardholder data functions outsourced",
                "applicable_to": [
                    "E-commerce with hosted payment page (iframe)",
                    "Mail/telephone order with outsourced processing",
                ],
                "requirements": "Shortest SAQ, ~20 questions",
            },
            "saq_a_ep": {
                "description": "E-commerce merchants with website that impacts payment security",
                "applicable_to": [
                    "E-commerce with redirect to payment processor",
                    "E-commerce with JavaScript from payment processor",
                ],
                "requirements": "More questions than SAQ A, focuses on website security",
            },
            "saq_b": {
                "description": "Merchants with only imprint machines or standalone terminals",
                "applicable_to": [
                    "Standalone, dial-out terminals (no IP connectivity)",
                    "Imprint machines only",
                ],
                "requirements": "Physical security focused",
            },
            "saq_c": {
                "description": "Merchants with payment application systems connected to internet",
                "applicable_to": [
                    "Web-based virtual terminals",
                    "Payment applications on IP-connected systems",
                ],
                "requirements": "Network security and application security",
            },
            "saq_d": {
                "description": "All other merchants and all service providers",
                "applicable_to": [
                    "Merchants storing cardholder data",
                    "Service providers",
                    "Complex environments",
                ],
                "requirements": "Full PCI DSS assessment (~400 questions)",
            },
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        requirement: str,
        sub_requirement: str,
        current_state: str,
        compliant_state: str,
    ) -> PCIDSSFinding:
        """Generate a structured PCI-DSS finding"""
        return PCIDSSFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            requirement=requirement,
            sub_requirement=sub_requirement,
            current_state=current_state,
            compliant_state=compliant_state,
            remediation={
                "effort": "HIGH" if severity in ["CRITICAL", "HIGH"] else "MEDIUM",
                "priority": severity,
                "timeline": "Immediate" if severity == "CRITICAL" else "30 days"
            }
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for PCI-DSS compliance"""
        return [
            {
                "name": "Qualys PCI",
                "command": "qualys-scan --profile pci-dss",
                "description": "PCI ASV vulnerability scanning"
            },
            {
                "name": "Nessus",
                "command": "nessuscli scan --policy pci-internal",
                "description": "Internal vulnerability scanning"
            },
            {
                "name": "OpenSCAP",
                "command": "oscap xccdf eval --profile pci-dss --report report.html content.xml",
                "description": "Configuration compliance scanning"
            },
            {
                "name": "OWASP ZAP",
                "command": "zap-cli quick-scan --spider -r https://app.example.com",
                "description": "Web application security testing"
            },
            {
                "name": "Trivy",
                "command": "trivy image --severity CRITICAL,HIGH payment-app:latest",
                "description": "Container vulnerability scanning"
            },
            {
                "name": "git-secrets",
                "command": "git secrets --scan",
                "description": "Detect secrets in code (PAN, credentials)"
            },
        ]


def create_enhanced_pci_dss_assistant():
    """Factory function to create Enhanced PCI-DSS Compliance Assistant"""
    return {
        "name": "Enhanced PCI-DSS Compliance Reviewer",
        "version": "2.0.0",
        "system_prompt": """You are an expert PCI-DSS v4.0 compliance specialist with comprehensive
knowledge of payment card security standards. Your expertise covers:

PCI-DSS REQUIREMENTS (1-12):
1. Install and maintain network security controls
2. Apply secure configurations to all system components
3. Protect stored account data (encryption, tokenization, key management)
4. Protect cardholder data with strong cryptography during transmission
5. Protect all systems and networks from malicious software
6. Develop and maintain secure systems and software
7. Restrict access to system components and cardholder data by business need to know
8. Identify users and authenticate access to system components
9. Restrict physical access to cardholder data
10. Log and monitor all access to system components and cardholder data
11. Test security of systems and networks regularly
12. Support information security with organizational policies and programs

TECHNICAL EXPERTISE:
- Cardholder Data Environment (CDE) scoping and segmentation
- Tokenization vs encryption for PAN storage
- Key management and cryptographic controls (AES-256, HSM)
- Network segmentation and firewall configuration
- Vulnerability management and penetration testing
- Authentication and MFA requirements
- Audit logging and log retention (10.x requirements)
- Secure coding practices and code review

SAQ EXPERTISE:
- SAQ A: Card-not-present, all functions outsourced
- SAQ A-EP: E-commerce merchants with website security impact
- SAQ B: Imprint machines or standalone terminals
- SAQ C: Payment applications connected to internet
- SAQ D: Full assessment for complex environments

Analyze systems, code, and configurations for PCI-DSS compliance gaps.
Provide specific, actionable findings with requirement references and remediation guidance.

Format findings with PCI-DSS requirement numbers and severity levels.""",
        "assistant_class": EnhancedPCIDSSAssistant,
        "finding_model": PCIDSSFinding,
        "domain": "compliance",
        "subdomain": "pci-dss",
        "tags": ["pci-dss", "payment", "security", "compliance", "tokenization", "encryption"],
        "tools": EnhancedPCIDSSAssistant.get_tool_recommendations(),
        "capabilities": [
            "requirement_assessment",
            "cde_scoping",
            "vulnerability_analysis",
            "encryption_review",
            "network_segmentation_review",
            "saq_determination"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedPCIDSSAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate requirements overview
    print("--- PCI-DSS 12 Requirements Overview ---")
    requirements = assistant.requirements_overview()
    for group, reqs in requirements.items():
        print(f"\n{group.replace('_', ' ').title()}:")
        for num, desc in reqs.items():
            print(f"  Requirement {num}: {desc[:60]}...")

    # Show tokenization vs encryption
    print("\n--- Tokenization vs Encryption ---")
    token_enc = assistant.tokenization()
    print("Tokenization: Replace PAN with non-sensitive token")
    print("Encryption: Mathematically transform PAN with key management")

    # Show network segmentation
    print("\n--- Network Segmentation ---")
    segmentation = assistant.network_segmentation()
    print("CDE must be isolated from non-CDE systems")

    # Show Requirement 1 - Network Security
    print("\n--- Requirement 1: Network Security Controls ---")
    req1 = assistant.requirement_1_network_security()
    for control_id, details in req1.items():
        print(f"\n{control_id}: {details['description']}")

    # Show Requirement 3 - Protect Stored Data
    print("\n--- Requirement 3: Protect Stored Account Data ---")
    req3 = assistant.requirement_3_protect_stored_data()
    for control_id, details in req3.items():
        print(f"\n{control_id}: {details['description']}")

    # Show Requirement 6 - Secure Development
    print("\n--- Requirement 6: Develop Secure Systems ---")
    req6 = assistant.requirement_6_secure_development()
    for control_id, details in req6.items():
        print(f"\n{control_id}: {details['description']}")

    # Show Requirement 8 - Authentication
    print("\n--- Requirement 8: Identify and Authenticate ---")
    req8 = assistant.requirement_8_authentication()
    for control_id, details in req8.items():
        print(f"\n{control_id}: {details['description']}")

    # Show Requirement 10 - Logging
    print("\n--- Requirement 10: Logging and Monitoring ---")
    req10 = assistant.requirement_10_logging()
    for control_id, details in req10.items():
        print(f"\n{control_id}: {details['description']}")

    # Show SAQ types
    print("\n--- SAQ Types ---")
    saqs = assistant.saq_types()
    for saq_type, details in saqs.items():
        print(f"\n{saq_type.upper().replace('_', ' ')}: {details['description']}")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="PCI-001",
        title="Unencrypted PAN Storage Detected",
        severity="CRITICAL",
        requirement="3",
        sub_requirement="3.4",
        current_state="PAN stored in plaintext in database",
        compliant_state="PAN must be rendered unreadable using strong cryptography (AES-256)"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Requirement: {finding.requirement}.{finding.sub_requirement}")
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
    config = create_enhanced_pci_dss_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
