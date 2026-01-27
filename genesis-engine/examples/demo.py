#!/usr/bin/env python3
"""
Hive BizOS Factory - Demo Script

This script demonstrates the factory building a real FHIR-compliant feature.

Usage:
    python examples/demo.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.factory_deps import FactoryDeps
from graph.factory_graph import run_factory


async def demo_appointment_cancellation():
    """
    Demo: Build appointment cancellation feature.
    
    This demonstrates the full factory pipeline:
    1. Architect designs the feature
    2. Builder implements it
    3. Self-healing loop fixes any issues
    4. QA validates the output
    """
    print("\n" + "=" * 80)
    print("HIVE BIZOS FACTORY - DEMO")
    print("=" * 80)
    print("\nFeature Request: Add appointment cancellation with automatic slot release")
    print("\nThis will:")
    print("  1. Search FHIR documentation for Appointment resource")
    print("  2. Design a FHIR-compliant implementation")
    print("  3. Generate production Python code")
    print("  4. Run linting and quality checks")
    print("  5. Self-correct any issues")
    print("\n" + "=" * 80)
    
    # Setup dependencies
    deps = FactoryDeps.from_env()
    
    # Ensure workspace exists
    os.makedirs(deps.workspace_root, exist_ok=True)
    
    # Run factory
    result = await run_factory(
        request="Add appointment cancellation feature with automatic slot release",
        deps=deps
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if result["status"] == "success":
        print("\n✅ SUCCESS!")
        print(f"\nFiles created ({len(result['files_created'])}):")
        for filepath in result["files_created"]:
            print(f"  ✓ {filepath}")
        
        print(f"\nWorkspace location: {deps.workspace_root}")
        print("\nNext steps:")
        print("  1. Review generated code")
        print("  2. Deploy to your application")
        print("  3. Test with real data")
        
    elif result["status"] == "needs_human":
        print("\n⚠️  NEEDS HUMAN INTERVENTION")
        print(f"\nFailed after {result['iteration_count']} iterations")
        print("\nRecent errors:")
        for error in result["error_log"][-3:]:
            print(f"  • {error[:100]}...")
        
        print(f"\nWorkspace location: {deps.workspace_root}")
        print("\nNext steps:")
        print("  1. Review error logs")
        print("  2. Fix issues manually")
        print("  3. Re-run factory")
    
    else:
        print(f"\n❌ FAILED: {result['status']}")
        if result.get("error_log"):
            print("\nErrors:")
            for error in result["error_log"]:
                print(f"  • {error}")
    
    print("\n" + "=" * 80)


async def demo_simple_feature():
    """
    Demo: Build a simple health check endpoint.
    
    This is a simpler example that should complete quickly.
    """
    print("\n" + "=" * 80)
    print("SIMPLE DEMO - Health Check Endpoint")
    print("=" * 80)
    
    deps = FactoryDeps.from_env()
    os.makedirs(deps.workspace_root, exist_ok=True)
    
    result = await run_factory(
        request="Add a health check endpoint that returns API status",
        deps=deps
    )
    
    if result["status"] == "success":
        print("\n✅ Created health check endpoint!")
        print(f"Files: {', '.join(result['files_created'])}")


async def check_environment():
    """
    Check that all required environment variables are set.
    """
    required = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY"
    ]
    
    optional = [
        "WORKSPACE_ROOT",
        "TENANT_ID",
        "MILVUS_URI",
        "DATABASE_URL",
        "AWS_REGION"
    ]
    
    print("\n" + "=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80)
    
    missing = []
    for var in required:
        value = os.getenv(var)
        if value:
            # Show first/last 4 chars only
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: NOT SET")
            missing.append(var)
    
    print("\nOptional:")
    for var in optional:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"  {var}: Using default")
    
    if missing:
        print("\n" + "=" * 80)
        print("ERROR: Missing required environment variables!")
        print("=" * 80)
        print("\nPlease set the following:")
        for var in missing:
            if var == "ANTHROPIC_API_KEY":
                print(f"\n{var}:")
                print("  1. Visit: https://console.anthropic.com/")
                print("  2. Sign up and get API key")
                print("  3. Set: export ANTHROPIC_API_KEY='sk-ant-...'")
            elif var == "OPENAI_API_KEY":
                print(f"\n{var}:")
                print("  1. Visit: https://platform.openai.com/")
                print("  2. Sign up and get API key")
                print("  3. Set: export OPENAI_API_KEY='sk-...'")
        
        return False
    
    print("\n✅ Environment OK!")
    return True


async def main():
    """
    Main demo function with menu.
    """
    # Check environment
    if not await check_environment():
        sys.exit(1)
    
    # Menu
    print("\n" + "=" * 80)
    print("DEMO MENU")
    print("=" * 80)
    print("\n1. Full Demo: Appointment Cancellation (complex feature)")
    print("2. Simple Demo: Health Check Endpoint (simple feature)")
    print("3. Custom Feature (enter your own request)")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        await demo_appointment_cancellation()
    elif choice == "2":
        await demo_simple_feature()
    elif choice == "3":
        request = input("\nEnter feature request: ").strip()
        if request:
            deps = FactoryDeps.from_env()
            os.makedirs(deps.workspace_root, exist_ok=True)
            result = await run_factory(request, deps)
            
            if result["status"] == "success":
                print(f"\n✅ Created {len(result['files_created'])} files!")
            else:
                print(f"\n❌ Status: {result['status']}")
    elif choice == "4":
        print("\nGoodbye!")
    else:
        print("\nInvalid option!")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
