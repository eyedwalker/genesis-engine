#!/usr/bin/env python3
"""
View and analyze software factory output.

Shows what the factory created, including:
- Generated code files
- Database models
- API endpoints
- Tests
- Configuration files
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import json


def find_latest_workspace(base_path: str = "./workspace") -> Path | None:
    """Find the most recently modified workspace."""
    base = Path(base_path)

    if not base.exists():
        return None

    # Check for tenant workspaces
    workspaces = []

    # Direct tenant directories
    for tenant_dir in base.iterdir():
        if tenant_dir.is_dir() and not tenant_dir.name.startswith('.'):
            workspaces.append(tenant_dir)

    # Snapshot directories
    snapshots = base / "snapshots"
    if snapshots.exists():
        for snapshot in snapshots.iterdir():
            if snapshot.is_dir():
                workspace = snapshot / "workspace"
                if workspace.exists():
                    workspaces.append(workspace)

    if not workspaces:
        return None

    # Return most recent
    return max(workspaces, key=lambda p: p.stat().st_mtime)


def analyze_workspace(workspace_path: Path) -> Dict:
    """Analyze workspace contents."""

    analysis = {
        "path": str(workspace_path),
        "files": {
            "total": 0,
            "python": 0,
            "tests": 0,
            "config": 0
        },
        "models": [],
        "api_endpoints": [],
        "services": [],
        "tests": [],
        "migrations": [],
        "docs": [],
        "lines_of_code": 0
    }

    # Walk directory
    for root, dirs, files in os.walk(workspace_path):
        # Skip hidden and cache dirs
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(workspace_path)

            analysis["files"]["total"] += 1

            # Python files
            if file.endswith('.py'):
                analysis["files"]["python"] += 1

                # Count lines
                try:
                    with open(file_path, 'r') as f:
                        lines = len(f.readlines())
                        analysis["lines_of_code"] += lines
                except:
                    pass

                # Categorize
                if 'test' in file or 'tests' in str(rel_path):
                    analysis["files"]["tests"] += 1
                    analysis["tests"].append(str(rel_path))
                elif 'model' in str(rel_path):
                    analysis["models"].append(str(rel_path))
                elif 'api' in str(rel_path) or 'endpoint' in str(rel_path):
                    analysis["api_endpoints"].append(str(rel_path))
                elif 'service' in str(rel_path):
                    analysis["services"].append(str(rel_path))
                elif 'migration' in str(rel_path) or 'alembic' in str(rel_path):
                    analysis["migrations"].append(str(rel_path))

            # Config files
            elif file in ['.env', '.env.example', 'config.py', 'settings.py', 'pyproject.toml']:
                analysis["files"]["config"] += 1

            # Docs
            elif file.endswith('.md'):
                analysis["docs"].append(str(rel_path))

    return analysis


def print_analysis(analysis: Dict):
    """Pretty print the analysis."""

    print("\n" + "="*60)
    print("📊 SOFTWARE FACTORY OUTPUT ANALYSIS")
    print("="*60)

    print(f"\n📁 Workspace: {analysis['path']}")

    print(f"\n📈 Statistics:")
    print(f"   Total files: {analysis['files']['total']}")
    print(f"   Python files: {analysis['files']['python']}")
    print(f"   Test files: {analysis['files']['tests']}")
    print(f"   Config files: {analysis['files']['config']}")
    print(f"   Lines of code: {analysis['lines_of_code']:,}")

    if analysis['models']:
        print(f"\n🗄️  Database Models ({len(analysis['models'])}):")
        for model in analysis['models'][:5]:
            print(f"   ✓ {model}")
        if len(analysis['models']) > 5:
            print(f"   ... and {len(analysis['models']) - 5} more")

    if analysis['api_endpoints']:
        print(f"\n🌐 API Endpoints ({len(analysis['api_endpoints'])}):")
        for endpoint in analysis['api_endpoints'][:5]:
            print(f"   ✓ {endpoint}")
        if len(analysis['api_endpoints']) > 5:
            print(f"   ... and {len(analysis['api_endpoints']) - 5} more")

    if analysis['services']:
        print(f"\n⚙️  Services ({len(analysis['services'])}):")
        for service in analysis['services'][:5]:
            print(f"   ✓ {service}")
        if len(analysis['services']) > 5:
            print(f"   ... and {len(analysis['services']) - 5} more")

    if analysis['tests']:
        print(f"\n🧪 Tests ({len(analysis['tests'])}):")
        for test in analysis['tests'][:5]:
            print(f"   ✓ {test}")
        if len(analysis['tests']) > 5:
            print(f"   ... and {len(analysis['tests']) - 5} more")

    if analysis['docs']:
        print(f"\n📚 Documentation ({len(analysis['docs'])}):")
        for doc in analysis['docs']:
            print(f"   ✓ {doc}")

    print("\n" + "="*60)


def show_file_preview(workspace_path: Path, file_path: str, lines: int = 30):
    """Show preview of a file."""

    full_path = workspace_path / file_path

    if not full_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"\n{'='*60}")
    print(f"📄 {file_path}")
    print("="*60)

    try:
        with open(full_path, 'r') as f:
            content = f.readlines()

            for i, line in enumerate(content[:lines], 1):
                print(f"{i:4d} | {line.rstrip()}")

            if len(content) > lines:
                print(f"\n... ({len(content) - lines} more lines)")

    except Exception as e:
        print(f"❌ Error reading file: {e}")


def interactive_browser(workspace_path: Path):
    """Interactive file browser."""

    analysis = analyze_workspace(workspace_path)

    while True:
        print("\n" + "="*60)
        print("🔍 FACTORY OUTPUT BROWSER")
        print("="*60)
        print("\nOptions:")
        print("1. View summary")
        print("2. Browse models")
        print("3. Browse API endpoints")
        print("4. Browse services")
        print("5. Browse tests")
        print("6. View specific file")
        print("7. Export analysis to JSON")
        print("8. Exit")

        choice = input("\nChoice (1-8): ").strip()

        if choice == "1":
            print_analysis(analysis)

        elif choice == "2":
            if not analysis['models']:
                print("No models found")
                continue
            print("\nModels:")
            for i, model in enumerate(analysis['models'], 1):
                print(f"{i}. {model}")
            idx = input("View model # (or Enter to skip): ").strip()
            if idx.isdigit():
                show_file_preview(workspace_path, analysis['models'][int(idx)-1])

        elif choice == "3":
            if not analysis['api_endpoints']:
                print("No API endpoints found")
                continue
            print("\nAPI Endpoints:")
            for i, endpoint in enumerate(analysis['api_endpoints'], 1):
                print(f"{i}. {endpoint}")
            idx = input("View endpoint # (or Enter to skip): ").strip()
            if idx.isdigit():
                show_file_preview(workspace_path, analysis['api_endpoints'][int(idx)-1])

        elif choice == "4":
            if not analysis['services']:
                print("No services found")
                continue
            print("\nServices:")
            for i, service in enumerate(analysis['services'], 1):
                print(f"{i}. {service}")
            idx = input("View service # (or Enter to skip): ").strip()
            if idx.isdigit():
                show_file_preview(workspace_path, analysis['services'][int(idx)-1])

        elif choice == "5":
            if not analysis['tests']:
                print("No tests found")
                continue
            print("\nTests:")
            for i, test in enumerate(analysis['tests'], 1):
                print(f"{i}. {test}")
            idx = input("View test # (or Enter to skip): ").strip()
            if idx.isdigit():
                show_file_preview(workspace_path, analysis['tests'][int(idx)-1])

        elif choice == "6":
            file_path = input("Enter file path (relative to workspace): ").strip()
            show_file_preview(workspace_path, file_path)

        elif choice == "7":
            output_file = "factory_analysis.json"
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"✅ Exported to {output_file}")

        elif choice == "8":
            break

        else:
            print("Invalid choice")


def main():
    """Main entry point."""

    # Find workspace
    print("🔍 Looking for factory output...")

    workspace = find_latest_workspace()

    if not workspace:
        print("❌ No factory output found in ./workspace/")
        print("\nRun the factory first:")
        print("  python3 examples/genesis_demo.py")
        return

    print(f"✅ Found workspace: {workspace}")

    # Analyze
    analysis = analyze_workspace(workspace)
    print_analysis(analysis)

    # Interactive mode
    mode = input("\nEnter interactive mode? (y/n): ").strip().lower()
    if mode == 'y':
        interactive_browser(workspace)


if __name__ == "__main__":
    main()
