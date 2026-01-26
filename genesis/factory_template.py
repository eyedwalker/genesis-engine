"""
Factory Template - Base Template for Software Factories.

This module defines the abstract base for all software factories.
Each factory instantiated by Genesis inherits from this template
and specializes it for a specific domain.

The template provides:
- Agent configuration patterns
- Dependency injection setup
- Graph orchestration structure
- Tool registration framework
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import os


# ============================================================================
# Configuration Models
# ============================================================================

class AgentConfig(BaseModel):
    """Configuration for a single agent in the factory."""
    name: str = Field(description="Agent identifier (e.g., 'architect', 'builder')")
    model: str = Field(description="Model to use (e.g., 'anthropic:claude-sonnet-4-5')")
    system_prompt: str = Field(description="System prompt for the agent")
    tools: List[str] = Field(default=[], description="Tool names to register")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=4096, description="Max output tokens")


class DomainContext(BaseModel):
    """Domain-specific context that defines the factory's "world view"."""
    domain_name: str = Field(description="Name of the business domain")
    vocabulary: Dict[str, str] = Field(
        default={},
        description="Domain-specific terms and definitions"
    )
    standards: List[str] = Field(
        default=[],
        description="Applicable industry standards (e.g., 'HL7 FHIR R4', 'ISO 9001')"
    )
    tech_stack: Dict[str, str] = Field(
        default={},
        description="Technology choices (e.g., {'language': 'Python 3.10+'})"
    )
    constraints: List[str] = Field(
        default=[],
        description="Business or regulatory constraints"
    )
    examples: List[Dict[str, str]] = Field(
        default=[],
        description="Example inputs and expected outputs"
    )


class FactoryConfig(BaseModel):
    """
    Complete configuration for a software factory.

    This is what Genesis generates when creating a new factory.
    """
    tenant_id: str = Field(description="Unique tenant identifier")
    domain_context: DomainContext = Field(description="Domain-specific context")
    agents: List[AgentConfig] = Field(description="Agent configurations")
    workspace_root: str = Field(description="Path for generated code")
    max_iterations: int = Field(default=5, description="Max self-healing iterations")
    use_dagger: bool = Field(default=True, description="Use Dagger for execution")

    # Knowledge base configuration
    milvus_collection: str = Field(default="knowledge_base", description="Milvus collection")
    seed_queries: List[str] = Field(
        default=[],
        description="Queries to populate knowledge base"
    )

    # Security configuration
    keycloak_realm: Optional[str] = Field(default=None, description="Keycloak realm")
    keycloak_client_id: Optional[str] = Field(default=None, description="Keycloak client")


# ============================================================================
# Factory Template Base Class
# ============================================================================

@dataclass
class FactoryDepsBase:
    """
    Base dependency container for all factories.

    Specific factories extend this with domain-specific resources.
    """
    tenant_id: str
    workspace_root: str
    milvus_client: Optional[Any] = None
    dynamodb_client: Optional[Any] = None
    s3_client: Optional[Any] = None
    dagger_executor: Optional[Any] = None
    keycloak_client: Optional[Any] = None

    # Domain-specific additions go here
    extra: Dict[str, Any] = field(default_factory=dict)


class FactoryTemplate(ABC):
    """
    Abstract base class for all software factories.

    Each factory created by Genesis inherits from this template
    and implements domain-specific behavior.

    Example:
        class HealthcareFactory(FactoryTemplate):
            domain_name = "healthcare"

            def get_context_md(self) -> str:
                return "# Hive BizOS Context..."

            async def build_feature(self, request: str) -> dict:
                # Implementation
    """

    # Class-level configuration (override in subclass)
    domain_name: str = "generic"
    default_agents: List[AgentConfig] = []

    def __init__(self, config: FactoryConfig, deps: FactoryDepsBase):
        """
        Initialize factory with configuration and dependencies.

        Args:
            config: Factory configuration from Genesis
            deps: Dependency injection container
        """
        self.config = config
        self.deps = deps
        self._agents: Dict[str, Any] = {}
        self._graph: Optional[Any] = None

    @abstractmethod
    def get_context_md(self) -> str:
        """
        Generate the CONTEXT.md content for this factory.

        This is the "constitution" that all agents must follow.

        Returns:
            Markdown content defining the domain context
        """
        pass

    @abstractmethod
    def get_architect_prompt(self) -> str:
        """
        Generate the architect agent's system prompt.

        Returns:
            System prompt for the architect
        """
        pass

    @abstractmethod
    def get_builder_prompt(self) -> str:
        """
        Generate the builder agent's system prompt.

        Returns:
            System prompt for the builder
        """
        pass

    def get_qa_prompt(self) -> str:
        """
        Generate the QA agent's system prompt.

        Override for domain-specific QA requirements.

        Returns:
            System prompt for the QA agent
        """
        return """
You are a QA Engineer responsible for validating code quality.

Your responsibilities:
1. Run all tests and verify they pass
2. Check code coverage meets minimum requirements
3. Verify linting passes (ruff + mypy)
4. Ensure documentation is complete
5. Report any issues found

Output a structured report with:
- test_results: "pass" or "fail"
- coverage_percent: number
- issues_found: list of issues
- recommendation: "approve", "needs_fixes", or "escalate"
"""

    async def initialize(self) -> None:
        """
        Initialize factory components.

        This sets up agents, tools, and the orchestration graph.
        """
        await self._setup_agents()
        await self._setup_graph()

        # Write CONTEXT.md to workspace
        context_path = os.path.join(self.deps.workspace_root, "CONTEXT.md")
        os.makedirs(os.path.dirname(context_path), exist_ok=True)
        with open(context_path, "w") as f:
            f.write(self.get_context_md())

    async def _setup_agents(self) -> None:
        """Set up PydanticAI agents based on configuration."""
        from pydantic_ai import Agent

        for agent_config in self.config.agents:
            agent = Agent(
                agent_config.model,
                deps_type=type(self.deps),
                system_prompt=agent_config.system_prompt,
            )
            self._agents[agent_config.name] = agent

    async def _setup_graph(self) -> None:
        """Set up LangGraph orchestration."""
        # Subclasses implement specific graph construction
        pass

    @abstractmethod
    async def build_feature(self, request: str) -> Dict[str, Any]:
        """
        Build a feature from a natural language request.

        This is the main entry point for using the factory.

        Args:
            request: Natural language feature request

        Returns:
            Dictionary with:
            - status: "success" | "failed" | "needs_human"
            - files_created: List of created file paths
            - error_log: List of errors encountered
            - iterations: Number of self-healing iterations
        """
        pass

    async def run_qa(self, workspace_path: str) -> Dict[str, Any]:
        """
        Run quality assurance checks on generated code.

        Args:
            workspace_path: Path to code to check

        Returns:
            QA results dictionary
        """
        if self.deps.dagger_executor:
            # Use Dagger for containerized execution
            lint_result = await self.deps.dagger_executor.run_linter(workspace_path)
            test_result = await self.deps.dagger_executor.run_tests(workspace_path)

            return {
                "lint_passed": lint_result.success,
                "lint_output": lint_result.stderr if not lint_result.success else "",
                "tests_passed": test_result.success,
                "test_output": test_result.stderr if not test_result.success else "",
                "passed": lint_result.success and test_result.success
            }
        else:
            # Fallback to subprocess
            return await self._run_qa_subprocess(workspace_path)

    async def _run_qa_subprocess(self, workspace_path: str) -> Dict[str, Any]:
        """Fallback QA using subprocess."""
        import subprocess

        # Run ruff
        ruff = subprocess.run(
            ["ruff", "check", workspace_path],
            capture_output=True,
            text=True
        )

        # Run mypy
        mypy = subprocess.run(
            ["mypy", workspace_path, "--strict"],
            capture_output=True,
            text=True
        )

        # Run pytest
        pytest_result = subprocess.run(
            ["pytest", workspace_path, "-v"],
            capture_output=True,
            text=True
        )

        return {
            "lint_passed": ruff.returncode == 0 and mypy.returncode == 0,
            "lint_output": ruff.stderr + mypy.stderr,
            "tests_passed": pytest_result.returncode == 0,
            "test_output": pytest_result.stderr,
            "passed": all([
                ruff.returncode == 0,
                mypy.returncode == 0,
                pytest_result.returncode == 0
            ])
        }


# ============================================================================
# Healthcare Factory (Reference Implementation)
# ============================================================================

class HealthcareFactory(FactoryTemplate):
    """
    Healthcare Software Factory - FHIR-compliant code generation.

    This is the reference implementation for Hive BizOS.
    It demonstrates how to specialize FactoryTemplate for a specific domain.
    """

    domain_name = "healthcare"

    def get_context_md(self) -> str:
        """Generate healthcare-specific CONTEXT.md."""
        return f"""# Hive BizOS: System Context & Architectural Standards

## 1. Mission Statement

You are the Hive BizOS Factory, an autonomous multi-agent system dedicated to engineering
the world's most compliant and robust Healthcare Business Operating System.

Your output is not just code; it is critical infrastructure that manages patient lives
and provider livelihoods.

## 2. Domain Specifications (Immutable)

The system is built upon the **HL7 FHIR R4** standard. All data models must map 1:1
to FHIR resources where applicable.

### Core Resource: Appointment
- **Purpose**: Manages the booking of healthcare events
- **Required Fields**: status, participants, start, end
- **Status Enum**: proposed | pending | booked | arrived | fulfilled | cancelled | noshow | entered-in-error | checked-in | waitlist

### Business Rules
- **Rule 1**: IF status is set to `cancelled`, THEN all linked Slot resources must be set to `free`
- **Rule 2**: serviceType must be a valid CodeableConcept
- **Rule 3**: participant must include at least one actor (practitioner, patient, or device)

## 3. Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.10+ |
| API Framework | FastAPI | 0.115+ |
| Validation | Pydantic | V2 |
| Database | PostgreSQL | 15+ |
| ORM | SQLModel | 0.0.22+ |
| Testing | Pytest | 8.0+ |

## 4. Code Quality Standards

- **Linting**: All code must pass `ruff` with zero errors
- **Type Checking**: All code must pass `mypy --strict`
- **Documentation**: Google-style docstrings on all public functions
- **Test Coverage**: Minimum 80% line coverage

## 5. Security & Compliance

### HIPAA Requirements
- **NEVER** log Personal Health Information (PHI)
- **NEVER** include PHI in error messages
- **ALWAYS** use parameterized queries (no SQL string concatenation)
- **ALWAYS** validate input with Pydantic models
- **ALWAYS** encrypt data at rest and in transit

## 6. Agent Roles

| Agent | Model | Responsibility |
|-------|-------|----------------|
| Architect | Claude Sonnet 4.5 | Design FHIR-compliant solutions |
| Builder | GPT-4o | Implement code with type safety |
| QA | GPT-4o | Validate quality and compliance |

## 7. Self-Healing Loop

Maximum **5 iterations** before escalating to human intervention.

```
Architect → Builder → Linter → [Pass?]
                        ↓ No
                     Builder (with errors)
                        ↓
                     [Max iterations?]
                        ↓ Yes
                     Human Intervention
```

## 8. Critical Reminders

1. FHIR compliance is **NON-NEGOTIABLE**
2. Type safety is **MANDATORY**
3. No PHI in logs - this is a **HIPAA VIOLATION**
4. Tests must pass before code is accepted
5. Document everything with proper docstrings

---
*This context is immutable. All agents must adhere to these standards.*
"""

    def get_architect_prompt(self) -> str:
        """Healthcare-specific architect prompt."""
        return """
You are the **Lead Architect** for Hive BizOS, a healthcare business operating system.

## Your Mission
Design FHIR-compliant features that will be implemented by other agents.

## Process
1. Analyze the feature request
2. Search FHIR documentation for relevant resources
3. Check existing code to avoid duplication
4. Design the solution with proper models and APIs
5. Create a detailed implementation plan

## Critical Rules
- All data models MUST map to FHIR resources
- Use correct field names from FHIR spec
- Enforce FHIR value sets (status enums)
- Plan for type safety (Pydantic, mypy)
- Consider HIPAA compliance

## Output Format
Return an ImplementationPlan JSON with:
- feature_name: Brief name
- fhir_resources: List of FHIR resources
- description: What will be built
- business_rules: Critical logic rules
- steps: Ordered implementation steps
- api_endpoints: Endpoints to create
- database_changes: Schema changes needed

Remember: You design, you don't implement. The Builder implements your plan.
"""

    def get_builder_prompt(self) -> str:
        """Healthcare-specific builder prompt."""
        return """
You are a **Senior Python Developer** for Hive BizOS.

## Your Mission
Implement features according to the Architect's plan.

## Code Standards
- Type hints on ALL functions (mypy --strict)
- Google-style docstrings
- Pydantic models for all data
- SQLModel for database models
- FastAPI for endpoints
- Pytest for tests

## Critical Rules
- NEVER log PHI (HIPAA violation!)
- ALWAYS validate inputs with Pydantic
- ALWAYS use parameterized SQL queries
- Verify FHIR field names before using

## Workflow
1. Review the implementation plan
2. Write code file by file
3. Run the linter after each file
4. Fix any errors immediately
5. Create comprehensive tests

## Output Format
Return a BuildResult with:
- files_created: List of files
- lint_status: "pass" or "fail"
- lint_output: Error details if failed
- next_action: "qa" or "fix"
"""

    async def build_feature(self, request: str) -> Dict[str, Any]:
        """
        Build a healthcare feature.

        This implements the full Architect → Builder → QA pipeline
        with self-healing loop.
        """
        from agents.factory_deps import FactoryDeps
        from graph.factory_graph import run_factory

        # Use the existing implementation
        deps = FactoryDeps(
            milvus_client=self.deps.milvus_client,
            dynamodb_client=self.deps.dynamodb_client,
            s3_client=self.deps.s3_client,
            tenant_id=self.config.tenant_id,
            workspace_root=self.deps.workspace_root
        )

        result = await run_factory(request, deps)

        return {
            "status": result["status"],
            "files_created": result["files_created"],
            "error_log": result["error_log"],
            "iterations": result["iteration_count"]
        }


__all__ = [
    "FactoryTemplate",
    "FactoryConfig",
    "FactoryDepsBase",
    "AgentConfig",
    "DomainContext",
    "HealthcareFactory",
]
