#!/usr/bin/env python3
"""
Generate .env.example files from templates.

Quick tool to create environment configuration files for different domains.
"""

import sys
from pathlib import Path

# Import modules directly to avoid triggering genesis.__init__.py (which requires API keys)
import importlib.util

def import_module_by_path(name, path):
    """Import a module from a file path without triggering parent __init__.py"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # Add to sys.modules for subsequent imports
    spec.loader.exec_module(module)
    return module

# Get project root
project_root = Path(__file__).parent.parent

# Import standards module (required by env_templates)
standards_path = project_root / "genesis" / "standards.py"
standards = import_module_by_path("genesis.standards", standards_path)

# Import env_templates module
env_templates_path = project_root / "genesis" / "env_templates.py"
env_templates = import_module_by_path("genesis.env_templates", env_templates_path)

EnvTemplateBuilder = env_templates.EnvTemplateBuilder


def main():
    """Generate environment templates."""

    print("\n" + "="*60)
    print("Generate .env.example from Templates")
    print("="*60)

    print("\nSelect template:")
    print("1. Base (Genesis Engine only)")
    print("2. Healthcare (FHIR + HIPAA)")
    print("3. E-Commerce (Stripe + SendGrid)")
    print("4. Fintech (Plaid + KYC)")
    print("5. Base + AWS")

    choice = input("\nChoice (1-5): ").strip()

    templates = {
        "1": ("base", EnvTemplateBuilder.build_base_template()),
        "2": ("healthcare", EnvTemplateBuilder.build_healthcare_template()),
        "3": ("ecommerce", EnvTemplateBuilder.build_ecommerce_template()),
        "4": ("fintech", EnvTemplateBuilder.build_fintech_template()),
        "5": ("base_aws", EnvTemplateBuilder.build_with_aws(
            EnvTemplateBuilder.build_base_template()
        )),
    }

    if choice not in templates:
        print("❌ Invalid choice")
        return

    template_name, env_vars = templates[choice]

    # Get project name
    project_name = input("\nProject name (e.g., 'My Health App'): ").strip()
    if not project_name:
        project_name = f"{template_name.title()} Project"

    # Generate content
    content = EnvTemplateBuilder.generate_env_file(
        vars=env_vars,
        project_name=project_name,
        include_notes=True
    )

    # Save to file
    output_file = f"{project_name.lower().replace(' ', '_')}.env.example"
    with open(output_file, "w") as f:
        f.write(content)

    print(f"\n✅ Generated: {output_file}")
    print(f"   Variables: {len(env_vars)}")

    # Show breakdown
    var_types = {}
    for var in env_vars:
        var_type = var.var_type.value
        var_types[var_type] = var_types.get(var_type, 0) + 1

    print("\n📊 Variable Breakdown:")
    for var_type, count in sorted(var_types.items()):
        print(f"   - {var_type}: {count}")

    # Show required vs optional
    required = sum(1 for v in env_vars if v.required)
    optional = len(env_vars) - required

    print(f"\n   Required: {required}")
    print(f"   Optional: {optional}")

    # Next steps
    print("\n📝 Next Steps:")
    print(f"   1. Copy to .env: cp {output_file} .env")
    print("   2. Fill in required values (marked with '=')")
    print("   3. Add .env to .gitignore")
    print("   4. Never commit .env to version control!")


if __name__ == "__main__":
    main()
