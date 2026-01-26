#!/usr/bin/env python3
"""
Example: Creating Custom Factories with Different Parameter Styles

This shows three ways to create factories:
1. Simple domain description (easiest)
2. Detailed domain description (recommended)
3. Full blueprint customization (advanced)
"""

import asyncio
from genesis import GenesisEngine, run_genesis
from genesis.genesis_agent import (
    FactoryBlueprint,
    TechStackRecommendation,
    AgentPromptSpec,
    DomainVocabulary,
    KnowledgeBaseSeed
)


async def example_1_simple():
    """Example 1: Simplest approach - just describe your domain."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Domain Description")
    print("="*60)

    engine = GenesisEngine.from_env()

    # Minimal parameters - Genesis figures out the rest
    factory = await engine.create_factory(
        tenant_id="bookstore_simple",
        domain_description="Online bookstore with inventory management"
    )

    print(f"✅ Created factory: {factory.config.domain_context.domain_name}")
    print(f"   Standards: {factory.config.domain_context.standards}")

    # Build a feature
    result = await factory.build_feature("Add book search by ISBN")
    print(f"   Result: {result['status']}")


async def example_2_detailed():
    """Example 2: Detailed description with specifics."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Detailed Domain Description")
    print("="*60)

    engine = GenesisEngine.from_env()

    domain_description = """
    Legal document management system for corporate law firms.

    ## Core Requirements
    - Stores contracts, pleadings, briefs, and correspondence
    - Version control with audit trail for all edits
    - Role-based access (partner, associate, paralegal, client)
    - Full-text search with OCR for scanned documents
    - Redaction tools for privileged information

    ## Integrations
    - Integrates with DocuSign for e-signatures
    - Connects to court e-filing systems (PACER, ECF)
    - Syncs with billing system for matter tracking

    ## Compliance
    - Must comply with ABA Model Rules of Professional Conduct
    - GDPR compliance for EU client data
    - SOC 2 Type II certification requirements
    - Attorney-client privilege protection

    ## Technical Requirements
    - Document retention policies (7+ years)
    - Encrypted storage for sensitive documents
    - Conflict of interest checks before new matters
    - Automatic deadline tracking and calendaring
    """

    factory = await engine.create_factory(
        tenant_id="lawfirm_detailed",
        domain_description=domain_description,
        display_name="Smith & Associates Law",
        contact_email="it@smithlaw.com"
    )

    print(f"✅ Created factory: {factory.config.domain_context.domain_name}")
    print(f"   Mission: {factory.config.domain_context.mission_statement[:80]}...")
    print(f"   Standards: {factory.config.domain_context.standards[:3]}")

    # Build features
    features = [
        "Add document upload with automatic OCR",
        "Add redaction tool for privileged information",
        "Add conflict check before creating new matter"
    ]

    for feature in features:
        print(f"\n   Building: {feature}")
        result = await factory.build_feature(feature)
        print(f"   Status: {result['status']}")


async def example_3_custom_blueprint():
    """Example 3: Full control with custom blueprint."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom Blueprint")
    print("="*60)

    engine = GenesisEngine.from_env()

    # Define complete blueprint manually
    blueprint = FactoryBlueprint(
        factory_name="ecommerce_jewelry_factory",
        domain_name="luxury_jewelry_ecommerce",

        # Domain context
        mission_statement="Builds e-commerce features for high-end jewelry sales",

        vocabulary=DomainVocabulary(terms={
            "carat": "Unit of weight for gemstones (1 carat = 200mg)",
            "clarity": "Gemstone quality grade (IF, VVS1, VVS2, VS1, VS2, SI1, SI2, I1, I2, I3)",
            "cut": "Diamond shape and facet arrangement (Round, Princess, Emerald, etc.)",
            "certificate": "Third-party gemstone grading report (GIA, AGS, IGI)",
            "appraisal": "Professional valuation document for insurance",
            "hallmark": "Official mark indicating metal purity (925 for sterling, 750 for 18k)"
        }),

        standards=[
            "Kimberley Process Certification (conflict-free diamonds)",
            "Responsible Jewelry Council Code of Practices",
            "PCI-DSS Level 1 for payment processing",
            "ISO 9001 for quality management"
        ],

        constraints=[
            "All diamonds >0.5ct must have GIA/AGS certificate",
            "High-value items (>$10k) require signature on delivery",
            "Cannot ship to countries under sanctions",
            "Insurance required for shipments >$5k",
            "Photos must show actual item (no stock photos for >$1k)"
        ],

        # Tech stack
        tech_stack=TechStackRecommendation(
            language="Python 3.11+",
            framework="FastAPI",
            database="PostgreSQL with PostGIS (for geographic restrictions)",
            orm="SQLModel",
            testing="pytest with Hypothesis for property testing",
            additional=[
                "Stripe for payment processing",
                "Cloudinary for high-res image management",
                "Twilio SendGrid for transactional emails",
                "Redis for cart session management",
                "Celery for background certificate verification"
            ],
            rationale="""
            FastAPI for async performance and OpenAPI docs.
            PostgreSQL + PostGIS for shipping restriction zones.
            Cloudinary handles high-res jewelry images with zoom.
            Stripe Connect for marketplace vendor payouts.
            """
        ),

        # Architect prompt
        architect_spec=AgentPromptSpec(
            agent_name="architect",
            model="anthropic:claude-sonnet-4-5",
            system_prompt="""
            You design luxury jewelry e-commerce features.

            ## Critical Business Rules

            1. **Gemstone Certification**
               - Diamonds >0.5ct MUST have GIA/AGS certificate
               - Certificate number must be verified against issuer database
               - Include certificate PDF in product listing

            2. **Pricing & Valuation**
               - Appraisal value stored separately from sale price
               - Insurance value = Appraisal value (not sale price)
               - Track metal spot prices for cost basis

            3. **Shipping & Insurance**
               - Orders >$5k require signature + insurance
               - No shipments to sanctioned countries
               - Track carrier and insurance policy per shipment

            4. **Product Authentication**
               - Each item has unique inventory ID
               - Photos of actual item (no stock photos for >$1k)
               - Maintain chain of custody documentation

            ## Output Requirements

            Design solutions that include:
            - Database schema for gemstone specifications
            - API endpoints for product CRUD
            - Integration points (Stripe, certificate APIs)
            - Business logic validation rules
            - Audit logging for high-value transactions
            """,
            tools_needed=["search_docs", "read_code", "list_files"]
        ),

        # Builder prompt
        builder_spec=AgentPromptSpec(
            agent_name="builder",
            model="anthropic:claude-sonnet-4-5",
            system_prompt="""
            You implement luxury jewelry features in production Python.

            ## Code Standards

            - All prices: Decimal (never float)
            - All weights in carats: Decimal with 2 decimals
            - Dates: timezone-aware datetime
            - Certificate numbers: String (alphanumeric)
            - Images: URLs to CDN (not stored in DB)

            ## Domain Models Required

            ```python
            class ClarityGrade(str, Enum):
                FL = "Flawless"
                IF = "Internally Flawless"
                VVS1 = "Very Very Slightly Included 1"
                # ... etc

            class DiamondSpec(SQLModel):
                carat_weight: Decimal
                clarity: ClarityGrade
                cut_grade: CutGrade
                color_grade: ColorGrade
                certificate_number: str
                certificate_issuer: CertIssuer  # GIA, AGS, IGI
            ```

            ## Validation Rules

            - Price validation: Must be positive, max 2 decimals
            - Weight validation: Must be positive, max 3 decimals
            - Certificate: Required for diamonds >0.5ct
            - Images: Minimum 3 photos, max 10 per item

            ## Security

            - Never log credit card numbers
            - Mask last 4 digits only in audit logs
            - Require 2FA for orders >$10k
            - Rate limit product search API
            """,
            tools_needed=["write_code", "read_code", "run_linter"]
        ),

        # QA prompt
        qa_spec=AgentPromptSpec(
            agent_name="qa",
            model="anthropic:claude-sonnet-4-5",
            system_prompt="""
            Test luxury jewelry features rigorously.

            ## Required Test Coverage

            1. **Pricing Edge Cases**
               - Decimal precision (no rounding errors)
               - Currency conversion accuracy
               - Discount calculation edge cases

            2. **Certificate Validation**
               - Invalid certificate numbers rejected
               - Certificate API timeout handling
               - Expired certificates flagged

            3. **Shipping Restrictions**
               - Sanctioned countries blocked
               - High-value signature requirements
               - Insurance calculation accuracy

            4. **Concurrent Inventory**
               - Race conditions on last item
               - Inventory reservation expiry
               - Double-booking prevention

            5. **Payment Security**
               - PCI compliance checks
               - Fraud detection integration
               - Chargeback handling
            """,
            tools_needed=["run_tests", "check_coverage"]
        ),

        # Knowledge base
        knowledge_seed=KnowledgeBaseSeed(
            queries=[
                "GIA diamond grading standards",
                "Kimberley Process certification requirements",
                "PCI-DSS compliance for jewelry e-commerce",
                "Stripe marketplace integration best practices",
                "Jewelry appraisal valuation methods",
                "Gemstone certification API documentation",
                "Luxury e-commerce shipping insurance",
                "Conflict-free diamond certification"
            ],
            sources=[
                "https://www.gia.edu/diamond-grading",
                "https://www.kimberleyprocess.com",
                "https://stripe.com/docs/connect",
                "https://www.pcisecuritystandards.org"
            ]
        ),

        # Code examples
        example_models="""
from sqlmodel import SQLModel, Field
from decimal import Decimal
from enum import Enum

class ClarityGrade(str, Enum):
    FL = "fl"
    IF = "if"
    VVS1 = "vvs1"
    VVS2 = "vvs2"

class Product(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    inventory_count: int = Field(ge=0)

class Diamond(SQLModel, table=True):
    id: int = Field(primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    carat_weight: Decimal = Field(max_digits=5, decimal_places=3)
    clarity: ClarityGrade
    certificate_number: str = Field(index=True)
    certificate_issuer: str  # GIA, AGS, IGI
        """,

        example_service="""
class ProductService:
    def validate_diamond(self, spec: DiamondSpec) -> bool:
        # Rule: Diamonds >0.5ct need certificate
        if spec.carat_weight > Decimal("0.5"):
            if not spec.certificate_number:
                raise ValueError("Certificate required for >0.5ct")

        # Verify certificate with GIA API
        is_valid = self.verify_certificate(
            spec.certificate_number,
            spec.certificate_issuer
        )

        return is_valid
        """,

        example_api="""
@router.post("/products", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends()
):
    # Validate diamond specs if applicable
    if data.diamond_spec:
        service.validate_diamond(data.diamond_spec)

    product = service.create_product(data)
    return product
        """,

        example_test="""
def test_diamond_requires_certificate_over_half_carat():
    spec = DiamondSpec(
        carat_weight=Decimal("0.6"),
        clarity=ClarityGrade.VVS1,
        certificate_number=None  # Missing!
    )

    with pytest.raises(ValueError, match="Certificate required"):
        service.validate_diamond(spec)
        """
    )

    # Create factory from custom blueprint
    factory = await engine.create_factory_from_blueprint(
        tenant_id="luxury_jewels",
        blueprint=blueprint,
        display_name="Tiffany & Co. (Example)",
        contact_email="dev@example.com"
    )

    print(f"✅ Created custom factory: {factory.config.domain_context.domain_name}")
    print(f"   Tech Stack: {factory.config.tech_stack.framework}")
    print(f"   Standards: {len(factory.config.domain_context.standards)} compliance requirements")

    # Build a feature
    result = await factory.build_feature(
        "Add diamond product listing with GIA certificate verification"
    )

    print(f"   Feature result: {result['status']}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("FACTORY PARAMETER EXAMPLES")
    print("="*60)

    # Choose which example to run
    print("\nSelect example:")
    print("1. Simple domain description")
    print("2. Detailed domain description")
    print("3. Custom blueprint (advanced)")
    print("4. Run all")

    choice = input("\nChoice (1-4): ").strip()

    if choice == "1":
        await example_1_simple()
    elif choice == "2":
        await example_2_detailed()
    elif choice == "3":
        await example_3_custom_blueprint()
    elif choice == "4":
        await example_1_simple()
        await example_2_detailed()
        await example_3_custom_blueprint()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
