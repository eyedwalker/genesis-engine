#!/bin/bash
# Hive BizOS Factory - Quick Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "=================================="
echo "Hive BizOS Factory - Quick Setup"
echo "=================================="
echo ""

# ============================================================================
# Step 1: Check Python Version
# ============================================================================

echo "📋 Checking Python version..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"
echo ""

# ============================================================================
# Step 2: Install Dependencies
# ============================================================================

echo "📦 Installing Python dependencies..."

# Check if Poetry is available
if command -v poetry &> /dev/null; then
    echo "   Using Poetry..."
    poetry install
else
    echo "   Using pip..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
fi

echo "✅ Dependencies installed"
echo ""

# ============================================================================
# Step 3: Setup Environment File
# ============================================================================

echo "🔧 Setting up environment file..."

if [ -f ".env" ]; then
    echo "⚠️  .env already exists, skipping..."
else
    cp .env.example .env
    echo "✅ Created .env from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
    echo ""
    echo "   Required:"
    echo "   - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)"
    echo "   - OPENAI_API_KEY (get from https://platform.openai.com/)"
    echo ""
fi

# ============================================================================
# Step 4: Create Workspace Directory
# ============================================================================

echo "📁 Creating workspace directory..."

mkdir -p workspace
echo "✅ Workspace created at ./workspace"
echo ""

# ============================================================================
# Step 5: Verify Installation
# ============================================================================

echo "🧪 Verifying installation..."

# Try importing key packages
python3 -c "import pydantic_ai; import langgraph; import anthropic; import openai" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ All packages imported successfully"
else
    echo "❌ Package import failed"
    echo "   Run: pip install -r requirements.txt"
    exit 1
fi

echo ""

# ============================================================================
# Step 6: Check for Terraform (Optional)
# ============================================================================

echo "🔍 Checking for Terraform (optional)..."

if command -v terraform &> /dev/null; then
    TERRAFORM_VERSION=$(terraform --version | head -1 | cut -d 'v' -f 2)
    echo "✅ Terraform $TERRAFORM_VERSION found"
else
    echo "⚠️  Terraform not found (optional for local testing)"
    echo "   Install from: https://www.terraform.io/downloads"
fi

echo ""

# ============================================================================
# Summary
# ============================================================================

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env and add your API keys:"
echo "   - ANTHROPIC_API_KEY=sk-ant-..."
echo "   - OPENAI_API_KEY=sk-..."
echo ""
echo "2. Run the demo:"
echo "   python3 examples/demo.py"
echo ""
echo "3. (Optional) Deploy to AWS:"
echo "   cd infrastructure/terraform"
echo "   terraform init"
echo "   terraform apply"
echo ""
echo "📚 Read README.md for full documentation"
echo ""
echo "Need help? Open an issue on GitHub"
echo ""
