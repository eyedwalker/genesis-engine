"""
Enhanced Event-Driven Architecture Advisor

Comprehensive event-driven patterns covering:
- Event sourcing implementation
- CQRS (Command Query Responsibility Segregation)
- Saga patterns (orchestration vs choreography)
- Event store design
- Event versioning and upcasting
- Message brokers (Kafka, RabbitMQ)
- Exactly-once semantics

References:
- Event Sourcing: https://martinfowler.com/eaaDev/EventSourcing.html
- CQRS: https://martinfowler.com/bliki/CQRS.html
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class EventDrivenFinding(BaseModel):
    finding_id: str = Field(...)
    title: str = Field(...)
    severity: str = Field(...)
    category: str = Field(...)
    pattern_violated: str = Field(default="")
    current_design: str = Field(default="")
    improved_design: str = Field(default="")
    tools: List[Dict[str, str]] = Field(default_factory=list)
    remediation: Dict[str, str] = Field(default_factory=dict)


class EnhancedEventDrivenAssistant:
    """Enhanced Event-Driven Architecture Advisor"""

    def __init__(self):
        self.name = "Enhanced Event-Driven Architecture Advisor"
        self.version = "2.0.0"
        self.standards = ["Event Sourcing", "CQRS", "Saga Pattern"]

    @staticmethod
    def event_sourcing() -> Dict[str, Any]:
        """Event sourcing patterns"""
        return {
            "concept": """
# Event Sourcing: Store state changes as sequence of events
# Instead of storing current state, store all events that led to current state

# Traditional: Store current balance
# UPDATE accounts SET balance = 150 WHERE id = 1

# Event Sourcing: Store events
events = [
    AccountCreated(account_id=1, initial_balance=100),
    MoneyDeposited(account_id=1, amount=100),
    MoneyWithdrawn(account_id=1, amount=50),
]
# Current state = replay events: 100 + 100 - 50 = 150
            """,
            "event_store": """
# Event Store Schema
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    stream_id VARCHAR(255) NOT NULL,
    stream_type VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    version INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stream_id, version)  -- Optimistic concurrency
);

# Append event
def append_event(stream_id, event, expected_version):
    try:
        db.execute('''
            INSERT INTO events (stream_id, stream_type, event_type, event_data, version)
            VALUES (?, ?, ?, ?, ?)
        ''', stream_id, stream_type, event.type, event.data, expected_version + 1)
    except UniqueViolation:
        raise ConcurrencyError("Stream was modified")
            """,
            "projections": """
# Projections: Build read models from events
class AccountBalanceProjection:
    def __init__(self):
        self.balances = {}

    def handle(self, event):
        if event.type == "AccountCreated":
            self.balances[event.account_id] = event.initial_balance
        elif event.type == "MoneyDeposited":
            self.balances[event.account_id] += event.amount
        elif event.type == "MoneyWithdrawn":
            self.balances[event.account_id] -= event.amount

    def get_balance(self, account_id):
        return self.balances.get(account_id, 0)
            """,
        }

    @staticmethod
    def cqrs() -> Dict[str, Any]:
        """CQRS patterns"""
        return {
            "separation": """
# CQRS: Separate read and write models

# Write Model (Commands)
class CreateOrderCommand:
    customer_id: str
    items: List[OrderItem]

class OrderCommandHandler:
    def handle(self, command: CreateOrderCommand):
        order = Order.create(command.customer_id, command.items)
        self.repository.save(order)
        self.event_bus.publish(OrderCreatedEvent(order.id))

# Read Model (Queries)
class OrderReadModel:
    def __init__(self, db):
        self.db = db

    def get_orders_by_customer(self, customer_id):
        return self.db.query('''
            SELECT * FROM order_read_model
            WHERE customer_id = ?
            ORDER BY created_at DESC
        ''', customer_id)

# Read model updated by event handlers
class OrderReadModelUpdater:
    @event_handler(OrderCreatedEvent)
    def on_order_created(self, event):
        self.db.execute('''
            INSERT INTO order_read_model (id, customer_id, status, total)
            VALUES (?, ?, ?, ?)
        ''', event.order_id, event.customer_id, 'created', event.total)
            """,
        }

    @staticmethod
    def saga_patterns() -> Dict[str, Any]:
        """Saga patterns for distributed transactions"""
        return {
            "choreography": """
# Choreography: Services coordinate via events (no central coordinator)

# Order Service
@event_handler(OrderCreatedEvent)
def on_order_created(event):
    publish(ReserveInventoryCommand(event.order_id, event.items))

# Inventory Service
@event_handler(ReserveInventoryCommand)
def on_reserve_inventory(event):
    try:
        reserve(event.items)
        publish(InventoryReservedEvent(event.order_id))
    except OutOfStock:
        publish(InventoryFailedEvent(event.order_id))

# Payment Service
@event_handler(InventoryReservedEvent)
def on_inventory_reserved(event):
    try:
        charge(event.order_id)
        publish(PaymentCompletedEvent(event.order_id))
    except PaymentFailed:
        publish(PaymentFailedEvent(event.order_id))
        publish(ReleaseInventoryCommand(event.order_id))  # Compensate
            """,
            "orchestration": """
# Orchestration: Central coordinator manages saga

class OrderSaga:
    def __init__(self):
        self.state = "STARTED"

    async def execute(self, order_id):
        try:
            await self.reserve_inventory(order_id)
            self.state = "INVENTORY_RESERVED"

            await self.process_payment(order_id)
            self.state = "PAYMENT_COMPLETED"

            await self.confirm_order(order_id)
            self.state = "COMPLETED"
        except Exception as e:
            await self.compensate(order_id)
            self.state = "FAILED"

    async def compensate(self, order_id):
        if self.state == "PAYMENT_COMPLETED":
            await self.refund_payment(order_id)
        if self.state in ["INVENTORY_RESERVED", "PAYMENT_COMPLETED"]:
            await self.release_inventory(order_id)
        await self.cancel_order(order_id)
            """,
        }

    # =========================================================================
    # EVENT VERSIONING AND UPCASTING
    # =========================================================================

    @staticmethod
    def event_versioning() -> Dict[str, Any]:
        """Event versioning and schema evolution patterns"""
        return {
            "versioning_strategies": {
                "description": "Handle event schema changes over time",
                "bad": '''
# BAD: No versioning - breaking changes break consumers
class OrderCreatedEvent:
    order_id: str
    customer_id: str
    items: list

# Later change - adds required field, breaks old consumers!
class OrderCreatedEvent:
    order_id: str
    customer_id: str
    items: list
    shipping_address: str  # New required field!
                ''',
                "good": '''
# GOOD: Explicit versioning with upcasting
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class EventMetadata:
    event_id: str
    event_type: str
    version: int
    timestamp: datetime
    correlation_id: str
    causation_id: Optional[str]

@dataclass
class OrderCreatedEventV1:
    """Original version"""
    VERSION = 1
    order_id: str
    customer_id: str
    items: list[dict]

@dataclass
class OrderCreatedEventV2:
    """Added shipping_address"""
    VERSION = 2
    order_id: str
    customer_id: str
    items: list[dict]
    shipping_address: str

@dataclass
class OrderCreatedEventV3:
    """Added currency, split address into components"""
    VERSION = 3
    order_id: str
    customer_id: str
    items: list[dict]
    shipping_street: str
    shipping_city: str
    shipping_country: str
    currency: str

class EventUpcaster(ABC):
    """Transform old events to newer versions"""

    @abstractmethod
    def can_upcast(self, event_type: str, from_version: int) -> bool:
        pass

    @abstractmethod
    def upcast(self, event_data: dict, from_version: int) -> dict:
        pass

class OrderCreatedUpcaster(EventUpcaster):
    def can_upcast(self, event_type: str, from_version: int) -> bool:
        return event_type == "OrderCreated" and from_version < 3

    def upcast(self, event_data: dict, from_version: int) -> dict:
        """Upcast to latest version"""
        if from_version == 1:
            # V1 -> V2: Add default shipping address
            event_data = {
                **event_data,
                "shipping_address": "Unknown",
                "version": 2
            }
            from_version = 2

        if from_version == 2:
            # V2 -> V3: Split address, add currency
            address = event_data.get("shipping_address", "Unknown")
            event_data = {
                **event_data,
                "shipping_street": address,
                "shipping_city": "Unknown",
                "shipping_country": "Unknown",
                "currency": "USD",  # Default
                "version": 3
            }
            del event_data["shipping_address"]

        return event_data

class EventStore:
    """Event store with upcasting support"""

    def __init__(self):
        self.upcasters: list[EventUpcaster] = [
            OrderCreatedUpcaster(),
            # Add more upcasters as needed
        ]

    def read_events(self, stream_id: str) -> list:
        """Read events and upcast to latest version"""
        raw_events = db.execute(
            "SELECT * FROM events WHERE stream_id = %s ORDER BY version",
            (stream_id,)
        ).fetchall()

        upcasted_events = []
        for raw in raw_events:
            event_data = json.loads(raw["event_data"])
            event_version = raw["schema_version"]
            event_type = raw["event_type"]

            # Find applicable upcaster
            for upcaster in self.upcasters:
                if upcaster.can_upcast(event_type, event_version):
                    event_data = upcaster.upcast(event_data, event_version)

            upcasted_events.append(event_data)

        return upcasted_events
                ''',
            },
            "weak_schema": '''
# Alternative: Weak schema approach
# Store events with flexible schema, handle missing fields in consumers

class FlexibleEventHandler:
    """Handle events with potentially missing fields"""

    def handle_order_created(self, event: dict):
        order_id = event["order_id"]  # Always required
        customer_id = event["customer_id"]  # Always required

        # Optional fields with defaults
        shipping_address = event.get("shipping_address", self._lookup_default_address(customer_id))
        currency = event.get("currency", "USD")

        # Process with resolved values
        self._process_order(order_id, customer_id, shipping_address, currency)
            ''',
        }

    # =========================================================================
    # MESSAGE BROKERS
    # =========================================================================

    @staticmethod
    def kafka_patterns() -> Dict[str, Any]:
        """Apache Kafka patterns and best practices"""
        return {
            "producer_patterns": {
                "description": "Kafka producer best practices",
                "bad": '''
# BAD: Fire and forget with no error handling
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def publish_event(topic: str, event: dict):
    # No acknowledgment, no error handling!
    producer.send(topic, json.dumps(event).encode())
                ''',
                "good": '''
# GOOD: Reliable producer with proper configuration
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from typing import Optional, Callable

class ReliableKafkaProducer:
    """Production-ready Kafka producer"""

    def __init__(self, bootstrap_servers: list[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            # Durability settings
            acks='all',  # Wait for all replicas
            retries=3,
            retry_backoff_ms=1000,
            # Idempotence - exactly-once semantics
            enable_idempotence=True,
            max_in_flight_requests_per_connection=5,
            # Serialization
            key_serializer=lambda k: k.encode() if k else None,
            value_serializer=lambda v: json.dumps(v).encode(),
            # Performance
            linger_ms=10,  # Batch for 10ms
            batch_size=16384,
            compression_type='snappy',
        )

    def publish(
        self,
        topic: str,
        value: dict,
        key: Optional[str] = None,
        headers: Optional[dict] = None,
        on_success: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ):
        """Publish with callbacks"""
        kafka_headers = [
            (k, v.encode()) for k, v in (headers or {}).items()
        ]

        future = self.producer.send(
            topic,
            key=key,
            value=value,
            headers=kafka_headers
        )

        # Add callbacks
        def handle_success(record_metadata):
            logger.info(
                "Message sent",
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset
            )
            if on_success:
                on_success(record_metadata)

        def handle_error(exception):
            logger.error("Failed to send message", error=str(exception))
            if on_error:
                on_error(exception)

        future.add_callback(handle_success)
        future.add_errback(handle_error)

        return future

    def publish_sync(self, topic: str, value: dict, key: str = None, timeout: float = 10.0):
        """Synchronous publish with timeout"""
        future = self.producer.send(topic, key=key, value=value)

        try:
            record_metadata = future.get(timeout=timeout)
            return {
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        except KafkaError as e:
            logger.error("Kafka send failed", error=str(e))
            raise

    def flush(self):
        """Flush pending messages"""
        self.producer.flush()

    def close(self):
        """Close producer gracefully"""
        self.producer.flush()
        self.producer.close()
                ''',
            },
            "consumer_patterns": {
                "description": "Kafka consumer best practices",
                "bad": '''
# BAD: Auto-commit without processing guarantee
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers='localhost:9092',
    enable_auto_commit=True,  # Commits before processing complete!
    auto_offset_reset='latest'  # Misses old messages on restart
)

for message in consumer:
    process(message)  # If this fails after commit, message is lost!
                ''',
                "good": '''
# GOOD: Manual commit with at-least-once delivery
from kafka import KafkaConsumer, OffsetAndMetadata, TopicPartition
from typing import Callable
import signal

class ReliableKafkaConsumer:
    """Production-ready Kafka consumer"""

    def __init__(
        self,
        topics: list[str],
        group_id: str,
        bootstrap_servers: list[str]
    ):
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            # Manual commit for at-least-once
            enable_auto_commit=False,
            # Start from earliest on new consumer group
            auto_offset_reset='earliest',
            # Deserialization
            key_deserializer=lambda k: k.decode() if k else None,
            value_deserializer=lambda v: json.loads(v.decode()),
            # Performance
            max_poll_records=100,
            fetch_max_wait_ms=500,
            # Session management
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
        )
        self.running = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Graceful shutdown on SIGTERM/SIGINT"""
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            self.running = False

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def consume(
        self,
        handler: Callable[[dict], None],
        batch_size: int = 1,
        commit_every_n: int = 10
    ):
        """Consume messages with manual commit"""
        processed_count = 0
        offsets_to_commit = {}

        try:
            while self.running:
                messages = self.consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        try:
                            # Process message
                            handler(record.value)

                            # Track offset for commit
                            offsets_to_commit[topic_partition] = OffsetAndMetadata(
                                record.offset + 1, None
                            )
                            processed_count += 1

                            # Commit periodically
                            if processed_count % commit_every_n == 0:
                                self._commit_offsets(offsets_to_commit)
                                offsets_to_commit = {}

                        except Exception as e:
                            logger.error(
                                "Message processing failed",
                                topic=record.topic,
                                partition=record.partition,
                                offset=record.offset,
                                error=str(e)
                            )
                            # Don't commit - message will be reprocessed
                            # Consider: Dead letter queue for poison messages
                            self._handle_poison_message(record, e)

            # Final commit before shutdown
            if offsets_to_commit:
                self._commit_offsets(offsets_to_commit)

        finally:
            self.consumer.close()
            logger.info("Consumer closed")

    def _commit_offsets(self, offsets: dict):
        """Commit offsets synchronously"""
        try:
            self.consumer.commit(offsets)
            logger.debug("Offsets committed", offsets=str(offsets))
        except Exception as e:
            logger.error("Offset commit failed", error=str(e))

    def _handle_poison_message(self, record, error: Exception):
        """Handle messages that repeatedly fail processing"""
        # Send to dead letter queue
        dlq_producer.publish(
            topic=f"{record.topic}.dlq",
            value={
                "original_message": record.value,
                "error": str(error),
                "failed_at": datetime.utcnow().isoformat(),
                "original_topic": record.topic,
                "original_partition": record.partition,
                "original_offset": record.offset
            }
        )
                ''',
            },
            "exactly_once": '''
# Exactly-once semantics with transactions
class TransactionalKafkaProducer:
    """Kafka producer with exactly-once semantics"""

    def __init__(self, bootstrap_servers: list[str], transactional_id: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            enable_idempotence=True,
            transactional_id=transactional_id,
            acks='all',
            key_serializer=lambda k: k.encode() if k else None,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        # Initialize transactions
        self.producer.init_transactions()

    def send_with_transaction(self, messages: list[dict]):
        """Send multiple messages in a transaction"""
        try:
            self.producer.begin_transaction()

            for msg in messages:
                self.producer.send(
                    msg["topic"],
                    key=msg.get("key"),
                    value=msg["value"]
                )

            self.producer.commit_transaction()
            logger.info("Transaction committed", message_count=len(messages))

        except Exception as e:
            logger.error("Transaction failed", error=str(e))
            self.producer.abort_transaction()
            raise

# Consumer with read_committed isolation
consumer = KafkaConsumer(
    'my-topic',
    isolation_level='read_committed',  # Only read committed messages
    # ... other config
)
            ''',
        }

    # =========================================================================
    # OUTBOX PATTERN
    # =========================================================================

    @staticmethod
    def outbox_pattern() -> Dict[str, Any]:
        """Transactional outbox pattern for reliable messaging"""
        return {
            "description": "Guarantee message publishing alongside database updates",
            "problem": '''
# Problem: Dual writes - database and message broker not atomic
def create_order(order_data):
    # If this succeeds...
    db.execute("INSERT INTO orders (...) VALUES (...)")
    db.commit()

    # ...but this fails, we have inconsistency!
    kafka.send("orders", order_event)  # Network failure?
            ''',
            "solution": '''
# GOOD: Transactional Outbox Pattern
from sqlalchemy.orm import Session
from dataclasses import dataclass
import uuid

@dataclass
class OutboxMessage:
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict
    created_at: datetime
    published_at: datetime | None = None

class OutboxRepository:
    """Outbox table for reliable event publishing"""

    def save(self, session: Session, message: OutboxMessage):
        session.execute(
            """
            INSERT INTO outbox (id, aggregate_type, aggregate_id, event_type, payload, created_at)
            VALUES (:id, :aggregate_type, :aggregate_id, :event_type, :payload, :created_at)
            """,
            {
                "id": message.id,
                "aggregate_type": message.aggregate_type,
                "aggregate_id": message.aggregate_id,
                "event_type": message.event_type,
                "payload": json.dumps(message.payload),
                "created_at": message.created_at
            }
        )

class OrderService:
    """Service using outbox pattern"""

    def create_order(self, order_data: dict) -> Order:
        with db.begin() as session:
            # Create order
            order = Order(**order_data)
            session.add(order)

            # Create outbox message in SAME transaction
            outbox_message = OutboxMessage(
                id=str(uuid.uuid4()),
                aggregate_type="Order",
                aggregate_id=order.id,
                event_type="OrderCreated",
                payload={
                    "order_id": order.id,
                    "customer_id": order.customer_id,
                    "total": str(order.total),
                    "items": [item.to_dict() for item in order.items]
                },
                created_at=datetime.utcnow()
            )
            outbox_repo.save(session, outbox_message)

            # Both committed atomically
            session.commit()

        return order

class OutboxPublisher:
    """Publish outbox messages to Kafka"""

    def __init__(self, kafka_producer: ReliableKafkaProducer):
        self.producer = kafka_producer

    def poll_and_publish(self, batch_size: int = 100):
        """Poll outbox and publish to Kafka"""
        # Get unpublished messages
        messages = db.execute(
            """
            SELECT * FROM outbox
            WHERE published_at IS NULL
            ORDER BY created_at
            LIMIT :limit
            FOR UPDATE SKIP LOCKED
            """,
            {"limit": batch_size}
        ).fetchall()

        for msg in messages:
            try:
                # Publish to Kafka
                topic = f"{msg.aggregate_type.lower()}.{msg.event_type}"
                self.producer.publish_sync(
                    topic=topic,
                    key=msg.aggregate_id,
                    value=json.loads(msg.payload)
                )

                # Mark as published
                db.execute(
                    "UPDATE outbox SET published_at = :published_at WHERE id = :id",
                    {"published_at": datetime.utcnow(), "id": msg.id}
                )
                db.commit()

            except Exception as e:
                logger.error("Failed to publish outbox message", id=msg.id, error=str(e))
                db.rollback()

    def cleanup_old_messages(self, retention_days: int = 7):
        """Delete old published messages"""
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        db.execute(
            "DELETE FROM outbox WHERE published_at < :cutoff",
            {"cutoff": cutoff}
        )
        db.commit()
            ''',
            "debezium_cdc": '''
# Alternative: Change Data Capture with Debezium
# Debezium reads database transaction log and publishes to Kafka

# debezium-connector-config.json
{
    "name": "orders-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "db.example.com",
        "database.port": "5432",
        "database.user": "debezium",
        "database.password": "${secrets:db-password}",
        "database.dbname": "orders",
        "table.include.list": "public.outbox",
        "transforms": "outbox",
        "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
        "transforms.outbox.table.field.event.key": "aggregate_id",
        "transforms.outbox.table.field.event.payload": "payload",
        "transforms.outbox.route.topic.replacement": "events.${routedByValue}",
        "transforms.outbox.table.expand.json.payload": "true"
    }
}

# Debezium automatically:
# 1. Reads PostgreSQL WAL (transaction log)
# 2. Captures INSERT to outbox table
# 3. Publishes to Kafka topic based on aggregate_type
# 4. Ensures exactly-once delivery (with Kafka transactions)
            ''',
        }

    # =========================================================================
    # IDEMPOTENCY
    # =========================================================================

    @staticmethod
    def idempotency_patterns() -> Dict[str, Any]:
        """Idempotency patterns for message processing"""
        return {
            "description": "Ensure messages can be safely reprocessed",
            "idempotent_consumer": '''
# GOOD: Idempotent message consumer
class IdempotentMessageHandler:
    """Handle messages idempotently"""

    def __init__(self):
        # Store processed message IDs
        self.processed_store = redis.Redis()
        self.expiry_seconds = 86400 * 7  # 7 days

    def handle(self, message: dict, processor: Callable):
        """Process message idempotently"""
        message_id = message.get("event_id") or message.get("id")

        if not message_id:
            logger.warning("Message without ID, cannot guarantee idempotency")
            return processor(message)

        # Check if already processed
        key = f"processed:{message_id}"
        if self.processed_store.exists(key):
            logger.info("Duplicate message, skipping", message_id=message_id)
            return None

        try:
            # Process message
            result = processor(message)

            # Mark as processed
            self.processed_store.setex(key, self.expiry_seconds, "1")

            return result

        except Exception as e:
            # Don't mark as processed on failure - allow retry
            logger.error("Processing failed", message_id=message_id, error=str(e))
            raise
            ''',
            "idempotency_key": '''
# GOOD: Idempotency key for API operations
from functools import wraps
import hashlib

def idempotent_operation(key_param: str = "idempotency_key"):
    """Decorator for idempotent API operations"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get idempotency key from request
            idempotency_key = kwargs.get(key_param) or request.headers.get("Idempotency-Key")

            if not idempotency_key:
                # No key provided - execute normally (not idempotent)
                return await func(*args, **kwargs)

            # Check for existing result
            cache_key = f"idempotent:{idempotency_key}"
            cached_result = redis.get(cache_key)

            if cached_result:
                logger.info("Returning cached idempotent result", key=idempotency_key)
                return json.loads(cached_result)

            # Execute operation
            try:
                result = await func(*args, **kwargs)

                # Cache result
                redis.setex(
                    cache_key,
                    86400,  # 24 hour expiry
                    json.dumps(result)
                )

                return result

            except Exception as e:
                # Cache error to return same error on retry
                error_result = {"error": str(e), "type": type(e).__name__}
                redis.setex(cache_key, 86400, json.dumps(error_result))
                raise

        return wrapper
    return decorator

# Usage
@idempotent_operation()
async def create_payment(payment_data: dict, idempotency_key: str = None):
    """Create payment - idempotent with key"""
    payment = await payment_service.create(payment_data)
    return payment.to_dict()
            ''',
            "natural_idempotency": '''
# GOOD: Natural idempotency through business logic
class InventoryService:
    """Naturally idempotent inventory operations"""

    def reserve_inventory(self, order_id: str, items: list[dict]):
        """Reserve inventory - naturally idempotent"""
        # Check if reservation already exists for this order
        existing = db.query(InventoryReservation).filter_by(
            order_id=order_id
        ).first()

        if existing:
            logger.info("Reservation already exists", order_id=order_id)
            return existing  # Return existing reservation

        # Create new reservation
        reservation = InventoryReservation(
            id=generate_uuid(),
            order_id=order_id,
            items=items,
            status="reserved",
            created_at=datetime.utcnow()
        )
        db.add(reservation)
        db.commit()

        return reservation

    def complete_reservation(self, order_id: str):
        """Complete reservation - naturally idempotent"""
        reservation = db.query(InventoryReservation).filter_by(
            order_id=order_id
        ).first()

        if not reservation:
            raise NotFoundError(f"No reservation for order {order_id}")

        if reservation.status == "completed":
            logger.info("Already completed", order_id=order_id)
            return reservation  # Already done, return success

        # Update inventory counts and mark complete
        for item in reservation.items:
            db.execute(
                "UPDATE inventory SET reserved = reserved - :qty WHERE sku = :sku",
                {"qty": item["quantity"], "sku": item["sku"]}
            )

        reservation.status = "completed"
        reservation.completed_at = datetime.utcnow()
        db.commit()

        return reservation
            ''',
        }

    # =========================================================================
    # DEAD LETTER QUEUES
    # =========================================================================

    @staticmethod
    def dead_letter_queue() -> Dict[str, Any]:
        """Dead letter queue patterns for handling failed messages"""
        return {
            "description": "Handle messages that cannot be processed",
            "implementation": '''
# GOOD: Dead letter queue handling
from dataclasses import dataclass
from enum import Enum

class DLQReason(Enum):
    PROCESSING_ERROR = "processing_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT = "timeout"
    MAX_RETRIES = "max_retries"
    POISON_MESSAGE = "poison_message"

@dataclass
class DeadLetterMessage:
    original_message: dict
    original_topic: str
    original_partition: int
    original_offset: int
    error_message: str
    error_type: str
    reason: DLQReason
    retry_count: int
    failed_at: datetime
    stack_trace: str | None = None

class DeadLetterQueueService:
    """Manage dead letter queue messages"""

    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min

    def __init__(self, kafka_producer: ReliableKafkaProducer):
        self.producer = kafka_producer

    def send_to_dlq(
        self,
        original_message: dict,
        original_topic: str,
        partition: int,
        offset: int,
        error: Exception,
        retry_count: int = 0
    ):
        """Send failed message to DLQ"""
        dlq_message = DeadLetterMessage(
            original_message=original_message,
            original_topic=original_topic,
            original_partition=partition,
            original_offset=offset,
            error_message=str(error),
            error_type=type(error).__name__,
            reason=self._determine_reason(error, retry_count),
            retry_count=retry_count,
            failed_at=datetime.utcnow(),
            stack_trace=traceback.format_exc()
        )

        self.producer.publish(
            topic=f"{original_topic}.dlq",
            key=str(offset),
            value=asdict(dlq_message)
        )

        # Alert on DLQ
        if retry_count >= self.MAX_RETRIES:
            alert_service.send(
                severity="warning",
                title=f"Message sent to DLQ after {retry_count} retries",
                details={
                    "topic": original_topic,
                    "error": str(error)
                }
            )

    def _determine_reason(self, error: Exception, retry_count: int) -> DLQReason:
        if retry_count >= self.MAX_RETRIES:
            return DLQReason.MAX_RETRIES
        if isinstance(error, ValidationError):
            return DLQReason.VALIDATION_ERROR
        if isinstance(error, TimeoutError):
            return DLQReason.TIMEOUT
        return DLQReason.PROCESSING_ERROR

    def process_dlq(self, handler: Callable, topic: str):
        """Process DLQ messages for retry or manual handling"""
        consumer = KafkaConsumer(
            f"{topic}.dlq",
            bootstrap_servers=config.KAFKA_BROKERS,
            group_id=f"{topic}-dlq-processor",
            auto_offset_reset="earliest"
        )

        for message in consumer:
            dlq_message = DeadLetterMessage(**json.loads(message.value))

            # Check if retriable
            if dlq_message.reason in [DLQReason.PROCESSING_ERROR, DLQReason.TIMEOUT]:
                if dlq_message.retry_count < self.MAX_RETRIES:
                    # Schedule retry with backoff
                    delay = self.RETRY_DELAYS[dlq_message.retry_count]
                    scheduler.schedule(
                        self._retry_message,
                        args=[dlq_message],
                        delay_seconds=delay
                    )
                    continue

            # Non-retriable or max retries - needs manual intervention
            self._create_incident(dlq_message)

    def _retry_message(self, dlq_message: DeadLetterMessage):
        """Retry a DLQ message"""
        try:
            # Republish to original topic
            self.producer.publish(
                topic=dlq_message.original_topic,
                value={
                    **dlq_message.original_message,
                    "_retry_count": dlq_message.retry_count + 1
                }
            )
        except Exception as e:
            # If retry fails, send back to DLQ with incremented count
            self.send_to_dlq(
                original_message=dlq_message.original_message,
                original_topic=dlq_message.original_topic,
                partition=dlq_message.original_partition,
                offset=dlq_message.original_offset,
                error=e,
                retry_count=dlq_message.retry_count + 1
            )

    def _create_incident(self, dlq_message: DeadLetterMessage):
        """Create incident for messages requiring manual intervention"""
        incident_service.create(
            title=f"DLQ message requires attention: {dlq_message.original_topic}",
            severity="medium",
            details={
                "topic": dlq_message.original_topic,
                "error": dlq_message.error_message,
                "retry_count": dlq_message.retry_count,
                "message_preview": str(dlq_message.original_message)[:500]
            }
        )
            ''',
        }

    # =========================================================================
    # EVENT ORDERING
    # =========================================================================

    @staticmethod
    def event_ordering() -> Dict[str, Any]:
        """Event ordering and sequencing patterns"""
        return {
            "partition_key": '''
# GOOD: Use partition key for ordering within an entity
class OrderEventPublisher:
    """Publish order events with guaranteed ordering per order"""

    def publish(self, order_id: str, event: dict):
        # Use order_id as partition key
        # All events for same order go to same partition
        # Kafka guarantees ordering within a partition
        kafka.publish(
            topic="order-events",
            key=order_id,  # Partition key
            value=event
        )

# Events for order-123 always go to same partition
publisher.publish("order-123", {"type": "OrderCreated", ...})
publisher.publish("order-123", {"type": "OrderPaid", ...})
publisher.publish("order-123", {"type": "OrderShipped", ...})
# Consumer receives them in order
            ''',
            "sequence_numbers": '''
# GOOD: Use sequence numbers for ordering verification
from dataclasses import dataclass

@dataclass
class SequencedEvent:
    stream_id: str
    sequence_number: int  # Monotonically increasing per stream
    event_type: str
    payload: dict
    timestamp: datetime

class SequenceTracker:
    """Track and verify event sequences"""

    def __init__(self):
        self.last_seen: dict[str, int] = {}

    def process(self, event: SequencedEvent) -> bool:
        """Process event, detecting gaps and out-of-order delivery"""
        expected = self.last_seen.get(event.stream_id, 0) + 1

        if event.sequence_number < expected:
            # Duplicate or out-of-order
            logger.warning(
                "Out-of-order event",
                stream_id=event.stream_id,
                expected=expected,
                received=event.sequence_number
            )
            return False  # Skip duplicate

        if event.sequence_number > expected:
            # Gap detected - events missing
            logger.error(
                "Event gap detected",
                stream_id=event.stream_id,
                expected=expected,
                received=event.sequence_number,
                gap=event.sequence_number - expected
            )
            # Request missing events or wait for them
            self._handle_gap(event.stream_id, expected, event.sequence_number)
            return False

        # Expected sequence
        self.last_seen[event.stream_id] = event.sequence_number
        return True
            ''',
            "causal_ordering": '''
# GOOD: Causal ordering with vector clocks
from dataclasses import dataclass, field

@dataclass
class VectorClock:
    """Vector clock for causal ordering"""
    clocks: dict[str, int] = field(default_factory=dict)

    def increment(self, node_id: str):
        """Increment clock for local node"""
        self.clocks[node_id] = self.clocks.get(node_id, 0) + 1

    def merge(self, other: 'VectorClock'):
        """Merge with another vector clock (take max of each)"""
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        for node in all_nodes:
            self.clocks[node] = max(
                self.clocks.get(node, 0),
                other.clocks.get(node, 0)
            )

    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this clock happens-before other"""
        at_least_one_less = False
        for node in set(self.clocks.keys()) | set(other.clocks.keys()):
            self_time = self.clocks.get(node, 0)
            other_time = other.clocks.get(node, 0)

            if self_time > other_time:
                return False  # Not happens-before
            if self_time < other_time:
                at_least_one_less = True

        return at_least_one_less

@dataclass
class CausalEvent:
    event_id: str
    event_type: str
    payload: dict
    vector_clock: VectorClock
    causation_id: str | None  # Event that caused this event

class CausalEventProcessor:
    """Process events respecting causal order"""

    def __init__(self):
        self.pending: dict[str, list[CausalEvent]] = {}
        self.delivered_clocks: dict[str, VectorClock] = {}

    def receive(self, event: CausalEvent):
        """Receive event and deliver when causally ready"""
        stream_id = event.payload.get("aggregate_id")
        delivered_clock = self.delivered_clocks.get(stream_id, VectorClock())

        # Check if causally ready (all causal dependencies delivered)
        if self._is_deliverable(event, delivered_clock):
            self._deliver(event)
            self._check_pending(stream_id)
        else:
            # Buffer until dependencies arrive
            if stream_id not in self.pending:
                self.pending[stream_id] = []
            self.pending[stream_id].append(event)

    def _is_deliverable(self, event: CausalEvent, delivered_clock: VectorClock) -> bool:
        """Check if all causal dependencies have been delivered"""
        return event.vector_clock.happens_before(delivered_clock) or \\
               event.vector_clock == delivered_clock
            ''',
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        pattern_violated: str,
        current_design: str,
        improved_design: str,
    ) -> EventDrivenFinding:
        """Generate a structured finding"""
        return EventDrivenFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            pattern_violated=pattern_violated,
            current_design=current_design,
            improved_design=improved_design,
            tools=self.get_tool_recommendations(),
            remediation={
                "effort": "HIGH" if severity in ["CRITICAL", "HIGH"] else "MEDIUM",
                "priority": severity
            }
        )

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended tools for event-driven architecture"""
        return [
            {
                "name": "EventStoreDB",
                "command": "docker run --rm -p 2113:2113 eventstore/eventstore",
                "description": "Purpose-built event store database"
            },
            {
                "name": "Apache Kafka",
                "command": "docker compose up kafka zookeeper",
                "description": "Distributed event streaming platform"
            },
            {
                "name": "Debezium",
                "command": "docker run debezium/connect",
                "description": "Change data capture for databases"
            },
            {
                "name": "Kafka UI",
                "command": "docker run -p 8080:8080 provectuslabs/kafka-ui",
                "description": "Web UI for Kafka cluster management"
            },
            {
                "name": "Schema Registry",
                "command": "docker run confluentinc/cp-schema-registry",
                "description": "Schema evolution for event contracts"
            },
            {
                "name": "ksqlDB",
                "command": "docker run confluentinc/ksqldb-server",
                "description": "SQL interface for stream processing"
            },
        ]


def create_enhanced_event_driven_assistant():
    """Factory function to create Enhanced Event-Driven Architecture Assistant"""
    return {
        "name": "Enhanced Event-Driven Architecture Advisor",
        "version": "2.0.0",
        "system_prompt": """You are an expert event-driven architecture advisor with comprehensive
knowledge of building scalable, resilient event-driven systems. Your expertise covers:

EVENT SOURCING:
- Event store design and implementation
- Projections and read model materialization
- Snapshotting for performance optimization
- Event versioning and upcasting
- Temporal queries and event replay

CQRS (Command Query Responsibility Segregation):
- Command handling and validation
- Event publication and subscription
- Read model updates and eventual consistency
- Query optimization for read models

SAGA PATTERNS:
- Choreography vs orchestration trade-offs
- Compensating transactions for failure recovery
- State machine design for long-running processes
- Timeout and retry strategies

MESSAGE BROKERS:
- Apache Kafka: partitioning, consumer groups, exactly-once semantics
- RabbitMQ: exchanges, queues, dead letter handling
- AWS SQS/SNS, Azure Service Bus, Google Pub/Sub
- Producer reliability (acks, retries, idempotence)
- Consumer patterns (at-least-once, exactly-once)

RELIABILITY PATTERNS:
- Transactional outbox for reliable publishing
- Idempotency for message deduplication
- Dead letter queues for poison message handling
- Event ordering and sequence guarantees
- Causal consistency with vector clocks

INFRASTRUCTURE:
- Schema registries for contract evolution
- CDC (Change Data Capture) with Debezium
- Stream processing with Kafka Streams, ksqlDB
- Monitoring and observability for event flows

Analyze architectures and code for event-driven best practices.
Provide specific recommendations with implementation patterns.

Format findings with pattern references and severity levels.""",
        "assistant_class": EnhancedEventDrivenAssistant,
        "finding_model": EventDrivenFinding,
        "domain": "architecture",
        "subdomain": "event-driven",
        "tags": ["event-sourcing", "cqrs", "saga", "kafka", "distributed", "messaging"],
        "tools": EnhancedEventDrivenAssistant.get_tool_recommendations(),
        "capabilities": [
            "event_sourcing_review",
            "cqrs_analysis",
            "saga_pattern_design",
            "message_broker_optimization",
            "reliability_assessment",
            "schema_evolution_guidance"
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedEventDrivenAssistant()
    print(f"=== {assistant.name} v{assistant.version} ===\n")
    print(f"Standards: {', '.join(assistant.standards)}\n")

    # Demonstrate event sourcing
    print("--- Event Sourcing ---")
    es = assistant.event_sourcing()
    print("Event sourcing stores state changes as sequence of events")
    print("Key concepts: Event store, projections, snapshotting")

    # Demonstrate CQRS
    print("\n--- CQRS ---")
    cqrs = assistant.cqrs()
    print("CQRS separates read and write models for independent scaling")

    # Demonstrate saga patterns
    print("\n--- Saga Patterns ---")
    sagas = assistant.saga_patterns()
    print("Choreography: Services coordinate via events")
    print("Orchestration: Central coordinator manages saga")

    # Show event versioning
    print("\n--- Event Versioning ---")
    versioning = assistant.event_versioning()
    print("Handle schema evolution with upcasting")

    # Show Kafka patterns
    print("\n--- Kafka Patterns ---")
    kafka = assistant.kafka_patterns()
    print("Producer: acks=all, idempotence, transactions")
    print("Consumer: manual commit, at-least-once delivery")

    # Show outbox pattern
    print("\n--- Transactional Outbox ---")
    outbox = assistant.outbox_pattern()
    print("Guarantee atomic database updates and message publishing")

    # Show idempotency patterns
    print("\n--- Idempotency Patterns ---")
    idempotency = assistant.idempotency_patterns()
    print("Ensure messages can be safely reprocessed")

    # Show DLQ patterns
    print("\n--- Dead Letter Queue ---")
    dlq = assistant.dead_letter_queue()
    print("Handle messages that cannot be processed")

    # Show ordering patterns
    print("\n--- Event Ordering ---")
    ordering = assistant.event_ordering()
    print("Partition keys, sequence numbers, causal ordering")

    # Generate sample finding
    print("\n--- Sample Finding ---")
    finding = assistant.generate_finding(
        finding_id="EDA-001",
        title="Missing Idempotency in Event Consumer",
        severity="HIGH",
        category="Reliability",
        pattern_violated="Idempotent Consumer",
        current_design="Consumer processes messages without deduplication check",
        improved_design="Implement idempotent consumer with message ID tracking"
    )
    print(f"ID: {finding.finding_id}")
    print(f"Title: {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Pattern Violated: {finding.pattern_violated}")
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
    config = create_enhanced_event_driven_assistant()
    print(f"Name: {config['name']}")
    print(f"Version: {config['version']}")
    print(f"Domain: {config['domain']}")
    print(f"Tags: {', '.join(config['tags'])}")
    print(f"Capabilities: {', '.join(config['capabilities'][:3])}...")
