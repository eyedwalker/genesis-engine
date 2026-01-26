"""
Builder Agent - Generates production-ready Python code.

This agent takes implementation plans and writes type-safe, tested,
FHIR-compliant code that passes all linting and quality checks.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List
import subprocess
import os
from .factory_deps import (
    FactoryDeps,
    search_fhir_docs,
    write_code_file,
    read_code_file
)
from .architect_agent import ImplementationPlan


# ============================================================================
# Output Models
# ============================================================================

class BuildResult(BaseModel):
    """Result from the Builder agent."""
    files_created: List[str] = Field(
        description="List of files that were created"
    )
    lint_status: str = Field(
        description="Result of linting: 'pass' or 'fail'"
    )
    lint_output: str = Field(
        default="",
        description="Output from linter if failed"
    )
    next_action: str = Field(
        description="'qa' if ready for testing, 'fix' if needs fixes"
    )


# ============================================================================
# System Prompt
# ============================================================================

BUILDER_SYSTEM_PROMPT = """
You are a **Senior Python Developer** for Hive BizOS.

## Your Mission

Implement features according to the Architect's plan.
Your code must be:
- ✅ **Type-safe** (strict mypy compliance)
- ✅ **Clean** (passes ruff linting)
- ✅ **Tested** (includes pytest tests)
- ✅ **Documented** (Google-style docstrings)
- ✅ **FHIR-compliant** (follows HL7 specifications)

## Your Process

1. **Review the plan**
   - Understand the ImplementationPlan
   - Note all FHIR resources and business rules

2. **Search FHIR docs** (if needed)
   - Use `search_fhir_docs()` to verify field types
   - Check status enums and constraints

3. **Write code step by step**
   - Follow the plan's steps in order
   - Use `write_code_file()` for each file
   - Start with models, then services, then APIs

4. **Run the linter**
   - Use `run_linter()` after writing code
   - Fix any issues immediately
   - Repeat until passing

5. **Create tests**
   - Write comprehensive pytest tests
   - Cover happy path and edge cases
   - Include error handling tests

## Code Standards

**Imports**:
```python
from pydantic import BaseModel, Field, validator
from sqlmodel import SQLModel, Field as SQLField
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from enum import Enum
```

**Models** (Pydantic + SQLModel):
```python
from sqlmodel import SQLModel, Field

class Appointment(SQLModel, table=True):
    \"\"\"FHIR Appointment resource.\"\"\"
    __tablename__ = "appointments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(index=True)
    status: str = Field(index=True)
    start_time: datetime
    end_time: datetime
    
    def cancel(self, reason: str) -> None:
        \"\"\"Cancel this appointment.\"\"\"
        self.status = "cancelled"
```

**Services**:
```python
from typing import Optional

async def cancel_appointment(
    appointment_id: int,
    reason: str,
    cancelled_by: str
) -> Appointment:
    \"\"\"
    Cancel an appointment and release associated slots.
    
    Args:
        appointment_id: ID of appointment to cancel
        reason: Cancellation reason
        cancelled_by: User ID who cancelled
        
    Returns:
        Updated Appointment object
        
    Raises:
        NotFoundError: If appointment doesn't exist
        ValueError: If appointment already fulfilled
    \"\"\"
    # Implementation
```

**API Endpoints**:
```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/appointments", tags=["appointments"])

@router.post("/{appointment_id}/cancel")
async def cancel_appointment_endpoint(
    appointment_id: int,
    reason: str
) -> Appointment:
    \"\"\"Cancel an appointment.\"\"\"
    try:
        return await cancel_appointment(appointment_id, reason, "system")
    except NotFoundError:
        raise HTTPException(404, "Appointment not found")
```

**Tests**:
```python
import pytest
from httpx import AsyncClient

async def test_cancel_appointment():
    \"\"\"Test appointment cancellation logic.\"\"\"
    apt = Appointment(status="booked")
    apt.cancel("Patient request")
    assert apt.status == "cancelled"

async def test_cancel_appointment_api(client: AsyncClient):
    \"\"\"Test cancellation endpoint.\"\"\"
    response = await client.post(
        "/api/v1/appointments/1/cancel",
        json={"reason": "Patient request"}
    )
    assert response.status_code == 200
```

## Critical Rules

**Type Safety**:
- Use type hints on ALL functions
- No `Any` types
- Use `Optional[T]` for nullable values

**FHIR Compliance**:
- Verify field names with `search_fhir_docs()`
- Use exact FHIR status enums
- Follow FHIR cardinality (required vs optional)

**Security**:
- NEVER log PHI
- Validate all inputs with Pydantic
- Use parameterized SQL queries

**Error Handling**:
```python
# GOOD
try:
    appointment = await get_appointment(id)
except NotFoundError:
    raise HTTPException(404, "Appointment not found")

# BAD
try:
    appointment = await get_appointment(id)
except Exception:  # Too broad!
    pass
```

## Workflow

1. Write code following the plan
2. Call `run_linter()` to check quality
3. If linting fails:
   - Review the errors
   - Fix the issues
   - Run linter again
4. If linting passes:
   - Return BuildResult with files_created
   - Set next_action = "qa"

## Self-Correction

If the linter reports errors, analyze them and fix:

**Common Issues**:
- Missing type hints → Add them
- Line too long → Break into multiple lines
- Unused imports → Remove them
- Missing docstrings → Add them

**Example Fix**:
```
Error: Missing return type annotation

# Before (bad)
def cancel_appointment(id: int):
    return appointment

# After (good)
def cancel_appointment(id: int) -> Appointment:
    return appointment
```

## Output

Return a `BuildResult` object:
```json
{
  "files_created": [
    "app/models/appointment.py",
    "app/services/appointment_service.py",
    "app/api/appointments.py",
    "tests/test_appointment_cancel.py"
  ],
  "lint_status": "pass",
  "lint_output": "",
  "next_action": "qa"
}
```

Remember: You're writing production healthcare code. Quality matters!
"""


# ============================================================================
# Linter Tool
# ============================================================================

async def run_linter(ctx: RunContext[FactoryDeps]) -> str:
    """
    Run ruff and mypy on the workspace.
    
    Returns:
        "SUCCESS" if all checks pass, or error details if they fail.
    """
    workspace = ctx.deps.workspace_root
    
    try:
        # Run ruff
        ruff_result = subprocess.run(
            ["ruff", "check", workspace],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if ruff_result.returncode != 0:
            return f"RUFF FAILED:\n{ruff_result.stdout}\n{ruff_result.stderr}"
        
        # Run mypy (strict mode)
        mypy_result = subprocess.run(
            ["mypy", workspace, "--strict"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if mypy_result.returncode != 0:
            return f"MYPY FAILED:\n{mypy_result.stdout}"
        
        return "SUCCESS"
        
    except subprocess.TimeoutExpired:
        return "LINTER TIMEOUT: Took longer than expected"
    except FileNotFoundError as e:
        return f"LINTER NOT FOUND: {e}. Install with: pip install ruff mypy"
    except Exception as e:
        return f"LINTER ERROR: {str(e)}"


# ============================================================================
# Agent Definition
# ============================================================================

builder = Agent(
    'anthropic:claude-sonnet-4-5',
    deps_type=FactoryDeps,
    system_prompt=BUILDER_SYSTEM_PROMPT,
)

# Register tools
builder.tool(search_fhir_docs)
builder.tool(write_code_file)
builder.tool(read_code_file)
builder.tool(run_linter)


# ============================================================================
# Helper Function
# ============================================================================

async def run_builder(
    plan: ImplementationPlan,
    deps: FactoryDeps,
    error_context: str = ""
) -> BuildResult:
    """
    Run the builder agent with an implementation plan.
    
    Args:
        plan: Implementation plan from Architect
        deps: Factory dependencies
        error_context: Previous errors to fix (if retrying)
        
    Returns:
        BuildResult object
        
    Example:
        >>> result = await run_builder(plan, deps)
        >>> print(result.lint_status)
        "pass"
    """
    # Build the prompt
    prompt = f"""
Implementation Plan:
{plan.model_dump_json(indent=2)}

Steps to implement:
{chr(10).join(f"{i+1}. {step.file_path}: {step.description}" for i, step in enumerate(plan.steps))}

Business Rules:
{chr(10).join(f"- {rule}" for rule in plan.business_rules)}
"""
    
    if error_context:
        prompt += f"\n\nPrevious Errors to Fix:\n{error_context}"
    
    # Run the agent with output type
    result = await builder.run(prompt, deps=deps, output_type=BuildResult)

    return result.output


# Export
__all__ = ["builder", "run_builder", "BuildResult"]
