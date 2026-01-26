"""
Genesis Engine - Factory-as-a-Service Platform.

The Genesis Engine is a meta-platform that instantiates bespoke software factories
for external tenants. It transforms domain descriptions into fully autonomous
development systems.

Components:
- genesis_agent: Meta-prompting agent that designs new factories
- factory_template: Base template for all factories
- dagger_executor: Containerized execution pipelines
- tenant_manager: Multi-tenant provisioning with Keycloak
- devcontainer: Human-in-the-loop escalation

Usage:
    from genesis import GenesisEngine

    engine = GenesisEngine.from_env()
    factory = await engine.create_factory(
        tenant_id="apex_logistics",
        domain_description="Cold-chain logistics with IoT integration"
    )

    result = await factory.build_feature("Add temperature monitoring")
"""

from .genesis_engine import GenesisEngine
from .genesis_agent import genesis_agent, run_genesis
from .factory_template import FactoryTemplate, FactoryConfig
from .dagger_executor import DaggerExecutor
from .tenant_manager import TenantManager
from .devcontainer import DevContainerManager

__all__ = [
    "GenesisEngine",
    "genesis_agent",
    "run_genesis",
    "FactoryTemplate",
    "FactoryConfig",
    "DaggerExecutor",
    "TenantManager",
    "DevContainerManager",
]
