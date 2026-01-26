# Environment Templates & Code Assistants

Complete guide to reusable environment configurations and specialized code assistants.

## Overview

Based on the Genesis Engine's production `.env`, we've extracted:
- **Reusable environment templates** for different domains
- **8 specialized code assistants** for quality, security, and design review

## Environment Templates

### Base Template (All Factories)

Every factory includes these standard variables from `genesis/env_templates.py`:

#### AI API Keys
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...  # Primary (required)
OPENAI_API_KEY=sk-proj-...          # Fallback (optional)
GROQ_API_KEY=gsk_...                # Fast inference (optional)
GOOGLE_API_KEY=AIza...              # Alternative model (optional)
```

#### Genesis Engine Configuration
```bash
USE_DAGGER=true                     # Containerized builds
MAX_ITERATIONS=5                    # Self-healing attempts
GENESIS_WORKSPACE=/tmp/genesis      # Factory blueprints
WORKSPACE_ROOT=./workspace          # Generated code output
TENANT_ID=default                   # Multi-tenancy ID
```

#### Database
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/db
DB_POOL_SIZE=10
```

#### Vector Database (Milvus)
```bash
MILVUS_URI=http://localhost:19530
MILVUS_COLLECTION=factory_knowledge
```

#### Identity Management (Keycloak)
```bash
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=genesis
KEYCLOAK_CLIENT_ID=genesis-engine
KEYCLOAK_CLIENT_SECRET=
```

#### AWS (Optional)
```bash
AWS_REGION=us-west-2
DYNAMODB_TABLE=genesis_factories
S3_BUCKET=genesis-artifacts
```

#### Optimization
```bash
OPTIMIZE_AI_COSTS=true              # Use cheaper models for simple tasks
ENABLE_PROMPT_CACHE=true            # Anthropic caching
LOG_LEVEL=INFO
```

### Domain-Specific Templates

#### Healthcare Factory
```python
from genesis.env_templates import EnvTemplateBuilder

env_vars = EnvTemplateBuilder.build_healthcare_template()
```

Adds:
```bash
FHIR_SERVER_URL=https://fhir.server.com/fhir/R4
FHIR_CLIENT_ID=my-app-client-id
FHIR_CLIENT_SECRET=secret123
HIPAA_AUDIT_LOG_BUCKET=hipaa-audit-logs
PHI_ENCRYPTION_KEY_ID=arn:aws:kms:...
```

#### E-Commerce Factory
```python
env_vars = EnvTemplateBuilder.build_ecommerce_template()
```

Adds:
```bash
STRIPE_API_KEY=sk_test_51...
STRIPE_WEBHOOK_SECRET=whsec_...
SHIPSTATION_API_KEY=abc123...
SENDGRID_API_KEY=SG.abc123...
PRODUCT_IMAGE_CDN=https://cdn.cloudflare.com
```

#### Fintech Factory
```python
env_vars = EnvTemplateBuilder.build_fintech_template()
```

Adds:
```bash
PLAID_CLIENT_ID=abc123...
PLAID_SECRET=secret123...
PLAID_ENVIRONMENT=sandbox
FRAUD_DETECTION_API_KEY=fd_abc123...
KYC_PROVIDER_API_KEY=kyc_abc123...
```

## Using Environment Templates

### Method 1: In Factory Interview

The AI interview tool automatically selects the right template:

```bash
python3 examples/factory_interview.py
```

The AI asks about your domain and automatically includes:
- Base Genesis Engine variables
- Domain-specific integrations (FHIR, Stripe, etc.)
- AWS configuration if needed

Outputs `.env.example` with all variables documented.

### Method 2: Programmatically

```python
from genesis.env_templates import EnvTemplateBuilder

# Healthcare project
env_vars = EnvTemplateBuilder.build_healthcare_template()

# Generate .env.example file
content = EnvTemplateBuilder.generate_env_file(
    vars=env_vars,
    project_name="MyHealthApp",
    include_notes=True
)

with open(".env.example", "w") as f:
    f.write(content)
```

### Method 3: Custom Composition

```python
from genesis.env_templates import (
    BaseEnvTemplate,
    EcommerceEnvTemplate,
    EnvTemplateBuilder
)

# Start with base
env_vars = EnvTemplateBuilder.build_base_template()

# Add e-commerce specific
env_vars += EcommerceEnvTemplate.get_ecommerce_vars()

# Add AWS
env_vars = EnvTemplateBuilder.build_with_aws(env_vars)

# Add your custom variables
from genesis.standards import EnvironmentVariableSpec, EnvironmentVariableType

env_vars.append(
    EnvironmentVariableSpec(
        name="CUSTOM_API_KEY",
        description="My custom service API key",
        var_type=EnvironmentVariableType.API_KEY,
        required=True,
        example="custom_...",
        sensitive=True
    )
)

# Generate file
content = EnvTemplateBuilder.generate_env_file(env_vars, "MyProject")
```

## Code Assistants

8 specialized AI assistants for different aspects of development.

### Quality Assurance Assistants

#### 1. Accessibility Compliance Reviewer
```python
from genesis.assistants import create_accessibility_assistant

assistant = create_accessibility_assistant()
```

**Expertise:**
- WCAG 2.1 AA/AAA compliance
- Semantic HTML and ARIA
- Keyboard navigation
- Screen reader compatibility
- Color contrast analysis

**When to invoke:** After UI component implementation

**Example check:**
```python
# Reviews code for:
# - Proper heading hierarchy (h1 → h2 → h3)
# - Keyboard accessible interactive elements
# - Sufficient color contrast (4.5:1)
# - Meaningful alt text
# - Focus indicators
```

#### 2. Security Vulnerability Reviewer
```python
from genesis.assistants import create_security_assistant

assistant = create_security_assistant()
```

**Expertise:**
- OWASP Top 10 vulnerabilities
- SQL/XSS/CSRF protection
- Authentication & session management
- Sensitive data exposure
- Security misconfigurations

**When to invoke:** After feature implementation, before deployment

**Example check:**
```python
# Scans for:
# - SQL injection (parameterized queries?)
# - XSS vulnerabilities (input sanitization?)
# - Missing CSRF tokens
# - Unencrypted sensitive data
# - Insecure Direct Object References (IDOR)
```

#### 3. Performance Optimizer
```python
from genesis.assistants import create_performance_assistant

assistant = create_performance_assistant()
```

**Expertise:**
- Database query optimization (N+1, indexes)
- API response times
- Memory usage
- Async/concurrency issues
- Caching strategies

**When to invoke:** After tests pass, before production

**Example check:**
```python
# Identifies:
# - Missing indexes on foreign keys
# - N+1 query problems
# - Response times > 200ms
# - Blocking I/O in async code
# - Unbounded caches
```

### Design & UX Assistants

#### 4. UX Content Writer
```python
from genesis.assistants import create_ux_writer_assistant

assistant = create_ux_writer_assistant()
```

**Expertise:**
- Microcopy and UX writing
- Error messages
- Button labels
- Empty states
- Inclusive language

**When to invoke:** During UI implementation

**Example improvements:**
```python
# Before: "Error occurred"
# After:  "Email not found. Check spelling or create an account."

# Before: "Submit"
# After:  "Create Account"

# Before: "No data"
# After:  "No appointments yet. Schedule your first appointment."
```

### Architecture Assistants

#### 5. API Design Reviewer
```python
from genesis.assistants import create_api_designer_assistant

assistant = create_api_designer_assistant()
```

**Expertise:**
- RESTful API design
- HTTP methods and status codes
- Response format consistency
- Pagination
- API versioning

**When to invoke:** During architecture phase

**Example review:**
```python
# Checks:
# ✓ URLs are resource-oriented (/users not /getUsers)
# ✓ HTTP methods used correctly (POST for create, PUT for update)
# ✓ Status codes appropriate (201 Created, 404 Not Found)
# ✓ Responses consistently formatted
# ✓ Large lists paginated
```

#### 6. Database Schema Reviewer
```python
from genesis.assistants import create_database_assistant

assistant = create_database_assistant()
```

**Expertise:**
- PostgreSQL schema design
- Normalization
- Indexes and query optimization
- Migrations
- Data types

**When to invoke:** During data model design

**Example review:**
```python
# Checks:
# - Foreign keys have indexes
# - Appropriate data types (DECIMAL for money, not FLOAT)
# - TIMESTAMP WITH TIME ZONE for dates
# - NOT NULL constraints for required fields
# - EXPLAIN ANALYZE for slow queries
```

### Domain-Specific Assistants

#### 7. FHIR Compliance Reviewer
```python
from genesis.assistants import create_fhir_assistant

assistant = create_fhir_assistant()
```

**Expertise:**
- FHIR R4 specification
- Healthcare interoperability
- HIPAA compliance
- SMART on FHIR

**When to invoke:** During healthcare feature implementation

**Example check:**
```python
# Validates:
# - Resources conform to FHIR R4 spec
# - Cardinality rules (0..1, 1..1, 0..*, 1..*)
# - Code systems (LOINC, SNOMED, ICD-10)
# - References format (Patient/123)
# - HIPAA audit logging
```

#### 8. PCI-DSS Compliance Reviewer
```python
from genesis.assistants import create_pci_compliance_assistant

assistant = create_pci_compliance_assistant()
```

**Expertise:**
- PCI-DSS v4.0 compliance
- Payment card data security
- Tokenization
- Encryption requirements

**When to invoke:** Before handling any card data

**Example check:**
```python
# Enforces:
# - NEVER store CVV/CVC
# - NEVER store full PAN (use tokens)
# - TLS 1.2+ for data in transit
# - Strong encryption (AES-256) at rest
# - Logging/monitoring of CHD access
```

## Using Assistants in Factories

### Automatic Selection by Domain

```python
from genesis.assistants import get_assistants_for_domain

# Healthcare factory gets:
# - Security, Performance, API, Database (base)
# - FHIR Compliance
# - Accessibility (for patient portals)
assistants = get_assistants_for_domain("healthcare")

# E-commerce factory gets:
# - Security, Performance, API, Database (base)
# - PCI-DSS Compliance
# - Accessibility
# - UX Writer
assistants = get_assistants_for_domain("ecommerce")

# SaaS factory gets:
# - Security, Performance, API, Database (base)
# - Accessibility
# - UX Writer
assistants = get_assistants_for_domain("saas")
```

### In Factory Blueprint

```python
from genesis.genesis_agent import FactoryBlueprint
from genesis.assistants import get_assistants_for_domain

blueprint = FactoryBlueprint(
    factory_name="healthcare_factory",
    domain_name="healthcare",
    # ... other config ...

    # Add assistants
    assistants=get_assistants_for_domain("healthcare")
)
```

### Manual Workflow

```python
from genesis.assistants import (
    create_security_assistant,
    create_accessibility_assistant
)

# 1. Build feature
result = await factory.build_feature("Add patient registration")

# 2. Run security review
security = create_security_assistant()
security_issues = await review_code_with_assistant(
    security,
    result['generated_files']
)

# 3. Run accessibility review
a11y = create_accessibility_assistant()
a11y_issues = await review_code_with_assistant(
    a11y,
    result['ui_files']
)

# 4. Fix issues and rebuild
if security_issues or a11y_issues:
    await factory.fix_issues(security_issues + a11y_issues)
```

## View All Assistants

```python
from genesis.assistants import get_assistant_summary

print(get_assistant_summary())
```

Output:
```
# Genesis Engine - Code Assistants Catalog

## Quality Assurance

### A11y Compliance Reviewer
- **Role**: accessibility
- **When**: After UI component implementation, before QA approval

### Security Vulnerability Reviewer
- **Role**: security
- **When**: After feature implementation, before deployment

### Performance Optimizer
- **Role**: performance
- **When**: After feature passes tests, before production deployment

## Design & UX

### UX Content Writer
- **Role**: ux_writer
- **When**: During UI implementation, review all user-facing text

## Architecture

### API Design Reviewer
- **Role**: api_designer
- **When**: During architecture phase, review all API endpoints

### Database Schema Reviewer
- **Role**: database
- **When**: During data model design, before implementation

## Domain-Specific

### FHIR Compliance Reviewer
- **Role**: api_designer
- **When**: During healthcare feature implementation, review all FHIR resources

### PCI-DSS Compliance Reviewer
- **Role**: security
- **When**: During payment feature implementation, before handling any card data
```

## Complete Example: Healthcare Factory

```python
import asyncio
from genesis import GenesisEngine
from genesis.env_templates import EnvTemplateBuilder
from genesis.assistants import get_assistants_for_domain

async def main():
    # 1. Create environment template
    env_vars = EnvTemplateBuilder.build_healthcare_template()

    # Generate .env.example
    env_content = EnvTemplateBuilder.generate_env_file(
        vars=env_vars,
        project_name="MyHealthApp"
    )

    with open(".env.example", "w") as f:
        f.write(env_content)

    print("✅ Created .env.example with FHIR and HIPAA variables")

    # 2. Get recommended assistants for healthcare
    assistants = get_assistants_for_domain("healthcare")

    print(f"✅ Configured {len(assistants)} assistants:")
    for assistant in assistants:
        print(f"   - {assistant.name}")

    # 3. Create factory
    engine = GenesisEngine.from_env()
    factory = await engine.create_factory(
        tenant_id="my_clinic",
        domain_description="""
        FHIR-compliant EHR system for small clinics.
        - Patient demographics and scheduling
        - HIPAA audit logging
        - SMART on FHIR apps
        """,
        display_name="My Clinic EHR",
        assistants=assistants  # Add assistants to factory
    )

    print("✅ Created factory with specialized healthcare assistants")

    # 4. Build a feature
    result = await factory.build_feature(
        "Add patient appointment scheduling with FHIR Appointment resources"
    )

    print(f"✅ Built feature: {result['status']}")

    # Assistants automatically review:
    # - Security: HIPAA compliance, PHI protection
    # - FHIR: Resource structure, code systems
    # - Accessibility: Patient portal usability
    # - Performance: Query optimization
    # - API: RESTful design
    # - Database: Schema correctness

asyncio.run(main())
```

## Summary

| Component | Location | Purpose |
|-----------|----------|---------|
| **Environment Templates** | `genesis/env_templates.py` | Reusable .env variables by domain |
| **Code Assistants** | `genesis/assistants.py` | 8 specialized review agents |
| **Standards** | `genesis/standards.py` | Base specs (used by templates) |
| **Interview Tool** | `examples/factory_interview.py` | AI-driven setup (uses both) |

### Quick Start

1. **Run interview** to get custom environment and assistants:
   ```bash
   python3 examples/factory_interview.py
   ```

2. **Or use templates directly**:
   ```python
   from genesis.env_templates import EnvTemplateBuilder
   from genesis.assistants import get_assistants_for_domain

   env_vars = EnvTemplateBuilder.build_healthcare_template()
   assistants = get_assistants_for_domain("healthcare")
   ```

3. **Create factory** with generated config:
   ```python
   factory = await engine.create_factory(
       tenant_id="my_app",
       domain_description="...",
       environment_variables=env_vars,
       assistants=assistants
   )
   ```

Every factory gets production-ready configuration and expert code review automatically! 🚀
