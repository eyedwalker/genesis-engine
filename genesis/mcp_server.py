#!/usr/bin/env python3
"""
Genesis MCP Server - Model Context Protocol Server for Genesis Assistants

This MCP server exposes Genesis Engine assistants to any MCP-compatible tool:
- Claude Code (CLI)
- Claude Desktop
- Cursor
- Cline
- Continue
- Any MCP-compatible IDE/tool

Features:
- Code review with 18 specialized assistants
- Architecture pattern guidance (VBD, Clean, Hexagonal)
- Compliance checking (GDPR, HIPAA, PCI-DSS, SOC2)
- Performance optimization recommendations
- Accessibility auditing (WCAG 2.2)

Usage:
    # Start the server
    python -m genesis.mcp_server

    # Configure in Claude Code (~/.claude/settings.json):
    {
        "mcpServers": {
            "genesis": {
                "command": "python",
                "args": ["-m", "genesis.mcp_server"],
                "cwd": "/path/to/wuhbah"
            }
        }
    }

    # Or with uvx (recommended):
    {
        "mcpServers": {
            "genesis": {
                "command": "uvx",
                "args": ["--from", "genesis-engine", "genesis-mcp"]
            }
        }
    }
"""

import asyncio
import json
import sys
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# MCP Protocol Implementation
# Using stdio transport for maximum compatibility


class MCPMessageType(str, Enum):
    """MCP message types"""
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class MCPResource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"


@dataclass
class MCPPrompt:
    """MCP Prompt template"""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)


class GenesisAssistantLoader:
    """Dynamically loads Genesis assistants"""

    def __init__(self):
        self.assistants: Dict[str, Any] = {}
        self.assistant_configs: Dict[str, Dict] = {}
        self._load_assistants()

    def _load_assistants(self):
        """Discover and load all enhanced assistants"""
        genesis_path = Path(__file__).parent

        for file in genesis_path.glob("assistants_enhanced_*.py"):
            if file.name == "assistants_enhanced_example.py":
                continue

            module_name = file.stem
            try:
                # Import the module
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
                                    self.assistant_configs[assistant_key] = config

                                    # Instantiate the class
                                    if "assistant_class" in config:
                                        self.assistants[assistant_key] = config["assistant_class"]()
                                    break
                            except Exception:
                                continue

            except Exception as e:
                print(f"Warning: Could not load {module_name}: {e}", file=sys.stderr)

    def get_assistant(self, name: str) -> Optional[Any]:
        """Get an assistant instance by name"""
        return self.assistants.get(name)

    def get_config(self, name: str) -> Optional[Dict]:
        """Get assistant config by name"""
        return self.assistant_configs.get(name)

    def list_assistants(self) -> List[str]:
        """List all available assistants"""
        return list(self.assistants.keys())


class GenesisMCPServer:
    """MCP Server exposing Genesis assistants"""

    def __init__(self):
        self.loader = GenesisAssistantLoader()
        self.server_info = {
            "name": "genesis-assistants",
            "version": "1.0.0",
            "description": "Genesis Engine code review assistants"
        }

    def get_tools(self) -> List[MCPTool]:
        """Define available MCP tools"""
        tools = [
            # Core review tool
            MCPTool(
                name="genesis_review_code",
                description="Review code using Genesis assistants. Supports security, accessibility, performance, and compliance checks.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to review"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (python, javascript, typescript, etc.)",
                            "default": "python"
                        },
                        "assistants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": f"Which assistants to use. Available: {', '.join(self.loader.list_assistants())}",
                            "default": ["security", "performance"]
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context about the code (e.g., 'API endpoint', 'database query')"
                        }
                    },
                    "required": ["code"]
                }
            ),

            # Get specific patterns
            MCPTool(
                name="genesis_get_patterns",
                description="Get best practice patterns from a specific assistant (e.g., security patterns, caching strategies)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "assistant": {
                            "type": "string",
                            "description": f"Assistant name. Available: {', '.join(self.loader.list_assistants())}"
                        },
                        "category": {
                            "type": "string",
                            "description": "Specific category/topic (e.g., 'sql_injection', 'cache_stampede', 'wcag_aa')"
                        }
                    },
                    "required": ["assistant"]
                }
            ),

            # Architecture guidance
            MCPTool(
                name="genesis_architecture_guide",
                description="Get architecture pattern guidance (VBD, Clean Architecture, CQRS, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "enum": ["vbd", "clean", "hexagonal", "cqrs", "event_driven", "layered"],
                            "description": "Architecture pattern"
                        },
                        "component": {
                            "type": "string",
                            "description": "Specific component type (engine, manager, adapter, dto)"
                        }
                    },
                    "required": ["pattern"]
                }
            ),

            # Generate code scaffold
            MCPTool(
                name="genesis_scaffold",
                description="Generate code scaffolding using VBD architecture patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Domain name (e.g., 'Order', 'Payment', 'User')"
                        },
                        "components": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["dto", "engine", "manager", "adapter", "interface"]
                            },
                            "description": "Components to generate",
                            "default": ["dto", "engine", "manager"]
                        }
                    },
                    "required": ["domain"]
                }
            ),

            # Compliance check
            MCPTool(
                name="genesis_compliance_check",
                description="Check code against compliance standards (GDPR, HIPAA, PCI-DSS, SOC2, FHIR)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code to check"
                        },
                        "standards": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["gdpr", "hipaa", "pci_dss", "soc2", "fhir"]
                            },
                            "description": "Compliance standards to check against"
                        }
                    },
                    "required": ["code", "standards"]
                }
            ),

            # List assistants
            MCPTool(
                name="genesis_list_assistants",
                description="List all available Genesis assistants with their capabilities",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]

        return tools

    def get_resources(self) -> List[MCPResource]:
        """Define available MCP resources"""
        resources = []

        # Add each assistant as a resource
        for name in self.loader.list_assistants():
            config = self.loader.get_config(name)
            if config:
                resources.append(MCPResource(
                    uri=f"genesis://assistant/{name}",
                    name=f"Genesis {config.get('name', name)}",
                    description=config.get("system_prompt", "")[:200] + "...",
                    mimeType="application/json"
                ))

        # Add architecture patterns resource
        resources.append(MCPResource(
            uri="genesis://patterns/vbd",
            name="VBD Architecture Patterns",
            description="Volatility-Based Decomposition architecture patterns and templates",
            mimeType="application/json"
        ))

        return resources

    def get_prompts(self) -> List[MCPPrompt]:
        """Define available MCP prompts"""
        return [
            MCPPrompt(
                name="security_review",
                description="Comprehensive security review using OWASP Top 10",
                arguments=[
                    {"name": "code", "description": "Code to review", "required": True}
                ]
            ),
            MCPPrompt(
                name="accessibility_audit",
                description="WCAG 2.2 accessibility audit",
                arguments=[
                    {"name": "code", "description": "UI code to audit", "required": True},
                    {"name": "level", "description": "WCAG level (A, AA, AAA)", "required": False}
                ]
            ),
            MCPPrompt(
                name="performance_optimization",
                description="Performance optimization recommendations",
                arguments=[
                    {"name": "code", "description": "Code to optimize", "required": True},
                    {"name": "target", "description": "Target metric (LCP, INP, CLS)", "required": False}
                ]
            ),
            MCPPrompt(
                name="architecture_design",
                description="Architecture design guidance",
                arguments=[
                    {"name": "requirements", "description": "Feature requirements", "required": True},
                    {"name": "pattern", "description": "Preferred pattern (vbd, clean, hexagonal)", "required": False}
                ]
            ),
        ]

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""

        if tool_name == "genesis_list_assistants":
            return self._list_assistants()

        elif tool_name == "genesis_review_code":
            return await self._review_code(
                code=arguments.get("code", ""),
                language=arguments.get("language", "python"),
                assistants=arguments.get("assistants", ["security", "performance"]),
                context=arguments.get("context", "")
            )

        elif tool_name == "genesis_get_patterns":
            return self._get_patterns(
                assistant=arguments.get("assistant", ""),
                category=arguments.get("category")
            )

        elif tool_name == "genesis_architecture_guide":
            return self._get_architecture_guide(
                pattern=arguments.get("pattern", "vbd"),
                component=arguments.get("component")
            )

        elif tool_name == "genesis_scaffold":
            return self._generate_scaffold(
                domain=arguments.get("domain", ""),
                components=arguments.get("components", ["dto", "engine", "manager"])
            )

        elif tool_name == "genesis_compliance_check":
            return await self._compliance_check(
                code=arguments.get("code", ""),
                standards=arguments.get("standards", [])
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _list_assistants(self) -> Dict[str, Any]:
        """List all available assistants"""
        assistants = []

        for name in self.loader.list_assistants():
            config = self.loader.get_config(name)
            if config:
                assistants.append({
                    "name": name,
                    "display_name": config.get("name", name),
                    "domain": config.get("domain", "general"),
                    "tags": config.get("tags", []),
                    "description": config.get("system_prompt", "")[:300]
                })

        return {
            "assistants": assistants,
            "count": len(assistants)
        }

    async def _review_code(
        self,
        code: str,
        language: str,
        assistants: List[str],
        context: str
    ) -> Dict[str, Any]:
        """Review code using specified assistants"""
        findings = []

        for assistant_name in assistants:
            assistant = self.loader.get_assistant(assistant_name)
            if not assistant:
                findings.append({
                    "assistant": assistant_name,
                    "error": f"Assistant '{assistant_name}' not found"
                })
                continue

            # Get patterns from assistant
            patterns = {}
            for method_name in dir(assistant):
                if not method_name.startswith("_") and method_name not in ["name", "version", "generate_finding"]:
                    method = getattr(assistant, method_name)
                    if callable(method):
                        try:
                            result = method()
                            if isinstance(result, dict):
                                patterns[method_name] = result
                        except TypeError:
                            # Method requires arguments
                            pass

            findings.append({
                "assistant": assistant_name,
                "config": self.loader.get_config(assistant_name),
                "patterns": patterns,
                "review_context": {
                    "language": language,
                    "context": context,
                    "code_length": len(code)
                }
            })

        return {
            "code_preview": code[:500] + "..." if len(code) > 500 else code,
            "language": language,
            "assistants_used": assistants,
            "findings": findings
        }

    def _get_patterns(self, assistant: str, category: Optional[str]) -> Dict[str, Any]:
        """Get patterns from specific assistant"""
        assistant_obj = self.loader.get_assistant(assistant)
        if not assistant_obj:
            return {"error": f"Assistant '{assistant}' not found"}

        patterns = {}
        for method_name in dir(assistant_obj):
            if method_name.startswith("_"):
                continue
            if method_name in ["name", "version", "generate_finding"]:
                continue

            method = getattr(assistant_obj, method_name)
            if callable(method):
                try:
                    result = method()
                    if isinstance(result, dict):
                        # Filter by category if specified
                        if category:
                            if category.lower() in method_name.lower():
                                patterns[method_name] = result
                        else:
                            patterns[method_name] = result
                except TypeError:
                    pass

        return {
            "assistant": assistant,
            "category": category,
            "patterns": patterns
        }

    def _get_architecture_guide(self, pattern: str, component: Optional[str]) -> Dict[str, Any]:
        """Get architecture pattern guidance"""
        try:
            from .architecture_patterns import (
                VBDArchitectureSpec,
                VBDCodeTemplates,
                LayeredArchitectureSpec,
                CleanArchitectureSpec
            )

            if pattern == "vbd":
                spec = VBDArchitectureSpec()
                templates = VBDCodeTemplates()

                result = {
                    "pattern": "vbd",
                    "description": "Volatility-Based Decomposition",
                    "layers": [layer.value for layer in spec.layers],
                    "dependency_rules": spec.dependency_rules,
                    "testing_strategy": spec.testing_strategy,
                    "directory_structure": spec.directory_structure
                }

                if component:
                    if component == "engine":
                        result["template"] = templates.engine_template()
                        result["responsibilities"] = spec.engine_responsibilities
                    elif component == "manager":
                        result["template"] = templates.manager_template()
                        result["responsibilities"] = spec.manager_responsibilities
                    elif component == "adapter":
                        result["template"] = templates.adapter_template()
                        result["responsibilities"] = spec.adapter_responsibilities
                    elif component == "dto":
                        result["template"] = templates.dto_template()
                        result["responsibilities"] = spec.dto_responsibilities
                    elif component == "interface":
                        result["template"] = templates.interface_template()
                        result["responsibilities"] = spec.interface_responsibilities

                return result

            elif pattern == "layered":
                spec = LayeredArchitectureSpec()
                return {
                    "pattern": "layered",
                    "description": "Traditional N-tier layered architecture",
                    "layers": spec.layers
                }

            elif pattern == "clean":
                spec = CleanArchitectureSpec()
                return {
                    "pattern": "clean",
                    "description": "Clean Architecture (Uncle Bob)",
                    "layers": spec.layers
                }

            else:
                return {"error": f"Unknown pattern: {pattern}"}

        except ImportError as e:
            return {"error": f"Could not load architecture patterns: {e}"}

    def _generate_scaffold(self, domain: str, components: List[str]) -> Dict[str, Any]:
        """Generate code scaffolding"""
        try:
            from .architecture_patterns import VBDCodeTemplates

            templates = VBDCodeTemplates()
            generated = {}

            replacements = {
                "{domain}": domain,
                "{domain_lower}": domain.lower(),
                "{domain_description}": f"{domain} operations",
                "{operation}": domain.lower(),
            }

            for component in components:
                if component == "dto":
                    template = templates.dto_template()
                elif component == "engine":
                    template = templates.engine_template()
                elif component == "manager":
                    template = templates.manager_template()
                elif component == "adapter":
                    template = templates.adapter_template()
                    replacements["{system}"] = "Database"
                    replacements["{system_lower}"] = "database"
                    replacements["{interface}"] = "Repository"
                    replacements["{interface_lower}"] = "repository"
                    replacements["{resource}"] = domain.lower() + "s"
                elif component == "interface":
                    template = templates.interface_template()
                    replacements["{interface}"] = "Repository"
                    replacements["{interface_description}"] = f"{domain} data access"
                else:
                    continue

                # Apply replacements
                code = template
                for key, value in replacements.items():
                    code = code.replace(key, value)

                generated[component] = {
                    "filename": f"{domain.lower()}_{component}.py",
                    "code": code
                }

            return {
                "domain": domain,
                "components": list(generated.keys()),
                "files": generated
            }

        except ImportError as e:
            return {"error": f"Could not generate scaffold: {e}"}

    async def _compliance_check(self, code: str, standards: List[str]) -> Dict[str, Any]:
        """Check code against compliance standards"""
        results = []

        standard_to_assistant = {
            "gdpr": "gdpr",
            "hipaa": "fhir",  # FHIR assistant covers HIPAA
            "pci_dss": "pci_dss",
            "soc2": "soc2",
            "fhir": "fhir"
        }

        for standard in standards:
            assistant_name = standard_to_assistant.get(standard)
            if not assistant_name:
                results.append({
                    "standard": standard,
                    "error": f"No assistant for standard: {standard}"
                })
                continue

            assistant = self.loader.get_assistant(assistant_name)
            if not assistant:
                results.append({
                    "standard": standard,
                    "error": f"Assistant '{assistant_name}' not loaded"
                })
                continue

            # Get compliance patterns
            patterns = {}
            for method_name in dir(assistant):
                if not method_name.startswith("_"):
                    method = getattr(assistant, method_name)
                    if callable(method):
                        try:
                            result = method()
                            if isinstance(result, dict):
                                patterns[method_name] = result
                        except TypeError:
                            pass

            results.append({
                "standard": standard,
                "assistant": assistant_name,
                "requirements": patterns
            })

        return {
            "code_preview": code[:200] + "..." if len(code) > 200 else code,
            "standards_checked": standards,
            "results": results
        }

    async def handle_resource_read(self, uri: str) -> Dict[str, Any]:
        """Handle MCP resource reads"""
        if uri.startswith("genesis://assistant/"):
            assistant_name = uri.replace("genesis://assistant/", "")
            return self._get_patterns(assistant_name, None)

        elif uri == "genesis://patterns/vbd":
            return self._get_architecture_guide("vbd", None)

        return {"error": f"Unknown resource: {uri}"}

    async def handle_prompt_get(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP prompt requests"""
        prompts = {
            "security_review": """Review the following code for security vulnerabilities:

```
{code}
```

Check for:
1. OWASP Top 10 vulnerabilities
2. Input validation issues
3. Authentication/authorization flaws
4. Data exposure risks
5. Injection vulnerabilities

Provide specific line numbers and remediation suggestions.""",

            "accessibility_audit": """Audit the following UI code for WCAG 2.2 {level} compliance:

```
{code}
```

Check for:
1. Keyboard navigation
2. Screen reader compatibility
3. Color contrast
4. Focus management
5. ARIA usage

Provide specific issues and fixes.""",

            "performance_optimization": """Analyze the following code for performance issues:

```
{code}
```

Focus on:
1. Core Web Vitals ({target})
2. Database query optimization
3. Memory usage
4. Caching opportunities
5. Async/await patterns

Provide specific optimization recommendations.""",

            "architecture_design": """Design an architecture for the following requirements:

{requirements}

Use {pattern} architecture pattern.

Provide:
1. Component structure
2. Data flow
3. API design
4. Error handling approach
5. Testing strategy"""
        }

        template = prompts.get(name)
        if not template:
            return {"error": f"Unknown prompt: {name}"}

        # Fill in arguments
        for key, value in arguments.items():
            template = template.replace("{" + key + "}", str(value))

        # Set defaults for unfilled placeholders
        template = template.replace("{level}", "AA")
        template = template.replace("{target}", "LCP, INP, CLS")
        template = template.replace("{pattern}", "VBD")

        return {
            "name": name,
            "prompt": template
        }


# ============================================================================
# MCP Protocol Handler (stdio)
# ============================================================================

async def handle_mcp_message(server: GenesisMCPServer, message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming MCP messages"""
    method = message.get("method", "")
    params = message.get("params", {})
    msg_id = message.get("id")

    response = {"jsonrpc": "2.0", "id": msg_id}

    try:
        if method == "initialize":
            response["result"] = {
                "protocolVersion": "2024-11-05",
                "serverInfo": server.server_info,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False}
                }
            }

        elif method == "initialized":
            response["result"] = {}

        elif method == "tools/list":
            tools = server.get_tools()
            response["result"] = {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema
                    }
                    for t in tools
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = await server.handle_tool_call(tool_name, arguments)
            response["result"] = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }

        elif method == "resources/list":
            resources = server.get_resources()
            response["result"] = {
                "resources": [
                    {
                        "uri": r.uri,
                        "name": r.name,
                        "description": r.description,
                        "mimeType": r.mimeType
                    }
                    for r in resources
                ]
            }

        elif method == "resources/read":
            uri = params.get("uri", "")
            result = await server.handle_resource_read(uri)
            response["result"] = {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }

        elif method == "prompts/list":
            prompts = server.get_prompts()
            response["result"] = {
                "prompts": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "arguments": p.arguments
                    }
                    for p in prompts
                ]
            }

        elif method == "prompts/get":
            name = params.get("name", "")
            arguments = params.get("arguments", {})
            result = await server.handle_prompt_get(name, arguments)
            response["result"] = {
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": result.get("prompt", "")
                        }
                    }
                ]
            }

        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}"
            }

    except Exception as e:
        response["error"] = {
            "code": -32603,
            "message": str(e)
        }

    return response


async def run_stdio_server():
    """Run MCP server using stdio transport"""
    server = GenesisMCPServer()

    print(f"Genesis MCP Server starting...", file=sys.stderr)
    print(f"Loaded {len(server.loader.list_assistants())} assistants", file=sys.stderr)

    # Read from stdin, write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            # Read line from stdin
            line = await reader.readline()
            if not line:
                break

            line = line.decode().strip()
            if not line:
                continue

            # Parse JSON-RPC message
            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                continue

            # Handle message
            response = await handle_mcp_message(server, message)

            # Write response
            print(json.dumps(response), flush=True)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            break


def main():
    """Main entry point"""
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()
