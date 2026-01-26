# Volatility-Based Decomposition (VBD) Architecture

Complete guide to VBD architecture in the Genesis Engine.

## What is VBD?

**Volatility-Based Decomposition** organizes code by **rate of change** (volatility) rather than technical layers.

### Traditional Layered vs VBD

**Traditional Layered** (by technology):
```
Controllers → Services → Repositories → Models
```
Problem: Business logic scattered across layers, changes ripple everywhere.

**VBD** (by volatility):
```
DTOs (structure changes)
  ↓
Interfaces (stable contracts)
  ↓
Engines (rarely changes - core business rules)
  ↓
Managers (moderate changes - workflows)
  ↓
Adapters (frequent changes - external systems)
```
Benefit: Changes isolated to specific volatility zones.

## VBD Layers

### 1. DTOs - Data Transfer Objects

**Volatility**: Structural (changes with requirements)
**Purpose**: Data structures with validation
**Dependencies**: None (pure data)
**Testing**: Schema validation

```python
from pydantic import BaseModel, Field

class CreateOrderDTO(BaseModel):
    """Input for order creation."""
    customer_id: str = Field(..., description="Customer ID")
    items: List[dict] = Field(..., min_items=1)
    discount_code: Optional[str] = None

    @validator("items")
    def validate_items(cls, v):
        # Validate structure
        return v
```

**When to create**: Input/output contracts for operations
**Directory**: `app/dtos/`

---

### 2. Interfaces - Contracts

**Volatility**: LOW (stable contracts)
**Purpose**: Define contracts for adapters
**Dependencies**: DTOs only
**Testing**: N/A (no implementation)

```python
from abc import ABC, abstractmethod

class IPaymentGateway(ABC):
    """Contract for payment processing."""

    @abstractmethod
    async def authorize(self, amount: Decimal, method: str) -> dict:
        """Authorize payment."""
        pass

    @abstractmethod
    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        pass
```

**When to create**: When multiple adapters could implement same contract
**Directory**: `app/interfaces/`

---

### 3. Engines - Core Business Logic

**Volatility**: LOW (rarely changes)
**Purpose**: Pure business rules and calculations
**Dependencies**: DTOs, Interfaces (no adapters!)
**Testing**: Pure unit tests (no mocks)

```python
class PricingEngine:
    """
    Core pricing calculations.

    Pure functions - no side effects, no external calls.
    Same input → Same output.
    """

    TAX_RATE = Decimal("0.08")

    def calculate_total(
        self,
        items: List[dict],
        discount_code: Optional[str]
    ) -> PricingResultDTO:
        """
        Calculate order total with discounts and tax.

        Pure function - deterministic.
        """
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        discount = self._calculate_discount(subtotal, discount_code)
        tax = (subtotal - discount) * self.TAX_RATE
        total = subtotal - discount + tax

        return PricingResultDTO(
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total
        )

    def _calculate_discount(self, subtotal, code):
        """Apply discount based on code."""
        if code == "SAVE10":
            return subtotal * Decimal("0.10")
        return Decimal("0.00")
```

**Key characteristics**:
- ✅ Pure functions (deterministic)
- ✅ No external dependencies (no database, no API calls)
- ✅ Framework-agnostic
- ✅ Easy to test (no mocks needed)
- ✅ Business logic in ONE place

**When to create**: Core domain calculations, validation rules
**Directory**: `app/engines/`

**Examples**:
- `PricingEngine` - Calculate prices, discounts, taxes
- `ValidationEngine` - Business rule validation
- `CalculationEngine` - Complex domain math
- `RuleEngine` - Apply business rules
- `ScoringEngine` - Calculate scores/ratings

---

### 4. Managers - Orchestration

**Volatility**: MEDIUM (workflows evolve)
**Purpose**: Coordinate operations across engines and adapters
**Dependencies**: Engines, Adapters (via interfaces), DTOs
**Testing**: Integration tests (mock adapters)

```python
class OrderManager:
    """
    Orchestrates order creation workflow.

    Coordinates: Validation → Pricing → Inventory → Payment → Persistence
    """

    def __init__(
        self,
        pricing_engine: PricingEngine,
        validation_engine: ValidationEngine,
        repository: IRepository,
        payment_gateway: IPaymentGateway,
        inventory_service: IInventoryService
    ):
        """Inject dependencies."""
        self.pricing_engine = pricing_engine
        self.validation_engine = validation_engine
        self.repository = repository
        self.payment_gateway = payment_gateway
        self.inventory_service = inventory_service

    async def create_order(
        self,
        dto: CreateOrderDTO,
        payment_method: str
    ) -> OrderResponseDTO:
        """
        Orchestrate complete order creation.

        Workflow:
        1. Validate via engine
        2. Calculate pricing via engine
        3. Reserve inventory via adapter
        4. Authorize payment via adapter
        5. Persist via repository
        6. Capture payment via adapter
        7. Send notification via adapter
        """
        # Step 1: Validate (engine)
        is_valid, error = self.validation_engine.validate_order(dto)
        if not is_valid:
            raise ValueError(error)

        # Step 2: Calculate pricing (engine)
        pricing = self.pricing_engine.calculate_total(dto.items, dto.discount_code)

        # Step 3: Reserve inventory (adapter)
        for item in dto.items:
            reserved = await self.inventory_service.reserve(
                item["product_id"],
                item["quantity"]
            )
            if not reserved:
                raise RuntimeError("Inventory unavailable")

        # Step 4: Authorize payment (adapter)
        payment = await self.payment_gateway.authorize(pricing.total, payment_method)

        # Step 5: Persist order (repository adapter)
        order = await self.repository.create({
            "customer_id": dto.customer_id,
            "total": pricing.total,
            "payment_id": payment["transaction_id"],
        })

        # Step 6: Capture payment (adapter)
        await self.payment_gateway.capture(payment["transaction_id"])

        # Step 7: Map to response DTO
        return OrderResponseDTO(
            id=order["id"],
            total_amount=pricing.total,
            status="confirmed"
        )
```

**Key characteristics**:
- ✅ Orchestrates workflow steps
- ✅ Handles transactions
- ✅ Maps between DTOs and domain objects
- ✅ Coordinates multiple services
- ✅ Contains rollback logic

**When to create**: Multi-step workflows, resource lifecycle
**Directory**: `app/managers/`

**Examples**:
- `OrderManager` - Order lifecycle
- `UserManager` - User registration/activation
- `PaymentManager` - Payment workflows
- `ReportManager` - Report generation

---

### 5. Adapters - External Integration

**Volatility**: HIGH (external systems change frequently)
**Purpose**: Integrate with external systems
**Dependencies**: Interfaces, DTOs
**Testing**: Integration tests (real/test systems)

```python
class StripePaymentAdapter(IPaymentGateway):
    """
    Stripe payment gateway adapter.

    Implements IPaymentGateway interface.
    High volatility - Stripe API changes.
    """

    def __init__(self, api_key: str):
        """Initialize Stripe client."""
        self.api_key = api_key
        self._client = self._init_stripe()

    def _init_stripe(self):
        """Initialize Stripe SDK."""
        import stripe
        stripe.api_key = self.api_key
        return stripe

    async def authorize(self, amount: Decimal, method: str) -> dict:
        """Authorize payment via Stripe."""
        try:
            payment_intent = self._client.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency="usd",
                payment_method=method,
                capture_method="manual"  # Authorize only
            )

            return {
                "transaction_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": amount
            }

        except stripe.error.StripeError as e:
            raise RuntimeError(f"Stripe authorization failed: {e}")

    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        try:
            payment_intent = self._client.PaymentIntent.capture(transaction_id)

            return {
                "transaction_id": payment_intent.id,
                "status": payment_intent.status
            }

        except stripe.error.StripeError as e:
            raise RuntimeError(f"Stripe capture failed: {e}")
```

**Key characteristics**:
- ✅ Implements interface contract
- ✅ Handles external API specifics
- ✅ Maps external format ↔ internal DTOs
- ✅ Error handling for external failures
- ✅ Can be swapped (Stripe → PayPal)

**When to create**: Database access, external APIs, message queues
**Directory**: `app/adapters/`

**Examples**:
- `PostgresOrderRepository` - Database CRUD
- `StripePaymentAdapter` - Stripe API
- `SendGridEmailAdapter` - SendGrid API
- `RedisCache Adapter` - Redis operations
- `S3StorageAdapter` - AWS S3

---

## Directory Structure

```
app/
├── dtos/                          # Data Transfer Objects
│   ├── order_dto.py              # Order DTOs
│   ├── user_dto.py               # User DTOs
│   └── payment_dto.py            # Payment DTOs
│
├── interfaces/                    # Contracts
│   ├── i_repository.py           # Repository contract
│   ├── i_payment_gateway.py      # Payment contract
│   └── i_notification.py         # Notification contract
│
├── engines/                       # Core Business Logic (LOW volatility)
│   ├── pricing_engine.py         # Pricing calculations
│   ├── validation_engine.py      # Business rules
│   └── inventory_engine.py       # Inventory logic
│
├── managers/                      # Orchestration (MEDIUM volatility)
│   ├── order_manager.py          # Order workflows
│   ├── user_manager.py           # User workflows
│   └── payment_manager.py        # Payment workflows
│
├── adapters/                      # External Systems (HIGH volatility)
│   ├── database/
│   │   ├── postgres_repository.py
│   │   └── mongo_repository.py
│   ├── payment/
│   │   ├── stripe_adapter.py
│   │   └── paypal_adapter.py
│   ├── notification/
│   │   └── sendgrid_adapter.py
│   └── cache/
│       └── redis_adapter.py
│
└── api/                           # API Layer (uses Managers)
    ├── order_routes.py
    └── user_routes.py
```

## Dependency Rules

**Critical**: Dependencies flow in ONE direction (prevent cyclic deps)

```
DTOs ←─── Interfaces ←─── Engines ←─── Managers ←─── API
  ↑                         ↑           ↑
  └─────── Adapters ────────┴───────────┘
```

**Rules**:
1. ✅ DTOs depend on: Nothing
2. ✅ Interfaces depend on: DTOs only
3. ✅ Engines depend on: DTOs, Interfaces
4. ✅ Adapters depend on: DTOs, Interfaces
5. ✅ Managers depend on: DTOs, Interfaces, Engines, Adapters
6. ✅ API Layer depends on: DTOs, Managers

**Forbidden**:
- ❌ Engines depending on Adapters (breaks purity)
- ❌ Adapters depending on Managers (creates cycles)
- ❌ Managers depending on API Layer (wrong direction)

## Testing Strategy

### Engines - Pure Unit Tests
```python
def test_pricing_engine_calculate_discount():
    """Test pricing engine (no mocks needed)."""
    engine = PricingEngine()

    # Pure function test - deterministic
    result = engine.calculate_total(
        items=[{"price": 100, "quantity": 1}],
        discount_code="SAVE10"
    )

    assert result.subtotal == Decimal("100.00")
    assert result.discount == Decimal("10.00")
    assert result.total == Decimal("97.20")  # After tax
```

### Managers - Integration Tests (Mock Adapters)
```python
@pytest.fixture
def mock_payment_gateway():
    """Mock payment adapter."""
    gateway = Mock(spec=IPaymentGateway)
    gateway.authorize.return_value = {"transaction_id": "test_123"}
    gateway.capture.return_value = {"status": "captured"}
    return gateway

async def test_order_manager_create_order(mock_payment_gateway):
    """Test order manager workflow."""
    manager = OrderManager(
        pricing_engine=PricingEngine(),
        payment_gateway=mock_payment_gateway,
        # ... other mocked adapters
    )

    result = await manager.create_order(dto, "pm_card")

    assert result.status == "confirmed"
    mock_payment_gateway.authorize.assert_called_once()
    mock_payment_gateway.capture.assert_called_once()
```

### Adapters - Integration Tests (Real Systems)
```python
@pytest.mark.integration
async def test_stripe_adapter_authorize():
    """Test Stripe adapter with test API."""
    adapter = StripePaymentAdapter(api_key=TEST_STRIPE_KEY)

    result = await adapter.authorize(
        amount=Decimal("99.99"),
        method="pm_card_visa"
    )

    assert result["status"] == "requires_capture"
    assert "transaction_id" in result
```

## Benefits of VBD

### 1. Changes Isolated by Volatility
- **Stripe API changes?** → Only `StripePaymentAdapter` changes
- **New discount rule?** → Only `PricingEngine` changes
- **Workflow reordering?** → Only `OrderManager` changes

### 2. Easy Testing
- **Engines**: Pure unit tests (no mocks, fast)
- **Managers**: Integration tests (mock external systems)
- **Adapters**: Integration tests (real or test systems)

### 3. Framework Independence
- **Engines** are pure Python (no FastAPI, no SQLAlchemy)
- Can swap frameworks without changing business logic

### 4. Swappable Adapters
Multiple implementations of same interface:
```python
# Development
manager = OrderManager(
    payment_gateway=MockPaymentAdapter()  # No real charges
)

# Production
manager = OrderManager(
    payment_gateway=StripePaymentAdapter(api_key=...)
)

# Switch providers
manager = OrderManager(
    payment_gateway=PayPalPaymentAdapter(api_key=...)
)
```

### 5. Clear Boundaries
- **Engines**: Business rules (what)
- **Managers**: Workflows (how)
- **Adapters**: External systems (where)

## When to Use VBD

✅ **Use VBD when**:
- Complex business logic that changes independently of workflows
- Multiple external integrations
- Need to swap implementations (Stripe ↔ PayPal)
- High test coverage requirements
- Long-term maintenance expected

❌ **Skip VBD for**:
- Simple CRUD apps (traditional layered is fine)
- Rapid prototypes (overkill)
- Single developer for short project

## VBD in Genesis Engine

The Genesis Engine can generate VBD architecture:

```python
from genesis import GenesisEngine
from genesis.architecture_patterns import VBDArchitectureSpec

# Create factory with VBD architecture
engine = GenesisEngine.from_env()

factory = await engine.create_factory(
    tenant_id="ecommerce_store",
    domain_description="E-commerce platform with complex pricing",
    architecture=VBDArchitectureSpec()  # Use VBD pattern
)

# Build feature
result = await factory.build_feature(
    "Add discount codes with percentage and flat rate support"
)
```

Generated structure:
```
workspace/
└── app/
    ├── dtos/
    │   └── discount_dto.py          # CreateDiscountDTO, DiscountResponseDTO
    ├── interfaces/
    │   └── i_discount_repository.py # IDiscountRepository contract
    ├── engines/
    │   └── discount_engine.py       # Discount calculation logic
    ├── managers/
    │   └── discount_manager.py      # Discount lifecycle workflows
    ├── adapters/
    │   └── postgres_discount_adapter.py # PostgreSQL implementation
    └── api/
        └── discount_routes.py       # FastAPI endpoints
```

## Example: Run Full Demo

```bash
python3 examples/vbd_architecture_example.py
```

Output shows complete order workflow with all VBD layers:
```
📝 Creating order...

📝 Database: Created order abc123
💳 Stripe: Authorized $109.97 on pm_card_visa
📦 Inventory: Reserved 2x prod_1
📦 Inventory: Reserved 1x prod_2
💰 Stripe: Captured payment pi_test_123456
📧 Email: Sent to customer@example.com

✅ Order created successfully!
   Order ID: abc123
   Total: $109.97
   Status: confirmed
```

## Quick Reference

| Layer | Volatility | Dependencies | Testing | Examples |
|-------|-----------|--------------|---------|----------|
| **DTOs** | Structural | None | Schema validation | `CreateOrderDTO`, `OrderResponseDTO` |
| **Interfaces** | LOW | DTOs | N/A | `IPaymentGateway`, `IRepository` |
| **Engines** | LOW | DTOs, Interfaces | Pure unit tests | `PricingEngine`, `ValidationEngine` |
| **Managers** | MEDIUM | Engines, Adapters, DTOs | Integration (mock adapters) | `OrderManager`, `UserManager` |
| **Adapters** | HIGH | Interfaces, DTOs | Integration (real systems) | `StripeAdapter`, `PostgresRepository` |

## Next Steps

1. **Run example**: `python3 examples/vbd_architecture_example.py`
2. **Review templates**: See [genesis/architecture_patterns.py](genesis/architecture_patterns.py)
3. **Generate with VBD**: Use VBDArchitectureSpec in factory creation
4. **Read guide**: [Complete guide with all templates](ENV_AND_ASSISTANTS.md)

VBD keeps your business logic pure, workflows flexible, and external integrations isolated! 🚀
