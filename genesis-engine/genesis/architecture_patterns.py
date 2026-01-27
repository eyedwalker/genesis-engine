"""
Architecture Patterns for Factory Code Generation.

Defines structural patterns including Volatility-Based Decomposition (VBD).
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


# ============================================================================
# Architecture Pattern Types
# ============================================================================

class ArchitecturePattern(str, Enum):
    """Supported architecture patterns."""
    VBD = "vbd"                          # Volatility-Based Decomposition
    LAYERED = "layered"                  # Traditional N-tier (Controller → Service → Repository)
    CLEAN = "clean"                      # Clean Architecture (Entities → Use Cases → Adapters)
    HEXAGONAL = "hexagonal"              # Ports & Adapters
    CQRS = "cqrs"                        # Command Query Responsibility Segregation
    EVENT_DRIVEN = "event_driven"        # Event-driven microservices


# ============================================================================
# Volatility-Based Decomposition (VBD)
# ============================================================================

class VBDLayer(str, Enum):
    """VBD architectural layers by volatility (rate of change)."""
    ENGINE = "engine"          # Core business rules (rarely changes)
    MANAGER = "manager"        # Workflow orchestration (moderate changes)
    ADAPTER = "adapter"        # External integrations (frequent changes)
    DTO = "dto"               # Data Transfer Objects (structural changes)
    INTERFACE = "interface"    # Public API contracts (infrequent changes)


class VBDArchitectureSpec(BaseModel):
    """Volatility-Based Decomposition architecture specification."""

    pattern: ArchitecturePattern = Field(
        default=ArchitecturePattern.VBD,
        description="Architecture pattern"
    )

    # Layer Definitions
    layers: List[VBDLayer] = Field(
        default_factory=lambda: [
            VBDLayer.DTO,
            VBDLayer.INTERFACE,
            VBDLayer.ENGINE,
            VBDLayer.MANAGER,
            VBDLayer.ADAPTER,
        ],
        description="Architectural layers in dependency order"
    )

    # Engine Layer (Lowest Volatility)
    engine_responsibilities: List[str] = Field(
        default_factory=lambda: [
            "Core business logic and rules",
            "Domain calculations and algorithms",
            "Pure functions (no side effects)",
            "Framework-agnostic code",
            "Rarely changes (high stability)",
        ],
        description="What engines are responsible for"
    )

    engine_naming: str = Field(
        default="{domain}Engine",
        description="Naming convention for engines (e.g., PricingEngine, InventoryEngine)"
    )

    engine_examples: List[str] = Field(
        default_factory=lambda: [
            "PricingEngine - Calculate prices, discounts, taxes",
            "ValidationEngine - Business rule validation",
            "CalculationEngine - Complex domain calculations",
            "RuleEngine - Apply business rules",
        ],
        description="Common engine types"
    )

    # Manager Layer (Medium Volatility)
    manager_responsibilities: List[str] = Field(
        default_factory=lambda: [
            "Orchestrate workflows across engines",
            "Coordinate multiple operations",
            "Handle transactions and state",
            "Map between DTOs and domain objects",
            "Changes moderately (workflow evolution)",
        ],
        description="What managers are responsible for"
    )

    manager_naming: str = Field(
        default="{domain}Manager",
        description="Naming convention for managers (e.g., OrderManager, UserManager)"
    )

    manager_examples: List[str] = Field(
        default_factory=lambda: [
            "OrderManager - Orchestrate order creation (validation → pricing → inventory)",
            "UserManager - User lifecycle (registration → verification → activation)",
            "PaymentManager - Payment workflow (authorize → capture → reconcile)",
            "ReportManager - Generate reports (aggregate → calculate → format)",
        ],
        description="Common manager types"
    )

    # Adapter Layer (High Volatility)
    adapter_responsibilities: List[str] = Field(
        default_factory=lambda: [
            "External system integration",
            "Database operations (repositories)",
            "Third-party API calls",
            "Message queue publishers/subscribers",
            "Changes frequently (external dependencies)",
        ],
        description="What adapters are responsible for"
    )

    adapter_naming: str = Field(
        default="{system}Adapter",
        description="Naming convention for adapters (e.g., StripeAdapter, PostgresAdapter)"
    )

    adapter_examples: List[str] = Field(
        default_factory=lambda: [
            "DatabaseAdapter - CRUD operations on database",
            "StripeAdapter - Stripe payment API integration",
            "EmailAdapter - SendGrid/SMTP email sending",
            "CacheAdapter - Redis/Memcached operations",
            "QueueAdapter - RabbitMQ/SQS message handling",
        ],
        description="Common adapter types"
    )

    # DTO Layer (Structural Volatility)
    dto_responsibilities: List[str] = Field(
        default_factory=lambda: [
            "Data structure definitions",
            "Input/output contracts",
            "Validation schemas (Pydantic)",
            "Serialization/deserialization",
            "Changes when data structure evolves",
        ],
        description="What DTOs are responsible for"
    )

    dto_naming: str = Field(
        default="{domain}DTO",
        description="Naming convention for DTOs (e.g., CreateOrderDTO, OrderResponseDTO)"
    )

    dto_examples: List[str] = Field(
        default_factory=lambda: [
            "CreateOrderDTO - Input for order creation",
            "OrderResponseDTO - Output for order queries",
            "UpdateUserDTO - Input for user updates",
            "PaymentResultDTO - Output from payment processing",
        ],
        description="Common DTO types"
    )

    # Interface Layer (Contract Volatility)
    interface_responsibilities: List[str] = Field(
        default_factory=lambda: [
            "Define public contracts (abstract base classes)",
            "Dependency injection interfaces",
            "Protocols for adapters",
            "Changes rarely (stable contracts)",
        ],
        description="What interfaces define"
    )

    interface_naming: str = Field(
        default="I{domain} or {domain}Protocol",
        description="Naming convention for interfaces"
    )

    interface_examples: List[str] = Field(
        default_factory=lambda: [
            "IPaymentAdapter - Contract for payment adapters",
            "IRepository - Contract for data access",
            "IMessageQueue - Contract for message queues",
            "ICache - Contract for caching systems",
        ],
        description="Common interface types"
    )

    # Directory Structure
    directory_structure: Dict[str, str] = Field(
        default_factory=lambda: {
            "dtos": "Data Transfer Objects",
            "interfaces": "Abstract contracts",
            "engines": "Core business logic",
            "managers": "Workflow orchestration",
            "adapters": "External integrations",
        },
        description="Directory structure for VBD"
    )

    # Dependency Rules
    dependency_rules: List[str] = Field(
        default_factory=lambda: [
            "DTOs depend on: nothing (pure data)",
            "Interfaces depend on: DTOs only",
            "Engines depend on: DTOs, Interfaces",
            "Managers depend on: DTOs, Interfaces, Engines",
            "Adapters depend on: DTOs, Interfaces",
            "API Layer depends on: DTOs, Managers",
        ],
        description="Dependency flow rules (prevent cyclic dependencies)"
    )

    # Testing Strategy
    testing_strategy: Dict[str, str] = Field(
        default_factory=lambda: {
            "engines": "Pure unit tests (no mocks, deterministic)",
            "managers": "Integration tests (mock adapters)",
            "adapters": "Integration tests (real/test external systems)",
            "dtos": "Schema validation tests",
        },
        description="Testing approach per layer"
    )


# ============================================================================
# Code Generation Templates
# ============================================================================

class VBDCodeTemplates:
    """Code templates for VBD components."""

    @staticmethod
    def engine_template() -> str:
        """Template for an Engine (core business logic)."""
        return '''"""
{domain} Engine - Core Business Logic.

Contains pure business rules and calculations.
No external dependencies, framework-agnostic.
"""

from typing import List, Optional
from decimal import Decimal
from ..dtos.{domain_lower}_dto import {domain}DTO, {domain}ResultDTO


class {domain}Engine:
    """
    Core business logic for {domain_description}.

    Volatility: LOW (rarely changes)
    Dependencies: DTOs only
    Testing: Pure unit tests (no mocks)
    """

    def __init__(self):
        """Initialize engine with business rules."""
        pass

    def calculate_{operation}(
        self,
        input_data: {domain}DTO
    ) -> {domain}ResultDTO:
        """
        Execute {operation} calculation.

        Pure function: Same input → Same output.
        No side effects, no external calls.

        Args:
            input_data: Validated input DTO

        Returns:
            Calculation result DTO

        Raises:
            ValueError: If business rules violated
        """
        # Validate business rules
        self._validate_business_rules(input_data)

        # Perform calculation
        result = self._compute_{operation}(input_data)

        return {domain}ResultDTO(
            result=result,
            valid=True,
            message="Calculation successful"
        )

    def _validate_business_rules(self, data: {domain}DTO) -> None:
        """Validate domain business rules."""
        # Example: Amount must be positive
        if data.amount <= 0:
            raise ValueError("Amount must be positive")

        # Example: Quantity within limits
        if data.quantity < 1 or data.quantity > 1000:
            raise ValueError("Quantity must be between 1 and 1000")

    def _compute_{operation}(self, data: {domain}DTO) -> Decimal:
        """
        Core calculation logic.

        Pure function - deterministic, no side effects.
        """
        # Business logic here
        base_amount = data.amount * data.quantity

        # Apply business rules
        result = base_amount * Decimal("1.0")

        return result
'''

    @staticmethod
    def manager_template() -> str:
        """Template for a Manager (orchestration)."""
        return '''"""
{domain} Manager - Workflow Orchestration.

Coordinates operations across engines and adapters.
Handles transactions and state management.
"""

from typing import Optional
from ..dtos.{domain_lower}_dto import Create{domain}DTO, {domain}ResponseDTO
from ..interfaces.i_repository import IRepository
from ..interfaces.i_event_publisher import IEventPublisher
from ..engines.{domain_lower}_engine import {domain}Engine


class {domain}Manager:
    """
    Orchestrates {domain} workflows.

    Volatility: MEDIUM (changes with workflow evolution)
    Dependencies: Engines, Adapters (via interfaces), DTOs
    Testing: Integration tests (mock adapters)
    """

    def __init__(
        self,
        engine: {domain}Engine,
        repository: IRepository,
        event_publisher: Optional[IEventPublisher] = None
    ):
        """
        Initialize manager with dependencies.

        Args:
            engine: Business logic engine
            repository: Data persistence adapter
            event_publisher: Event publishing adapter (optional)
        """
        self.engine = engine
        self.repository = repository
        self.event_publisher = event_publisher

    async def create_{domain_lower}(
        self,
        dto: Create{domain}DTO
    ) -> {domain}ResponseDTO:
        """
        Orchestrate {domain} creation workflow.

        Workflow:
        1. Validate via engine
        2. Calculate via engine
        3. Persist via repository
        4. Publish event (if configured)

        Args:
            dto: Creation request DTO

        Returns:
            Response DTO with created resource

        Raises:
            ValueError: If validation fails
            RuntimeError: If persistence fails
        """
        # Step 1: Validate business rules via engine
        validation_result = self.engine.validate_{domain_lower}(dto)
        if not validation_result.valid:
            raise ValueError(f"Validation failed: {{validation_result.message}}")

        # Step 2: Perform calculations via engine
        calculation_result = self.engine.calculate_{operation}(dto)

        # Step 3: Prepare for persistence
        entity_data = self._map_dto_to_entity(dto, calculation_result)

        # Step 4: Persist via repository (transactional)
        try:
            entity = await self.repository.create(entity_data)
        except Exception as e:
            raise RuntimeError(f"Failed to persist {domain_lower}: {{e}}")

        # Step 5: Publish event (fire-and-forget)
        if self.event_publisher:
            await self._publish_created_event(entity)

        # Step 6: Return response
        return self._map_entity_to_response(entity)

    async def update_{domain_lower}(
        self,
        id: str,
        dto: Update{domain}DTO
    ) -> {domain}ResponseDTO:
        """
        Orchestrate {domain} update workflow.

        Workflow:
        1. Fetch existing entity
        2. Validate update via engine
        3. Apply changes
        4. Persist via repository
        5. Publish event

        Args:
            id: Entity identifier
            dto: Update request DTO

        Returns:
            Updated entity response

        Raises:
            NotFoundError: If entity doesn't exist
            ValueError: If update violates business rules
        """
        # Step 1: Fetch existing
        existing = await self.repository.get_by_id(id)
        if not existing:
            raise NotFoundError(f"{domain} not found: {{id}}")

        # Step 2: Validate update
        validation_result = self.engine.validate_update(existing, dto)
        if not validation_result.valid:
            raise ValueError(f"Update invalid: {{validation_result.message}}")

        # Step 3: Apply changes
        updated_data = self._apply_update(existing, dto)

        # Step 4: Persist
        updated_entity = await self.repository.update(id, updated_data)

        # Step 5: Publish event
        if self.event_publisher:
            await self._publish_updated_event(updated_entity)

        return self._map_entity_to_response(updated_entity)

    def _map_dto_to_entity(self, dto, calculation_result):
        """Map DTO to entity for persistence."""
        return {{
            "field1": dto.field1,
            "field2": dto.field2,
            "calculated_value": calculation_result.result,
        }}

    def _map_entity_to_response(self, entity) -> {domain}ResponseDTO:
        """Map entity to response DTO."""
        return {domain}ResponseDTO(
            id=entity["id"],
            field1=entity["field1"],
            field2=entity["field2"],
            created_at=entity["created_at"],
        )

    async def _publish_created_event(self, entity):
        """Publish entity created event."""
        await self.event_publisher.publish(
            event_type="{domain}Created",
            payload={{"id": entity["id"]}}
        )

    async def _publish_updated_event(self, entity):
        """Publish entity updated event."""
        await self.event_publisher.publish(
            event_type="{domain}Updated",
            payload={{"id": entity["id"]}}
        )
'''

    @staticmethod
    def adapter_template() -> str:
        """Template for an Adapter (external integration)."""
        return '''"""
{system} Adapter - External System Integration.

Implements interface contract for {system} integration.
High volatility - changes with external API updates.
"""

from typing import List, Optional, Dict, Any
from ..interfaces.i_{interface_lower} import I{interface}
from ..dtos.{domain_lower}_dto import {domain}DTO


class {system}Adapter(I{interface}):
    """
    Adapter for {system} integration.

    Volatility: HIGH (changes with external system updates)
    Dependencies: Interface contract, DTOs
    Testing: Integration tests with test/mock {system}
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.{system_lower}.com",
        timeout: int = 30
    ):
        """
        Initialize {system} adapter.

        Args:
            api_key: {system} API key
            base_url: {system} API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._client = self._initialize_client()

    def _initialize_client(self):
        """Initialize HTTP client for {system}."""
        import httpx
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={{
                "Authorization": f"Bearer {{self.api_key}}",
                "Content-Type": "application/json",
            }},
            timeout=self.timeout,
        )

    async def create(self, data: {domain}DTO) -> Dict[str, Any]:
        """
        Create resource in {system}.

        Maps DTO to {system} API format and handles response.

        Args:
            data: Input DTO

        Returns:
            Created resource data

        Raises:
            RuntimeError: If {system} API call fails
        """
        try:
            # Map DTO to {system} format
            payload = self._map_dto_to_{system_lower}(data)

            # Call {system} API
            response = await self._client.post(
                "/{resource}",
                json=payload
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Map {system} response to standard format
            return self._map_{system_lower}_to_entity(result)

        except Exception as e:
            raise RuntimeError(f"{system} API error: {{e}}")

    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve resource from {system} by ID.

        Args:
            id: Resource identifier

        Returns:
            Resource data or None if not found
        """
        try:
            response = await self._client.get(f"/{resource}/{{id}}")

            if response.status_code == 404:
                return None

            response.raise_for_status()
            result = response.json()

            return self._map_{system_lower}_to_entity(result)

        except Exception as e:
            raise RuntimeError(f"{system} API error: {{e}}")

    async def update(
        self,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update resource in {system}.

        Args:
            id: Resource identifier
            data: Update data

        Returns:
            Updated resource data
        """
        try:
            payload = self._map_update_to_{system_lower}(data)

            response = await self._client.patch(
                f"/{resource}/{{id}}",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            return self._map_{system_lower}_to_entity(result)

        except Exception as e:
            raise RuntimeError(f"{system} API error: {{e}}")

    async def delete(self, id: str) -> bool:
        """
        Delete resource from {system}.

        Args:
            id: Resource identifier

        Returns:
            True if deleted successfully
        """
        try:
            response = await self._client.delete(f"/{resource}/{{id}}")
            response.raise_for_status()
            return True

        except Exception as e:
            raise RuntimeError(f"{system} API error: {{e}}")

    def _map_dto_to_{system_lower}(self, dto: {domain}DTO) -> Dict[str, Any]:
        """Map DTO to {system} API format."""
        return {{
            "{system_lower}_field1": dto.field1,
            "{system_lower}_field2": dto.field2,
        }}

    def _map_{system_lower}_to_entity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map {system} response to standard entity format."""
        return {{
            "id": data.get("id"),
            "field1": data.get("{system_lower}_field1"),
            "field2": data.get("{system_lower}_field2"),
            "created_at": data.get("created_at"),
        }}

    def _map_update_to_{system_lower}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map update data to {system} API format."""
        return {{
            "{system_lower}_field": data.get("field"),
        }}

    async def close(self):
        """Close adapter connections."""
        await self._client.aclose()
'''

    @staticmethod
    def dto_template() -> str:
        """Template for DTOs (data structures)."""
        return '''"""
{domain} DTOs - Data Transfer Objects.

Input/output data structures with validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal
from datetime import datetime


class Create{domain}DTO(BaseModel):
    """
    Input DTO for {domain} creation.

    Volatility: MEDIUM (changes with requirements)
    """

    field1: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Description of field1"
    )

    field2: int = Field(
        ...,
        ge=0,
        le=1000,
        description="Description of field2"
    )

    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Monetary amount"
    )

    optional_field: Optional[str] = Field(
        default=None,
        description="Optional field"
    )

    @validator("field1")
    def validate_field1(cls, v):
        """Custom validation for field1."""
        if not v.strip():
            raise ValueError("field1 cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {{
            "example": {{
                "field1": "Example value",
                "field2": 42,
                "amount": "99.99",
                "optional_field": "Optional"
            }}
        }}


class Update{domain}DTO(BaseModel):
    """Input DTO for {domain} updates."""

    field1: Optional[str] = Field(default=None, min_length=1, max_length=100)
    field2: Optional[int] = Field(default=None, ge=0, le=1000)
    amount: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)


class {domain}ResponseDTO(BaseModel):
    """Output DTO for {domain} queries."""

    id: str = Field(..., description="Unique identifier")
    field1: str
    field2: int
    amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {{
            "example": {{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "field1": "Example",
                "field2": 42,
                "amount": "99.99",
                "created_at": "2024-01-01T12:00:00Z"
            }}
        }}


class {domain}ResultDTO(BaseModel):
    """Output DTO for engine calculations."""

    result: Decimal
    valid: bool
    message: str
    metadata: Optional[dict] = None
'''

    @staticmethod
    def interface_template() -> str:
        """Template for Interfaces (contracts)."""
        return '''"""
{interface} Interface - Contract Definition.

Abstract base class defining contract for {interface_description}.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class I{interface}(ABC):
    """
    Interface for {interface_description}.

    Volatility: LOW (stable contract)
    Implementations: Can have multiple adapters
    """

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource.

        Args:
            data: Resource data

        Returns:
            Created resource with ID

        Raises:
            RuntimeError: If creation fails
        """
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve resource by ID.

        Args:
            id: Resource identifier

        Returns:
            Resource data or None if not found
        """
        pass

    @abstractmethod
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List resources with optional filters.

        Args:
            filters: Optional filter criteria
            limit: Max results to return
            offset: Number of results to skip

        Returns:
            List of resources
        """
        pass

    @abstractmethod
    async def update(
        self,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing resource.

        Args:
            id: Resource identifier
            data: Update data

        Returns:
            Updated resource

        Raises:
            NotFoundError: If resource doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Delete resource.

        Args:
            id: Resource identifier

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If resource doesn't exist
        """
        pass
'''


# ============================================================================
# Other Architecture Patterns (Brief)
# ============================================================================

class LayeredArchitectureSpec(BaseModel):
    """Traditional N-tier layered architecture."""
    pattern: ArchitecturePattern = ArchitecturePattern.LAYERED
    layers: List[str] = Field(
        default_factory=lambda: [
            "Presentation (API/Controllers)",
            "Business Logic (Services)",
            "Data Access (Repositories)",
            "Domain Models"
        ]
    )


class CleanArchitectureSpec(BaseModel):
    """Clean Architecture (Uncle Bob)."""
    pattern: ArchitecturePattern = ArchitecturePattern.CLEAN
    layers: List[str] = Field(
        default_factory=lambda: [
            "Entities (Domain Models)",
            "Use Cases (Application Logic)",
            "Interface Adapters (Controllers, Gateways)",
            "Frameworks & Drivers (External)"
        ]
    )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "ArchitecturePattern",
    "VBDLayer",
    "VBDArchitectureSpec",
    "VBDCodeTemplates",
    "LayeredArchitectureSpec",
    "CleanArchitectureSpec",
]
