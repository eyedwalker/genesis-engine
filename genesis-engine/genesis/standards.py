"""
Engineering and UX Standards for Factory Configuration.

Extends FactoryBlueprint with standardized specifications for:
- Code quality and engineering practices
- UI/UX design systems
- Environment variables and configuration
- Assistant agents for specialized tasks
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================================
# Environment Variables
# ============================================================================

class EnvironmentVariableType(str, Enum):
    """Types of environment variables."""
    API_KEY = "api_key"
    DATABASE_URL = "database_url"
    FEATURE_FLAG = "feature_flag"
    SERVICE_URL = "service_url"
    CONFIG = "config"
    SECRET = "secret"


class EnvironmentVariableSpec(BaseModel):
    """Specification for an environment variable."""
    name: str = Field(description="Variable name (e.g., 'STRIPE_API_KEY')")
    description: str = Field(description="What this variable is for")
    var_type: EnvironmentVariableType = Field(description="Variable type/category")
    required: bool = Field(default=True, description="Is this required?")
    default_value: Optional[str] = Field(default=None, description="Default if optional")
    example: str = Field(description="Example value")
    validation: Optional[str] = Field(
        default=None,
        description="Validation rule (regex, format, etc.)"
    )
    sensitive: bool = Field(
        default=False,
        description="Should this be kept secret? (never log)"
    )


# ============================================================================
# Engineering Standards
# ============================================================================

class LintingLevel(str, Enum):
    """Linting strictness levels."""
    STRICT = "strict"       # All warnings are errors
    MODERATE = "moderate"   # Common issues enforced
    RELAXED = "relaxed"     # Basic checks only


class EngineeringStandardsSpec(BaseModel):
    """Engineering and code quality standards."""

    # Code Style
    style_guide: str = Field(
        default="PEP 8",
        description="Code style guide to follow"
    )

    formatter: str = Field(
        default="black",
        description="Code formatter (black, prettier, etc.)"
    )

    formatter_config: Dict[str, Any] = Field(
        default_factory=lambda: {"line_length": 100},
        description="Formatter configuration"
    )

    # Type Checking
    type_checker: str = Field(
        default="mypy",
        description="Type checker to use"
    )

    type_strictness: str = Field(
        default="strict",
        description="Type checking strictness (strict, moderate, none)"
    )

    # Linting
    linter: str = Field(
        default="ruff",
        description="Linter to use"
    )

    linting_level: LintingLevel = Field(
        default=LintingLevel.MODERATE,
        description="How strict should linting be?"
    )

    enabled_rules: List[str] = Field(
        default_factory=lambda: [
            "E",  # pycodestyle errors
            "W",  # pycodestyle warnings
            "F",  # pyflakes
            "I",  # isort
            "B",  # bugbear
        ],
        description="Enabled linting rules"
    )

    ignored_rules: List[str] = Field(
        default_factory=list,
        description="Rules to ignore"
    )

    # Testing
    test_framework: str = Field(
        default="pytest",
        description="Testing framework"
    )

    min_coverage: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Minimum test coverage percentage"
    )

    coverage_enforcement: str = Field(
        default="moderate",
        description="How to enforce coverage (strict, moderate, none)"
    )

    property_testing: bool = Field(
        default=False,
        description="Use property-based testing (Hypothesis)?"
    )

    # Documentation
    docstring_style: str = Field(
        default="Google",
        description="Docstring format (Google, NumPy, Sphinx)"
    )

    require_docstrings: List[str] = Field(
        default_factory=lambda: ["public_functions", "classes"],
        description="Where docstrings are required"
    )

    documentation_tool: str = Field(
        default="mkdocs",
        description="Documentation generator"
    )

    # Security
    security_scanning: bool = Field(
        default=True,
        description="Run security vulnerability scanning?"
    )

    dependency_checker: str = Field(
        default="safety",
        description="Dependency vulnerability checker"
    )

    # Git Hooks
    pre_commit_hooks: List[str] = Field(
        default_factory=lambda: ["format", "lint", "type-check"],
        description="Pre-commit hooks to enforce"
    )


# ============================================================================
# UI/UX Standards
# ============================================================================

class AccessibilityLevel(str, Enum):
    """WCAG accessibility levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class UIUXStandardsSpec(BaseModel):
    """UI/UX design and implementation standards."""

    # Design System
    design_system: str = Field(
        description="Design system (Material Design, Fluent, custom)"
    )

    component_library: str = Field(
        description="Component library (MUI, Ant Design, Shadcn, etc.)"
    )

    style_approach: str = Field(
        default="tailwind",
        description="Styling approach (tailwind, css-modules, styled-components)"
    )

    # Accessibility
    accessibility_level: AccessibilityLevel = Field(
        default=AccessibilityLevel.AA,
        description="WCAG compliance level"
    )

    accessibility_requirements: List[str] = Field(
        default_factory=lambda: [
            "Keyboard navigation support",
            "Screen reader compatibility",
            "Sufficient color contrast (4.5:1)",
            "Alt text for all images"
        ],
        description="Specific accessibility requirements"
    )

    # Responsive Design
    responsive_breakpoints: Dict[str, str] = Field(
        default_factory=lambda: {
            "mobile": "640px",
            "tablet": "768px",
            "desktop": "1024px",
            "wide": "1280px"
        },
        description="Responsive breakpoints"
    )

    mobile_first: bool = Field(
        default=True,
        description="Use mobile-first approach?"
    )

    # Typography
    font_family_primary: str = Field(
        default="Inter, system-ui, sans-serif",
        description="Primary font stack"
    )

    font_family_mono: str = Field(
        default="'Fira Code', monospace",
        description="Monospace font for code"
    )

    type_scale: str = Field(
        default="1.25 (Major Third)",
        description="Typographic scale ratio"
    )

    # Color System
    color_palette: Dict[str, str] = Field(
        default_factory=lambda: {
            "primary": "#0066CC",
            "secondary": "#6C757D",
            "success": "#28A745",
            "warning": "#FFC107",
            "error": "#DC3545",
            "neutral": "#F8F9FA"
        },
        description="Color palette"
    )

    dark_mode: bool = Field(
        default=True,
        description="Support dark mode?"
    )

    # Spacing
    spacing_unit: str = Field(
        default="4px",
        description="Base spacing unit"
    )

    # Icons
    icon_library: str = Field(
        default="heroicons",
        description="Icon library to use"
    )

    # Animation
    enable_animations: bool = Field(
        default=True,
        description="Enable UI animations?"
    )

    animation_duration: str = Field(
        default="200ms",
        description="Standard animation duration"
    )

    respect_prefers_reduced_motion: bool = Field(
        default=True,
        description="Respect user's motion preferences?"
    )


# ============================================================================
# Assistant Agents
# ============================================================================

class AssistantRole(str, Enum):
    """Specialized assistant roles."""
    ACCESSIBILITY = "accessibility"     # A11y expert
    SECURITY = "security"              # Security reviewer
    PERFORMANCE = "performance"        # Performance optimizer
    UX_WRITER = "ux_writer"           # UX copy writer
    API_DESIGNER = "api_designer"     # API design expert
    DATABASE = "database"             # DB schema expert


class AssistantSpec(BaseModel):
    """Specification for a specialized assistant agent."""

    role: AssistantRole = Field(description="Assistant's role")

    name: str = Field(description="Assistant name")

    model: str = Field(
        default="anthropic:claude-sonnet-4-5",
        description="AI model to use"
    )

    system_prompt: str = Field(description="System prompt defining expertise")

    when_to_invoke: str = Field(
        description="When this assistant should be consulted"
    )

    tools_needed: List[str] = Field(
        default_factory=list,
        description="Tools this assistant needs"
    )


# Example assistants
def create_accessibility_assistant() -> AssistantSpec:
    """Create accessibility review assistant."""
    return AssistantSpec(
        role=AssistantRole.ACCESSIBILITY,
        name="A11y Reviewer",
        system_prompt="""
        You are an accessibility (a11y) expert specializing in WCAG 2.1 compliance.

        Review code for:
        - Semantic HTML usage
        - ARIA attributes (use sparingly, prefer semantic HTML)
        - Keyboard navigation (tab order, focus management)
        - Color contrast ratios
        - Screen reader compatibility
        - Alt text quality

        Flag violations and suggest fixes with code examples.
        """,
        when_to_invoke="After UI component implementation, before QA",
        tools_needed=["read_code", "run_accessibility_tests"]
    )


def create_security_assistant() -> AssistantSpec:
    """Create security review assistant."""
    return AssistantSpec(
        role=AssistantRole.SECURITY,
        name="Security Reviewer",
        system_prompt="""
        You are a security expert reviewing code for vulnerabilities.

        Check for:
        - SQL injection vectors
        - XSS vulnerabilities
        - CSRF protection
        - Authentication bypass
        - Insecure direct object references
        - Sensitive data exposure
        - Security misconfiguration

        Reference OWASP Top 10. Provide specific remediation steps.
        """,
        when_to_invoke="After feature implementation, before deployment",
        tools_needed=["read_code", "run_security_scanner"]
    )


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "EnvironmentVariableType",
    "EnvironmentVariableSpec",
    "LintingLevel",
    "EngineeringStandardsSpec",
    "AccessibilityLevel",
    "UIUXStandardsSpec",
    "AssistantRole",
    "AssistantSpec",
    "create_accessibility_assistant",
    "create_security_assistant",
]
