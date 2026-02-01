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

# Load environment variables first (before any imports that need API keys)
from pathlib import Path
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Guard heavy imports that require optional dependencies (e.g. pydantic_ai)
# The API server uses importlib to load only what it needs, but the package
# __init__ still runs when Python resolves the module path.
try:
    from .genesis_engine import GenesisEngine
    from .genesis_agent import genesis_agent, run_genesis
    from .factory_template import FactoryTemplate, FactoryConfig
    from .dagger_executor import DaggerExecutor
    from .tenant_manager import TenantManager
    from .devcontainer import DevContainerManager
except ImportError:
    GenesisEngine = None
    genesis_agent = None
    run_genesis = None
    FactoryTemplate = None
    FactoryConfig = None
    DaggerExecutor = None
    TenantManager = None
    DevContainerManager = None

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
