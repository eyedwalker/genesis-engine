#!/usr/bin/env python3
"""Quick test of the architect agent with new PydanticAI API."""

import asyncio
from agents.architect_agent import run_architect
from agents.factory_deps import FactoryDeps

async def test():
    print("Testing architect agent...")

    # Create deps
    deps = FactoryDeps.from_env()

    # Run architect
    plan = await run_architect(
        "Add a simple test feature",
        deps
    )

    print(f"✅ Success!")
    print(f"Feature: {plan.feature_name}")
    print(f"FHIR Resources: {plan.fhir_resources}")
    print(f"Steps: {len(plan.steps)}")

if __name__ == "__main__":
    asyncio.run(test())
