"""
Genesis Engine - Factory-as-a-Service Orchestrator.

This is the main entry point for the Genesis Engine. It coordinates:
- Factory creation from domain descriptions
- Multi-tenant provisioning
- Factory lifecycle management
- Human escalation workflows

The Genesis Engine transforms business descriptions into fully autonomous
software factories. Each factory can then generate production code
for its specific domain.

Usage:
    engine = GenesisEngine.from_env()

    # Create a new factory
    factory = await engine.create_factory(
        tenant_id="apex_logistics",
        domain_description="Cold-chain logistics with IoT temperature monitoring"
    )

    # Build a feature
    result = await factory.build_feature("Add temperature alert system")

    # Handle escalation
    if result["status"] == "needs_human":
        snapshot = await engine.create_escalation(factory, result)
        print(f"Human help needed: {snapshot.vscode_url}")
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field
import os

from .genesis_agent import (
    run_genesis,
    FactoryBlueprint,
    GenesisDeps,
    generate_context_md
)
from .factory_template import (
    FactoryTemplate,
    FactoryConfig,
    FactoryDepsBase,
    HealthcareFactory,
    AgentConfig,
    DomainContext
)
from .tenant_manager import TenantManager, TenantConfig
from .devcontainer import DevContainerManager, EscalationSnapshot
from .dagger_executor import DaggerExecutor, create_executor


# ============================================================================
# Models
# ============================================================================

class FactoryStatus(BaseModel):
    """Status of a factory instance."""
    tenant_id: str
    factory_name: str
    domain: str
    status: str  # "active" | "provisioning" | "suspended" | "error"
    features_built: int
    credits_remaining: float
    last_activity: Optional[str] = None


class EngineMetrics(BaseModel):
    """Metrics for the Genesis Engine."""
    total_factories: int
    active_factories: int
    total_features_built: int
    pending_escalations: int


# ============================================================================
# Genesis Engine
# ============================================================================

@dataclass
class GenesisEngine:
    """
    The Genesis Engine - Meta-Platform for Software Factories.

    This is the highest-level abstraction in the system. It manages:
    - Factory creation from domain descriptions
    - Tenant provisioning and isolation
    - Factory lifecycle (create, pause, resume, delete)
    - Human escalation workflows
    - Usage metering and billing

    Architecture:
    ```
    GenesisEngine
        ├── Genesis Agent (meta-prompting)
        ├── Tenant Manager (Keycloak + Milvus)
        ├── DevContainer Manager (human-in-loop)
        └── Factory Instances
            ├── Healthcare Factory (Hive BizOS)
            ├── Logistics Factory (Apex)
            └── ... (any domain)
    ```

    Example:
        engine = GenesisEngine.from_env()

        # Create factory for new domain
        factory = await engine.create_factory(
            tenant_id="apex_logistics",
            domain_description="Cold-chain logistics with IoT integration"
        )

        # Or use pre-built healthcare factory
        healthcare = await engine.get_healthcare_factory(tenant_id="clinic_abc")

        # Build features
        result = await factory.build_feature("Add shipment tracking")
    """

    # Core components
    tenant_manager: TenantManager
    devcontainer_manager: DevContainerManager
    genesis_deps: GenesisDeps

    # Factory registry
    _factories: Dict[str, FactoryTemplate] = field(default_factory=dict)
    _blueprints: Dict[str, FactoryBlueprint] = field(default_factory=dict)

    # Configuration
    workspace_root: str = "/tmp/genesis"
    use_dagger: bool = True

    @classmethod
    def from_env(cls) -> "GenesisEngine":
        """
        Create Genesis Engine from environment variables.

        Required env vars:
        - WORKSPACE_ROOT: Base path for workspaces
        - AWS_REGION: AWS region for services

        Optional env vars:
        - MILVUS_URI: Milvus connection string
        - KEYCLOAK_URL: Keycloak server URL
        - USE_DAGGER: Whether to use Dagger (default: true)
        """
        workspace_root = os.getenv("WORKSPACE_ROOT", "/tmp/genesis")

        # Create managers
        tenant_manager = TenantManager.from_env()
        devcontainer_manager = DevContainerManager(
            snapshot_dir=os.path.join(workspace_root, "snapshots")
        )
        genesis_deps = GenesisDeps(workspace_root=workspace_root)

        return cls(
            tenant_manager=tenant_manager,
            devcontainer_manager=devcontainer_manager,
            genesis_deps=genesis_deps,
            workspace_root=workspace_root,
            use_dagger=os.getenv("USE_DAGGER", "true").lower() == "true"
        )

    async def create_factory(
        self,
        tenant_id: str,
        domain_description: str,
        display_name: Optional[str] = None,
        contact_email: str = "admin@example.com"
    ) -> FactoryTemplate:
        """
        Create a new factory from a domain description.

        This is the main entry point for Factory-as-a-Service.
        It uses the Genesis Agent to analyze the domain and generate
        a complete factory configuration.

        Args:
            tenant_id: Unique tenant identifier
            domain_description: Natural language description of the domain
            display_name: Human-readable name (defaults to tenant_id)
            contact_email: Contact email for the tenant

        Returns:
            Configured FactoryTemplate ready to build features

        Example:
            factory = await engine.create_factory(
                tenant_id="apex_logistics",
                domain_description="Cold-chain logistics with IoT sensors"
            )
            result = await factory.build_feature("Add temperature monitoring")
        """
        print(f"\n{'='*60}")
        print(f"GENESIS ENGINE: Creating factory for {tenant_id}")
        print(f"{'='*60}")
        print(f"Domain: {domain_description[:100]}...")

        # 1. Provision tenant resources
        print("\n1. Provisioning tenant resources...")
        provision_result = await self.tenant_manager.provision_tenant(
            tenant_id=tenant_id,
            display_name=display_name or tenant_id,
            domain=domain_description[:50],
            contact_email=contact_email
        )

        if not provision_result.success:
            raise RuntimeError(
                f"Failed to provision tenant: {provision_result.errors}"
            )

        print(f"   Created: {', '.join(provision_result.resources_created)}")

        # 2. Run Genesis Agent to create blueprint
        print("\n2. Running Genesis Agent (meta-prompting)...")
        blueprint = await run_genesis(
            domain_description=domain_description,
            deps=self.genesis_deps
        )

        print(f"   Factory: {blueprint.factory_name}")
        print(f"   Domain: {blueprint.domain_name}")
        print(f"   Tech Stack: {blueprint.tech_stack.language} / {blueprint.tech_stack.framework}")

        # 3. Store blueprint
        self._blueprints[tenant_id] = blueprint

        # 4. Create factory instance
        print("\n3. Creating factory instance...")
        factory = await self._instantiate_factory(
            tenant_id=tenant_id,
            blueprint=blueprint
        )

        # 5. Initialize factory
        await factory.initialize()

        # 6. Populate knowledge base
        print("\n4. Seeding knowledge base...")
        await self._seed_knowledge_base(tenant_id, blueprint)

        print(f"\n{'='*60}")
        print(f"GENESIS ENGINE: Factory ready!")
        print(f"{'='*60}")

        return factory

    async def get_healthcare_factory(
        self,
        tenant_id: str,
        contact_email: str = "admin@example.com"
    ) -> FactoryTemplate:
        """
        Get or create a healthcare factory (Hive BizOS).

        This is a convenience method for the pre-built healthcare domain.
        It uses the optimized Healthcare Factory template.

        Args:
            tenant_id: Unique tenant identifier
            contact_email: Contact email

        Returns:
            HealthcareFactory instance
        """
        # Check if already exists
        if tenant_id in self._factories:
            return self._factories[tenant_id]

        # Provision tenant
        provision_result = await self.tenant_manager.provision_tenant(
            tenant_id=tenant_id,
            display_name=f"Healthcare: {tenant_id}",
            domain="healthcare",
            contact_email=contact_email
        )

        # Get tenant config
        tenant_config = await self.tenant_manager.get_tenant(tenant_id)

        # Create factory config
        factory_config = FactoryConfig(
            tenant_id=tenant_id,
            domain_context=DomainContext(
                domain_name="healthcare",
                vocabulary={
                    "FHIR": "Fast Healthcare Interoperability Resources",
                    "Appointment": "A booking of a healthcare event"
                },
                standards=["HL7 FHIR R4", "HIPAA"],
                tech_stack={
                    "language": "Python 3.10+",
                    "framework": "FastAPI",
                    "database": "PostgreSQL 15+"
                }
            ),
            agents=[
                AgentConfig(
                    name="architect",
                    model="anthropic:claude-sonnet-4-5",
                    system_prompt="Healthcare architect prompt",
                    tools=["search_fhir_docs", "read_code_file", "list_workspace_files"]
                ),
                AgentConfig(
                    name="builder",
                    model="anthropic:claude-sonnet-4-5",
                    system_prompt="Healthcare builder prompt",
                    tools=["write_code_file", "read_code_file", "run_linter"]
                )
            ],
            workspace_root=tenant_config.workspace_path,
            use_dagger=self.use_dagger
        )

        # Create factory deps
        deps = FactoryDepsBase(
            tenant_id=tenant_id,
            workspace_root=tenant_config.workspace_path,
            milvus_client=self.tenant_manager.milvus_client,
            dynamodb_client=self.tenant_manager.dynamodb_client,
            s3_client=self.tenant_manager.s3_client,
            dagger_executor=create_executor(self.use_dagger) if self.use_dagger else None
        )

        # Create healthcare factory
        factory = HealthcareFactory(config=factory_config, deps=deps)
        await factory.initialize()

        # Store reference
        self._factories[tenant_id] = factory

        return factory

    async def _instantiate_factory(
        self,
        tenant_id: str,
        blueprint: FactoryBlueprint
    ) -> FactoryTemplate:
        """
        Instantiate a factory from a blueprint.

        Args:
            tenant_id: Tenant identifier
            blueprint: Factory blueprint from Genesis

        Returns:
            Configured factory instance
        """
        # Get tenant config
        tenant_config = await self.tenant_manager.get_tenant(tenant_id)

        # Create factory config from blueprint
        factory_config = FactoryConfig(
            tenant_id=tenant_id,
            domain_context=DomainContext(
                domain_name=blueprint.domain_name,
                vocabulary=blueprint.vocabulary.terms,
                standards=blueprint.standards,
                constraints=blueprint.constraints,
                tech_stack={
                    "language": blueprint.tech_stack.language,
                    "framework": blueprint.tech_stack.framework,
                    "database": blueprint.tech_stack.database
                }
            ),
            agents=[
                AgentConfig(
                    name="architect",
                    model=blueprint.architect_spec.model,
                    system_prompt=blueprint.architect_spec.system_prompt,
                    tools=blueprint.architect_spec.tools_needed
                ),
                AgentConfig(
                    name="builder",
                    model=blueprint.builder_spec.model,
                    system_prompt=blueprint.builder_spec.system_prompt,
                    tools=blueprint.builder_spec.tools_needed
                ),
                AgentConfig(
                    name="qa",
                    model=blueprint.qa_spec.model,
                    system_prompt=blueprint.qa_spec.system_prompt,
                    tools=blueprint.qa_spec.tools_needed
                )
            ],
            workspace_root=tenant_config.workspace_path,
            seed_queries=blueprint.knowledge_seed.queries,
            use_dagger=self.use_dagger
        )

        # Create factory deps
        deps = FactoryDepsBase(
            tenant_id=tenant_id,
            workspace_root=tenant_config.workspace_path,
            milvus_client=self.tenant_manager.milvus_client,
            dynamodb_client=self.tenant_manager.dynamodb_client,
            s3_client=self.tenant_manager.s3_client,
            dagger_executor=create_executor(self.use_dagger) if self.use_dagger else None
        )

        # Create dynamic factory class
        factory = DynamicFactory(
            config=factory_config,
            deps=deps,
            blueprint=blueprint
        )

        # Store reference
        self._factories[tenant_id] = factory

        return factory

    async def _seed_knowledge_base(
        self,
        tenant_id: str,
        blueprint: FactoryBlueprint
    ) -> None:
        """
        Seed the knowledge base with domain documentation.

        Args:
            tenant_id: Tenant identifier
            blueprint: Factory blueprint with seed queries
        """
        # In production, this would:
        # 1. Execute seed queries against web search
        # 2. Fetch documentation from sources
        # 3. Embed documents using OpenAI/Cohere
        # 4. Insert into Milvus partition

        # For now, log the queries that would be executed
        print(f"   Seed queries for {tenant_id}:")
        for query in blueprint.knowledge_seed.queries[:3]:
            print(f"     - {query}")
        if len(blueprint.knowledge_seed.queries) > 3:
            print(f"     ... and {len(blueprint.knowledge_seed.queries) - 3} more")

    async def create_escalation(
        self,
        factory: FactoryTemplate,
        build_result: Dict[str, Any]
    ) -> EscalationSnapshot:
        """
        Create an escalation when factory needs human help.

        Args:
            factory: Factory that encountered the issue
            build_result: Result from failed build

        Returns:
            EscalationSnapshot with VS Code URL
        """
        snapshot = await self.devcontainer_manager.create_escalation_snapshot(
            tenant_id=factory.config.tenant_id,
            workspace_path=factory.deps.workspace_root,
            feature_request=build_result.get("request", "Unknown"),
            iteration_count=build_result.get("iterations", 0),
            error_log=build_result.get("error_log", []),
            files_created=build_result.get("files_created", [])
        )

        print(f"\n{'='*60}")
        print("HUMAN INTERVENTION REQUIRED")
        print(f"{'='*60}")
        print(f"Snapshot ID: {snapshot.snapshot_id}")
        print(f"VS Code URL: {snapshot.vscode_url}")
        print(f"Workspace: {snapshot.workspace_path}")
        print(f"{'='*60}")

        return snapshot

    async def get_factory(self, tenant_id: str) -> Optional[FactoryTemplate]:
        """Get factory by tenant ID."""
        return self._factories.get(tenant_id)

    async def list_factories(self) -> List[FactoryStatus]:
        """List all active factories."""
        statuses = []

        for tenant_id, factory in self._factories.items():
            tenant = await self.tenant_manager.get_tenant(tenant_id)
            if tenant:
                statuses.append(FactoryStatus(
                    tenant_id=tenant_id,
                    factory_name=factory.config.domain_context.domain_name,
                    domain=factory.config.domain_context.domain_name,
                    status="active",
                    features_built=tenant.features_built,
                    credits_remaining=tenant.credits_remaining
                ))

        return statuses

    async def get_metrics(self) -> EngineMetrics:
        """Get engine metrics."""
        pending = await self.devcontainer_manager.list_pending_escalations()
        tenants = await self.tenant_manager.list_tenants()

        total_features = sum(t.features_built for t in tenants)

        return EngineMetrics(
            total_factories=len(self._factories),
            active_factories=len([f for f in self._factories.values()]),
            total_features_built=total_features,
            pending_escalations=len(pending)
        )

    async def delete_factory(self, tenant_id: str) -> bool:
        """
        Delete a factory and all associated resources.

        Args:
            tenant_id: Tenant to delete

        Returns:
            True if successful
        """
        if tenant_id in self._factories:
            del self._factories[tenant_id]

        if tenant_id in self._blueprints:
            del self._blueprints[tenant_id]

        return await self.tenant_manager.delete_tenant(tenant_id)


# ============================================================================
# Dynamic Factory (Generated by Genesis)
# ============================================================================

class DynamicFactory(FactoryTemplate):
    """
    Dynamic factory created by Genesis from a blueprint.

    This class adapts a FactoryBlueprint into a working factory
    that can generate code for its specific domain.
    """

    def __init__(
        self,
        config: FactoryConfig,
        deps: FactoryDepsBase,
        blueprint: FactoryBlueprint
    ):
        super().__init__(config, deps)
        self.blueprint = blueprint

    def get_context_md(self) -> str:
        """Generate CONTEXT.md from blueprint."""
        return generate_context_md(self.blueprint)

    def get_architect_prompt(self) -> str:
        """Get architect prompt from blueprint."""
        return self.blueprint.architect_spec.system_prompt

    def get_builder_prompt(self) -> str:
        """Get builder prompt from blueprint."""
        return self.blueprint.builder_spec.system_prompt

    def get_qa_prompt(self) -> str:
        """Get QA prompt from blueprint."""
        return self.blueprint.qa_spec.system_prompt

    async def build_feature(self, request: str) -> Dict[str, Any]:
        """
        Build a feature using the dynamic factory.

        This uses the Genesis-generated prompts to guide
        the Architect → Builder → QA pipeline.
        """
        # For now, delegate to the existing implementation
        # In production, this would use the custom prompts
        from agents.factory_deps import FactoryDeps
        from graph.factory_graph import run_factory

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
            "iterations": result["iteration_count"],
            "request": request
        }


__all__ = [
    "GenesisEngine",
    "FactoryStatus",
    "EngineMetrics",
]
