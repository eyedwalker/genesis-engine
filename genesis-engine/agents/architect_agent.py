"""
Architect Agent - Designs FHIR-compliant system features.

This agent analyzes feature requests and creates detailed implementation plans
that conform to HL7 FHIR R4 standards.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from .factory_deps import (
    FactoryDeps,
    search_fhir_docs,
    read_code_file,
    list_workspace_files
)


# ============================================================================
# Output Models
# ============================================================================

class PlanStep(BaseModel):
    """A single implementation step in the plan."""
    file_path: str = Field(
        description="Relative path where file will be created"
    )
    description: str = Field(
        description="What this file does"
    )
    dependencies: List[str] = Field(
        default=[],
        description="Other steps this depends on"
    )


class ImplementationPlan(BaseModel):
    """
    Complete implementation plan for a feature.
    
    This is the output format from the Architect agent.
    """
    feature_name: str = Field(
        description="Short name for the feature"
    )
    fhir_resources: List[str] = Field(
        description="FHIR resources involved (e.g., Appointment, Slot)"
    )
    description: str = Field(
        description="Detailed description of what will be built"
    )
    business_rules: List[str] = Field(
        description="Critical business logic rules to implement"
    )
    steps: List[PlanStep] = Field(
        description="Ordered list of implementation steps"
    )
    api_endpoints: List[str] = Field(
        description="API endpoints to create (e.g., POST /appointments/{id}/cancel)"
    )
    database_changes: List[str] = Field(
        description="Database migrations or schema changes needed"
    )


# ============================================================================
# System Prompt
# ============================================================================

ARCHITECT_SYSTEM_PROMPT = """
You are the **Lead Architect** for Hive BizOS, a healthcare business operating system.

## Your Mission

Design FHIR-compliant features that will be implemented by other agents.
Your plans must be:
- ✅ **Compliant** with HL7 FHIR R4 standard
- ✅ **Type-safe** using Pydantic models
- ✅ **Secure** (HIPAA-compliant, no PHI in logs)
- ✅ **Complete** (all edge cases covered)

## Your Process

1. **Analyze the request**
   - What is the user asking for?
   - What FHIR resources are involved?

2. **Search FHIR documentation**
   - Use `search_fhir_docs()` to find relevant specs
   - Verify field names, status enums, constraints

3. **Check existing code**
   - Use `list_workspace_files()` to see what exists
   - Use `read_code_file()` to review implementations
   - Avoid duplicate functionality

4. **Design the solution**
   - Define Pydantic models
   - Specify API endpoints
   - List business rules
   - Plan database changes

5. **Create implementation plan**
   - Break into ordered steps
   - Specify file paths and dependencies
   - Return structured JSON

## Critical Rules

**FHIR Compliance**:
- All data models MUST map to FHIR resources
- Use correct field names from FHIR spec
- Enforce FHIR value sets (e.g., status enums)

**Type Safety**:
- All models must use Pydantic
- Specify exact types (no `Any`)
- Include field validators where needed

**Security**:
- NEVER include PHI in logs
- Always validate inputs
- Use proper authentication/authorization

**Example FHIR Status Enum**:
```python
from enum import Enum

class AppointmentStatus(str, Enum):
    PROPOSED = "proposed"
    PENDING = "pending"
    BOOKED = "booked"
    ARRIVED = "arrived"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    NOSHOW = "noshow"
    ENTERED_IN_ERROR = "entered-in-error"
    CHECKED_IN = "checked-in"
    WAITLIST = "waitlist"
```

## Output Format

Return a valid `ImplementationPlan` JSON object with:
- `feature_name`: Brief name
- `fhir_resources`: List of FHIR resources
- `description`: What will be built
- `business_rules`: Critical logic rules
- `steps`: Ordered implementation steps
- `api_endpoints`: Endpoints to create
- `database_changes`: Schema changes needed

## Example

**Input**: "Add appointment cancellation"

**Your Output**:
```json
{
  "feature_name": "appointment_cancellation",
  "fhir_resources": ["Appointment", "Slot"],
  "description": "Enable cancellation of appointments with automatic slot release",
  "business_rules": [
    "When Appointment.status → 'cancelled', set linked Slot.status → 'free'",
    "Audit log must record who cancelled and why",
    "Send notification to all participants"
  ],
  "steps": [
    {
      "file_path": "app/models/appointment.py",
      "description": "Update Appointment model with cancel() method",
      "dependencies": []
    },
    {
      "file_path": "app/services/appointment_service.py",
      "description": "Implement cancel_appointment() business logic",
      "dependencies": ["app/models/appointment.py"]
    },
    {
      "file_path": "app/api/appointments.py",
      "description": "Add POST /appointments/{id}/cancel endpoint",
      "dependencies": ["app/services/appointment_service.py"]
    },
    {
      "file_path": "tests/test_appointment_cancel.py",
      "description": "Tests for cancellation logic",
      "dependencies": ["app/services/appointment_service.py"]
    }
  ],
  "api_endpoints": [
    "POST /api/v1/appointments/{id}/cancel"
  ],
  "database_changes": [
    "Add index on appointments.status for faster queries"
  ]
}
```

## Remember

You don't write code - you design the architecture.
The Builder agent will implement your plan.
Focus on correctness, completeness, and FHIR compliance.

Refer to the CONTEXT.md file for all standards and requirements.
"""


# ============================================================================
# Agent Definition
# ============================================================================

architect = Agent(
    'anthropic:claude-sonnet-4-5',
    deps_type=FactoryDeps,
    system_prompt=ARCHITECT_SYSTEM_PROMPT,
)

# Register tools
architect.tool(search_fhir_docs)
architect.tool(read_code_file)
architect.tool(list_workspace_files)


# ============================================================================
# Helper Function
# ============================================================================

async def run_architect(
    request: str,
    deps: FactoryDeps,
    context: str = ""
) -> ImplementationPlan:
    """
    Run the architect agent on a feature request.
    
    Args:
        request: User's feature request
        deps: Factory dependencies
        context: Additional context (optional)
        
    Returns:
        ImplementationPlan object
        
    Example:
        >>> plan = await run_architect(
        ...     "Add appointment cancellation",
        ...     deps
        ... )
        >>> print(plan.feature_name)
        "appointment_cancellation"
    """
    # Build the prompt with context
    prompt = f"Feature Request: {request}"
    if context:
        prompt += f"\n\nAdditional Context:\n{context}"
    
    # Run the agent with output type
    result = await architect.run(prompt, deps=deps, output_type=ImplementationPlan)

    return result.output


# Export
__all__ = ["architect", "run_architect", "ImplementationPlan", "PlanStep"]
