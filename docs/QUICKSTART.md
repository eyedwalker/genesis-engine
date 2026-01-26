# Hive BizOS Factory - Quick Start Guide
## From Zero to Building Features in 30 Minutes

This guide will walk you through setting up and running the factory for the first time.

**Time Required**: 30 minutes  
**Cost**: $0 (using free AI credits)  
**Prerequisites**: Computer with internet access

---

## 📋 Before You Start

### What You'll Need

1. **Computer** (Mac, Windows, or Linux)
2. **Python 3.10+** ([Download](https://www.python.org/downloads/))
3. **Git** ([Download](https://git-scm.com/downloads))
4. **API Keys** (free signup):
   - Anthropic (Claude): https://console.anthropic.com/
   - OpenAI (GPT-4): https://platform.openai.com/

### What You'll Get

- A working AI software factory
- Ability to generate FHIR-compliant code
- $10 worth of free AI credits
- ~139 features for free!

---

## 🚀 Step-by-Step Setup

### Step 1: Get Your API Keys (5 minutes)

#### Anthropic (Claude)

1. Go to: https://console.anthropic.com/
2. Click "Sign Up"
3. Verify email
4. Go to "API Keys"
5. Click "Create Key"
6. Copy the key (starts with `sk-ant-`)
7. **Free credit**: $5 (good for 111 features!)

#### OpenAI (GPT-4)

1. Go to: https://platform.openai.com/
2. Click "Sign Up"
3. Verify email and phone
4. Go to "API Keys"
5. Click "Create new secret key"
6. Copy the key (starts with `sk-`)
7. **Free credit**: $5 (good for 28 features!)

**💾 Save these keys somewhere safe!**

---

### Step 2: Clone the Repository (2 minutes)

```bash
# Clone the repo
git clone <your-repo-url>
cd hive-factory-free-tier

# Verify files
ls
# Should see: agents/ config/ examples/ README.md etc.
```

---

### Step 3: Install Dependencies (5 minutes)

#### Option A: Using the Setup Script (Easiest)

```bash
# Make script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh

# This will:
# - Check Python version
# - Install all dependencies
# - Create workspace directory
# - Create .env file
```

#### Option B: Manual Installation

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry (recommended)
poetry install

# Create workspace
mkdir -p workspace

# Create environment file
cp .env.example .env
```

---

### Step 4: Configure Environment (3 minutes)

Open `.env` in your text editor and add your API keys:

```bash
# Required - Add your API keys here
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
OPENAI_API_KEY=sk-YOUR-KEY-HERE

# Optional - Keep defaults for testing
WORKSPACE_ROOT=./workspace
TENANT_ID=default
AWS_REGION=us-east-1
```

**⚠️ IMPORTANT**: Never commit `.env` to Git! It's already in `.gitignore`.

---

### Step 5: Run Your First Demo! (2 minutes)

```bash
# Run the demo script
python examples/demo.py

# You should see:
# ==================================================
# HIVE BIZOS FACTORY - DEMO
# ==================================================
# 
# DEMO MENU:
# 1. Full Demo: Appointment Cancellation (complex)
# 2. Simple Demo: Health Check Endpoint (simple)
# 3. Custom Feature
# 4. Exit
```

**Select option 2** (Simple Demo) for your first run.

---

### Step 6: Watch the Magic! ✨ (30 seconds)

The factory will:

```
🏗️  ARCHITECT: Analyzing request...
   ✅ Created plan for 'health_check_endpoint'
   - FHIR Resources: None
   - Steps: 2

👷 BUILDER: Implementing plan (iteration 1)...
   - Files created: 2
   - Lint status: pass
   ✅ Code passes all checks!

🧪 QA: Checking code quality...
   ✅ All checks passed!

==================================================
🏭 FACTORY ✅ COMPLETED
==================================================
Files created: 2
  ✓ app/api/health.py
  ✓ tests/test_health.py
```

**That's it! You just built your first feature!** 🎉

---

## 📂 What Just Happened?

### Generated Files

Check your `workspace/` directory:

```bash
ls workspace/
# app/
# tests/

cat workspace/app/api/health.py
# You'll see production-ready FastAPI code!
```

### Example Generated Code

```python
# workspace/app/api/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns API status and version.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0"
    )
```

**This code**:
- ✅ Passes `ruff` linting
- ✅ Passes `mypy` type checking
- ✅ Has tests
- ✅ Has documentation
- ✅ Is production-ready!

---

## 🎯 Try More Features

### Example 1: Appointment Cancellation (Complex)

```bash
python examples/demo.py
# Select option 1: Full Demo
```

This will generate:
- `app/models/appointment.py` - Pydantic models
- `app/services/appointment_service.py` - Business logic
- `app/api/appointments.py` - FastAPI endpoints
- `tests/test_appointment_cancel.py` - Comprehensive tests

**Time**: 15-30 seconds  
**Cost**: ~$0.22

### Example 2: Custom Feature

```bash
python examples/demo.py
# Select option 3: Custom Feature

# Enter: "Add patient search by name and date of birth"
```

The factory will:
1. Search FHIR Patient resource docs
2. Design HIPAA-compliant search
3. Implement fuzzy matching
4. Add proper validation
5. Create tests

**Time**: 20-40 seconds  
**Cost**: ~$0.30

---

## 💰 Cost Tracking

### Monitor Your Usage

**Anthropic**:
```
Visit: https://console.anthropic.com/settings/usage
See: API calls, tokens used, cost
```

**OpenAI**:
```
Visit: https://platform.openai.com/usage
See: API calls, tokens used, cost
```

### Expected Costs

| Activity | Features | Cost |
|----------|----------|------|
| **Today's demos** | 3-5 | $0.60-1.10 |
| **First week** (learning) | 10-20 | $2.20-4.40 |
| **First month** (building) | 50-100 | $11-22 |
| **Using free credits** | 139 | **$0!** |

Your free $10 in credits covers ~139 features!

---

## 🐛 Troubleshooting

### Issue: "Module not found"

```bash
# Re-install dependencies
pip install -r requirements.txt

# Or with Poetry
poetry install
```

### Issue: "API key invalid"

```bash
# Check your .env file
cat .env

# Make sure keys are correct:
# - Anthropic keys start with: sk-ant-
# - OpenAI keys start with: sk-

# No spaces or quotes needed in .env
```

### Issue: "Linter not found"

```bash
# Install ruff and mypy
pip install ruff mypy

# Verify installation
ruff --version
mypy --version
```

### Issue: "Permission denied"

```bash
# On Mac/Linux, make script executable
chmod +x scripts/setup.sh

# Then run
./scripts/setup.sh
```

### Still Having Issues?

1. Check the full error message
2. Read `docs/TROUBLESHOOTING.md`
3. Search existing GitHub issues
4. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Python version
   - Operating system

---

## 🌟 Next Steps

### 1. Understand the Architecture

Read `docs/ARCHITECTURE.md` to learn:
- How agents communicate
- The self-healing loop
- FHIR compliance mechanisms

### 2. Deploy to AWS (Optional)

For production use:

```bash
cd infrastructure/terraform

# Create terraform.tfvars
cat > terraform.tfvars << EOF
aws_region = "us-east-1"
db_password = "YourSecurePassword123!"
anthropic_api_key = "sk-ant-..."
openai_api_key = "sk-..."
EOF

# Deploy
terraform init
terraform apply
```

**Cost**: $0.40/month (first 12 months)

### 3. Optimize Costs

Read `docs/COST_OPTIMIZATION.md` to learn:
- How to reduce AI costs by 75%
- Prompt caching strategies
- Using cheaper models for simple features

### 4. Build Real Features

Try building parts of your actual application:

```bash
python examples/demo.py
# Select option 3: Custom

# Examples:
# - "Add patient registration with FHIR validation"
# - "Create appointment scheduling with conflict detection"
# - "Implement billing integration with account management"
```

### 5. Contribute

Help improve the factory:
- Add more FHIR resources
- Improve error handling
- Optimize costs
- Write documentation

See `CONTRIBUTING.md` for guidelines.

---

## 📚 Additional Resources

### Documentation

- **README.md**: Overview and features
- **ARCHITECTURE.md**: Deep dive into system design
- **COST_OPTIMIZATION.md**: Minimize your costs
- **TROUBLESHOOTING.md**: Common issues and solutions

### External Resources

- **FHIR Specification**: https://hl7.org/fhir/
- **PydanticAI Docs**: https://ai.pydantic.dev/
- **LangGraph Tutorial**: https://langchain-ai.github.io/langgraph/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

### Community

- **GitHub Issues**: Report bugs, request features
- **Discussions**: Ask questions, share ideas
- **Discord** (optional): Real-time chat

---

## ✅ Success Checklist

After completing this guide, you should be able to:

- [ ] Run `python examples/demo.py` successfully
- [ ] See generated code in `workspace/`
- [ ] Understand the basic factory flow
- [ ] Check your API usage costs
- [ ] Build a simple custom feature

**If you can do all of the above, you're ready!** 🚀

---

## 🎓 Learning Path

### Week 1: Basics
- Run demos
- Explore generated code
- Understand FHIR basics
- Try simple custom features

### Week 2: Customization
- Modify agent prompts
- Add custom tools
- Optimize for your use case
- Deploy to AWS (optional)

### Week 3: Production
- Build real application features
- Implement proper testing
- Set up CI/CD
- Monitor costs and quality

### Week 4: Advanced
- Contribute improvements
- Add new FHIR resources
- Optimize performance
- Scale to production

---

## 💡 Tips for Success

1. **Start Simple**: Begin with basic features, get comfortable
2. **Read Generated Code**: Learn from what the AI creates
3. **Monitor Costs**: Check usage daily at first
4. **Use Free Credits Wisely**: 139 features is plenty for learning
5. **Ask Questions**: Use GitHub Discussions
6. **Contribute Back**: Share improvements with the community

---

## 🎉 You Did It!

Congratulations! You now have:
- ✅ A working AI software factory
- ✅ Ability to generate production code
- ✅ Understanding of the basic workflow
- ✅ Free credits to keep experimenting

**Now go build something amazing!** 🏥🤖

---

**Questions?** Open an issue on GitHub  
**Found a bug?** We'd love to hear about it  
**Have an idea?** Start a discussion  

**Happy building!** 🚀
