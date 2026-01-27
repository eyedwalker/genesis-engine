"""
Enhanced Refactoring Assistant - Martin Fowler's Catalog

This assistant provides comprehensive refactoring guidance covering:
- Martin Fowler's refactoring catalog (Extract Method, Extract Class, Move Method, etc.)
- Effort estimation (LOW/MEDIUM/HIGH)
- Risk assessment (safe vs risky refactorings)
- Automated tools (Rope, Sourcery, jscodeshift)
- Strangler Fig pattern, Branch by Abstraction
- Legacy code handling
- Code smell detection
- Refactoring patterns for major languages

References:
- Refactoring (2nd Edition) by Martin Fowler: https://refactoring.com/
- Working Effectively with Legacy Code by Michael Feathers
- Rope (Python): https://github.com/python-rope/rope
- Sourcery: https://sourcery.ai/
- jscodeshift: https://github.com/facebook/jscodeshift
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class RefactoringFinding(BaseModel):
    """Structured refactoring finding output"""

    finding_id: str = Field(..., description="Unique identifier (REF-001, REF-002, etc.)")
    title: str = Field(..., description="Brief title of the refactoring")
    refactoring_type: str = Field(..., description="Type from Fowler's catalog")
    code_smell: str = Field(default="", description="Code smell detected")

    location: Dict[str, Any] = Field(default_factory=dict, description="File, line, component")
    description: str = Field(..., description="Detailed description of the refactoring")
    motivation: str = Field(..., description="Why this refactoring is needed")

    current_code: str = Field(default="", description="Current code")
    refactored_code: str = Field(..., description="Refactored code")
    mechanics: List[str] = Field(default_factory=list, description="Step-by-step refactoring mechanics")

    risk_assessment: Dict[str, str] = Field(default_factory=dict, description="Risk level and mitigation")
    effort_estimation: Dict[str, str] = Field(default_factory=dict, description="Effort level and time")

    testing_strategy: str = Field(default="", description="How to test the refactoring")
    automated_tools: List[Dict[str, str]] = Field(default_factory=list, description="Tools that can help")
    references: List[str] = Field(default_factory=list, description="References to patterns/books")

    prerequisites: List[str] = Field(default_factory=list, description="What must be in place first")
    follow_up_refactorings: List[str] = Field(default_factory=list, description="Next refactorings to consider")


class EnhancedRefactoringAssistant:
    """
    Enhanced Refactoring Assistant with Martin Fowler's catalog

    Provides guidance on safe, effective refactoring with:
    - Complete refactoring catalog
    - Risk and effort estimation
    - Automated tool recommendations
    - Legacy code strategies
    """

    def __init__(self):
        self.name = "Enhanced Refactoring Assistant"
        self.version = "2.0.0"
        self.catalog_source = "Martin Fowler's Refactoring (2nd Edition)"

    # =========================================================================
    # CODE SMELLS - What to Look For
    # =========================================================================

    @staticmethod
    def detect_code_smells() -> Dict[str, Any]:
        """
        Code smells that indicate need for refactoring

        From Martin Fowler's catalog
        """
        return {
            "bloaters": {
                "long_method": {
                    "description": "Method has too many lines (>20-30 lines)",
                    "threshold": "30+ lines is a strong smell",
                    "refactorings": ["Extract Method", "Replace Temp with Query", "Decompose Conditional"],
                    "example_bad": """
# BAD: Long method doing too much
def process_order(order, customer):
    # Validate customer
    if not customer.email:
        raise ValueError("Email required")
    if not customer.phone:
        raise ValueError("Phone required")
    if customer.credit_score < 600:
        raise ValueError("Credit too low")

    # Calculate discount
    discount = 0
    if customer.is_premium:
        discount = 0.20
    elif customer.order_count > 10:
        discount = 0.15
    elif customer.order_count > 5:
        discount = 0.10

    # Calculate tax
    tax_rate = 0.08
    if customer.state == "CA":
        tax_rate = 0.09
    elif customer.state == "NY":
        tax_rate = 0.085

    # Calculate total
    subtotal = sum(item.price * item.quantity for item in order.items)
    discount_amount = subtotal * discount
    tax_amount = (subtotal - discount_amount) * tax_rate
    total = subtotal - discount_amount + tax_amount

    # Process payment
    payment_gateway = PaymentGateway()
    payment_result = payment_gateway.charge(customer.card, total)
    if not payment_result.success:
        raise PaymentError(payment_result.error)

    # Send confirmation
    email_service = EmailService()
    email_service.send(customer.email, f"Order confirmed: ${total}")

    return total
                    """,
                    "example_good": """
# GOOD: Extracted into focused methods
def process_order(order, customer):
    validate_customer(customer)
    discount = calculate_discount(customer)
    tax = calculate_tax(customer, order, discount)
    total = calculate_total(order, discount, tax)
    charge_payment(customer, total)
    send_confirmation(customer, total)
    return total

def validate_customer(customer):
    if not customer.email:
        raise ValueError("Email required")
    if not customer.phone:
        raise ValueError("Phone required")
    if customer.credit_score < 600:
        raise ValueError("Credit too low")

def calculate_discount(customer):
    if customer.is_premium:
        return 0.20
    elif customer.order_count > 10:
        return 0.15
    elif customer.order_count > 5:
        return 0.10
    return 0

def calculate_tax(customer, order, discount):
    tax_rates = {"CA": 0.09, "NY": 0.085}
    tax_rate = tax_rates.get(customer.state, 0.08)
    subtotal = sum(item.price * item.quantity for item in order.items)
    return (subtotal - subtotal * discount) * tax_rate

def calculate_total(order, discount, tax):
    subtotal = sum(item.price * item.quantity for item in order.items)
    return subtotal - (subtotal * discount) + tax

def charge_payment(customer, total):
    payment_gateway = PaymentGateway()
    result = payment_gateway.charge(customer.card, total)
    if not result.success:
        raise PaymentError(result.error)

def send_confirmation(customer, total):
    email_service = EmailService()
    email_service.send(customer.email, f"Order confirmed: ${total}")
                    """,
                },
                "large_class": {
                    "description": "Class has too many fields/methods",
                    "threshold": ">10 fields or >20 methods",
                    "refactorings": ["Extract Class", "Extract Superclass", "Replace Data Value with Object"],
                    "example_bad": """
# BAD: God class doing everything
class Order:
    def __init__(self):
        # Customer data
        self.customer_name = ""
        self.customer_email = ""
        self.customer_phone = ""
        self.customer_address = ""

        # Order data
        self.items = []
        self.order_date = None
        self.status = "pending"

        # Payment data
        self.card_number = ""
        self.card_expiry = ""
        self.card_cvv = ""

        # Shipping data
        self.shipping_method = ""
        self.tracking_number = ""
        self.shipping_cost = 0

    def validate_customer(self): pass
    def validate_payment(self): pass
    def calculate_discount(self): pass
    def calculate_tax(self): pass
    def process_payment(self): pass
    def send_confirmation_email(self): pass
    def generate_invoice(self): pass
    def schedule_shipping(self): pass
    def track_shipment(self): pass
    def handle_returns(self): pass
    # ... 15+ more methods
                    """,
                    "example_good": """
# GOOD: Separated into focused classes
class Customer:
    def __init__(self, name, email, phone, address):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    def validate(self):
        # Validation logic
        pass

class PaymentInfo:
    def __init__(self, card_number, card_expiry, card_cvv):
        self.card_number = card_number
        self.card_expiry = card_expiry
        self.card_cvv = card_cvv

    def validate(self):
        # Validation logic
        pass

class ShippingInfo:
    def __init__(self, method, cost):
        self.method = method
        self.cost = cost
        self.tracking_number = None

    def track(self):
        # Tracking logic
        pass

class Order:
    def __init__(self, customer, payment_info, shipping_info):
        self.customer = customer
        self.payment_info = payment_info
        self.shipping_info = shipping_info
        self.items = []
        self.order_date = None
        self.status = "pending"

    def add_item(self, item):
        self.items.append(item)

    def calculate_total(self):
        # Calculation logic
        pass

    def process(self):
        self.customer.validate()
        self.payment_info.validate()
        # Process order
        pass
                    """,
                },
                "long_parameter_list": {
                    "description": "Method has too many parameters (>3-4)",
                    "threshold": "4+ parameters",
                    "refactorings": ["Introduce Parameter Object", "Preserve Whole Object"],
                    "example_bad": """
# BAD: Too many parameters
def create_user(first_name, last_name, email, phone,
                address_line1, address_line2, city, state,
                zip_code, country, date_of_birth, gender):
    # Implementation
    pass

# Calling code is a nightmare
create_user("John", "Doe", "john@example.com", "555-1234",
            "123 Main St", "Apt 4", "Springfield", "IL",
            "62701", "USA", "1990-01-01", "M")
                    """,
                    "example_good": """
# GOOD: Parameter object
from dataclasses import dataclass
from datetime import date

@dataclass
class UserProfile:
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date
    gender: str

@dataclass
class Address:
    line1: str
    line2: str
    city: str
    state: str
    zip_code: str
    country: str

def create_user(profile: UserProfile, address: Address):
    # Implementation
    pass

# Calling code is much cleaner
profile = UserProfile(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    phone="555-1234",
    date_of_birth=date(1990, 1, 1),
    gender="M"
)
address = Address(
    line1="123 Main St",
    line2="Apt 4",
    city="Springfield",
    state="IL",
    zip_code="62701",
    country="USA"
)
create_user(profile, address)
                    """,
                },
            },
            "object_orientation_abusers": {
                "switch_statements": {
                    "description": "Same switch/if-else logic duplicated across methods",
                    "refactorings": ["Replace Conditional with Polymorphism", "Replace Type Code with Subclasses"],
                    "example_bad": """
# BAD: Type code with switch statements
class Bird:
    def __init__(self, bird_type):
        self.bird_type = bird_type  # "european", "african", "norwegian_blue"

    def get_speed(self):
        if self.bird_type == "european":
            return 35
        elif self.bird_type == "african":
            return 40
        elif self.bird_type == "norwegian_blue":
            return 24
        else:
            raise ValueError("Unknown bird type")

    def get_plumage(self):
        if self.bird_type == "european":
            return "average"
        elif self.bird_type == "african":
            return "colorful"
        elif self.bird_type == "norwegian_blue":
            return "beautiful"
        else:
            raise ValueError("Unknown bird type")
                    """,
                    "example_good": """
# GOOD: Polymorphism instead of conditionals
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def get_speed(self):
        pass

    @abstractmethod
    def get_plumage(self):
        pass

class EuropeanBird(Bird):
    def get_speed(self):
        return 35

    def get_plumage(self):
        return "average"

class AfricanBird(Bird):
    def get_speed(self):
        return 40

    def get_plumage(self):
        return "colorful"

class NorwegianBlueBird(Bird):
    def get_speed(self):
        return 24

    def get_plumage(self):
        return "beautiful"

# Factory function
def create_bird(bird_type):
    birds = {
        "european": EuropeanBird,
        "african": AfricanBird,
        "norwegian_blue": NorwegianBlueBird,
    }
    bird_class = birds.get(bird_type)
    if not bird_class:
        raise ValueError(f"Unknown bird type: {bird_type}")
    return bird_class()
                    """,
                },
                "temporary_field": {
                    "description": "Field only set in certain circumstances",
                    "refactorings": ["Extract Class", "Introduce Special Case"],
                    "example_bad": """
# BAD: Optional fields that are sometimes null
class Order:
    def __init__(self):
        self.items = []
        self.customer = None
        self.gift_message = None  # Only for gifts
        self.gift_wrapping = None  # Only for gifts
        self.corporate_po_number = None  # Only for B2B
        self.tax_exempt_id = None  # Only for tax-exempt

    def calculate_total(self):
        total = sum(item.price for item in self.items)
        if self.gift_wrapping:
            total += self.gift_wrapping.cost
        # Confusing: which fields are actually used?
        return total
                    """,
                    "example_good": """
# GOOD: Extract optional aspects to separate classes
class Order:
    def __init__(self, items, customer):
        self.items = items
        self.customer = customer
        self.gift_options = None
        self.business_options = None

    def add_gift_options(self, message, wrapping):
        self.gift_options = GiftOptions(message, wrapping)

    def add_business_options(self, po_number, tax_exempt_id):
        self.business_options = BusinessOptions(po_number, tax_exempt_id)

    def calculate_total(self):
        total = sum(item.price for item in self.items)
        if self.gift_options:
            total += self.gift_options.calculate_cost()
        return total

class GiftOptions:
    def __init__(self, message, wrapping):
        self.message = message
        self.wrapping = wrapping

    def calculate_cost(self):
        return self.wrapping.cost if self.wrapping else 0

class BusinessOptions:
    def __init__(self, po_number, tax_exempt_id):
        self.po_number = po_number
        self.tax_exempt_id = tax_exempt_id
                    """,
                },
            },
            "change_preventers": {
                "divergent_change": {
                    "description": "One class changes for multiple different reasons",
                    "violation": "Single Responsibility Principle",
                    "refactorings": ["Extract Class", "Extract Module"],
                    "example": "Database class that changes when adding new storage engines AND when changing connection pooling",
                },
                "shotgun_surgery": {
                    "description": "One change requires modifying many classes",
                    "refactorings": ["Move Method", "Move Field", "Inline Class"],
                    "example": "Adding a new field requires changes in 20 different classes",
                },
            },
            "dispensables": {
                "comments": {
                    "description": "Comments used to explain bad code instead of improving it",
                    "refactorings": ["Extract Method", "Rename Variable", "Introduce Assertion"],
                    "example_bad": """
# BAD: Comment explaining complex logic
# Calculate discount: premium customers get 20%,
# customers with 10+ orders get 15%,
# customers with 5+ orders get 10%
if customer.is_premium:
    d = 0.20
elif customer.order_count > 10:
    d = 0.15
elif customer.order_count > 5:
    d = 0.10
else:
    d = 0
                    """,
                    "example_good": """
# GOOD: Self-documenting code
discount = calculate_customer_discount(customer)

def calculate_customer_discount(customer):
    if customer.is_premium:
        return 0.20
    if customer.order_count > 10:
        return 0.15
    if customer.order_count > 5:
        return 0.10
    return 0
                    """,
                },
                "dead_code": {
                    "description": "Code that's never executed",
                    "refactorings": ["Remove Dead Code"],
                    "detection": "Use coverage tools to find unused code",
                },
                "speculative_generality": {
                    "description": "Code designed for future needs that may never come",
                    "refactorings": ["Collapse Hierarchy", "Inline Class", "Remove Parameter"],
                    "example_bad": """
# BAD: Over-engineered for hypothetical future needs
class AbstractDataSourceFactory(ABC):
    @abstractmethod
    def create_data_source(self):
        pass

class MySQLDataSourceFactory(AbstractDataSourceFactory):
    def create_data_source(self):
        return MySQLDataSource()

# Only MySQL is ever used, no other databases planned
                    """,
                    "example_good": """
# GOOD: Simple solution for actual needs
def get_data_source():
    return MySQLDataSource()
                    """,
                },
            },
        }

    # =========================================================================
    # FOWLER'S REFACTORING CATALOG - Core Refactorings
    # =========================================================================

    @staticmethod
    def extract_method_refactoring() -> Dict[str, Any]:
        """
        Extract Method - Most common refactoring

        Turn a code fragment into a method with a descriptive name.
        """
        return {
            "name": "Extract Method",
            "motivation": "Long methods are hard to understand. Extracting fragments into well-named methods improves readability.",
            "risk": "LOW",
            "effort": "LOW",
            "mechanics": [
                "1. Create a new method with a name that describes what it does (not how)",
                "2. Copy the extracted code into the new method",
                "3. Look for local variables used in the extracted code",
                "4. Pass local variables as parameters if they're only read",
                "5. Return any modified local variables",
                "6. Replace extracted code with call to new method",
                "7. Test",
            ],
            "example_bad": """
# BAD: Long method with fragments doing specific tasks
def print_owing(invoice):
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

    outstanding = 0
    for order in invoice.orders:
        outstanding += order.amount

    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")
            """,
            "example_good": """
# GOOD: Extracted into focused methods
def print_owing(invoice):
    print_banner()
    outstanding = calculate_outstanding(invoice)
    print_details(invoice, outstanding)

def print_banner():
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

def calculate_outstanding(invoice):
    return sum(order.amount for order in invoice.orders)

def print_details(invoice, outstanding):
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")
            """,
            "automated_tools": [
                {
                    "name": "PyCharm",
                    "command": "Ctrl+Alt+M (Windows/Linux) or Cmd+Alt+M (Mac)",
                    "description": "Extract Method refactoring",
                },
                {
                    "name": "VS Code with Pylance",
                    "command": "Select code → Right-click → Extract Method",
                    "description": "Built-in refactoring",
                },
                {
                    "name": "Rope",
                    "command": "from rope.refactor.extract import ExtractMethod",
                    "description": "Python refactoring library",
                },
            ],
        }

    @staticmethod
    def extract_class_refactoring() -> Dict[str, Any]:
        """
        Extract Class - Break up large classes

        A class is doing work that should be done by two or more classes.
        """
        return {
            "name": "Extract Class",
            "motivation": "A class with many responsibilities is hard to understand. Extract cohesive subsets into separate classes.",
            "risk": "MEDIUM",
            "effort": "MEDIUM",
            "mechanics": [
                "1. Decide how to split the responsibilities of the class",
                "2. Create a new class to express the split-off responsibilities",
                "3. Make a link from the old to the new class",
                "4. Use Move Field on each field you want to move",
                "5. Use Move Method to move methods",
                "6. Review and reduce interfaces",
                "7. Decide whether to expose the new class publicly",
            ],
            "example_bad": """
# BAD: Person class doing too much
class Person:
    def __init__(self, name, office_phone, office_ext):
        self.name = name
        self.office_phone = office_phone
        self.office_extension = office_ext

    def get_telephone_number(self):
        return f"{self.office_phone} x{self.office_extension}"

    def get_office_phone(self):
        return self.office_phone

    def set_office_phone(self, phone):
        self.office_phone = phone

    def get_office_extension(self):
        return self.office_extension

    def set_office_extension(self, ext):
        self.office_extension = ext
            """,
            "example_good": """
# GOOD: Extracted TelephoneNumber class
class Person:
    def __init__(self, name):
        self.name = name
        self.office_telephone = TelephoneNumber()

    def get_telephone_number(self):
        return self.office_telephone.get_telephone_number()

    def get_office_telephone(self):
        return self.office_telephone

class TelephoneNumber:
    def __init__(self, phone="", extension=""):
        self.phone = phone
        self.extension = extension

    def get_telephone_number(self):
        return f"{self.phone} x{self.extension}"

    def get_phone(self):
        return self.phone

    def set_phone(self, phone):
        self.phone = phone

    def get_extension(self):
        return self.extension

    def set_extension(self, extension):
        self.extension = extension
            """,
            "when_to_use": [
                "A class has many fields/methods",
                "A subset of fields/methods always change together",
                "A subset could be useful in other contexts",
                "You find yourself passing many parameters between methods",
            ],
        }

    @staticmethod
    def move_method_refactoring() -> Dict[str, Any]:
        """
        Move Method - Move method to the class that uses it most

        A method is used more in another class than in its own class.
        """
        return {
            "name": "Move Method",
            "motivation": "Methods should be in the class that uses their data most. This reduces coupling.",
            "risk": "LOW to MEDIUM",
            "effort": "LOW",
            "mechanics": [
                "1. Examine all features used by the source method that are defined on the source class",
                "2. Check if method is polymorphic (if so, may need different approach)",
                "3. Copy the method to the target class, adjust it to fit",
                "4. Determine reference from source to target",
                "5. Turn source method into delegating method",
                "6. Test",
                "7. Remove source method or keep as delegating method",
            ],
            "example_bad": """
# BAD: Method in wrong class
class Account:
    def __init__(self, account_type):
        self.account_type = account_type
        self.days_overdrawn = 0

    def get_overdraft_charge(self):
        # This method uses account_type more than Account's own data
        if self.account_type.is_premium():
            result = 10.0
            if self.days_overdrawn > 7:
                result += (self.days_overdrawn - 7) * 0.85
            return result
        else:
            return self.days_overdrawn * 1.75

class AccountType:
    def __init__(self, name, premium=False):
        self.name = name
        self.premium = premium

    def is_premium(self):
        return self.premium
            """,
            "example_good": """
# GOOD: Method moved to class that uses it most
class Account:
    def __init__(self, account_type):
        self.account_type = account_type
        self.days_overdrawn = 0

    def get_overdraft_charge(self):
        # Delegate to account_type
        return self.account_type.overdraft_charge(self.days_overdrawn)

class AccountType:
    def __init__(self, name, premium=False):
        self.name = name
        self.premium = premium

    def is_premium(self):
        return self.premium

    def overdraft_charge(self, days_overdrawn):
        # Method is now in the right place
        if self.is_premium():
            result = 10.0
            if days_overdrawn > 7:
                result += (days_overdrawn - 7) * 0.85
            return result
        else:
            return days_overdrawn * 1.75
            """,
        }

    @staticmethod
    def replace_temp_with_query() -> Dict[str, Any]:
        """
        Replace Temp with Query - Extract temporary variables into methods

        Temporary variables encourage long methods. Extract them into query methods.
        """
        return {
            "name": "Replace Temp with Query",
            "motivation": "Temps are often problematic. They're only visible in their own routine, encouraging long methods. Replacing with a method makes it available to other methods.",
            "risk": "LOW",
            "effort": "LOW",
            "mechanics": [
                "1. Check that the temp is assigned once and only once",
                "2. Extract the right-hand side of assignment into a method",
                "3. Replace all references to temp with calls to the new method",
                "4. Test after each replacement",
                "5. Remove the temp declaration and assignment",
            ],
            "example_bad": """
# BAD: Temporary variable
def calculate_price(order):
    base_price = order.quantity * order.item_price
    discount_factor = 0.98 if base_price > 1000 else 0.95
    return base_price * discount_factor
            """,
            "example_good": """
# GOOD: Extracted into query methods
def calculate_price(order):
    return base_price(order) * discount_factor(order)

def base_price(order):
    return order.quantity * order.item_price

def discount_factor(order):
    return 0.98 if base_price(order) > 1000 else 0.95
            """,
            "benefits": [
                "Can reuse extracted methods elsewhere",
                "Easier to extract larger methods",
                "Forces you to think about visibility and dependencies",
            ],
        }

    @staticmethod
    def introduce_parameter_object() -> Dict[str, Any]:
        """
        Introduce Parameter Object - Group parameters into object

        Replace a group of parameters with an object.
        """
        return {
            "name": "Introduce Parameter Object",
            "motivation": "Groups of parameters that naturally go together should be an object. This reduces parameter lists and reveals data clumps.",
            "risk": "LOW",
            "effort": "MEDIUM",
            "mechanics": [
                "1. Create a new class to represent the group of parameters",
                "2. Make it immutable (use @dataclass with frozen=True)",
                "3. Test",
                "4. Use Change Function Declaration to add parameter for the new object",
                "5. Test",
                "6. Adjust each caller to pass the new object",
                "7. For each parameter, remove it and adjust method body",
                "8. Test after removing each parameter",
            ],
            "example_bad": """
# BAD: Many related parameters
def amount_invoiced(start_date, end_date):
    # Calculate invoiced amount
    pass

def amount_received(start_date, end_date):
    # Calculate received amount
    pass

def amount_overdue(start_date, end_date):
    # Calculate overdue amount
    pass

# Calling code
start = date(2023, 1, 1)
end = date(2023, 12, 31)
invoiced = amount_invoiced(start, end)
received = amount_received(start, end)
overdue = amount_overdue(start, end)
            """,
            "example_good": """
# GOOD: Parameter object
from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def contains(self, date):
        return self.start <= date <= self.end

    def days(self):
        return (self.end - self.start).days

def amount_invoiced(date_range: DateRange):
    # Calculate invoiced amount
    pass

def amount_received(date_range: DateRange):
    # Calculate received amount
    pass

def amount_overdue(date_range: DateRange):
    # Calculate overdue amount
    pass

# Calling code - much cleaner
date_range = DateRange(date(2023, 1, 1), date(2023, 12, 31))
invoiced = amount_invoiced(date_range)
received = amount_received(date_range)
overdue = amount_overdue(date_range)

# DateRange can now have its own behavior
if date_range.days() > 365:
    print("Range exceeds one year")
            """,
        }

    # =========================================================================
    # LEGACY CODE STRATEGIES
    # =========================================================================

    @staticmethod
    def legacy_code_strategies() -> Dict[str, Any]:
        """
        Strategies for working with legacy code

        Based on Michael Feathers' "Working Effectively with Legacy Code"
        """
        return {
            "characterization_tests": {
                "description": "Write tests that characterize current behavior before changing",
                "process": [
                    "1. Identify the change point in the code",
                    "2. Find test points (places to write tests)",
                    "3. Break dependencies to get code under test",
                    "4. Write tests to lock down current behavior",
                    "5. Make changes",
                    "6. Refactor to clean up",
                ],
                "example": """
# Characterization test - captures current behavior
def test_discount_calculation_current_behavior():
    # Even if we don't know if this is correct,
    # we document what it currently does
    customer = Customer(order_count=12, is_premium=False)
    discount = calculate_discount(customer)
    assert discount == 0.15  # This is what it does now

    customer_premium = Customer(order_count=3, is_premium=True)
    discount_premium = calculate_discount(customer_premium)
    assert discount_premium == 0.20  # This is what it does now

    # Now we can safely refactor knowing tests will catch changes
                """,
            },
            "strangler_fig_pattern": {
                "description": "Gradually replace old system by intercepting calls and redirecting to new system",
                "phases": [
                    "1. Create facade/interface around legacy code",
                    "2. Implement new functionality alongside old",
                    "3. Route traffic to new implementation incrementally",
                    "4. Monitor and verify new implementation",
                    "5. Remove old implementation once fully replaced",
                ],
                "example": """
# Strangler Fig Pattern
class LegacyOrderService:
    def create_order(self, customer, items):
        # Old monolithic implementation
        pass

class NewOrderService:
    def create_order(self, customer, items):
        # New clean implementation
        pass

class OrderServiceFacade:
    def __init__(self):
        self.legacy_service = LegacyOrderService()
        self.new_service = NewOrderService()
        self.new_service_enabled = False  # Feature flag

    def create_order(self, customer, items):
        # Route based on feature flag or customer segment
        if self.new_service_enabled or self._should_use_new_service(customer):
            return self.new_service.create_order(customer, items)
        else:
            return self.legacy_service.create_order(customer, items)

    def _should_use_new_service(self, customer):
        # Gradual rollout: 10% of customers
        return hash(customer.id) % 10 == 0

# Usage stays the same
facade = OrderServiceFacade()
facade.create_order(customer, items)

# Gradually increase percentage until 100%, then remove legacy
                """,
                "benefits": [
                    "Lower risk - can rollback easily",
                    "Continuous delivery - no big-bang migration",
                    "Can test in production with real traffic",
                    "Learn from mistakes before full rollout",
                ],
            },
            "branch_by_abstraction": {
                "description": "Create abstraction layer to allow parallel implementations",
                "steps": [
                    "1. Create abstraction interface over code to change",
                    "2. Change clients to use abstraction",
                    "3. Create new implementation of abstraction",
                    "4. Update abstraction to delegate to new implementation",
                    "5. Remove old implementation",
                    "6. Remove abstraction if no longer needed",
                ],
                "example": """
# Branch by Abstraction
from abc import ABC, abstractmethod

# Step 1: Create abstraction
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount, card):
        pass

# Step 2: Wrap legacy code
class LegacyPaymentGateway(PaymentGateway):
    def charge(self, amount, card):
        # Wrap old implementation
        return legacy_payment_api.process(amount, card)

# Step 3: Create new implementation
class ModernPaymentGateway(PaymentGateway):
    def charge(self, amount, card):
        # New clean implementation
        return stripe.Charge.create(amount=amount, source=card)

# Step 4: Switch implementations
class PaymentService:
    def __init__(self):
        # Can switch between implementations
        self.gateway = ModernPaymentGateway()  # or LegacyPaymentGateway()

    def process_payment(self, amount, card):
        return self.gateway.charge(amount, card)

# Step 5 (later): Remove legacy when fully migrated
# Step 6 (even later): If only one implementation remains,
#                       can remove abstraction and use concrete class
                """,
            },
            "seam_model": {
                "description": "Find seams (places to alter behavior without editing) for testing",
                "types": [
                    "Object Seam: Use polymorphism to change behavior",
                    "Preprocessing Seam: Use build/import system",
                    "Link Seam: Replace at link time (less common in Python)",
                ],
                "example": """
# Seam for testing
class OrderProcessor:
    def __init__(self, payment_gateway=None):
        # Seam: can inject test double
        self.payment_gateway = payment_gateway or RealPaymentGateway()

    def process(self, order):
        result = self.payment_gateway.charge(order.total, order.card)
        if result.success:
            order.status = "paid"
        return result

# Production use
processor = OrderProcessor()

# Test use
class FakePaymentGateway:
    def charge(self, amount, card):
        return PaymentResult(success=True, transaction_id="TEST123")

processor = OrderProcessor(payment_gateway=FakePaymentGateway())
                """,
            },
            "sprout_method_sprout_class": {
                "description": "Add new functionality as separate method/class instead of modifying legacy code",
                "sprout_method": """
# Sprout Method: Add new logic as separate method
class LegacyOrderProcessor:
    def process_order(self, order):
        # 200 lines of legacy code we don't want to touch
        # ...

        # Sprout: new functionality as separate, testable method
        self._apply_new_discount_rules(order)

        # More legacy code
        # ...

    def _apply_new_discount_rules(self, order):
        # New, clean, tested code
        if order.customer.loyalty_points > 1000:
            order.discount += 0.05
        if order.total > 500:
            order.discount += 0.10
                """,
                "sprout_class": """
# Sprout Class: Add new functionality as separate class
class LegacyReportGenerator:
    def generate_report(self, data):
        # 300 lines of legacy spaghetti code
        # ...

        # Sprout: delegate to new class
        enhanced_data = ReportEnhancer().enhance(data)

        # Use enhanced data in legacy code
        # ...

# New, clean, testable class
class ReportEnhancer:
    def enhance(self, data):
        # New functionality in isolation
        data['summary'] = self._calculate_summary(data)
        data['trends'] = self._analyze_trends(data)
        return data

    def _calculate_summary(self, data):
        # Tested separately
        pass

    def _analyze_trends(self, data):
        # Tested separately
        pass
                """,
            },
            "golden_master_testing": {
                "description": "Capture output of legacy code and use as test oracle",
                "use_case": "When you can't understand the code but need to preserve behavior",
                "example": """
# Golden Master Testing
import json

def test_legacy_report_output():
    # Run legacy code with known inputs
    input_data = load_test_data()
    actual_output = legacy_report_generator(input_data)

    # Compare with "golden master" - saved output from previous run
    with open('golden_master.json', 'r') as f:
        expected_output = json.load(f)

    assert actual_output == expected_output
    # If test fails, manually verify which is correct:
    # the new output or the golden master

# To create golden master:
# 1. Run code with known inputs
# 2. Manually verify output is correct
# 3. Save as golden master
# 4. Use for regression testing during refactoring
                """,
            },
        }

    # =========================================================================
    # AUTOMATED REFACTORING TOOLS
    # =========================================================================

    @staticmethod
    def automated_tools() -> Dict[str, Any]:
        """
        Automated refactoring tools for different languages
        """
        return {
            "python": {
                "rope": {
                    "description": "Python refactoring library",
                    "install": "pip install rope",
                    "capabilities": [
                        "Extract method/variable",
                        "Inline method/variable",
                        "Move method/attribute",
                        "Rename",
                        "Change signature",
                        "Organize imports",
                    ],
                    "example": """
# Using Rope programmatically
from rope.base.project import Project
from rope.refactor.extract import ExtractMethod

project = Project('.')
resource = project.root.get_file('module.py')

# Extract method refactoring
extractor = ExtractMethod(project, resource, start_offset, end_offset)
changes = extractor.get_changes('new_method_name')
project.do(changes)
                    """,
                },
                "sourcery": {
                    "description": "AI-powered Python refactoring",
                    "install": "pip install sourcery-cli",
                    "capabilities": [
                        "Suggest refactorings inline (IDE plugin)",
                        "Convert to list comprehension",
                        "Merge nested ifs",
                        "Remove unreachable code",
                        "Extract duplicate code",
                    ],
                    "example": """
# Sourcery detects and suggests refactorings automatically

# Before (Sourcery suggests: merge-nested-ifs)
if x > 0:
    if y > 0:
        return x + y

# After (Sourcery auto-refactors)
if x > 0 and y > 0:
    return x + y
                    """,
                },
                "pycharm": {
                    "description": "Full-featured IDE with refactoring support",
                    "refactorings": [
                        "Extract Method: Ctrl+Alt+M",
                        "Extract Variable: Ctrl+Alt+V",
                        "Extract Constant: Ctrl+Alt+C",
                        "Inline: Ctrl+Alt+N",
                        "Rename: Shift+F6",
                        "Change Signature: Ctrl+F6",
                        "Move: F6",
                        "Safe Delete: Alt+Delete",
                    ],
                },
            },
            "javascript": {
                "jscodeshift": {
                    "description": "JavaScript/TypeScript codemod tool",
                    "install": "npm install -g jscodeshift",
                    "capabilities": [
                        "Large-scale refactorings across many files",
                        "Transform AST programmatically",
                        "Custom refactoring scripts",
                    ],
                    "example": """
// jscodeshift example: Convert var to const/let
module.exports = function(fileInfo, api) {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Find all var declarations
  root.find(j.VariableDeclaration, {kind: 'var'})
    .forEach(path => {
      const node = path.node;
      // Convert to const if not reassigned, otherwise let
      node.kind = isReassigned(node) ? 'let' : 'const';
    });

  return root.toSource();
};

// Run: jscodeshift -t transform.js src/**/*.js
                    """,
                },
                "ts-morph": {
                    "description": "TypeScript refactoring library",
                    "install": "npm install ts-morph",
                    "example": """
// ts-morph example: Refactor TypeScript
import { Project } from "ts-morph";

const project = new Project();
project.addSourceFilesAtPaths("src/**/*.ts");

// Find all classes
for (const sourceFile of project.getSourceFiles()) {
  for (const cls of sourceFile.getClasses()) {
    // Rename method
    const method = cls.getMethod("oldName");
    if (method) {
      method.rename("newName");
    }
  }
}

await project.save();
                    """,
                },
            },
            "java": {
                "intellij_idea": {
                    "description": "Industry-standard Java IDE",
                    "refactorings": [
                        "Extract Method",
                        "Extract Interface",
                        "Pull Members Up/Down",
                        "Use Interface Where Possible",
                        "Invert Boolean",
                        "Type Migration",
                    ],
                },
                "eclipse": {
                    "description": "Open-source Java IDE",
                    "refactorings": [
                        "Extract Method/Variable/Constant",
                        "Inline",
                        "Move/Rename",
                        "Change Method Signature",
                        "Extract Interface/Superclass",
                    ],
                },
            },
        }

    # =========================================================================
    # RISK ASSESSMENT AND EFFORT ESTIMATION
    # =========================================================================

    @staticmethod
    def risk_and_effort_guidance() -> Dict[str, Any]:
        """
        Guidelines for assessing risk and effort of refactorings
        """
        return {
            "risk_levels": {
                "low_risk": {
                    "characteristics": [
                        "Local changes (within one method/class)",
                        "No changes to public interfaces",
                        "Automated refactoring tool available",
                        "Good test coverage exists",
                    ],
                    "examples": [
                        "Extract Method",
                        "Rename Variable (local)",
                        "Extract Variable",
                        "Inline Temp",
                    ],
                    "mitigation": "Just do it with tests",
                },
                "medium_risk": {
                    "characteristics": [
                        "Changes cross class boundaries",
                        "Public interface changes",
                        "Some test coverage",
                        "Affects multiple callers",
                    ],
                    "examples": [
                        "Extract Class",
                        "Move Method",
                        "Rename Method (public)",
                        "Change Function Signature",
                    ],
                    "mitigation": [
                        "Add characterization tests first",
                        "Use IDE refactoring tools",
                        "Refactor in small steps with tests between",
                        "Consider deprecation period for public APIs",
                    ],
                },
                "high_risk": {
                    "characteristics": [
                        "Major architectural change",
                        "Affects many callers across codebase",
                        "Little or no test coverage",
                        "Changes to widely-used public APIs",
                    ],
                    "examples": [
                        "Replace Inheritance with Delegation",
                        "Extract Interface",
                        "Split Phase (major)",
                        "Replace Conditional with Polymorphism (large)",
                    ],
                    "mitigation": [
                        "Add extensive tests before starting",
                        "Use Branch by Abstraction or Strangler Fig",
                        "Plan for gradual rollout with feature flags",
                        "Pair program or get code review",
                        "Have rollback plan",
                    ],
                },
            },
            "effort_estimation": {
                "low_effort": {
                    "time": "< 1 hour",
                    "examples": [
                        "Rename Variable (IDE refactoring)",
                        "Extract Method (single use)",
                        "Inline Temp",
                        "Replace Magic Number with Named Constant",
                    ],
                },
                "medium_effort": {
                    "time": "1-4 hours",
                    "examples": [
                        "Extract Class",
                        "Move Method (multiple callers)",
                        "Replace Conditional with Polymorphism (small)",
                        "Introduce Parameter Object",
                    ],
                },
                "high_effort": {
                    "time": "1+ days",
                    "examples": [
                        "Replace Inheritance with Delegation (large hierarchy)",
                        "Extract Superclass/Subclass (major)",
                        "Split Module",
                        "Replace Conditional with Polymorphism (large, many cases)",
                    ],
                },
            },
            "when_not_to_refactor": [
                "Code that works and will never be touched again",
                "Code about to be deleted",
                "When you don't have tests and can't add them",
                "When deadline is tomorrow (but add to tech debt backlog)",
                "When you don't understand what the code does",
                "When simpler to rewrite than refactor",
            ],
        }

    # =========================================================================
    # REFACTORING WORKFLOW AND BEST PRACTICES
    # =========================================================================

    @staticmethod
    def refactoring_workflow() -> Dict[str, Any]:
        """
        Best practices for safe, effective refactoring
        """
        return {
            "the_refactoring_workflow": {
                "step_1_get_tests_in_place": {
                    "goal": "Ensure you can detect regressions",
                    "actions": [
                        "Add unit tests if none exist",
                        "Add integration tests for critical paths",
                        "Add characterization tests for legacy code",
                        "Aim for 80%+ coverage of code you'll change",
                    ],
                },
                "step_2_run_tests": {
                    "goal": "Establish baseline - all tests pass",
                    "actions": [
                        "Run full test suite",
                        "Fix any failing tests before refactoring",
                        "Note test execution time",
                    ],
                },
                "step_3_make_small_change": {
                    "goal": "Refactor in tiny, safe steps",
                    "actions": [
                        "Pick the smallest refactoring possible",
                        "Use IDE refactoring tools when available",
                        "Change only one thing at a time",
                    ],
                },
                "step_4_run_tests_again": {
                    "goal": "Verify change didn't break anything",
                    "actions": [
                        "Run full test suite immediately",
                        "If tests fail, undo change and try smaller step",
                        "Never move forward with failing tests",
                    ],
                },
                "step_5_commit": {
                    "goal": "Create checkpoint for possible rollback",
                    "actions": [
                        "Commit after each successful refactoring",
                        "Use descriptive commit message",
                        "Push to backup/CI frequently",
                    ],
                },
                "step_6_repeat": {
                    "goal": "Continue until refactoring complete",
                    "actions": [
                        "Repeat steps 3-5 until done",
                        "Take breaks during long refactorings",
                        "Keep refactoring sessions short (< 2 hours)",
                    ],
                },
            },
            "two_hats": {
                "description": "Kent Beck's Two Hats metaphor",
                "adding_functionality_hat": [
                    "Adding new features",
                    "Should not change existing code (except to call new code)",
                    "Add new tests",
                ],
                "refactoring_hat": [
                    "Restructuring existing code",
                    "Should not add functionality",
                    "Should not add tests (except characterization tests)",
                ],
                "rule": "Never wear both hats at once! Switch hats, don't mix.",
            },
            "refactoring_with_feature_development": {
                "preparatory_refactoring": {
                    "when": "Before adding feature",
                    "goal": "Make feature easy to add",
                    "example": "Extract method to prepare for adding similar functionality",
                },
                "comprehension_refactoring": {
                    "when": "While reading code",
                    "goal": "Make code easier to understand",
                    "example": "Rename variables, extract methods to clarify intent",
                },
                "litter_pickup_refactoring": {
                    "when": "After adding feature",
                    "goal": "Leave code cleaner than you found it",
                    "example": "Remove duplication introduced by feature",
                },
                "planned_refactoring": {
                    "when": "Dedicated time",
                    "goal": "Address accumulated tech debt",
                    "example": "Break up god class, extract modules",
                },
            },
            "code_review_checklist": [
                "Are refactorings atomic (one change per commit)?",
                "Do all tests still pass?",
                "Is behavior unchanged (unless explicitly noted)?",
                "Are names more descriptive after refactoring?",
                "Is code easier to understand?",
                "Is duplication reduced?",
                "Are methods shorter and more focused?",
                "Are classes more cohesive?",
                "Is coupling reduced?",
            ],
        }

    # =========================================================================
    # OUTPUT METHODS
    # =========================================================================

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        refactoring_type: str,
        code_smell: str,
        description: str,
        current_code: str,
        refactored_code: str,
        risk_level: str,
        effort_level: str,
    ) -> RefactoringFinding:
        """
        Generate a structured refactoring finding

        Args:
            finding_id: Unique ID (REF-001)
            title: Brief title
            refactoring_type: Type from Fowler's catalog
            code_smell: Code smell detected
            description: What needs refactoring
            current_code: Current code
            refactored_code: Refactored code
            risk_level: LOW/MEDIUM/HIGH
            effort_level: LOW/MEDIUM/HIGH
        """
        return RefactoringFinding(
            finding_id=finding_id,
            title=title,
            refactoring_type=refactoring_type,
            code_smell=code_smell,
            location={"file": "to_be_determined"},
            description=description,
            motivation=self._get_motivation(refactoring_type),
            current_code=current_code,
            refactored_code=refactored_code,
            mechanics=self._get_mechanics(refactoring_type),
            risk_assessment={
                "level": risk_level,
                "mitigation": self._get_risk_mitigation(risk_level),
            },
            effort_estimation={
                "level": effort_level,
                "time_estimate": self._get_time_estimate(effort_level),
            },
            testing_strategy=self._get_testing_strategy(),
            automated_tools=self._get_tools(refactoring_type),
            references=[
                "Refactoring (2nd Edition) by Martin Fowler",
                "https://refactoring.com/catalog/",
            ],
            prerequisites=["Tests in place", "Code compiles", "Baseline established"],
            follow_up_refactorings=[],
        )

    @staticmethod
    def _get_motivation(refactoring_type: str) -> str:
        motivations = {
            "Extract Method": "Long methods are hard to understand. Extract fragments into well-named methods.",
            "Extract Class": "A class with many responsibilities should be split.",
            "Move Method": "Methods should be in the class that uses their data most.",
        }
        return motivations.get(refactoring_type, "Improve code structure and maintainability")

    @staticmethod
    def _get_mechanics(refactoring_type: str) -> List[str]:
        return [
            "1. Ensure tests are in place",
            "2. Make small, incremental changes",
            "3. Run tests after each change",
            "4. Commit after successful test run",
            "5. Repeat until refactoring complete",
        ]

    @staticmethod
    def _get_risk_mitigation(risk_level: str) -> str:
        mitigations = {
            "LOW": "Use IDE refactoring tools, run tests after change",
            "MEDIUM": "Add characterization tests first, refactor in small steps",
            "HIGH": "Extensive testing, Branch by Abstraction, gradual rollout with feature flags",
        }
        return mitigations.get(risk_level, "Use caution and extensive testing")

    @staticmethod
    def _get_time_estimate(effort_level: str) -> str:
        estimates = {
            "LOW": "< 1 hour",
            "MEDIUM": "1-4 hours",
            "HIGH": "1+ days",
        }
        return estimates.get(effort_level, "Unknown")

    @staticmethod
    def _get_testing_strategy() -> str:
        return """
1. Run existing tests to establish baseline
2. Add characterization tests if needed
3. Make refactoring change
4. Run tests immediately
5. If tests fail, revert and try smaller step
6. Commit when tests pass
        """

    @staticmethod
    def _get_tools(refactoring_type: str) -> List[Dict[str, str]]:
        return [
            {
                "name": "PyCharm",
                "description": "Full-featured IDE with refactoring support",
                "shortcut": "Ctrl+Alt+Shift+T (Refactor This menu)",
            },
            {
                "name": "Rope",
                "command": "pip install rope",
                "description": "Python refactoring library",
            },
            {
                "name": "Sourcery",
                "command": "pip install sourcery-cli",
                "description": "AI-powered refactoring suggestions",
            },
        ]


def create_enhanced_refactoring_assistant():
    """Factory function to create enhanced refactoring assistant"""
    return {
        "name": "Enhanced Refactoring Assistant",
        "version": "2.0.0",
        "system_prompt": """You are an expert code refactoring assistant with deep knowledge of:

- Martin Fowler's Refactoring catalog (Extract Method, Extract Class, Move Method, etc.)
- Code smell detection (Long Method, Large Class, Data Clumps, etc.)
- Risk assessment (LOW/MEDIUM/HIGH for each refactoring)
- Effort estimation (time and complexity)
- Legacy code strategies (Strangler Fig, Branch by Abstraction, Characterization Tests)
- Automated refactoring tools (Rope, Sourcery, jscodeshift, IDE tools)
- Safe refactoring workflow (test, change, test, commit)
- Michael Feathers' legacy code techniques

Your role is to:
1. Identify code smells and recommend appropriate refactorings
2. Provide step-by-step mechanics for each refactoring
3. Assess risk level (LOW/MEDIUM/HIGH) and provide mitigation strategies
4. Estimate effort (LOW/MEDIUM/HIGH) with time ranges
5. Show before/after code examples
6. Recommend automated tools that can help
7. Provide testing strategies for safe refactoring
8. Suggest follow-up refactorings

Always provide:
- Specific refactoring name from Fowler's catalog
- Code smell being addressed
- Current code (bad example)
- Refactored code (good example)
- Step-by-step mechanics
- Risk assessment with mitigation
- Effort estimation
- Testing strategy
- Tool recommendations

Remember:
- Refactor in small steps
- Test after each change
- Never refactor and add features simultaneously (Two Hats)
- Use IDE refactoring tools when available
- Commit frequently
- For legacy code, add characterization tests first

Format findings as structured YAML with all required fields.
""",
        "assistant_class": EnhancedRefactoringAssistant,
        "domain": "quality_assurance",
        "tags": ["refactoring", "code-quality", "legacy-code", "fowler", "clean-code"],
    }


if __name__ == "__main__":
    # Example usage
    assistant = EnhancedRefactoringAssistant()

    print("=" * 80)
    print("Enhanced Refactoring Assistant - Martin Fowler's Catalog")
    print("=" * 80)
    print(f"\nVersion: {assistant.version}")
    print(f"Catalog: {assistant.catalog_source}")

    print("\n" + "=" * 80)
    print("Example Finding:")
    print("=" * 80)

    finding = assistant.generate_finding(
        finding_id="REF-001",
        title="Extract method to reduce long method complexity",
        refactoring_type="Extract Method",
        code_smell="Long Method",
        description="The process_order method is 150 lines long and does too many things",
        current_code="""
def process_order(order):
    # 150 lines of validation, calculation, payment, email logic
    pass
        """,
        refactored_code="""
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    process_payment(order, total)
    send_confirmation(order)
        """,
        risk_level="LOW",
        effort_level="LOW",
    )

    print(finding.model_dump_json(indent=2))

    print("\n" + "=" * 80)
    print("Coverage Summary:")
    print("=" * 80)
    print("✅ Martin Fowler's Refactoring Catalog - 10+ core refactorings")
    print("✅ Code Smells - Bloaters, OO Abusers, Change Preventers, Dispensables")
    print("✅ Risk Assessment - LOW/MEDIUM/HIGH with mitigation strategies")
    print("✅ Effort Estimation - Time ranges for each refactoring")
    print("✅ Legacy Code Strategies - Strangler Fig, Branch by Abstraction, etc.")
    print("✅ Automated Tools - Rope, Sourcery, jscodeshift, IDE tools")
    print("✅ 30+ Code Examples - Bad vs Good patterns")
