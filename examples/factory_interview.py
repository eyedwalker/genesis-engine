#!/usr/bin/env python3
"""
Interactive AI Interview for Factory Definition.

Conducts a conversational interview to help you define complete
factory parameters, including:
- Domain description
- Standards and compliance
- Technical requirements
- Engineering standards
- API keys and environment variables
"""

import asyncio
import os
from dataclasses import dataclass
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent


# ============================================================================
# Output Models
# ============================================================================

class EnvironmentVariable(BaseModel):
    """Environment variable specification."""
    name: str = Field(description="Variable name (e.g., 'STRIPE_API_KEY')")
    description: str = Field(description="What this variable is for")
    required: bool = Field(description="Is this variable required?")
    default_value: Optional[str] = Field(default=None, description="Default value if any")
    example: str = Field(description="Example value")
    category: str = Field(description="Category: api_key, database, feature_flag, etc.")


class EngineeringStandard(BaseModel):
    """Engineering and code quality standards."""
    code_style: str = Field(description="Code style guide (e.g., 'PEP 8', 'Google Style')")
    linting_rules: List[str] = Field(description="Linting rules to enforce")
    formatting: str = Field(description="Code formatter (e.g., 'black', 'prettier')")
    type_checking: str = Field(description="Type checker (e.g., 'mypy strict')")
    documentation: str = Field(description="Documentation requirements")
    testing: Dict[str, str] = Field(description="Testing standards (coverage, etc.)")


class UIUXStandard(BaseModel):
    """UI/UX design standards."""
    design_system: str = Field(description="Design system (e.g., 'Material Design', 'Ant Design')")
    component_library: str = Field(description="Component library to use")
    accessibility: List[str] = Field(description="Accessibility standards (WCAG 2.1 AA, etc.)")
    responsive_breakpoints: List[str] = Field(description="Responsive breakpoints")
    color_palette: str = Field(description="Color palette guidelines")
    typography: str = Field(description="Typography system")


class CompleteFactorySpec(BaseModel):
    """Complete factory specification from interview."""

    # Basic info
    factory_name: str
    domain_name: str
    description: str

    # Business context
    industry: str
    target_users: List[str]
    core_features: List[str]
    standards_compliance: List[str]
    business_constraints: List[str]

    # Technical specifications
    programming_language: str
    web_framework: str
    database_type: str
    authentication_method: str
    deployment_target: str

    # Standards
    engineering_standards: EngineeringStandard
    uiux_standards: Optional[UIUXStandard] = None

    # Environment & Integration
    environment_variables: List[EnvironmentVariable]
    third_party_integrations: List[str]

    # Team preferences
    preferred_ai_models: List[str]
    code_review_level: str  # "strict", "moderate", "relaxed"


# ============================================================================
# Interview Agent
# ============================================================================

@dataclass
class InterviewDeps:
    """Dependencies for interview agent."""
    conversation_history: List[Dict[str, str]]


INTERVIEWER_PROMPT = """
You are a **Software Factory Consultant** helping users define their software project.

## Your Mission

Conduct a friendly, conversational interview to gather all information needed to
create a software factory. Ask follow-up questions, suggest best practices, and
help users think through their requirements.

## Interview Topics (in order)

### 1. Business Domain
- What industry/domain? (e.g., "e-commerce", "healthcare", "fintech")
- Who are the users? (e.g., "small business owners", "doctors")
- What's the core problem being solved?

### 2. Core Features
- What are the 3-5 main features?
- Any critical integrations? (Stripe, AWS, etc.)
- Special requirements? (real-time, high-volume, etc.)

### 3. Compliance & Standards
- Any industry standards? (HIPAA, PCI-DSS, GDPR, etc.)
- Regulatory requirements?
- Data retention policies?

### 4. Technical Preferences
- Programming language? (suggest Python if unsure)
- Web framework? (FastAPI, Django, Flask?)
- Database? (PostgreSQL, MongoDB, etc.)
- Authentication? (OAuth2, JWT, sessions?)

### 5. Engineering Standards
- Code style preferences?
- Testing coverage requirements?
- Documentation level?

### 6. UI/UX Standards (if applicable)
- Need a UI? (web app, mobile, API only?)
- Design system preferences?
- Accessibility requirements?

### 7. Environment & Integrations
- What API keys will be needed? (Stripe, SendGrid, AWS, etc.)
- External services to integrate?
- Deployment target? (AWS, Docker, Heroku, etc.)

### 8. Team Preferences
- Preferred AI models for agents? (Claude, GPT-4, etc.)
- How strict on code review? (strict/moderate/relaxed)

## Conversation Style

- Be friendly and conversational
- Ask one question at a time
- Provide suggestions when helpful
- Summarize what you've learned so far
- Confirm understanding before moving on

## Example Interaction

User: "I want to build a SaaS product"

You: "Great! Let's design your software factory together. 🚀

First, what industry or domain is this SaaS product for? For example:
- E-commerce (online stores)
- Healthcare (patient management)
- Finance (accounting, payments)
- Education (learning management)
- Something else?

This helps me understand what standards and integrations you'll need."

User: "It's for restaurant reservations"

You: "Perfect! Restaurant reservation systems are a great use case.

Who are the main users? For example:
- Restaurant owners/managers
- Restaurant staff (hosts, servers)
- Diners making reservations
- All of the above?

This helps me design the right features and permissions."

## Output

When you have all information, return a CompleteFactorySpec object with everything filled out.
"""

interviewer = Agent(
    'anthropic:claude-sonnet-4-5',
    deps_type=InterviewDeps,
    system_prompt=INTERVIEWER_PROMPT
)


async def conduct_interview() -> CompleteFactorySpec:
    """Conduct the interactive interview."""

    print("\n" + "="*60)
    print("🤖 SOFTWARE FACTORY INTERVIEW")
    print("="*60)
    print("""
I'll help you define your software factory through a conversation.
We'll cover:
- Business domain and users
- Core features
- Compliance requirements
- Technical stack
- Engineering standards
- Environment variables needed

Let's start!
    """)

    conversation_history = []
    deps = InterviewDeps(conversation_history=conversation_history)

    # Initial prompt
    initial_message = """
Hi! I'm your Software Factory Consultant. I'll help you define your software project
so we can build a custom code generator for it.

Let's start with the basics:

**What type of software are you building?**

For example:
- "E-commerce platform for handmade goods"
- "Patient appointment scheduling for clinics"
- "Inventory management for warehouses"
- "CRM for real estate agents"

Just describe it in a sentence or two.
"""

    print(f"\n🤖 Assistant:\n{initial_message}")

    while True:
        # Get user input
        user_input = input("\n👤 You: ").strip()

        if not user_input:
            print("Please provide an answer.")
            continue

        if user_input.lower() in ['quit', 'exit', 'done']:
            print("Interview cancelled.")
            return None

        # Add to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Get AI response
        try:
            result = await interviewer.run(
                user_input,
                deps=deps,
                output_type=None  # Let agent decide when to output spec
            )

            # Check if we got a complete spec
            if isinstance(result.output, CompleteFactorySpec):
                print("\n✅ Interview complete! Here's what I gathered:\n")
                return result.output

            # Continue conversation
            response = result.output
            conversation_history.append({
                "role": "assistant",
                "content": response
            })

            print(f"\n🤖 Assistant:\n{response}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Let's try again.")


def generate_env_file(spec: CompleteFactorySpec, output_path: str = ".env.example"):
    """Generate .env.example file from spec."""

    content = f"""# {spec.factory_name} - Environment Variables
# Generated by Factory Interview

# ============================================================================
# REQUIRED VARIABLES
# ============================================================================

"""

    # Group by category
    by_category: Dict[str, List[EnvironmentVariable]] = {}
    for var in spec.environment_variables:
        if var.category not in by_category:
            by_category[var.category] = []
        by_category[var.category].append(var)

    # Write each category
    category_names = {
        "api_key": "API Keys & Authentication",
        "database": "Database Configuration",
        "feature_flag": "Feature Flags",
        "service_url": "External Services",
        "config": "Application Configuration"
    }

    for category, vars in by_category.items():
        content += f"# {category_names.get(category, category.title())}\n"

        for var in vars:
            content += f"# {var.description}\n"
            if not var.required:
                content += "# (Optional)\n"
            content += f"# Example: {var.example}\n"

            if var.default_value:
                content += f"{var.name}={var.default_value}\n"
            else:
                content += f"{var.name}=\n"

            content += "\n"

    # Write file
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Generated {output_path}")


def generate_engineering_standards_doc(spec: CompleteFactorySpec, output_path: str = "ENGINEERING_STANDARDS.md"):
    """Generate engineering standards documentation."""

    content = f"""# Engineering Standards - {spec.factory_name}

## Code Style

**Style Guide**: {spec.engineering_standards.code_style}

**Formatter**: {spec.engineering_standards.formatting}

**Type Checking**: {spec.engineering_standards.type_checking}

## Linting Rules

"""

    for rule in spec.engineering_standards.linting_rules:
        content += f"- {rule}\n"

    content += f"""

## Documentation

{spec.engineering_standards.documentation}

## Testing Standards

"""

    for key, value in spec.engineering_standards.testing.items():
        content += f"**{key.title()}**: {value}\n\n"

    if spec.uiux_standards:
        content += f"""

## UI/UX Standards

**Design System**: {spec.uiux_standards.design_system}

**Component Library**: {spec.uiux_standards.component_library}

### Accessibility

"""
        for std in spec.uiux_standards.accessibility:
            content += f"- {std}\n"

        content += f"""

### Typography

{spec.uiux_standards.typography}

### Color Palette

{spec.uiux_standards.color_palette}

### Responsive Breakpoints

"""
        for bp in spec.uiux_standards.responsive_breakpoints:
            content += f"- {bp}\n"

    # Write file
    with open(output_path, 'w') as f:
        f.write(content)

    print(f"✅ Generated {output_path}")


async def main():
    """Main entry point."""

    # Conduct interview
    spec = await conduct_interview()

    if not spec:
        return

    # Show summary
    print("\n" + "="*60)
    print("📋 FACTORY SPECIFICATION SUMMARY")
    print("="*60)

    print(f"\n🏭 Factory: {spec.factory_name}")
    print(f"   Domain: {spec.domain_name}")
    print(f"   Industry: {spec.industry}")

    print(f"\n🎯 Target Users:")
    for user in spec.target_users:
        print(f"   - {user}")

    print(f"\n⚙️  Tech Stack:")
    print(f"   Language: {spec.programming_language}")
    print(f"   Framework: {spec.web_framework}")
    print(f"   Database: {spec.database_type}")

    print(f"\n📜 Compliance:")
    for std in spec.standards_compliance:
        print(f"   - {std}")

    print(f"\n🔌 Integrations:")
    for integration in spec.third_party_integrations:
        print(f"   - {integration}")

    print(f"\n🔑 Environment Variables: {len(spec.environment_variables)}")

    # Generate artifacts
    print("\n" + "="*60)
    print("GENERATING ARTIFACTS")
    print("="*60)

    generate_env_file(spec, f"{spec.factory_name}.env.example")
    generate_engineering_standards_doc(spec, f"{spec.factory_name}_ENGINEERING.md")

    # Save spec as JSON
    import json
    spec_file = f"{spec.factory_name}_spec.json"
    with open(spec_file, 'w') as f:
        json.dump(spec.model_dump(), f, indent=2)
    print(f"✅ Generated {spec_file}")

    # Offer to create factory
    create = input("\n🚀 Create factory now? (y/n): ").strip().lower()

    if create == 'y':
        from genesis import GenesisEngine

        # Build domain description from spec
        domain_desc = f"""
{spec.description}

Industry: {spec.industry}

Target Users:
{chr(10).join(f"- {user}" for user in spec.target_users)}

Core Features:
{chr(10).join(f"- {feature}" for feature in spec.core_features)}

Standards & Compliance:
{chr(10).join(f"- {std}" for std in spec.standards_compliance)}

Technical Requirements:
- Language: {spec.programming_language}
- Framework: {spec.web_framework}
- Database: {spec.database_type}
- Auth: {spec.authentication_method}
- Deployment: {spec.deployment_target}

Integrations:
{chr(10).join(f"- {integration}" for integration in spec.third_party_integrations)}

Engineering Standards:
- Code Style: {spec.engineering_standards.code_style}
- Formatter: {spec.engineering_standards.formatting}
- Type Checking: {spec.engineering_standards.type_checking}
- Testing: {spec.engineering_standards.testing}
        """

        print("\n🏗️  Creating factory...")

        engine = GenesisEngine.from_env()
        factory = await engine.create_factory(
            tenant_id=spec.factory_name.lower().replace(' ', '_'),
            domain_description=domain_desc,
            display_name=spec.factory_name
        )

        print(f"\n✅ Factory created!")
        print(f"   Build features with: factory.build_feature('...')")

    print("\n🎉 Done!")


if __name__ == "__main__":
    asyncio.run(main())
