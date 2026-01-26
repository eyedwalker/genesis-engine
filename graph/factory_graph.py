"""
Factory Orchestration Graph - Self-Healing Development Pipeline.

This module defines the LangGraph state machine that coordinates agents
in a cyclic workflow with automatic retry and human-in-the-loop escalation.
"""

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.types import RunnableConfig
import operator
from agents.architect_agent import run_architect, ImplementationPlan
from agents.builder_agent import run_builder, BuildResult
from agents.factory_deps import FactoryDeps


# ============================================================================
# State Definition
# ============================================================================

class FactoryState(TypedDict):
    """
    State that flows through the factory graph.
    
    This state is updated by each node and passed to the next.
    """
    # Input
    request: str
    
    # Architect output
    plan: Optional[ImplementationPlan]
    
    # Builder output  
    build_result: Optional[BuildResult]
    files_created: Annotated[List[str], operator.add]  # Accumulate files
    
    # Error tracking
    error_log: Annotated[List[str], operator.add]  # Accumulate errors
    iteration_count: int
    
    # Status
    status: str  # "in_progress" | "success" | "failed" | "needs_human"


# ============================================================================
# Node Functions
# ============================================================================

async def architect_node(state: FactoryState, *, config: RunnableConfig) -> dict:
    """
    Architect agent node - Creates implementation plan.

    Args:
        state: Current graph state
        config: Runnable config containing deps

    Returns:
        State updates
    """
    print(f"\n🏗️  ARCHITECT: Analyzing request...")

    # Extract dependencies from config
    deps = config.get("configurable", {}).get("deps")
    if deps is None:
        raise ValueError("Missing deps in config")
    
    try:
        plan = await run_architect(
            request=state["request"],
            deps=deps
        )
        
        print(f"✅ ARCHITECT: Created plan for '{plan.feature_name}'")
        print(f"   - FHIR Resources: {', '.join(plan.fhir_resources)}")
        print(f"   - Steps: {len(plan.steps)}")
        
        return {
            "plan": plan,
            "status": "in_progress"
        }
        
    except Exception as e:
        error_msg = f"Architect failed: {str(e)}"
        print(f"❌ ARCHITECT: {error_msg}")
        
        return {
            "error_log": [error_msg],
            "status": "failed"
        }


async def builder_node(state: FactoryState, *, config: RunnableConfig) -> dict:
    """
    Builder agent node - Implements the plan.

    Args:
        state: Current graph state
        config: Runnable config containing deps

    Returns:
        State updates
    """
    print(f"\n👷 BUILDER: Implementing plan (iteration {state['iteration_count'] + 1})...")

    # Extract dependencies from config
    deps = config.get("configurable", {}).get("deps")
    if deps is None:
        raise ValueError("Missing deps in config")
    
    # Get error context from previous iterations
    error_context = "\n".join(state.get("error_log", [])[-3:])  # Last 3 errors
    
    try:
        build_result = await run_builder(
            plan=state["plan"],
            deps=deps,
            error_context=error_context
        )
        
        print(f"   - Files created: {len(build_result.files_created)}")
        print(f"   - Lint status: {build_result.lint_status}")
        
        if build_result.lint_status == "pass":
            print("✅ BUILDER: Code passes all checks!")
            return {
                "build_result": build_result,
                "files_created": build_result.files_created,
                "status": "in_progress"
            }
        else:
            print(f"⚠️  BUILDER: Linting failed, will retry...")
            return {
                "build_result": build_result,
                "error_log": [build_result.lint_output],
                "iteration_count": state["iteration_count"] + 1,
                "status": "in_progress"
            }
        
    except Exception as e:
        error_msg = f"Builder failed: {str(e)}"
        print(f"❌ BUILDER: {error_msg}")
        
        return {
            "error_log": [error_msg],
            "iteration_count": state["iteration_count"] + 1,
            "status": "in_progress"
        }


async def qa_node(state: FactoryState, *, config: RunnableConfig) -> dict:
    """
    QA agent node - Runs tests (placeholder for now).

    In full implementation, this would:
    - Execute pytest via Dagger
    - Analyze coverage
    - Report failures

    For free tier MVP, we skip containerized testing.

    Args:
        state: Current graph state
        config: Runnable config containing deps

    Returns:
        State updates
    """
    # Extract dependencies from config
    deps = config.get("configurable", {}).get("deps")
    if deps is None:
        raise ValueError("Missing deps in config")
    
    print(f"\n🧪 QA: Checking code quality...")
    
    # For MVP: If linting passed, we're good
    if state["build_result"].lint_status == "pass":
        print("✅ QA: All checks passed!")
        return {
            "status": "success"
        }
    else:
        print("⚠️  QA: Quality checks failed")
        return {
            "error_log": ["QA checks failed"],
            "status": "in_progress"
        }


async def human_intervention_node(state: FactoryState, *, config: RunnableConfig) -> dict:
    """
    Human intervention node - Escalates to human.

    In full implementation, this would:
    - Create DevContainer snapshot
    - Send alert to developer
    - Wait for human fix

    For MVP, we just log the failure.

    Args:
        state: Current graph state
        config: Runnable config containing deps

    Returns:
        State updates
    """
    # Extract dependencies from config
    deps = config.get("configurable", {}).get("deps")
    if deps is None:
        raise ValueError("Missing deps in config")
    
    print(f"\n🚨 HUMAN INTERVENTION NEEDED")
    print(f"   Failed after {state['iteration_count']} iterations")
    print(f"   Recent errors:")
    for error in state.get("error_log", [])[-3:]:
        print(f"   - {error[:100]}...")
    
    return {
        "status": "needs_human"
    }


# ============================================================================
# Conditional Edge Functions
# ============================================================================

def check_builder_result(state: FactoryState) -> str:
    """
    Determine next step after builder runs.
    
    Returns:
        - "qa" if code passes linting
        - "retry" if linting failed and iterations < 5
        - "human" if too many failures
    """
    build_result = state.get("build_result")
    
    # If linting passed, move to QA
    if build_result and build_result.lint_status == "pass":
        return "qa"
    
    # If too many iterations, escalate to human
    if state["iteration_count"] >= 5:
        return "human"
    
    # Otherwise, retry
    return "retry"


def check_qa_result(state: FactoryState) -> str:
    """
    Determine next step after QA runs.
    
    Returns:
        - END if tests pass
        - "retry" if tests fail and iterations < 5  
        - "human" if too many failures
    """
    # If status is success, we're done
    if state["status"] == "success":
        return END
    
    # If too many iterations, escalate to human
    if state["iteration_count"] >= 5:
        return "human"
    
    # Otherwise, retry from builder
    return "retry"


# ============================================================================
# Graph Construction
# ============================================================================

def create_factory_graph() -> StateGraph:
    """
    Create the factory orchestration graph.
    
    Graph structure:
    ```
    START
      ↓
    Architect (design plan)
      ↓
    Builder (write code)
      ↓
    Check Result
      ├─ pass → QA
      ├─ fail → Builder (retry, max 5)
      └─ too many fails → Human
    
    QA (run tests)
      ├─ pass → END
      ├─ fail → Builder (retry)
      └─ too many fails → Human
    
    Human (escalate)
      → END
    ```
    
    Returns:
        Compiled StateGraph
    """
    workflow = StateGraph(FactoryState)
    
    # Add nodes
    workflow.add_node("architect", architect_node)
    workflow.add_node("builder", builder_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("human", human_intervention_node)
    
    # Set entry point
    workflow.set_entry_point("architect")
    
    # Architect always goes to Builder
    workflow.add_edge("architect", "builder")
    
    # Builder has conditional routing
    workflow.add_conditional_edges(
        "builder",
        check_builder_result,
        {
            "qa": "qa",
            "retry": "builder",  # Self-healing loop!
            "human": "human"
        }
    )
    
    # QA has conditional routing
    workflow.add_conditional_edges(
        "qa",
        check_qa_result,
        {
            END: END,
            "retry": "builder",  # Self-healing loop!
            "human": "human"
        }
    )
    
    # Human intervention ends the flow
    workflow.add_edge("human", END)
    
    return workflow.compile()


# ============================================================================
# Main Entry Point
# ============================================================================

async def run_factory(
    request: str,
    deps: FactoryDeps
) -> FactoryState:
    """
    Run the complete factory pipeline on a feature request.
    
    Args:
        request: User's feature request
        deps: Factory dependencies
        
    Returns:
        Final state after completion
        
    Example:
        >>> deps = FactoryDeps.from_env()
        >>> state = await run_factory(
        ...     "Add appointment cancellation",
        ...     deps
        ... )
        >>> print(state["status"])
        "success"
        >>> print(state["files_created"])
        ["app/models/appointment.py", ...]
    """
    # Create graph
    app = create_factory_graph()
    
    # Initial state
    initial_state: FactoryState = {
        "request": request,
        "plan": None,
        "build_result": None,
        "files_created": [],
        "error_log": [],
        "iteration_count": 0,
        "status": "in_progress"
    }
    
    # Run graph
    print(f"\n{'='*60}")
    print(f"🏭 FACTORY STARTING")
    print(f"{'='*60}")
    print(f"Request: {request}")
    
    # Execute with dependencies
    final_state = await app.ainvoke(initial_state, config={"configurable": {"deps": deps}})
    
    print(f"\n{'='*60}")
    print(f"🏭 FACTORY {'✅ COMPLETED' if final_state['status'] == 'success' else '❌ ' + final_state['status'].upper()}")
    print(f"{'='*60}")
    
    if final_state["status"] == "success":
        print(f"Files created: {len(final_state['files_created'])}")
        for filepath in final_state["files_created"]:
            print(f"  ✓ {filepath}")
    else:
        print(f"Status: {final_state['status']}")
        print(f"Iterations: {final_state['iteration_count']}")
    
    return final_state


# Export
__all__ = ["create_factory_graph", "run_factory", "FactoryState"]
