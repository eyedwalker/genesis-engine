# Hive BizOS AI Factory - AWS Free Tier Edition
## Build Healthcare Software Autonomously for $8-15/month

**An autonomous AI-powered software factory that generates FHIR-compliant healthcare code.**

---

## 🎯 What Is This?

This is a **fully autonomous software development system** that:
- Takes feature requests in plain English
- Designs FHIR-compliant solutions (Architect AI)
- Writes production Python code (Builder AI)
- Tests and fixes bugs automatically (Self-Healing Loop)
- Deploys on AWS Free Tier for minimal cost

**Example**:
```
You: "Add appointment cancellation feature"
  ↓ (10 seconds later)
Factory: ✅ Done! Created:
  - app/models/appointment.py
  - app/services/appointment_service.py
  - app/api/appointments.py
  - tests/test_appointment_cancel.py
```

---

## 💰 Cost Breakdown

| Service | Free Tier | After Free Tier | Our Usage |
|---------|-----------|-----------------|-----------|
| **RDS PostgreSQL** | 750 hrs/month (12 mo) | $13/month | t3.micro, Single-AZ |
| **DynamoDB** | 25GB forever | Forever free | Cache storage |
| **Lambda** | 1M requests/month forever | Forever free | Agent execution |
| **S3** | 5GB (12 mo) | $0.12/GB | Code storage |
| **Secrets Manager** | - | $0.40/month | API keys |
| **AI APIs** | - | $0.22/feature | Claude + GPT-4 |
| | | | |
| **Month 1-12** | | **$0.40 + AI** | = **$8-15/month** |
| **Month 13+** | | **$13.40 + AI** | = **$25-40/month** |

**Building 50 features in Month 1**: $0.40 + (50 × $0.22) = **$11.40**

---

## 🚀 Quick Start (30 Minutes)

### Prerequisites

- AWS Account (free tier eligible)
- Python 3.10+
- Terraform 1.0+
- Anthropic API key (free $5 credit)
- OpenAI API key (free $5 credit)

### Step 1: Get API Keys (5 minutes)

```bash
# 1. Anthropic (Claude)
# Visit: https://console.anthropic.com/
# Sign up, get API key
# Free credit: $5 (111 features worth!)

# 2. OpenAI (GPT-4)
# Visit: https://platform.openai.com/
# Sign up, get API key
# Free credit: $5 (28 features worth!)
```

### Step 2: Clone & Setup (5 minutes)

```bash
# Clone repository
git clone <your-repo>
cd hive-factory-free-tier

# Install Python dependencies
pip install -r requirements.txt

# Or use Poetry (recommended)
poetry install
```

### Step 3: Deploy Infrastructure (10 minutes)

```bash
# Navigate to infrastructure
cd infrastructure/terraform

# Create terraform.tfvars
cat > terraform.tfvars << EOF
aws_region         = "us-east-1"
environment        = "free-tier"
tenant_id          = "default"
db_password        = "YourSecurePassword123!"
anthropic_api_key  = "sk-ant-your-key"
openai_api_key     = "sk-your-key"
EOF

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy (takes ~10 minutes)
terraform apply

# Save outputs
terraform output > ../outputs.txt
```

### Step 4: Test Locally (10 minutes)

```bash
# Set environment variables
export DATABASE_URL=$(terraform output -raw database_endpoint)
export ANTHROPIC_API_KEY="sk-ant-your-key"
export OPENAI_API_KEY="sk-your-key"
export WORKSPACE_ROOT="./workspace"
export TENANT_ID="default"

# Run the factory
cd ../..
python examples/demo.py
```

---

## 📁 Project Structure

```
hive-factory-free-tier/
├── config/
│   └── CONTEXT.md              # System context for all agents
│
├── agents/
│   ├── factory_deps.py         # Shared dependencies & tools
│   ├── architect_agent.py      # Claude-powered architect
│   └── builder_agent.py        # GPT-4-powered builder
│
├── graph/
│   └── factory_graph.py        # LangGraph orchestration
│
├── infrastructure/
│   └── terraform/
│       └── main.tf             # AWS Free Tier setup
│
├── examples/
│   └── demo.py                 # Example usage
│
├── docs/
│   ├── ARCHITECTURE.md         # System architecture
│   ├── COST_OPTIMIZATION.md    # How to minimize costs
│   └── TROUBLESHOOTING.md      # Common issues
│
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Poetry configuration
└── README.md                  # This file
```

---

## 🏗️ Architecture

### High-Level Flow

```
User Request
    ↓
┌─────────────────────┐
│  Architect (Claude) │  → Searches FHIR docs
│  - Designs feature  │  → Creates implementation plan
└─────────┬───────────┘
          ↓
┌─────────────────────┐
│  Builder (GPT-4)    │  → Writes Python code
│  - Implements plan  │  → Runs linter
└─────────┬───────────┘
          ↓
     Linting passes?
          ├─ YES → QA
          └─ NO → Loop back to Builder (max 5 times)
          
┌─────────────────────┐
│  QA (GPT-4)         │  → Runs tests
│  - Validates code   │  → Checks coverage
└─────────────────────┘
          ↓
     All tests pass?
          ├─ YES → ✅ Done!
          ├─ NO → Loop back to Builder (max 5 times)
          └─ Too many fails → 🚨 Human intervention
```

### Self-Healing Loop

**The factory automatically fixes its own bugs!**

```python
Iteration 1: Builder writes code → Linter fails → Extract errors
Iteration 2: Builder fixes errors → Linter fails → Extract errors
Iteration 3: Builder fixes errors → Linter passes → QA runs
Iteration 4: Tests fail → Builder fixes → Tests pass → ✅ Success!
```

**Maximum 5 iterations** before human escalation.

---

## 🔧 Technologies Used

| Technology | Purpose | Cost |
|------------|---------|------|
| **PydanticAI** | Type-safe AI agents | Free |
| **LangGraph** | Workflow orchestration | Free |
| **Claude Sonnet 4.5** | System design (Architect) | $0.045/feature |
| **GPT-4o** | Code generation (Builder) | $0.175/feature |
| **FastAPI** | Web framework | Free |
| **PostgreSQL** | Database (RDS) | Free tier |
| **DynamoDB** | Cache | Free forever |
| **Milvus** | Vector search (optional) | Free (self-hosted) |
| **Terraform** | Infrastructure as code | Free |

---

## 📝 Example Usage

### Example 1: Appointment Cancellation

```python
from graph.factory_graph import run_factory
from agents.factory_deps import FactoryDeps

# Initialize dependencies
deps = FactoryDeps.from_env()

# Request feature
result = await run_factory(
    request="Add appointment cancellation feature with automatic slot release",
    deps=deps
)

# Check result
print(result["status"])  # "success"
print(result["files_created"])
# [
#   "app/models/appointment.py",
#   "app/services/appointment_service.py",
#   "app/api/appointments.py",
#   "tests/test_appointment_cancel.py"
# ]
```

### Example 2: Patient Search

```python
result = await run_factory(
    request="Add patient search by name and date of birth",
    deps=deps
)

# Factory automatically:
# 1. Searches FHIR Patient resource docs
# 2. Designs search endpoint
# 3. Implements fuzzy matching
# 4. Adds tests
# 5. Validates HIPAA compliance
```

### Example 3: Billing Integration

```python
result = await run_factory(
    request="Link appointments to billing accounts",
    deps=deps
)

# Factory automatically:
# 1. Identifies Appointment + Account resources
# 2. Designs foreign key relationship
# 3. Implements referential integrity
# 4. Creates migration script
# 5. Tests billing calculations
```

---

## 🎯 What The Factory Can Build

**✅ Can Build**:
- FHIR resource CRUD operations
- Status transitions (appointment → cancelled)
- Search endpoints with filters
- Business logic (slot release, notifications)
- Database migrations
- API documentation
- Comprehensive tests

**⚠️ Needs Guidance**:
- Complex integrations (Epic, Cerner)
- Third-party API connections
- Payment processing
- Real-time messaging

**❌ Cannot Build** (yet):
- Frontend UI components
- Mobile applications
- DevOps infrastructure
- Non-FHIR domains

---

## 🔐 Security & Compliance

### HIPAA Compliance

The factory is designed with HIPAA compliance in mind:

✅ **No PHI in Logs**: All agents instructed to never log patient data  
✅ **Encrypted Storage**: RDS encryption at rest enabled  
✅ **Encrypted Transit**: All connections use TLS  
✅ **Audit Logging**: All data access is logged  
✅ **Access Control**: IAM roles with least privilege  

**Note**: You are responsible for signing a BAA with AWS for HIPAA compliance.

### Security Best Practices

```python
# ✅ GOOD: Parameterized query
query = select(Patient).where(Patient.id == patient_id)

# ❌ BAD: String concatenation (SQL injection!)
query = f"SELECT * FROM patients WHERE id = {patient_id}"
```

---

## 📊 Cost Optimization Tips

### 1. Minimize AI Calls

```python
# Enable prompt caching (saves 50%)
# Anthropic automatically caches system prompts

# Use cheaper models for simple features
# GPT-4o-mini for CRUD operations
```

### 2. Use Free Tier Efficiently

```python
# DynamoDB: 25GB + 200M requests/month FREE forever
# Use for caching instead of ElastiCache

# Lambda: 1M requests FREE forever
# Use for agent execution instead of EC2
```

### 3. Monitor Costs

```bash
# Set up billing alerts
aws budgets create-budget \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**Target**: Keep infrastructure under $1/month, AI costs $10-30/month

---

## 🐛 Troubleshooting

### Issue: "Linter not found"

```bash
# Install linting tools
pip install ruff mypy

# Or via requirements
pip install -r requirements.txt
```

### Issue: "Milvus connection failed"

```bash
# Milvus is optional - factory uses fallback FHIR knowledge
# To use Milvus, set MILVUS_URI environment variable

# Or run Milvus locally
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
```

### Issue: "Database connection failed"

```bash
# Check RDS endpoint
terraform output database_endpoint

# Verify security group allows connections
# Check VPC configuration in Terraform

# Test connection
psql -h <endpoint> -U hive_admin -d hive_bizos
```

### Issue: "Out of AI credits"

```bash
# Free credits exhausted
# Add payment method to Anthropic/OpenAI accounts

# Check usage
# Anthropic: https://console.anthropic.com/settings/usage
# OpenAI: https://platform.openai.com/usage
```

---

## 📈 Scaling Beyond Free Tier

### When to Upgrade

**Stay on Free Tier while**:
- Building < 5 features/day
- Testing and iterating
- Solo development
- < 10 users

**Upgrade when**:
- Building > 10 features/day (AI costs increase)
- Need high availability (Multi-AZ RDS)
- Production launch (> 100 users)
- Need faster performance

### Upgrade Path

```
Month 1-12: Free Tier ($8-15/month)
    ↓
Month 13+: Paid Tier ($25-40/month)
    ↓
High Volume: Optimized ($100-200/month)
    ↓
Production: Full Stack ($500-1000/month)
```

---

## 🤝 Contributing

We welcome contributions! Areas of focus:

- [ ] QA Agent with Dagger integration
- [ ] DevContainer creation for human intervention
- [ ] Milvus knowledge base hydration
- [ ] Additional FHIR resources
- [ ] Cost optimization improvements
- [ ] Security enhancements

See `CONTRIBUTING.md` for guidelines.

---

## 📄 License

MIT License - See `LICENSE` file

---

## 🙏 Acknowledgments

- Built on HL7 FHIR R4 Standard
- Powered by Anthropic Claude & OpenAI GPT-4
- Orchestrated with PydanticAI & LangGraph
- Infrastructure by Terraform & AWS

---

## 📞 Support

**Issues**: Open a GitHub issue  
**Questions**: Start a discussion  
**Security**: Email security@yourdomain.com  

---

## 🎓 Learning Resources

**New to FHIR?**
- HL7 FHIR Documentation: https://hl7.org/fhir/
- FHIR for Developers: https://www.hl7.org/fhir/overview-dev.html

**New to AI Agents?**
- PydanticAI Docs: https://ai.pydantic.dev/
- LangGraph Tutorial: https://langchain-ai.github.io/langgraph/

**New to AWS?**
- AWS Free Tier: https://aws.amazon.com/free/
- Terraform Tutorial: https://learn.hashicorp.com/terraform

---

## 🚀 Next Steps

1. ✅ Deploy infrastructure (`terraform apply`)
2. ✅ Run demo (`python examples/demo.py`)
3. ✅ Build your first feature!
4. 📖 Read `ARCHITECTURE.md` for deep dive
5. 💰 Review `COST_OPTIMIZATION.md` for savings
6. 🔧 Check `TROUBLESHOOTING.md` if stuck

**Ready to build healthcare software autonomously?** 

**Let's go! 🏥🤖**

---

**Star ⭐ this repo if you find it useful!**
