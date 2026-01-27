"""
Genesis Engine API Server

FastAPI backend providing:
- REST API for factory and assistant management
- WebSocket for real-time collaboration
- Code review with actual pattern matching
- SQLite persistence

Usage:
    uvicorn genesis.api.server:app --reload --port 8000
"""

import re
import asyncio
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import database module directly (avoid genesis/__init__.py which has heavy deps)
import sys
_db_path = Path(__file__).parent.parent / "database.py"
_spec = importlib.util.spec_from_file_location("database", _db_path)
db = importlib.util.module_from_spec(_spec)
sys.modules["genesis.database"] = db
_spec.loader.exec_module(db)


# ============================================================================
# Models
# ============================================================================

class FactoryCreate(BaseModel):
    """Request model for creating a factory"""
    name: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default="")
    assistants: List[str] = Field(default_factory=lambda: ["security", "performance"])


class FactoryResponse(BaseModel):
    """Response model for factory"""
    id: str
    name: str
    domain: str
    description: str
    status: str
    features_built: int
    created_at: str
    updated_at: str
    assistants: List[str]


class CodeReviewRequest(BaseModel):
    """Request model for code review"""
    code: str = Field(..., min_length=1)
    file_name: str = Field(default="untitled.py")
    language: str = Field(default="python")
    assistants: List[str] = Field(default_factory=lambda: ["security", "performance"])
    factory_id: Optional[str] = None


class Finding(BaseModel):
    """Single code review finding"""
    id: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    assistant: str
    line: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None


class CodeReviewResponse(BaseModel):
    """Response model for code review"""
    review_id: str
    status: str
    file_name: str
    language: str
    findings: List[Finding]
    summary: Dict[str, int]
    assistants_used: List[str]


class AssistantInfo(BaseModel):
    """Assistant information"""
    id: str
    name: str
    domain: str
    tags: List[str]
    description: str
    methods_count: int


# ============================================================================
# State Management
# ============================================================================

@dataclass
class ServerState:
    """Server state for assistants (loaded in memory)"""
    assistants: Dict[str, Any] = field(default_factory=dict)
    assistant_configs: Dict[str, Dict] = field(default_factory=dict)
    active_connections: Dict[str, Set[WebSocket]] = field(default_factory=dict)


state = ServerState()


def get_api_key(key_name: str = "anthropic_api_key") -> Optional[str]:
    """Get API key from database, falling back to environment variable"""
    import os

    # Try database first
    db_value = db.get_setting(key_name)
    if db_value:
        return db_value

    # Fallback to environment variable
    env_key = key_name.upper()
    return os.environ.get(env_key)


def get_ai_model() -> str:
    """Get configured AI model"""
    model = db.get_setting("ai_model")
    return model or "claude-sonnet-4-20250514"


# ============================================================================
# Code Review Patterns
# ============================================================================

# Security patterns
SECURITY_PATTERNS = {
    "sql_injection": {
        "patterns": [
            r'execute\s*\(\s*f["\']',
            r'execute\s*\(\s*["\'].*%s',
            r'cursor\.execute\s*\(\s*["\'].*\+',
            r'\.format\s*\(.*\).*execute',
        ],
        "severity": "critical",
        "title": "Potential SQL Injection",
        "description": "String interpolation in SQL query can lead to SQL injection attacks",
        "recommendation": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
    },
    "eval_usage": {
        "patterns": [r'\beval\s*\(', r'\bexec\s*\('],
        "severity": "critical",
        "title": "Dangerous eval/exec Usage",
        "description": "eval() and exec() can execute arbitrary code, leading to code injection",
        "recommendation": "Avoid eval/exec. Use ast.literal_eval() for safe literal evaluation"
    },
    "hardcoded_secrets": {
        "patterns": [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][A-Za-z0-9_-]{20,}["\']',
        ],
        "severity": "high",
        "title": "Potential Hardcoded Secret",
        "description": "Secrets should not be hardcoded in source code",
        "recommendation": "Use environment variables or a secrets manager"
    },
    "shell_injection": {
        "patterns": [
            r'os\.system\s*\(',
            r'subprocess\.call\s*\(\s*["\']',
            r'subprocess\.run\s*\(\s*f["\']',
            r'shell\s*=\s*True',
        ],
        "severity": "high",
        "title": "Potential Command Injection",
        "description": "Shell commands with user input can lead to command injection",
        "recommendation": "Use subprocess with shell=False and pass arguments as a list"
    },
    "insecure_random": {
        "patterns": [r'\brandom\.(random|randint|choice)\s*\('],
        "severity": "medium",
        "title": "Insecure Random Number Generator",
        "description": "random module is not cryptographically secure",
        "recommendation": "Use secrets module for security-sensitive randomness"
    },
    "debug_enabled": {
        "patterns": [r'DEBUG\s*=\s*True', r'debug\s*=\s*True'],
        "severity": "medium",
        "title": "Debug Mode Enabled",
        "description": "Debug mode should be disabled in production",
        "recommendation": "Set DEBUG=False in production environments"
    },
}

# Performance patterns
PERFORMANCE_PATTERNS = {
    "n_plus_one": {
        "patterns": [
            r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.query\s*\(',
            r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.get\s*\(',
            r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.filter\s*\(',
        ],
        "severity": "high",
        "title": "Potential N+1 Query",
        "description": "Database query inside a loop can cause performance issues",
        "recommendation": "Use eager loading, batch queries, or prefetch related data"
    },
    "inefficient_loop": {
        "patterns": [
            r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
            r'\+=\s*\[\w+\]',  # list concatenation in loop
        ],
        "severity": "medium",
        "title": "Inefficient Loop Pattern",
        "description": "This loop pattern may be inefficient",
        "recommendation": "Use enumerate() instead of range(len()), use list.extend() or comprehensions"
    },
    "global_import": {
        "patterns": [r'from\s+\w+\s+import\s+\*'],
        "severity": "low",
        "title": "Wildcard Import",
        "description": "Wildcard imports can pollute namespace and slow startup",
        "recommendation": "Import only what you need explicitly"
    },
    "no_caching": {
        "patterns": [
            r'def\s+get_\w+\s*\([^)]*\)\s*:\s*\n\s*.*return\s+requests\.get',
        ],
        "severity": "medium",
        "title": "Missing Cache",
        "description": "HTTP requests without caching can impact performance",
        "recommendation": "Consider caching responses using functools.lru_cache or a caching library"
    },
}

# Accessibility patterns (for frontend code)
ACCESSIBILITY_PATTERNS = {
    "missing_alt": {
        "patterns": [r'<img[^>]+(?<!alt=)[^>]*>', r'<img(?![^>]*alt=)'],
        "severity": "medium",
        "title": "Missing Alt Attribute",
        "description": "Images should have alt text for screen readers",
        "recommendation": "Add alt attribute: <img src='...' alt='Description of image'>"
    },
    "missing_label": {
        "patterns": [r'<input[^>]+(?<!aria-label)[^>]*(?<!id=)[^>]*>'],
        "severity": "medium",
        "title": "Missing Form Label",
        "description": "Form inputs should have associated labels",
        "recommendation": "Add <label for='input-id'> or aria-label attribute"
    },
    "no_keyboard_handler": {
        "patterns": [r'onClick\s*=.*(?!onKeyDown)'],
        "severity": "low",
        "title": "Missing Keyboard Handler",
        "description": "Click handlers should have keyboard equivalents",
        "recommendation": "Add onKeyDown handler for keyboard accessibility"
    },
}


def analyze_code(code: str, language: str, assistants: List[str]) -> List[Finding]:
    """Analyze code using pattern matching"""
    findings = []
    lines = code.split('\n')

    # Map assistants to pattern sets
    pattern_map = {
        "security": SECURITY_PATTERNS,
        "performance": PERFORMANCE_PATTERNS,
        "accessibility": ACCESSIBILITY_PATTERNS,
    }

    for assistant_id in assistants:
        patterns = pattern_map.get(assistant_id, {})

        for pattern_name, pattern_info in patterns.items():
            for pattern in pattern_info["patterns"]:
                try:
                    matches = list(re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE))
                    for match in matches:
                        # Find line number
                        line_num = code[:match.start()].count('\n') + 1

                        # Get code snippet
                        snippet_start = max(0, line_num - 2)
                        snippet_end = min(len(lines), line_num + 2)
                        snippet = '\n'.join(lines[snippet_start:snippet_end])

                        findings.append(Finding(
                            id=f"{assistant_id}-{pattern_name}-{line_num}",
                            severity=pattern_info["severity"],
                            title=pattern_info["title"],
                            description=pattern_info["description"],
                            assistant=assistant_id,
                            line=line_num,
                            code_snippet=snippet,
                            recommendation=pattern_info.get("recommendation")
                        ))
                        break  # Only report once per pattern type
                except re.error:
                    continue

    return findings


# ============================================================================
# Assistant Loader
# ============================================================================

def load_assistants():
    """Load all enhanced assistants"""
    genesis_path = Path(__file__).parent.parent

    for file in genesis_path.glob("assistants_enhanced_*.py"):
        if file.name == "assistants_enhanced_example.py":
            continue

        module_name = file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name in dir(module):
                if name.startswith("create_enhanced_"):
                    factory = getattr(module, name)
                    if callable(factory):
                        try:
                            config = factory()
                            if isinstance(config, dict) and "name" in config:
                                assistant_key = module_name.replace("assistants_enhanced_", "")
                                state.assistant_configs[assistant_key] = config

                                if "assistant_class" in config:
                                    state.assistants[assistant_key] = config["assistant_class"]()
                                break
                        except Exception:
                            continue
        except Exception as e:
            print(f"Warning: Could not load {module_name}: {e}")

    print(f"Loaded {len(state.assistants)} assistants")


# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    print("Genesis API Server starting...")

    # Initialize database
    db.init_db()

    # Load assistants
    load_assistants()

    # Create demo factories if database is empty
    factories = db.get_all_factories()
    if not factories:
        print("Creating demo factories...")
        db.create_factory(
            id="demo-healthcare",
            name="Healthcare Platform",
            domain="healthcare",
            description="HIPAA-compliant healthcare management platform",
            assistants=["security", "fhir", "accessibility"],
        )
        db.create_factory(
            id="demo-ecommerce",
            name="E-Commerce Engine",
            domain="e-commerce",
            description="PCI-DSS compliant online store platform",
            assistants=["security", "pci_dss", "performance"],
        )
        # Update demo factories with some features
        db.update_factory("demo-healthcare", features_built=45, status="active")
        db.update_factory("demo-ecommerce", features_built=32, status="active")

    yield

    print("Genesis API Server shutting down...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Genesis Engine API",
    description="Factory-as-a-Service Platform API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST Endpoints - Health & Root
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = db.get_stats()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "assistants_loaded": len(state.assistants),
        "factories_active": stats["active_factories"],
        "total_reviews": stats["total_reviews"]
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Genesis Engine API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "factories": "/api/factories",
            "assistants": "/api/assistants",
            "review": "/api/review",
            "stats": "/api/stats",
            "websocket": "/ws/{room_id}"
        }
    }


# ============================================================================
# REST Endpoints - Factories (Database-backed)
# ============================================================================

@app.get("/api/factories")
async def list_factories():
    """List all factories"""
    factories = db.get_all_factories()
    return factories


@app.post("/api/factories")
async def create_factory(request: FactoryCreate, background_tasks: BackgroundTasks):
    """Create a new factory"""
    factory_id = f"factory-{uuid.uuid4().hex[:8]}"

    factory = db.create_factory(
        id=factory_id,
        name=request.name,
        domain=request.domain,
        description=request.description,
        assistants=request.assistants,
    )

    # Simulate provisioning in background
    background_tasks.add_task(provision_factory, factory_id)

    return factory


async def provision_factory(factory_id: str):
    """Background task to provision a factory"""
    await asyncio.sleep(3)  # Simulate provisioning
    db.update_factory(factory_id, status="active")


@app.get("/api/factories/{factory_id}")
async def get_factory(factory_id: str):
    """Get factory by ID"""
    factory = db.get_factory(factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory


@app.patch("/api/factories/{factory_id}")
async def update_factory(factory_id: str, updates: Dict[str, Any]):
    """Update factory"""
    factory = db.update_factory(factory_id, **updates)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory


@app.delete("/api/factories/{factory_id}")
async def delete_factory(factory_id: str):
    """Delete a factory"""
    # Also delete setup tasks
    db.delete_setup_tasks_for_factory(factory_id)
    if not db.delete_factory(factory_id):
        raise HTTPException(status_code=404, detail="Factory not found")
    return {"status": "deleted", "id": factory_id}


# ============================================================================
# REST Endpoints - Setup Tasks (Onboarding Checklist)
# ============================================================================

class SetupTask(BaseModel):
    """Setup task model"""
    id: str
    factory_id: str
    category: str
    title: str
    description: str
    status: str
    task_type: str
    action_url: Optional[str] = None
    action_command: Optional[str] = None
    required: bool
    order_index: int
    metadata: Dict[str, Any] = {}
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: str


class SetupTaskUpdate(BaseModel):
    """Update model for setup task"""
    status: Optional[str] = None
    notes: Optional[str] = None
    completed_by: Optional[str] = None


class SetupProgress(BaseModel):
    """Setup progress summary"""
    total: int
    completed: int
    required_total: int
    required_completed: int
    percent: int
    by_category: Dict[str, Dict[str, int]]


class GenerateSetupRequest(BaseModel):
    """Request to generate setup tasks from a plan"""
    plan: Dict[str, Any]


@app.get("/api/factories/{factory_id}/setup")
async def get_factory_setup_tasks(factory_id: str):
    """Get all setup tasks for a factory"""
    factory = db.get_factory(factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    tasks = db.get_setup_tasks_for_factory(factory_id)
    progress = db.get_setup_progress(factory_id)

    return {
        "factory_id": factory_id,
        "tasks": tasks,
        "progress": progress
    }


@app.get("/api/factories/{factory_id}/setup/progress", response_model=SetupProgress)
async def get_factory_setup_progress(factory_id: str):
    """Get setup progress for a factory"""
    factory = db.get_factory(factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    return db.get_setup_progress(factory_id)


@app.patch("/api/factories/{factory_id}/setup/{task_id}")
async def update_setup_task(factory_id: str, task_id: str, update: SetupTaskUpdate):
    """Update a setup task status or notes"""
    task = db.get_setup_task(task_id)
    if not task or task["factory_id"] != factory_id:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = {k: v for k, v in update.model_dump().items() if v is not None}
    updated_task = db.update_setup_task(task_id, **updates)

    return updated_task


@app.post("/api/factories/{factory_id}/setup/generate")
async def generate_setup_tasks(factory_id: str, request: GenerateSetupRequest):
    """Generate setup tasks from a factory plan"""
    factory = db.get_factory(factory_id)
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    # Delete any existing setup tasks for this factory
    db.delete_setup_tasks_for_factory(factory_id)

    plan = request.plan
    tasks_created = []
    order = 0

    # Infrastructure tasks based on architecture
    architecture = plan.get("architecture", "")
    if architecture:
        tasks_created.append(db.create_setup_task(
            id=f"{factory_id}-infra-arch",
            factory_id=factory_id,
            category="infrastructure",
            title="Review Architecture Design",
            description=f"Review and confirm the recommended architecture: {architecture}",
            task_type="manual",
            required=True,
            order_index=order
        ))
        order += 1

    # Database setup
    data_models = plan.get("data_models", [])
    if data_models:
        tasks_created.append(db.create_setup_task(
            id=f"{factory_id}-infra-db",
            factory_id=factory_id,
            category="infrastructure",
            title="Set Up Database",
            description=f"Create database and tables for: {', '.join(data_models[:5])}",
            task_type="manual",
            required=True,
            order_index=order,
            metadata={"data_models": data_models}
        ))
        order += 1

    # Compliance-specific tasks
    compliance = plan.get("compliance", [])
    for comp in compliance:
        comp_lower = comp.lower()
        if "hipaa" in comp_lower:
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-compliance-hipaa",
                factory_id=factory_id,
                category="compliance",
                title="HIPAA Compliance Setup",
                description="Configure HIPAA-compliant data handling, encryption, and audit logging",
                task_type="manual",
                required=True,
                order_index=order
            ))
            order += 1
        elif "pci" in comp_lower:
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-compliance-pci",
                factory_id=factory_id,
                category="compliance",
                title="PCI-DSS Compliance Setup",
                description="Set up secure payment processing environment and data isolation",
                task_type="manual",
                required=True,
                order_index=order
            ))
            order += 1
        elif "gdpr" in comp_lower:
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-compliance-gdpr",
                factory_id=factory_id,
                category="compliance",
                title="GDPR Compliance Setup",
                description="Implement data consent, right to deletion, and data export features",
                task_type="manual",
                required=True,
                order_index=order
            ))
            order += 1

    # Integration-specific tasks
    integrations = plan.get("integrations", [])
    for integration in integrations:
        int_lower = integration.lower()

        # Payment providers
        if any(p in int_lower for p in ["stripe", "payment", "billing"]):
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-stripe",
                factory_id=factory_id,
                category="credentials",
                title="Configure Stripe API Keys",
                description="Create Stripe account and add API keys to environment",
                task_type="external",
                action_url="https://dashboard.stripe.com/apikeys",
                required=True,
                order_index=order,
                metadata={"env_vars": ["STRIPE_PUBLIC_KEY", "STRIPE_SECRET_KEY"]}
            ))
            order += 1

        # Auth providers
        elif any(p in int_lower for p in ["auth0", "authentication", "oauth"]):
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-auth",
                factory_id=factory_id,
                category="credentials",
                title="Configure Authentication Provider",
                description="Set up OAuth/authentication provider and add credentials",
                task_type="external",
                required=True,
                order_index=order,
                metadata={"env_vars": ["AUTH_CLIENT_ID", "AUTH_CLIENT_SECRET"]}
            ))
            order += 1

        # AWS
        elif "aws" in int_lower or "s3" in int_lower:
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-aws",
                factory_id=factory_id,
                category="credentials",
                title="Configure AWS Credentials",
                description="Set up AWS IAM user and add credentials for S3, Lambda, etc.",
                task_type="external",
                action_url="https://console.aws.amazon.com/iam/",
                required=True,
                order_index=order,
                metadata={"env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"]}
            ))
            order += 1

        # Database services
        elif any(p in int_lower for p in ["postgres", "mysql", "mongodb", "database"]):
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-db-ext",
                factory_id=factory_id,
                category="credentials",
                title=f"Configure Database Connection",
                description=f"Set up connection string for {integration}",
                task_type="manual",
                required=True,
                order_index=order,
                metadata={"env_vars": ["DATABASE_URL"]}
            ))
            order += 1

        # Email services
        elif any(p in int_lower for p in ["email", "sendgrid", "mailgun", "ses"]):
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-email",
                factory_id=factory_id,
                category="credentials",
                title="Configure Email Service",
                description=f"Set up email provider ({integration}) API keys",
                task_type="external",
                required=False,
                order_index=order,
                metadata={"env_vars": ["EMAIL_API_KEY", "EMAIL_FROM_ADDRESS"]}
            ))
            order += 1

        # Generic integration
        else:
            tasks_created.append(db.create_setup_task(
                id=f"{factory_id}-int-{integration.lower().replace(' ', '-')[:20]}",
                factory_id=factory_id,
                category="integration",
                title=f"Set Up {integration}",
                description=f"Configure integration with {integration}",
                task_type="manual",
                required=False,
                order_index=order
            ))
            order += 1

    # Security tasks based on recommendations
    security = plan.get("security_considerations", [])
    if security:
        tasks_created.append(db.create_setup_task(
            id=f"{factory_id}-security-review",
            factory_id=factory_id,
            category="configuration",
            title="Security Configuration Review",
            description="Review and implement security considerations: " + "; ".join(security[:3]),
            task_type="manual",
            required=True,
            order_index=order,
            metadata={"considerations": security}
        ))
        order += 1

    # Environment setup
    tasks_created.append(db.create_setup_task(
        id=f"{factory_id}-config-env",
        factory_id=factory_id,
        category="configuration",
        title="Create Environment File",
        description="Create .env file with all required environment variables",
        task_type="manual",
        required=True,
        order_index=order
    ))
    order += 1

    # Final verification
    tasks_created.append(db.create_setup_task(
        id=f"{factory_id}-config-verify",
        factory_id=factory_id,
        category="configuration",
        title="Verify Setup Complete",
        description="Run health checks and verify all systems are connected",
        task_type="automated",
        action_command="npm run verify",
        required=True,
        order_index=order
    ))

    return {
        "factory_id": factory_id,
        "tasks_created": len(tasks_created),
        "tasks": tasks_created
    }


# ============================================================================
# REST Endpoints - Code Review (Real Pattern Matching)
# ============================================================================

@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """Review code using pattern matching"""
    review_id = f"review-{uuid.uuid4().hex[:8]}"

    # Run pattern analysis
    findings = analyze_code(request.code, request.language, request.assistants)

    # Calculate summary
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        if finding.severity in summary:
            summary[finding.severity] += 1

    # Save to database
    db.create_review(
        id=review_id,
        file_name=request.file_name,
        code_snippet=request.code[:1000],  # First 1000 chars
        findings=[f.model_dump() for f in findings],
        assistants_used=request.assistants,
        factory_id=request.factory_id,
        language=request.language,
    )

    # Increment factory features if associated
    if request.factory_id:
        db.increment_features(request.factory_id)

    return CodeReviewResponse(
        review_id=review_id,
        status="completed",
        file_name=request.file_name,
        language=request.language,
        findings=findings,
        summary=summary,
        assistants_used=request.assistants
    )


@app.post("/api/review/ai", response_model=CodeReviewResponse)
async def review_code_ai(request: CodeReviewRequest):
    """Review code using Claude AI for deeper analysis"""
    api_key = get_api_key("anthropic_api_key")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI review requires Anthropic API key. Configure it in Settings."
        )

    review_id = f"review-{uuid.uuid4().hex[:8]}"

    # First run pattern analysis for quick wins
    pattern_findings = analyze_code(request.code, request.language, request.assistants)

    # Build AI prompt
    assistant_context = ", ".join(request.assistants)
    prompt = f"""You are an expert code reviewer specializing in {assistant_context}.

Analyze this {request.language} code for issues related to: {assistant_context}

CODE TO REVIEW:
```{request.language}
{request.code}
```

For each issue found, respond with a JSON array of findings. Each finding must have:
- severity: "critical", "high", "medium", or "low"
- title: Short title (max 50 chars)
- description: What's wrong and why it matters
- line: Line number where issue occurs (integer)
- recommendation: How to fix it

Focus on actionable, specific issues. Don't repeat the same issue multiple times.
Return ONLY a valid JSON array, no other text."""

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": get_ai_model(),
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"AI service error: {response.text}")

        result = response.json()
        ai_text = result["content"][0]["text"]

        # Parse AI response
        import json as json_lib
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in ai_text:
            ai_text = ai_text.split("```json")[1].split("```")[0]
        elif "```" in ai_text:
            ai_text = ai_text.split("```")[1].split("```")[0]

        ai_findings_raw = json_lib.loads(ai_text.strip())

        # Convert to Finding objects
        ai_findings = []
        for i, f in enumerate(ai_findings_raw):
            ai_findings.append(Finding(
                id=f"ai-{request.assistants[0] if request.assistants else 'general'}-{i}",
                severity=f.get("severity", "medium"),
                title=f.get("title", "Issue found"),
                description=f.get("description", ""),
                assistant="ai",
                line=f.get("line"),
                code_snippet=None,
                recommendation=f.get("recommendation")
            ))

        # Combine pattern + AI findings (deduplicate by line/title)
        seen = set()
        all_findings = []
        for f in pattern_findings + ai_findings:
            key = (f.line, f.title[:20] if f.title else "")
            if key not in seen:
                seen.add(key)
                all_findings.append(f)

    except json_lib.JSONDecodeError:
        # Fall back to pattern findings if AI parsing fails
        all_findings = pattern_findings
    except Exception as e:
        print(f"AI review error: {e}")
        all_findings = pattern_findings

    # Calculate summary
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in all_findings:
        if finding.severity in summary:
            summary[finding.severity] += 1

    # Save to database
    db.create_review(
        id=review_id,
        file_name=request.file_name,
        code_snippet=request.code[:1000],
        findings=[f.model_dump() for f in all_findings],
        assistants_used=request.assistants + ["ai"],
        factory_id=request.factory_id,
        language=request.language,
    )

    return CodeReviewResponse(
        review_id=review_id,
        status="completed",
        file_name=request.file_name,
        language=request.language,
        findings=all_findings,
        summary=summary,
        assistants_used=request.assistants + ["ai"]
    )


class FixRequest(BaseModel):
    """Request to generate a fix for code"""
    code: str
    finding_title: str
    finding_description: str
    recommendation: str
    language: str = "python"


class FixResponse(BaseModel):
    """Response with fixed code"""
    original_code: str
    fixed_code: str
    explanation: str


@app.post("/api/fix", response_model=FixResponse)
async def generate_fix(request: FixRequest):
    """Generate a fix for a code issue using AI"""
    api_key = get_api_key("anthropic_api_key")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Fix generation requires Anthropic API key. Configure it in Settings."
        )

    prompt = f"""You are an expert {request.language} developer. Fix the following code issue.

ISSUE: {request.finding_title}
DESCRIPTION: {request.finding_description}
RECOMMENDATION: {request.recommendation}

ORIGINAL CODE:
```{request.language}
{request.code}
```

Provide the FIXED code that resolves this issue. Only return the fixed code, no explanations.
Return the complete fixed code wrapped in a code block."""

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": get_ai_model(),
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="AI service error")

        result = response.json()
        ai_text = result["content"][0]["text"]

        # Extract code from response
        fixed_code = ai_text
        if "```" in ai_text:
            # Extract code block
            parts = ai_text.split("```")
            if len(parts) >= 2:
                code_block = parts[1]
                # Remove language identifier if present
                if code_block.startswith(request.language):
                    code_block = code_block[len(request.language):].strip()
                elif code_block.startswith("\n"):
                    code_block = code_block.strip()
                fixed_code = code_block

        return FixResponse(
            original_code=request.code,
            fixed_code=fixed_code.strip(),
            explanation=f"Fixed: {request.finding_title}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fix generation failed: {str(e)}")


class PlanQuestion(BaseModel):
    """Interview question for factory planning"""
    id: str
    question: str
    context: str
    options: Optional[List[str]] = None
    multiselect: bool = False  # Allow multiple selections


class FeatureSubPlan(BaseModel):
    """Detailed sub-plan for a feature"""
    feature: str  # Feature name
    description: str  # What this feature does
    tasks: List[str]  # Implementation tasks
    components: List[str] = []  # UI components needed
    api_routes: List[str] = []  # API endpoints for this feature
    data_models: List[str] = []  # Database models needed
    dependencies: List[str] = []  # Other features this depends on
    assistant_tools: List[str] = []  # Which assistants/tools to use
    estimated_effort: str = "medium"  # low, medium, high


class UIUXPreferences(BaseModel):
    """UI/UX design preferences"""
    style: str = "modern"  # modern, minimal, playful, corporate, etc.
    color_scheme: str = ""  # Primary colors or theme
    target_audience: str = ""  # Who the UI is designed for
    inspiration_urls: List[str] = []  # Figma, Builder.io, Dribbble, etc.
    key_pages: List[str] = []  # Main pages/screens needed
    component_library: str = ""  # Preferred UI library (shadcn, MUI, etc.)
    accessibility_level: str = "AA"  # WCAG level: A, AA, AAA
    responsive_priority: str = "mobile-first"  # mobile-first, desktop-first, both
    special_requirements: List[str] = []  # Dark mode, RTL, animations, etc.


class FactoryPlan(BaseModel):
    """Detailed factory plan"""
    name: str
    domain: str
    description: str
    architecture: str
    assistants: List[str]
    features: List[str]
    compliance: List[str]
    integrations: List[str]
    data_models: List[str] = []
    api_endpoints: List[str] = []
    security_considerations: List[str] = []
    estimated_complexity: str = "medium"
    # UI/UX preferences
    ui_ux: Optional[UIUXPreferences] = None
    # Detailed sub-plans for each feature
    feature_plans: List[FeatureSubPlan] = []


class DesignReference(BaseModel):
    """Design reference URL or description"""
    type: str  # "url", "description", "style_preset"
    value: str  # URL or description text
    notes: str = ""  # Additional notes about the reference


class PlanRequest(BaseModel):
    """Request for factory planning"""
    name: str
    domain: str
    description: str
    answers: Optional[Dict[str, str]] = None  # Answers to interview questions
    design_references: Optional[List[DesignReference]] = None  # UI/UX design references


class PlanResponse(BaseModel):
    """AI-generated factory plan"""
    status: str  # 'questions' or 'plan'
    questions: Optional[List[PlanQuestion]] = None
    plan: Optional[FactoryPlan] = None


@app.post("/api/factories/plan", response_model=PlanResponse)
async def plan_factory(request: PlanRequest):
    """Generate a factory plan with AI interview"""
    api_key = get_api_key("anthropic_api_key")
    if not api_key:
        # Return basic plan without AI
        return PlanResponse(
            status="plan",
            plan=FactoryPlan(
                name=request.name,
                domain=request.domain,
                description=request.description,
                architecture="VBD (Volatility-Based Decomposition)",
                assistants=["security", "performance"],
                features=["Basic CRUD operations", "Authentication", "API endpoints"],
                compliance=[],
                integrations=[],
                data_models=["User", "Session"],
                api_endpoints=["/api/users", "/api/auth"],
                security_considerations=["Input validation", "Authentication required"],
                estimated_complexity="medium"
            )
        )

    # Build design reference context if provided
    design_context = ""
    if request.design_references:
        design_parts = []
        for ref in request.design_references:
            if ref.type == "url":
                design_parts.append(f"- Reference URL: {ref.value}" + (f" ({ref.notes})" if ref.notes else ""))
            elif ref.type == "style_preset":
                design_parts.append(f"- Style preset: {ref.value}")
            else:
                design_parts.append(f"- Design note: {ref.value}")
        if design_parts:
            design_context = "\n\nDESIGN REFERENCES PROVIDED:\n" + "\n".join(design_parts)

    # If no answers yet, generate interview questions
    if not request.answers:
        question_prompt = f"""You are a software architect and UX designer helping plan a new project.

The user wants to create a {request.domain} application called "{request.name}".
Description: {request.description}{design_context}

Generate 5-6 clarifying questions to understand their requirements better.
Focus on:
1. Key features they need (MULTISELECT - user can pick multiple)
2. Compliance/security requirements (MULTISELECT)
3. Integrations needed (MULTISELECT)
4. Scale expectations
5. UI/UX preferences (visual style, target audience, key user flows)
6. Design system preferences (component library, responsive approach)

Return a JSON array of questions. Each question must have exactly these fields:
- id: unique string identifier (e.g., "features", "compliance", "ui_style")
- question: the question text
- context: brief context or why this matters
- options: array of suggested answers (provide options for all questions to make selection easier)
- multiselect: boolean - true if user can select multiple options, false for single choice

IMPORTANT: For features, compliance, and integrations questions, set multiselect=true so users can select all that apply.

Example format:
[
  {{"id": "features", "question": "What features do you need?", "context": "Select all that apply", "options": ["User Authentication", "Dashboard", "Payments", "Admin Panel", "API", "Notifications", "Reports", "Search"], "multiselect": true}},
  {{"id": "compliance", "question": "What compliance requirements apply?", "context": "Select all that apply", "options": ["HIPAA", "PCI-DSS", "GDPR", "SOC2", "None"], "multiselect": true}},
  {{"id": "integrations", "question": "What integrations do you need?", "context": "Select all that apply", "options": ["Stripe/Payments", "Auth0/OAuth", "Email (SendGrid)", "AWS/Cloud", "Database", "Analytics"], "multiselect": true}},
  {{"id": "scale", "question": "Expected scale?", "context": "Affects architecture decisions", "options": ["Small (<1k users)", "Medium (1k-100k)", "Large (100k+)"], "multiselect": false}},
  {{"id": "ui_style", "question": "What visual style fits your brand?", "context": "Influences component design", "options": ["Modern & Clean", "Playful & Colorful", "Corporate & Professional", "Minimal & Elegant"], "multiselect": false}}
]

Return ONLY valid JSON array, no other text."""

        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": get_ai_model(),
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": question_prompt}]
                    },
                    timeout=30.0
                )

            if response.status_code == 200:
                result = response.json()
                ai_text = result["content"][0]["text"]

                import json as json_lib
                if "```json" in ai_text:
                    ai_text = ai_text.split("```json")[1].split("```")[0]
                elif "```" in ai_text:
                    ai_text = ai_text.split("```")[1].split("```")[0]

                questions_raw = json_lib.loads(ai_text.strip())
                questions = [
                    PlanQuestion(
                        id=q.get("id", f"q{i}"),
                        question=q.get("question", ""),
                        context=q.get("context", ""),
                        options=q.get("options"),
                        multiselect=q.get("multiselect", False)
                    )
                    for i, q in enumerate(questions_raw)
                ]
                return PlanResponse(status="questions", questions=questions)
        except Exception as e:
            print(f"Question generation error: {e}")

        # Fallback questions
        return PlanResponse(
            status="questions",
            questions=[
                PlanQuestion(id="features", question="What features do you need?", context="Select all that apply", options=["User Authentication", "Dashboard", "Payments", "Admin Panel", "API", "Notifications", "Reports", "Search", "File Upload", "Real-time Updates"], multiselect=True),
                PlanQuestion(id="compliance", question="What compliance requirements apply?", context="Select all that apply", options=["HIPAA", "PCI-DSS", "GDPR", "SOC2", "None"], multiselect=True),
                PlanQuestion(id="integrations", question="What integrations do you need?", context="Select all that apply", options=["Stripe/Payments", "Auth0/OAuth", "Email (SendGrid)", "AWS/Cloud", "PostgreSQL", "MongoDB", "Analytics", "Slack/Teams"], multiselect=True),
                PlanQuestion(id="scale", question="What's your expected scale?", context="Affects architecture decisions", options=["Small (<1k users)", "Medium (1k-100k)", "Large (100k+)"], multiselect=False),
                PlanQuestion(id="ui_style", question="What visual style fits your brand?", context="Influences component design", options=["Modern & Clean", "Playful & Colorful", "Corporate & Professional", "Minimal & Elegant"], multiselect=False),
                PlanQuestion(id="key_pages", question="What are the main screens/pages?", context="Select all that apply", options=["Dashboard", "Settings", "Profile", "Admin", "Landing Page", "Onboarding", "Reports", "Search"], multiselect=True),
            ]
        )

    # Generate plan from answers
    answers_text = "\n".join([f"- {k}: {v}" for k, v in request.answers.items()])

    # Available assistants/tools for reference
    available_tools = """
AVAILABLE ASSISTANTS & TOOLS:
- security: Code security analysis, vulnerability detection, OWASP patterns
- performance: Performance optimization, caching strategies, query optimization
- accessibility: WCAG compliance, screen reader support, keyboard navigation
- fhir: Healthcare FHIR data standards and HL7 compliance
- hipaa: HIPAA compliance patterns, PHI handling, audit logging
- pci_dss: Payment card security, tokenization, secure data handling
- gdpr: Data privacy, consent management, right to deletion
- sox: Financial audit trails, access controls
- multitenancy: Multi-tenant architecture, data isolation, tenant management
- iot: IoT protocols, device management, real-time data streams
"""

    plan_prompt = f"""You are a senior software architect and UX designer creating a DETAILED implementation plan.

PROJECT: {request.name}
DOMAIN: {request.domain}
DESCRIPTION: {request.description}

USER REQUIREMENTS:
{answers_text}{design_context}

{available_tools}

Create a comprehensive factory plan with DETAILED sub-plans for EACH feature. Return a JSON object:
{{
    "name": "{request.name}",
    "domain": "{request.domain}",
    "description": "enhanced description based on requirements",
    "architecture": "recommended architecture pattern with detailed explanation",
    "assistants": ["relevant assistants from the available tools list above"],
    "features": ["list of 5-10 features to build"],
    "compliance": ["applicable compliance requirements"],
    "integrations": ["external integrations needed"],
    "data_models": ["key data entities/models"],
    "api_endpoints": ["main API endpoints with methods: GET /api/users, POST /api/auth, etc."],
    "security_considerations": ["security notes and recommendations"],
    "estimated_complexity": "low" or "medium" or "high",
    "ui_ux": {{
        "style": "visual style",
        "color_scheme": "recommended colors",
        "target_audience": "who uses this",
        "inspiration_urls": ["user-provided reference URLs"],
        "key_pages": ["main pages/screens"],
        "component_library": "recommended UI library",
        "accessibility_level": "AA or AAA",
        "responsive_priority": "mobile-first or desktop-first",
        "special_requirements": ["dark mode", "RTL", etc.]
    }},
    "feature_plans": [
        {{
            "feature": "Feature Name",
            "description": "What this feature does and why",
            "tasks": ["Specific implementation task 1", "Task 2", "Task 3"],
            "components": ["UI Component 1", "Component 2"],
            "api_routes": ["POST /api/feature", "GET /api/feature/:id"],
            "data_models": ["Model1", "Model2"],
            "dependencies": ["Other features this depends on"],
            "assistant_tools": ["Which assistants help: security, performance, etc."],
            "estimated_effort": "low/medium/high"
        }}
    ]
}}

IMPORTANT: Create a feature_plan entry for EACH feature in the features list. Be specific about:
- Exact implementation tasks (what code to write)
- Which UI components are needed
- Which API routes support this feature
- Which data models are involved
- Which assistant tools should review this feature

Return ONLY valid JSON, no other text."""

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": get_ai_model(),
                    "max_tokens": 2000,
                    "messages": [{"role": "user", "content": plan_prompt}]
                },
                timeout=30.0
            )

        if response.status_code == 200:
            result = response.json()
            ai_text = result["content"][0]["text"]

            import json as json_lib
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0]
            elif "```" in ai_text:
                ai_text = ai_text.split("```")[1].split("```")[0]

            plan_data = json_lib.loads(ai_text.strip())

            # Parse UI/UX preferences if present
            ui_ux_data = plan_data.get("ui_ux")
            ui_ux = None
            if ui_ux_data:
                ui_ux = UIUXPreferences(
                    style=ui_ux_data.get("style", "modern"),
                    color_scheme=ui_ux_data.get("color_scheme", ""),
                    target_audience=ui_ux_data.get("target_audience", ""),
                    inspiration_urls=ui_ux_data.get("inspiration_urls", []),
                    key_pages=ui_ux_data.get("key_pages", []),
                    component_library=ui_ux_data.get("component_library", ""),
                    accessibility_level=ui_ux_data.get("accessibility_level", "AA"),
                    responsive_priority=ui_ux_data.get("responsive_priority", "mobile-first"),
                    special_requirements=ui_ux_data.get("special_requirements", [])
                )

            # Parse feature plans if present
            feature_plans = []
            for fp in plan_data.get("feature_plans", []):
                feature_plans.append(FeatureSubPlan(
                    feature=fp.get("feature", ""),
                    description=fp.get("description", ""),
                    tasks=fp.get("tasks", []),
                    components=fp.get("components", []),
                    api_routes=fp.get("api_routes", []),
                    data_models=fp.get("data_models", []),
                    dependencies=fp.get("dependencies", []),
                    assistant_tools=fp.get("assistant_tools", []),
                    estimated_effort=fp.get("estimated_effort", "medium")
                ))

            plan = FactoryPlan(
                name=plan_data.get("name", request.name),
                domain=plan_data.get("domain", request.domain),
                description=plan_data.get("description", request.description),
                architecture=plan_data.get("architecture", "VBD"),
                assistants=plan_data.get("assistants", ["security", "performance"]),
                features=plan_data.get("features", []),
                compliance=plan_data.get("compliance", []),
                integrations=plan_data.get("integrations", []),
                data_models=plan_data.get("data_models", []),
                api_endpoints=plan_data.get("api_endpoints", []),
                security_considerations=plan_data.get("security_considerations", []),
                estimated_complexity=plan_data.get("estimated_complexity", "medium"),
                ui_ux=ui_ux,
                feature_plans=feature_plans
            )
            return PlanResponse(status="plan", plan=plan)

    except Exception as e:
        print(f"Plan generation error: {e}")

    # Fallback plan
    features = [f.strip() for f in request.answers.get("features", "").split(",") if f.strip()]
    compliance = [c.strip() for c in request.answers.get("compliance", "").split(",") if c.strip()]
    integrations = [i.strip() for i in request.answers.get("integrations", "").split(",") if i.strip()]
    ui_style = request.answers.get("ui_style", "Modern & Clean")
    key_pages = [p.strip() for p in request.answers.get("key_pages", "").split(",") if p.strip()]

    return PlanResponse(
        status="plan",
        plan=FactoryPlan(
            name=request.name,
            domain=request.domain,
            description=request.description,
            architecture="VBD (Volatility-Based Decomposition)",
            assistants=["security", "performance"],
            features=features or ["Basic CRUD", "Authentication"],
            compliance=compliance or [],
            integrations=integrations or [],
            data_models=["User", "Session"],
            api_endpoints=["/api/users", "/api/auth"],
            security_considerations=["Input validation required"],
            estimated_complexity="medium",
            ui_ux=UIUXPreferences(
                style=ui_style.lower().split()[0] if ui_style else "modern",
                key_pages=key_pages or ["Dashboard", "Settings"],
                component_library="shadcn/ui",
                inspiration_urls=[ref.value for ref in (request.design_references or []) if ref.type == "url"]
            )
        )
    )


@app.get("/api/reviews")
async def list_reviews(limit: int = 20):
    """Get recent reviews"""
    return db.get_recent_reviews(limit)


@app.get("/api/reviews/{review_id}")
async def get_review(review_id: str):
    """Get review by ID"""
    review = db.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


# ============================================================================
# REST Endpoints - Assistants
# ============================================================================

@app.get("/api/assistants")
async def list_assistants():
    """List all available assistants"""
    assistants = []

    for key, config in state.assistant_configs.items():
        methods_count = 0
        if key in state.assistants:
            assistant = state.assistants[key]
            for name in dir(assistant):
                if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
                    if callable(getattr(assistant, name)):
                        methods_count += 1

        assistants.append({
            "id": key,
            "name": config.get("name", key),
            "domain": config.get("domain", "general"),
            "tags": config.get("tags", [])[:5],
            "description": config.get("system_prompt", "")[:200],
            "methods_count": methods_count
        })

    return assistants


@app.get("/api/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """Get assistant details"""
    if assistant_id not in state.assistant_configs:
        raise HTTPException(status_code=404, detail="Assistant not found")

    config = state.assistant_configs[assistant_id]
    assistant = state.assistants.get(assistant_id)

    methods = []
    if assistant:
        for name in dir(assistant):
            if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
                method = getattr(assistant, name)
                if callable(method):
                    methods.append({
                        "name": name,
                        "doc": method.__doc__[:100] if method.__doc__ else None
                    })

    return {
        "id": assistant_id,
        "name": config.get("name", assistant_id),
        "domain": config.get("domain", "general"),
        "tags": config.get("tags", []),
        "system_prompt": config.get("system_prompt", "")[:500],
        "methods": methods
    }


@app.get("/api/assistants/{assistant_id}/patterns/{pattern_name}")
async def get_assistant_pattern(assistant_id: str, pattern_name: str):
    """Get specific pattern from assistant"""
    if assistant_id not in state.assistants:
        raise HTTPException(status_code=404, detail="Assistant not found")

    assistant = state.assistants[assistant_id]

    if not hasattr(assistant, pattern_name):
        raise HTTPException(status_code=404, detail="Pattern not found")

    method = getattr(assistant, pattern_name)
    if not callable(method):
        raise HTTPException(status_code=400, detail="Not a callable method")

    try:
        result = method()
        return {"pattern": pattern_name, "data": result}
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Method requires arguments: {e}")


# ============================================================================
# REST Endpoints - Stats
# ============================================================================

@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    stats = db.get_stats()
    return {
        "factories": {
            "total": stats["total_factories"],
            "active": stats["active_factories"]
        },
        "features": {
            "total": stats["total_features"]
        },
        "reviews": {
            "total": stats["total_reviews"],
            "findings": stats["findings"]
        },
        "assistants": {
            "loaded": len(state.assistants)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# REST Endpoints - Settings
# ============================================================================

class SettingUpdate(BaseModel):
    """Request model for updating a setting"""
    value: str


class SettingsBatchUpdate(BaseModel):
    """Request model for batch updating settings"""
    settings: Dict[str, str]


@app.get("/api/settings")
async def get_all_settings():
    """Get all settings grouped by category"""
    return db.get_all_settings()


@app.get("/api/settings/status")
async def get_settings_status():
    """Get configuration status (what's missing)"""
    return db.get_settings_status()


@app.get("/api/settings/category/{category}")
async def get_settings_by_category(category: str):
    """Get settings for a specific category"""
    valid_categories = ["ai", "integrations", "defaults", "ui"]
    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {valid_categories}")
    return db.get_settings_by_category(category)


@app.get("/api/settings/{key}")
async def get_setting(key: str):
    """Get a single setting value"""
    value = db.get_setting(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"key": key, "value": value}


@app.put("/api/settings/{key}")
async def update_setting(key: str, request: SettingUpdate):
    """Update a single setting"""
    result = db.update_setting(key, request.value)
    if not result:
        raise HTTPException(status_code=404, detail="Setting not found")
    return result


@app.put("/api/settings")
async def update_settings_batch(request: SettingsBatchUpdate):
    """Update multiple settings at once"""
    return db.update_settings_batch(request.settings)


@app.get("/api/settings/test/ai")
async def test_ai_connection():
    """Test AI API key configuration"""
    api_key = db.get_setting("anthropic_api_key")
    if not api_key:
        return {"status": "error", "message": "Anthropic API key not configured"}

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": get_ai_model(),
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Say hello"}]
                },
                timeout=10.0
            )

        if response.status_code == 200:
            return {"status": "ok", "message": "AI connection successful"}
        elif response.status_code == 401:
            return {"status": "error", "message": "Invalid API key"}
        else:
            return {"status": "error", "message": f"API error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# WebSocket - Real-time Collaboration
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.user_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_info: Dict):
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(websocket)
        self.user_info[websocket] = {**user_info, "room_id": room_id}

        await self.broadcast(room_id, {
            "type": "user_join",
            "user": user_info,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.user_info:
            room_id = self.user_info[websocket]["room_id"]
            user_info = self.user_info[websocket]

            if room_id in self.rooms:
                self.rooms[room_id].discard(websocket)
                if not self.rooms[room_id]:
                    del self.rooms[room_id]

            del self.user_info[websocket]
            return room_id, user_info
        return None, None

    async def broadcast(self, room_id: str, message: Dict, exclude: WebSocket = None):
        if room_id not in self.rooms:
            return

        for connection in self.rooms[room_id]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    def get_room_users(self, room_id: str) -> List[Dict]:
        if room_id not in self.rooms:
            return []
        return [self.user_info[ws] for ws in self.rooms[room_id] if ws in self.user_info]


manager = ConnectionManager()


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time collaboration"""
    user_id = websocket.query_params.get("user_id", f"user-{uuid.uuid4().hex[:8]}")
    user_name = websocket.query_params.get("name", "Anonymous")

    user_info = {
        "id": user_id,
        "name": user_name,
        "status": "online"
    }

    await manager.connect(websocket, room_id, user_info)

    await websocket.send_json({
        "type": "room_state",
        "users": manager.get_room_users(room_id),
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                await manager.broadcast(room_id, {
                    "type": "chat",
                    "user": user_info,
                    "content": data.get("content", ""),
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif msg_type == "code_change":
                await manager.broadcast(room_id, {
                    "type": "code_change",
                    "user": user_info,
                    "changes": data.get("changes", []),
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude=websocket)
            elif msg_type == "cursor_move":
                await manager.broadcast(room_id, {
                    "type": "cursor_move",
                    "user_id": user_id,
                    "position": data.get("position", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude=websocket)
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        room_id, user_info = manager.disconnect(websocket)
        if room_id:
            await manager.broadcast(room_id, {
                "type": "user_leave",
                "user": user_info,
                "timestamp": datetime.utcnow().isoformat()
            })


# ============================================================================
# Terminal WebSocket - Shell Access
# ============================================================================

import pty
import os
import select
import subprocess
import signal
import struct
import fcntl
import termios

class TerminalSession:
    """Manages a PTY terminal session"""

    def __init__(self, shell: str = "/bin/bash"):
        self.shell = shell
        self.master_fd = None
        self.slave_fd = None
        self.pid = None
        self.running = False

    def start(self, rows: int = 24, cols: int = 80):
        """Start a new terminal session"""
        self.master_fd, self.slave_fd = pty.openpty()

        # Set terminal size
        self.resize(rows, cols)

        # Fork process
        self.pid = os.fork()

        if self.pid == 0:
            # Child process
            os.close(self.master_fd)
            os.setsid()
            os.dup2(self.slave_fd, 0)
            os.dup2(self.slave_fd, 1)
            os.dup2(self.slave_fd, 2)
            os.close(self.slave_fd)

            # Set environment
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["PS1"] = "\\[\\033[1;32m\\]genesis\\[\\033[0m\\]:\\[\\033[1;34m\\]\\w\\[\\033[0m\\]$ "

            os.execvpe(self.shell, [self.shell], env)
        else:
            # Parent process
            os.close(self.slave_fd)
            self.running = True

    def resize(self, rows: int, cols: int):
        """Resize terminal"""
        if self.master_fd:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def write(self, data: bytes):
        """Write data to terminal"""
        if self.master_fd and self.running:
            os.write(self.master_fd, data)

    def read(self, timeout: float = 0.1) -> bytes:
        """Read data from terminal"""
        if not self.master_fd or not self.running:
            return b""

        ready, _, _ = select.select([self.master_fd], [], [], timeout)
        if ready:
            try:
                return os.read(self.master_fd, 4096)
            except OSError:
                self.running = False
                return b""
        return b""

    def stop(self):
        """Stop terminal session"""
        self.running = False
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
                os.waitpid(self.pid, 0)
            except (OSError, ChildProcessError):
                pass
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        self.master_fd = None
        self.pid = None


# Store active terminal sessions
terminal_sessions: Dict[str, TerminalSession] = {}


@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal access"""
    await websocket.accept()

    # Create new terminal session
    terminal = TerminalSession()
    terminal_sessions[session_id] = terminal

    try:
        # Get initial size from client
        init_data = await websocket.receive_json()
        rows = init_data.get("rows", 24)
        cols = init_data.get("cols", 80)

        # Start terminal
        terminal.start(rows, cols)

        # Send welcome message
        await websocket.send_json({
            "type": "output",
            "data": f"\r\n\x1b[1;36m╭───────────────────────────────────────╮\x1b[0m\r\n"
                    f"\x1b[1;36m│\x1b[0m  \x1b[1;32mGenesis Engine Terminal\x1b[0m              \x1b[1;36m│\x1b[0m\r\n"
                    f"\x1b[1;36m│\x1b[0m  Session: {session_id[:8]}                    \x1b[1;36m│\x1b[0m\r\n"
                    f"\x1b[1;36m╰───────────────────────────────────────╯\x1b[0m\r\n\r\n"
        })

        async def read_output():
            """Read terminal output and send to client"""
            while terminal.running:
                output = terminal.read(0.05)
                if output:
                    await websocket.send_json({
                        "type": "output",
                        "data": output.decode("utf-8", errors="replace")
                    })
                await asyncio.sleep(0.01)

        # Start output reader task
        output_task = asyncio.create_task(read_output())

        # Handle incoming messages
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                msg_type = message.get("type")

                if msg_type == "input":
                    data = message.get("data", "")
                    terminal.write(data.encode("utf-8"))
                elif msg_type == "resize":
                    rows = message.get("rows", 24)
                    cols = message.get("cols", 80)
                    terminal.resize(rows, cols)
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                if not terminal.running:
                    break
                continue

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass
    finally:
        # Cleanup
        terminal.stop()
        if session_id in terminal_sessions:
            del terminal_sessions[session_id]


if __name__ == "__main__":
    import uvicorn
    # Run without reload to avoid importing through genesis package
    uvicorn.run(app, host="0.0.0.0", port=8000)
