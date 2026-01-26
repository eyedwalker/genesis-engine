#!/usr/bin/env python3
"""
Quick verification that Genesis Engine is properly installed.
"""

import sys

def verify_imports():
    """Test all critical imports."""
    print("🔍 Verifying Genesis Engine installation...\n")

    try:
        print("1. Testing agent imports...")
        from agents.architect_agent import architect, run_architect
        from agents.builder_agent import builder, run_builder
        print("   ✅ Agents module loaded")

        print("\n2. Testing graph imports...")
        from graph.factory_graph import run_factory
        print("   ✅ Graph module loaded")

        print("\n3. Testing Genesis imports...")
        from genesis.genesis_engine import GenesisEngine
        from genesis.genesis_agent import genesis_agent, run_genesis
        from genesis.factory_template import FactoryTemplate, HealthcareFactory
        from genesis.dagger_executor import DaggerExecutor, create_executor
        from genesis.tenant_manager import TenantManager
        from genesis.devcontainer import DevContainerManager
        print("   ✅ Genesis module loaded")

        print("\n4. Testing AI frameworks...")
        import pydantic_ai
        import langgraph
        print(f"   ✅ PydanticAI {pydantic_ai.__version__}")
        print(f"   ✅ LangGraph loaded")

        print("\n5. Testing utilities...")
        import dagger
        import pymilvus
        print("   ✅ Dagger SDK loaded")
        print("   ✅ Milvus SDK loaded")

        print("\n" + "="*60)
        print("✨ ALL IMPORTS SUCCESSFUL!")
        print("="*60)

        print("\n📋 Next steps:")
        print("1. Start Docker Desktop")
        print("2. Run: cd docker && docker compose up -d")
        print("3. Run: python3 examples/genesis_demo.py")
        print("\nOr see START_HERE.md for detailed instructions.")

        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        print("\nTry running: pip install -e '.[all]'")
        return False

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
