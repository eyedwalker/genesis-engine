"""
Enhanced Code Review Assistant

Comprehensive code quality review covering:
- Complexity metrics (Cyclomatic, Cognitive, Halstead)
- Code churn analysis and technical debt
- SOLID principles with examples
- Design patterns and anti-patterns
- Code smells (21 common smells)
- Naming conventions by language
- Dependency injection patterns
- Error handling best practices

References:
- Clean Code (Robert C. Martin)
- Refactoring (Martin Fowler)
- Design Patterns (Gang of Four)
- Cyclomatic Complexity (Thomas McCabe)
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class CodeReviewFinding(BaseModel):
    """Structured code review finding output"""

    finding_id: str = Field(..., description="Unique identifier (CR-001, CR-002, etc.)")
    title: str = Field(..., description="Brief title of the code issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Complexity/Smell/SOLID/Pattern/Naming")

    location: Dict[str, Any] = Field(default_factory=dict, description="File, line, function/class")
    description: str = Field(..., description="Detailed description of the issue")

    metrics: Dict[str, Any] = Field(default_factory=dict, description="Complexity metrics")
    principles_violated: List[str] = Field(default_factory=list, description="SOLID/DRY/KISS violated")

    current_code: str = Field(default="", description="Current problematic code")
    improved_code: str = Field(default="", description="Improved code")
    explanation: str = Field(default="", description="Why the improvement is better")

    refactoring_pattern: str = Field(default="", description="Refactoring pattern to apply")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Analysis tools")

    remediation: Dict[str, str] = Field(default_factory=dict, description="Effort and priority")


class EnhancedCodeReviewAssistant:
    """
    Enhanced Code Review Assistant with comprehensive quality analysis

    Reviews:
    - Code complexity (Cyclomatic, Cognitive, Halstead)
    - Code smells and anti-patterns
    - SOLID principles adherence
    - Design patterns usage
    - Naming and readability
    """

    def __init__(self):
        self.name = "Enhanced Code Review Assistant"
        self.version = "2.0.0"
        self.standards = ["Clean Code", "SOLID", "DRY", "KISS", "YAGNI"]

    # =========================================================================
    # COMPLEXITY METRICS
    # =========================================================================

    @staticmethod
    def complexity_metrics_guide() -> Dict[str, Any]:
        """
        Guide to code complexity metrics
        """
        return {
            "cyclomatic_complexity": {
                "description": "Number of independent paths through code",
                "formula": "M = E - N + 2P (E=edges, N=nodes, P=connected components)",
                "calculation": "Count: if, for, while, case, &&, ||, catch, ?, : +1",
                "thresholds": {
                    "1-10": "Simple, low risk",
                    "11-20": "Moderate complexity",
                    "21-50": "Complex, high risk",
                    "50+": "Untestable, refactor immediately",
                },
                "target": "≤ 10 per function",
                "example": """
# Cyclomatic Complexity = 5
def calculate_discount(price, customer_type, is_member, quantity):
    discount = 0

    if customer_type == 'premium':  # +1
        discount = 0.20
    elif customer_type == 'regular':  # +1
        discount = 0.10

    if is_member:  # +1
        discount += 0.05

    if quantity > 100:  # +1
        discount += 0.10

    return price * (1 - discount)

# M = 5 (4 decision points + 1)
# This is acceptable (< 10)

# High complexity example (M = 15)
def process_order(order):
    if order.status == 'new':  # +1
        if order.total > 100:  # +1
            if order.customer.is_premium():  # +1
                apply_premium_discount()
            elif order.has_coupon():  # +1
                apply_coupon()
        elif order.items_count > 5:  # +1
            if order.customer.is_member():  # +1
                apply_bulk_discount()

        for item in order.items:  # +1
            if item.is_taxable():  # +1
                apply_tax(item)

        if order.requires_shipping():  # +1
            if order.destination.is_remote():  # +1
                add_extra_shipping()
            else:
                add_standard_shipping()

        if order.payment_method == 'credit':  # +1
            process_credit_payment()
        elif order.payment_method == 'paypal':  # +1
            process_paypal_payment()
        else:
            process_cash_payment()

# M = 15 (TOO COMPLEX! Refactor needed)
                """,
                "tools": [
                    {
                        "name": "radon (Python)",
                        "install": "pip install radon",
                        "command": "radon cc app/ -a -nb",
                        "output": """
app/services.py
    M 45:0 OrderService.process_order - C (15)
    M 80:0 OrderService.calculate_total - A (3)
        """,
                    },
                    {
                        "name": "complexity-report (JavaScript)",
                        "install": "npm install -g complexity-report",
                        "command": "cr --format json src/",
                    },
                    {
                        "name": "lizard (Multi-language)",
                        "install": "pip install lizard",
                        "command": "lizard app/",
                    },
                ],
            },
            "cognitive_complexity": {
                "description": "How difficult code is to understand (human perspective)",
                "difference": "Cyclomatic counts paths, Cognitive counts mental effort",
                "rules": [
                    "Nested structures increase by nesting level",
                    "Break/continue don't add complexity",
                    "Recursion adds +1",
                    "Boolean operators in different contexts add +1",
                ],
                "example": """
# Cyclomatic: 4, Cognitive: 7
def example(a, b, c):
    if a:  # +1, nesting level 1
        if b:  # +2 (nested)
            if c:  # +3 (deeply nested)
                return 1
    return 0

# Cognitive complexity penalizes nesting more!

# Cyclomatic: 3, Cognitive: 1
def flat_example(a, b, c):
    if not a:  # +1
        return 0
    if not b:  # +0 (same level)
        return 0
    if not c:  # +0 (same level)
        return 0
    return 1

# Guard clauses reduce cognitive complexity!
                """,
                "target": "≤ 15 per function",
            },
            "halstead_metrics": {
                "description": "Measures based on operators and operands",
                "metrics": {
                    "n1": "Number of distinct operators",
                    "n2": "Number of distinct operands",
                    "N1": "Total occurrences of operators",
                    "N2": "Total occurrences of operands",
                    "vocabulary": "n = n1 + n2",
                    "length": "N = N1 + N2",
                    "volume": "V = N * log2(n)",
                    "difficulty": "D = (n1/2) * (N2/n2)",
                    "effort": "E = D * V",
                },
                "interpretation": {
                    "volume": "Program size (bits required)",
                    "difficulty": "How hard to write/understand",
                    "effort": "Mental effort required",
                },
                "tools": [
                    {
                        "name": "radon (Python)",
                        "command": "radon hal app/services.py",
                    },
                ],
            },
        }

    # =========================================================================
    # SOLID PRINCIPLES
    # =========================================================================

    @staticmethod
    def solid_principles() -> Dict[str, Any]:
        """
        SOLID principles with examples
        """
        return {
            "single_responsibility": {
                "principle": "A class should have only one reason to change",
                "bad": """
# BAD: UserManager does too many things
class UserManager:
    def create_user(self, email, password):
        # 1. Validates email
        if not self.is_valid_email(email):
            raise ValueError()

        # 2. Hashes password
        hashed = self.hash_password(password)

        # 3. Saves to database
        self.db.execute("INSERT INTO users...")

        # 4. Sends welcome email
        self.send_email(email, "Welcome!")

        # 5. Logs audit event
        self.logger.info(f"Created user {email}")

# Violates SRP: 5 responsibilities!
# Changes to email validation, password hashing, database schema,
# email templates, or logging all require modifying this class.
                """,
                "good": """
# GOOD: Separate responsibilities
class EmailValidator:
    def is_valid(self, email):
        return '@' in email and '.' in email

class PasswordHasher:
    def hash(self, password):
        return bcrypt.hashpw(password, bcrypt.gensalt())

class UserRepository:
    def save(self, user):
        self.db.execute("INSERT INTO users...", user)

class WelcomeEmailSender:
    def send(self, user):
        self.mailer.send(user.email, "Welcome!")

class AuditLogger:
    def log_user_created(self, user):
        self.logger.info(f"Created user {user.email}")

class UserService:
    def __init__(self, validator, hasher, repository, email_sender, audit_logger):
        self.validator = validator
        self.hasher = hasher
        self.repository = repository
        self.email_sender = email_sender
        self.audit_logger = audit_logger

    def create_user(self, email, password):
        if not self.validator.is_valid(email):
            raise ValueError()

        user = User(email, self.hasher.hash(password))
        self.repository.save(user)
        self.email_sender.send(user)
        self.audit_logger.log_user_created(user)

# Each class has ONE reason to change
                """,
            },
            "open_closed": {
                "principle": "Open for extension, closed for modification",
                "bad": """
# BAD: Must modify class to add new shape
class AreaCalculator:
    def calculate(self, shape):
        if shape.type == 'circle':
            return 3.14 * shape.radius ** 2
        elif shape.type == 'rectangle':
            return shape.width * shape.height
        elif shape.type == 'triangle':
            return 0.5 * shape.base * shape.height
        # Adding new shape = modify this function!
                """,
                "good": """
# GOOD: Extend with new classes, don't modify existing code
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate(self, shape: Shape):
        return shape.area()  # Works for any Shape!

# Add new shape = create new class, don't modify existing
class Hexagon(Shape):
    def area(self):
        return ...  # New shape, no modifications needed!
                """,
            },
            "liskov_substitution": {
                "principle": "Subtypes must be substitutable for their base types",
                "bad": """
# BAD: Square violates LSP
class Rectangle:
    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, width):
        self.width = width
        self.height = width  # Unexpected side effect!

    def set_height(self, height):
        self.width = height
        self.height = height  # Unexpected side effect!

# Breaks client code:
def test_rectangle(rect):
    rect.set_width(5)
    rect.set_height(4)
    assert rect.area() == 20  # Fails for Square!

# Violation: Square is NOT substitutable for Rectangle
                """,
                "good": """
# GOOD: Separate hierarchies
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

# No inheritance relationship, no LSP violation
                """,
            },
            "interface_segregation": {
                "principle": "Clients shouldn't depend on interfaces they don't use",
                "bad": """
# BAD: Fat interface
class Worker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def sleep(self):
        pass

class HumanWorker(Worker):
    def work(self):
        print("Working")
    def eat(self):
        print("Eating")
    def sleep(self):
        print("Sleeping")

class RobotWorker(Worker):
    def work(self):
        print("Working")
    def eat(self):
        pass  # Robots don't eat! (Forced to implement)
    def sleep(self):
        pass  # Robots don't sleep! (Forced to implement)
                """,
                "good": """
# GOOD: Segregated interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class HumanWorker(Workable, Eatable, Sleepable):
    def work(self):
        print("Working")
    def eat(self):
        print("Eating")
    def sleep(self):
        print("Sleeping")

class RobotWorker(Workable):
    def work(self):
        print("Working")
    # Only implements what it needs!
                """,
            },
            "dependency_inversion": {
                "principle": "Depend on abstractions, not concretions",
                "bad": """
# BAD: High-level module depends on low-level module
class MySQLDatabase:
    def save(self, data):
        # MySQL-specific code
        pass

class UserService:
    def __init__(self):
        self.db = MySQLDatabase()  # Tightly coupled!

    def create_user(self, user):
        self.db.save(user)

# Can't swap MySQL for PostgreSQL without changing UserService
                """,
                "good": """
# GOOD: Both depend on abstraction
from abc import ABC, abstractmethod

class Database(ABC):  # Abstraction
    @abstractmethod
    def save(self, data):
        pass

class MySQLDatabase(Database):
    def save(self, data):
        # MySQL-specific code
        pass

class PostgreSQLDatabase(Database):
    def save(self, data):
        # PostgreSQL-specific code
        pass

class UserService:
    def __init__(self, db: Database):  # Depend on abstraction
        self.db = db

    def create_user(self, user):
        self.db.save(user)

# Can swap implementations easily:
service = UserService(MySQLDatabase())
# or
service = UserService(PostgreSQLDatabase())
                """,
            },
        }

    # =========================================================================
    # CODE SMELLS (21 Common Smells)
    # =========================================================================

    @staticmethod
    def code_smells() -> Dict[str, Any]:
        """
        21 common code smells and how to fix them
        """
        return {
            "bloaters": {
                "long_method": {
                    "smell": "Function > 50 lines",
                    "fix": "Extract Method refactoring",
                    "example": """
# BAD: 100-line method
def process_order(order):
    # 20 lines of validation
    # 30 lines of price calculation
    # 25 lines of inventory check
    # 25 lines of payment processing

# GOOD: Extract smaller methods
def process_order(order):
    validate_order(order)
    price = calculate_total_price(order)
    reserve_inventory(order)
    process_payment(order, price)
                    """,
                },
                "large_class": {
                    "smell": "Class > 300 lines or > 10 methods",
                    "fix": "Extract Class refactoring",
                },
                "long_parameter_list": {
                    "smell": "> 4 parameters",
                    "fix": "Introduce Parameter Object",
                    "example": """
# BAD: Too many parameters
def create_user(first_name, last_name, email, phone, address, city, state, zip):
    pass

# GOOD: Parameter object
class UserInfo:
    def __init__(self, first_name, last_name, email, phone, address):
        self.first_name = first_name
        ...

def create_user(user_info: UserInfo):
    pass
                    """,
                },
                "primitive_obsession": {
                    "smell": "Using primitives instead of small objects",
                    "example": """
# BAD: String for email everywhere
def send_email(email: str):
    if '@' not in email:  # Validation everywhere!
        raise ValueError()

# GOOD: Email value object
class Email:
    def __init__(self, value):
        if '@' not in value:
            raise ValueError()
        self.value = value

def send_email(email: Email):
    pass  # Already validated!
                    """,
                },
            },
            "object_orientation_abusers": {
                "switch_statements": {
                    "smell": "Type code with switch/if-elif chains",
                    "fix": "Replace Conditional with Polymorphism",
                    "example": """
# BAD: Switch on type
def calculate_shipping(order_type, weight):
    if order_type == 'standard':
        return weight * 0.5
    elif order_type == 'express':
        return weight * 1.5
    elif order_type == 'overnight':
        return weight * 3.0

# GOOD: Polymorphism
class ShippingMethod(ABC):
    @abstractmethod
    def calculate(self, weight):
        pass

class StandardShipping(ShippingMethod):
    def calculate(self, weight):
        return weight * 0.5

class ExpressShipping(ShippingMethod):
    def calculate(self, weight):
        return weight * 1.5
                    """,
                },
                "refused_bequest": {
                    "smell": "Subclass doesn't use inherited methods",
                    "fix": "Replace Inheritance with Delegation",
                },
            },
            "change_preventers": {
                "divergent_change": {
                    "smell": "One class changes for multiple reasons",
                    "fix": "Extract Class (SRP)",
                },
                "shotgun_surgery": {
                    "smell": "One change requires modifying many classes",
                    "fix": "Move Method, Move Field",
                },
            },
            "dispensables": {
                "duplicate_code": {
                    "smell": "Same code in multiple places",
                    "fix": "Extract Method/Class, Pull Up Method",
                    "example": """
# BAD: Duplicate validation
def create_user(email, password):
    if not email or '@' not in email:
        raise ValueError()
    if len(password) < 8:
        raise ValueError()

def update_user(user_id, email, password):
    if not email or '@' not in email:  # Duplicate!
        raise ValueError()
    if len(password) < 8:  # Duplicate!
        raise ValueError()

# GOOD: Extract validation
def validate_email(email):
    if not email or '@' not in email:
        raise ValueError()

def validate_password(password):
    if len(password) < 8:
        raise ValueError()

def create_user(email, password):
    validate_email(email)
    validate_password(password)
                    """,
                },
                "dead_code": {
                    "smell": "Unused variables, functions, classes",
                    "fix": "Delete it!",
                },
                "speculative_generality": {
                    "smell": "Code for future use that never comes",
                    "fix": "Delete unused abstractions (YAGNI)",
                },
            },
            "couplers": {
                "feature_envy": {
                    "smell": "Method uses another class more than its own",
                    "fix": "Move Method",
                    "example": """
# BAD: Feature envy
class Order:
    def get_total(self):
        return self.price * self.quantity

class OrderProcessor:
    def calculate_discount(self, order):
        # Uses order fields extensively
        base = order.price * order.quantity
        if order.customer.is_premium():
            base *= 0.9
        return base

# GOOD: Move to Order
class Order:
    def get_total(self):
        base = self.price * self.quantity
        if self.customer.is_premium():
            base *= 0.9
        return base
                    """,
                },
                "inappropriate_intimacy": {
                    "smell": "Classes know too much about each other's internals",
                    "fix": "Move Method, Extract Class",
                },
            },
        }

    # =========================================================================
    # DEPENDENCY INJECTION PATTERNS
    # =========================================================================

    @staticmethod
    def dependency_injection_patterns() -> Dict[str, Any]:
        """
        Dependency injection patterns and implementations
        """
        return {
            "constructor_injection": {
                "description": "Dependencies provided through constructor",
                "bad": """
# BAD: Hard-coded dependencies
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # Hard-coded!
        self.mailer = SMTPMailer()  # Hard-coded!
        self.logger = FileLogger()  # Hard-coded!

    def create_order(self, order):
        self.db.save(order)
        self.mailer.send(order.customer.email, "Order created")
        self.logger.log(f"Order {order.id} created")

# Problems:
# - Can't test with mocks
# - Can't swap implementations
# - Tightly coupled
                """,
                "good": """
# GOOD: Constructor injection
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, entity): pass

class Mailer(ABC):
    @abstractmethod
    def send(self, to, message): pass

class Logger(ABC):
    @abstractmethod
    def log(self, message): pass

class OrderService:
    def __init__(self, db: Database, mailer: Mailer, logger: Logger):
        self.db = db
        self.mailer = mailer
        self.logger = logger

    def create_order(self, order):
        self.db.save(order)
        self.mailer.send(order.customer.email, "Order created")
        self.logger.log(f"Order {order.id} created")

# Now testable with mocks:
class MockDatabase(Database):
    def __init__(self):
        self.saved = []
    def save(self, entity):
        self.saved.append(entity)

def test_create_order():
    mock_db = MockDatabase()
    mock_mailer = MockMailer()
    mock_logger = MockLogger()
    service = OrderService(mock_db, mock_mailer, mock_logger)
    service.create_order(Order(id=1))
    assert len(mock_db.saved) == 1
                """,
            },
            "setter_injection": {
                "description": "Dependencies set via setter methods",
                "example": """
# Setter injection (less preferred than constructor)
class ReportGenerator:
    def __init__(self):
        self._formatter = None
        self._exporter = None

    def set_formatter(self, formatter: Formatter):
        self._formatter = formatter

    def set_exporter(self, exporter: Exporter):
        self._exporter = exporter

    def generate(self, data):
        if not self._formatter or not self._exporter:
            raise RuntimeError("Dependencies not set")
        formatted = self._formatter.format(data)
        return self._exporter.export(formatted)

# Usage
generator = ReportGenerator()
generator.set_formatter(HTMLFormatter())
generator.set_exporter(PDFExporter())
                """,
            },
            "interface_injection": {
                "description": "Object implements an interface for dependency injection",
                "example": """
# Interface injection
class InjectDatabase(ABC):
    @abstractmethod
    def inject_database(self, db: Database): pass

class InjectMailer(ABC):
    @abstractmethod
    def inject_mailer(self, mailer: Mailer): pass

class OrderService(InjectDatabase, InjectMailer):
    def inject_database(self, db: Database):
        self.db = db

    def inject_mailer(self, mailer: Mailer):
        self.mailer = mailer

# Injector knows to call these methods
injector.inject_dependencies(service)
                """,
            },
            "di_containers": {
                "description": "Dependency injection containers/frameworks",
                "python_examples": {
                    "dependency_injector": """
# Using dependency-injector library
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    database = providers.Singleton(
        PostgreSQLDatabase,
        host=config.db.host,
        port=config.db.port,
    )

    mailer = providers.Factory(
        SMTPMailer,
        host=config.smtp.host,
    )

    order_service = providers.Factory(
        OrderService,
        db=database,
        mailer=mailer,
    )

# Usage
container = Container()
container.config.from_yaml('config.yaml')
service = container.order_service()
                    """,
                    "inject": """
# Using inject library
import inject

def configure(binder):
    binder.bind(Database, PostgreSQLDatabase())
    binder.bind(Mailer, SMTPMailer())

inject.configure(configure)

class OrderService:
    @inject.autoparams()
    def __init__(self, db: Database, mailer: Mailer):
        self.db = db
        self.mailer = mailer
                    """,
                    "fastapi": """
# FastAPI has built-in DI via Depends
from fastapi import Depends, FastAPI

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_order_service(db: Session = Depends(get_db)):
    return OrderService(db)

@app.post("/orders")
def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service)
):
    return service.create_order(order)
                    """,
                },
            },
        }

    # =========================================================================
    # ERROR HANDLING PATTERNS
    # =========================================================================

    @staticmethod
    def error_handling_patterns() -> Dict[str, Any]:
        """
        Error handling best practices and patterns
        """
        return {
            "exception_hierarchy": {
                "description": "Create meaningful exception hierarchies",
                "bad": """
# BAD: Generic exceptions everywhere
class OrderService:
    def create_order(self, order):
        if not order.items:
            raise Exception("No items")  # Too generic!
        if not order.customer:
            raise Exception("No customer")  # Can't distinguish!
        try:
            self.db.save(order)
        except:
            raise Exception("Failed")  # Lost all context!
                """,
                "good": """
# GOOD: Custom exception hierarchy
class OrderError(Exception):
    '''Base exception for order operations'''
    pass

class ValidationError(OrderError):
    '''Validation failed'''
    pass

class EmptyOrderError(ValidationError):
    '''Order has no items'''
    pass

class MissingCustomerError(ValidationError):
    '''Order has no customer'''
    pass

class PersistenceError(OrderError):
    '''Database operation failed'''
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class OrderService:
    def create_order(self, order):
        if not order.items:
            raise EmptyOrderError("Order must have at least one item")
        if not order.customer:
            raise MissingCustomerError("Order must have a customer")
        try:
            self.db.save(order)
        except DatabaseError as e:
            raise PersistenceError("Failed to save order", e) from e

# Now callers can handle specific cases:
try:
    service.create_order(order)
except EmptyOrderError:
    show_error("Please add items to your cart")
except MissingCustomerError:
    redirect_to_login()
except PersistenceError:
    show_error("Server error, please try again")
                """,
            },
            "fail_fast": {
                "description": "Validate early and fail immediately",
                "bad": """
# BAD: Fail late with unclear state
def process_payment(card_number, amount, currency):
    # Start processing...
    transaction = Transaction()
    transaction.amount = amount  # What if amount is negative?
    transaction.currency = currency  # What if invalid?

    # Charge card (now we find out card is invalid)
    result = gateway.charge(card_number, amount)  # Fails late!
    return result
                """,
                "good": """
# GOOD: Fail fast with guard clauses
def process_payment(card_number, amount, currency):
    # Validate everything first
    if not card_number or len(card_number) < 13:
        raise InvalidCardError("Invalid card number")
    if amount <= 0:
        raise InvalidAmountError("Amount must be positive")
    if currency not in SUPPORTED_CURRENCIES:
        raise UnsupportedCurrencyError(f"Currency {currency} not supported")

    # All validations passed, now process
    transaction = Transaction(amount=amount, currency=currency)
    return gateway.charge(card_number, transaction)
                """,
            },
            "never_catch_base_exception": {
                "description": "Avoid catching Exception or BaseException",
                "bad": """
# BAD: Catches everything including KeyboardInterrupt
try:
    process_data()
except Exception as e:  # Too broad!
    logger.error(f"Error: {e}")
    return None  # Silently returns None

# WORSE: Catches even system exit
try:
    process_data()
except:  # Catches EVERYTHING!
    pass  # Silent failure
                """,
                "good": """
# GOOD: Catch specific exceptions
try:
    process_data()
except ValueError as e:
    logger.warning(f"Invalid data: {e}")
    raise ValidationError("Invalid data format") from e
except IOError as e:
    logger.error(f"IO error: {e}")
    raise ProcessingError("Failed to process data") from e
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise PersistenceError("Database operation failed") from e

# If you must catch broadly, re-raise unexpected exceptions
try:
    process_data()
except (ValueError, IOError, DatabaseError) as e:
    handle_known_error(e)
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise  # Re-raise unexpected exceptions!
                """,
            },
            "context_managers": {
                "description": "Use context managers for resource cleanup",
                "bad": """
# BAD: Manual resource management
def read_file(path):
    f = open(path)
    data = f.read()
    f.close()  # Never called if error occurs!
    return data

# BAD: Try-finally everywhere
def read_file(path):
    f = None
    try:
        f = open(path)
        return f.read()
    finally:
        if f:
            f.close()  # Verbose and error-prone
                """,
                "good": """
# GOOD: Context manager
def read_file(path):
    with open(path) as f:
        return f.read()  # Automatically closed

# GOOD: Custom context manager for cleanup
from contextlib import contextmanager

@contextmanager
def database_transaction(db):
    transaction = db.begin()
    try:
        yield transaction
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise

# Usage
with database_transaction(db) as tx:
    tx.execute("INSERT INTO users ...")
    tx.execute("INSERT INTO profiles ...")
# Auto-committed on success, auto-rolled-back on error
                """,
            },
            "result_types": {
                "description": "Use Result types instead of exceptions for expected failures",
                "example": """
# Result type pattern (inspired by Rust/Haskell)
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E')

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]

# Usage
def parse_int(s: str) -> Result[int, str]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"Cannot parse '{s}' as integer")

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Err("Division by zero")
    return Ok(a / b)

# Clean error handling without exceptions
result = parse_int(user_input)
match result:
    case Ok(value):
        print(f"Parsed: {value}")
    case Err(error):
        print(f"Error: {error}")
                """,
            },
        }

    # =========================================================================
    # CODE DOCUMENTATION PATTERNS
    # =========================================================================

    @staticmethod
    def documentation_patterns() -> Dict[str, Any]:
        """
        Documentation best practices
        """
        return {
            "docstring_styles": {
                "google_style": '''
def calculate_total(items: List[Item], discount: float = 0.0) -> Decimal:
    """Calculate the total price with optional discount.

    This function sums up all item prices and applies any discount
    to the final total.

    Args:
        items: List of Item objects to calculate total for.
            Each item must have a price attribute.
        discount: Discount percentage as decimal (0.1 = 10%).
            Defaults to 0.0 (no discount).

    Returns:
        The total price as a Decimal, rounded to 2 decimal places.

    Raises:
        ValueError: If discount is negative or greater than 1.
        EmptyOrderError: If items list is empty.

    Example:
        >>> items = [Item(price=10.00), Item(price=20.00)]
        >>> calculate_total(items, discount=0.1)
        Decimal('27.00')
    """
    if not items:
        raise EmptyOrderError("Cannot calculate total for empty order")
    if discount < 0 or discount > 1:
        raise ValueError("Discount must be between 0 and 1")

    subtotal = sum(item.price for item in items)
    return Decimal(subtotal * (1 - discount)).quantize(Decimal('.01'))
                ''',
                "numpy_style": '''
def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
    """
    Calculate descriptive statistics for the given data.

    Parameters
    ----------
    data : np.ndarray
        A 1-dimensional numpy array of numerical values.
        Must contain at least one non-NaN value.

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - mean : arithmetic mean
        - median : median value
        - std : standard deviation
        - min : minimum value
        - max : maximum value

    Raises
    ------
    ValueError
        If data is empty or contains only NaN values.

    See Also
    --------
    numpy.mean : Calculate arithmetic mean.
    numpy.std : Calculate standard deviation.

    Examples
    --------
    >>> data = np.array([1, 2, 3, 4, 5])
    >>> stats = calculate_statistics(data)
    >>> stats['mean']
    3.0
    """
    pass
                ''',
            },
            "type_hints": {
                "description": "Use type hints for self-documenting code",
                "bad": """
# BAD: No type hints
def process(data, config, callback):
    # What types are expected?
    result = do_something(data)
    if config['enabled']:  # Is this a dict?
        callback(result)  # What signature?
    return result
                """,
                "good": """
# GOOD: Full type hints
from typing import Callable, TypedDict, Optional, List

class ProcessConfig(TypedDict):
    enabled: bool
    max_items: int
    timeout: Optional[float]

ProcessResult = List[Dict[str, Any]]
Callback = Callable[[ProcessResult], None]

def process(
    data: List[str],
    config: ProcessConfig,
    callback: Optional[Callback] = None
) -> ProcessResult:
    '''Process data according to config.'''
    result: ProcessResult = []
    for item in data[:config['max_items']]:
        result.append({'item': item, 'processed': True})

    if config['enabled'] and callback:
        callback(result)

    return result
                """,
            },
            "api_documentation": {
                "description": "Document API contracts clearly",
                "example": """
class UserService:
    '''Service for managing user accounts.

    This service handles user CRUD operations, authentication,
    and profile management. It requires a database connection
    and optional email service for notifications.

    Attributes:
        db: Database connection for persistence.
        mailer: Optional email service for notifications.

    Thread Safety:
        This class is thread-safe for concurrent operations.

    Example:
        >>> db = PostgresDatabase(connection_string)
        >>> service = UserService(db)
        >>> user = service.create_user(
        ...     email="user@example.com",
        ...     password="secure123"
        ... )
        >>> print(user.id)
        123
    '''

    def create_user(
        self,
        email: str,
        password: str,
        *,  # Force keyword-only arguments
        send_welcome_email: bool = True,
        role: UserRole = UserRole.STANDARD
    ) -> User:
        '''Create a new user account.

        Creates a new user with the given email and password.
        Passwords are automatically hashed before storage.

        Args:
            email: User's email address. Must be unique.
            password: Plain-text password. Must be >= 8 chars.
            send_welcome_email: Whether to send welcome email.
            role: Initial user role. Defaults to STANDARD.

        Returns:
            The newly created User object with generated ID.

        Raises:
            DuplicateEmailError: If email already exists.
            WeakPasswordError: If password doesn't meet policy.
            EmailDeliveryError: If welcome email fails (when enabled).

        Note:
            This method is idempotent if called with same email
            within a short time window (deduplication enabled).
        '''
        pass
                """,
            },
        }

    # =========================================================================
    # NAMING CONVENTIONS
    # =========================================================================

    @staticmethod
    def naming_conventions() -> Dict[str, Any]:
        """
        Naming conventions by language
        """
        return {
            "python": {
                "classes": "PascalCase (e.g., UserService, OrderManager)",
                "functions": "snake_case (e.g., calculate_total, send_email)",
                "constants": "SCREAMING_SNAKE_CASE (e.g., MAX_RETRY, DEFAULT_TIMEOUT)",
                "variables": "snake_case (e.g., user_count, is_active)",
                "private": "_single_leading_underscore (e.g., _internal_method)",
                "magic": "__double_leading_and_trailing__ (e.g., __init__, __str__)",
                "example": """
# Good Python naming
class OrderProcessor:  # PascalCase
    MAX_ITEMS = 100  # SCREAMING_SNAKE_CASE

    def __init__(self):
        self._cache = {}  # private

    def process_order(self, order_id):  # snake_case
        item_count = self._get_item_count(order_id)
        return item_count < self.MAX_ITEMS

    def _get_item_count(self, order_id):  # private method
        return len(self._cache.get(order_id, []))
                """,
            },
            "javascript": {
                "classes": "PascalCase (e.g., UserService, OrderManager)",
                "functions": "camelCase (e.g., calculateTotal, sendEmail)",
                "constants": "SCREAMING_SNAKE_CASE (e.g., MAX_RETRY, DEFAULT_TIMEOUT)",
                "variables": "camelCase (e.g., userCount, isActive)",
                "private": "#privateField or _conventionPrivate",
                "example": """
// Good JavaScript naming
class OrderProcessor {  // PascalCase
  static MAX_ITEMS = 100;  // SCREAMING_SNAKE_CASE
  #cache = {};  // private field

  constructor() {
    this.#cache = {};
  }

  processOrder(orderId) {  // camelCase
    const itemCount = this.#getItemCount(orderId);
    return itemCount < OrderProcessor.MAX_ITEMS;
  }

  #getItemCount(orderId) {  // private method
    return (this.#cache[orderId] || []).length;
  }
}
                """,
            },
            "best_practices": {
                "descriptive": "Use descriptive names (getUserById not get)",
                "avoid_abbreviations": "No abbreviations (calculate_total not calc_tot)",
                "boolean_prefix": "Boolean: is_, has_, can_, should_ (is_active, has_permission)",
                "no_magic_numbers": "Named constants instead of literals",
                "consistent": "Same naming pattern throughout codebase",
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
        metrics: Dict[str, Any],
        current_code: str,
        improved_code: str,
        explanation: str,
    ) -> CodeReviewFinding:
        """Generate a structured code review finding"""
        return CodeReviewFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            location={"file": code_location},
            description=issue_description,
            metrics=metrics,
            principles_violated=metrics.get("principles_violated", []),
            current_code=current_code,
            improved_code=improved_code,
            explanation=explanation,
            refactoring_pattern=self._get_refactoring_pattern(category),
            tools=self._get_tool_recommendations(),
            remediation={
                "effort": "MEDIUM",
                "priority": "HIGH" if severity == "CRITICAL" else "MEDIUM",
                "time_estimate": "2-4 hours",
            },
        )

    @staticmethod
    def _get_refactoring_pattern(category: str) -> str:
        """Get refactoring pattern recommendation"""
        patterns = {
            "Complexity": "Extract Method, Simplify Conditional",
            "Smell": "Extract Class, Move Method",
            "SOLID": "Introduce Interface, Dependency Injection",
            "Pattern": "Strategy Pattern, Template Method",
            "Naming": "Rename Method/Variable",
        }
        return patterns.get(category, "Refactor for clarity")

    @staticmethod
    def _get_tool_recommendations() -> List[Dict[str, str]]:
        """Get tool recommendations"""
        return [
            {
                "name": "radon (Python)",
                "command": "radon cc app/ -a -nb",
                "description": "Cyclomatic complexity analysis",
            },
            {
                "name": "pylint (Python)",
                "command": "pylint app/",
                "description": "Code quality and style",
            },
            {
                "name": "SonarQube",
                "url": "https://www.sonarqube.org/",
                "description": "Comprehensive code quality platform",
            },
        ]


    # =========================================================================
    # TESTING PATTERNS
    # =========================================================================

    @staticmethod
    def testing_patterns() -> Dict[str, Any]:
        """
        Testing best practices for code quality
        """
        return {
            "test_structure": {
                "arrange_act_assert": """
# GOOD: Clear AAA structure
def test_calculate_discount_for_premium_customer():
    # Arrange
    customer = Customer(tier='premium')
    order = Order(total=100.00)
    calculator = DiscountCalculator()

    # Act
    discount = calculator.calculate(customer, order)

    # Assert
    assert discount == 20.00  # 20% for premium
                """,
                "given_when_then": """
# BDD style
def test_premium_customer_gets_20_percent_discount():
    # Given a premium customer with a $100 order
    customer = Customer(tier='premium')
    order = Order(total=100.00)
    calculator = DiscountCalculator()

    # When calculating the discount
    discount = calculator.calculate(customer, order)

    # Then the discount should be $20
    assert discount == 20.00
                """,
            },
            "test_naming": {
                "description": "Test names should describe behavior",
                "bad": """
# BAD: Unclear test names
def test_calculate():
    pass

def test_user():
    pass

def test_order_1():
    pass
                """,
                "good": """
# GOOD: Descriptive test names
def test_calculate_returns_zero_for_empty_cart():
    pass

def test_user_creation_fails_with_invalid_email():
    pass

def test_order_total_includes_shipping_for_small_orders():
    pass

# Or with classes for grouping
class TestOrderTotal:
    def test_includes_shipping_for_orders_under_50():
        pass

    def test_free_shipping_for_orders_over_50():
        pass

    def test_applies_tax_after_discount():
        pass
                """,
            },
            "test_isolation": {
                "description": "Tests should be independent",
                "bad": """
# BAD: Tests depend on each other
class TestUserService:
    user_id = None  # Shared state!

    def test_create_user(self):
        user = service.create_user(email="test@example.com")
        TestUserService.user_id = user.id  # Set for next test

    def test_get_user(self):
        # Depends on test_create_user running first!
        user = service.get_user(TestUserService.user_id)
        assert user.email == "test@example.com"
                """,
                "good": """
# GOOD: Each test is independent
class TestUserService:
    @pytest.fixture
    def user(self, db):
        '''Create a fresh user for each test'''
        return service.create_user(email="test@example.com")

    def test_create_user(self, db):
        user = service.create_user(email="new@example.com")
        assert user.id is not None

    def test_get_user(self, user):  # Uses fixture
        fetched = service.get_user(user.id)
        assert fetched.email == user.email

    def test_update_user(self, user):  # Fresh user each time
        service.update_user(user.id, email="updated@example.com")
        fetched = service.get_user(user.id)
        assert fetched.email == "updated@example.com"
                """,
            },
            "mocking": {
                "description": "Use mocks to isolate units",
                "example": """
# GOOD: Mock external dependencies
from unittest.mock import Mock, patch, MagicMock

class TestOrderService:
    def test_create_order_sends_confirmation_email(self):
        # Arrange
        mock_mailer = Mock()
        mock_db = Mock()
        mock_db.save.return_value = Order(id=123)

        service = OrderService(db=mock_db, mailer=mock_mailer)
        order_data = OrderCreate(items=[...], customer_email="test@example.com")

        # Act
        service.create_order(order_data)

        # Assert
        mock_mailer.send.assert_called_once_with(
            to="test@example.com",
            subject="Order Confirmation",
            body=ANY  # Don't care about exact body
        )

    @patch('myapp.services.stripe')
    def test_payment_processing(self, mock_stripe):
        # Mock Stripe API
        mock_stripe.PaymentIntent.create.return_value = MagicMock(
            id='pi_123',
            status='succeeded'
        )

        result = payment_service.process(amount=100)

        assert result.success
        mock_stripe.PaymentIntent.create.assert_called_with(
            amount=10000,  # cents
            currency='usd'
        )
                """,
            },
        }

    @staticmethod
    def get_tool_recommendations() -> List[Dict[str, str]]:
        """Get recommended analysis tools"""
        return [
            {
                "name": "radon",
                "install": "pip install radon",
                "usage": "radon cc app/ -a -nb",
                "description": "Cyclomatic complexity and maintainability index",
            },
            {
                "name": "pylint",
                "install": "pip install pylint",
                "usage": "pylint app/ --output-format=json",
                "description": "Comprehensive linting and code quality",
            },
            {
                "name": "flake8",
                "install": "pip install flake8",
                "usage": "flake8 app/ --format=json",
                "description": "Style guide enforcement (PEP 8)",
            },
            {
                "name": "mypy",
                "install": "pip install mypy",
                "usage": "mypy app/ --json-report",
                "description": "Static type checking",
            },
            {
                "name": "black",
                "install": "pip install black",
                "usage": "black --check app/",
                "description": "Code formatting verification",
            },
            {
                "name": "isort",
                "install": "pip install isort",
                "usage": "isort --check-only app/",
                "description": "Import sorting verification",
            },
        ]


def create_enhanced_code_review_assistant():
    """Factory function to create enhanced code review assistant"""
    return {
        "name": "Enhanced Code Review Assistant",
        "version": "2.0.0",
        "system_prompt": """You are an expert code reviewer with deep knowledge of software engineering
best practices, clean code principles, and code quality metrics. Your expertise spans multiple
programming languages including Python, JavaScript, TypeScript, Java, Go, and Rust.

Your core competencies include:

1. COMPLEXITY ANALYSIS
   - Cyclomatic complexity measurement and interpretation
   - Cognitive complexity assessment (SonarQube methodology)
   - Halstead metrics (volume, difficulty, effort)
   - Maintainability index calculation

2. SOLID PRINCIPLES
   - Single Responsibility Principle (SRP) - one reason to change
   - Open/Closed Principle (OCP) - open for extension, closed for modification
   - Liskov Substitution Principle (LSP) - subtypes must be substitutable
   - Interface Segregation Principle (ISP) - no forced dependencies
   - Dependency Inversion Principle (DIP) - depend on abstractions

3. CODE SMELLS (21+ Common Patterns)
   - Bloaters: Long Method, Large Class, Long Parameter List
   - Object-Orientation Abusers: Switch Statements, Refused Bequest
   - Change Preventers: Divergent Change, Shotgun Surgery
   - Dispensables: Duplicate Code, Dead Code, Speculative Generality
   - Couplers: Feature Envy, Inappropriate Intimacy

4. DESIGN PATTERNS
   - Creational: Factory, Builder, Singleton, Prototype
   - Structural: Adapter, Decorator, Facade, Composite
   - Behavioral: Strategy, Observer, Command, Template Method

5. CLEAN CODE PRACTICES
   - Meaningful naming conventions by language
   - Proper function decomposition (7±2 rule)
   - DRY (Don't Repeat Yourself) adherence
   - KISS (Keep It Simple, Stupid) philosophy
   - YAGNI (You Aren't Gonna Need It) enforcement

6. DEPENDENCY INJECTION
   - Constructor injection patterns
   - Interface-based dependencies
   - DI container configuration

7. ERROR HANDLING
   - Exception hierarchy design
   - Fail-fast validation
   - Result types vs exceptions
   - Context manager usage

8. TESTING PATTERNS
   - Arrange-Act-Assert structure
   - Test isolation and independence
   - Mocking external dependencies
   - Test naming conventions

For each code review finding, provide:
- Unique finding ID (CR-001, CR-002, etc.)
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- Category (Complexity, Smell, SOLID, Pattern, Naming)
- Precise location (file, line, function/class)
- Current problematic code snippet
- Improved code with explanation
- Applicable refactoring pattern
- Tool commands for automated verification
- Remediation effort estimate

Format all findings as structured YAML for machine processing and CI/CD integration.
Use radon, pylint, flake8, and mypy for automated verification where applicable.
""",
        "assistant_class": EnhancedCodeReviewAssistant,
        "domain": "quality_assurance",
        "tags": ["code-review", "solid", "complexity", "clean-code", "refactoring"],
        "tools": [
            {"name": "radon", "install": "pip install radon"},
            {"name": "pylint", "install": "pip install pylint"},
            {"name": "flake8", "install": "pip install flake8"},
            {"name": "mypy", "install": "pip install mypy"},
            {"name": "black", "install": "pip install black"},
            {"name": "SonarQube", "url": "https://www.sonarqube.org/"},
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedCodeReviewAssistant()

    print("=" * 60)
    print("Enhanced Code Review Assistant")
    print("=" * 60)
    print(f"\nVersion: {assistant.version}")
    print(f"Standards: {', '.join(assistant.standards)}")

    print("\n" + "=" * 60)
    print("Example Finding:")
    print("=" * 60)

    finding = assistant.generate_finding(
        finding_id="CR-001",
        title="High cyclomatic complexity in process_order function",
        severity="HIGH",
        category="Complexity",
        code_location="app/services/order.py:process_order:45",
        issue_description="Function has cyclomatic complexity of 15 (threshold: 10)",
        metrics={
            "cyclomatic_complexity": 15,
            "cognitive_complexity": 22,
            "lines_of_code": 85,
            "principles_violated": ["SRP - Single Responsibility"],
        },
        current_code="def process_order(order): [85 lines with 15 decision points]",
        improved_code="def process_order(order): validate(order); calculate_price(order); ...",
        explanation="Extract methods for validation, pricing, inventory, payment reduces complexity to 4",
    )

    print(finding.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("Tool Recommendations:")
    print("=" * 60)
    for tool in assistant.get_tool_recommendations():
        print(f"\n{tool['name']}:")
        print(f"  Install: {tool['install']}")
        print(f"  Usage: {tool['usage']}")
        print(f"  Purpose: {tool['description']}")

    print("\n" + "=" * 60)
    print("SOLID Principles Summary:")
    print("=" * 60)
    solid = assistant.solid_principles()
    for principle, details in solid.items():
        print(f"\n{principle.upper().replace('_', ' ')}:")
        print(f"  {details['principle']}")

    print("\n" + "=" * 60)
    print("Dependency Injection Patterns:")
    print("=" * 60)
    di_patterns = assistant.dependency_injection_patterns()
    for pattern, details in di_patterns.items():
        print(f"\n{pattern.replace('_', ' ').title()}:")
        print(f"  {details.get('description', 'See code examples')}")

    print("\n" + "=" * 60)
    print("Error Handling Patterns:")
    print("=" * 60)
    error_patterns = assistant.error_handling_patterns()
    for pattern, details in error_patterns.items():
        print(f"\n{pattern.replace('_', ' ').title()}:")
        print(f"  {details.get('description', 'See code examples')}")

    print("\n" + "=" * 60)
    print("Coverage Summary:")
    print("=" * 60)
    print("- Complexity: Cyclomatic, Cognitive, Halstead metrics")
    print("- SOLID: All 5 principles with bad/good examples")
    print("- Code Smells: 21+ common smells with fixes")
    print("- Naming: Conventions for Python, JavaScript")
    print("- Dependency Injection: Constructor, Setter, Interface patterns")
    print("- Error Handling: Exception hierarchies, fail-fast, Result types")
    print("- Documentation: Google/NumPy docstrings, type hints")
    print("- Testing: AAA structure, isolation, mocking patterns")
    print("- Refactoring: Patterns and tool recommendations")
