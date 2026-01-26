"""
Comprehensive Test Suite for Enhanced Assistants

Tests each assistant for:
1. Factory function validity
2. Class instantiation
3. Static method outputs
4. Code example syntax
5. Required fields and structure
"""

import ast
import sys
import json
import importlib
import traceback
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result"""
    name: str
    status: TestStatus
    message: str = ""
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssistantTestSuite:
    """Test results for a single assistant"""
    assistant_name: str
    module_name: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    results: List[TestResult] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100


@dataclass
class FullTestReport:
    """Complete test report for all assistants"""
    timestamp: str
    total_assistants: int = 0
    total_tests: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_errors: int = 0
    assistant_results: List[AssistantTestSuite] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def overall_success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.total_passed / self.total_tests) * 100


class AssistantTester:
    """Test runner for enhanced assistants"""

    REQUIRED_FACTORY_KEYS = ["name", "version", "system_prompt", "assistant_class", "domain", "tags"]

    def __init__(self):
        self.assistant_modules = self._discover_assistants()

    def _discover_assistants(self) -> List[str]:
        """Find all enhanced assistant modules"""
        genesis_path = Path(__file__).parent.parent
        modules = []

        for file in genesis_path.glob("assistants_enhanced_*.py"):
            if file.name != "assistants_enhanced_example.py":  # Skip example
                module_name = file.stem
                modules.append(module_name)

        return sorted(modules)

    def _import_module(self, module_name: str):
        """Import an assistant module"""
        try:
            # Add parent to path if needed
            genesis_path = str(Path(__file__).parent.parent)
            if genesis_path not in sys.path:
                sys.path.insert(0, genesis_path)

            return importlib.import_module(module_name)
        except Exception as e:
            raise ImportError(f"Failed to import {module_name}: {e}")

    def _validate_python_syntax(self, code: str, context: str = "") -> Tuple[bool, str]:
        """Check if code string is valid Python syntax"""
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def _extract_code_examples(self, data: Any, path: str = "") -> List[Tuple[str, str]]:
        """Recursively extract code examples from nested data"""
        examples = []

        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key

                # Check if this looks like a code example
                if isinstance(value, str) and len(value) > 50:
                    # Heuristics for code detection
                    code_indicators = [
                        "def ", "class ", "import ", "from ",
                        "async def", "await ", "return ", "yield ",
                        "if __name__", "try:", "except:", "with ",
                        "# ", "'''", '"""', "->", "=>",
                    ]
                    if any(ind in value for ind in code_indicators):
                        examples.append((new_path, value))

                # Recurse into nested structures
                examples.extend(self._extract_code_examples(value, new_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                examples.extend(self._extract_code_examples(item, f"{path}[{i}]"))

        return examples

    def test_factory_function(self, module, module_name: str) -> List[TestResult]:
        """Test the factory function"""
        results = []

        # Find factory function - allow flexible naming (assistant, optimizer, analyzer, etc.)
        factory_name = None
        for name in dir(module):
            if name.startswith("create_enhanced_") and callable(getattr(module, name, None)):
                # Accept any create_enhanced_* function that returns a dict
                func = getattr(module, name)
                try:
                    result = func()
                    if isinstance(result, dict) and "name" in result:
                        factory_name = name
                        break
                except:
                    continue

        if not factory_name:
            results.append(TestResult(
                name="factory_function_exists",
                status=TestStatus.FAILED,
                message="No factory function found (expected create_enhanced_* returning dict with 'name' key)"
            ))
            return results

        results.append(TestResult(
            name="factory_function_exists",
            status=TestStatus.PASSED,
            message=f"Found {factory_name}"
        ))

        # Call factory function
        try:
            factory_func = getattr(module, factory_name)
            config = factory_func()

            results.append(TestResult(
                name="factory_function_callable",
                status=TestStatus.PASSED,
                message="Factory function executed successfully"
            ))

            # Check required keys
            missing_keys = [k for k in self.REQUIRED_FACTORY_KEYS if k not in config]
            if missing_keys:
                results.append(TestResult(
                    name="factory_required_keys",
                    status=TestStatus.FAILED,
                    message=f"Missing required keys: {missing_keys}",
                    details={"missing": missing_keys, "present": list(config.keys())}
                ))
            else:
                results.append(TestResult(
                    name="factory_required_keys",
                    status=TestStatus.PASSED,
                    message="All required keys present",
                    details={"keys": list(config.keys())}
                ))

            # Validate types
            type_checks = [
                ("name", str),
                ("version", str),
                ("system_prompt", str),
                ("domain", str),
                ("tags", list),
            ]

            for key, expected_type in type_checks:
                if key in config:
                    if isinstance(config[key], expected_type):
                        results.append(TestResult(
                            name=f"factory_type_{key}",
                            status=TestStatus.PASSED,
                            message=f"{key} is {expected_type.__name__}"
                        ))
                    else:
                        results.append(TestResult(
                            name=f"factory_type_{key}",
                            status=TestStatus.FAILED,
                            message=f"{key} should be {expected_type.__name__}, got {type(config[key]).__name__}"
                        ))

            # Check assistant_class is a class
            if "assistant_class" in config:
                if isinstance(config["assistant_class"], type):
                    results.append(TestResult(
                        name="factory_assistant_class",
                        status=TestStatus.PASSED,
                        message=f"assistant_class is {config['assistant_class'].__name__}"
                    ))
                else:
                    results.append(TestResult(
                        name="factory_assistant_class",
                        status=TestStatus.FAILED,
                        message="assistant_class should be a class"
                    ))

            # Check system_prompt is substantial
            if "system_prompt" in config:
                prompt_len = len(config["system_prompt"])
                if prompt_len >= 100:
                    results.append(TestResult(
                        name="factory_system_prompt_length",
                        status=TestStatus.PASSED,
                        message=f"System prompt is {prompt_len} characters"
                    ))
                else:
                    results.append(TestResult(
                        name="factory_system_prompt_length",
                        status=TestStatus.FAILED,
                        message=f"System prompt too short ({prompt_len} chars, expected >= 100)"
                    ))

            # Check tags are non-empty strings
            if "tags" in config and isinstance(config["tags"], list):
                if all(isinstance(t, str) and len(t) > 0 for t in config["tags"]):
                    results.append(TestResult(
                        name="factory_tags_valid",
                        status=TestStatus.PASSED,
                        message=f"All {len(config['tags'])} tags are valid strings"
                    ))
                else:
                    results.append(TestResult(
                        name="factory_tags_valid",
                        status=TestStatus.FAILED,
                        message="Tags should be non-empty strings"
                    ))

        except Exception as e:
            results.append(TestResult(
                name="factory_function_callable",
                status=TestStatus.ERROR,
                message=f"Factory function raised exception: {e}",
                details={"traceback": traceback.format_exc()}
            ))

        return results

    def test_class_instantiation(self, module, module_name: str) -> List[TestResult]:
        """Test that the assistant class can be instantiated"""
        results = []

        # Find the assistant class - allow flexible naming (Assistant, Optimizer, Analyzer, etc.)
        assistant_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.startswith("Enhanced"):
                # Accept Enhanced* classes that have name and version attributes
                try:
                    instance = obj()
                    if hasattr(instance, "name") and hasattr(instance, "version"):
                        assistant_class = obj
                        break
                except:
                    continue

        if not assistant_class:
            results.append(TestResult(
                name="class_exists",
                status=TestStatus.FAILED,
                message="No Enhanced*Assistant class found"
            ))
            return results

        results.append(TestResult(
            name="class_exists",
            status=TestStatus.PASSED,
            message=f"Found {assistant_class.__name__}"
        ))

        # Try to instantiate
        try:
            instance = assistant_class()
            results.append(TestResult(
                name="class_instantiates",
                status=TestStatus.PASSED,
                message="Class instantiated successfully"
            ))

            # Check for expected attributes
            expected_attrs = ["name", "version"]
            for attr in expected_attrs:
                if hasattr(instance, attr):
                    value = getattr(instance, attr)
                    results.append(TestResult(
                        name=f"class_attr_{attr}",
                        status=TestStatus.PASSED,
                        message=f"{attr} = {value}"
                    ))
                else:
                    results.append(TestResult(
                        name=f"class_attr_{attr}",
                        status=TestStatus.FAILED,
                        message=f"Missing attribute: {attr}"
                    ))

        except Exception as e:
            results.append(TestResult(
                name="class_instantiates",
                status=TestStatus.ERROR,
                message=f"Failed to instantiate: {e}",
                details={"traceback": traceback.format_exc()}
            ))

        return results

    def test_static_methods(self, module, module_name: str) -> List[TestResult]:
        """Test all static methods return valid data"""
        results = []

        # Find the assistant class - flexible naming
        assistant_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.startswith("Enhanced"):
                try:
                    instance = obj()
                    if hasattr(instance, "name") and hasattr(instance, "version"):
                        assistant_class = obj
                        break
                except:
                    continue

        if not assistant_class:
            return results

        # Find static methods
        static_methods = []
        for name in dir(assistant_class):
            if name.startswith("_"):
                continue
            attr = getattr(assistant_class, name)
            if callable(attr) and isinstance(getattr(type(assistant_class), name, None), staticmethod):
                static_methods.append(name)

        if not static_methods:
            results.append(TestResult(
                name="static_methods_exist",
                status=TestStatus.SKIPPED,
                message="No static methods found"
            ))
            return results

        results.append(TestResult(
            name="static_methods_exist",
            status=TestStatus.PASSED,
            message=f"Found {len(static_methods)} static methods: {', '.join(static_methods[:5])}{'...' if len(static_methods) > 5 else ''}"
        ))

        # Test each static method
        for method_name in static_methods:
            try:
                method = getattr(assistant_class, method_name)
                result = method()

                if result is None:
                    results.append(TestResult(
                        name=f"static_{method_name}_returns_value",
                        status=TestStatus.FAILED,
                        message="Method returned None"
                    ))
                elif isinstance(result, dict):
                    results.append(TestResult(
                        name=f"static_{method_name}_returns_value",
                        status=TestStatus.PASSED,
                        message=f"Returns dict with {len(result)} keys",
                        details={"keys": list(result.keys())[:10]}
                    ))
                elif isinstance(result, list):
                    results.append(TestResult(
                        name=f"static_{method_name}_returns_value",
                        status=TestStatus.PASSED,
                        message=f"Returns list with {len(result)} items"
                    ))
                else:
                    results.append(TestResult(
                        name=f"static_{method_name}_returns_value",
                        status=TestStatus.PASSED,
                        message=f"Returns {type(result).__name__}"
                    ))

            except TypeError as e:
                # Method requires arguments - skip
                results.append(TestResult(
                    name=f"static_{method_name}_returns_value",
                    status=TestStatus.SKIPPED,
                    message=f"Method requires arguments: {e}"
                ))
            except Exception as e:
                results.append(TestResult(
                    name=f"static_{method_name}_returns_value",
                    status=TestStatus.ERROR,
                    message=f"Method raised exception: {e}"
                ))

        return results

    def test_code_examples(self, module, module_name: str) -> List[TestResult]:
        """Test that embedded code examples have valid Python syntax"""
        results = []

        # Find the assistant class - flexible naming
        assistant_class = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name.startswith("Enhanced"):
                try:
                    instance = obj()
                    if hasattr(instance, "name") and hasattr(instance, "version"):
                        assistant_class = obj
                        break
                except:
                    continue

        if not assistant_class:
            return results

        # Collect all code examples from static methods
        all_examples = []

        for name in dir(assistant_class):
            if name.startswith("_"):
                continue
            attr = getattr(assistant_class, name)
            if callable(attr) and isinstance(getattr(type(assistant_class), name, None), staticmethod):
                try:
                    result = attr()
                    if result:
                        examples = self._extract_code_examples(result, name)
                        all_examples.extend(examples)
                except:
                    pass

        if not all_examples:
            results.append(TestResult(
                name="code_examples_found",
                status=TestStatus.SKIPPED,
                message="No code examples detected"
            ))
            return results

        results.append(TestResult(
            name="code_examples_found",
            status=TestStatus.PASSED,
            message=f"Found {len(all_examples)} code examples"
        ))

        # Validate Python syntax (sample to avoid too many tests)
        python_examples = [
            (path, code) for path, code in all_examples
            if not any(kw in code.lower() for kw in ["javascript", "typescript", "java ", "jsx", "tsx", "go ", "rust"])
        ]

        valid_count = 0
        invalid_count = 0

        for path, code in python_examples[:20]:  # Limit to first 20
            # Clean up code for parsing
            clean_code = code.strip()

            # Skip non-Python code markers
            if any(marker in clean_code[:50] for marker in ["// ", "/* ", "<!-- ", "```"]):
                continue

            is_valid, error = self._validate_python_syntax(clean_code)
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                results.append(TestResult(
                    name=f"code_syntax_{path[:30]}",
                    status=TestStatus.FAILED,
                    message=f"Invalid Python syntax: {error}",
                    details={"path": path, "code_preview": clean_code[:200]}
                ))

        if valid_count > 0:
            results.append(TestResult(
                name="code_examples_valid_syntax",
                status=TestStatus.PASSED if invalid_count == 0 else TestStatus.FAILED,
                message=f"{valid_count} valid, {invalid_count} invalid Python examples"
            ))

        return results

    def test_assistant(self, module_name: str) -> AssistantTestSuite:
        """Run all tests for a single assistant"""
        import time
        start_time = time.time()

        suite = AssistantTestSuite(
            assistant_name=module_name.replace("assistants_enhanced_", "").replace("_", " ").title(),
            module_name=module_name
        )

        try:
            module = self._import_module(module_name)

            # Run test categories
            suite.results.extend(self.test_factory_function(module, module_name))
            suite.results.extend(self.test_class_instantiation(module, module_name))
            suite.results.extend(self.test_static_methods(module, module_name))
            suite.results.extend(self.test_code_examples(module, module_name))

        except ImportError as e:
            suite.results.append(TestResult(
                name="module_import",
                status=TestStatus.ERROR,
                message=str(e)
            ))
        except Exception as e:
            suite.results.append(TestResult(
                name="test_execution",
                status=TestStatus.ERROR,
                message=f"Unexpected error: {e}",
                details={"traceback": traceback.format_exc()}
            ))

        # Calculate totals
        suite.total_tests = len(suite.results)
        suite.passed = sum(1 for r in suite.results if r.status == TestStatus.PASSED)
        suite.failed = sum(1 for r in suite.results if r.status == TestStatus.FAILED)
        suite.errors = sum(1 for r in suite.results if r.status == TestStatus.ERROR)
        suite.skipped = sum(1 for r in suite.results if r.status == TestStatus.SKIPPED)
        suite.duration_ms = (time.time() - start_time) * 1000

        return suite

    def run_all_tests(self) -> FullTestReport:
        """Run tests for all discovered assistants"""
        import time
        start_time = time.time()

        report = FullTestReport(
            timestamp=datetime.now().isoformat()
        )

        for module_name in self.assistant_modules:
            print(f"Testing {module_name}...")
            suite = self.test_assistant(module_name)
            report.assistant_results.append(suite)

            # Update totals
            report.total_tests += suite.total_tests
            report.total_passed += suite.passed
            report.total_failed += suite.failed
            report.total_errors += suite.errors

        report.total_assistants = len(self.assistant_modules)
        report.duration_ms = (time.time() - start_time) * 1000

        return report


def generate_html_report(report: FullTestReport) -> str:
    """Generate an HTML report from test results"""

    def status_color(status: TestStatus) -> str:
        return {
            TestStatus.PASSED: "#22c55e",
            TestStatus.FAILED: "#ef4444",
            TestStatus.ERROR: "#f97316",
            TestStatus.SKIPPED: "#6b7280",
        }.get(status, "#6b7280")

    def status_icon(status: TestStatus) -> str:
        return {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.ERROR: "⚠",
            TestStatus.SKIPPED: "○",
        }.get(status, "?")

    assistant_rows = []
    for suite in report.assistant_results:
        status_class = "passing" if suite.failed == 0 and suite.errors == 0 else "failing"
        assistant_rows.append(f"""
        <tr class="assistant-row {status_class}" onclick="toggleDetails('{suite.module_name}')">
            <td class="assistant-name">{suite.assistant_name}</td>
            <td class="stat passed">{suite.passed}</td>
            <td class="stat failed">{suite.failed}</td>
            <td class="stat errors">{suite.errors}</td>
            <td class="stat skipped">{suite.skipped}</td>
            <td class="stat rate">{suite.success_rate:.1f}%</td>
            <td class="stat time">{suite.duration_ms:.0f}ms</td>
        </tr>
        <tr class="details-row" id="details-{suite.module_name}">
            <td colspan="7">
                <div class="test-details">
                    {''.join(f'''
                    <div class="test-result" style="border-left-color: {status_color(r.status)}">
                        <span class="test-icon" style="color: {status_color(r.status)}">{status_icon(r.status)}</span>
                        <span class="test-name">{r.name}</span>
                        <span class="test-message">{r.message}</span>
                    </div>
                    ''' for r in suite.results)}
                </div>
            </td>
        </tr>
        """)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Genesis Enhanced Assistants - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 2rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .timestamp {{
            color: #64748b;
            font-size: 0.875rem;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .summary-card {{
            background: #1e293b;
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
        }}

        .summary-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        .summary-label {{
            color: #94a3b8;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .summary-card.passed .summary-value {{ color: #22c55e; }}
        .summary-card.failed .summary-value {{ color: #ef4444; }}
        .summary-card.total .summary-value {{ color: #60a5fa; }}
        .summary-card.rate .summary-value {{ color: #a78bfa; }}

        .progress-bar {{
            background: #334155;
            border-radius: 9999px;
            height: 8px;
            margin: 1rem 0 2rem;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #22c55e, #a78bfa);
            border-radius: 9999px;
            transition: width 0.5s ease;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 0.75rem;
            overflow: hidden;
        }}

        th {{
            background: #334155;
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.05em;
        }}

        .assistant-row {{
            cursor: pointer;
            transition: background 0.2s;
        }}

        .assistant-row:hover {{
            background: #334155;
        }}

        .assistant-row td {{
            padding: 1rem;
            border-top: 1px solid #334155;
        }}

        .assistant-name {{
            font-weight: 600;
        }}

        .stat {{
            text-align: center;
            font-family: 'SF Mono', Monaco, monospace;
        }}

        .stat.passed {{ color: #22c55e; }}
        .stat.failed {{ color: #ef4444; }}
        .stat.errors {{ color: #f97316; }}
        .stat.skipped {{ color: #6b7280; }}
        .stat.rate {{ color: #a78bfa; }}
        .stat.time {{ color: #64748b; }}

        .details-row {{
            display: none;
        }}

        .details-row.visible {{
            display: table-row;
        }}

        .test-details {{
            padding: 1rem;
            background: #0f172a;
            border-radius: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
        }}

        .test-result {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.5rem;
            border-left: 3px solid;
            margin-bottom: 0.5rem;
            background: #1e293b;
            border-radius: 0 0.25rem 0.25rem 0;
        }}

        .test-icon {{
            font-weight: 700;
            width: 1.5rem;
            text-align: center;
        }}

        .test-name {{
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.875rem;
            color: #e2e8f0;
            min-width: 200px;
        }}

        .test-message {{
            color: #94a3b8;
            font-size: 0.875rem;
            flex: 1;
        }}

        .passing .assistant-name::before {{
            content: "✓ ";
            color: #22c55e;
        }}

        .failing .assistant-name::before {{
            content: "✗ ";
            color: #ef4444;
        }}

        footer {{
            text-align: center;
            margin-top: 2rem;
            color: #64748b;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Genesis Enhanced Assistants</h1>
            <p class="timestamp">Test Report - {report.timestamp}</p>
        </header>

        <div class="summary">
            <div class="summary-card total">
                <div class="summary-value">{report.total_assistants}</div>
                <div class="summary-label">Assistants</div>
            </div>
            <div class="summary-card total">
                <div class="summary-value">{report.total_tests}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-card passed">
                <div class="summary-value">{report.total_passed}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card failed">
                <div class="summary-value">{report.total_failed}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-card rate">
                <div class="summary-value">{report.overall_success_rate:.1f}%</div>
                <div class="summary-label">Success Rate</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {report.overall_success_rate}%"></div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Assistant</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Errors</th>
                    <th>Skipped</th>
                    <th>Rate</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                {''.join(assistant_rows)}
            </tbody>
        </table>

        <footer>
            <p>Genesis Engine - Enhanced Assistants Test Suite</p>
            <p>Total Duration: {report.duration_ms:.0f}ms</p>
        </footer>
    </div>

    <script>
        function toggleDetails(moduleId) {{
            const row = document.getElementById('details-' + moduleId);
            row.classList.toggle('visible');
        }}
    </script>
</body>
</html>
"""
    return html


def generate_json_report(report: FullTestReport) -> str:
    """Generate JSON report"""
    def to_dict(obj):
        if hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if isinstance(value, list):
                    result[key] = [to_dict(item) for item in value]
                elif isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
            return result
        elif isinstance(value, Enum):
            return obj.value
        return obj

    return json.dumps(to_dict(report), indent=2)


def run_tests():
    """Main entry point for running tests"""
    print("=" * 60)
    print("Genesis Enhanced Assistants - Test Suite")
    print("=" * 60)
    print()

    tester = AssistantTester()

    print(f"Discovered {len(tester.assistant_modules)} assistant modules:")
    for module in tester.assistant_modules:
        print(f"  - {module}")
    print()

    report = tester.run_all_tests()

    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Assistants: {report.total_assistants}")
    print(f"Total Tests:      {report.total_tests}")
    print(f"Passed:           {report.total_passed}")
    print(f"Failed:           {report.total_failed}")
    print(f"Errors:           {report.total_errors}")
    print(f"Success Rate:     {report.overall_success_rate:.1f}%")
    print(f"Duration:         {report.duration_ms:.0f}ms")
    print()

    # Generate reports
    output_dir = Path(__file__).parent.parent.parent / "test_results"
    output_dir.mkdir(exist_ok=True)

    # HTML Report
    html_path = output_dir / "assistant_test_report.html"
    with open(html_path, "w") as f:
        f.write(generate_html_report(report))
    print(f"HTML Report: {html_path}")

    # JSON Report
    json_path = output_dir / "assistant_test_report.json"
    with open(json_path, "w") as f:
        f.write(generate_json_report(report))
    print(f"JSON Report: {json_path}")

    print()

    # Per-assistant summary
    print("Per-Assistant Results:")
    print("-" * 60)
    for suite in report.assistant_results:
        status = "✓" if suite.failed == 0 and suite.errors == 0 else "✗"
        print(f"  {status} {suite.assistant_name}: {suite.passed}/{suite.total_tests} passed ({suite.success_rate:.0f}%)")

    return report


if __name__ == "__main__":
    run_tests()
