# How to Define Factory Parameters

The Genesis Engine accepts parameters at multiple levels. Here's everything you can customize:

## 1. Simple Domain Description (Easiest)

Just describe your business domain in natural language:

```python
from genesis import GenesisEngine, run_genesis

engine = GenesisEngine.from_env()

# Create factory with domain description
factory = await engine.create_factory(
    tenant_id="my_company",
    domain_description="""
    E-commerce platform for handmade artisan goods.
    - Supports multi-vendor marketplace
    - Integrates with Stripe and PayPal
    - Must handle inventory across multiple warehouses
    - Needs fraud detection for high-value transactions
    - Complies with PCI-DSS for payment processing
    """,
    display_name="Artisan Market Inc.",
    contact_email="admin@artisanmarket.com"
)
```

### What Genesis Extracts

From your description, Genesis automatically determines:
- **Domain vocabulary** ("vendor", "inventory", "warehouse")
- **Standards** (PCI-DSS)
- **Tech stack** (payment APIs, fraud detection)
- **Constraints** (multi-vendor, fraud prevention)

## 2. FactoryBlueprint Structure (Advanced)

For full control, create a `FactoryBlueprint` directly:

```python
from genesis.genesis_agent import FactoryBlueprint, TechStackRecommendation, AgentPromptSpec

blueprint = FactoryBlueprint(
    factory_name="restaurant_factory",
    domain_name="restaurant_management",

    # Domain Context
    mission_statement="Builds restaurant reservation and table management systems",
    vocabulary={
        "terms": {
            "cover": "One dining seat at a table",
            "turn": "Complete dining cycle (seated → finished)",
            "86'd": "Menu item no longer available",
            "deuce": "Table for two guests"
        }
    },
    standards=[
        "PCI-DSS for payment processing",
        "ADA compliance for accessibility",
        "Local health code data retention"
    ],
    constraints=[
        "Tables cannot be double-booked",
        "Reservation window: 30 days advance max",
        "Minimum party size: 1, Maximum: 20"
    ],

    # Tech Stack
    tech_stack=TechStackRecommendation(
        language="Python 3.10+",
        framework="FastAPI",
        database="PostgreSQL",
        orm="SQLModel",
        testing="pytest",
        additional=["Redis for rate limiting", "Celery for async tasks"],
        rationale="FastAPI for async performance, PostgreSQL for ACID compliance"
    ),

    # Agent Configurations
    architect_spec=AgentPromptSpec(
        agent_name="architect",
        model="anthropic:claude-sonnet-4-5",
        system_prompt="""
        You design restaurant management features.

        Critical Rules:
        - All reservations must include party size and duration estimate
        - Table assignments must respect accessibility requirements
        - Never allow overbooking (enforce DB constraints)
        - All times in local restaurant timezone

        Output implementation plans with:
        - Database schema changes
        - API endpoints
        - Business logic rules
        - Edge cases handled
        """,
        tools_needed=["search_docs", "read_code", "list_files"]
    ),

    builder_spec=AgentPromptSpec(
        agent_name="builder",
        model="anthropic:claude-sonnet-4-5",
        system_prompt="""
        You implement restaurant features in production-quality Python.

        Code Standards:
        - Use Pydantic for all data validation
        - SQLModel for database models
        - Type hints required everywhere
        - Docstrings for all public functions

        Restaurant Domain Rules:
        - Party size: Integer 1-20
        - Reservation time: datetime with timezone
        - Table status: Enum(available, occupied, reserved, cleaning)
        - Payment status: Enum(pending, authorized, captured, refunded)
        """,
        tools_needed=["write_code", "read_code", "run_linter"]
    ),

    qa_spec=AgentPromptSpec(
        agent_name="qa",
        model="anthropic:claude-sonnet-4-5",
        system_prompt="""
        Test restaurant features thoroughly.

        Test Coverage Required:
        - Overbooking scenarios
        - Timezone edge cases
        - Concurrent reservation attempts
        - Payment failure handling
        - Table status transitions
        """,
        tools_needed=["run_tests", "check_coverage"]
    ),

    # Knowledge Base
    knowledge_seed={
        "queries": [
            "restaurant reservation system best practices",
            "table management algorithms",
            "OpenTable API documentation",
            "PCI-DSS payment compliance restaurant",
            "restaurant POS integration patterns"
        ],
        "sources": [
            "https://stripe.com/docs/payments",
            "https://developer.opentable.com",
            "https://www.pcisecuritystandards.org"
        ]
    },

    # Code Examples
    example_models='''
from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime

class TableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"

class Table(SQLModel, table=True):
    """Restaurant table."""
    id: int = Field(primary_key=True)
    number: str = Field(index=True)
    capacity: int = Field(ge=1, le=20)
    status: TableStatus = Field(default=TableStatus.AVAILABLE)
    section: str  # "patio", "main", "bar"
    is_accessible: bool = Field(default=False)

class Reservation(SQLModel, table=True):
    """Customer reservation."""
    id: int = Field(primary_key=True)
    customer_name: str
    customer_phone: str
    party_size: int = Field(ge=1, le=20)
    reservation_time: datetime
    duration_minutes: int = Field(default=90)
    table_id: int | None = Field(foreign_key="table.id")
    status: str  # pending, confirmed, seated, completed, cancelled
    ''',

    example_service='''
from datetime import datetime, timedelta

class ReservationService:
    """Business logic for reservations."""

    def __init__(self, db: Session):
        self.db = db

    def create_reservation(
        self,
        customer_name: str,
        party_size: int,
        time: datetime
    ) -> Reservation:
        """Create reservation with validation."""

        # Business rule: No reservations > 30 days out
        if time > datetime.now() + timedelta(days=30):
            raise ValueError("Cannot book more than 30 days in advance")

        # Find available table
        table = self.find_available_table(party_size, time)
        if not table:
            raise NoTablesAvailable("No tables for party of {party_size}")

        # Create reservation
        reservation = Reservation(
            customer_name=customer_name,
            party_size=party_size,
            reservation_time=time,
            table_id=table.id,
            status="confirmed"
        )

        self.db.add(reservation)
        self.db.commit()
        return reservation
    ''',

    example_api='''
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationResponse)
async def create_reservation(
    data: ReservationCreate,
    service: ReservationService = Depends(get_reservation_service)
):
    """Create a new reservation."""
    try:
        reservation = service.create_reservation(
            customer_name=data.customer_name,
            party_size=data.party_size,
            time=data.reservation_time
        )
        return reservation
    except NoTablesAvailable as e:
        raise HTTPException(status_code=409, detail=str(e))
    ''',

    example_test='''
import pytest
from datetime import datetime, timedelta

def test_create_reservation_success(service):
    """Test successful reservation creation."""
    time = datetime.now() + timedelta(days=1, hours=19)

    reservation = service.create_reservation(
        customer_name="John Doe",
        party_size=4,
        time=time
    )

    assert reservation.status == "confirmed"
    assert reservation.table_id is not None

def test_cannot_book_too_far_ahead(service):
    """Test 30-day advance booking limit."""
    time = datetime.now() + timedelta(days=31)

    with pytest.raises(ValueError, match="30 days"):
        service.create_reservation(
            customer_name="Jane",
            party_size=2,
            time=time
        )
    '''
)

# Create factory from blueprint
factory = await engine.create_factory_from_blueprint(
    tenant_id="fine_dining_corp",
    blueprint=blueprint
)
```

## 3. Key Parameters Explained

### Tenant Configuration

```python
factory = await engine.create_factory(
    # Identity
    tenant_id="unique_id",              # Unique identifier
    display_name="Company Name",        # Human-readable name
    contact_email="admin@company.com",  # Contact for escalations

    # Domain
    domain_description="...",           # What you're building

    # Optional overrides
    workspace_path="./custom/workspace", # Where to generate code
    use_dagger=True,                    # Use containerized builds
    max_iterations=5                    # Self-healing attempts
)
```

### Domain Description Best Practices

**Good Description:**
```
Inventory management system for automotive parts distributors.
- Tracks parts across 50+ warehouse locations
- Integrates with suppliers via EDI X12 850/855/856
- Supports just-in-time (JIT) replenishment
- Must handle hazardous material tracking per DOT regulations
- Real-time inventory sync with e-commerce platform
- Barcode and RFID scanning support
```

**Why it's good:**
- ✅ Specific domain (automotive parts)
- ✅ Mentions standards (EDI X12, DOT)
- ✅ Technical requirements (EDI, RFID)
- ✅ Business rules (JIT, hazmat tracking)
- ✅ Integrations (suppliers, e-commerce)

**Weak Description:**
```
Build an inventory system.
```

**Why it's weak:**
- ❌ Too generic
- ❌ No standards mentioned
- ❌ Missing constraints
- ❌ No integrations specified

### Tech Stack Customization

```python
tech_stack = TechStackRecommendation(
    language="Python 3.11+",           # Programming language
    framework="FastAPI",               # Web framework
    database="PostgreSQL",             # Primary database
    orm="SQLModel",                    # ORM layer
    testing="pytest + hypothesis",     # Testing tools

    additional=[
        "Redis for caching",
        "Celery for background jobs",
        "Alembic for migrations",
        "Pydantic for validation"
    ],

    rationale="""
    FastAPI chosen for async performance and automatic OpenAPI docs.
    PostgreSQL for ACID compliance and jsonb support.
    SQLModel combines Pydantic validation with SQLAlchemy ORM.
    """
)
```

### Agent Prompt Customization

```python
architect_spec = AgentPromptSpec(
    agent_name="architect",
    model="anthropic:claude-sonnet-4-5",  # or "openai:gpt-4o"

    system_prompt="""
    You are the Lead Architect for [DOMAIN].

    ## Your Mission
    Design [DOMAIN-SPECIFIC] features that are:
    - Compliant with [STANDARD_1], [STANDARD_2]
    - Type-safe using Pydantic
    - Secure ([SECURITY_REQUIREMENTS])
    - Complete (all edge cases covered)

    ## Critical Domain Rules
    1. [BUSINESS_RULE_1]
    2. [BUSINESS_RULE_2]
    3. [BUSINESS_RULE_3]

    ## Output Format
    Return ImplementationPlan with:
    - feature_name
    - [domain]_resources (e.g., fhir_resources for healthcare)
    - steps (ordered implementation)
    - api_endpoints
    - database_changes
    """,

    tools_needed=[
        "search_docs",      # Search domain documentation
        "read_code",        # Read existing code
        "list_files"        # Browse workspace
    ]
)
```

## 4. Environment Variables

Configure via `.env` file:

```bash
# Workspace
WORKSPACE_ROOT=./workspace
GENESIS_WORKSPACE=/tmp/genesis

# Execution
USE_DAGGER=true          # Containerized builds
MAX_ITERATIONS=5         # Self-healing attempts

# Services (optional)
MILVUS_URI=http://localhost:19530
KEYCLOAK_URL=http://localhost:8080
```

## 5. Programmatic Usage

```python
from genesis import GenesisEngine

# Initialize
engine = GenesisEngine.from_env()

# Method 1: Simple description
factory = await engine.create_factory(
    tenant_id="acme_corp",
    domain_description="SaaS billing platform with usage-based pricing"
)

# Method 2: Pre-built healthcare
factory = await engine.get_healthcare_factory(
    tenant_id="hospital_abc"
)

# Method 3: Custom blueprint
blueprint = await run_genesis("Your domain description")
factory = await engine.create_factory_from_blueprint(
    tenant_id="custom",
    blueprint=blueprint
)

# Build features
result = await factory.build_feature("Add invoice generation")
```

## 6. Quick Reference

| Parameter | Type | Where | Purpose |
|-----------|------|-------|---------|
| `tenant_id` | str | `create_factory()` | Unique identifier |
| `domain_description` | str | `create_factory()` | What to build |
| `display_name` | str | `create_factory()` | Company name |
| `contact_email` | str | `create_factory()` | Escalation contact |
| `workspace_path` | str | Optional | Code output location |
| `use_dagger` | bool | Optional | Containerized builds |
| `max_iterations` | int | Optional | Self-healing limit |
| `blueprint` | FactoryBlueprint | `create_factory_from_blueprint()` | Full config |

## 7. Examples by Industry

### Fintech
```python
domain = """
Payment processing platform for cross-border transactions.
- Supports 40+ currencies with real-time FX rates
- Complies with PSD2 Strong Customer Authentication
- Integrates with SWIFT for bank transfers
- Must handle PCI-DSS Level 1 compliance
- Anti-money laundering (AML) transaction monitoring
"""
```

### Healthcare
```python
domain = """
Electronic Health Records (EHR) system.
- HL7 FHIR R4 compliant
- HIPAA security and audit logging
- Integrates with HL7 v2 lab interfaces
- Supports SMART on FHIR apps
- ICD-10 and SNOMED CT coding
"""
```

### IoT
```python
domain = """
Industrial IoT monitoring for manufacturing plants.
- MQTT and OPC-UA device protocols
- Time-series data at 10ms resolution
- Predictive maintenance using ML models
- SCADA system integration
- ISO 27001 security requirements
"""
```

## Next Steps

1. **Start simple** with a domain description
2. **Let Genesis analyze** and create the blueprint
3. **Review generated prompts** in the workspace
4. **Customize if needed** by editing the blueprint
5. **Build features** with your new factory!

See [START_HERE.md](START_HERE.md) for running the demo.
