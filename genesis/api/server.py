"""
Genesis Engine API Server

FastAPI backend providing:
- REST API for factory and assistant management
- WebSocket for real-time collaboration
- Code review endpoints
- Metrics and monitoring

Usage:
    uvicorn genesis.api.server:app --reload --port 8000

Or with the CLI:
    genesis serve --port 8000
"""

import asyncio
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


# ============================================================================
# Models
# ============================================================================

class FactoryCreate(BaseModel):
    """Request model for creating a factory"""
    name: str = Field(..., min_length=1, max_length=100)
    domain: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=10)
    assistants: List[str] = Field(default_factory=list)


class FactoryResponse(BaseModel):
    """Response model for factory"""
    id: str
    name: str
    domain: str
    status: str
    features_built: int
    created_at: datetime
    last_activity: datetime
    assistants: List[str]


class CodeReviewRequest(BaseModel):
    """Request model for code review"""
    code: str = Field(..., min_length=1)
    language: str = Field(default="python")
    assistants: List[str] = Field(default_factory=lambda: ["security", "performance"])
    context: Optional[str] = None


class CodeReviewResponse(BaseModel):
    """Response model for code review"""
    request_id: str
    status: str
    findings: List[Dict[str, Any]]
    summary: Dict[str, int]


class AssistantInfo(BaseModel):
    """Assistant information"""
    id: str
    name: str
    domain: str
    tags: List[str]
    description: str
    methods: List[str]


class CollaborationMessage(BaseModel):
    """Real-time collaboration message"""
    type: str  # 'chat', 'code_change', 'cursor_move', 'user_join', 'user_leave'
    user_id: str
    content: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# State Management
# ============================================================================

@dataclass
class ServerState:
    """Server state management"""
    factories: Dict[str, Dict] = field(default_factory=dict)
    active_connections: Dict[str, Set[WebSocket]] = field(default_factory=dict)
    user_sessions: Dict[str, Dict] = field(default_factory=dict)
    assistants: Dict[str, Any] = field(default_factory=dict)
    assistant_configs: Dict[str, Dict] = field(default_factory=dict)


state = ServerState()


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

            # Find factory function
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
    # Startup
    print("Genesis API Server starting...")
    load_assistants()

    # Add demo factory
    state.factories["demo-1"] = {
        "id": "demo-1",
        "name": "Healthcare Platform",
        "domain": "healthcare",
        "status": "active",
        "features_built": 45,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "assistants": ["security", "fhir", "accessibility"]
    }

    yield

    # Shutdown
    print("Genesis API Server shutting down...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Genesis Engine API",
    description="Factory-as-a-Service Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST Endpoints - Health
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "assistants_loaded": len(state.assistants),
        "factories_active": len(state.factories)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Genesis Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "factories": "/api/factories",
            "assistants": "/api/assistants",
            "review": "/api/review",
            "websocket": "/ws/{room_id}"
        }
    }


# ============================================================================
# REST Endpoints - Factories
# ============================================================================

@app.get("/api/factories", response_model=List[FactoryResponse])
async def list_factories():
    """List all factories"""
    return [
        FactoryResponse(**factory)
        for factory in state.factories.values()
    ]


@app.post("/api/factories", response_model=FactoryResponse)
async def create_factory(request: FactoryCreate, background_tasks: BackgroundTasks):
    """Create a new factory"""
    factory_id = f"factory-{datetime.utcnow().timestamp():.0f}"

    factory = {
        "id": factory_id,
        "name": request.name,
        "domain": request.domain,
        "status": "provisioning",
        "features_built": 0,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "assistants": request.assistants or ["security", "performance"]
    }

    state.factories[factory_id] = factory

    # Simulate provisioning in background
    background_tasks.add_task(provision_factory, factory_id)

    return FactoryResponse(**factory)


async def provision_factory(factory_id: str):
    """Background task to provision a factory"""
    await asyncio.sleep(5)  # Simulate provisioning time

    if factory_id in state.factories:
        state.factories[factory_id]["status"] = "active"


@app.get("/api/factories/{factory_id}", response_model=FactoryResponse)
async def get_factory(factory_id: str):
    """Get factory by ID"""
    if factory_id not in state.factories:
        raise HTTPException(status_code=404, detail="Factory not found")

    return FactoryResponse(**state.factories[factory_id])


@app.delete("/api/factories/{factory_id}")
async def delete_factory(factory_id: str):
    """Delete a factory"""
    if factory_id not in state.factories:
        raise HTTPException(status_code=404, detail="Factory not found")

    del state.factories[factory_id]
    return {"status": "deleted", "id": factory_id}


# ============================================================================
# REST Endpoints - Assistants
# ============================================================================

@app.get("/api/assistants", response_model=List[AssistantInfo])
async def list_assistants():
    """List all available assistants"""
    assistants = []

    for key, config in state.assistant_configs.items():
        # Get methods from assistant instance
        methods = []
        if key in state.assistants:
            assistant = state.assistants[key]
            for name in dir(assistant):
                if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
                    if callable(getattr(assistant, name)):
                        methods.append(name)

        assistants.append(AssistantInfo(
            id=key,
            name=config.get("name", key),
            domain=config.get("domain", "general"),
            tags=config.get("tags", []),
            description=config.get("system_prompt", "")[:300],
            methods=methods
        ))

    return assistants


@app.get("/api/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    """Get assistant details and patterns"""
    if assistant_id not in state.assistants:
        raise HTTPException(status_code=404, detail="Assistant not found")

    assistant = state.assistants[assistant_id]
    config = state.assistant_configs[assistant_id]

    # Get all patterns from methods
    patterns = {}
    for name in dir(assistant):
        if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
            method = getattr(assistant, name)
            if callable(method):
                try:
                    result = method()
                    if isinstance(result, dict):
                        patterns[name] = result
                except TypeError:
                    pass

    return {
        "id": assistant_id,
        "name": config.get("name", assistant_id),
        "domain": config.get("domain", "general"),
        "tags": config.get("tags", []),
        "system_prompt": config.get("system_prompt", ""),
        "patterns": patterns
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
# REST Endpoints - Code Review
# ============================================================================

@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """Review code using selected assistants"""
    request_id = f"review-{datetime.utcnow().timestamp():.0f}"
    findings = []
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for assistant_id in request.assistants:
        if assistant_id not in state.assistants:
            continue

        assistant = state.assistants[assistant_id]
        config = state.assistant_configs[assistant_id]

        # Get patterns from assistant
        patterns = {}
        for name in dir(assistant):
            if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
                method = getattr(assistant, name)
                if callable(method):
                    try:
                        result = method()
                        if isinstance(result, dict):
                            patterns[name] = result
                    except TypeError:
                        pass

        findings.append({
            "assistant": assistant_id,
            "assistant_name": config.get("name", assistant_id),
            "patterns_checked": list(patterns.keys()),
            "domain": config.get("domain", "general"),
            "tags": config.get("tags", [])
        })

    return CodeReviewResponse(
        request_id=request_id,
        status="completed",
        findings=findings,
        summary=summary
    )


# ============================================================================
# WebSocket - Real-time Collaboration
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.user_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_info: Dict):
        """Connect a user to a room"""
        await websocket.accept()

        if room_id not in self.rooms:
            self.rooms[room_id] = set()

        self.rooms[room_id].add(websocket)
        self.user_info[websocket] = {**user_info, "room_id": room_id}

        # Notify others of new user
        await self.broadcast(room_id, {
            "type": "user_join",
            "user": user_info,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=websocket)

    def disconnect(self, websocket: WebSocket):
        """Disconnect a user"""
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
        """Broadcast message to all users in a room"""
        if room_id not in self.rooms:
            return

        for connection in self.rooms[room_id]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

    async def send_to_user(self, websocket: WebSocket, message: Dict):
        """Send message to specific user"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    def get_room_users(self, room_id: str) -> List[Dict]:
        """Get all users in a room"""
        if room_id not in self.rooms:
            return []

        return [
            self.user_info[ws]
            for ws in self.rooms[room_id]
            if ws in self.user_info
        ]


manager = ConnectionManager()


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for real-time collaboration"""

    # Get user info from query params
    user_id = websocket.query_params.get("user_id", f"user-{datetime.utcnow().timestamp():.0f}")
    user_name = websocket.query_params.get("name", "Anonymous")

    user_info = {
        "id": user_id,
        "name": user_name,
        "avatar": "👤",
        "status": "online",
        "role": "editor"
    }

    await manager.connect(websocket, room_id, user_info)

    # Send current room state to new user
    await manager.send_to_user(websocket, {
        "type": "room_state",
        "users": manager.get_room_users(room_id),
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()

            message_type = data.get("type", "chat")

            if message_type == "chat":
                # Broadcast chat message
                await manager.broadcast(room_id, {
                    "type": "chat",
                    "user": user_info,
                    "content": data.get("content", ""),
                    "timestamp": datetime.utcnow().isoformat()
                })

            elif message_type == "code_change":
                # Broadcast code change
                await manager.broadcast(room_id, {
                    "type": "code_change",
                    "user": user_info,
                    "file": data.get("file", ""),
                    "changes": data.get("changes", []),
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude=websocket)

            elif message_type == "cursor_move":
                # Broadcast cursor position
                await manager.broadcast(room_id, {
                    "type": "cursor_move",
                    "user_id": user_id,
                    "position": data.get("position", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude=websocket)

            elif message_type == "ping":
                # Respond to ping
                await manager.send_to_user(websocket, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        room_id, user_info = manager.disconnect(websocket)
        if room_id:
            await manager.broadcast(room_id, {
                "type": "user_leave",
                "user": user_info,
                "timestamp": datetime.utcnow().isoformat()
            })


# ============================================================================
# Metrics Endpoint
# ============================================================================

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    total_connections = sum(len(room) for room in manager.rooms.values())

    return {
        "factories": {
            "total": len(state.factories),
            "active": sum(1 for f in state.factories.values() if f["status"] == "active"),
            "building": sum(1 for f in state.factories.values() if f["status"] == "provisioning")
        },
        "assistants": {
            "loaded": len(state.assistants)
        },
        "collaboration": {
            "active_rooms": len(manager.rooms),
            "total_connections": total_connections
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
