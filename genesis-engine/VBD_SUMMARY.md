# VBD Architecture - Summary

Complete summary of Volatility-Based Decomposition (VBD) architecture added to Genesis Engine.

## What Was Added

### Core Module
**[genesis/architecture_patterns.py](genesis/architecture_patterns.py)** - 700+ lines

Defines VBD and other architectural patterns:
- `VBDArchitectureSpec` - Complete VBD specification
- `VBDCodeTemplates` - Templates for Engines, Managers, Adapters, DTOs, Interfaces
- `ArchitecturePattern` enum - VBD, Layered, Clean, Hexagonal, CQRS, Event-Driven

### Working Example
**[examples/vbd_architecture_example.py](examples/vbd_architecture_example.py)** - 600+ lines

Complete e-commerce order system demonstrating:
- ✅ **DTOs**: `CreateOrderDTO`, `OrderResponseDTO`, `PricingResultDTO`
- ✅ **Interfaces**: `IRepository`, `IPaymentGateway`, `IInventoryService`, `INotificationService`
- ✅ **Engines**: `PricingEngine`, `OrderValidationEngine`
- ✅ **Managers**: `OrderManager`
- ✅ **Adapters**: `PostgresOrderRepository`, `StripePaymentAdapter`, `RESTInventoryAdapter`, `SendGridNotificationAdapter`

### Documentation
**[VBD_ARCHITECTURE.md](VBD_ARCHITECTURE.md)** - Complete guide with:
- VBD principles and layers
- When to use each layer
- Code examples
- Testing strategies
- Directory structure
- Comparison to traditional architecture

## VBD Quick Reference

### The 5 Layers (by Volatility)

| Layer | Volatility | Purpose | Dependencies | Example |
|-------|-----------|---------|--------------|---------|
| **DTOs** | Structural | Data structures | None | `CreateOrderDTO`, `OrderResponseDTO` |
| **Interfaces** | LOW | Contracts | DTOs | `IPaymentGateway`, `IRepository` |
| **Engines** | LOW | Business rules | DTOs, Interfaces | `PricingEngine`, `ValidationEngine` |
| **Managers** | MEDIUM | Orchestration | Engines, Adapters, DTOs | `OrderManager`, `UserManager` |
| **Adapters** | HIGH | External systems | Interfaces, DTOs | `StripeAdapter`, `PostgresRepository` |

### Key Principles

1. **Engines are pure** - No side effects, no external calls
2. **Managers orchestrate** - Coordinate engines and adapters
3. **Adapters isolate** - External system changes don't ripple
4. **Interfaces enable** - Multiple implementations (Stripe ↔ PayPal)
5. **Dependencies flow** - One direction (prevent cycles)

## Run the Example

```bash
python3 examples/vbd_architecture_example.py
```

**Output**:
```
============================================================
VBD Architecture Example - Order System
============================================================

📝 Creating order...

📦 Inventory: Reserved 2x prod_1
📦 Inventory: Reserved 1x prod_2
💳 Stripe: Authorized $106.89 on pm_card_visa
📝 Database: Created order 5239e85f-0a17-42fe-b1a9-9f8c94df8e20
💰 Stripe: Captured payment pi_test_123456
📧 Email: Sent to customer@example.com

✅ Order created successfully!
   Order ID: 5239e85f-0a17-42fe-b1a9-9f8c94df8e20
   Total: $106.89
   Status: OrderStatus.CONFIRMED

============================================================
VBD Layers Demonstrated:
============================================================
✅ DTOs - Data structures (CreateOrderDTO, OrderResponseDTO)
✅ Interfaces - Contracts (IRepository, IPaymentGateway, etc.)
✅ Engines - Business logic (PricingEngine, ValidationEngine)
✅ Managers - Orchestration (OrderManager)
✅ Adapters - External systems (Postgres, Stripe, SendGrid)

📊 Volatility Levels:
   LOW:    Engines, Interfaces (stable)
   MEDIUM: Managers, DTOs (moderate change)
   HIGH:   Adapters (frequent changes)
```

## Code Templates Included

### 1. Engine Template
```python
class PricingEngine:
    """
    Core business logic - Pure functions.

    Volatility: LOW (rarely changes)
    Dependencies: DTOs only
    Testing: Pure unit tests (no mocks)
    """

    def calculate_total(self, items: List[dict], discount_code: str) -> PricingResultDTO:
        """Pure calculation - deterministic, no side effects."""
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        discount = self._apply_discount(subtotal, discount_code)
        tax = (subtotal - discount) * TAX_RATE
        return PricingResultDTO(total=subtotal - discount + tax)
```

### 2. Manager Template
```python
class OrderManager:
    """
    Workflow orchestration.

    Volatility: MEDIUM (workflows evolve)
    Dependencies: Engines, Adapters (via interfaces)
    Testing: Integration tests (mock adapters)
    """

    def __init__(
        self,
        pricing_engine: PricingEngine,
        repository: IRepository,
        payment_gateway: IPaymentGateway
    ):
        self.pricing_engine = pricing_engine
        self.repository = repository
        self.payment_gateway = payment_gateway

    async def create_order(self, dto: CreateOrderDTO) -> OrderResponseDTO:
        """
        Orchestrate: Validate → Price → Reserve → Pay → Persist
        """
        # Step 1: Calculate via engine
        pricing = self.pricing_engine.calculate_total(dto.items, dto.discount_code)

        # Step 2: Authorize payment via adapter
        payment = await self.payment_gateway.authorize(pricing.total, dto.payment_method)

        # Step 3: Persist via repository adapter
        order = await self.repository.create({"total": pricing.total, ...})

        # Step 4: Capture payment
        await self.payment_gateway.capture(payment["transaction_id"])

        return OrderResponseDTO(id=order["id"], total=pricing.total, ...)
```

### 3. Adapter Template
```python
class StripePaymentAdapter(IPaymentGateway):
    """
    External system integration.

    Volatility: HIGH (Stripe API changes)
    Dependencies: Interface contract, DTOs
    Testing: Integration tests (Stripe test API)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = stripe.Client(api_key=api_key)

    async def authorize(self, amount: Decimal, method: str) -> dict:
        """Authorize payment via Stripe API."""
        payment_intent = self._client.PaymentIntent.create(
            amount=int(amount * 100),
            currency="usd",
            payment_method=method,
            capture_method="manual"
        )
        return {"transaction_id": payment_intent.id}

    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        payment_intent = self._client.PaymentIntent.capture(transaction_id)
        return {"status": payment_intent.status}
```

### 4. Interface Template
```python
class IPaymentGateway(ABC):
    """
    Payment gateway contract.

    Volatility: LOW (stable contract)
    Implementations: StripeAdapter, PayPalAdapter, SquareAdapter
    """

    @abstractmethod
    async def authorize(self, amount: Decimal, method: str) -> dict:
        """Authorize payment."""
        pass

    @abstractmethod
    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        pass
```

### 5. DTO Template
```python
class CreateOrderDTO(BaseModel):
    """
    Input DTO for order creation.

    Volatility: Structural (changes with requirements)
    """

    customer_id: str = Field(..., description="Customer ID")
    items: List[dict] = Field(..., min_items=1)
    discount_code: Optional[str] = None

    @validator("items")
    def validate_items(cls, v):
        for item in v:
            if "product_id" not in item or "quantity" not in item:
                raise ValueError("Invalid item structure")
        return v
```

## Directory Structure

```
app/
├── dtos/                     # Data structures
│   ├── order_dto.py
│   ├── user_dto.py
│   └── payment_dto.py
│
├── interfaces/               # Contracts (LOW volatility)
│   ├── i_repository.py
│   ├── i_payment_gateway.py
│   └── i_notification.py
│
├── engines/                  # Business logic (LOW volatility)
│   ├── pricing_engine.py
│   ├── validation_engine.py
│   └── inventory_engine.py
│
├── managers/                 # Orchestration (MEDIUM volatility)
│   ├── order_manager.py
│   ├── user_manager.py
│   └── payment_manager.py
│
├── adapters/                 # External systems (HIGH volatility)
│   ├── database/
│   │   └── postgres_repository.py
│   ├── payment/
│   │   ├── stripe_adapter.py
│   │   └── paypal_adapter.py
│   └── notification/
│       └── sendgrid_adapter.py
│
└── api/                      # API Layer (uses Managers)
    ├── order_routes.py
    └── user_routes.py
```

## Benefits

### 1. Changes Isolated
- Stripe API changes? → Only `StripePaymentAdapter`
- New discount rule? → Only `PricingEngine`
- Workflow reordering? → Only `OrderManager`

### 2. Easy Testing
- **Engines**: Pure unit tests (fast, no mocks)
- **Managers**: Integration tests (mock adapters)
- **Adapters**: Integration tests (test APIs)

### 3. Swappable Implementations
```python
# Development
manager = OrderManager(payment_gateway=MockPaymentAdapter())

# Production with Stripe
manager = OrderManager(payment_gateway=StripePaymentAdapter(api_key=...))

# Switch to PayPal
manager = OrderManager(payment_gateway=PayPalPaymentAdapter(api_key=...))
```

### 4. Framework Independence
Engines are pure Python - no FastAPI, no SQLAlchemy, no framework coupling.

## Use in Genesis Engine

```python
from genesis import GenesisEngine
from genesis.architecture_patterns import VBDArchitectureSpec

# Create factory with VBD architecture
engine = GenesisEngine.from_env()

factory = await engine.create_factory(
    tenant_id="ecommerce_store",
    domain_description="E-commerce with complex pricing and inventory",
    architecture=VBDArchitectureSpec()  # ← Use VBD pattern
)

# Build feature
result = await factory.build_feature(
    "Add tiered discount system with quantity-based pricing"
)
```

**Generated structure**:
```
workspace/
└── app/
    ├── dtos/discount_dto.py           # DTOs
    ├── interfaces/i_discount_repo.py  # Interface
    ├── engines/discount_engine.py     # Pure business logic
    ├── managers/discount_manager.py   # Workflow orchestration
    ├── adapters/postgres_discount.py  # Database adapter
    └── api/discount_routes.py         # FastAPI routes
```

## When to Use VBD

✅ **Use VBD when**:
- Complex business rules that change independently
- Multiple external integrations
- Need to swap implementations
- High test coverage requirements
- Long-term project maintenance

❌ **Skip VBD for**:
- Simple CRUD apps
- Rapid prototypes
- Short-lived projects

## Comparison: Layered vs VBD

### Traditional Layered (by technology)
```
problem: Business logic scattered across layers

app/
├── controllers/      # API layer
├── services/         # Business logic mixed with orchestration
├── repositories/     # Data access
└── models/           # Domain models

Changes ripple across all layers
```

### VBD (by volatility)
```
solution: Business logic isolated in engines

app/
├── dtos/            # Structural changes
├── interfaces/      # Stable contracts
├── engines/         # Business logic (pure)
├── managers/        # Orchestration (moderate changes)
└── adapters/        # External systems (frequent changes)

Changes isolated to specific volatility zones
```

## Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| **genesis/architecture_patterns.py** | 700+ | VBD specification and code templates |
| **examples/vbd_architecture_example.py** | 600+ | Complete working order system |
| **VBD_ARCHITECTURE.md** | 600+ | Complete guide and documentation |
| **VBD_SUMMARY.md** | This file | Quick reference |

## Next Steps

1. **Run the example**:
   ```bash
   python3 examples/vbd_architecture_example.py
   ```

2. **Read the guide**: [VBD_ARCHITECTURE.md](VBD_ARCHITECTURE.md)

3. **Use in factories**:
   ```python
   from genesis.architecture_patterns import VBDArchitectureSpec
   factory = await engine.create_factory(..., architecture=VBDArchitectureSpec())
   ```

4. **Review templates**: See [genesis/architecture_patterns.py](genesis/architecture_patterns.py)

## Quick Decision Guide

**Do I need VBD?**

Ask yourself:
- 🤔 Complex business rules that change independently? → **Yes, use VBD**
- 🤔 Multiple external integrations (Stripe, Plaid, SendGrid)? → **Yes, use VBD**
- 🤔 Need to swap implementations (Stripe ↔ PayPal)? → **Yes, use VBD**
- 🤔 Simple CRUD app with basic validation? → **No, traditional layered is fine**
- 🤔 Rapid prototype or short-term project? → **No, VBD is overkill**

Your Genesis Engine now supports VBD architecture for production-grade systems! 🚀
