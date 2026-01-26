"""
Enhanced Microservices Architect Assistant

Comprehensive microservices architecture covering:
- Domain-Driven Design (bounded contexts, aggregates, entities)
- Service mesh patterns (Istio, Linkerd)
- Circuit breaker configuration (Hystrix, resilience4j)
- Saga patterns (orchestration vs choreography)
- Distributed tracing (OpenTelemetry, Jaeger)
- Service discovery (Consul, etcd)
- API gateway patterns
- Event-driven communication

References:
- Domain-Driven Design (Eric Evans)
- Building Microservices (Sam Newman)
- Microservices Patterns (Chris Richardson)
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class MicroservicesFinding(BaseModel):
    """Structured microservices finding output"""

    finding_id: str = Field(..., description="Unique identifier (MS-001, MS-002, etc.)")
    title: str = Field(..., description="Brief title of the architecture issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="DDD/Resilience/Communication/Discovery")

    location: Dict[str, Any] = Field(default_factory=dict, description="Service, component")
    description: str = Field(..., description="Detailed description of the issue")

    pattern_violated: Optional[str] = Field(default=None, description="Which pattern violated")
    current_design: str = Field(default="", description="Current architecture")
    improved_design: str = Field(default="", description="Improved architecture")

    implementation: str = Field(default="", description="How to implement the fix")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Tools to use")

    remediation: Dict[str, str] = Field(default_factory=dict, description="Effort and priority")


class EnhancedMicroservicesAssistant:
    """Enhanced Microservices Architect with comprehensive DDD and resilience patterns"""

    def __init__(self):
        self.name = "Enhanced Microservices Architect"
        self.version = "2.0.0"
        self.standards = ["DDD", "12-Factor App", "CQRS", "Event Sourcing"]

    # =========================================================================
    # DOMAIN-DRIVEN DESIGN
    # =========================================================================

    @staticmethod
    def ddd_patterns() -> Dict[str, Any]:
        """Domain-Driven Design patterns"""
        return {
            "bounded_context": {
                "description": "Explicit boundary within which a domain model applies",
                "identification": """
# How to identify bounded contexts:
# 1. Look for different meanings of same term
#    - "Account" in Banking vs "Account" in User Management
# 2. Look for natural team boundaries
# 3. Look for different business capabilities

# Example: E-commerce bounded contexts
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Catalog       │  │   Orders        │  │   Shipping      │
│                 │  │                 │  │                 │
│ Product         │  │ Order           │  │ Shipment        │
│ Category        │  │ OrderItem       │  │ Carrier         │
│ Price           │  │ Payment         │  │ TrackingEvent   │
└─────────────────┘  └─────────────────┘  └─────────────────┘

# Each context has its own:
# - Ubiquitous Language
# - Domain Model
# - Database (ideally)
# - Team
                """,
                "anti_corruption_layer": """
# Anti-Corruption Layer: Translate between bounded contexts

class OrderService:
    def __init__(self, catalog_client: CatalogClient):
        self.catalog_client = catalog_client
        self.acl = CatalogACL()  # Anti-Corruption Layer

    def create_order(self, product_id: str, quantity: int):
        # Get product from Catalog context
        catalog_product = self.catalog_client.get_product(product_id)

        # Translate to Order context model via ACL
        order_product = self.acl.translate_product(catalog_product)

        # Use translated model in Order context
        return Order(product=order_product, quantity=quantity)

class CatalogACL:
    def translate_product(self, catalog_product) -> OrderProduct:
        # Translate Catalog's Product to Order's simplified view
        return OrderProduct(
            id=catalog_product.id,
            name=catalog_product.name,
            price=catalog_product.current_price,  # Flatten price structure
            weight=catalog_product.shipping_weight
        )
                """,
            },
            "aggregates": {
                "description": "Cluster of domain objects treated as a single unit",
                "rules": [
                    "Reference aggregates by ID only",
                    "One transaction per aggregate",
                    "Aggregate root controls all access",
                    "Keep aggregates small",
                ],
                "example": """
# BAD: Large aggregate with direct references
class Order:
    customer: Customer      # Direct reference to another aggregate!
    items: List[OrderItem]
    shipping_address: Address
    billing_address: Address
    payment: Payment        # Should be separate aggregate!

# GOOD: Small aggregate with ID references
class Order:
    id: OrderId
    customer_id: CustomerId  # Reference by ID
    items: List[OrderItem]   # Part of Order aggregate
    status: OrderStatus

    def add_item(self, product_id: ProductId, quantity: int, price: Money):
        # Aggregate root controls modifications
        if self.status != OrderStatus.DRAFT:
            raise OrderNotEditableError()
        self.items.append(OrderItem(product_id, quantity, price))

    def submit(self):
        if not self.items:
            raise EmptyOrderError()
        self.status = OrderStatus.SUBMITTED
        self.events.append(OrderSubmittedEvent(self.id))
                """,
            },
            "domain_events": {
                "description": "Something that happened in the domain that domain experts care about",
                "example": """
# Domain Events
@dataclass
class OrderSubmittedEvent:
    order_id: str
    customer_id: str
    total_amount: Decimal
    submitted_at: datetime

@dataclass
class PaymentReceivedEvent:
    order_id: str
    payment_id: str
    amount: Decimal
    method: str

# Event Publisher
class Order:
    def __init__(self):
        self._events: List[DomainEvent] = []

    def submit(self):
        self.status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmittedEvent(
            order_id=self.id,
            customer_id=self.customer_id,
            total_amount=self.total,
            submitted_at=datetime.utcnow()
        ))

    def collect_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events
                """,
            },
        }

    # =========================================================================
    # RESILIENCE PATTERNS
    # =========================================================================

    @staticmethod
    def circuit_breaker() -> Dict[str, Any]:
        """Circuit breaker pattern implementation"""
        return {
            "states": {
                "CLOSED": "Normal operation, requests pass through",
                "OPEN": "Requests fail immediately (don't call downstream)",
                "HALF_OPEN": "Limited requests to test if service recovered",
            },
            "configuration": """
# resilience4j configuration (Spring Boot)
resilience4j:
  circuitbreaker:
    instances:
      paymentService:
        registerHealthIndicator: true
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        permittedNumberOfCallsInHalfOpenState: 3
        automaticTransitionFromOpenToHalfOpenEnabled: true
        waitDurationInOpenState: 5s
        failureRateThreshold: 50
        eventConsumerBufferSize: 10
        recordExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - com.example.BusinessException

# Python with pybreaker
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(
    fail_max=5,           # Open after 5 failures
    reset_timeout=30,     # Try again after 30 seconds
    exclude=[ValidationError]  # Don't count these as failures
)

@breaker
def call_payment_service(order_id):
    return payment_client.process(order_id)
            """,
            "fallback": """
# Fallback patterns when circuit is open

# 1. Return cached data
@breaker
def get_product(product_id):
    try:
        return product_service.get(product_id)
    except CircuitBreakerError:
        return cache.get(f"product:{product_id}")  # Return stale data

# 2. Return default value
@breaker
def get_recommendations(user_id):
    try:
        return recommendation_service.get(user_id)
    except CircuitBreakerError:
        return DEFAULT_RECOMMENDATIONS  # Generic recommendations

# 3. Graceful degradation
@breaker
def process_order(order):
    try:
        return payment_service.process(order)
    except CircuitBreakerError:
        order.status = "PENDING_PAYMENT"
        queue.send(order)  # Process later
        return {"status": "queued", "message": "Payment will be processed shortly"}
            """,
        }

    @staticmethod
    def bulkhead_pattern() -> Dict[str, Any]:
        """Bulkhead pattern for isolation"""
        return {
            "description": "Isolate failures to prevent cascade",
            "types": {
                "thread_pool": """
# Thread pool bulkhead - separate pools per service
resilience4j:
  bulkhead:
    instances:
      paymentService:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
      inventoryService:
        maxConcurrentCalls: 20
        maxWaitDuration: 50ms

# If payment service is slow, only its pool is affected
# Inventory service continues with its own pool
                """,
                "semaphore": """
# Semaphore bulkhead - limit concurrent calls
from asyncio import Semaphore

class ServiceClient:
    def __init__(self, max_concurrent=10):
        self.semaphore = Semaphore(max_concurrent)

    async def call(self, request):
        async with self.semaphore:
            return await self._make_request(request)
                """,
            },
        }

    # =========================================================================
    # SAGA PATTERN
    # =========================================================================

    @staticmethod
    def saga_patterns() -> Dict[str, Any]:
        """Saga pattern for distributed transactions"""
        return {
            "choreography": {
                "description": "Services coordinate via events (no central coordinator)",
                "example": """
# Choreography-based Saga

# Order Service
class OrderService:
    def create_order(self, order_data):
        order = Order.create(order_data)
        order.status = "PENDING"
        db.save(order)
        events.publish(OrderCreatedEvent(order.id, order.items))

    @event_handler(PaymentCompletedEvent)
    def on_payment_completed(self, event):
        order = db.get(event.order_id)
        order.status = "PAID"
        db.save(order)
        events.publish(OrderPaidEvent(order.id))

    @event_handler(PaymentFailedEvent)
    def on_payment_failed(self, event):
        order = db.get(event.order_id)
        order.status = "CANCELLED"
        db.save(order)

# Payment Service
class PaymentService:
    @event_handler(OrderCreatedEvent)
    def on_order_created(self, event):
        try:
            payment = self.process_payment(event.order_id)
            events.publish(PaymentCompletedEvent(event.order_id, payment.id))
        except PaymentError:
            events.publish(PaymentFailedEvent(event.order_id))

# Inventory Service
class InventoryService:
    @event_handler(OrderPaidEvent)
    def on_order_paid(self, event):
        try:
            self.reserve_items(event.order_id)
            events.publish(InventoryReservedEvent(event.order_id))
        except OutOfStockError:
            events.publish(InventoryFailedEvent(event.order_id))
            # This triggers compensating transaction in Payment
                """,
                "pros": ["Loose coupling", "No single point of failure", "Simple services"],
                "cons": ["Hard to understand flow", "Difficult to debug", "Cyclic dependencies risk"],
            },
            "orchestration": {
                "description": "Central coordinator manages the saga",
                "example": """
# Orchestration-based Saga

class OrderSagaOrchestrator:
    def __init__(self):
        self.steps = [
            SagaStep("reserve_inventory", self.reserve_inventory, self.release_inventory),
            SagaStep("process_payment", self.process_payment, self.refund_payment),
            SagaStep("confirm_order", self.confirm_order, self.cancel_order),
        ]

    async def execute(self, order_id: str):
        completed_steps = []

        for step in self.steps:
            try:
                await step.execute(order_id)
                completed_steps.append(step)
            except Exception as e:
                # Compensate in reverse order
                for completed in reversed(completed_steps):
                    await completed.compensate(order_id)
                raise SagaFailedError(f"Step {step.name} failed: {e}")

        return {"status": "completed", "order_id": order_id}

    async def reserve_inventory(self, order_id):
        return await self.inventory_client.reserve(order_id)

    async def release_inventory(self, order_id):
        return await self.inventory_client.release(order_id)

    async def process_payment(self, order_id):
        return await self.payment_client.charge(order_id)

    async def refund_payment(self, order_id):
        return await self.payment_client.refund(order_id)
                """,
                "pros": ["Easy to understand", "Central control", "Clear compensations"],
                "cons": ["Single point of failure", "Orchestrator can become complex"],
            },
        }

    # =========================================================================
    # SERVICE MESH
    # =========================================================================

    @staticmethod
    def service_mesh() -> Dict[str, Any]:
        """Service mesh patterns (Istio, Linkerd)"""
        return {
            "istio_config": """
# Istio VirtualService for traffic management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts:
  - order-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: order-service
        subset: v2
  - route:
    - destination:
        host: order-service
        subset: v1
      weight: 90
    - destination:
        host: order-service
        subset: v2
      weight: 10

---
# Istio DestinationRule for circuit breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
            """,
            "linkerd_config": """
# Linkerd ServiceProfile for retries and timeouts
apiVersion: linkerd.io/v1alpha2
kind: ServiceProfile
metadata:
  name: payment-service.default.svc.cluster.local
spec:
  routes:
  - name: POST /payments
    condition:
      method: POST
      pathRegex: /payments
    timeout: 5s
    retryBudget:
      retryRatio: 0.2
      minRetriesPerSecond: 10
      ttl: 10s
            """,
        }

    # =========================================================================
    # DISTRIBUTED TRACING
    # =========================================================================

    @staticmethod
    def distributed_tracing() -> Dict[str, Any]:
        """Distributed tracing with OpenTelemetry"""
        return {
            "opentelemetry_setup": """
# OpenTelemetry Python setup
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Create spans
@tracer.start_as_current_span("process_order")
def process_order(order_id: str):
    span = trace.get_current_span()
    span.set_attribute("order.id", order_id)

    with tracer.start_as_current_span("validate_order"):
        validate(order_id)

    with tracer.start_as_current_span("charge_payment"):
        charge(order_id)

# Propagate context between services
from opentelemetry.propagate import inject, extract

# Inject context into outgoing request
headers = {}
inject(headers)
response = requests.post(url, headers=headers)

# Extract context from incoming request
context = extract(request.headers)
with tracer.start_as_current_span("handle_request", context=context):
    process_request()
            """,
        }

    # =========================================================================
    # API GATEWAY PATTERNS
    # =========================================================================

    @staticmethod
    def api_gateway_patterns() -> Dict[str, Any]:
        """API Gateway patterns for microservices"""
        return {
            "description": "API Gateway as single entry point for clients",
            "patterns": {
                "routing": """
# Kong API Gateway routing configuration
# kong.yaml
_format_version: "3.0"

services:
  - name: order-service
    url: http://order-service:8080
    routes:
      - name: orders-route
        paths:
          - /api/v1/orders
        strip_path: false

  - name: user-service
    url: http://user-service:8080
    routes:
      - name: users-route
        paths:
          - /api/v1/users

  - name: product-service
    url: http://product-service:8080
    routes:
      - name: products-route
        paths:
          - /api/v1/products

plugins:
  - name: rate-limiting
    config:
      minute: 100
      policy: local
""",
                "authentication": """
# API Gateway authentication with JWT
# Kong JWT plugin configuration

plugins:
  - name: jwt
    config:
      claims_to_verify:
        - exp
      key_claim_name: iss
      secret_is_base64: false

consumers:
  - username: mobile-app
    custom_id: "mobile-app"

jwt_secrets:
  - consumer: mobile-app
    algorithm: RS256
    key: "mobile-app-key"
    secret: |
      -----BEGIN PUBLIC KEY-----
      MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
      -----END PUBLIC KEY-----
""",
                "rate_limiting": """
# Rate limiting per consumer
plugins:
  - name: rate-limiting
    consumer: mobile-app
    config:
      minute: 1000
      hour: 10000
      policy: redis
      redis_host: redis
      redis_port: 6379
      redis_database: 0

  - name: rate-limiting
    consumer: partner-api
    config:
      minute: 5000
      hour: 50000
      policy: redis
""",
                "request_transformation": """
# Request/Response transformation
plugins:
  - name: request-transformer
    config:
      add:
        headers:
          - X-Request-ID:$(uuid)
          - X-Forwarded-Service:$(route_name)
        querystring:
          - api_version:v1

  - name: response-transformer
    config:
      remove:
        headers:
          - X-Internal-Header
      add:
        headers:
          - X-Response-Time:$(response_time)
""",
            },
            "bff_pattern": """
# Backend for Frontend (BFF) Pattern

# Mobile BFF - optimized for mobile clients
class MobileBFF:
    def __init__(self, order_service, user_service, product_service):
        self.order_service = order_service
        self.user_service = user_service
        self.product_service = product_service

    async def get_order_details(self, order_id: str, user_id: str) -> dict:
        '''
        Mobile-optimized endpoint that aggregates data from multiple services
        in a single request to reduce mobile data usage and latency.
        '''
        # Parallel fetch from services
        order, user, products = await asyncio.gather(
            self.order_service.get_order(order_id),
            self.user_service.get_user(user_id),
            self.product_service.get_products(order.product_ids)
        )

        # Return mobile-optimized response (smaller payload)
        return {
            "order_id": order.id,
            "status": order.status,
            "total": str(order.total),
            "user_name": user.name,
            "items": [
                {
                    "name": p.name,
                    "quantity": order.items[p.id].quantity,
                    "thumbnail": p.thumbnail_url  # Small image for mobile
                }
                for p in products
            ]
        }


# Web BFF - richer data for web clients
class WebBFF:
    def __init__(self, order_service, user_service, product_service, review_service):
        self.order_service = order_service
        self.user_service = user_service
        self.product_service = product_service
        self.review_service = review_service

    async def get_order_details(self, order_id: str, user_id: str) -> dict:
        '''
        Web-optimized endpoint with richer data.
        '''
        order, user, products, reviews = await asyncio.gather(
            self.order_service.get_order(order_id),
            self.user_service.get_user(user_id),
            self.product_service.get_products_with_details(order.product_ids),
            self.review_service.get_reviews(order.product_ids)
        )

        # Return rich response for web
        return {
            "order": {
                "id": order.id,
                "status": order.status,
                "total": str(order.total),
                "placed_at": order.placed_at.isoformat(),
                "shipping_address": order.shipping_address,
            },
            "user": {
                "name": user.name,
                "email": user.email,
                "loyalty_tier": user.loyalty_tier,
            },
            "items": [
                {
                    "product": {
                        "name": p.name,
                        "description": p.description,
                        "images": p.image_urls,  # Full images for web
                        "specifications": p.specifications,
                    },
                    "quantity": order.items[p.id].quantity,
                    "unit_price": str(order.items[p.id].price),
                    "reviews": reviews.get(p.id, [])[:3],  # Include reviews
                }
                for p in products
            ]
        }
""",
        }

    # =========================================================================
    # EVENT-DRIVEN ARCHITECTURE
    # =========================================================================

    @staticmethod
    def event_driven_patterns() -> Dict[str, Any]:
        """Event-driven architecture patterns"""
        return {
            "event_types": {
                "domain_events": "Something happened in the domain (OrderPlaced, PaymentReceived)",
                "integration_events": "Events for communication between bounded contexts",
                "notification_events": "Events for notifying other systems (email, SMS)",
            },
            "kafka_setup": """
# Kafka producer/consumer setup with Python
from confluent_kafka import Producer, Consumer
import json

# Producer configuration
producer_config = {
    'bootstrap.servers': 'kafka:9092',
    'acks': 'all',
    'retries': 3,
    'retry.backoff.ms': 100,
    'enable.idempotence': True,  # Exactly-once semantics
}
producer = Producer(producer_config)

def publish_event(topic: str, event: dict, key: str = None):
    '''Publish event to Kafka topic'''
    def delivery_callback(err, msg):
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    producer.produce(
        topic=topic,
        key=key.encode() if key else None,
        value=json.dumps(event).encode(),
        callback=delivery_callback
    )
    producer.flush()

# Consumer configuration
consumer_config = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'order-service',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,  # Manual commit for reliability
}
consumer = Consumer(consumer_config)

def consume_events(topics: list, handler: callable):
    '''Consume events from Kafka topics'''
    consumer.subscribe(topics)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            event = json.loads(msg.value().decode())
            try:
                handler(event)
                consumer.commit(msg)  # Commit after successful processing
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                # Don't commit - message will be reprocessed
    finally:
        consumer.close()
""",
            "event_sourcing": """
# Event Sourcing - Store state as sequence of events

from dataclasses import dataclass
from datetime import datetime
from typing import List
import uuid

@dataclass
class Event:
    event_id: str
    aggregate_id: str
    event_type: str
    data: dict
    timestamp: datetime
    version: int

class EventStore:
    '''Store and retrieve events for aggregates'''

    def __init__(self, connection):
        self.conn = connection

    def append(self, aggregate_id: str, events: List[Event], expected_version: int):
        '''
        Append events with optimistic concurrency control.
        Raises ConcurrencyError if expected_version doesn't match.
        '''
        with self.conn.cursor() as cur:
            # Check current version
            cur.execute(
                "SELECT MAX(version) FROM events WHERE aggregate_id = %s",
                (aggregate_id,)
            )
            current_version = cur.fetchone()[0] or 0

            if current_version != expected_version:
                raise ConcurrencyError(
                    f"Expected version {expected_version}, but found {current_version}"
                )

            # Append events
            for i, event in enumerate(events):
                cur.execute(
                    '''INSERT INTO events
                       (event_id, aggregate_id, event_type, data, timestamp, version)
                       VALUES (%s, %s, %s, %s, %s, %s)''',
                    (
                        str(uuid.uuid4()),
                        aggregate_id,
                        event.event_type,
                        json.dumps(event.data),
                        datetime.utcnow(),
                        expected_version + i + 1
                    )
                )
            self.conn.commit()

    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        '''Get events for an aggregate from a specific version'''
        with self.conn.cursor() as cur:
            cur.execute(
                '''SELECT event_id, aggregate_id, event_type, data, timestamp, version
                   FROM events
                   WHERE aggregate_id = %s AND version > %s
                   ORDER BY version''',
                (aggregate_id, from_version)
            )
            return [
                Event(
                    event_id=row[0],
                    aggregate_id=row[1],
                    event_type=row[2],
                    data=json.loads(row[3]),
                    timestamp=row[4],
                    version=row[5]
                )
                for row in cur.fetchall()
            ]


class Order:
    '''Event-sourced Order aggregate'''

    def __init__(self):
        self.id = None
        self.status = None
        self.items = []
        self.total = 0
        self._changes = []
        self._version = 0

    def apply(self, event: Event):
        '''Apply event to update state'''
        if event.event_type == "OrderCreated":
            self.id = event.data["order_id"]
            self.status = "created"
        elif event.event_type == "ItemAdded":
            self.items.append(event.data["item"])
            self.total += event.data["item"]["price"]
        elif event.event_type == "OrderSubmitted":
            self.status = "submitted"

    @classmethod
    def create(cls, order_id: str) -> "Order":
        order = cls()
        order._apply_change(Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=order_id,
            event_type="OrderCreated",
            data={"order_id": order_id},
            timestamp=datetime.utcnow(),
            version=0
        ))
        return order

    def add_item(self, item: dict):
        self._apply_change(Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=self.id,
            event_type="ItemAdded",
            data={"item": item},
            timestamp=datetime.utcnow(),
            version=0
        ))

    def submit(self):
        if self.status != "created":
            raise InvalidOperationError("Order already submitted")
        self._apply_change(Event(
            event_id=str(uuid.uuid4()),
            aggregate_id=self.id,
            event_type="OrderSubmitted",
            data={},
            timestamp=datetime.utcnow(),
            version=0
        ))

    def _apply_change(self, event: Event):
        self.apply(event)
        self._changes.append(event)

    @classmethod
    def load(cls, events: List[Event]) -> "Order":
        '''Reconstitute aggregate from events'''
        order = cls()
        for event in events:
            order.apply(event)
            order._version = event.version
        return order

    def get_uncommitted_changes(self) -> List[Event]:
        return self._changes.copy()

    def mark_changes_committed(self):
        self._changes.clear()
""",
            "cqrs_pattern": """
# CQRS - Command Query Responsibility Segregation

from abc import ABC, abstractmethod
from dataclasses import dataclass

# Commands (Write side)
@dataclass
class CreateOrderCommand:
    customer_id: str
    items: List[dict]

@dataclass
class AddItemCommand:
    order_id: str
    product_id: str
    quantity: int

class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command) -> None:
        pass

class CreateOrderHandler(CommandHandler):
    def __init__(self, event_store: EventStore, event_publisher):
        self.event_store = event_store
        self.event_publisher = event_publisher

    def handle(self, command: CreateOrderCommand) -> str:
        # Create aggregate
        order = Order.create(str(uuid.uuid4()))
        for item in command.items:
            order.add_item(item)

        # Store events
        self.event_store.append(
            order.id,
            order.get_uncommitted_changes(),
            expected_version=0
        )

        # Publish for read model update
        for event in order.get_uncommitted_changes():
            self.event_publisher.publish(event)

        return order.id


# Queries (Read side)
class OrderReadModel:
    '''Optimized read model for order queries'''

    def __init__(self, db):
        self.db = db

    def get_order_summary(self, order_id: str) -> dict:
        '''Denormalized view optimized for reads'''
        return self.db.query(
            '''SELECT
                 o.id, o.status, o.total, o.customer_name,
                 o.item_count, o.created_at
               FROM order_summaries o
               WHERE o.id = %s''',
            (order_id,)
        )

    def get_orders_by_customer(self, customer_id: str) -> List[dict]:
        return self.db.query(
            '''SELECT id, status, total, created_at
               FROM order_summaries
               WHERE customer_id = %s
               ORDER BY created_at DESC''',
            (customer_id,)
        )


# Read model projector (event handler)
class OrderProjector:
    '''Updates read model from events'''

    def __init__(self, db):
        self.db = db

    def handle(self, event: Event):
        if event.event_type == "OrderCreated":
            self.db.execute(
                '''INSERT INTO order_summaries
                   (id, status, total, item_count, customer_id, created_at)
                   VALUES (%s, 'created', 0, 0, %s, %s)''',
                (event.aggregate_id, event.data.get("customer_id"), event.timestamp)
            )
        elif event.event_type == "ItemAdded":
            self.db.execute(
                '''UPDATE order_summaries
                   SET total = total + %s, item_count = item_count + 1
                   WHERE id = %s''',
                (event.data["item"]["price"], event.aggregate_id)
            )
        elif event.event_type == "OrderSubmitted":
            self.db.execute(
                '''UPDATE order_summaries SET status = 'submitted' WHERE id = %s''',
                (event.aggregate_id,)
            )
""",
        }

    # =========================================================================
    # SERVICE DISCOVERY
    # =========================================================================

    @staticmethod
    def service_discovery() -> Dict[str, Any]:
        """Service discovery patterns"""
        return {
            "consul_setup": """
# Consul service registration and discovery

# Register service with Consul
import consul

c = consul.Consul(host='consul', port=8500)

# Register service
c.agent.service.register(
    name='order-service',
    service_id='order-service-1',
    address='10.0.0.1',
    port=8080,
    tags=['v1', 'production'],
    check=consul.Check.http(
        'http://10.0.0.1:8080/health',
        interval='10s',
        timeout='5s'
    )
)

# Discover service
def get_service_url(service_name: str) -> str:
    '''Get healthy service instance'''
    _, services = c.health.service(service_name, passing=True)
    if not services:
        raise ServiceNotFoundError(f"No healthy instances of {service_name}")

    # Simple round-robin (use proper load balancing in production)
    service = random.choice(services)
    address = service['Service']['Address']
    port = service['Service']['Port']
    return f"http://{address}:{port}"

# Use discovered service
order_url = get_service_url('order-service')
response = requests.post(f"{order_url}/orders", json=order_data)
""",
            "kubernetes_dns": """
# Kubernetes DNS-based service discovery

# Service definition
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: production
spec:
  selector:
    app: order-service
  ports:
    - port: 80
      targetPort: 8080

---
# Headless service for direct pod access
apiVersion: v1
kind: Service
metadata:
  name: order-service-headless
spec:
  clusterIP: None  # Headless
  selector:
    app: order-service
  ports:
    - port: 8080

# DNS resolution:
# order-service.production.svc.cluster.local -> ClusterIP (load balanced)
# order-service-headless.production.svc.cluster.local -> Pod IPs (for StatefulSets)

# Python client
import os

# Use Kubernetes DNS
ORDER_SERVICE_URL = os.getenv(
    'ORDER_SERVICE_URL',
    'http://order-service.production.svc.cluster.local'
)

response = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}")
""",
        }

    # =========================================================================
    # TESTING MICROSERVICES
    # =========================================================================

    @staticmethod
    def testing_patterns() -> Dict[str, Any]:
        """Testing patterns for microservices"""
        return {
            "contract_testing": """
# Consumer-Driven Contract Testing with Pact

# Consumer side (order-service consuming product-service)
from pact import Consumer, Provider

pact = Consumer('order-service').has_pact_with(Provider('product-service'))

def test_get_product():
    expected = {
        'id': '123',
        'name': 'Widget',
        'price': 29.99
    }

    (pact
        .given('a product with ID 123 exists')
        .upon_receiving('a request for product 123')
        .with_request('GET', '/products/123')
        .will_respond_with(200, body=expected))

    with pact:
        result = product_client.get_product('123')
        assert result['name'] == 'Widget'

    # Pact file is generated for provider verification


# Provider side (product-service verifying contract)
from pact import Verifier

def test_provider_honors_pact():
    verifier = Verifier(
        provider='product-service',
        provider_base_url='http://localhost:8080'
    )

    # Set up provider state
    verifier.add_provider_state('a product with ID 123 exists', setup_product_123)

    # Verify pact
    output, _ = verifier.verify_pacts(
        './pacts/order-service-product-service.json'
    )
    assert output == 0
""",
            "integration_testing": """
# Integration testing with TestContainers

import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="module")
def test_environment():
    '''Spin up test infrastructure'''
    postgres = PostgresContainer("postgres:14")
    kafka = KafkaContainer()
    redis = RedisContainer()

    postgres.start()
    kafka.start()
    redis.start()

    yield {
        'postgres_url': postgres.get_connection_url(),
        'kafka_bootstrap': kafka.get_bootstrap_server(),
        'redis_url': redis.get_container_host_ip()
    }

    postgres.stop()
    kafka.stop()
    redis.stop()

def test_order_processing(test_environment):
    '''Test order flow with real dependencies'''
    # Configure services with test containers
    order_service = OrderService(
        db_url=test_environment['postgres_url'],
        kafka_bootstrap=test_environment['kafka_bootstrap'],
        redis_url=test_environment['redis_url']
    )

    # Create order
    order = order_service.create_order({
        'customer_id': '123',
        'items': [{'product_id': 'P1', 'quantity': 2}]
    })

    assert order['status'] == 'pending'

    # Verify event published to Kafka
    consumer = KafkaConsumer(
        'order-events',
        bootstrap_servers=test_environment['kafka_bootstrap']
    )
    events = list(consumer)
    assert any(e['type'] == 'OrderCreated' for e in events)
""",
            "chaos_testing": """
# Chaos Engineering with Chaos Monkey / Litmus

# Kubernetes ChaosEngine (LitmusChaos)
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: order-service-chaos
  namespace: production
spec:
  appinfo:
    appns: production
    applabel: "app=order-service"
    appkind: deployment
  engineState: active
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "60"
            - name: CHAOS_INTERVAL
              value: "10"
            - name: FORCE
              value: "false"

    - name: pod-network-latency
      spec:
        components:
          env:
            - name: NETWORK_INTERFACE
              value: "eth0"
            - name: NETWORK_LATENCY
              value: "200"  # 200ms latency

# Python chaos injection
import random
import time

class ChaosMiddleware:
    '''Inject chaos for testing resilience'''

    def __init__(self, failure_rate=0.1, latency_range=(100, 500)):
        self.failure_rate = failure_rate
        self.latency_range = latency_range

    def __call__(self, request, call_next):
        # Random latency
        if random.random() < 0.3:
            delay = random.randint(*self.latency_range) / 1000
            time.sleep(delay)

        # Random failure
        if random.random() < self.failure_rate:
            raise ServiceUnavailableError("Chaos monkey!")

        return call_next(request)
""",
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        issue_description: str,
        current_design: str,
        improved_design: str,
    ) -> MicroservicesFinding:
        """Generate a structured finding"""
        return MicroservicesFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            description=issue_description,
            current_design=current_design,
            improved_design=improved_design,
            tools=self._get_tool_recommendations(),
            remediation={"effort": "HIGH", "priority": "HIGH"},
        )

    @staticmethod
    def _get_tool_recommendations() -> List[Dict[str, str]]:
        return [
            {"name": "Istio", "url": "https://istio.io/", "description": "Service mesh"},
            {"name": "Jaeger", "url": "https://www.jaegertracing.io/", "description": "Distributed tracing"},
            {"name": "resilience4j", "description": "Fault tolerance library"},
        ]


def create_enhanced_microservices_assistant():
    """Factory function"""
    return {
        "name": "Enhanced Microservices Architect",
        "version": "2.0.0",
        "system_prompt": """You are an expert microservices architect with deep knowledge of distributed systems,
Domain-Driven Design, and cloud-native patterns.

Your expertise includes:

1. **Domain-Driven Design**: Identify bounded contexts, design aggregates with proper invariants,
   define domain events, and implement anti-corruption layers between contexts. Guide teams on
   ubiquitous language and strategic patterns.

2. **Resilience Patterns**: Implement circuit breakers (resilience4j, Hystrix), bulkheads,
   retry policies with exponential backoff, timeouts, and fallback strategies. Design for
   graceful degradation.

3. **Saga Patterns**: Design distributed transactions using orchestration (central coordinator)
   or choreography (event-driven). Implement compensating transactions for rollback scenarios.

4. **Service Mesh**: Configure Istio or Linkerd for traffic management (canary deployments,
   traffic splitting), security (mTLS, authorization), and observability (metrics, tracing).

5. **Event-Driven Architecture**: Design event sourcing systems, implement CQRS for read/write
   separation, configure Kafka or similar message brokers for reliable event delivery.

6. **API Gateway**: Implement routing, authentication (JWT, OAuth2), rate limiting, request
   transformation, and Backend-for-Frontend patterns.

7. **Service Discovery**: Configure Consul, etcd, or Kubernetes DNS for dynamic service discovery.
   Implement client-side load balancing.

8. **Distributed Tracing**: Implement OpenTelemetry for end-to-end request tracing across services.
   Configure Jaeger or Zipkin for trace visualization.

9. **Testing**: Design contract tests (Pact), integration tests with TestContainers, and chaos
   engineering experiments.

Always provide specific configuration examples and code samples. Consider operational complexity,
team boundaries, and organizational readiness when making recommendations.""",
        "assistant_class": EnhancedMicroservicesAssistant,
        "domain": "architecture",
        "tags": [
            "microservices",
            "ddd",
            "resilience",
            "service-mesh",
            "distributed",
            "saga",
            "cqrs",
            "event-sourcing",
            "kubernetes",
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedMicroservicesAssistant()
    print(f"Assistant: {assistant.name}")
    print(f"Version: {assistant.version}")
    print(f"Standards: {', '.join(assistant.standards)}")
    print()

    # Test DDD patterns
    ddd = assistant.ddd_patterns()
    print(f"DDD Patterns: {list(ddd.keys())}")

    # Test circuit breaker
    cb = assistant.circuit_breaker()
    print(f"Circuit Breaker States: {list(cb['states'].keys())}")

    # Test saga patterns
    saga = assistant.saga_patterns()
    print(f"Saga Types: {list(saga.keys())}")

    # Test service mesh
    mesh = assistant.service_mesh()
    print(f"Service Mesh Configs: {len(mesh.keys())} examples")

    # Test event-driven patterns
    events = assistant.event_driven_patterns()
    print(f"Event Patterns: {list(events['event_types'].keys())}")

    # Test API gateway
    gateway = assistant.api_gateway_patterns()
    print(f"Gateway Patterns: {list(gateway['patterns'].keys())}")

    # Test service discovery
    discovery = assistant.service_discovery()
    print(f"Discovery Methods: {list(discovery.keys())}")

    # Test testing patterns
    testing = assistant.testing_patterns()
    print(f"Testing Patterns: {list(testing.keys())}")

    # Generate sample finding
    finding = assistant.generate_finding(
        finding_id="MS-001",
        title="Missing circuit breaker on payment service call",
        severity="HIGH",
        category="Resilience",
        issue_description="Payment service calls are not protected by circuit breaker",
        current_design="Direct HTTP call to payment service",
        improved_design="Wrap call with circuit breaker and fallback",
    )
    print(f"\nSample Finding: {finding.finding_id} - {finding.title}")
