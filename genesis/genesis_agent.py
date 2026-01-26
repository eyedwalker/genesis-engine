"""
Genesis Agent - Meta-Prompting Factory Creator.

This is the heart of the Genesis Engine. The Genesis Agent analyzes
business domain descriptions and generates complete factory configurations,
including:
- Domain context (CONTEXT.md)
- Agent system prompts
- Knowledge base seed queries
- Technology stack recommendations

This is "Recursive Meta-Prompting" - an AI that writes prompts for other AIs.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import os


# ============================================================================
# Dependencies
# ============================================================================

@dataclass
class GenesisDeps:
    """
    Dependencies for the Genesis Agent.

    Unlike factory deps, Genesis needs access to:
    - Web search for domain research
    - Template repository for patterns
    - Milvus for storing generated knowledge
    """
    web_search_client: Optional[Any] = None
    template_repository: Optional[str] = None
    milvus_client: Optional[Any] = None
    workspace_root: str = "/tmp/genesis"


# ============================================================================
# Output Models
# ============================================================================

class DomainVocabulary(BaseModel):
    """Domain-specific vocabulary definitions."""
    terms: Dict[str, str] = Field(
        description="Dictionary of domain terms and their definitions"
    )


class TechStackRecommendation(BaseModel):
    """Recommended technology stack for the domain."""
    language: str = Field(description="Primary programming language")
    framework: str = Field(description="Web/API framework")
    database: str = Field(description="Database technology")
    orm: str = Field(description="ORM/data layer")
    testing: str = Field(description="Testing framework")
    additional: List[str] = Field(
        default=[],
        description="Additional technologies (e.g., 'Redis', 'Kafka')"
    )
    rationale: str = Field(description="Why this stack was chosen")


class AgentPromptSpec(BaseModel):
    """Specification for an agent's system prompt."""
    agent_name: str = Field(description="Name of the agent (architect, builder, qa)")
    model: str = Field(description="Recommended model (e.g., 'anthropic:claude-sonnet-4-5')")
    system_prompt: str = Field(description="Complete system prompt for this agent")
    tools_needed: List[str] = Field(description="Tools this agent should have access to")


class KnowledgeBaseSeed(BaseModel):
    """Seed queries for populating the factory's knowledge base."""
    queries: List[str] = Field(
        description="Search queries to fetch domain documentation"
    )
    sources: List[str] = Field(
        description="Recommended documentation URLs"
    )


class FactoryBlueprint(BaseModel):
    """
    Complete blueprint for a new software factory.

    This is what Genesis produces - everything needed to instantiate
    a fully functional, domain-specific software factory.
    """
    factory_name: str = Field(description="Name for this factory")
    domain_name: str = Field(description="Business domain (e.g., 'logistics', 'fintech')")

    # Domain Context (becomes CONTEXT.md)
    mission_statement: str = Field(description="What this factory builds")
    vocabulary: DomainVocabulary = Field(description="Domain-specific terms")
    standards: List[str] = Field(description="Applicable industry standards")
    constraints: List[str] = Field(description="Business/regulatory constraints")

    # Technical Specifications
    tech_stack: TechStackRecommendation = Field(description="Technology choices")

    # Agent Configurations
    architect_spec: AgentPromptSpec = Field(description="Architect agent configuration")
    builder_spec: AgentPromptSpec = Field(description="Builder agent configuration")
    qa_spec: AgentPromptSpec = Field(description="QA agent configuration")

    # Knowledge Base
    knowledge_seed: KnowledgeBaseSeed = Field(description="Knowledge base population")

    # Code Patterns
    example_models: str = Field(description="Example Pydantic/SQLModel code")
    example_service: str = Field(description="Example service layer code")
    example_api: str = Field(description="Example API endpoint code")
    example_test: str = Field(description="Example test code")


# ============================================================================
# Genesis System Prompt
# ============================================================================

GENESIS_SYSTEM_PROMPT = """
# The Genesis Engine: Factory Instantiation Protocol

You are the **Genesis Engine**, a meta-architect AI responsible for designing
autonomous software factories. You do not write application code; you write
the instructions and configurations that other agents will use to write
application code.

## Your Mission

Transform business domain descriptions into complete software factory
configurations. You produce "Factory Blueprints" that enable autonomous
code generation for any domain.

## Input

A high-level description of a **Target Business Domain**, such as:
- "A logistics company specializing in cold-chain storage with IoT integration"
- "A fintech startup building payment processing APIs"
- "A legal tech platform for contract management"

## Output Requirements

Generate a **FactoryBlueprint** containing:

### 1. Domain Context
- **Mission Statement**: What this factory produces
- **Vocabulary**: Domain-specific terms and definitions
- **Standards**: Relevant ISO, industry, or regulatory standards
- **Constraints**: Business rules and limitations

### 2. Technology Stack
Select optimal technologies for the domain:
- For real-time IoT: Asyncio, MQTT, Time-Series DB
- For financial: Strong typing, audit logging, PostgreSQL
- For healthcare: FHIR compliance, HIPAA logging rules

### 3. Agent Prompts
Draft system prompts for each agent:
- **Architect**: How to design solutions for this domain
- **Builder**: Coding standards and patterns for this domain
- **QA**: Testing requirements specific to this domain

### 4. Knowledge Base Seeds
Generate 10+ search queries to populate the factory's RAG memory:
- Documentation sources
- API specifications
- Best practices guides

### 5. Code Examples
Provide template code showing:
- Model definitions (Pydantic/SQLModel style)
- Service layer patterns
- API endpoint structure
- Test structure

## Meta-Rules

1. **Structure over Content**: Focus on defining constraints, not writing application code
2. **Type Safety**: Enforce strict typing in all generated instructions
3. **Self-Healing**: Include mandates for test-driven development
4. **Domain Expertise**: Extract domain knowledge from the description
5. **Production Ready**: Generated factories must produce deployable code

## Example Interaction

**Input**: "Build a factory for a High-Frequency Trading (HFT) platform."

**Output Thought Process**:
1. **Analyze**: HFT requires microsecond latency. Python may be too slow for core engine.
2. **Decision**: Factory should output Rust for matching engine, Python for dashboard/analytics.
3. **Context**: Define "Order Book", "Matching Algorithm", "FIX Protocol".
4. **Prompt Generation**: Instruct Builder to prioritize memory safety and zero-copy networking.
5. **Standards**: Reference FIX Protocol 4.4, SEC Rule 15c3-5.

**Output**: Complete FactoryBlueprint with all components.

## Remember

You are not writing the software. You are writing the instructions that will
enable an autonomous system to write the software. Think meta. Think constraints.
Think structure.

The quality of the factory you design determines the quality of all software
it will ever produce.
"""


# ============================================================================
# Genesis Agent Definition
# ============================================================================

genesis_agent = Agent(
    'anthropic:claude-opus-4-5',  # Using Opus for meta-reasoning
    deps_type=GenesisDeps,
    system_prompt=GENESIS_SYSTEM_PROMPT,
)


# ============================================================================
# Tools
# ============================================================================

@genesis_agent.tool
async def search_domain_info(
    ctx: RunContext[GenesisDeps],
    query: str
) -> str:
    """
    Search for domain-specific information.

    Use this to research industry standards, best practices, and
    technical requirements for the target domain.

    Args:
        query: Search query for domain research

    Returns:
        Relevant information found
    """
    # In production, this would use a web search API
    # For now, return helpful prompts
    return f"""
Search results for: "{query}"

Note: In production, this would fetch real documentation.
For now, use your knowledge to reason about:
- Industry standards applicable to this domain
- Common technical requirements
- Best practices for this type of software
- Regulatory or compliance requirements

Consider what documentation sources would be most valuable
and include them in your knowledge_seed recommendations.
"""


@genesis_agent.tool
async def get_template_patterns(
    ctx: RunContext[GenesisDeps],
    pattern_type: str
) -> str:
    """
    Retrieve template patterns for code generation.

    Args:
        pattern_type: Type of pattern (model, service, api, test)

    Returns:
        Template code pattern
    """
    patterns = {
        "model": '''
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StatusEnum(str, Enum):
    """Status values for the resource."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class ResourceBase(BaseModel):
    """Base model for the resource."""
    name: str = Field(description="Resource name")
    status: StatusEnum = Field(default=StatusEnum.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Resource(SQLModel, ResourceBase, table=True):
    """Database model for the resource."""
    __tablename__ = "resources"
    id: Optional[int] = SQLField(default=None, primary_key=True)
''',
        "service": '''
from typing import Optional, List
from sqlmodel import Session, select

async def create_resource(
    session: Session,
    data: ResourceCreate
) -> Resource:
    """
    Create a new resource.

    Args:
        session: Database session
        data: Resource creation data

    Returns:
        Created resource

    Raises:
        ValidationError: If data is invalid
    """
    resource = Resource(**data.model_dump())
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource

async def get_resource(
    session: Session,
    resource_id: int
) -> Optional[Resource]:
    """Get resource by ID."""
    return session.get(Resource, resource_id)
''',
        "api": '''
from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(prefix="/api/v1/resources", tags=["resources"])

@router.post("/", response_model=ResourceResponse)
async def create_resource_endpoint(
    data: ResourceCreate,
    session: Session = Depends(get_session)
) -> ResourceResponse:
    """
    Create a new resource.

    Args:
        data: Resource creation payload

    Returns:
        Created resource
    """
    resource = await create_resource(session, data)
    return ResourceResponse.model_validate(resource)

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource_endpoint(
    resource_id: int,
    session: Session = Depends(get_session)
) -> ResourceResponse:
    """Get resource by ID."""
    resource = await get_resource(session, resource_id)
    if not resource:
        raise HTTPException(404, "Resource not found")
    return ResourceResponse.model_validate(resource)
''',
        "test": '''
import pytest
from httpx import AsyncClient

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_resource(client: AsyncClient):
    """Test resource creation."""
    response = await client.post(
        "/api/v1/resources/",
        json={"name": "Test Resource"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Resource"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_get_resource_not_found(client: AsyncClient):
    """Test 404 for missing resource."""
    response = await client.get("/api/v1/resources/99999")
    assert response.status_code == 404
'''
    }
    return patterns.get(pattern_type, f"Unknown pattern type: {pattern_type}")


# ============================================================================
# Helper Functions
# ============================================================================

async def run_genesis(
    domain_description: str,
    deps: Optional[GenesisDeps] = None
) -> FactoryBlueprint:
    """
    Run the Genesis agent to create a factory blueprint.

    This is the main entry point for creating new factories.

    Args:
        domain_description: Description of the target business domain
        deps: Optional dependencies

    Returns:
        Complete FactoryBlueprint

    Example:
        blueprint = await run_genesis(
            "Cold-chain logistics with IoT temperature monitoring"
        )
        print(blueprint.factory_name)  # "cold_chain_logistics_factory"
    """
    if deps is None:
        deps = GenesisDeps()

    prompt = f"""
Analyze this business domain and create a complete Factory Blueprint:

## Domain Description
{domain_description}

## Your Task
1. Identify the core entities and relationships
2. Determine applicable industry standards
3. Recommend an optimal technology stack
4. Design agent prompts specialized for this domain
5. Generate knowledge base seed queries
6. Provide example code patterns

Output a complete FactoryBlueprint.
"""

    result = await genesis_agent.run(
        prompt,
        deps=deps,
        output_type=FactoryBlueprint
    )

    return result.output


def generate_context_md(blueprint: FactoryBlueprint) -> str:
    """
    Generate CONTEXT.md from a FactoryBlueprint.

    Args:
        blueprint: Factory blueprint from Genesis

    Returns:
        Markdown content for CONTEXT.md
    """
    vocab_section = "\n".join(
        f"- **{term}**: {definition}"
        for term, definition in blueprint.vocabulary.terms.items()
    )

    standards_section = "\n".join(f"- {std}" for std in blueprint.standards)
    constraints_section = "\n".join(f"- {c}" for c in blueprint.constraints)

    return f"""# {blueprint.factory_name}: System Context & Standards

## 1. Mission Statement

{blueprint.mission_statement}

## 2. Domain Vocabulary

{vocab_section}

## 3. Applicable Standards

{standards_section}

## 4. Business Constraints

{constraints_section}

## 5. Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | {blueprint.tech_stack.language} | {blueprint.tech_stack.rationale} |
| Framework | {blueprint.tech_stack.framework} | - |
| Database | {blueprint.tech_stack.database} | - |
| ORM | {blueprint.tech_stack.orm} | - |
| Testing | {blueprint.tech_stack.testing} | - |

## 6. Code Quality Standards

- All code must pass linting (ruff)
- All code must pass type checking (mypy --strict)
- All public functions must have docstrings
- Minimum 80% test coverage required

## 7. Agent Roles

| Agent | Model | Responsibility |
|-------|-------|----------------|
| Architect | {blueprint.architect_spec.model} | Design solutions |
| Builder | {blueprint.builder_spec.model} | Implement code |
| QA | {blueprint.qa_spec.model} | Validate quality |

## 8. Self-Healing Loop

Maximum 5 iterations before human escalation.

---
*Generated by Genesis Engine*
"""


__all__ = [
    "genesis_agent",
    "run_genesis",
    "FactoryBlueprint",
    "GenesisDeps",
    "generate_context_md",
]
