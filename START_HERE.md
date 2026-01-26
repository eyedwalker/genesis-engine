# Genesis Engine - Quick Start

Your Genesis Engine setup is complete! Here's how to get started.

## Setup Complete ✅

- ✅ Dagger CLI installed
- ✅ Python dependencies installed
- ✅ Docker Compose configured (Milvus, Keycloak, Attu)
- ✅ Environment variables configured (.env)
- ✅ Genesis module created

## What You Have

### 1. Services (Docker)
```bash
cd docker
docker compose up -d
```

This starts:
- **Milvus** (port 19530) - Vector database for RAG
- **Attu** (port 8000) - Milvus web UI at http://localhost:8000
- **Keycloak** (port 8080) - Identity management at http://localhost:8080
  - Login: `admin` / `admin`
  - Realm: `genesis`

### 2. Genesis Engine Components

#### Core Modules
- `genesis/genesis_engine.py` - Main orchestrator (Factory-as-a-Service)
- `genesis/genesis_agent.py` - Meta-prompting agent (creates factories)
- `genesis/factory_template.py` - Factory abstraction + Healthcare impl
- `genesis/dagger_executor.py` - Containerized CI/CD
- `genesis/tenant_manager.py` - Keycloak + Milvus multi-tenancy
- `genesis/devcontainer.py` - Human escalation

#### Agents (Healthcare Factory)
- `agents/architect_agent.py` - Designs FHIR-compliant features
- `agents/builder_agent.py` - Implements code from plans
- `graph/factory_graph.py` - LangGraph workflow orchestration

## Quick Start

### Option 1: Run the Demo (Recommended)

**Easy way** (handles Docker startup):
```bash
./run_demo.sh
```

**Manual way**:
```bash
# Make sure Docker Desktop is running first!

# Start all services
cd docker && docker compose up -d

# Go back to project root
cd ..

# Run the interactive demo
python3 examples/genesis_demo.py
```

**Important**: Always use `python3` (not `python`) since you have Anaconda installed.

**Demo Options:**
1. **Healthcare Factory** - Build FHIR features (existing implementation)
2. **Genesis New Domain** - Create a factory for ANY business domain
3. **Factory Lifecycle** - See full tenant provisioning

### Option 2: Use as Python Package

```python
import asyncio
from genesis import GenesisEngine, run_genesis

async def main():
    # Create a new software factory for e-commerce
    engine = GenesisEngine.from_env()

    blueprint = await run_genesis(
        "E-commerce platform with inventory, cart, and checkout"
    )

    factory = await engine.create_factory(blueprint)

    # Build a feature using the new factory
    result = await factory.build_feature(
        "Add abandoned cart recovery emails"
    )

    print(result)

asyncio.run(main())
```

### Option 3: CLI (if installed)

```bash
genesis --help
factory --help  # Healthcare-specific factory
```

## Environment Variables

Your [.env](/.env) file is already configured with:

```bash
# Required (you have these)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Optional (running locally)
MILVUS_URI=http://localhost:19530
KEYCLOAK_URL=http://localhost:8080
USE_DAGGER=true
```

## Verify Setup

**Quick verification**:
```bash
python3 verify_setup.py
```

**Manual checks**:
```bash
# Check services are running
docker ps

# Test Python imports
python3 -c "from genesis import GenesisEngine; print('✓ Ready!')"

# Check Dagger
dagger version
```

## Architecture

```
Genesis Engine (Meta-Layer)
├── Genesis Agent (Claude Opus) - Creates factory blueprints
├── Factory Templates - Domain-specific implementations
│   └── Healthcare Factory (Hive BizOS)
│       ├── Architect Agent - Designs FHIR features
│       ├── Builder Agent - Implements code
│       └── QA Agent - Tests & validates
├── Dagger Executor - Containerized builds
├── Tenant Manager - Multi-tenant isolation
└── DevContainer Manager - Human escalation
```

## What's Next?

### Try These Examples

1. **Build a Healthcare Feature**
   ```bash
   python3 examples/genesis_demo.py
   # Choose Option 1: Healthcare Factory
   # Request: "Add patient appointment reminders"
   ```

2. **Create a New Factory**
   ```bash
   python3 examples/genesis_demo.py
   # Choose Option 2: Genesis New Domain
   # Domain: "Restaurant management system"
   ```

3. **Explore the Generated Code**
   ```bash
   ls -la workspace/default/
   ```

### Configure Keycloak (Optional)

1. Open http://localhost:8080
2. Login: `admin` / `admin`
3. Create realm: `genesis`
4. Create client: `genesis-engine`
5. Copy client secret to `.env`

### View RAG Knowledge Base (Optional)

1. Open http://localhost:8000 (Attu - Milvus UI)
2. Connect to `localhost:19530`
3. Browse `factory_knowledge` collection

## Troubleshooting

**Docker not running?**
```bash
# Start Docker Desktop, then:
cd docker && docker compose up -d
```

**Import errors?**
```bash
pip install -e ".[all]"
```

**Port conflicts?**
```bash
# Edit docker/docker-compose.yml
# Change port mappings (e.g., 8080:8080 → 8081:8080)
```

**Dagger connection errors?**
```bash
# Falls back to subprocess automatically
# Or set: USE_DAGGER=false
```

## Key Files

- [QUICKSTART.md](/QUICKSTART.md) - Original project overview
- [.env](/.env) - Environment configuration
- [docker/docker-compose.yml](/docker/docker-compose.yml) - Services config
- [examples/genesis_demo.py](/examples/genesis_demo.py) - Interactive demo
- [genesis/](/genesis/) - Genesis Engine source

## Documentation

- Genesis Engine Spec: `docs/` (if you have the original spec doc)
- FHIR R4 Docs: https://hl7.org/fhir/R4/
- PydanticAI: https://ai.pydantic.dev
- LangGraph: https://langchain-ai.github.io/langgraph/
- Dagger: https://docs.dagger.io

## Need Help?

The Genesis Engine includes:
- Self-healing loops (max 5 iterations)
- DevContainer escalation for humans
- Comprehensive error handling

If you get stuck, check:
1. Docker containers are running
2. API keys are valid
3. Ports are available

---

**You're all set!** Start with the demo and explore from there. 🚀
