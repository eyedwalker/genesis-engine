#!/usr/bin/env python3
"""
View Code Assistants Catalog.

Explore the specialized AI assistants available for code review and quality assurance.
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

# Import standards module (required by assistants)
standards_path = project_root / "genesis" / "standards.py"
standards = import_module_by_path("genesis.standards", standards_path)

# Import assistants module
assistants_path = project_root / "genesis" / "assistants.py"
assistants = import_module_by_path("genesis.assistants", assistants_path)

get_all_assistants = assistants.get_all_assistants
get_assistants_for_domain = assistants.get_assistants_for_domain
get_assistant_summary = assistants.get_assistant_summary


def display_assistant_detail(assistant):
    """Display detailed information about an assistant."""
    print("\n" + "="*60)
    print(f"📋 {assistant.name}")
    print("="*60)

    print(f"\n🏷️  Role: {assistant.role.value}")
    print(f"🤖 Model: {assistant.model}")
    print(f"⏰ When to invoke: {assistant.when_to_invoke}")

    if assistant.tools_needed:
        print(f"\n🛠️  Tools needed:")
        for tool in assistant.tools_needed:
            print(f"   - {tool}")

    print(f"\n📖 System Prompt Preview:")
    # Show first 500 characters of prompt
    prompt_preview = assistant.system_prompt.strip()[:500]
    print(prompt_preview)
    if len(assistant.system_prompt) > 500:
        print("   ... (truncated)")


def interactive_browser():
    """Interactive assistant browser."""
    while True:
        print("\n" + "="*60)
        print("Genesis Engine - Code Assistants Catalog")
        print("="*60)

        print("\nOptions:")
        print("1. View all assistants (summary)")
        print("2. Browse assistants by category")
        print("3. Get assistants for domain")
        print("4. View specific assistant details")
        print("5. Export catalog to file")
        print("6. Exit")

        choice = input("\nChoice (1-6): ").strip()

        if choice == "1":
            # Summary view
            print("\n" + get_assistant_summary())
            input("\nPress Enter to continue...")

        elif choice == "2":
            # Browse by category
            categories = {
                "Quality Assurance": [
                    "A11y Compliance Reviewer",
                    "Security Vulnerability Reviewer",
                    "Performance Optimizer"
                ],
                "Design & UX": [
                    "UX Content Writer"
                ],
                "Architecture": [
                    "API Design Reviewer",
                    "Database Schema Reviewer"
                ],
                "Domain-Specific": [
                    "FHIR Compliance Reviewer",
                    "PCI-DSS Compliance Reviewer"
                ],
            }

            print("\nCategories:")
            for i, category in enumerate(categories.keys(), 1):
                print(f"{i}. {category}")

            cat_choice = input("\nSelect category (1-4): ").strip()
            cat_idx = int(cat_choice) - 1 if cat_choice.isdigit() else -1

            if 0 <= cat_idx < len(categories):
                category = list(categories.keys())[cat_idx]
                assistants_in_cat = categories[category]

                print(f"\n{category}:")
                for assistant_name in assistants_in_cat:
                    print(f"  - {assistant_name}")

                input("\nPress Enter to continue...")

        elif choice == "3":
            # Get assistants for domain
            print("\nEnter domain keywords (e.g., healthcare, ecommerce, fintech):")
            domain = input("Domain: ").strip()

            assistants = get_assistants_for_domain(domain)

            print(f"\n✅ Recommended assistants for '{domain}':")
            for assistant in assistants:
                print(f"   - {assistant.name}")

            print(f"\nTotal: {len(assistants)} assistants")

            detail = input("\nView details for any? (y/n): ").strip().lower()
            if detail == "y":
                for i, assistant in enumerate(assistants, 1):
                    print(f"{i}. {assistant.name}")

                idx_str = input("\nSelect assistant (number): ").strip()
                if idx_str.isdigit():
                    idx = int(idx_str) - 1
                    if 0 <= idx < len(assistants):
                        display_assistant_detail(assistants[idx])
                        input("\nPress Enter to continue...")

        elif choice == "4":
            # View specific assistant
            all_assistants = get_all_assistants()

            print("\nAvailable assistants:")
            for i, assistant in enumerate(all_assistants, 1):
                print(f"{i}. {assistant.name}")

            idx_str = input("\nSelect assistant (1-8): ").strip()
            if idx_str.isdigit():
                idx = int(idx_str) - 1
                if 0 <= idx < len(all_assistants):
                    display_assistant_detail(all_assistants[idx])
                    input("\nPress Enter to continue...")

        elif choice == "5":
            # Export to file
            filename = input("\nFilename (default: assistants_catalog.md): ").strip()
            if not filename:
                filename = "assistants_catalog.md"

            content = get_assistant_summary()

            # Add full details
            content += "\n\n# Detailed Information\n"

            all_assistants = get_all_assistants()
            for assistant in all_assistants:
                content += f"\n## {assistant.name}\n"
                content += f"- **Role**: {assistant.role.value}\n"
                content += f"- **Model**: {assistant.model}\n"
                content += f"- **When to invoke**: {assistant.when_to_invoke}\n"

                if assistant.tools_needed:
                    content += "\n**Tools needed:**\n"
                    for tool in assistant.tools_needed:
                        content += f"- {tool}\n"

                content += "\n**System Prompt:**\n"
                content += f"```\n{assistant.system_prompt.strip()}\n```\n"

            with open(filename, "w") as f:
                f.write(content)

            print(f"\n✅ Exported to: {filename}")
            input("\nPress Enter to continue...")

        elif choice == "6":
            print("\n👋 Goodbye!")
            break

        else:
            print("\n❌ Invalid choice")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1]

        if command == "list":
            # List all assistants
            assistants = get_all_assistants()
            print("Available Assistants:")
            for assistant in assistants:
                print(f"  - {assistant.name} ({assistant.role.value})")

        elif command == "summary":
            # Show summary
            print(get_assistant_summary())

        elif command == "domain":
            # Get assistants for domain
            if len(sys.argv) < 3:
                print("Usage: view_assistants.py domain <domain_name>")
                return

            domain = sys.argv[2]
            assistants = get_assistants_for_domain(domain)

            print(f"Recommended assistants for '{domain}':")
            for assistant in assistants:
                print(f"  - {assistant.name}")

        elif command == "export":
            # Export catalog
            filename = sys.argv[2] if len(sys.argv) > 2 else "assistants_catalog.md"

            content = get_assistant_summary()

            all_assistants = get_all_assistants()
            content += "\n\n# Detailed Information\n"

            for assistant in all_assistants:
                content += f"\n## {assistant.name}\n"
                content += f"- **Role**: {assistant.role.value}\n"
                content += f"- **Model**: {assistant.model}\n"
                content += f"- **When**: {assistant.when_to_invoke}\n\n"

            with open(filename, "w") as f:
                f.write(content)

            print(f"✅ Exported to: {filename}")

        else:
            print(f"Unknown command: {command}")
            print("Available commands: list, summary, domain, export")

    else:
        # Interactive mode
        interactive_browser()


if __name__ == "__main__":
    main()
