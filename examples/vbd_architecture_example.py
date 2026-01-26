#!/usr/bin/env python3
"""
VBD Architecture Example - Complete E-Commerce Order System.

Demonstrates Volatility-Based Decomposition with:
- DTOs (Data structures)
- Interfaces (Contracts)
- Engines (Business logic)
- Managers (Orchestration)
- Adapters (External systems)
"""

# ============================================================================
# DTOs - Data Transfer Objects (Structural Volatility)
# ============================================================================

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class CreateOrderDTO(BaseModel):
    """Input for order creation."""
    customer_id: str = Field(..., description="Customer identifier")
    items: List[dict] = Field(..., min_items=1, description="Order items")
    shipping_address: str = Field(..., min_length=10)
    discount_code: Optional[str] = None

    @validator("items")
    def validate_items(cls, v):
        """Validate order items structure."""
        for item in v:
            if "product_id" not in item or "quantity" not in item:
                raise ValueError("Each item must have product_id and quantity")
            if item["quantity"] <= 0:
                raise ValueError("Quantity must be positive")
        return v


class OrderResponseDTO(BaseModel):
    """Output for order queries."""
    id: str
    customer_id: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    status: OrderStatus
    created_at: datetime


class PricingResultDTO(BaseModel):
    """Output from pricing engine."""
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    shipping: Decimal
    total: Decimal


# ============================================================================
# Interfaces - Contracts (Low Volatility)
# ============================================================================

from abc import ABC, abstractmethod


class IRepository(ABC):
    """Repository contract for data persistence."""

    @abstractmethod
    async def create(self, data: dict) -> dict:
        """Create resource."""
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get resource by ID."""
        pass

    @abstractmethod
    async def update(self, id: str, data: dict) -> dict:
        """Update resource."""
        pass


class IPaymentGateway(ABC):
    """Payment gateway contract."""

    @abstractmethod
    async def authorize(self, amount: Decimal, payment_method: str) -> dict:
        """Authorize payment."""
        pass

    @abstractmethod
    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        pass


class IInventoryService(ABC):
    """Inventory service contract."""

    @abstractmethod
    async def reserve(self, product_id: str, quantity: int) -> bool:
        """Reserve inventory."""
        pass

    @abstractmethod
    async def release(self, product_id: str, quantity: int) -> bool:
        """Release reserved inventory."""
        pass


class INotificationService(ABC):
    """Notification service contract."""

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email notification."""
        pass


# ============================================================================
# Engines - Core Business Logic (Lowest Volatility)
# ============================================================================

class PricingEngine:
    """
    Core pricing and discount logic.

    Volatility: LOW - Business rules rarely change
    Dependencies: DTOs only
    Testing: Pure unit tests (no mocks)
    """

    TAX_RATE = Decimal("0.08")  # 8% tax
    SHIPPING_BASE = Decimal("5.00")
    SHIPPING_FREE_THRESHOLD = Decimal("100.00")

    def calculate_order_pricing(
        self,
        items: List[dict],
        discount_code: Optional[str] = None
    ) -> PricingResultDTO:
        """
        Calculate order pricing with discounts and tax.

        Pure function - deterministic, no side effects.

        Args:
            items: List of order items with product_id, quantity, price
            discount_code: Optional discount code

        Returns:
            Complete pricing breakdown
        """
        # Calculate subtotal
        subtotal = sum(
            Decimal(str(item["price"])) * item["quantity"]
            for item in items
        )

        # Calculate discount
        discount = self._calculate_discount(subtotal, discount_code)

        # Calculate tax (after discount)
        taxable_amount = subtotal - discount
        tax = (taxable_amount * self.TAX_RATE).quantize(Decimal("0.01"))

        # Calculate shipping
        shipping = self._calculate_shipping(subtotal)

        # Calculate total
        total = subtotal - discount + tax + shipping

        return PricingResultDTO(
            subtotal=subtotal,
            tax=tax,
            discount=discount,
            shipping=shipping,
            total=total
        )

    def _calculate_discount(
        self,
        subtotal: Decimal,
        discount_code: Optional[str]
    ) -> Decimal:
        """
        Apply discount based on code.

        Business Rule: Discount codes
        - "SAVE10": 10% off
        - "SAVE20": 20% off
        - "FREESHIP": No discount (handled in shipping)
        """
        if not discount_code:
            return Decimal("0.00")

        discount_code = discount_code.upper()

        if discount_code == "SAVE10":
            return (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
        elif discount_code == "SAVE20":
            return (subtotal * Decimal("0.20")).quantize(Decimal("0.01"))
        elif discount_code == "FREESHIP":
            return Decimal("0.00")  # Handled in shipping calculation
        else:
            return Decimal("0.00")  # Invalid code = no discount

    def _calculate_shipping(self, subtotal: Decimal) -> Decimal:
        """
        Calculate shipping cost.

        Business Rule: Free shipping over $100
        """
        if subtotal >= self.SHIPPING_FREE_THRESHOLD:
            return Decimal("0.00")
        return self.SHIPPING_BASE


class OrderValidationEngine:
    """
    Order validation business rules.

    Volatility: LOW - Core validation rules are stable
    """

    MAX_ITEMS_PER_ORDER = 50
    MAX_QUANTITY_PER_ITEM = 999

    def validate_order(self, dto: CreateOrderDTO) -> tuple[bool, Optional[str]]:
        """
        Validate order against business rules.

        Args:
            dto: Order creation DTO

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Rule: Maximum items per order
        if len(dto.items) > self.MAX_ITEMS_PER_ORDER:
            return False, f"Maximum {self.MAX_ITEMS_PER_ORDER} items per order"

        # Rule: Maximum quantity per item
        for item in dto.items:
            if item["quantity"] > self.MAX_QUANTITY_PER_ITEM:
                return False, f"Maximum quantity per item is {self.MAX_QUANTITY_PER_ITEM}"

        # Rule: Valid shipping address (simplified)
        if len(dto.shipping_address) < 10:
            return False, "Shipping address too short"

        return True, None


# ============================================================================
# Managers - Workflow Orchestration (Medium Volatility)
# ============================================================================

class OrderManager:
    """
    Orchestrates order creation workflow.

    Volatility: MEDIUM - Workflow steps may evolve
    Dependencies: Engines, Adapters (via interfaces), DTOs
    Testing: Integration tests (mock adapters)
    """

    def __init__(
        self,
        pricing_engine: PricingEngine,
        validation_engine: OrderValidationEngine,
        repository: IRepository,
        payment_gateway: IPaymentGateway,
        inventory_service: IInventoryService,
        notification_service: INotificationService
    ):
        """Initialize with dependencies."""
        self.pricing_engine = pricing_engine
        self.validation_engine = validation_engine
        self.repository = repository
        self.payment_gateway = payment_gateway
        self.inventory_service = inventory_service
        self.notification_service = notification_service

    async def create_order(
        self,
        dto: CreateOrderDTO,
        payment_method: str
    ) -> OrderResponseDTO:
        """
        Orchestrate complete order creation workflow.

        Workflow:
        1. Validate order (validation engine)
        2. Calculate pricing (pricing engine)
        3. Reserve inventory (inventory adapter)
        4. Authorize payment (payment adapter)
        5. Create order (repository)
        6. Capture payment (payment adapter)
        7. Send confirmation (notification adapter)

        Args:
            dto: Order creation request
            payment_method: Payment method identifier

        Returns:
            Created order response

        Raises:
            ValueError: If validation fails
            RuntimeError: If any step fails
        """
        # Step 1: Validate order
        is_valid, error = self.validation_engine.validate_order(dto)
        if not is_valid:
            raise ValueError(f"Order validation failed: {error}")

        # Step 2: Calculate pricing
        pricing = self.pricing_engine.calculate_order_pricing(
            dto.items,
            dto.discount_code
        )

        # Step 3: Reserve inventory
        try:
            for item in dto.items:
                reserved = await self.inventory_service.reserve(
                    item["product_id"],
                    item["quantity"]
                )
                if not reserved:
                    raise RuntimeError(f"Inventory unavailable for {item['product_id']}")
        except Exception as e:
            # Rollback reservations
            await self._rollback_inventory(dto.items)
            raise RuntimeError(f"Inventory reservation failed: {e}")

        # Step 4: Authorize payment
        try:
            payment_auth = await self.payment_gateway.authorize(
                pricing.total,
                payment_method
            )
        except Exception as e:
            # Rollback inventory
            await self._rollback_inventory(dto.items)
            raise RuntimeError(f"Payment authorization failed: {e}")

        # Step 5: Create order in database
        try:
            order_data = {
                "customer_id": dto.customer_id,
                "items": dto.items,
                "subtotal": float(pricing.subtotal),
                "tax": float(pricing.tax),
                "discount": float(pricing.discount),
                "shipping": float(pricing.shipping),
                "total": float(pricing.total),
                "status": OrderStatus.CONFIRMED.value,
                "payment_transaction_id": payment_auth["transaction_id"],
            }

            order = await self.repository.create(order_data)

        except Exception as e:
            # Rollback inventory and payment
            await self._rollback_inventory(dto.items)
            # Note: Payment authorization will auto-expire
            raise RuntimeError(f"Order creation failed: {e}")

        # Step 6: Capture payment
        try:
            await self.payment_gateway.capture(payment_auth["transaction_id"])
        except Exception as e:
            # Payment capture failed but order exists
            # Mark order for manual review
            await self.repository.update(
                order["id"],
                {"status": "payment_pending", "notes": f"Capture failed: {e}"}
            )
            raise RuntimeError(f"Payment capture failed: {e}")

        # Step 7: Send confirmation email (fire-and-forget)
        try:
            await self._send_order_confirmation(dto.customer_id, order["id"])
        except Exception:
            # Don't fail order if notification fails
            pass

        # Return response
        return OrderResponseDTO(
            id=order["id"],
            customer_id=order["customer_id"],
            total_amount=Decimal(str(order["total"])),
            discount_amount=Decimal(str(order["discount"])),
            final_amount=Decimal(str(order["total"])),
            status=OrderStatus(order["status"]),
            created_at=datetime.fromisoformat(order["created_at"])
        )

    async def _rollback_inventory(self, items: List[dict]):
        """Rollback inventory reservations."""
        for item in items:
            try:
                await self.inventory_service.release(
                    item["product_id"],
                    item["quantity"]
                )
            except Exception:
                # Log error but continue rollback
                pass

    async def _send_order_confirmation(self, customer_id: str, order_id: str):
        """Send order confirmation email."""
        # In real app, fetch customer email from customer service
        customer_email = f"customer-{customer_id}@example.com"

        await self.notification_service.send_email(
            to=customer_email,
            subject=f"Order Confirmation - {order_id}",
            body=f"Your order {order_id} has been confirmed!"
        )


# ============================================================================
# Adapters - External Integrations (High Volatility)
# ============================================================================

class PostgresOrderRepository(IRepository):
    """
    PostgreSQL adapter for order persistence.

    Volatility: HIGH - Database schema changes, migrations
    """

    def __init__(self, db_connection_string: str):
        """Initialize with database connection."""
        self.connection_string = db_connection_string
        # In real app, initialize asyncpg pool

    async def create(self, data: dict) -> dict:
        """Create order in PostgreSQL."""
        # Simulate database insert
        import uuid
        from datetime import datetime

        data["id"] = str(uuid.uuid4())
        data["created_at"] = datetime.utcnow().isoformat()

        # In real app: INSERT INTO orders ...
        print(f"📝 Database: Created order {data['id']}")

        return data

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get order by ID."""
        # In real app: SELECT * FROM orders WHERE id = ?
        print(f"📖 Database: Fetched order {id}")
        return {"id": id, "status": "confirmed"}

    async def update(self, id: str, data: dict) -> dict:
        """Update order."""
        # In real app: UPDATE orders SET ... WHERE id = ?
        print(f"✏️  Database: Updated order {id}")
        return {**data, "id": id}


class StripePaymentAdapter(IPaymentGateway):
    """
    Stripe payment gateway adapter.

    Volatility: HIGH - Stripe API changes
    """

    def __init__(self, api_key: str):
        """Initialize Stripe client."""
        self.api_key = api_key

    async def authorize(self, amount: Decimal, payment_method: str) -> dict:
        """Authorize payment via Stripe."""
        # In real app: stripe.PaymentIntent.create(...)
        print(f"💳 Stripe: Authorized ${amount} on {payment_method}")

        return {
            "transaction_id": "pi_test_123456",
            "status": "authorized",
            "amount": float(amount)
        }

    async def capture(self, transaction_id: str) -> dict:
        """Capture authorized payment."""
        # In real app: stripe.PaymentIntent.capture(transaction_id)
        print(f"💰 Stripe: Captured payment {transaction_id}")

        return {
            "transaction_id": transaction_id,
            "status": "captured"
        }


class RESTInventoryAdapter(IInventoryService):
    """
    REST API adapter for inventory service.

    Volatility: HIGH - External API changes
    """

    def __init__(self, api_url: str, api_key: str):
        """Initialize inventory API client."""
        self.api_url = api_url
        self.api_key = api_key

    async def reserve(self, product_id: str, quantity: int) -> bool:
        """Reserve inventory via REST API."""
        # In real app: POST /inventory/reserve
        print(f"📦 Inventory: Reserved {quantity}x {product_id}")
        return True

    async def release(self, product_id: str, quantity: int) -> bool:
        """Release inventory reservation."""
        # In real app: POST /inventory/release
        print(f"↩️  Inventory: Released {quantity}x {product_id}")
        return True


class SendGridNotificationAdapter(INotificationService):
    """
    SendGrid email adapter.

    Volatility: HIGH - Email provider changes
    """

    def __init__(self, api_key: str):
        """Initialize SendGrid client."""
        self.api_key = api_key

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SendGrid."""
        # In real app: sendgrid.send(...)
        print(f"📧 Email: Sent to {to} - {subject}")
        return True


# ============================================================================
# Demonstration
# ============================================================================

async def main():
    """Demonstrate VBD architecture."""
    print("\n" + "="*60)
    print("VBD Architecture Example - Order System")
    print("="*60)

    # Initialize Engines (Low volatility - stable business logic)
    pricing_engine = PricingEngine()
    validation_engine = OrderValidationEngine()

    # Initialize Adapters (High volatility - external systems)
    repository = PostgresOrderRepository("postgresql://localhost/orders")
    payment_gateway = StripePaymentAdapter("sk_test_...")
    inventory_service = RESTInventoryAdapter("https://inventory.api", "api_key")
    notification_service = SendGridNotificationAdapter("SG.api_key")

    # Initialize Manager (Medium volatility - orchestration)
    order_manager = OrderManager(
        pricing_engine=pricing_engine,
        validation_engine=validation_engine,
        repository=repository,
        payment_gateway=payment_gateway,
        inventory_service=inventory_service,
        notification_service=notification_service
    )

    # Create order
    print("\n📝 Creating order...\n")

    order_dto = CreateOrderDTO(
        customer_id="cust_123",
        items=[
            {"product_id": "prod_1", "quantity": 2, "price": "29.99"},
            {"product_id": "prod_2", "quantity": 1, "price": "49.99"},
        ],
        shipping_address="123 Main St, City, State 12345",
        discount_code="SAVE10"
    )

    try:
        result = await order_manager.create_order(
            dto=order_dto,
            payment_method="pm_card_visa"
        )

        print("\n✅ Order created successfully!")
        print(f"   Order ID: {result.id}")
        print(f"   Total: ${result.final_amount}")
        print(f"   Status: {result.status}")

    except Exception as e:
        print(f"\n❌ Order failed: {e}")

    print("\n" + "="*60)
    print("VBD Layers Demonstrated:")
    print("="*60)
    print("✅ DTOs - Data structures (CreateOrderDTO, OrderResponseDTO)")
    print("✅ Interfaces - Contracts (IRepository, IPaymentGateway, etc.)")
    print("✅ Engines - Business logic (PricingEngine, ValidationEngine)")
    print("✅ Managers - Orchestration (OrderManager)")
    print("✅ Adapters - External systems (Postgres, Stripe, SendGrid)")
    print("\n📊 Volatility Levels:")
    print("   LOW:    Engines, Interfaces (stable)")
    print("   MEDIUM: Managers, DTOs (moderate change)")
    print("   HIGH:   Adapters (frequent changes)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
