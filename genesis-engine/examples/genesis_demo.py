#!/usr/bin/env python3
"""
Genesis Engine Demo - Factory-as-a-Service.

This demo shows how to use the Genesis Engine to:
1. Create a new software factory for any domain
2. Build features using the factory
3. Handle human escalation when needed

Usage:
    python examples/genesis_demo.py
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_environment() -> bool:
    """Check for required environment variables."""
    required = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required if not os.getenv(var)]

    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them in your .env file or export them:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export OPENAI_API_KEY=sk-...")
        return False

    return True


async def demo_healthcare_factory():
    """
    Demo 1: Use the pre-built Healthcare Factory (Hive BizOS).

    This is the fastest way to get started - no Genesis needed.
    """
    print("\n" + "=" * 60)
    print("DEMO 1: Healthcare Factory (Hive BizOS)")
    print("=" * 60)

    from genesis import GenesisEngine

    # Create engine
    engine = GenesisEngine.from_env()

    # Get healthcare factory
    print("\nCreating healthcare factory for tenant 'demo_clinic'...")
    factory = await engine.get_healthcare_factory(
        tenant_id="demo_clinic",
        contact_email="demo@clinic.com"
    )

    # Build a feature
    print("\nBuilding feature: 'Add appointment reminder notifications'...")
    result = await factory.build_feature(
        "Add appointment reminder notifications that send SMS 24 hours before the appointment"
    )

    print(f"\nResult: {result['status']}")
    print(f"Files created: {len(result['files_created'])}")
    for f in result['files_created']:
        print(f"  - {f}")

    if result['status'] == 'needs_human':
        print("\nHuman intervention needed!")
        snapshot = await engine.create_escalation(factory, result)
        print(f"Open VS Code: {snapshot.vscode_url}")

    return result


async def demo_genesis_new_domain():
    """
    Demo 2: Create a completely new factory for a different domain.

    This shows the full Genesis Engine capability - analyzing a new
    domain and generating a complete factory configuration.
    """
    print("\n" + "=" * 60)
    print("DEMO 2: Genesis Engine - Create New Factory")
    print("=" * 60)

    from genesis import GenesisEngine

    # Create engine
    engine = GenesisEngine.from_env()

    # Define a new domain
    domain_description = """
    A cold-chain logistics company that:
    - Manages temperature-sensitive shipments (pharmaceuticals, food)
    - Uses IoT sensors to monitor container temperatures
    - Must comply with FDA 21 CFR Part 11 for pharma shipments
    - Needs real-time alerts when temperature exceeds thresholds
    - Tracks chain of custody for each shipment
    - Integrates with warehouse management systems
    """

    print(f"\nDomain: Cold-Chain Logistics")
    print(f"Description: {domain_description[:100]}...")

    # Create factory (this runs the Genesis Agent)
    print("\nRunning Genesis Agent to analyze domain and create factory...")
    print("(This uses Claude Opus for meta-prompting)")

    factory = await engine.create_factory(
        tenant_id="apex_logistics",
        domain_description=domain_description,
        display_name="Apex Logistics Inc.",
        contact_email="admin@apexlogistics.com"
    )

    # Show what Genesis created
    print("\nGenesis created factory with:")
    print(f"  - Domain: {factory.config.domain_context.domain_name}")
    print(f"  - Standards: {', '.join(factory.config.domain_context.standards)}")

    # Build a feature
    print("\nBuilding feature: 'Add temperature excursion alerts'...")
    result = await factory.build_feature(
        "Add real-time temperature excursion alerts when container temperature exceeds threshold"
    )

    print(f"\nResult: {result['status']}")
    print(f"Files created: {len(result['files_created'])}")
    for f in result['files_created']:
        print(f"  - {f}")

    return result


async def demo_factory_lifecycle():
    """
    Demo 3: Full factory lifecycle management.

    Shows provisioning, building, metrics, and cleanup.
    """
    print("\n" + "=" * 60)
    print("DEMO 3: Factory Lifecycle Management")
    print("=" * 60)

    from genesis import GenesisEngine

    engine = GenesisEngine.from_env()

    # Create factory
    print("\n1. Creating factory...")
    factory = await engine.get_healthcare_factory(
        tenant_id="lifecycle_demo",
        contact_email="demo@example.com"
    )

    # Build multiple features
    print("\n2. Building features...")
    features = [
        "Add patient search endpoint",
        "Add appointment status update API"
    ]

    for feature in features:
        print(f"\n   Building: {feature[:50]}...")
        result = await factory.build_feature(feature)
        print(f"   Status: {result['status']}")

    # Get metrics
    print("\n3. Engine metrics...")
    metrics = await engine.get_metrics()
    print(f"   Total factories: {metrics.total_factories}")
    print(f"   Active factories: {metrics.active_factories}")
    print(f"   Features built: {metrics.total_features_built}")
    print(f"   Pending escalations: {metrics.pending_escalations}")

    # List factories
    print("\n4. Active factories...")
    factories = await engine.list_factories()
    for f in factories:
        print(f"   - {f.tenant_id}: {f.domain} ({f.features_built} features)")

    # Cleanup
    print("\n5. Cleaning up...")
    await engine.delete_factory("lifecycle_demo")
    print("   Factory deleted.")

    return True


def main():
    """Main entry point."""
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Check environment
    if not check_environment():
        sys.exit(1)

    print("=" * 60)
    print("GENESIS ENGINE DEMO")
    print("Factory-as-a-Service Platform")
    print("=" * 60)

    print("\nSelect a demo:")
    print("1. Healthcare Factory (Hive BizOS) - Quick start")
    print("2. Genesis New Domain - Create factory for logistics")
    print("3. Factory Lifecycle - Full management demo")
    print("4. Exit")

    choice = input("\nChoice (1-4): ").strip()

    if choice == "1":
        asyncio.run(demo_healthcare_factory())
    elif choice == "2":
        asyncio.run(demo_genesis_new_domain())
    elif choice == "3":
        asyncio.run(demo_factory_lifecycle())
    elif choice == "4":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
