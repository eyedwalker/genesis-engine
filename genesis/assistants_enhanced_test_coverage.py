"""
Enhanced Test Coverage Analyzer Assistant

Comprehensive test coverage analysis covering:
- Coverage metrics (line, branch, function, path, mutation)
- Missing test identification
- Edge case detection (null, empty, boundaries, race conditions)
- Mutation testing (detecting weak tests)
- Property-based testing patterns (Hypothesis, QuickCheck)
- Flaky test detection
- Coverage gap analysis and critical path identification

References:
- Pytest: https://docs.pytest.org/
- Coverage.py: https://coverage.readthedocs.io/
- Hypothesis: https://hypothesis.readthedocs.io/
- MutPy: https://github.com/mutpy/mutpy
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class TestCoverageFinding(BaseModel):
    """Structured test coverage finding output"""

    finding_id: str = Field(..., description="Unique identifier (TEST-001, TEST-002, etc.)")
    title: str = Field(..., description="Brief title of the coverage gap")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Missing/EdgeCase/Mutation/Flaky/Integration")

    location: Dict[str, Any] = Field(default_factory=dict, description="File, line, function")
    description: str = Field(..., description="Detailed description of the gap")

    coverage_metrics: Dict[str, Any] = Field(default_factory=dict, description="Coverage percentages")
    missing_tests: List[str] = Field(default_factory=list, description="What tests are missing")
    uncovered_paths: List[str] = Field(default_factory=list, description="Uncovered execution paths")

    suggested_tests: str = Field(default="", description="Recommended test cases")
    test_template: str = Field(default="", description="Code template for tests")

    testing_strategy: str = Field(default="", description="How to test this scenario")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Testing tools")
    references: List[str] = Field(default_factory=list, description="Testing documentation")

    remediation: Dict[str, str] = Field(default_factory=dict, description="Effort and priority")


class EnhancedTestCoverageAnalyzer:
    """
    Enhanced Test Coverage Analyzer with comprehensive coverage analysis

    Analyzes:
    - Line/branch/function/path coverage
    - Mutation testing (test quality)
    - Edge cases and boundary conditions
    - Flaky tests
    - Integration vs unit test balance
    """

    def __init__(self):
        self.name = "Enhanced Test Coverage Analyzer"
        self.version = "2.0.0"
        self.standards = ["Pytest", "Coverage.py", "Hypothesis", "Mutation Testing"]

    # =========================================================================
    # COVERAGE METRICS
    # =========================================================================

    @staticmethod
    def coverage_metrics_guide() -> Dict[str, Any]:
        """
        Guide to coverage metrics and targets
        """
        return {
            "metrics": {
                "line_coverage": {
                    "description": "Percentage of executed lines",
                    "target": "80%+ (minimum), 90%+ (good), 95%+ (excellent)",
                    "command": "pytest --cov=app --cov-report=html",
                    "example": """
# coverage.py example
coverage run -m pytest
coverage report
coverage html  # Generates htmlcov/index.html

# Output:
Name                Stmts   Miss  Cover
---------------------------------------
app/models.py         150     15    90%
app/services.py       200     40    80%
app/utils.py          100      5    95%
---------------------------------------
TOTAL                 450     60    87%
                    """,
                },
                "branch_coverage": {
                    "description": "Percentage of executed branches (if/else, loops)",
                    "target": "75%+ (minimum), 85%+ (good)",
                    "command": "pytest --cov=app --cov-branch --cov-report=html",
                    "example": """
# Branch coverage example
def process_payment(amount, user):
    if amount <= 0:  # Branch 1: True/False
        raise ValueError("Invalid amount")

    if user.balance >= amount:  # Branch 2: True/False
        user.balance -= amount
        return True
    else:
        return False

# Need tests for all branches:
# 1. amount <= 0 (True)
# 2. amount > 0 (False)
# 3. balance >= amount (True)
# 4. balance < amount (False)
                    """,
                },
                "function_coverage": {
                    "description": "Percentage of functions called at least once",
                    "target": "90%+ (most functions should be tested)",
                    "example": """
# Function coverage report
def public_function():  # COVERED (90% of uses)
    pass

def _private_helper():  # COVERED (called by public_function)
    pass

def deprecated_function():  # NOT COVERED (never called)
    pass  # Should be removed or documented why untested
                    """,
                },
                "path_coverage": {
                    "description": "Percentage of unique execution paths through code",
                    "target": "Critical paths: 100%, Others: 70%+",
                    "explanation": """
# Path coverage example
def calculate_discount(price, customer_type, is_member):
    discount = 0

    if customer_type == 'premium':  # Path A
        discount = 0.20
    elif customer_type == 'regular':  # Path B
        discount = 0.10

    if is_member:  # Path C
        discount += 0.05

    return price * (1 - discount)

# Unique paths:
# 1. premium + member: A + C
# 2. premium + not member: A
# 3. regular + member: B + C
# 4. regular + not member: B
# 5. other type + member: C
# 6. other type + not member: (no discount)

# Need 6 tests to cover all paths!
                    """,
                },
                "mutation_coverage": {
                    "description": "Percentage of mutants killed by tests (test quality)",
                    "target": "80%+ mutation score indicates strong tests",
                    "explanation": """
# Mutation testing: Change code slightly, do tests still fail?

# Original code
def is_adult(age):
    return age >= 18

# Mutant 1: Change >= to >
def is_adult(age):
    return age > 18  # Test with age=18 should fail!

# Mutant 2: Change 18 to 17
def is_adult(age):
    return age >= 17  # Test should fail!

# Strong tests kill mutants (tests fail when code mutates)
                    """,
                    "tools": [
                        {
                            "name": "mutmut (Python)",
                            "install": "pip install mutmut",
                            "command": "mutmut run --paths-to-mutate=app/",
                            "report": "mutmut html",
                        },
                        {
                            "name": "MutPy (Python)",
                            "install": "pip install mutpy",
                            "command": "mut.py --target app.module --unit-test tests.test_module",
                        },
                        {
                            "name": "Stryker (JavaScript)",
                            "install": "npm install --save-dev @stryker-mutator/core",
                            "command": "npx stryker run",
                        },
                    ],
                },
            },
            "setup": {
                "pytest_coverage": """
# Install coverage tools
pip install pytest pytest-cov coverage

# pytest.ini configuration
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-branch
    --cov-fail-under=80

# Run tests with coverage
pytest

# View HTML report
open htmlcov/index.html
                """,
                "coverage_config": """
# .coveragerc configuration
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */venv/*
    */__init__.py

[report]
precision = 2
show_missing = True
skip_covered = False

exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstract
                """,
            },
        }

    # =========================================================================
    # MISSING TEST IDENTIFICATION
    # =========================================================================

    @staticmethod
    def identify_missing_tests() -> Dict[str, Any]:
        """
        Identify what tests are missing
        """
        return {
            "untested_functions": {
                "example": """
# Code with coverage gaps
class OrderService:
    def create_order(self, items):  # 85% covered
        total = self.calculate_total(items)
        self.validate_inventory(items)
        return self.save_order(items, total)

    def calculate_total(self, items):  # 100% covered ✅
        return sum(item.price * item.qty for item in items)

    def validate_inventory(self, items):  # 60% covered ⚠️
        for item in items:
            if item.qty > self.get_stock(item.id):
                raise InsufficientStockError()
        # Edge case: what if get_stock() raises exception? NOT TESTED!

    def cancel_order(self, order_id):  # 0% covered ❌
        # NO TESTS AT ALL!
        order = self.get_order(order_id)
        self.refund_payment(order)
        self.restore_inventory(order)

    def _internal_helper(self):  # 0% covered (OK if truly internal)
        pass

# Missing tests:
# 1. cancel_order - NO TESTS
# 2. validate_inventory - edge cases missing
# 3. Error handling paths
                """,
                "suggested_tests": """
# Tests to add

def test_cancel_order_success():
    # Happy path test
    service = OrderService()
    order = service.create_order([item1, item2])
    service.cancel_order(order.id)

    assert order.status == 'cancelled'
    assert order.refund_issued == True

def test_cancel_order_already_cancelled():
    # Edge case: double cancellation
    service = OrderService()
    order = service.create_order([item1])
    service.cancel_order(order.id)

    with pytest.raises(OrderAlreadyCancelledError):
        service.cancel_order(order.id)

def test_validate_inventory_service_error():
    # Edge case: inventory service throws error
    service = OrderService()
    mock_get_stock = Mock(side_effect=InventoryServiceError())
    service.get_stock = mock_get_stock

    with pytest.raises(InventoryServiceError):
        service.validate_inventory([item1])
                """,
            },
            "uncovered_branches": {
                "example": """
def process_refund(order, reason):
    if order.status != 'completed':
        raise InvalidOrderError()  # ✅ Tested

    if reason == 'damaged':
        refund_amount = order.total  # ✅ Tested
    elif reason == 'unsatisfied':
        refund_amount = order.total * 0.5  # ✅ Tested
    else:
        refund_amount = 0  # ❌ NOT TESTED!

    if order.payment_method == 'credit_card':
        process_card_refund(refund_amount)  # ✅ Tested
    else:
        process_bank_refund(refund_amount)  # ❌ NOT TESTED!

    return refund_amount

# Missing tests:
# 1. reason = 'other' → refund_amount = 0
# 2. payment_method != 'credit_card' → process_bank_refund
                """,
            },
        }

    # =========================================================================
    # EDGE CASE DETECTION
    # =========================================================================

    @staticmethod
    def edge_case_patterns() -> Dict[str, Any]:
        """
        Common edge cases that are often missed
        """
        return {
            "null_and_empty": {
                "description": "Null, None, empty string, empty list/dict",
                "examples": """
# Function to test
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

# Edge cases to test:
def test_calculate_average_empty_list():
    with pytest.raises(ZeroDivisionError):
        calculate_average([])  # len() = 0!

def test_calculate_average_none():
    with pytest.raises(TypeError):
        calculate_average(None)  # None is not iterable

def test_calculate_average_single_item():
    assert calculate_average([5]) == 5  # Boundary case

def test_calculate_average_negative_numbers():
    assert calculate_average([-5, -10]) == -7.5  # Negatives
                """,
            },
            "boundary_values": {
                "description": "Min, max, zero, one, at limits",
                "examples": """
# Boundary value testing
def discount_for_quantity(qty):
    if qty < 10:
        return 0
    elif qty < 50:
        return 0.10
    elif qty < 100:
        return 0.20
    else:
        return 0.30

# Boundary tests (test values around boundaries):
def test_discount_boundaries():
    assert discount_for_quantity(0) == 0     # Minimum
    assert discount_for_quantity(9) == 0     # Just below 10
    assert discount_for_quantity(10) == 0.10 # Exactly 10
    assert discount_for_quantity(11) == 0.10 # Just above 10

    assert discount_for_quantity(49) == 0.10 # Just below 50
    assert discount_for_quantity(50) == 0.20 # Exactly 50
    assert discount_for_quantity(51) == 0.20 # Just above 50

    assert discount_for_quantity(99) == 0.20  # Just below 100
    assert discount_for_quantity(100) == 0.30 # Exactly 100
    assert discount_for_quantity(1000) == 0.30 # Large value

def test_discount_invalid():
    with pytest.raises(ValueError):
        discount_for_quantity(-1)  # Negative!
                """,
            },
            "race_conditions": {
                "description": "Concurrent access, async timing issues",
                "examples": """
# Race condition in concurrent code
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        current = self.count  # Read
        # Race: Another thread could increment here!
        self.count = current + 1  # Write

# Test for race condition
import threading

def test_counter_race_condition():
    counter = Counter()

    def increment_many():
        for _ in range(1000):
            counter.increment()

    # Run 10 threads concurrently
    threads = [threading.Thread(target=increment_many) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should be 10,000, but will be less due to race condition!
    assert counter.count < 10000  # Demonstrates the bug

# Fixed version with lock
class SafeCounter:
    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.count += 1

def test_safe_counter():
    counter = SafeCounter()
    # Same test, now passes
    assert counter.count == 10000  # ✅
                """,
            },
            "unicode_and_special_chars": {
                "description": "Unicode, emojis, SQL injection chars, XSS",
                "examples": """
def test_username_special_characters():
    # Unicode characters
    assert is_valid_username("用户名") == True

    # Emojis
    assert is_valid_username("user😀") == True

    # SQL injection attempts
    assert is_valid_username("admin'--") == False
    assert is_valid_username("'; DROP TABLE users--") == False

    # XSS attempts
    assert is_valid_username("<script>alert('xss')</script>") == False

    # Very long input
    assert is_valid_username("a" * 10000) == False

    # Null bytes
    assert is_valid_username("user\\x00admin") == False
                """,
            },
            "time_and_dates": {
                "description": "Timezones, DST, leap years, date boundaries",
                "examples": """
from datetime import datetime, timezone
import pytest

def test_date_edge_cases():
    # Leap year
    assert is_leap_year(2024) == True
    assert is_leap_year(2023) == False
    assert is_leap_year(2000) == True   # Divisible by 400
    assert is_leap_year(1900) == False  # Divisible by 100 but not 400

def test_timezone_handling():
    # Different timezones
    utc_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    pst_time = convert_timezone(utc_time, 'America/Los_Angeles')

    assert pst_time.hour == 4  # PST is UTC-8

def test_dst_transition():
    # Daylight Saving Time transition
    # March 10, 2024 2:00 AM → 3:00 AM (spring forward)
    before_dst = datetime(2024, 3, 10, 1, 59)
    after_dst = datetime(2024, 3, 10, 3, 0)

    assert (after_dst - before_dst).seconds == 1 * 60  # Only 1 minute!
                """,
            },
        }

    # =========================================================================
    # PROPERTY-BASED TESTING
    # =========================================================================

    @staticmethod
    def property_based_testing() -> Dict[str, Any]:
        """
        Property-based testing with Hypothesis
        """
        return {
            "concept": """
Property-based testing: Instead of specific test cases, define properties that should
always be true, then generate hundreds of random inputs to test.

Benefits:
- Finds edge cases you didn't think of
- Tests with diverse inputs automatically
- Shrinks failing cases to minimal examples
            """,
            "hypothesis_basics": """
# Install Hypothesis
pip install hypothesis

# Basic property-based test
from hypothesis import given, strategies as st

# Traditional test: specific cases
def test_reverse_traditional():
    assert reverse("hello") == "olleh"
    assert reverse("") == ""
    assert reverse("a") == "a"

# Property-based test: test property for ANY string
@given(st.text())
def test_reverse_property(s):
    # Property: Reversing twice returns original
    assert reverse(reverse(s)) == s

# Hypothesis generates 100+ random strings:
# "", "abc", "🎉", "\\x00\\x01", very long strings, unicode, etc.
            """,
            "common_properties": {
                "idempotence": """
# Property: Applying operation multiple times = applying once
@given(st.lists(st.integers()))
def test_sort_idempotent(lst):
    sorted_once = sorted(lst)
    sorted_twice = sorted(sorted(lst))
    assert sorted_once == sorted_twice
                """,
                "inverse_operations": """
# Property: Inverse operations cancel out
@given(st.text())
def test_encode_decode(text):
    assert decode(encode(text)) == text

@given(st.integers(), st.integers())
def test_addition_subtraction(a, b):
    assert (a + b) - b == a
                """,
                "commutativity": """
# Property: Order doesn't matter
@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a

@given(st.sets(st.integers()), st.sets(st.integers()))
def test_set_union_commutative(a, b):
    assert a.union(b) == b.union(a)
                """,
                "invariants": """
# Property: Certain properties always hold
@given(st.lists(st.integers()))
def test_sort_length_preserved(lst):
    assert len(sorted(lst)) == len(lst)

@given(st.lists(st.integers(), min_size=1))
def test_sort_min_max(lst):
    sorted_lst = sorted(lst)
    assert sorted_lst[0] == min(lst)
    assert sorted_lst[-1] == max(lst)
                """,
            },
            "strategies": """
# Hypothesis strategies for generating test data

from hypothesis import strategies as st

# Primitive types
st.integers()                    # Any integer
st.integers(min_value=0, max_value=100)  # Range
st.floats(allow_nan=False)       # Floats without NaN
st.text()                        # Any string (including unicode)
st.text(min_size=1, max_size=10) # Length constraints
st.booleans()                    # True/False

# Collections
st.lists(st.integers())          # List of integers
st.lists(st.text(), min_size=1, max_size=5)
st.dictionaries(keys=st.text(), values=st.integers())
st.tuples(st.text(), st.integers())  # Fixed-size tuple

# Complex strategies
st.emails()                      # Valid email addresses
st.uuids()                       # UUIDs
st.datetimes()                   # Datetime objects

# Custom strategies
@st.composite
def user_strategy(draw):
    return User(
        name=draw(st.text(min_size=1, max_size=50)),
        age=draw(st.integers(min_value=0, max_value=120)),
        email=draw(st.emails())
    )

@given(user_strategy())
def test_user_validation(user):
    assert user.age >= 0
    assert '@' in user.email
            """,
            "example": """
# Real-world example: Testing JSON serialization

import json
from hypothesis import given, strategies as st

# Property: Any JSON-serializable object should round-trip
@given(st.recursive(
    st.one_of(
        st.none(),
        st.booleans(),
        st.floats(allow_nan=False),
        st.text(),
    ),
    lambda children: st.lists(children) | st.dictionaries(st.text(), children)
))
def test_json_roundtrip(obj):
    serialized = json.dumps(obj)
    deserialized = json.loads(serialized)
    assert deserialized == obj

# Hypothesis will generate:
# - Nested lists and dicts
# - Unicode strings
# - Edge case numbers
# - Empty collections
# - Very deep nesting
# All automatically!
            """,
        }

    # =========================================================================
    # FLAKY TEST DETECTION
    # =========================================================================

    @staticmethod
    def flaky_test_detection() -> Dict[str, Any]:
        """
        Detect and fix flaky tests
        """
        return {
            "causes": [
                "Timing issues (async, sleep, timeouts)",
                "Random data generation",
                "Shared state between tests",
                "External dependencies (network, database)",
                "Test execution order dependence",
                "Date/time dependence",
            ],
            "detection": """
# Run tests multiple times to detect flakiness
pytest -x --count=100  # pytest-repeat plugin

# Or use pytest-flakefinder
pip install pytest-flakefinder
pytest --flake-finder --flake-runs=50

# GitHub Actions: Run tests in parallel multiple times
- name: Test for flakiness
  run: |
    for i in {1..10}; do
      pytest tests/ || exit 1
    done
            """,
            "common_fixes": {
                "timing_issues": """
# BAD: Flaky due to timing
import time

def test_async_operation():
    start_background_job()
    time.sleep(1)  # Might not be enough time!
    assert job_completed()  # ❌ Flaky

# GOOD: Wait with timeout
import time

def test_async_operation_fixed():
    start_background_job()

    # Poll with timeout
    timeout = 10
    start_time = time.time()
    while time.time() - start_time < timeout:
        if job_completed():
            return  # ✅ Success
        time.sleep(0.1)

    assert False, "Job did not complete in time"

# BETTER: Use proper async testing
import pytest

@pytest.mark.asyncio
async def test_async_operation_proper():
    job = start_background_job()
    await job.wait(timeout=10)
    assert job.completed
                """,
                "shared_state": """
# BAD: Tests share state
class TestUserService:
    user_service = UserService()  # Shared! ❌

    def test_create_user(self):
        user = self.user_service.create("alice")
        assert user.name == "alice"

    def test_user_count(self):
        # Fails if test_create_user runs first!
        assert self.user_service.count() == 0  # ❌ Flaky

# GOOD: Fresh state per test
class TestUserService:
    def setup_method(self):
        self.user_service = UserService()  # Fresh per test ✅

    def test_create_user(self):
        user = self.user_service.create("alice")
        assert user.name == "alice"

    def test_user_count(self):
        assert self.user_service.count() == 0  # ✅ Always passes
                """,
                "random_data": """
# BAD: Random data causes flakiness
import random

def test_sorting():
    data = [random.randint(0, 100) for _ in range(10)]
    sorted_data = custom_sort(data)
    assert sorted_data == sorted(data)  # ❌ Might fail occasionally

# GOOD: Use seeded random or Hypothesis
import random

def test_sorting_seeded():
    random.seed(42)  # Reproducible
    data = [random.randint(0, 100) for _ in range(10)]
    sorted_data = custom_sort(data)
    assert sorted_data == sorted(data)  # ✅ Deterministic

# BETTER: Property-based testing
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorting_property(data):
    sorted_data = custom_sort(data)
    assert sorted_data == sorted(data)  # ✅ Tests many cases
                """,
            },
        }

    # =========================================================================
    # TEST STRATEGY
    # =========================================================================

    @staticmethod
    def test_strategy_guide() -> Dict[str, Any]:
        """
        Guide for test strategy and test pyramid
        """
        return {
            "test_pyramid": """
Test Pyramid (by quantity):

        /\\
       /  \\     E2E Tests (UI/Integration)
      /    \\    - 10% of tests
     /------\\   - Slow, brittle, expensive
    /        \\
   / Integration - 20% of tests
  /  Tests     \\ - Medium speed
 /--------------\\
/                \\
/  Unit Tests     \\ - 70% of tests
/                  \\ - Fast, focused, many
--------------------

Unit Tests:
- Test single function/class
- Fast (<1ms each)
- No external dependencies
- Most tests should be here

Integration Tests:
- Test multiple components together
- Medium speed (10-100ms)
- May use test database
- Focus on interactions

E2E Tests:
- Test entire user flow
- Slow (seconds)
- Brittle (break often)
- Only critical flows
            """,
            "what_to_test": {
                "priority_1_critical": [
                    "Payment processing",
                    "Authentication/authorization",
                    "Data validation",
                    "Business logic",
                    "Security-critical code",
                ],
                "priority_2_important": [
                    "API endpoints",
                    "Database operations",
                    "Complex algorithms",
                    "Error handling",
                    "Edge cases",
                ],
                "priority_3_nice_to_have": [
                    "Utility functions",
                    "Simple CRUD operations",
                    "UI components",
                ],
                "skip": [
                    "Third-party library code",
                    "Trivial getters/setters",
                    "Auto-generated code",
                    "Framework code",
                ],
            },
            "coverage_targets": {
                "critical_paths": "100% (payment, auth, security)",
                "business_logic": "90-100%",
                "api_endpoints": "85-95%",
                "utilities": "80-90%",
                "ui_components": "70-80%",
                "overall_target": "80-85% (good balance)",
            },
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        code_location: str,
        issue_description: str,
        coverage_metrics: Dict[str, Any],
        suggested_tests: str,
        test_template: str,
    ) -> TestCoverageFinding:
        """Generate a structured test coverage finding"""
        return TestCoverageFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            location={"file": code_location},
            description=issue_description,
            coverage_metrics=coverage_metrics,
            missing_tests=coverage_metrics.get("missing_tests", []),
            uncovered_paths=coverage_metrics.get("uncovered_paths", []),
            suggested_tests=suggested_tests,
            test_template=test_template,
            testing_strategy=self._get_testing_strategy(category),
            tools=self._get_tool_recommendations(),
            remediation={
                "effort": "MEDIUM",
                "priority": "HIGH" if severity == "CRITICAL" else "MEDIUM",
                "time_estimate": "1-3 hours",
            },
        )

    @staticmethod
    def _get_testing_strategy(category: str) -> str:
        """Generate testing strategy based on category"""
        return """
1. Identify missing test cases:
   - Review coverage report
   - Check for uncovered branches
   - Look for edge cases

2. Write tests (TDD):
   - Red: Write failing test
   - Green: Make it pass
   - Refactor: Clean up code

3. Verify coverage improved:
   - pytest --cov=app --cov-report=html
   - Check coverage went up
   - Review HTML report

4. Run mutation testing:
   - mutmut run
   - Verify tests catch mutations
   - Add tests for surviving mutants
        """

    @staticmethod
    def _get_tool_recommendations() -> List[Dict[str, str]]:
        """Get tool recommendations"""
        return [
            {
                "name": "pytest-cov",
                "command": "pytest --cov=app --cov-report=html",
                "description": "Coverage measurement with HTML report",
            },
            {
                "name": "Hypothesis",
                "install": "pip install hypothesis",
                "description": "Property-based testing",
            },
            {
                "name": "mutmut",
                "command": "mutmut run",
                "description": "Mutation testing for Python",
            },
        ]


def create_enhanced_test_coverage_analyzer():
    """Factory function to create enhanced test coverage analyzer"""
    return {
        "name": "Enhanced Test Coverage Analyzer",
        "version": "2.0.0",
        "system_prompt": """You are an expert test coverage analyst with deep knowledge of:

- Coverage metrics (line, branch, function, path, mutation)
- Missing test identification
- Edge case detection (null, empty, boundaries, race conditions)
- Mutation testing (test quality assessment)
- Property-based testing (Hypothesis, QuickCheck)
- Flaky test detection and fixes
- Test strategy (test pyramid, what to test)

Your role is to:
1. Identify coverage gaps
2. Recommend specific test cases
3. Detect edge cases that are missing
4. Suggest property-based tests
5. Find flaky tests
6. Provide test templates

Always provide:
- Coverage percentages (line, branch, function)
- List of missing tests
- Suggested test cases with code
- Testing strategy (unit, integration, e2e)
- Priority (critical paths = 100% coverage)

Format findings as structured YAML with all required fields.
""",
        "assistant_class": EnhancedTestCoverageAnalyzer,
        "domain": "quality_assurance",
        "tags": ["testing", "coverage", "mutation-testing", "hypothesis", "pytest"],
    }


if __name__ == "__main__":
    analyzer = EnhancedTestCoverageAnalyzer()

    print("=" * 60)
    print("Enhanced Test Coverage Analyzer")
    print("=" * 60)
    print(f"\nVersion: {analyzer.version}")
    print(f"Standards: {', '.join(analyzer.standards)}")

    print("\n" + "=" * 60)
    print("Example Finding:")
    print("=" * 60)

    finding = analyzer.generate_finding(
        finding_id="TEST-001",
        title="Missing edge case tests for payment processing",
        severity="CRITICAL",
        category="EdgeCase",
        code_location="app/services/payment.py:process_payment:42",
        issue_description="Payment processing lacks tests for negative amounts, zero, and boundary conditions",
        coverage_metrics={
            "line_coverage": "75%",
            "branch_coverage": "60%",
            "missing_tests": [
                "test_process_payment_negative_amount",
                "test_process_payment_zero_amount",
                "test_process_payment_exceeds_limit",
            ],
            "uncovered_paths": [
                "amount <= 0 → ValueError",
                "amount > user.credit_limit → InsufficientFundsError",
            ],
        },
        suggested_tests="test_process_payment_negative_amount, test_process_payment_zero_amount, test_process_payment_exceeds_limit",
        test_template="""
def test_process_payment_negative_amount():
    with pytest.raises(ValueError):
        process_payment(-10.00, user)
        """,
    )

    print(finding.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("Coverage Summary:")
    print("=" * 60)
    print("✅ Coverage Metrics - Line, branch, function, path, mutation")
    print("✅ Missing Tests - Identification and recommendations")
    print("✅ Edge Cases - Null, empty, boundaries, race conditions")
    print("✅ Property-Based Testing - Hypothesis patterns")
    print("✅ Mutation Testing - Test quality assessment")
    print("✅ Flaky Tests - Detection and fixes")
