

# Complete Guide: Viewing Results, Defining Factories, and Standards

This guide answers your key questions about the Genesis Engine.

## 1. How to See Factory Results

### Quick View

```bash
python3 examples/view_factory_results.py
```

This will:
- ✅ Find the latest generated code
- ✅ Show statistics (files, lines of code)
- ✅ List models, APIs, services, tests
- ✅ Let you browse and preview files
- ✅ Export analysis to JSON

### Manual Exploration

Generated code is in `./workspace/`:

```bash
# List all workspaces
ls -la ./workspace/

# View latest
ls -la ./workspace/snapshots/*/workspace/

# Browse generated code
cd ./workspace/snapshots/SNAPSHOT_ID/workspace/
tree app/
```

### Workspace Structure

```
workspace/
├── SNAPSHOT_ID/
│   └── workspace/
│       ├── CONTEXT.md              # Domain knowledge
│       ├── app/
│       │   ├── models/             # Database models
│       │   ├── schemas/            # Pydantic schemas
│       │   ├── api/                # API endpoints
│       │   ├── services/           # Business logic
│       │   ├── repositories/       # Data access
│       │   └── workers/            # Background jobs
│       ├── tests/                  # Test files
│       ├── alembic/                # DB migrations
│       ├── docs/                   # Documentation
│       └── .env.example            # Environment template
```

### View Specific Files

```bash
# View a model
cat ./workspace/.../app/models/appointment.py

# View API endpoint
cat ./workspace/.../app/api/appointments.py

# View tests
cat ./workspace/.../tests/test_appointments.py

# Check CONTEXT.md for domain knowledge
cat ./workspace/.../CONTEXT.md
```

## 2. AI Interview Tool for Factory Definition

### Run the Interactive Interview

```bash
python3 examples/factory_interview.py
```

### What It Does

The AI will ask you questions about:

1. **Business Domain**
   - "What industry is this for?"
   - "Who are your users?"
   - "What problem are you solving?"

2. **Core Features**
   - "What are the main 3-5 features?"
   - "Any critical integrations?"
   - "Special requirements?"

3. **Compliance**
   - "Any industry standards?" (HIPAA, PCI-DSS, etc.)
   - "Regulatory requirements?"
   - "Data retention policies?"

4. **Technical Preferences**
   - "Programming language?"
   - "Web framework?"
   - "Database type?"
   - "Authentication method?"

5. **Engineering Standards**
   - "Code style preferences?"
   - "Testing coverage requirements?"
   - "Documentation level?"

6. **UI/UX Standards** (if applicable)
   - "Design system?"
   - "Component library?"
   - "Accessibility requirements?"

7. **Environment Variables**
   - "What API keys needed?" (Stripe, SendGrid, AWS, etc.)
   - "External services?"
   - "Deployment target?"

8. **Team Preferences**
   - "Preferred AI models?"
   - "Code review strictness?"

### Example Conversation

```
🤖 What type of software are you building?

👤 SaaS platform for restaurant reservations

🤖 Great! Who are the main users?
   - Restaurant owners/managers
   - Restaurant staff
   - Diners
   - All of the above?

👤 All of the above

🤖 Perfect! What are the core features? (3-5 main ones)

👤 - Online booking system
   - Table management
   - Waitlist management
   - Customer notifications

... (continues) ...

✅ Interview complete!

📋 Generating:
   ✓ restaurant_reservations.env.example
   ✓ restaurant_reservations_ENGINEERING.md
   ✓ restaurant_reservations_spec.json

🚀 Create factory now? (y/n): y

✅ Factory created!
```

### Generated Artifacts

After the interview, you get:

1. **`.env.example`** - All environment variables needed
2. **`ENGINEERING_STANDARDS.md`** - Code quality rules
3. **`spec.json`** - Complete factory specification
4. **Factory** - Ready to build features!

## 3. Defining Engineering & UI/UX Standards

### Method 1: Via Interview (Easiest)

The interview tool asks about standards and generates them automatically.

### Method 2: Programmatically

```python
from genesis.standards import (
    EngineeringStandardsSpec,
    UIUXStandardsSpec,
    LintingLevel,
    AccessibilityLevel
)

# Define engineering standards
eng_standards = EngineeringStandardsSpec(
    style_guide="PEP 8",
    formatter="black",
    formatter_config={"line_length": 100},

    type_checker="mypy",
    type_strictness="strict",

    linter="ruff",
    linting_level=LintingLevel.STRICT,
    enabled_rules=["E", "W", "F", "I", "B", "C4", "UP"],
    ignored_rules=["E501"],  # Line too long (handled by formatter)

    test_framework="pytest",
    min_coverage=90,  # 90% coverage required
    coverage_enforcement="strict",
    property_testing=True,  # Use Hypothesis

    docstring_style="Google",
    require_docstrings=["public_functions", "classes", "modules"],

    security_scanning=True,
    dependency_checker="safety",

    pre_commit_hooks=["format", "lint", "type-check", "test"]
)

# Define UI/UX standards
uiux_standards = UIUXStandardsSpec(
    design_system="Material Design 3",
    component_library="MUI (Material-UI)",
    style_approach="tailwind",

    accessibility_level=AccessibilityLevel.AA,
    accessibility_requirements=[
        "WCAG 2.1 AA compliance",
        "Keyboard navigation for all interactive elements",
        "Screen reader compatibility",
        "Color contrast ratio 4.5:1 minimum",
        "Alt text for all images",
        "Focus indicators visible",
        "No content flashing faster than 3 times/second"
    ],

    responsive_breakpoints={
        "xs": "0px",
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px",
        "2xl": "1536px"
    },
    mobile_first=True,

    font_family_primary="Inter, system-ui, sans-serif",
    font_family_mono="'Fira Code', Consolas, monospace",
    type_scale="1.25 (Major Third)",

    color_palette={
        "primary": "#1976D2",      # Blue
        "secondary": "#DC004E",    # Pink
        "success": "#2E7D32",      # Green
        "warning": "#ED6C02",      # Orange
        "error": "#D32F2F",        # Red
        "info": "#0288D1",         # Light Blue
        "background": "#FFFFFF",
        "surface": "#F5F5F5",
        "text": "#212121"
    },
    dark_mode=True,

    spacing_unit="8px",  # Material Design standard

    icon_library="Material Icons",

    enable_animations=True,
    animation_duration="300ms",
    respect_prefers_reduced_motion=True
)

# Use in factory creation
# (Add to FactoryBlueprint or pass to interview results)
```

### Method 3: In Blueprint Definition

```python
from genesis.genesis_agent import FactoryBlueprint

blueprint = FactoryBlueprint(
    # ... other fields ...

    engineering_standards=eng_standards,
    uiux_standards=uiux_standards,

    # Standards will be enforced by:
    # - Builder agent (follows coding rules)
    # - QA agent (runs linters, checks coverage)
    # - Accessibility assistant (reviews UI code)
)
```

### Using Specialized Assistants

```python
from genesis.standards import (
    create_accessibility_assistant,
    create_security_assistant
)

# Add to your factory
accessibility_assistant = create_accessibility_assistant()
security_assistant = create_security_assistant()

# Assistants are invoked automatically:
# - A11y assistant: After UI components are built
# - Security assistant: Before deployment
# - They review code and suggest improvements
```

## 4. Defining Environment Variables & API Keys

### Method 1: Via Interview

The interview asks what integrations you need and generates `.env.example` automatically.

### Method 2: Programmatically

```python
from genesis.standards import EnvironmentVariableSpec, EnvironmentVariableType

# Define all env vars your generated software will need
env_vars = [
    # API Keys
    EnvironmentVariableSpec(
        name="STRIPE_API_KEY",
        description="Stripe API key for payment processing",
        var_type=EnvironmentVariableType.API_KEY,
        required=True,
        example="sk_test_51A1B2C3...",
        sensitive=True  # Never log this!
    ),

    EnvironmentVariableSpec(
        name="SENDGRID_API_KEY",
        description="SendGrid for transactional emails",
        var_type=EnvironmentVariableType.API_KEY,
        required=True,
        example="SG.abc123...",
        sensitive=True
    ),

    # Database
    EnvironmentVariableSpec(
        name="DATABASE_URL",
        description="PostgreSQL connection string",
        var_type=EnvironmentVariableType.DATABASE_URL,
        required=True,
        example="postgresql://user:pass@localhost:5432/dbname",
        sensitive=True
    ),

    # Service URLs
    EnvironmentVariableSpec(
        name="REDIS_URL",
        description="Redis for caching and sessions",
        var_type=EnvironmentVariableType.SERVICE_URL,
        required=False,
        default_value="redis://localhost:6379/0",
        example="redis://localhost:6379/0",
        sensitive=False
    ),

    # Feature Flags
    EnvironmentVariableSpec(
        name="ENABLE_ANALYTICS",
        description="Enable analytics tracking",
        var_type=EnvironmentVariableType.FEATURE_FLAG,
        required=False,
        default_value="false",
        example="true",
        validation="true|false",
        sensitive=False
    ),

    # Configuration
    EnvironmentVariableSpec(
        name="LOG_LEVEL",
        description="Application log level",
        var_type=EnvironmentVariableType.CONFIG,
        required=False,
        default_value="INFO",
        example="DEBUG",
        validation="DEBUG|INFO|WARNING|ERROR",
        sensitive=False
    ),

    EnvironmentVariableSpec(
        name="MAX_UPLOAD_SIZE_MB",
        description="Maximum file upload size in MB",
        var_type=EnvironmentVariableType.CONFIG,
        required=False,
        default_value="10",
        example="25",
        validation="^[0-9]+$",
        sensitive=False
    )
]

# Factory will automatically:
# 1. Generate .env.example with all these variables
# 2. Add validation code to check required vars on startup
# 3. Create config.py that loads and validates them
# 4. Mark sensitive vars to never be logged
```

### Generated `.env.example`

```bash
# Generated by Factory Interview

# ============================================================================
# API Keys & Authentication
# ============================================================================

# Stripe API key for payment processing
# Example: sk_test_51A1B2C3...
STRIPE_API_KEY=

# SendGrid for transactional emails
# Example: SG.abc123...
SENDGRID_API_KEY=

# ============================================================================
# Database Configuration
# ============================================================================

# PostgreSQL connection string
# Example: postgresql://user:pass@localhost:5432/dbname
DATABASE_URL=

# ============================================================================
# External Services
# ============================================================================

# Redis for caching and sessions
# (Optional)
# Example: redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# ============================================================================
# Feature Flags
# ============================================================================

# Enable analytics tracking
# (Optional)
# Example: true
ENABLE_ANALYTICS=false

# ============================================================================
# Application Configuration
# ============================================================================

# Application log level
# (Optional)
# Example: DEBUG
LOG_LEVEL=INFO

# Maximum file upload size in MB
# (Optional)
# Example: 25
MAX_UPLOAD_SIZE_MB=10
```

### Generated Config Validation

The factory automatically generates validation code:

```python
# Generated: app/config.py

from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # API Keys (required, sensitive)
    stripe_api_key: str = Field(..., description="Stripe API key")
    sendgrid_api_key: str = Field(..., description="SendGrid API key")

    # Database (required, sensitive)
    database_url: str = Field(..., description="PostgreSQL URL")

    # Services (optional)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection"
    )

    # Feature flags (optional)
    enable_analytics: bool = Field(
        default=False,
        description="Enable analytics"
    )

    # Config (optional)
    log_level: str = Field(
        default="INFO",
        description="Log level"
    )

    max_upload_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max upload size"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if v not in allowed:
            raise ValueError(f"Must be one of {allowed}")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

        # Mark sensitive fields
        secrets = [
            "stripe_api_key",
            "sendgrid_api_key",
            "database_url"
        ]

# Load settings
settings = Settings()

# Validation happens automatically on import
# Missing required vars will raise clear error messages
```

## Complete Workflow Example

### 1. Run Interview

```bash
python3 examples/factory_interview.py
```

Answer questions about your project.

### 2. Review Generated Artifacts

```bash
ls -la
# my_project.env.example
# my_project_ENGINEERING.md
# my_project_spec.json
```

### 3. Create Factory

Interview offers to create factory automatically, or:

```python
from genesis import GenesisEngine
import json

# Load spec
with open('my_project_spec.json') as f:
    spec = json.load(f)

# Create factory
engine = GenesisEngine.from_env()
factory = await engine.create_factory_from_spec(spec)
```

### 4. Build Features

```bash
python3 -c "
import asyncio
from genesis import GenesisEngine

async def build():
    engine = GenesisEngine.from_env()
    factory = await engine.get_factory('my_project')

    result = await factory.build_feature('Add user authentication')
    print(f'Status: {result[\"status\"]}')

asyncio.run(build())
"
```

### 5. View Results

```bash
python3 examples/view_factory_results.py
```

### 6. Setup Environment

```bash
# Copy generated env template
cp my_project.env.example .env

# Fill in your actual API keys
nano .env

# Generated code validates on startup
python3 -m app.main
```

## Summary

| Task | Tool | Command |
|------|------|---------|
| **View Results** | Result viewer | `python3 examples/view_factory_results.py` |
| **Define Factory** | AI interview | `python3 examples/factory_interview.py` |
| **Set Standards** | In interview or code | See sections 3 & 4 above |
| **Environment Vars** | Auto-generated | `.env.example` created automatically |
| **Run Demo** | Genesis demo | `python3 examples/genesis_demo.py` |
| **Custom Example** | Parameter examples | `python3 examples/custom_factory_example.py` |

## Next Steps

1. **Try the interview**: `python3 examples/factory_interview.py`
2. **View generated code**: `python3 examples/view_factory_results.py`
3. **Customize standards**: See `genesis/standards.py`
4. **Build features**: Use your new factory!

All your generated software will automatically include:
- ✅ Environment validation
- ✅ Engineering standards enforcement
- ✅ UI/UX guidelines (if applicable)
- ✅ Security best practices
- ✅ Accessibility compliance
- ✅ Complete documentation

The Genesis Engine creates **production-ready** code generators tailored to your exact requirements! 🚀
