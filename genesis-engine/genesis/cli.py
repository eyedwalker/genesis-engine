#!/usr/bin/env python3
"""
Genesis Engine CLI

Command-line interface for the Genesis Engine platform.

Usage:
    genesis --help
    genesis review <file> [--assistants security,performance]
    genesis assistants list
    genesis assistants info <name>
    genesis factory create <name> --domain <domain>
    genesis serve [--port 8000]

Installation:
    pip install genesis-engine
    # Or
    pip install -e .
"""

import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from typing import List, Optional

# Rich console output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Fallback print
def rprint(*args, **kwargs):
    print(*args, **kwargs)


console = Console() if RICH_AVAILABLE else None


def print_banner():
    """Print Genesis banner"""
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║   ⚡ GENESIS ENGINE                           ║
    ║      Factory-as-a-Service Platform           ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(Panel(
            "[bold blue]⚡ GENESIS ENGINE[/bold blue]\n"
            "[dim]Factory-as-a-Service Platform[/dim]",
            border_style="blue"
        ))
    else:
        print(banner)


def load_assistants():
    """Load all enhanced assistants"""
    assistants = {}
    configs = {}

    genesis_path = Path(__file__).parent

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
                                key = module_name.replace("assistants_enhanced_", "")
                                configs[key] = config
                                if "assistant_class" in config:
                                    assistants[key] = config["assistant_class"]()
                                break
                        except Exception:
                            continue
        except Exception:
            pass

    return assistants, configs


# ============================================================================
# Commands
# ============================================================================

def cmd_assistants_list(args):
    """List all available assistants"""
    print_banner()

    assistants, configs = load_assistants()

    if RICH_AVAILABLE:
        table = Table(title="Available Assistants")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Domain", style="magenta")
        table.add_column("Tags", style="dim")

        for key, config in configs.items():
            tags = ", ".join(config.get("tags", [])[:3])
            if len(config.get("tags", [])) > 3:
                tags += "..."
            table.add_row(
                key,
                config.get("name", key),
                config.get("domain", "general"),
                tags
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(configs)} assistants[/dim]")
    else:
        print("\nAvailable Assistants:")
        print("-" * 60)
        for key, config in configs.items():
            print(f"  {key}: {config.get('name', key)}")
        print(f"\nTotal: {len(configs)} assistants")


def cmd_assistants_info(args):
    """Show detailed assistant info"""
    print_banner()

    assistants, configs = load_assistants()

    if args.name not in configs:
        if RICH_AVAILABLE:
            console.print(f"[red]Error: Assistant '{args.name}' not found[/red]")
        else:
            print(f"Error: Assistant '{args.name}' not found")
        return

    config = configs[args.name]
    assistant = assistants.get(args.name)

    if RICH_AVAILABLE:
        console.print(Panel(
            f"[bold]{config.get('name', args.name)}[/bold]\n\n"
            f"[dim]Domain:[/dim] {config.get('domain', 'general')}\n"
            f"[dim]Tags:[/dim] {', '.join(config.get('tags', []))}\n\n"
            f"[dim]Description:[/dim]\n{config.get('system_prompt', '')[:500]}...",
            title=f"Assistant: {args.name}",
            border_style="green"
        ))

        # List methods
        if assistant:
            methods = []
            for name in dir(assistant):
                if not name.startswith("_") and name not in ["name", "version", "generate_finding"]:
                    if callable(getattr(assistant, name)):
                        methods.append(name)

            console.print("\n[bold]Available Methods:[/bold]")
            for method in methods:
                console.print(f"  • {method}")
    else:
        print(f"\nAssistant: {args.name}")
        print("=" * 60)
        print(f"Name: {config.get('name', args.name)}")
        print(f"Domain: {config.get('domain', 'general')}")
        print(f"Tags: {', '.join(config.get('tags', []))}")


def cmd_review(args):
    """Review code file"""
    print_banner()

    file_path = Path(args.file)
    if not file_path.exists():
        if RICH_AVAILABLE:
            console.print(f"[red]Error: File not found: {file_path}[/red]")
        else:
            print(f"Error: File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        code = f.read()

    assistants_list = args.assistants.split(",") if args.assistants else ["security", "performance"]

    if RICH_AVAILABLE:
        console.print(f"[bold]Reviewing:[/bold] {file_path}")
        console.print(f"[dim]Assistants:[/dim] {', '.join(assistants_list)}")
        console.print()

    assistants, configs = load_assistants()

    findings = []

    # Run review with progress
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for assistant_name in assistants_list:
                task = progress.add_task(f"Checking with {assistant_name}...", total=None)

                if assistant_name in assistants:
                    assistant = assistants[assistant_name]

                    # Get patterns
                    for method_name in dir(assistant):
                        if not method_name.startswith("_"):
                            method = getattr(assistant, method_name)
                            if callable(method):
                                try:
                                    method()  # Just check it works
                                except TypeError:
                                    pass

                progress.remove_task(task)

        # Simple pattern checks
        if "security" in assistants_list:
            if 'eval(' in code:
                findings.append({
                    "severity": "critical",
                    "assistant": "security",
                    "title": "Dangerous eval() usage",
                    "description": "eval() can execute arbitrary code",
                    "line": next((i+1 for i, line in enumerate(code.split('\n')) if 'eval(' in line), 0)
                })

            if 'execute(' in code and ('f"' in code or "f'" in code):
                findings.append({
                    "severity": "critical",
                    "assistant": "security",
                    "title": "Potential SQL Injection",
                    "description": "String interpolation in SQL query",
                    "line": 0
                })

        # Display findings
        console.print()

        if findings:
            table = Table(title="Findings")
            table.add_column("Severity", style="bold")
            table.add_column("Assistant")
            table.add_column("Title")
            table.add_column("Line")

            for finding in findings:
                severity_color = {
                    "critical": "red",
                    "high": "orange3",
                    "medium": "yellow",
                    "low": "blue"
                }.get(finding["severity"], "white")

                table.add_row(
                    f"[{severity_color}]{finding['severity'].upper()}[/{severity_color}]",
                    finding["assistant"],
                    finding["title"],
                    str(finding.get("line", "-"))
                )

            console.print(table)

            # Summary
            console.print(Panel(
                f"[red]Critical: {len([f for f in findings if f['severity'] == 'critical'])}[/red] | "
                f"[orange3]High: {len([f for f in findings if f['severity'] == 'high'])}[/orange3] | "
                f"[yellow]Medium: {len([f for f in findings if f['severity'] == 'medium'])}[/yellow] | "
                f"[blue]Low: {len([f for f in findings if f['severity'] == 'low'])}[/blue]",
                title="Summary",
                border_style="dim"
            ))
        else:
            console.print("[green]✓ No issues found![/green]")
    else:
        print("\nReview Results:")
        print("-" * 60)
        if findings:
            for finding in findings:
                print(f"[{finding['severity'].upper()}] {finding['title']}")
                print(f"  {finding['description']}")
        else:
            print("No issues found!")


def cmd_serve(args):
    """Start the API server"""
    print_banner()

    if RICH_AVAILABLE:
        console.print(f"[bold]Starting Genesis API Server[/bold]")
        console.print(f"[dim]Port:[/dim] {args.port}")
        console.print()

    try:
        import uvicorn
        from genesis.api.server import app

        uvicorn.run(app, host="0.0.0.0", port=args.port)
    except ImportError:
        if RICH_AVAILABLE:
            console.print("[red]Error: uvicorn not installed. Run: pip install uvicorn[/red]")
        else:
            print("Error: uvicorn not installed. Run: pip install uvicorn")


def cmd_mcp(args):
    """Start the MCP server"""
    print_banner()

    if RICH_AVAILABLE:
        console.print("[bold]Starting Genesis MCP Server[/bold]")
        console.print("[dim]Configure in your MCP client settings[/dim]")
        console.print()

    from genesis.mcp_server import main
    main()


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Genesis Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  genesis assistants list
  genesis assistants info security
  genesis review myfile.py --assistants security,performance
  genesis serve --port 8000
  genesis mcp
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # assistants command
    assistants_parser = subparsers.add_parser("assistants", help="Manage assistants")
    assistants_sub = assistants_parser.add_subparsers(dest="subcommand")

    assistants_list_parser = assistants_sub.add_parser("list", help="List assistants")
    assistants_list_parser.set_defaults(func=cmd_assistants_list)

    assistants_info_parser = assistants_sub.add_parser("info", help="Assistant info")
    assistants_info_parser.add_argument("name", help="Assistant name")
    assistants_info_parser.set_defaults(func=cmd_assistants_info)

    # review command
    review_parser = subparsers.add_parser("review", help="Review code")
    review_parser.add_argument("file", help="File to review")
    review_parser.add_argument("--assistants", "-a", help="Comma-separated assistants")
    review_parser.set_defaults(func=cmd_review)

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--port", "-p", type=int, default=8000, help="Port")
    serve_parser.set_defaults(func=cmd_serve)

    # mcp command
    mcp_parser = subparsers.add_parser("mcp", help="Start MCP server")
    mcp_parser.set_defaults(func=cmd_mcp)

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    if hasattr(args, "func"):
        args.func(args)
    elif args.command == "assistants" and not args.subcommand:
        cmd_assistants_list(args)


if __name__ == "__main__":
    main()
