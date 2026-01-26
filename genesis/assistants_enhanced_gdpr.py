"""
Enhanced GDPR Compliance Reviewer Assistant

Comprehensive GDPR compliance covering:
- 6 Lawful bases for processing (Article 6)
- Special category data (Article 9)
- Data Protection Impact Assessment (DPIA) triggers
- Privacy by Design and Default
- Data Processing Agreements (DPA)
- Cross-border data transfers (SCCs, BCRs)
- User rights implementation (access, erasure, portability)
- Consent management
- Breach notification (72 hours)

References:
- GDPR Regulation (EU) 2016/679
- EDPB Guidelines
- ICO Guidance
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class GDPRFinding(BaseModel):
    """Structured GDPR finding output"""

    finding_id: str = Field(..., description="Unique identifier (GDPR-001, etc.)")
    title: str = Field(..., description="Brief title of the compliance issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="LawfulBasis/Consent/Rights/Transfer/Security")

    gdpr_article: str = Field(default="", description="Relevant GDPR Article")
    description: str = Field(..., description="Detailed description")
    risk: str = Field(default="", description="Risk of non-compliance")
    fine_risk: str = Field(default="", description="Potential fine (up to €20M or 4%)")

    current_implementation: str = Field(default="", description="Current code/process")
    compliant_implementation: str = Field(default="", description="Compliant code/process")

    remediation: Dict[str, str] = Field(default_factory=dict)
    references: List[str] = Field(default_factory=list)


class EnhancedGDPRAssistant:
    """Enhanced GDPR Compliance Reviewer"""

    def __init__(self):
        self.name = "Enhanced GDPR Compliance Reviewer"
        self.version = "2.0.0"
        self.standards = ["GDPR", "ePrivacy", "EDPB Guidelines"]

    # =========================================================================
    # LAWFUL BASES (Article 6)
    # =========================================================================

    @staticmethod
    def lawful_bases() -> Dict[str, Any]:
        """Six lawful bases for processing personal data"""
        return {
            "consent": {
                "article": "Article 6(1)(a)",
                "requirements": [
                    "Freely given (no detriment for refusing)",
                    "Specific (for each purpose)",
                    "Informed (clear explanation)",
                    "Unambiguous (clear affirmative action)",
                    "Withdrawable (easy to withdraw as to give)",
                ],
                "bad": """
# BAD: Pre-ticked checkbox
<input type="checkbox" checked name="marketing_consent">
I agree to receive marketing emails

# BAD: Bundled consent
<input type="checkbox" name="all_consent">
I agree to Terms, Privacy Policy, and Marketing
                """,
                "good": """
# GOOD: Granular, opt-in consent
<fieldset>
  <legend>Communication preferences</legend>

  <input type="checkbox" id="marketing" name="marketing_consent">
  <label for="marketing">
    I want to receive marketing emails about new products
    <a href="/privacy#marketing">Learn more</a>
  </label>

  <input type="checkbox" id="analytics" name="analytics_consent">
  <label for="analytics">
    I allow analytics cookies to improve user experience
    <a href="/privacy#analytics">Learn more</a>
  </label>
</fieldset>

# Store consent with metadata
consent_record = {
    "user_id": user.id,
    "purpose": "marketing_emails",
    "given_at": datetime.utcnow(),
    "method": "web_form",
    "version": "privacy_policy_v2.3",
    "ip_address": request.ip,  # For audit trail
    "withdrawable": True
}
                """,
            },
            "contract": {
                "article": "Article 6(1)(b)",
                "description": "Processing necessary for contract performance",
                "valid_uses": [
                    "Processing delivery address to ship order",
                    "Processing payment details to complete purchase",
                    "Processing employment data for payroll",
                ],
                "invalid_uses": [
                    "Marketing (not necessary for contract)",
                    "Profiling for personalization",
                    "Sharing with third parties for their purposes",
                ],
            },
            "legal_obligation": {
                "article": "Article 6(1)(c)",
                "description": "Processing required by law",
                "examples": [
                    "Tax records retention (usually 7 years)",
                    "Employment records",
                    "Anti-money laundering (AML) checks",
                    "Medical records retention",
                ],
            },
            "vital_interests": {
                "article": "Article 6(1)(d)",
                "description": "Protect life of data subject or another person",
                "examples": ["Medical emergency", "Natural disaster response"],
                "note": "Rarely applicable for commercial organizations",
            },
            "public_task": {
                "article": "Article 6(1)(e)",
                "description": "Processing for public interest or official authority",
                "examples": ["Government services", "Public health"],
            },
            "legitimate_interests": {
                "article": "Article 6(1)(f)",
                "description": "Legitimate business interests (with balancing test)",
                "requirements": """
# Three-part test (LIA - Legitimate Interests Assessment)

1. PURPOSE TEST: Is there a legitimate interest?
   - Business interest (fraud prevention, security)
   - Third party interest
   - Societal benefit

2. NECESSITY TEST: Is processing necessary?
   - No less intrusive way to achieve the purpose?
   - Proportionate to the interest?

3. BALANCING TEST: Do data subject rights override?
   - Nature of personal data (sensitive?)
   - Reasonable expectations of data subject?
   - Relationship with data subject?
   - Potential harm to data subject?
   - Safeguards in place?
                """,
                "valid_examples": [
                    "Fraud prevention",
                    "Network security",
                    "Direct marketing to existing customers (with opt-out)",
                    "Intra-group data transfers for admin purposes",
                ],
            },
        }

    # =========================================================================
    # USER RIGHTS
    # =========================================================================

    @staticmethod
    def user_rights() -> Dict[str, Any]:
        """Data subject rights implementation"""
        return {
            "right_to_access": {
                "article": "Article 15",
                "deadline": "1 month (extendable to 3 months for complex requests)",
                "must_provide": [
                    "Purposes of processing",
                    "Categories of personal data",
                    "Recipients or categories of recipients",
                    "Retention period",
                    "Existence of other rights",
                    "Source of data (if not from subject)",
                    "Automated decision-making info",
                ],
                "implementation": """
# Subject Access Request (SAR) endpoint
@app.post("/api/v1/data-requests/access")
async def request_data_access(request: AccessRequest, user: User):
    # Verify identity
    if not verify_identity(user, request.verification_docs):
        raise HTTPException(401, "Identity verification required")

    # Create SAR ticket
    sar = SubjectAccessRequest(
        user_id=user.id,
        requested_at=datetime.utcnow(),
        deadline=datetime.utcnow() + timedelta(days=30),
        status="pending"
    )
    db.save(sar)

    # Async job to collect data from all systems
    collect_user_data.delay(sar.id, user.id)

    return {"request_id": sar.id, "deadline": sar.deadline}

# Data collection job
async def collect_user_data(sar_id: str, user_id: str):
    data = {
        "profile": await user_service.get_user_data(user_id),
        "orders": await order_service.get_user_orders(user_id),
        "support_tickets": await support_service.get_tickets(user_id),
        "marketing_preferences": await marketing_service.get_prefs(user_id),
        "login_history": await auth_service.get_login_history(user_id),
        # ... all systems holding personal data
    }

    # Generate portable format (JSON, CSV)
    export_file = generate_export(data)

    # Notify user
    send_sar_complete_email(user_id, export_file)
                """,
            },
            "right_to_erasure": {
                "article": "Article 17 (Right to be Forgotten)",
                "grounds": [
                    "Data no longer necessary for original purpose",
                    "Consent withdrawn",
                    "Data subject objects (and no overriding legitimate grounds)",
                    "Unlawful processing",
                    "Legal obligation to erase",
                ],
                "exceptions": [
                    "Legal obligation to retain",
                    "Public health purposes",
                    "Archiving in public interest",
                    "Legal claims",
                ],
                "implementation": """
# Erasure request endpoint
@app.post("/api/v1/data-requests/erasure")
async def request_erasure(request: ErasureRequest, user: User):
    # Verify identity
    verify_identity(user, request.verification)

    # Check for legal retention requirements
    retention_blocks = check_retention_requirements(user.id)
    if retention_blocks:
        return {
            "status": "partial",
            "message": "Some data must be retained",
            "retained_categories": retention_blocks,
            "retention_reasons": get_retention_reasons(retention_blocks)
        }

    # Create erasure job
    erasure_request = ErasureRequest(
        user_id=user.id,
        requested_at=datetime.utcnow(),
        status="pending"
    )
    db.save(erasure_request)

    # Async erasure from all systems
    erase_user_data.delay(erasure_request.id, user.id)

    return {"request_id": erasure_request.id, "status": "processing"}

# Erasure job - must erase from ALL systems
async def erase_user_data(request_id: str, user_id: str):
    systems = [
        ("user_db", user_service.delete_user),
        ("orders_db", order_service.anonymize_orders),
        ("analytics", analytics_service.delete_user_data),
        ("backups", backup_service.queue_erasure),
        ("logs", log_service.redact_user_data),
        ("third_parties", notify_third_parties),
    ]

    for system_name, delete_func in systems:
        try:
            await delete_func(user_id)
            log_erasure(request_id, system_name, "success")
        except Exception as e:
            log_erasure(request_id, system_name, "failed", str(e))
            alert_dpo(request_id, system_name, e)
                """,
            },
            "right_to_portability": {
                "article": "Article 20",
                "requirements": [
                    "Machine-readable format (JSON, CSV, XML)",
                    "Structured, commonly used format",
                    "Data provided by subject OR generated by their activity",
                    "Only applies to consent or contract basis",
                ],
                "implementation": """
# Data portability endpoint
@app.get("/api/v1/data-requests/export")
async def export_data(format: str = "json", user: User = Depends(get_user)):
    # Collect portable data
    portable_data = {
        "profile": {
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
        },
        "activity": {
            "orders": [order.to_dict() for order in user.orders],
            "reviews": [review.to_dict() for review in user.reviews],
            "wishlist": [item.to_dict() for item in user.wishlist],
        },
        "preferences": user.preferences,
        "exported_at": datetime.utcnow().isoformat(),
        "format_version": "1.0"
    }

    if format == "json":
        return JSONResponse(portable_data)
    elif format == "csv":
        return generate_csv_export(portable_data)
                """,
            },
        }

    # =========================================================================
    # DATA TRANSFERS
    # =========================================================================

    @staticmethod
    def cross_border_transfers() -> Dict[str, Any]:
        """Cross-border data transfer mechanisms"""
        return {
            "adequacy_decisions": {
                "description": "Countries deemed adequate by EU Commission",
                "countries": [
                    "UK", "Switzerland", "Canada (commercial)",
                    "Japan", "South Korea", "New Zealand",
                    "Israel", "Argentina", "Uruguay"
                ],
                "note": "US: Data Privacy Framework (2023) - check current status",
            },
            "standard_contractual_clauses": {
                "description": "SCCs for transfers to non-adequate countries",
                "requirements": [
                    "Use latest EU SCCs (2021 version)",
                    "Complete Transfer Impact Assessment (TIA)",
                    "Implement supplementary measures if needed",
                ],
                "dpa_clause_example": """
# DPA with SCCs reference
class DataProcessingAgreement:
    processor: str
    controller: str
    sccs_module: str  # Module 1, 2, 3, or 4
    transfer_impact_assessment: str
    supplementary_measures: List[str]

# SCCs Module selection:
# Module 1: Controller to Controller
# Module 2: Controller to Processor (most common)
# Module 3: Processor to Processor
# Module 4: Processor to Controller
                """,
            },
        }

    # =========================================================================
    # BREACH NOTIFICATION
    # =========================================================================

    @staticmethod
    def breach_notification() -> Dict[str, Any]:
        """Data breach notification requirements"""
        return {
            "supervisory_authority": {
                "deadline": "72 hours from awareness",
                "threshold": "Unless unlikely to result in risk to rights/freedoms",
                "must_include": [
                    "Nature of breach (categories, number of subjects)",
                    "DPO contact details",
                    "Likely consequences",
                    "Measures taken/proposed",
                ],
            },
            "data_subjects": {
                "deadline": "Without undue delay",
                "threshold": "High risk to rights and freedoms",
                "must_include": [
                    "Clear, plain language description",
                    "DPO contact details",
                    "Likely consequences",
                    "Measures taken to address",
                    "Measures subjects can take to protect themselves",
                ],
            },
            "implementation": """
# Breach response workflow
class BreachIncident:
    detected_at: datetime
    detected_by: str
    description: str
    affected_data_categories: List[str]
    affected_subjects_count: int
    risk_level: str  # LOW, MEDIUM, HIGH

    def assess_notification_requirement(self):
        # 72-hour deadline starts when "aware" of breach
        deadline = self.detected_at + timedelta(hours=72)

        # Must notify supervisory authority unless no risk
        notify_authority = self.risk_level != "LOW"

        # Must notify subjects if high risk
        notify_subjects = self.risk_level == "HIGH"

        return {
            "notify_authority": notify_authority,
            "notify_subjects": notify_subjects,
            "authority_deadline": deadline,
            "authority_template": self.generate_authority_notification(),
            "subject_template": self.generate_subject_notification()
        }
            """,
        }

    # =========================================================================
    # PRIVACY BY DESIGN (Article 25)
    # =========================================================================

    @staticmethod
    def privacy_by_design() -> Dict[str, Any]:
        """Privacy by Design and Default (Article 25)"""
        return {
            "principles": {
                "proactive": "Anticipate and prevent privacy risks before they occur",
                "default": "Maximum privacy as the default setting",
                "embedded": "Privacy built into design, not bolted on",
                "functionality": "Full functionality - no false trade-offs",
                "end_to_end": "Protection throughout the data lifecycle",
                "visibility": "Transparent operations",
                "respect": "User-centric design",
            },
            "data_minimization": {
                "bad": '''
# BAD: Collecting unnecessary data
def register_user(data: dict):
    user = User(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        date_of_birth=data["dob"],  # Why needed for newsletter?
        address=data["address"],     # Why needed?
        occupation=data["occupation"],  # Why needed?
        income_bracket=data["income"],  # Definitely not needed!
    )
    db.save(user)
                ''',
                "good": '''
# GOOD: Collect only what's necessary
from enum import Enum

class ProcessingPurpose(Enum):
    NEWSLETTER = "newsletter"
    ORDER_FULFILLMENT = "order_fulfillment"
    SUPPORT = "support"

# Define minimum required fields per purpose
REQUIRED_FIELDS = {
    ProcessingPurpose.NEWSLETTER: ["email"],
    ProcessingPurpose.ORDER_FULFILLMENT: ["name", "email", "shipping_address"],
    ProcessingPurpose.SUPPORT: ["name", "email"],
}

def register_user(data: dict, purpose: ProcessingPurpose):
    """Register user with only required fields"""
    required = REQUIRED_FIELDS[purpose]

    # Only store what's necessary
    user_data = {field: data[field] for field in required if field in data}
    user_data["processing_purpose"] = purpose.value

    user = User(**user_data)
    db.save(user)

    # Audit log
    audit_log.info(
        "User registered with data minimization",
        purpose=purpose.value,
        fields_collected=list(user_data.keys())
    )

    return user
                ''',
            },
            "pseudonymization": '''
# GOOD: Pseudonymization for analytics
import hashlib
import secrets

class PseudonymizationService:
    """Pseudonymize personal data for analytics"""

    def __init__(self):
        # Salt should be stored securely, rotated periodically
        self.salt = config.PSEUDONYMIZATION_SALT

    def pseudonymize_id(self, user_id: str) -> str:
        """Create consistent pseudonym for user ID"""
        return hashlib.sha256(
            f"{self.salt}{user_id}".encode()
        ).hexdigest()[:16]

    def pseudonymize_email(self, email: str) -> str:
        """Pseudonymize email, preserving domain for analytics"""
        local, domain = email.split("@")
        pseudo_local = hashlib.sha256(
            f"{self.salt}{local}".encode()
        ).hexdigest()[:8]
        return f"{pseudo_local}@{domain}"

    def pseudonymize_record(self, record: dict, fields: list[str]) -> dict:
        """Pseudonymize specified fields in a record"""
        result = record.copy()

        for field in fields:
            if field in result and result[field]:
                if field == "email":
                    result[field] = self.pseudonymize_email(result[field])
                else:
                    result[field] = self.pseudonymize_id(result[field])

        return result

# Usage for analytics export
def export_analytics_data(start_date: date, end_date: date) -> list:
    """Export pseudonymized data for analytics"""
    records = db.query(UserActivity).filter(
        UserActivity.timestamp.between(start_date, end_date)
    ).all()

    pseudonymizer = PseudonymizationService()

    return [
        pseudonymizer.pseudonymize_record(
            record.to_dict(),
            fields=["user_id", "email", "name"]
        )
        for record in records
    ]
            ''',
            "storage_limitation": '''
# GOOD: Implement data retention policies
from datetime import datetime, timedelta
from enum import Enum

class DataCategory(Enum):
    ACCOUNT_DATA = "account_data"
    TRANSACTION_DATA = "transaction_data"
    MARKETING_DATA = "marketing_data"
    SUPPORT_DATA = "support_data"
    ANALYTICS_DATA = "analytics_data"

# Retention periods per data category
RETENTION_PERIODS = {
    DataCategory.ACCOUNT_DATA: timedelta(days=0),  # Until account deletion
    DataCategory.TRANSACTION_DATA: timedelta(days=365 * 7),  # 7 years (legal)
    DataCategory.MARKETING_DATA: timedelta(days=365 * 2),  # 2 years
    DataCategory.SUPPORT_DATA: timedelta(days=365 * 3),  # 3 years
    DataCategory.ANALYTICS_DATA: timedelta(days=365),  # 1 year
}

class DataRetentionService:
    """Manage data retention and deletion"""

    def apply_retention_policy(self, category: DataCategory):
        """Delete data past retention period"""
        retention = RETENTION_PERIODS[category]
        cutoff_date = datetime.utcnow() - retention

        if category == DataCategory.MARKETING_DATA:
            deleted = db.execute(
                "DELETE FROM marketing_consents WHERE created_at < :cutoff",
                {"cutoff": cutoff_date}
            )
        elif category == DataCategory.ANALYTICS_DATA:
            deleted = db.execute(
                "DELETE FROM user_analytics WHERE created_at < :cutoff",
                {"cutoff": cutoff_date}
            )
        # ... other categories

        audit_log.info(
            "Retention policy applied",
            category=category.value,
            cutoff_date=cutoff_date.isoformat(),
            records_deleted=deleted.rowcount
        )

    def schedule_deletion(self, user_id: str, deletion_date: datetime):
        """Schedule data deletion (for account deletion requests)"""
        db.save(DeletionSchedule(
            user_id=user_id,
            scheduled_for=deletion_date,
            status="pending"
        ))

        audit_log.info(
            "Data deletion scheduled",
            user_id=user_id,
            scheduled_for=deletion_date.isoformat()
        )
            ''',
        }

    # =========================================================================
    # DATA PROTECTION IMPACT ASSESSMENT (Article 35)
    # =========================================================================

    @staticmethod
    def dpia() -> Dict[str, Any]:
        """Data Protection Impact Assessment requirements"""
        return {
            "when_required": [
                "Systematic and extensive profiling with significant effects",
                "Large-scale processing of special category data (Article 9)",
                "Large-scale systematic monitoring of public areas",
                "Processing using new technologies with high risk",
                "Processing that could deny services or contracts",
                "Large-scale processing of data on vulnerable individuals",
            ],
            "must_contain": [
                "Systematic description of processing operations and purposes",
                "Assessment of necessity and proportionality",
                "Assessment of risks to rights and freedoms",
                "Measures to address risks (safeguards, security, mechanisms)",
            ],
            "implementation": '''
# GOOD: DPIA implementation
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DPIARisk:
    description: str
    likelihood: RiskLevel
    impact: RiskLevel
    affected_rights: list[str]
    mitigations: list[str]
    residual_risk: RiskLevel

@dataclass
class DPIA:
    id: str
    project_name: str
    description: str
    data_controller: str
    dpo_consulted: bool
    dpo_opinion: str

    # Processing description
    data_subjects: list[str]  # Customers, employees, etc.
    data_categories: list[str]
    special_categories: list[str]  # Article 9 data
    processing_purposes: list[str]
    lawful_bases: list[str]
    retention_period: str
    recipients: list[str]
    international_transfers: bool
    transfer_safeguards: Optional[str]

    # Necessity and proportionality
    necessity_assessment: str
    proportionality_assessment: str

    # Risks and mitigations
    identified_risks: list[DPIARisk] = field(default_factory=list)
    overall_risk_level: RiskLevel = RiskLevel.MEDIUM

    # Sign-off
    completed_by: str
    completed_at: datetime
    review_date: datetime
    status: str  # draft, review, approved, rejected

class DPIAService:
    def create_dpia(self, project_name: str, description: str) -> DPIA:
        """Create new DPIA"""
        dpia = DPIA(
            id=f"DPIA-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            project_name=project_name,
            description=description,
            data_controller=config.DATA_CONTROLLER,
            dpo_consulted=False,
            dpo_opinion="",
            data_subjects=[],
            data_categories=[],
            special_categories=[],
            processing_purposes=[],
            lawful_bases=[],
            retention_period="",
            recipients=[],
            international_transfers=False,
            transfer_safeguards=None,
            necessity_assessment="",
            proportionality_assessment="",
            identified_risks=[],
            overall_risk_level=RiskLevel.MEDIUM,
            completed_by="",
            completed_at=None,
            review_date=datetime.utcnow() + timedelta(days=365),
            status="draft"
        )
        db.save(dpia)
        return dpia

    def add_risk(
        self,
        dpia_id: str,
        description: str,
        likelihood: RiskLevel,
        impact: RiskLevel,
        affected_rights: list[str],
        mitigations: list[str]
    ) -> DPIARisk:
        """Add identified risk to DPIA"""
        dpia = db.query(DPIA).get(dpia_id)

        # Calculate residual risk after mitigations
        residual = self._calculate_residual_risk(likelihood, impact, len(mitigations))

        risk = DPIARisk(
            description=description,
            likelihood=likelihood,
            impact=impact,
            affected_rights=affected_rights,
            mitigations=mitigations,
            residual_risk=residual
        )
        dpia.identified_risks.append(risk)

        # Update overall risk
        dpia.overall_risk_level = self._calculate_overall_risk(dpia.identified_risks)

        db.save(dpia)
        return risk

    def _calculate_residual_risk(
        self,
        likelihood: RiskLevel,
        impact: RiskLevel,
        mitigation_count: int
    ) -> RiskLevel:
        """Calculate residual risk after mitigations"""
        risk_matrix = {
            (RiskLevel.LOW, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.LOW, RiskLevel.MEDIUM): RiskLevel.LOW,
            (RiskLevel.MEDIUM, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.HIGH, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.HIGH, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.CRITICAL, RiskLevel.HIGH): RiskLevel.CRITICAL,
        }
        inherent = risk_matrix.get((likelihood, impact), RiskLevel.MEDIUM)

        # Reduce by one level per 2 mitigations (simplified)
        reduction = mitigation_count // 2
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        current_index = risk_levels.index(inherent)
        new_index = max(0, current_index - reduction)

        return risk_levels[new_index]

    def consult_dpo(self, dpia_id: str, dpo_id: str, opinion: str):
        """Record DPO consultation"""
        dpia = db.query(DPIA).get(dpia_id)
        dpia.dpo_consulted = True
        dpia.dpo_opinion = opinion
        db.save(dpia)

        # If high residual risk, must consult supervisory authority
        if dpia.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            notification_service.send(
                to="privacy@company.com",
                template="dpia_high_risk",
                data={"dpia": dpia, "message": "Consider consulting supervisory authority"}
            )
            ''',
        }

    # =========================================================================
    # SPECIAL CATEGORY DATA (Article 9)
    # =========================================================================

    @staticmethod
    def special_category_data() -> Dict[str, Any]:
        """Special category data handling (Article 9)"""
        return {
            "categories": [
                "Racial or ethnic origin",
                "Political opinions",
                "Religious or philosophical beliefs",
                "Trade union membership",
                "Genetic data",
                "Biometric data for identification",
                "Health data",
                "Sex life or sexual orientation",
            ],
            "lawful_bases_article_9": [
                "Explicit consent",
                "Employment, social security law obligations",
                "Vital interests (subject incapable of consent)",
                "Legitimate activities of foundations/associations",
                "Data manifestly made public by subject",
                "Legal claims",
                "Substantial public interest",
                "Medical diagnosis/treatment",
                "Public health",
                "Archiving in public interest, research, statistics",
            ],
            "implementation": '''
# GOOD: Special category data handling
from enum import Enum
from typing import Optional

class SpecialCategory(Enum):
    RACIAL_ETHNIC = "racial_ethnic_origin"
    POLITICAL = "political_opinions"
    RELIGIOUS = "religious_beliefs"
    TRADE_UNION = "trade_union_membership"
    GENETIC = "genetic_data"
    BIOMETRIC = "biometric_data"
    HEALTH = "health_data"
    SEXUAL = "sex_life_orientation"

class Article9Basis(Enum):
    EXPLICIT_CONSENT = "explicit_consent"
    EMPLOYMENT_LAW = "employment_law"
    VITAL_INTERESTS = "vital_interests"
    FOUNDATION_ACTIVITIES = "foundation_activities"
    MANIFESTLY_PUBLIC = "manifestly_public"
    LEGAL_CLAIMS = "legal_claims"
    PUBLIC_INTEREST = "public_interest"
    MEDICAL = "medical_diagnosis"
    PUBLIC_HEALTH = "public_health"
    RESEARCH = "research_statistics"

class SpecialCategoryDataService:
    """Handle special category data per Article 9"""

    def can_process(
        self,
        category: SpecialCategory,
        basis: Article9Basis,
        explicit_consent: Optional[dict] = None
    ) -> tuple[bool, str]:
        """Check if processing is lawful under Article 9"""

        # Explicit consent requires specific evidence
        if basis == Article9Basis.EXPLICIT_CONSENT:
            if not explicit_consent:
                return False, "Explicit consent required but not provided"
            if not self._validate_explicit_consent(explicit_consent, category):
                return False, "Consent not sufficiently explicit for this category"
            return True, "Processing permitted under explicit consent"

        # Medical basis requires healthcare context
        if basis == Article9Basis.MEDICAL:
            if category != SpecialCategory.HEALTH:
                return False, "Medical basis only applies to health data"
            if not self._is_healthcare_context():
                return False, "Not in healthcare professional context"
            return True, "Processing permitted for medical purposes"

        # Employment law basis
        if basis == Article9Basis.EMPLOYMENT_LAW:
            if category not in [
                SpecialCategory.HEALTH,
                SpecialCategory.TRADE_UNION,
                SpecialCategory.RACIAL_ETHNIC
            ]:
                return False, "Employment law basis limited to specific categories"
            return True, "Processing permitted under employment law"

        return False, f"No valid basis for processing {category.value}"

    def _validate_explicit_consent(
        self,
        consent: dict,
        category: SpecialCategory
    ) -> bool:
        """Validate consent is sufficiently explicit for special category"""
        required_elements = [
            "consent_text_specific_to_category",  # Not bundled
            "timestamp",
            "method",
            "category_explicitly_mentioned",
            "purpose_specific",
        ]

        # Check consent record contains all elements
        if not all(elem in consent for elem in required_elements):
            return False

        # Verify category was explicitly mentioned in consent
        if category.value not in consent.get("consent_text", "").lower():
            return False

        return True

    def process_health_data(
        self,
        user_id: str,
        health_data: dict,
        basis: Article9Basis,
        purpose: str
    ):
        """Process health data with appropriate safeguards"""
        # Verify basis
        can_process, reason = self.can_process(
            SpecialCategory.HEALTH,
            basis
        )
        if not can_process:
            raise GDPRViolationError(f"Cannot process health data: {reason}")

        # Encrypt at rest
        encrypted_data = encryption_service.encrypt(
            json.dumps(health_data),
            classification="special_category"
        )

        # Store with audit trail
        record = HealthDataRecord(
            user_id=user_id,
            encrypted_data=encrypted_data,
            lawful_basis=basis.value,
            purpose=purpose,
            processed_at=datetime.utcnow(),
            processed_by=current_user.id
        )
        db.save(record)

        # Comprehensive audit log
        audit_log.info(
            "Special category data processed",
            user_id=user_id,
            category="health_data",
            lawful_basis=basis.value,
            purpose=purpose,
            processed_by=current_user.id
        )
            ''',
        }

    # =========================================================================
    # COOKIE CONSENT (ePrivacy)
    # =========================================================================

    @staticmethod
    def cookie_consent() -> Dict[str, Any]:
        """Cookie consent management (ePrivacy Directive)"""
        return {
            "cookie_categories": {
                "strictly_necessary": "No consent required (essential for service)",
                "functional": "Consent required (preferences, language)",
                "analytics": "Consent required (usage statistics)",
                "marketing": "Consent required (advertising, tracking)",
            },
            "bad": '''
# BAD: Cookie wall / forced consent
// Setting cookies before consent
document.cookie = "analytics_id=" + generateId();
document.cookie = "marketing_id=" + generateId();

// Then showing consent banner
showConsentBanner();
            ''',
            "good": '''
# GOOD: Proper cookie consent implementation
class CookieConsentService:
    """GDPR/ePrivacy compliant cookie consent"""

    STRICTLY_NECESSARY = ["session_id", "csrf_token", "consent_preferences"]

    def __init__(self):
        self.consent_store = {}

    def get_consent_status(self, user_id: str) -> dict:
        """Get current consent status"""
        consent = db.query(CookieConsent).filter_by(user_id=user_id).first()

        if not consent:
            return {
                "strictly_necessary": True,  # Always allowed
                "functional": False,
                "analytics": False,
                "marketing": False,
                "consent_given": False
            }

        return consent.preferences

    def set_consent(self, user_id: str, preferences: dict) -> dict:
        """Record consent preferences"""
        # Validate preferences
        valid_categories = ["functional", "analytics", "marketing"]
        for category in preferences:
            if category not in valid_categories:
                raise ValueError(f"Invalid category: {category}")

        consent = CookieConsent(
            user_id=user_id,
            preferences={
                "strictly_necessary": True,  # Always true
                **{k: bool(v) for k, v in preferences.items()}
            },
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            consent_given_at=datetime.utcnow(),
            consent_version=config.COOKIE_POLICY_VERSION
        )
        db.save(consent)

        # Audit log
        audit_log.info(
            "Cookie consent recorded",
            user_id=user_id,
            preferences=preferences
        )

        return consent.preferences

    def can_set_cookie(self, user_id: str, cookie_name: str, category: str) -> bool:
        """Check if cookie can be set"""
        # Strictly necessary - always allowed
        if cookie_name in self.STRICTLY_NECESSARY:
            return True

        # Check consent for category
        consent = self.get_consent_status(user_id)
        return consent.get(category, False)

    def get_consent_banner_config(self) -> dict:
        """Generate consent banner configuration"""
        return {
            "title": "Cookie Preferences",
            "description": "We use cookies to enhance your experience...",
            "privacy_policy_link": "/privacy-policy",
            "categories": [
                {
                    "id": "strictly_necessary",
                    "name": "Strictly Necessary",
                    "description": "Essential for the website to function",
                    "required": True,
                    "default": True
                },
                {
                    "id": "functional",
                    "name": "Functional",
                    "description": "Remember your preferences",
                    "required": False,
                    "default": False
                },
                {
                    "id": "analytics",
                    "name": "Analytics",
                    "description": "Help us improve our website",
                    "required": False,
                    "default": False
                },
                {
                    "id": "marketing",
                    "name": "Marketing",
                    "description": "Personalized advertisements",
                    "required": False,
                    "default": False
                }
            ],
            "buttons": {
                "accept_all": "Accept All",
                "reject_all": "Reject All",
                "save_preferences": "Save Preferences"
            }
        }
            ''',
        }

    # =========================================================================
    # DATA PROCESSING AGREEMENTS
    # =========================================================================

    @staticmethod
    def data_processing_agreement() -> Dict[str, Any]:
        """Data Processing Agreement requirements (Article 28)"""
        return {
            "required_clauses": [
                "Subject matter and duration of processing",
                "Nature and purpose of processing",
                "Type of personal data and categories of subjects",
                "Controller's obligations and rights",
                "Processor only acts on documented instructions",
                "Confidentiality obligations on personnel",
                "Technical and organizational security measures",
                "Conditions for sub-processor engagement",
                "Assistance with data subject rights",
                "Assistance with security and breach notification",
                "Return or deletion of data after services end",
                "Audit rights",
            ],
            "implementation": '''
# GOOD: DPA management system
@dataclass
class DataProcessingAgreement:
    id: str
    processor_name: str
    processor_contact: str
    controller_name: str

    # Processing details
    subject_matter: str
    duration: str
    processing_nature: str
    processing_purpose: str
    data_types: list[str]
    data_subject_categories: list[str]

    # Security
    security_measures: list[str]
    sub_processors: list[dict]
    sub_processor_approval_required: bool

    # Data subject rights
    rights_assistance_process: str

    # Breach notification
    breach_notification_hours: int  # Usually 24-48

    # Data handling
    data_return_process: str
    data_deletion_process: str

    # Audit
    audit_rights: str

    # SCCs for international transfers
    includes_sccs: bool
    sccs_module: str | None  # 1, 2, 3, or 4

    # Metadata
    effective_date: date
    expiry_date: date
    signed_date: date | None
    status: str  # draft, pending_signature, active, expired

class DPAManagementService:
    def create_dpa(self, processor_name: str, processing_details: dict) -> DataProcessingAgreement:
        """Create new DPA"""
        dpa = DataProcessingAgreement(
            id=f"DPA-{datetime.now().strftime('%Y%m%d')}-{generate_uuid()[:6]}",
            processor_name=processor_name,
            processor_contact=processing_details.get("contact"),
            controller_name=config.COMPANY_NAME,
            subject_matter=processing_details["subject_matter"],
            duration=processing_details["duration"],
            processing_nature=processing_details["nature"],
            processing_purpose=processing_details["purpose"],
            data_types=processing_details["data_types"],
            data_subject_categories=processing_details["subject_categories"],
            security_measures=processing_details.get("security_measures", []),
            sub_processors=processing_details.get("sub_processors", []),
            sub_processor_approval_required=True,
            rights_assistance_process=processing_details.get("rights_process", ""),
            breach_notification_hours=processing_details.get("breach_hours", 24),
            data_return_process=processing_details.get("return_process", ""),
            data_deletion_process=processing_details.get("deletion_process", ""),
            audit_rights=processing_details.get("audit_rights", "Annual audit upon request"),
            includes_sccs=processing_details.get("international_transfer", False),
            sccs_module=processing_details.get("sccs_module"),
            effective_date=processing_details.get("effective_date", date.today()),
            expiry_date=processing_details.get("expiry_date", date.today() + timedelta(days=365)),
            signed_date=None,
            status="draft"
        )
        db.save(dpa)

        audit_log.info("DPA created", dpa_id=dpa.id, processor=processor_name)
        return dpa

    def review_sub_processor(self, dpa_id: str, sub_processor: dict) -> bool:
        """Review new sub-processor request"""
        dpa = db.query(DataProcessingAgreement).get(dpa_id)

        if dpa.sub_processor_approval_required:
            # Create approval request
            approval = SubProcessorApproval(
                dpa_id=dpa_id,
                sub_processor_name=sub_processor["name"],
                sub_processor_purpose=sub_processor["purpose"],
                sub_processor_location=sub_processor["location"],
                requested_at=datetime.utcnow(),
                status="pending"
            )
            db.save(approval)

            # Notify DPO
            notification_service.send(
                to="dpo@company.com",
                template="sub_processor_approval",
                data={"dpa": dpa, "sub_processor": sub_processor}
            )

            return False  # Pending approval

        return True  # Auto-approved
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        gdpr_article: str,
        description: str,
        current_impl: str,
        compliant_impl: str,
    ) -> GDPRFinding:
        """Generate a structured GDPR finding"""
        fine_risk = {
            "CRITICAL": "Up to EUR 20M or 4% global turnover",
            "HIGH": "Up to EUR 10M or 2% global turnover",
            "MEDIUM": "Administrative fines possible",
            "LOW": "Remediation recommended",
        }
        return GDPRFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            gdpr_article=gdpr_article,
            description=description,
            fine_risk=fine_risk.get(severity, ""),
            current_implementation=current_impl,
            compliant_implementation=compliant_impl,
            remediation={
                "effort": "HIGH" if severity in ["CRITICAL", "HIGH"] else "MEDIUM",
                "priority": severity,
                "timeline": "Immediate" if severity == "CRITICAL" else "30 days"
            },
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for GDPR compliance"""
        return [
            {
                "name": "OneTrust",
                "command": "onetrust scan --domain example.com",
                "description": "Privacy management and cookie scanning"
            },
            {
                "name": "Cookiebot",
                "command": "cookiebot scan example.com",
                "description": "Cookie consent and compliance scanning"
            },
            {
                "name": "GDPR Analyzer",
                "command": "gdpr-analyze --project ./",
                "description": "Code analysis for GDPR compliance"
            },
            {
                "name": "DataGrail",
                "command": "datagrail discovery --org myorg",
                "description": "Data discovery and mapping"
            },
            {
                "name": "BigID",
                "command": "bigid scan --data-sources all",
                "description": "Personal data discovery and classification"
            },
            {
                "name": "Transcend",
                "command": "transcend privacy-requests --status pending",
                "description": "Automated DSR fulfillment"
            },
        ]


def create_enhanced_gdpr_assistant():
    """Factory function to create Enhanced GDPR Compliance Assistant"""
    return {
        "name": "Enhanced GDPR Compliance Reviewer",
        "version": "2.0.0",
        "system_prompt": """You are an expert GDPR compliance specialist with comprehensive knowledge
of EU data protection law and implementation best practices. Your expertise covers:

LEGAL FRAMEWORK:
- GDPR Regulation (EU) 2016/679
- ePrivacy Directive (cookies, electronic communications)
- EDPB Guidelines and opinions
- National DPA guidance (ICO, CNIL, etc.)

LAWFUL BASES (Article 6):
- Consent requirements (freely given, specific, informed, unambiguous)
- Contract necessity
- Legal obligation
- Vital interests
- Public task
- Legitimate interests (three-part balancing test)

SPECIAL CATEGORY DATA (Article 9):
- Health, genetic, biometric data
- Racial/ethnic origin, political opinions, religious beliefs
- Trade union membership, sex life/orientation
- Explicit consent and other Article 9(2) bases

DATA SUBJECT RIGHTS:
- Right of access (Article 15) - 1 month deadline
- Right to erasure/right to be forgotten (Article 17)
- Right to data portability (Article 20)
- Right to rectification, restriction, objection

ACCOUNTABILITY REQUIREMENTS:
- Privacy by Design and Default (Article 25)
- Data Protection Impact Assessments (Article 35)
- Records of processing activities (Article 30)
- Data Processing Agreements (Article 28)

INTERNATIONAL TRANSFERS:
- Adequacy decisions
- Standard Contractual Clauses (SCCs 2021)
- Binding Corporate Rules
- Transfer Impact Assessments

BREACH MANAGEMENT:
- 72-hour notification to supervisory authority
- Communication to data subjects (high risk)
- Documentation and remediation

Analyze systems, code, and processes for GDPR compliance gaps.
Provide specific remediation guidance with Article references.

Format findings with severity levels and fine risk assessment.""",
        "assistant_class": EnhancedGDPRAssistant,
        "finding_model": GDPRFinding,
        "domain": "compliance",
        "subdomain": "gdpr",
        "tags": ["gdpr", "privacy", "compliance", "data-protection", "eu", "eprivacy"],
        "tools": EnhancedGDPRAssistant.get_tool_recommendations(),
        "capabilities": [
            "lawful_basis_assessment",
            "consent_review",
            "data_subject_rights_implementation",
            "dpia_guidance",
            "dpa_review",
            "breach_notification",
            "cookie_compliance",
            "international_transfers"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedGDPRAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate lawful bases
    print("--- Lawful Bases (Article 6) ---")
    bases = assistant.lawful_bases()
    for basis, details in list(bases.items())[:3]:
        print(f"\n{basis}: Article {details.get('article', 'N/A')}")

    # Demonstrate user rights
    print("\n--- Data Subject Rights ---")
    rights = assistant.user_rights()
    for right, details in rights.items():
        print(f"\n{right}: {details.get('article', details.get('deadline', 'N/A'))}")

    # Show cross-border transfers
    print("\n--- Cross-Border Transfers ---")
    transfers = assistant.cross_border_transfers()
    print("Adequacy decisions: UK, Switzerland, Japan, etc.")
    print("SCCs: For non-adequate countries with TIA")

    # Show breach notification
    print("\n--- Breach Notification ---")
    breach = assistant.breach_notification()
    print(f"Supervisory Authority: {breach['supervisory_authority']['deadline']}")
    print(f"Data Subjects: {breach['data_subjects']['deadline']}")

    # Show Privacy by Design
    print("\n--- Privacy by Design (Article 25) ---")
    pbd = assistant.privacy_by_design()
    for principle, desc in list(pbd["principles"].items())[:3]:
        print(f"  {principle}: {desc[:50]}...")

    # Show DPIA
    print("\n--- DPIA (Article 35) ---")
    dpia = assistant.dpia()
    print("When required:")
    for trigger in dpia["when_required"][:3]:
        print(f"  - {trigger[:60]}...")

    # Show special category data
    print("\n--- Special Category Data (Article 9) ---")
    special = assistant.special_category_data()
    print("Categories:")
    for cat in special["categories"][:4]:
        print(f"  - {cat}")

    # Show cookie consent
    print("\n--- Cookie Consent (ePrivacy) ---")
    cookies = assistant.cookie_consent()
    for cat, desc in cookies["cookie_categories"].items():
        print(f"  {cat}: {desc}")

    # Show DPA requirements
    print("\n--- Data Processing Agreements (Article 28) ---")
    dpa = assistant.data_processing_agreement()
    print("Required clauses:")
    for clause in dpa["required_clauses"][:4]:
        print(f"  - {clause}")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="GDPR-001",
        title="Pre-ticked Consent Checkbox",
        severity="HIGH",
        category="Consent",
        gdpr_article="Article 6(1)(a), Article 7",
        description="Marketing consent checkbox is pre-ticked, violating consent requirements",
        current_impl="<input type='checkbox' checked name='marketing'>",
        compliant_impl="<input type='checkbox' name='marketing'> (unchecked by default)"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"GDPR Article: {finding.gdpr_article}")
    print(f"Fine Risk: {finding.fine_risk}")
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
    config = create_enhanced_gdpr_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
