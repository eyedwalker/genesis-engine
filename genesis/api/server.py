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

# Import database module
try:
    from genesis import database as db
except ImportError:
    from .. import database as db


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
    if not db.delete_factory(factory_id):
        raise HTTPException(status_code=404, detail="Factory not found")
    return {"status": "deleted", "id": factory_id}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
