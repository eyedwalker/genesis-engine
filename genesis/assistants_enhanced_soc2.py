"""
Enhanced SOC 2 Compliance Reviewer

Comprehensive SOC 2 compliance covering:
- Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy)
- Type I vs Type II audits
- Evidence collection
- Control testing procedures
- Common Criteria mapping

References:
- AICPA Trust Service Criteria
- SOC 2 Reporting Framework
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SOC2Finding(BaseModel):
    finding_id: str = Field(...)
    title: str = Field(...)
    severity: str = Field(...)
    trust_criteria: str = Field(default="", description="Security/Availability/etc.")
    control_objective: str = Field(default="")
    current_state: str = Field(default="")
    required_state: str = Field(default="")
    evidence_needed: List[str] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedSOC2Assistant:
    """Enhanced SOC 2 Compliance Reviewer"""

    def __init__(self):
        self.name = "Enhanced SOC 2 Compliance Reviewer"
        self.version = "2.0.0"
        self.standards = ["SOC 2", "AICPA TSC"]

    @staticmethod
    def trust_service_criteria() -> Dict[str, Any]:
        """SOC 2 Trust Service Criteria"""
        return {
            "security": {
                "required": True,
                "description": "Protection against unauthorized access",
                "common_criteria": [
                    "CC1 - Control Environment",
                    "CC2 - Communication and Information",
                    "CC3 - Risk Assessment",
                    "CC4 - Monitoring Activities",
                    "CC5 - Control Activities",
                    "CC6 - Logical and Physical Access Controls",
                    "CC7 - System Operations",
                    "CC8 - Change Management",
                    "CC9 - Risk Mitigation",
                ],
                "controls_example": """
# CC6.1 - Logical Access Security
# Control: Access to systems requires multi-factor authentication

# Evidence needed:
1. MFA configuration screenshots
2. Access control policy document
3. User access review logs (quarterly)
4. Terminated user deprovisioning records
                """,
            },
            "availability": {
                "required": False,
                "description": "System is available for operation as committed",
                "controls_example": """
# A1.1 - Capacity Planning
# Control: System capacity is monitored and maintained

# Evidence needed:
1. Capacity monitoring dashboards
2. Auto-scaling configuration
3. Incident response for outages
4. SLA documentation and metrics
                """,
            },
            "processing_integrity": {
                "required": False,
                "description": "System processing is complete, valid, accurate, timely",
                "controls_example": """
# PI1.1 - Data Validation
# Control: Input data is validated before processing

# Evidence needed:
1. Input validation code/configuration
2. Error handling procedures
3. Data reconciliation reports
                """,
            },
            "confidentiality": {
                "required": False,
                "description": "Information designated as confidential is protected",
                "controls_example": """
# C1.1 - Data Classification
# Control: Confidential data is identified and classified

# Evidence needed:
1. Data classification policy
2. Encryption configuration (at rest and in transit)
3. Access controls for confidential data
                """,
            },
            "privacy": {
                "required": False,
                "description": "Personal information is collected, used, retained, disclosed per privacy notice",
                "note": "Overlaps with GDPR compliance",
            },
        }

    @staticmethod
    def type_comparison() -> Dict[str, Any]:
        """Type I vs Type II audits"""
        return {
            "type_i": {
                "description": "Point-in-time assessment",
                "duration": "Single date",
                "what_tested": "Design of controls",
                "use_case": "First-time SOC 2, quick compliance proof",
            },
            "type_ii": {
                "description": "Period assessment (usually 6-12 months)",
                "duration": "3-12 months observation period",
                "what_tested": "Design AND operating effectiveness",
                "use_case": "Mature organizations, customer requirements",
            },
        }

    # =========================================================================
    # SECURITY CONTROLS (CC6)
    # =========================================================================

    @staticmethod
    def logical_access_controls() -> Dict[str, Any]:
        """CC6 - Logical and Physical Access Controls"""
        return {
            "cc6_1_access_security": {
                "description": "Entity implements logical access security measures",
                "bad": '''
# BAD: No password policy enforcement
def create_user(username: str, password: str):
    # No password requirements!
    user = User(username=username, password=hash_password(password))
    db.save(user)
    return user

# BAD: No MFA implementation
def authenticate(username: str, password: str):
    user = db.query(User).filter_by(username=username).first()
    if check_password(password, user.password):
        return create_session(user)  # Direct access without MFA
    raise AuthError("Invalid credentials")
                ''',
                "good": '''
# GOOD: Password policy enforcement
from pydantic import validator
import re

class PasswordPolicy:
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL = True
    BREACHED_PASSWORD_CHECK = True

def validate_password(password: str) -> tuple[bool, list[str]]:
    """Validate password against policy"""
    errors = []

    if len(password) < PasswordPolicy.MIN_LENGTH:
        errors.append(f"Password must be at least {PasswordPolicy.MIN_LENGTH} characters")

    if PasswordPolicy.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")

    if PasswordPolicy.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")

    if PasswordPolicy.REQUIRE_NUMBERS and not re.search(r'\d', password):
        errors.append("Password must contain number")

    if PasswordPolicy.REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain special character")

    if PasswordPolicy.BREACHED_PASSWORD_CHECK:
        if is_password_breached(password):
            errors.append("Password found in known breach database")

    return len(errors) == 0, errors

# GOOD: MFA implementation
from pyotp import TOTP
import secrets

class MFAService:
    def __init__(self):
        self.totp_issuer = "MyCompany"

    def setup_mfa(self, user_id: str) -> dict:
        """Generate MFA secret for user"""
        secret = secrets.token_hex(20)
        totp = TOTP(secret)

        # Store encrypted secret
        db.execute(
            "UPDATE users SET mfa_secret = %s, mfa_enabled = false WHERE id = %s",
            encrypt(secret), user_id
        )

        return {
            "secret": secret,
            "provisioning_uri": totp.provisioning_uri(
                name=user_id,
                issuer_name=self.totp_issuer
            ),
            "backup_codes": self._generate_backup_codes(user_id)
        }

    def verify_mfa(self, user_id: str, code: str) -> bool:
        """Verify MFA code"""
        user = db.query(User).get(user_id)

        # Check TOTP code
        secret = decrypt(user.mfa_secret)
        totp = TOTP(secret)

        if totp.verify(code, valid_window=1):  # Allow 30-second window
            return True

        # Check backup codes
        if self._check_backup_code(user_id, code):
            return True

        # Log failed attempt
        audit_log.warning("MFA verification failed", user_id=user_id)
        return False

    def _generate_backup_codes(self, user_id: str) -> list[str]:
        """Generate one-time backup codes"""
        codes = [secrets.token_hex(4) for _ in range(10)]
        hashed_codes = [hash_code(c) for c in codes]
        db.execute(
            "UPDATE users SET backup_codes = %s WHERE id = %s",
            json.dumps(hashed_codes), user_id
        )
        return codes  # Return unhashed codes to show user once
                ''',
            },
            "cc6_2_access_provisioning": {
                "description": "New access requests go through authorization process",
                "good": '''
# GOOD: Access request workflow
from enum import Enum
from datetime import datetime

class AccessRequestStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    REVOKED = "revoked"

class AccessRequest(BaseModel):
    id: str
    user_id: str
    requested_roles: list[str]
    justification: str
    requested_at: datetime
    status: AccessRequestStatus
    approved_by: str | None
    approved_at: datetime | None

class AccessRequestService:
    def create_request(self, user_id: str, roles: list[str], justification: str) -> AccessRequest:
        """Create access request requiring manager approval"""
        request = AccessRequest(
            id=generate_uuid(),
            user_id=user_id,
            requested_roles=roles,
            justification=justification,
            requested_at=datetime.utcnow(),
            status=AccessRequestStatus.PENDING,
        )
        db.save(request)

        # Notify approvers
        manager = self._get_manager(user_id)
        notification_service.send(
            to=manager.email,
            template="access_request",
            data={"request": request}
        )

        # SOC 2 audit log
        audit_log.info(
            "Access request created",
            request_id=request.id,
            user_id=user_id,
            roles=roles
        )

        return request

    def approve_request(self, request_id: str, approver_id: str) -> AccessRequest:
        """Approve access request (requires authorization)"""
        request = db.query(AccessRequest).get(request_id)
        approver = db.query(User).get(approver_id)

        # Verify approver is authorized
        if not self._can_approve(approver, request):
            raise PermissionError("Not authorized to approve this request")

        # Check for segregation of duties
        if request.user_id == approver_id:
            raise PermissionError("Cannot approve own access request")

        # Update request
        request.status = AccessRequestStatus.APPROVED
        request.approved_by = approver_id
        request.approved_at = datetime.utcnow()
        db.save(request)

        # Provision access
        self._provision_access(request)

        # SOC 2 audit log
        audit_log.info(
            "Access request approved",
            request_id=request_id,
            approved_by=approver_id
        )

        return request
                ''',
            },
            "cc6_3_access_removal": {
                "description": "Access is removed when no longer needed",
                "good": '''
# GOOD: Automated access removal on termination
class TerminationService:
    def process_termination(self, employee_id: str, termination_date: date):
        """Remove all access upon termination"""
        user = db.query(User).filter_by(employee_id=employee_id).first()

        # Disable account immediately
        user.is_active = False
        user.disabled_at = datetime.utcnow()
        user.disabled_reason = "termination"
        db.save(user)

        # Revoke all sessions
        session_service.revoke_all_sessions(user.id)

        # Disable SSO
        sso_provider.disable_user(user.email)

        # Remove from all groups/roles
        access_removed = []
        for role in user.roles:
            self._revoke_role(user.id, role.id)
            access_removed.append(role.name)

        # Revoke API keys
        api_service.revoke_all_keys(user.id)

        # Transfer ownership of resources
        ownership_service.transfer_resources(user.id, user.manager_id)

        # SOC 2 audit log - critical for evidence
        audit_log.info(
            "User terminated and access removed",
            user_id=user.id,
            employee_id=employee_id,
            termination_date=termination_date.isoformat(),
            access_removed=access_removed,
            sessions_revoked=True,
            sso_disabled=True
        )

        # Notify IT security
        notification_service.send(
            to="security@company.com",
            template="termination_completed",
            data={
                "employee_id": employee_id,
                "access_removed": access_removed
            }
        )

# GOOD: Quarterly access review
class AccessReviewService:
    def initiate_quarterly_review(self):
        """Start quarterly user access review"""
        review = AccessReview(
            id=generate_uuid(),
            period=f"Q{get_quarter()}-{datetime.now().year}",
            started_at=datetime.utcnow(),
            status="in_progress"
        )
        db.save(review)

        # Get all users with elevated access
        users_to_review = db.query(User).filter(
            User.roles.any(Role.is_privileged == True)
        ).all()

        for user in users_to_review:
            review_item = AccessReviewItem(
                review_id=review.id,
                user_id=user.id,
                current_roles=[r.name for r in user.roles],
                reviewer_id=user.manager_id,
                status="pending"
            )
            db.save(review_item)

            # Notify reviewer
            notification_service.send(
                to=user.manager.email,
                template="access_review_required",
                data={"user": user, "deadline": review.deadline}
            )

        return review
                ''',
            },
        }

    # =========================================================================
    # SYSTEM OPERATIONS (CC7)
    # =========================================================================

    @staticmethod
    def system_operations() -> Dict[str, Any]:
        """CC7 - System Operations Controls"""
        return {
            "cc7_1_vulnerability_management": {
                "description": "Entity detects and monitors security vulnerabilities",
                "good": '''
# GOOD: Automated vulnerability scanning pipeline
import subprocess
from dataclasses import dataclass

@dataclass
class VulnerabilityReport:
    scanner: str
    scan_date: datetime
    target: str
    critical: int
    high: int
    medium: int
    low: int
    findings: list[dict]

class VulnerabilityScanner:
    def scan_container_image(self, image: str) -> VulnerabilityReport:
        """Scan container image with Trivy"""
        result = subprocess.run(
            ["trivy", "image", "--format", "json", image],
            capture_output=True, text=True
        )
        findings = json.loads(result.stdout)

        report = VulnerabilityReport(
            scanner="trivy",
            scan_date=datetime.utcnow(),
            target=image,
            critical=sum(1 for f in findings if f["severity"] == "CRITICAL"),
            high=sum(1 for f in findings if f["severity"] == "HIGH"),
            medium=sum(1 for f in findings if f["severity"] == "MEDIUM"),
            low=sum(1 for f in findings if f["severity"] == "LOW"),
            findings=findings
        )

        # Store for audit trail
        db.save(report)

        # Alert on critical findings
        if report.critical > 0:
            alert_service.send(
                severity="critical",
                title=f"Critical vulnerabilities in {image}",
                details=report
            )

        return report

    def scan_infrastructure(self) -> VulnerabilityReport:
        """Scan infrastructure with Nessus/OpenVAS"""
        # Weekly infrastructure scan
        scanner = nessus.Scanner(api_key=config.NESSUS_API_KEY)
        scan_id = scanner.launch_scan(
            targets=config.SCAN_TARGETS,
            policy="SOC2-Compliance"
        )

        # Wait for completion and get results
        results = scanner.get_results(scan_id)

        report = VulnerabilityReport(
            scanner="nessus",
            scan_date=datetime.utcnow(),
            target="infrastructure",
            critical=results["critical_count"],
            high=results["high_count"],
            medium=results["medium_count"],
            low=results["low_count"],
            findings=results["findings"]
        )

        db.save(report)
        return report
                ''',
            },
            "cc7_2_security_monitoring": {
                "description": "Entity monitors system components for anomalies",
                "good": '''
# GOOD: Security monitoring and alerting
from datadog import statsd
import sentry_sdk

class SecurityMonitor:
    def __init__(self):
        self.alert_thresholds = {
            "failed_logins_per_minute": 10,
            "api_errors_per_minute": 100,
            "unusual_data_access": 1000,  # records accessed
        }

    def monitor_failed_logins(self, user_id: str, ip_address: str):
        """Track and alert on failed login attempts"""
        key = f"failed_logins:{ip_address}"
        count = redis.incr(key)
        redis.expire(key, 60)  # 1-minute window

        # Log for audit
        audit_log.warning(
            "Failed login attempt",
            user_id=user_id,
            ip_address=ip_address,
            attempt_count=count
        )

        # Alert on threshold breach
        if count >= self.alert_thresholds["failed_logins_per_minute"]:
            alert_service.send(
                severity="high",
                title="Potential brute force attack",
                details={
                    "ip_address": ip_address,
                    "attempts": count,
                    "threshold": self.alert_thresholds["failed_logins_per_minute"]
                }
            )
            # Auto-block IP
            firewall.block_ip(ip_address, duration_minutes=30)

    def monitor_data_access(self, user_id: str, resource: str, records_accessed: int):
        """Monitor for unusual data access patterns"""
        # Track access volume
        key = f"data_access:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
        total = redis.incrby(key, records_accessed)
        redis.expire(key, 86400)  # 24 hours

        # Log for audit trail
        audit_log.info(
            "Data access",
            user_id=user_id,
            resource=resource,
            records_accessed=records_accessed,
            daily_total=total
        )

        # Alert on unusual volume
        if total > self.alert_thresholds["unusual_data_access"]:
            user = db.query(User).get(user_id)
            baseline = self._get_user_baseline(user_id)

            if total > baseline * 10:  # 10x normal
                alert_service.send(
                    severity="high",
                    title="Unusual data access detected",
                    details={
                        "user_id": user_id,
                        "user_email": user.email,
                        "records_accessed": total,
                        "baseline": baseline,
                        "resource": resource
                    }
                )

    def monitor_privileged_actions(self, user_id: str, action: str, target: str):
        """Monitor and log all privileged operations"""
        # All privileged actions must be logged
        audit_log.info(
            "Privileged action performed",
            user_id=user_id,
            action=action,
            target=target,
            timestamp=datetime.utcnow().isoformat()
        )

        # Real-time dashboard metric
        statsd.increment("privileged_actions", tags=[
            f"action:{action}",
            f"user:{user_id}"
        ])
                ''',
            },
            "cc7_3_incident_response": {
                "description": "Entity responds to identified security incidents",
                "good": '''
# GOOD: Incident response workflow
from enum import Enum

class IncidentSeverity(Enum):
    P1_CRITICAL = "P1"  # 15 min response
    P2_HIGH = "P2"      # 1 hour response
    P3_MEDIUM = "P3"    # 4 hours response
    P4_LOW = "P4"       # 24 hours response

class SecurityIncident(BaseModel):
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: str  # detected, triaging, contained, eradicated, recovered, closed
    detected_at: datetime
    detected_by: str
    affected_systems: list[str]
    affected_users: list[str]
    timeline: list[dict]
    root_cause: str | None
    lessons_learned: str | None

class IncidentResponseService:
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        detected_by: str,
        affected_systems: list[str]
    ) -> SecurityIncident:
        """Create and initiate incident response"""
        incident = SecurityIncident(
            id=f"INC-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            title=title,
            description=description,
            severity=severity,
            status="detected",
            detected_at=datetime.utcnow(),
            detected_by=detected_by,
            affected_systems=affected_systems,
            affected_users=[],
            timeline=[{
                "timestamp": datetime.utcnow().isoformat(),
                "action": "Incident detected",
                "actor": detected_by
            }]
        )
        db.save(incident)

        # Immediate notifications based on severity
        self._notify_incident_team(incident)

        # P1/P2: Page on-call
        if severity in [IncidentSeverity.P1_CRITICAL, IncidentSeverity.P2_HIGH]:
            pagerduty.create_incident(
                title=f"[{severity.value}] {title}",
                service="security",
                urgency="high" if severity == IncidentSeverity.P1_CRITICAL else "low"
            )

        # Create war room for P1
        if severity == IncidentSeverity.P1_CRITICAL:
            slack.create_channel(f"inc-{incident.id.lower()}")
            zoom.create_meeting(f"Incident {incident.id} War Room")

        return incident

    def update_incident_status(
        self,
        incident_id: str,
        new_status: str,
        notes: str,
        actor: str
    ):
        """Update incident status with timeline entry"""
        incident = db.query(SecurityIncident).get(incident_id)

        incident.status = new_status
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": f"Status changed to {new_status}",
            "notes": notes,
            "actor": actor
        })
        db.save(incident)

        # Audit log for SOC 2
        audit_log.info(
            "Incident status updated",
            incident_id=incident_id,
            new_status=new_status,
            actor=actor
        )

    def close_incident(
        self,
        incident_id: str,
        root_cause: str,
        lessons_learned: str,
        actor: str
    ):
        """Close incident with post-mortem"""
        incident = db.query(SecurityIncident).get(incident_id)

        incident.status = "closed"
        incident.root_cause = root_cause
        incident.lessons_learned = lessons_learned
        incident.timeline.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "Incident closed",
            "actor": actor
        })
        db.save(incident)

        # Generate post-mortem document
        postmortem = self._generate_postmortem(incident)

        # Schedule follow-up for action items
        self._schedule_followups(incident, lessons_learned)

        return postmortem
                ''',
            },
        }

    # =========================================================================
    # CHANGE MANAGEMENT (CC8)
    # =========================================================================

    @staticmethod
    def change_management() -> Dict[str, Any]:
        """CC8 - Change Management Controls"""
        return {
            "cc8_1_change_process": {
                "description": "Changes to infrastructure and software follow managed process",
                "bad": '''
# BAD: Direct production deployment without review
def deploy_to_production(artifact: str):
    ssh.connect("prod-server")
    ssh.execute(f"docker pull {artifact}")
    ssh.execute(f"docker run -d {artifact}")
    # No review, no testing, no rollback plan!
                ''',
                "good": '''
# GOOD: Change management workflow
from enum import Enum
from datetime import datetime, timedelta

class ChangeType(Enum):
    STANDARD = "standard"    # Pre-approved, low risk
    NORMAL = "normal"        # Requires CAB approval
    EMERGENCY = "emergency"  # Post-hoc approval

class ChangeStatus(Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

class ChangeRequest(BaseModel):
    id: str
    title: str
    description: str
    change_type: ChangeType
    status: ChangeStatus
    requester_id: str
    created_at: datetime
    scheduled_at: datetime | None
    completed_at: datetime | None

    # Impact assessment
    affected_systems: list[str]
    risk_level: str
    impact_assessment: str

    # Approvals
    code_review_approved: bool
    security_review_approved: bool
    cab_approved: bool  # Change Advisory Board
    approvers: list[dict]

    # Execution
    implementation_plan: str
    rollback_plan: str
    test_plan: str

class ChangeManagementService:
    def create_change_request(
        self,
        title: str,
        description: str,
        change_type: ChangeType,
        requester_id: str,
        affected_systems: list[str],
        implementation_plan: str,
        rollback_plan: str,
        test_plan: str
    ) -> ChangeRequest:
        """Create change request requiring approval"""
        # Risk assessment
        risk_level = self._assess_risk(affected_systems, change_type)

        cr = ChangeRequest(
            id=f"CR-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            title=title,
            description=description,
            change_type=change_type,
            status=ChangeStatus.DRAFT,
            requester_id=requester_id,
            created_at=datetime.utcnow(),
            affected_systems=affected_systems,
            risk_level=risk_level,
            impact_assessment=self._generate_impact_assessment(affected_systems),
            implementation_plan=implementation_plan,
            rollback_plan=rollback_plan,
            test_plan=test_plan,
            code_review_approved=False,
            security_review_approved=False,
            cab_approved=change_type == ChangeType.STANDARD,  # Pre-approved
            approvers=[]
        )
        db.save(cr)

        # Audit log
        audit_log.info(
            "Change request created",
            cr_id=cr.id,
            requester=requester_id,
            change_type=change_type.value
        )

        return cr

    def approve_change(
        self,
        cr_id: str,
        approver_id: str,
        approval_type: str  # code_review, security_review, cab
    ):
        """Record approval for change request"""
        cr = db.query(ChangeRequest).get(cr_id)
        approver = db.query(User).get(approver_id)

        # Verify approver has authority
        if not self._can_approve(approver, approval_type):
            raise PermissionError(f"Not authorized to approve {approval_type}")

        # Segregation of duties - requester cannot approve
        if cr.requester_id == approver_id:
            raise PermissionError("Cannot approve own change request")

        # Record approval
        cr.approvers.append({
            "approver_id": approver_id,
            "approval_type": approval_type,
            "approved_at": datetime.utcnow().isoformat()
        })

        if approval_type == "code_review":
            cr.code_review_approved = True
        elif approval_type == "security_review":
            cr.security_review_approved = True
        elif approval_type == "cab":
            cr.cab_approved = True

        # Check if all approvals received
        if self._all_approvals_received(cr):
            cr.status = ChangeStatus.APPROVED

        db.save(cr)

        # Audit log
        audit_log.info(
            "Change request approved",
            cr_id=cr_id,
            approver=approver_id,
            approval_type=approval_type
        )

    def execute_change(self, cr_id: str, executor_id: str):
        """Execute approved change with audit trail"""
        cr = db.query(ChangeRequest).get(cr_id)

        # Verify change is approved
        if cr.status != ChangeStatus.APPROVED:
            raise ValueError("Change not approved")

        # Verify executor has authority
        if not self._can_execute(executor_id, cr):
            raise PermissionError("Not authorized to execute change")

        cr.status = ChangeStatus.IN_PROGRESS
        db.save(cr)

        audit_log.info(
            "Change execution started",
            cr_id=cr_id,
            executor=executor_id
        )

        try:
            # Execute implementation plan
            result = deployment_service.deploy(cr.implementation_plan)

            # Run post-deployment tests
            test_result = testing_service.run_tests(cr.test_plan)

            if test_result.passed:
                cr.status = ChangeStatus.COMPLETED
                cr.completed_at = datetime.utcnow()
            else:
                # Automatic rollback on test failure
                self.rollback_change(cr_id, "Post-deployment tests failed")
                cr.status = ChangeStatus.ROLLED_BACK

        except Exception as e:
            # Rollback on failure
            self.rollback_change(cr_id, str(e))
            cr.status = ChangeStatus.FAILED

        db.save(cr)

        audit_log.info(
            "Change execution completed",
            cr_id=cr_id,
            status=cr.status.value
        )
                ''',
            },
        }

    # =========================================================================
    # RISK MITIGATION (CC9)
    # =========================================================================

    @staticmethod
    def risk_management() -> Dict[str, Any]:
        """CC9 - Risk Mitigation Controls"""
        return {
            "cc9_1_risk_assessment": {
                "description": "Entity identifies and assesses risks",
                "good": '''
# GOOD: Risk assessment and tracking
from enum import Enum

class RiskLikelihood(Enum):
    RARE = 1
    UNLIKELY = 2
    POSSIBLE = 3
    LIKELY = 4
    ALMOST_CERTAIN = 5

class RiskImpact(Enum):
    NEGLIGIBLE = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    SEVERE = 5

class Risk(BaseModel):
    id: str
    title: str
    description: str
    category: str  # Security, Operational, Compliance, Financial
    likelihood: RiskLikelihood
    impact: RiskImpact
    risk_score: int  # likelihood * impact
    owner_id: str
    status: str  # identified, assessed, mitigated, accepted, closed

    # Mitigation
    mitigation_plan: str | None
    mitigating_controls: list[str]
    residual_likelihood: RiskLikelihood | None
    residual_impact: RiskImpact | None
    residual_score: int | None

    # Tracking
    identified_at: datetime
    last_reviewed: datetime
    review_frequency: str  # quarterly, annually

class RiskManagementService:
    def identify_risk(
        self,
        title: str,
        description: str,
        category: str,
        likelihood: RiskLikelihood,
        impact: RiskImpact,
        owner_id: str
    ) -> Risk:
        """Identify and document new risk"""
        risk = Risk(
            id=f"RISK-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            title=title,
            description=description,
            category=category,
            likelihood=likelihood,
            impact=impact,
            risk_score=likelihood.value * impact.value,
            owner_id=owner_id,
            status="identified",
            mitigating_controls=[],
            identified_at=datetime.utcnow(),
            last_reviewed=datetime.utcnow(),
            review_frequency="quarterly"
        )
        db.save(risk)

        # Notify risk owner
        notification_service.send(
            to=owner_id,
            template="new_risk_assigned",
            data={"risk": risk}
        )

        # High/Critical risks escalate to leadership
        if risk.risk_score >= 16:  # High risk
            notification_service.send(
                to="security-leadership@company.com",
                template="high_risk_identified",
                data={"risk": risk}
            )

        # Audit log
        audit_log.info(
            "Risk identified",
            risk_id=risk.id,
            risk_score=risk.risk_score,
            category=category
        )

        return risk

    def add_mitigation(
        self,
        risk_id: str,
        mitigation_plan: str,
        controls: list[str],
        residual_likelihood: RiskLikelihood,
        residual_impact: RiskImpact
    ):
        """Add mitigation plan with residual risk assessment"""
        risk = db.query(Risk).get(risk_id)

        risk.mitigation_plan = mitigation_plan
        risk.mitigating_controls = controls
        risk.residual_likelihood = residual_likelihood
        risk.residual_impact = residual_impact
        risk.residual_score = residual_likelihood.value * residual_impact.value
        risk.status = "mitigated"
        risk.last_reviewed = datetime.utcnow()

        db.save(risk)

        audit_log.info(
            "Risk mitigation added",
            risk_id=risk_id,
            original_score=risk.risk_score,
            residual_score=risk.residual_score
        )

    def conduct_risk_review(self):
        """Quarterly risk register review"""
        risks = db.query(Risk).filter(
            Risk.status.in_(["identified", "mitigated"]),
            Risk.last_reviewed < datetime.utcnow() - timedelta(days=90)
        ).all()

        review_report = []
        for risk in risks:
            # Request review from owner
            review_item = {
                "risk_id": risk.id,
                "title": risk.title,
                "current_score": risk.risk_score,
                "residual_score": risk.residual_score,
                "owner": risk.owner_id,
                "days_since_review": (datetime.utcnow() - risk.last_reviewed).days
            }
            review_report.append(review_item)

            notification_service.send(
                to=risk.owner_id,
                template="risk_review_required",
                data={"risk": risk}
            )

        # Report to leadership
        notification_service.send(
            to="risk-committee@company.com",
            template="quarterly_risk_review",
            data={"risks_requiring_review": review_report}
        )

        return review_report
                ''',
            },
            "cc9_2_vendor_management": {
                "description": "Entity assesses and manages vendor risks",
                "good": '''
# GOOD: Vendor risk management
class VendorRiskTier(Enum):
    CRITICAL = "critical"  # Business critical, high data access
    HIGH = "high"          # Significant data access or impact
    MEDIUM = "medium"      # Limited data access
    LOW = "low"            # No data access, limited impact

class Vendor(BaseModel):
    id: str
    name: str
    description: str
    risk_tier: VendorRiskTier
    data_shared: list[str]  # Types of data shared
    contract_start: date
    contract_end: date
    soc2_report: str | None  # Link to SOC 2 report
    last_assessment: datetime
    assessment_frequency: str
    owner_id: str

class VendorManagementService:
    def onboard_vendor(
        self,
        name: str,
        description: str,
        data_shared: list[str],
        contract_start: date,
        contract_end: date,
        owner_id: str
    ) -> Vendor:
        """Onboard new vendor with risk assessment"""
        # Determine risk tier based on data shared
        risk_tier = self._assess_vendor_risk(data_shared)

        vendor = Vendor(
            id=f"VND-{generate_uuid()[:8]}",
            name=name,
            description=description,
            risk_tier=risk_tier,
            data_shared=data_shared,
            contract_start=contract_start,
            contract_end=contract_end,
            last_assessment=datetime.utcnow(),
            assessment_frequency=self._get_assessment_frequency(risk_tier),
            owner_id=owner_id
        )

        # Critical/High tier requires additional review
        if risk_tier in [VendorRiskTier.CRITICAL, VendorRiskTier.HIGH]:
            # Require SOC 2 report
            vendor.soc2_report = None  # Must be provided

            # Security review required
            security_review_service.create_review(
                subject_type="vendor",
                subject_id=vendor.id,
                priority="high"
            )

            # Legal review for contract
            legal_service.create_contract_review(vendor.id)

        db.save(vendor)

        audit_log.info(
            "Vendor onboarded",
            vendor_id=vendor.id,
            vendor_name=name,
            risk_tier=risk_tier.value
        )

        return vendor

    def _assess_vendor_risk(self, data_shared: list[str]) -> VendorRiskTier:
        """Assess vendor risk tier based on data access"""
        critical_data = ["pii", "phi", "financial", "credentials"]
        high_data = ["customer_data", "employee_data"]

        if any(d in critical_data for d in data_shared):
            return VendorRiskTier.CRITICAL
        if any(d in high_data for d in data_shared):
            return VendorRiskTier.HIGH
        if data_shared:
            return VendorRiskTier.MEDIUM
        return VendorRiskTier.LOW

    def _get_assessment_frequency(self, tier: VendorRiskTier) -> str:
        """Determine assessment frequency based on risk tier"""
        return {
            VendorRiskTier.CRITICAL: "quarterly",
            VendorRiskTier.HIGH: "semi-annually",
            VendorRiskTier.MEDIUM: "annually",
            VendorRiskTier.LOW: "bi-annually"
        }[tier]
                ''',
            },
        }

    # =========================================================================
    # AVAILABILITY CONTROLS (A1)
    # =========================================================================

    @staticmethod
    def availability_controls() -> Dict[str, Any]:
        """A1 - Availability Trust Service Criteria"""
        return {
            "a1_1_capacity_planning": {
                "description": "Entity maintains capacity to meet availability commitments",
                "good": '''
# GOOD: Capacity monitoring and planning
class CapacityMonitor:
    def __init__(self):
        self.thresholds = {
            "cpu_warning": 70,
            "cpu_critical": 85,
            "memory_warning": 75,
            "memory_critical": 90,
            "disk_warning": 70,
            "disk_critical": 85
        }

    def collect_metrics(self) -> dict:
        """Collect capacity metrics from all systems"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "systems": []
        }

        for system in infrastructure.get_all_systems():
            system_metrics = {
                "system_id": system.id,
                "system_name": system.name,
                "cpu_percent": system.get_cpu_usage(),
                "memory_percent": system.get_memory_usage(),
                "disk_percent": system.get_disk_usage(),
                "network_bandwidth_mbps": system.get_network_usage(),
                "request_rate": system.get_request_rate()
            }
            metrics["systems"].append(system_metrics)

            # Check thresholds and alert
            self._check_thresholds(system, system_metrics)

        # Store for trending
        db.save(CapacitySnapshot(**metrics))

        return metrics

    def generate_capacity_report(self, period_days: int = 30) -> dict:
        """Generate capacity planning report"""
        snapshots = db.query(CapacitySnapshot).filter(
            CapacitySnapshot.timestamp > datetime.utcnow() - timedelta(days=period_days)
        ).all()

        report = {
            "period": f"Last {period_days} days",
            "generated_at": datetime.utcnow().isoformat(),
            "systems": []
        }

        for system_id in set(s["system_id"] for snapshot in snapshots for s in snapshot.systems):
            system_data = [
                s for snapshot in snapshots
                for s in snapshot.systems
                if s["system_id"] == system_id
            ]

            system_report = {
                "system_id": system_id,
                "cpu_avg": statistics.mean(s["cpu_percent"] for s in system_data),
                "cpu_max": max(s["cpu_percent"] for s in system_data),
                "cpu_trend": self._calculate_trend([s["cpu_percent"] for s in system_data]),
                "memory_avg": statistics.mean(s["memory_percent"] for s in system_data),
                "memory_max": max(s["memory_percent"] for s in system_data),
                "days_until_capacity": self._predict_capacity_exhaustion(system_data)
            }
            report["systems"].append(system_report)

            # Alert if capacity exhaustion predicted within 30 days
            if system_report["days_until_capacity"] < 30:
                alert_service.send(
                    severity="warning",
                    title=f"Capacity exhaustion predicted for {system_id}",
                    details=system_report
                )

        return report
                ''',
            },
            "a1_2_backup_recovery": {
                "description": "Entity maintains backup and recovery procedures",
                "good": '''
# GOOD: Backup and recovery procedures
class BackupService:
    def __init__(self):
        self.retention_policy = {
            "daily": 7,      # Keep 7 daily backups
            "weekly": 4,     # Keep 4 weekly backups
            "monthly": 12,   # Keep 12 monthly backups
            "yearly": 7      # Keep 7 yearly backups
        }

    async def perform_backup(self, database: str) -> dict:
        """Perform automated backup with verification"""
        backup_id = f"backup-{database}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        backup_record = {
            "id": backup_id,
            "database": database,
            "started_at": datetime.utcnow(),
            "status": "in_progress"
        }
        db.save(BackupRecord(**backup_record))

        try:
            # Create backup
            backup_path = await self._create_backup(database, backup_id)

            # Encrypt backup
            encrypted_path = await self._encrypt_backup(backup_path)

            # Upload to offsite storage (different region)
            storage_location = await storage.upload(
                encrypted_path,
                bucket=config.BACKUP_BUCKET,
                region=config.BACKUP_REGION  # Different from primary
            )

            # Verify backup integrity
            checksum = self._calculate_checksum(encrypted_path)
            verified = await self._verify_backup(backup_id, checksum)

            backup_record.update({
                "completed_at": datetime.utcnow(),
                "status": "completed",
                "storage_location": storage_location,
                "size_bytes": os.path.getsize(encrypted_path),
                "checksum": checksum,
                "verified": verified
            })

            # Audit log
            audit_log.info(
                "Backup completed",
                backup_id=backup_id,
                database=database,
                verified=verified
            )

        except Exception as e:
            backup_record.update({
                "completed_at": datetime.utcnow(),
                "status": "failed",
                "error": str(e)
            })

            # Alert on backup failure
            alert_service.send(
                severity="critical",
                title=f"Backup failed for {database}",
                details={"backup_id": backup_id, "error": str(e)}
            )

        db.save(BackupRecord(**backup_record))
        return backup_record

    async def test_recovery(self, backup_id: str) -> dict:
        """Quarterly recovery test"""
        backup = db.query(BackupRecord).get(backup_id)

        test_record = {
            "id": f"recovery-test-{generate_uuid()[:8]}",
            "backup_id": backup_id,
            "started_at": datetime.utcnow(),
            "status": "in_progress"
        }

        try:
            # Restore to isolated environment
            restore_env = await self._create_isolated_environment()

            # Perform restore
            restore_time_start = datetime.utcnow()
            await self._restore_backup(backup_id, restore_env)
            restore_duration = (datetime.utcnow() - restore_time_start).total_seconds()

            # Verify data integrity
            integrity_check = await self._verify_data_integrity(restore_env)

            # Test application connectivity
            app_test = await self._test_application(restore_env)

            test_record.update({
                "completed_at": datetime.utcnow(),
                "status": "passed" if integrity_check and app_test else "failed",
                "restore_duration_seconds": restore_duration,
                "integrity_check": integrity_check,
                "application_test": app_test,
                "rto_met": restore_duration < config.RTO_SECONDS  # Recovery Time Objective
            })

            # Cleanup test environment
            await self._cleanup_environment(restore_env)

        except Exception as e:
            test_record.update({
                "completed_at": datetime.utcnow(),
                "status": "failed",
                "error": str(e)
            })

        db.save(RecoveryTest(**test_record))

        # Audit log
        audit_log.info(
            "Recovery test completed",
            test_id=test_record["id"],
            status=test_record["status"]
        )

        return test_record
                ''',
            },
        }

    @staticmethod
    def evidence_collection() -> Dict[str, Any]:
        """Evidence collection for SOC 2"""
        return {
            "access_controls": [
                "User access reviews (quarterly)",
                "Terminated user lists with deprovisioning dates",
                "MFA enforcement configuration",
                "Privileged access logs",
                "Role-based access matrix",
            ],
            "change_management": [
                "Change request tickets",
                "Code review approvals",
                "Deployment logs",
                "Rollback procedures",
                "Testing evidence before deployment",
            ],
            "monitoring": [
                "Security monitoring dashboards",
                "Alert configuration",
                "Incident tickets and resolution",
                "Vulnerability scan reports",
                "Penetration test results",
            ],
            "policies": [
                "Information Security Policy",
                "Acceptable Use Policy",
                "Incident Response Plan",
                "Business Continuity Plan",
                "Vendor Management Policy",
            ],
        }

    # =========================================================================
    # PROCESSING INTEGRITY (PI1)
    # =========================================================================

    @staticmethod
    def processing_integrity_controls() -> Dict[str, Any]:
        """PI1 - Processing Integrity Trust Service Criteria"""
        return {
            "pi1_1_input_validation": {
                "description": "System processing is complete, valid, accurate, and timely",
                "bad": '''
# BAD: No input validation
def process_transaction(data: dict):
    # Direct processing without validation!
    transaction = Transaction(
        amount=data["amount"],
        account_id=data["account_id"],
        type=data["type"]
    )
    db.save(transaction)
    return transaction
                ''',
                "good": '''
# GOOD: Comprehensive input validation
from pydantic import BaseModel, validator, Field
from decimal import Decimal

class TransactionInput(BaseModel):
    amount: Decimal = Field(..., gt=0, le=1000000)
    account_id: str = Field(..., min_length=10, max_length=20)
    type: str = Field(..., regex="^(credit|debit)$")
    reference: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime

    @validator("account_id")
    def validate_account_exists(cls, v):
        if not account_service.exists(v):
            raise ValueError("Account does not exist")
        return v

    @validator("timestamp")
    def validate_timestamp(cls, v):
        # Timestamp must be within last 5 minutes
        if abs((datetime.utcnow() - v).total_seconds()) > 300:
            raise ValueError("Timestamp out of acceptable range")
        return v

def process_transaction(data: dict) -> Transaction:
    """Process transaction with validation and audit trail"""
    # Validate input
    validated = TransactionInput(**data)

    # Check for duplicates (idempotency)
    existing = db.query(Transaction).filter_by(
        reference=validated.reference
    ).first()
    if existing:
        audit_log.warning("Duplicate transaction rejected", reference=validated.reference)
        return existing

    # Process transaction
    transaction = Transaction(
        id=generate_uuid(),
        amount=validated.amount,
        account_id=validated.account_id,
        type=validated.type,
        reference=validated.reference,
        processed_at=datetime.utcnow(),
        status="completed"
    )
    db.save(transaction)

    # Audit log
    audit_log.info(
        "Transaction processed",
        transaction_id=transaction.id,
        amount=str(validated.amount),
        type=validated.type
    )

    return transaction
                ''',
            },
            "pi1_4_output_verification": {
                "description": "Output is reviewed and verified",
                "good": '''
# GOOD: Output verification with reconciliation
class ReconciliationService:
    def reconcile_daily_transactions(self, date: date) -> dict:
        """Daily transaction reconciliation"""
        # Get all transactions for the day
        transactions = db.query(Transaction).filter(
            Transaction.processed_at >= date,
            Transaction.processed_at < date + timedelta(days=1)
        ).all()

        # Calculate totals
        total_credits = sum(t.amount for t in transactions if t.type == "credit")
        total_debits = sum(t.amount for t in transactions if t.type == "debit")

        # Get external source of truth
        bank_statement = bank_api.get_daily_summary(date)

        # Reconcile
        credit_diff = abs(total_credits - bank_statement.credits)
        debit_diff = abs(total_debits - bank_statement.debits)

        reconciliation = {
            "date": date.isoformat(),
            "our_credits": str(total_credits),
            "our_debits": str(total_debits),
            "bank_credits": str(bank_statement.credits),
            "bank_debits": str(bank_statement.debits),
            "credit_difference": str(credit_diff),
            "debit_difference": str(debit_diff),
            "status": "matched" if credit_diff == 0 and debit_diff == 0 else "discrepancy",
            "reconciled_at": datetime.utcnow().isoformat()
        }

        db.save(ReconciliationRecord(**reconciliation))

        # Alert on discrepancies
        if reconciliation["status"] == "discrepancy":
            alert_service.send(
                severity="high",
                title=f"Reconciliation discrepancy for {date}",
                details=reconciliation
            )

        # Audit log
        audit_log.info(
            "Daily reconciliation completed",
            date=date.isoformat(),
            status=reconciliation["status"]
        )

        return reconciliation
                ''',
            },
        }

    # =========================================================================
    # CONFIDENTIALITY (C1)
    # =========================================================================

    @staticmethod
    def confidentiality_controls() -> Dict[str, Any]:
        """C1 - Confidentiality Trust Service Criteria"""
        return {
            "c1_1_data_classification": {
                "description": "Confidential information is identified and classified",
                "good": '''
# GOOD: Data classification system
from enum import Enum

class DataClassification(Enum):
    PUBLIC = "public"              # Can be shared externally
    INTERNAL = "internal"          # Internal use only
    CONFIDENTIAL = "confidential"  # Limited access, business sensitive
    RESTRICTED = "restricted"      # Highly sensitive, strict access

class ClassifiedData(BaseModel):
    id: str
    classification: DataClassification
    data_type: str
    owner_id: str
    access_groups: list[str]
    encryption_required: bool
    retention_period_days: int
    disposal_method: str

class DataClassificationService:
    classification_rules = {
        "pii": DataClassification.CONFIDENTIAL,
        "phi": DataClassification.RESTRICTED,
        "financial_data": DataClassification.RESTRICTED,
        "employee_data": DataClassification.CONFIDENTIAL,
        "customer_data": DataClassification.CONFIDENTIAL,
        "public_content": DataClassification.PUBLIC,
        "internal_docs": DataClassification.INTERNAL,
    }

    def classify_data(self, data_type: str, content: Any) -> ClassifiedData:
        """Classify data based on content type"""
        classification = self.classification_rules.get(
            data_type, DataClassification.INTERNAL
        )

        classified = ClassifiedData(
            id=generate_uuid(),
            classification=classification,
            data_type=data_type,
            owner_id=current_user.id,
            access_groups=self._get_default_access_groups(classification),
            encryption_required=classification in [
                DataClassification.CONFIDENTIAL,
                DataClassification.RESTRICTED
            ],
            retention_period_days=self._get_retention_period(classification),
            disposal_method="secure_delete" if classification != DataClassification.PUBLIC else "standard"
        )

        # Audit classification
        audit_log.info(
            "Data classified",
            data_id=classified.id,
            classification=classification.value,
            data_type=data_type
        )

        return classified

    def check_access(self, user_id: str, data_id: str) -> bool:
        """Check if user has access to classified data"""
        data = db.query(ClassifiedData).get(data_id)
        user = db.query(User).get(user_id)

        # Owner always has access
        if data.owner_id == user_id:
            return True

        # Check group membership
        user_groups = set(user.groups)
        required_groups = set(data.access_groups)

        has_access = bool(user_groups & required_groups)

        # Audit access check
        audit_log.info(
            "Data access check",
            user_id=user_id,
            data_id=data_id,
            classification=data.classification.value,
            access_granted=has_access
        )

        return has_access
                ''',
            },
            "c1_2_encryption": {
                "description": "Confidential data is encrypted",
                "good": '''
# GOOD: Encryption for confidential data
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

class EncryptionService:
    def __init__(self):
        self.key_service = KeyManagementService()

    def encrypt_field(self, plaintext: str, classification: DataClassification) -> str:
        """Encrypt sensitive field"""
        if classification not in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
            return plaintext  # No encryption needed for lower classifications

        # Get encryption key (rotated regularly)
        key = self.key_service.get_current_key()
        fernet = Fernet(key)

        encrypted = fernet.encrypt(plaintext.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_field(self, ciphertext: str, key_id: str) -> str:
        """Decrypt sensitive field"""
        key = self.key_service.get_key(key_id)
        fernet = Fernet(key)

        encrypted = base64.b64decode(ciphertext.encode())
        return fernet.decrypt(encrypted).decode()

class KeyManagementService:
    """Key management with rotation"""

    def __init__(self):
        self.kms = aws_kms.Client()  # Or HashiCorp Vault

    def get_current_key(self) -> bytes:
        """Get current encryption key from KMS"""
        response = self.kms.decrypt(
            KeyId=config.KMS_KEY_ID,
            CiphertextBlob=self._get_encrypted_dek()
        )
        return base64.b64encode(response["Plaintext"])

    def rotate_keys(self):
        """Rotate encryption keys (scheduled monthly)"""
        # Generate new DEK
        new_dek = Fernet.generate_key()

        # Encrypt with KMS CMK
        encrypted_dek = self.kms.encrypt(
            KeyId=config.KMS_KEY_ID,
            Plaintext=new_dek
        )["CiphertextBlob"]

        # Store new key version
        key_version = {
            "version": self._get_next_version(),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode(),
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        db.save(EncryptionKey(**key_version))

        # Mark old key as deprecated (keep for decryption)
        self._deprecate_old_keys()

        # Audit log
        audit_log.info(
            "Encryption key rotated",
            new_version=key_version["version"]
        )
                ''',
            },
        }

    # =========================================================================
    # AUDIT LOGGING
    # =========================================================================

    @staticmethod
    def audit_logging() -> Dict[str, Any]:
        """Comprehensive audit logging for SOC 2 compliance"""
        return {
            "structured_logging": '''
# GOOD: Structured audit logging
import structlog
from typing import Any

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class AuditLogger:
    def __init__(self):
        self.logger = structlog.get_logger("audit")

    def log_event(
        self,
        event_type: str,
        action: str,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        outcome: str,
        details: dict[str, Any] = None
    ):
        """Log audit event with required fields"""
        self.logger.info(
            event_type,
            action=action,
            actor_id=actor_id,
            actor_ip=request.remote_addr if request else None,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            details=details or {},
            session_id=get_session_id(),
            request_id=get_request_id(),
        )

    def log_authentication(
        self,
        user_id: str,
        method: str,
        success: bool,
        failure_reason: str = None
    ):
        """Log authentication events"""
        self.log_event(
            event_type="authentication",
            action="login" if success else "login_failed",
            actor_id=user_id,
            resource_type="session",
            resource_id=get_session_id() if success else "none",
            outcome="success" if success else "failure",
            details={
                "method": method,
                "failure_reason": failure_reason,
                "user_agent": request.headers.get("User-Agent"),
                "mfa_used": method == "mfa"
            }
        )

    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,  # read, create, update, delete
        fields_accessed: list[str] = None
    ):
        """Log data access events"""
        self.log_event(
            event_type="data_access",
            action=action,
            actor_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome="success",
            details={
                "fields_accessed": fields_accessed,
                "query_time_ms": get_query_time()
            }
        )

    def log_configuration_change(
        self,
        user_id: str,
        setting_name: str,
        old_value: Any,
        new_value: Any
    ):
        """Log configuration changes"""
        self.log_event(
            event_type="configuration_change",
            action="update",
            actor_id=user_id,
            resource_type="configuration",
            resource_id=setting_name,
            outcome="success",
            details={
                "old_value": str(old_value),
                "new_value": str(new_value)
            }
        )

audit_log = AuditLogger()
            ''',
            "log_retention": '''
# GOOD: Log retention and archival
class LogRetentionService:
    def __init__(self):
        self.retention_periods = {
            "audit_logs": 365 * 7,      # 7 years for SOC 2
            "security_logs": 365 * 3,   # 3 years
            "application_logs": 90,      # 90 days
            "debug_logs": 30             # 30 days
        }

    def archive_old_logs(self, log_type: str):
        """Archive logs past retention period"""
        retention_days = self.retention_periods[log_type]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Archive to cold storage
        logs_to_archive = db.query(Log).filter(
            Log.type == log_type,
            Log.created_at < cutoff_date,
            Log.archived == False
        ).all()

        for batch in chunk(logs_to_archive, 1000):
            # Compress and encrypt
            archive_file = self._create_archive(batch)

            # Upload to S3 Glacier
            storage.upload(
                archive_file,
                bucket=config.ARCHIVE_BUCKET,
                storage_class="GLACIER"
            )

            # Mark as archived
            for log in batch:
                log.archived = True
                log.archive_location = archive_file
            db.commit()

        audit_log.info(
            "Logs archived",
            log_type=log_type,
            count=len(logs_to_archive),
            cutoff_date=cutoff_date.isoformat()
        )
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        trust_criteria: str,
        control_objective: str,
        current_state: str,
        required_state: str,
        evidence_needed: List[str],
    ) -> SOC2Finding:
        """Generate a structured SOC 2 finding"""
        return SOC2Finding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            trust_criteria=trust_criteria,
            control_objective=control_objective,
            current_state=current_state,
            required_state=required_state,
            evidence_needed=evidence_needed,
            remediation={
                "effort": "MEDIUM" if severity in ["LOW", "MEDIUM"] else "HIGH",
                "priority": severity,
                "timeline": "30 days" if severity == "CRITICAL" else "90 days"
            }
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for SOC 2 compliance"""
        return [
            {
                "name": "Vanta",
                "command": "vanta-agent --scan",
                "description": "Automated compliance monitoring and evidence collection"
            },
            {
                "name": "Drata",
                "command": "drata scan --framework soc2",
                "description": "Continuous compliance automation"
            },
            {
                "name": "AWS Config",
                "command": "aws configservice get-compliance-details-by-config-rule --config-rule-name soc2-rules",
                "description": "AWS compliance rule evaluation"
            },
            {
                "name": "Prowler",
                "command": "prowler aws --compliance soc2",
                "description": "AWS security best practices assessment"
            },
            {
                "name": "ScoutSuite",
                "command": "scout aws --ruleset soc2",
                "description": "Multi-cloud security auditing"
            },
            {
                "name": "Lynis",
                "command": "lynis audit system --pentest",
                "description": "Unix/Linux system security auditing"
            },
        ]


def create_enhanced_soc2_assistant():
    """Factory function to create Enhanced SOC 2 Compliance Assistant"""
    return {
        "name": "Enhanced SOC 2 Compliance Reviewer",
        "version": "2.0.0",
        "system_prompt": """You are an expert SOC 2 compliance reviewer and auditor with comprehensive
knowledge of the AICPA Trust Service Criteria framework. Your expertise covers:

TRUST SERVICE CRITERIA:
- Security (CC1-CC9): Control environment, communication, risk assessment, monitoring,
  control activities, logical/physical access, system operations, change management, risk mitigation
- Availability (A1): Capacity planning, disaster recovery, backup procedures, SLA management
- Processing Integrity (PI1): Data validation, error handling, reconciliation, output verification
- Confidentiality (C1): Data classification, encryption, access controls, disposal
- Privacy (P1-P8): Notice, choice, collection, use, disclosure, access, quality, monitoring

AUDIT EXPERTISE:
- Type I (point-in-time) vs Type II (period assessment) audit differences
- Evidence collection and documentation requirements
- Control testing procedures and sampling methodologies
- Gap analysis and remediation planning
- Common Control Criteria (CC) mapping

TECHNICAL IMPLEMENTATION:
- Authentication and MFA implementation
- Access control provisioning and review
- Vulnerability management and monitoring
- Incident response procedures
- Change management workflows
- Backup and recovery testing
- Audit logging and retention
- Encryption and key management

Analyze systems, code, and processes for SOC 2 compliance gaps. Provide specific,
actionable findings with evidence requirements and remediation guidance. Reference
specific Trust Service Criteria and Common Criteria in your assessments.

Format findings with severity levels, affected criteria, and estimated remediation effort.""",
        "assistant_class": EnhancedSOC2Assistant,
        "finding_model": SOC2Finding,
        "domain": "compliance",
        "subdomain": "soc2",
        "tags": ["soc2", "audit", "compliance", "security", "controls", "trust-services"],
        "tools": EnhancedSOC2Assistant.get_tool_recommendations(),
        "capabilities": [
            "trust_service_criteria_assessment",
            "control_testing",
            "evidence_collection",
            "gap_analysis",
            "remediation_planning",
            "audit_preparation"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedSOC2Assistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate Trust Service Criteria
    print("--- Trust Service Criteria ---")
    tsc = assistant.trust_service_criteria()
    for criteria, details in tsc.items():
        print(f"\n{criteria.upper()}:")
        print(f"  Required: {details.get('required', 'N/A')}")
        print(f"  Description: {details.get('description', '')[:100]}...")

    # Demonstrate Type Comparison
    print("\n--- Type I vs Type II ---")
    types = assistant.type_comparison()
    for audit_type, details in types.items():
        print(f"\n{audit_type.upper()}:")
        print(f"  Description: {details['description']}")
        print(f"  Duration: {details['duration']}")
        print(f"  What's tested: {details['what_tested']}")

    # Show security controls
    print("\n--- Logical Access Controls (CC6) ---")
    cc6 = assistant.logical_access_controls()
    for control_id, details in cc6.items():
        print(f"\n{control_id}:")
        print(f"  {details['description']}")

    # Show system operations
    print("\n--- System Operations (CC7) ---")
    cc7 = assistant.system_operations()
    for control_id, details in cc7.items():
        print(f"\n{control_id}:")
        print(f"  {details['description']}")

    # Show change management
    print("\n--- Change Management (CC8) ---")
    cc8 = assistant.change_management()
    for control_id, details in cc8.items():
        print(f"\n{control_id}:")
        print(f"  {details['description']}")

    # Show availability controls
    print("\n--- Availability Controls (A1) ---")
    a1 = assistant.availability_controls()
    for control_id, details in a1.items():
        print(f"\n{control_id}:")
        print(f"  {details['description']}")

    # Show evidence collection requirements
    print("\n--- Evidence Collection ---")
    evidence = assistant.evidence_collection()
    for category, items in evidence.items():
        print(f"\n{category}:")
        for item in items[:3]:
            print(f"  - {item}")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="SOC2-001",
        title="Missing Multi-Factor Authentication",
        severity="HIGH",
        trust_criteria="CC6.1",
        control_objective="Logical access security measures restrict access",
        current_state="Single-factor authentication (password only)",
        required_state="Multi-factor authentication for all users",
        evidence_needed=[
            "MFA configuration screenshots",
            "User enrollment reports",
            "Authentication logs showing MFA usage"
        ]
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Trust Criteria: {finding.trust_criteria}")
    print(f"Remediation: {finding.remediation}")

    # Show tool recommendations
    print("\n--- Tool Recommendations ---")
    tools = assistant.get_tool_recommendations()
    for tool in tools[:3]:
        print(f"\n{tool['name']}:")
        print(f"  Command: {tool['command']}")
        print(f"  Description: {tool['description']}")

    # Show factory function output
    print("\n--- Factory Function ---")
    config = create_enhanced_soc2_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
