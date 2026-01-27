"""
Enhanced Database Schema Reviewer Assistant

Comprehensive database design and optimization covering:
- Normalization forms (1NF through 5NF, BCNF)
- Index types and optimization (B-tree, Hash, GiST, GIN, BRIN)
- Partitioning strategies (range, list, hash)
- Sharding patterns (horizontal, vertical, functional)
- Query optimization (EXPLAIN, N+1 detection)
- Zero-downtime migrations
- Connection pooling
- ACID vs BASE tradeoffs

References:
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- MySQL Documentation: https://dev.mysql.com/doc/
- Database Normalization (Edgar F. Codd)
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class DatabaseFinding(BaseModel):
    """Structured database finding output"""

    finding_id: str = Field(..., description="Unique identifier (DB-001, DB-002, etc.)")
    title: str = Field(..., description="Brief title of the database issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Normalization/Index/Query/Schema/Migration")

    location: Dict[str, Any] = Field(default_factory=dict, description="Table, column, query")
    description: str = Field(..., description="Detailed description of the issue")

    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    normal_form_violation: Optional[str] = Field(default=None, description="Which normal form violated")

    current_schema: str = Field(default="", description="Current schema/query")
    improved_schema: str = Field(default="", description="Improved schema/query")
    explanation: str = Field(default="", description="Why the improvement is better")

    migration_strategy: str = Field(default="", description="How to migrate safely")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Database tools")
    references: List[str] = Field(default_factory=list, description="Documentation")

    remediation: Dict[str, str] = Field(default_factory=dict, description="Effort and priority")


class EnhancedDatabaseAssistant:
    """
    Enhanced Database Schema Reviewer with comprehensive coverage

    Reviews:
    - Schema normalization (1NF-5NF)
    - Index optimization
    - Query performance
    - Partitioning and sharding
    - Migration safety
    """

    def __init__(self):
        self.name = "Enhanced Database Schema Reviewer"
        self.version = "2.0.0"
        self.standards = ["SQL Standard", "ACID", "CAP Theorem", "Codd's Rules"]

    # =========================================================================
    # NORMALIZATION FORMS
    # =========================================================================

    @staticmethod
    def normalization_guide() -> Dict[str, Any]:
        """Database normalization forms (1NF through 5NF)"""
        return {
            "1nf": {
                "name": "First Normal Form (1NF)",
                "rules": [
                    "Each column contains atomic (indivisible) values",
                    "Each column contains values of a single type",
                    "Each row is unique (has a primary key)",
                    "No repeating groups or arrays",
                ],
                "bad": """
-- BAD: Violates 1NF (multi-valued column)
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    products VARCHAR(500)  -- "Widget, Gadget, Gizmo" - NOT ATOMIC!
);

-- BAD: Repeating groups
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    product1 VARCHAR(100),
    product2 VARCHAR(100),
    product3 VARCHAR(100)  -- What if 4 products?
);
                """,
                "good": """
-- GOOD: Atomic values, separate table for products
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    order_date DATE
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2)
);
                """,
            },
            "2nf": {
                "name": "Second Normal Form (2NF)",
                "rules": [
                    "Must be in 1NF",
                    "All non-key columns depend on the ENTIRE primary key",
                    "No partial dependencies (for composite keys)",
                ],
                "bad": """
-- BAD: Violates 2NF (partial dependency)
-- Composite key: (student_id, course_id)
CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    student_name VARCHAR(100),  -- Depends only on student_id, NOT course_id!
    course_name VARCHAR(100),   -- Depends only on course_id, NOT student_id!
    grade CHAR(2),
    PRIMARY KEY (student_id, course_id)
);
-- student_name depends only on student_id (partial dependency)
                """,
                "good": """
-- GOOD: Separate tables, no partial dependencies
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100)
);

CREATE TABLE enrollments (
    student_id INT REFERENCES students(student_id),
    course_id INT REFERENCES courses(course_id),
    grade CHAR(2),
    PRIMARY KEY (student_id, course_id)
);
-- Now grade depends on the ENTIRE composite key
                """,
            },
            "3nf": {
                "name": "Third Normal Form (3NF)",
                "rules": [
                    "Must be in 2NF",
                    "No transitive dependencies",
                    "Non-key columns depend ONLY on the primary key",
                ],
                "bad": """
-- BAD: Violates 3NF (transitive dependency)
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100),  -- Depends on department_id, not employee_id!
    department_budget DECIMAL(15,2)  -- Also transitive!
);
-- department_name depends on department_id, which depends on employee_id
-- (employee_id -> department_id -> department_name) = transitive
                """,
                "good": """
-- GOOD: No transitive dependencies
CREATE TABLE departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100),
    department_budget DECIMAL(15,2)
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100),
    department_id INT REFERENCES departments(department_id)
);
-- Now all non-key columns depend directly on the primary key
                """,
            },
            "bcnf": {
                "name": "Boyce-Codd Normal Form (BCNF)",
                "rules": [
                    "Must be in 3NF",
                    "Every determinant must be a candidate key",
                    "Stricter than 3NF for certain edge cases",
                ],
                "example": """
-- Scenario: Professor teaches only one subject
-- Subject can be taught by multiple professors
-- Student can take multiple subjects

-- BAD: Violates BCNF
CREATE TABLE schedule (
    student_id INT,
    subject VARCHAR(100),
    professor VARCHAR(100),
    PRIMARY KEY (student_id, subject)
);
-- professor -> subject (professor determines subject)
-- but professor is not a candidate key!

-- GOOD: BCNF compliant
CREATE TABLE professor_subjects (
    professor VARCHAR(100) PRIMARY KEY,
    subject VARCHAR(100)
);

CREATE TABLE student_professors (
    student_id INT,
    professor VARCHAR(100) REFERENCES professor_subjects(professor),
    PRIMARY KEY (student_id, professor)
);
                """,
            },
            "4nf": {
                "name": "Fourth Normal Form (4NF)",
                "rules": [
                    "Must be in BCNF",
                    "No multi-valued dependencies",
                    "Independent multi-valued facts should be in separate tables",
                ],
                "example": """
-- BAD: Violates 4NF (multi-valued dependencies)
-- A person can have multiple skills AND multiple languages
-- But skills and languages are INDEPENDENT of each other
CREATE TABLE person_attributes (
    person_id INT,
    skill VARCHAR(100),
    language VARCHAR(100),
    PRIMARY KEY (person_id, skill, language)
);
-- This creates redundant rows!
-- person_id=1, skill='Python', language='English'
-- person_id=1, skill='Python', language='Spanish'
-- person_id=1, skill='Java', language='English'
-- person_id=1, skill='Java', language='Spanish'

-- GOOD: 4NF compliant - separate independent facts
CREATE TABLE person_skills (
    person_id INT,
    skill VARCHAR(100),
    PRIMARY KEY (person_id, skill)
);

CREATE TABLE person_languages (
    person_id INT,
    language VARCHAR(100),
    PRIMARY KEY (person_id, language)
);
                """,
            },
            "5nf": {
                "name": "Fifth Normal Form (5NF)",
                "rules": [
                    "Must be in 4NF",
                    "No join dependencies",
                    "Cannot be decomposed further without loss of information",
                ],
                "note": "Rarely needed in practice. Most schemas stop at 3NF or BCNF.",
            },
        }

    # =========================================================================
    # INDEX TYPES AND OPTIMIZATION
    # =========================================================================

    @staticmethod
    def index_types() -> Dict[str, Any]:
        """Index types and when to use them"""
        return {
            "btree": {
                "name": "B-tree Index (Default)",
                "use_cases": [
                    "Equality comparisons (=)",
                    "Range queries (<, >, BETWEEN)",
                    "Sorting (ORDER BY)",
                    "Most common index type",
                ],
                "example": """
-- B-tree index (default)
CREATE INDEX idx_users_email ON users(email);

-- Composite B-tree index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Partial index (only active users)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Queries that use B-tree effectively:
SELECT * FROM users WHERE email = 'user@example.com';  -- Equality
SELECT * FROM orders WHERE created_at > '2024-01-01';  -- Range
SELECT * FROM orders ORDER BY created_at DESC;        -- Sorting
                """,
            },
            "hash": {
                "name": "Hash Index",
                "use_cases": [
                    "Equality comparisons ONLY (=)",
                    "NOT for range queries",
                    "Faster than B-tree for pure equality",
                ],
                "example": """
-- Hash index (PostgreSQL)
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- Good for:
SELECT * FROM users WHERE email = 'user@example.com';  -- ✅

-- NOT good for (won't use hash index):
SELECT * FROM users WHERE email LIKE 'user%';  -- ❌
SELECT * FROM users ORDER BY email;            -- ❌
                """,
            },
            "gin": {
                "name": "GIN (Generalized Inverted Index)",
                "use_cases": [
                    "Full-text search",
                    "JSONB containment queries",
                    "Array containment queries",
                    "Multiple values per row",
                ],
                "example": """
-- GIN for full-text search
CREATE INDEX idx_articles_search ON articles
USING GIN (to_tsvector('english', title || ' ' || body));

SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('database');

-- GIN for JSONB
CREATE INDEX idx_users_metadata ON users USING GIN (metadata);

SELECT * FROM users WHERE metadata @> '{"role": "admin"}';
SELECT * FROM users WHERE metadata ? 'premium';

-- GIN for arrays
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

SELECT * FROM posts WHERE tags @> ARRAY['python', 'database'];
                """,
            },
            "gist": {
                "name": "GiST (Generalized Search Tree)",
                "use_cases": [
                    "Geometric data (PostGIS)",
                    "Range types",
                    "Full-text search (alternative to GIN)",
                    "Nearest neighbor queries",
                ],
                "example": """
-- GiST for geometric queries (PostGIS)
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

SELECT * FROM locations
WHERE ST_DWithin(geom, ST_MakePoint(-122.4, 37.8)::geography, 1000);

-- GiST for range types
CREATE INDEX idx_reservations_dates ON reservations
USING GIST (daterange(check_in, check_out));

SELECT * FROM reservations
WHERE daterange(check_in, check_out) && daterange('2024-06-01', '2024-06-15');
                """,
            },
            "brin": {
                "name": "BRIN (Block Range Index)",
                "use_cases": [
                    "Very large tables (billions of rows)",
                    "Naturally ordered data (timestamps, serial IDs)",
                    "Much smaller than B-tree",
                    "Tradeoff: Less precise, scans more blocks",
                ],
                "example": """
-- BRIN for time-series data (PostgreSQL)
CREATE INDEX idx_events_created ON events USING BRIN (created_at);

-- BRIN is tiny: 128KB vs 2GB B-tree for billion rows
-- Works well when data is physically ordered by the indexed column

-- Good for:
SELECT * FROM events WHERE created_at > '2024-01-01';

-- Best when data is inserted in order!
                """,
            },
            "covering": {
                "name": "Covering Index (Index-Only Scans)",
                "use_cases": [
                    "Avoid table lookups entirely",
                    "All queried columns in index",
                    "Significant performance boost",
                ],
                "example": """
-- INCLUDE columns for covering index (PostgreSQL 11+)
CREATE INDEX idx_orders_cover ON orders (user_id, status)
INCLUDE (total_amount, created_at);

-- Query satisfied entirely from index (no table access!)
SELECT user_id, status, total_amount, created_at
FROM orders
WHERE user_id = 123 AND status = 'completed';

-- EXPLAIN shows "Index Only Scan"
                """,
            },
        }

    @staticmethod
    def index_best_practices() -> Dict[str, Any]:
        """Index optimization best practices"""
        return {
            "when_to_index": [
                "Columns in WHERE clauses",
                "Columns in JOIN conditions",
                "Columns in ORDER BY",
                "Columns with high selectivity",
                "Foreign keys",
            ],
            "when_not_to_index": [
                "Small tables (< 1000 rows)",
                "Columns with low selectivity (boolean, status with few values)",
                "Frequently updated columns",
                "Wide columns (large text)",
            ],
            "composite_index_order": """
-- Order matters! Put most selective column first
-- Or put equality conditions before range conditions

-- Good: Equality first, then range
CREATE INDEX idx_orders ON orders (status, created_at);

SELECT * FROM orders WHERE status = 'pending' AND created_at > '2024-01-01';
-- Uses full index

-- Bad order for this query:
CREATE INDEX idx_orders_bad ON orders (created_at, status);
-- Can only use first column efficiently
            """,
            "unused_indexes": """
-- Find unused indexes (PostgreSQL)
SELECT
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(i.indexrelid)) AS size,
    idx_scan AS times_used
FROM pg_stat_user_indexes i
JOIN pg_index USING (indexrelid)
WHERE idx_scan = 0
AND NOT indisunique
ORDER BY pg_relation_size(i.indexrelid) DESC;

-- Drop unused indexes to save space and speed up writes
            """,
        }

    # =========================================================================
    # PARTITIONING
    # =========================================================================

    @staticmethod
    def partitioning_strategies() -> Dict[str, Any]:
        """Table partitioning strategies"""
        return {
            "range": {
                "name": "Range Partitioning",
                "use_case": "Time-series data, sequential data",
                "example": """
-- Range partitioning by date (PostgreSQL)
CREATE TABLE events (
    id BIGSERIAL,
    event_type VARCHAR(50),
    payload JSONB,
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Queries automatically route to correct partition
SELECT * FROM events WHERE created_at >= '2024-01-15';
-- Only scans events_2024_01, not all partitions!

-- Automate partition creation with pg_partman
                """,
            },
            "list": {
                "name": "List Partitioning",
                "use_case": "Categorical data, multi-tenant",
                "example": """
-- List partitioning by region
CREATE TABLE orders (
    id BIGSERIAL,
    customer_id INT,
    region VARCHAR(20) NOT NULL,
    total DECIMAL(10,2)
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders
    FOR VALUES IN ('US', 'CA');

CREATE TABLE orders_eu PARTITION OF orders
    FOR VALUES IN ('UK', 'DE', 'FR');

CREATE TABLE orders_apac PARTITION OF orders
    FOR VALUES IN ('JP', 'AU', 'SG');

-- Multi-tenant partitioning
CREATE TABLE data (
    tenant_id INT NOT NULL,
    ...
) PARTITION BY LIST (tenant_id);

CREATE TABLE data_tenant_1 PARTITION OF data FOR VALUES IN (1);
CREATE TABLE data_tenant_2 PARTITION OF data FOR VALUES IN (2);
                """,
            },
            "hash": {
                "name": "Hash Partitioning",
                "use_case": "Even distribution, no natural range",
                "example": """
-- Hash partitioning for even distribution
CREATE TABLE users (
    id BIGSERIAL,
    email VARCHAR(255),
    created_at TIMESTAMPTZ
) PARTITION BY HASH (id);

CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE users_1 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE users_2 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE users_3 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Evenly distributes data across 4 partitions
                """,
            },
            "benefits": [
                "Faster queries (partition pruning)",
                "Easier maintenance (drop old partitions)",
                "Parallel query execution",
                "Smaller indexes per partition",
            ],
            "considerations": [
                "Partition key must be in primary key",
                "Cross-partition queries can be slower",
                "Need to manage partition creation",
                "Foreign keys have limitations",
            ],
        }

    # =========================================================================
    # SHARDING
    # =========================================================================

    @staticmethod
    def sharding_patterns() -> Dict[str, Any]:
        """Database sharding patterns"""
        return {
            "horizontal": {
                "name": "Horizontal Sharding",
                "description": "Same schema, different rows on different servers",
                "strategies": {
                    "hash_based": """
-- Hash-based sharding
-- Shard key: user_id
-- Shard = hash(user_id) % num_shards

def get_shard(user_id, num_shards=4):
    return hash(user_id) % num_shards

# User 123 -> Shard 3
# User 456 -> Shard 0
# etc.

# Pros: Even distribution
# Cons: Hard to reshard (rehashing needed)
                    """,
                    "range_based": """
-- Range-based sharding
-- Users 1-1M -> Shard 1
-- Users 1M-2M -> Shard 2
-- etc.

SHARD_RANGES = {
    1: (1, 1_000_000),
    2: (1_000_001, 2_000_000),
    3: (2_000_001, 3_000_000),
}

def get_shard(user_id):
    for shard, (start, end) in SHARD_RANGES.items():
        if start <= user_id <= end:
            return shard

# Pros: Easy range queries, easy to add shards
# Cons: Uneven distribution (hot shards)
                    """,
                    "directory_based": """
-- Directory-based sharding
-- Lookup table maps keys to shards

CREATE TABLE shard_directory (
    user_id BIGINT PRIMARY KEY,
    shard_id INT NOT NULL
);

def get_shard(user_id):
    return db.query(
        "SELECT shard_id FROM shard_directory WHERE user_id = ?",
        user_id
    )

# Pros: Flexible, easy to move users between shards
# Cons: Extra lookup, single point of failure
                    """,
                },
            },
            "vertical": {
                "name": "Vertical Sharding",
                "description": "Different tables on different servers",
                "example": """
-- Vertical sharding by domain
-- User service database
Server 1: users, user_profiles, user_settings

-- Order service database
Server 2: orders, order_items, payments

-- Product service database
Server 3: products, categories, inventory

# Pros: Natural service boundaries
# Cons: Cross-service joins impossible
                """,
            },
            "functional": {
                "name": "Functional Sharding",
                "description": "Different functions on different servers",
                "example": """
-- Functional sharding
-- Read replicas for read-heavy workloads
Primary (writes) -> Replica 1 (reads)
                 -> Replica 2 (reads)
                 -> Replica 3 (analytics)

# Application routes:
def get_connection(operation):
    if operation == 'write':
        return primary_db
    elif operation == 'analytics':
        return analytics_replica
    else:
        return random.choice(read_replicas)
                """,
            },
            "tools": [
                {"name": "Vitess", "url": "https://vitess.io/", "description": "MySQL sharding"},
                {"name": "Citus", "url": "https://www.citusdata.com/", "description": "PostgreSQL sharding"},
                {"name": "ProxySQL", "description": "MySQL query routing"},
            ],
        }

    # =========================================================================
    # ZERO-DOWNTIME MIGRATIONS
    # =========================================================================

    @staticmethod
    def zero_downtime_migrations() -> Dict[str, Any]:
        """Safe database migration patterns"""
        return {
            "add_column": {
                "safe": True,
                "pattern": """
-- Adding a column is safe (no lock in modern DBs)
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- But be careful with defaults on large tables!
-- BAD: Locks table while setting default for all rows
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- GOOD: Add column nullable first, then backfill
ALTER TABLE users ADD COLUMN status VARCHAR(20);
-- Backfill in batches
UPDATE users SET status = 'active' WHERE status IS NULL LIMIT 10000;
-- Then add default for new rows
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active';
                """,
            },
            "rename_column": {
                "safe": False,
                "pattern": """
-- NEVER rename column directly (breaks running code)
-- BAD:
ALTER TABLE users RENAME COLUMN name TO full_name;

-- GOOD: Expand and Contract pattern
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(100);

-- Step 2: Dual-write (app writes to both columns)
UPDATE users SET full_name = name WHERE full_name IS NULL;

-- Step 3: Deploy code that reads from new column
-- Step 4: Deploy code that only writes to new column
-- Step 5: Drop old column (after verifying)
ALTER TABLE users DROP COLUMN name;
                """,
            },
            "add_index": {
                "safe": "With CONCURRENTLY",
                "pattern": """
-- BAD: Locks table during index creation
CREATE INDEX idx_users_email ON users(email);

-- GOOD: Create index concurrently (no lock)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Note: CONCURRENTLY is slower, but doesn't block writes
-- If it fails, you may need to drop the invalid index:
DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
                """,
            },
            "drop_column": {
                "safe": "With preparation",
                "pattern": """
-- Step 1: Stop reading from column (deploy code change)
-- Step 2: Stop writing to column (deploy code change)
-- Step 3: Drop column
ALTER TABLE users DROP COLUMN old_column;

-- For PostgreSQL, dropping column is instant (just marks invisible)
-- Space reclaimed on next VACUUM
                """,
            },
            "change_type": {
                "safe": False,
                "pattern": """
-- NEVER change column type directly (may lock, may fail)
-- BAD:
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- GOOD: Create new column, migrate, swap
ALTER TABLE users ADD COLUMN age_new BIGINT;
UPDATE users SET age_new = age WHERE age_new IS NULL;
-- Deploy code to use age_new
ALTER TABLE users DROP COLUMN age;
ALTER TABLE users RENAME COLUMN age_new TO age;
                """,
            },
        }

    # =========================================================================
    # QUERY OPTIMIZATION
    # =========================================================================

    @staticmethod
    def query_optimization() -> Dict[str, Any]:
        """Query optimization patterns"""
        return {
            "explain_analyze": """
-- Always use EXPLAIN ANALYZE to understand query performance

EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;

-- Look for:
-- - Seq Scan (sequential scan) = missing index
-- - High "actual time" = slow operation
-- - High "rows" with low "actual rows" = bad estimate
-- - Nested Loop with many iterations = consider different join
            """,
            "n_plus_one": {
                "bad": """
# BAD: N+1 queries
users = db.query("SELECT * FROM users LIMIT 100")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
    # 1 + 100 = 101 queries!
                """,
                "good": """
# GOOD: Single query with JOIN
users_with_orders = db.query('''
    SELECT u.*, json_agg(o.*) as orders
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    GROUP BY u.id
    LIMIT 100
''')
# 1 query!

# Or use ORM with eager loading
users = User.objects.prefetch_related('orders').all()[:100]
                """,
            },
            "pagination": {
                "bad": """
-- BAD: OFFSET pagination (slow for large offsets)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 100000;
-- Must scan 100,000 rows to skip them!
                """,
                "good": """
-- GOOD: Keyset pagination (constant performance)
SELECT * FROM products
WHERE id > 12345  -- Last ID from previous page
ORDER BY id
LIMIT 20;

-- Or with composite key
SELECT * FROM products
WHERE (created_at, id) > ('2024-01-15', 12345)
ORDER BY created_at, id
LIMIT 20;
                """,
            },
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        table_name: str,
        issue_description: str,
        current_schema: str,
        improved_schema: str,
        explanation: str,
    ) -> DatabaseFinding:
        """Generate a structured database finding"""
        return DatabaseFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            location={"table": table_name},
            description=issue_description,
            current_schema=current_schema,
            improved_schema=improved_schema,
            explanation=explanation,
            migration_strategy=self._get_migration_strategy(category),
            tools=self._get_tool_recommendations(),
            remediation={
                "effort": "MEDIUM",
                "priority": "HIGH" if severity == "CRITICAL" else "MEDIUM",
            },
        )

    @staticmethod
    def _get_migration_strategy(category: str) -> str:
        return """
1. Create migration script
2. Test on staging with production-like data
3. Create rollback script
4. Schedule during low-traffic period
5. Monitor query performance after migration
        """

    @staticmethod
    def _get_tool_recommendations() -> List[Dict[str, str]]:
        return [
            {"name": "pgBadger", "command": "pgbadger /var/log/postgresql/*.log"},
            {"name": "EXPLAIN ANALYZE", "command": "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query>"},
            {"name": "pg_stat_statements", "description": "Query performance statistics"},
        ]


def create_enhanced_database_assistant():
    """Factory function to create enhanced database assistant"""
    return {
        "name": "Enhanced Database Schema Reviewer",
        "version": "2.0.0",
        "system_prompt": """You are an expert database architect with deep knowledge of:

- Normalization forms (1NF through 5NF, BCNF)
- Index types and optimization (B-tree, Hash, GIN, GiST, BRIN)
- Partitioning strategies (range, list, hash)
- Sharding patterns (horizontal, vertical, functional)
- Query optimization (EXPLAIN ANALYZE, N+1 detection)
- Zero-downtime migrations (expand/contract pattern)
- Connection pooling configuration
- ACID vs BASE tradeoffs

Your role is to:
1. Identify normalization violations
2. Recommend appropriate indexes
3. Suggest partitioning strategies for large tables
4. Detect query performance issues
5. Provide safe migration patterns
6. Optimize schema design

Always provide:
- Current schema showing issue
- Improved schema with explanation
- Migration strategy for safe deployment
- Performance impact analysis
- Tools for validation

Format findings as structured YAML.""",
        "assistant_class": EnhancedDatabaseAssistant,
        "domain": "architecture",
        "tags": ["database", "sql", "normalization", "indexing", "sharding"],
    }


    # =========================================================================
    # ADDITIONAL DATABASE PATTERNS - EXTENDED COVERAGE
    # =========================================================================

    @staticmethod
    def check_database_backup_strategies() -> Dict[str, Any]:
        """Database backup and recovery strategies"""
        return {
            "description": "Backup strategies for database disaster recovery",
            "strategies": [
                "Full backups - Complete database copy",
                "Incremental backups - Only changes since last backup",
                "Differential backups - Changes since last full backup",
                "Point-in-time recovery (PITR) - WAL-based recovery",
                "Continuous archiving - Real-time backup",
            ],
            "examples": {
                "bad": """
-- BAD: No backup strategy
-- Running production without regular backups
-- No point-in-time recovery capability
-- Single copy of data

# No pg_dump scheduled
# No WAL archiving configured
# No replication for redundancy
""",
                "good": """
-- GOOD: Comprehensive backup strategy

-- 1. Configure WAL archiving for PITR
-- postgresql.conf:
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
wal_level = replica

-- 2. Regular full backups with pg_dump
pg_dump -Fc -f /backup/full/db_$(date +%Y%m%d).dump mydb

-- 3. Continuous archiving with pgBackRest
pgbackrest --stanza=main backup --type=full
pgbackrest --stanza=main backup --type=incr

-- 4. Point-in-time recovery
pg_restore -d mydb_recovered /backup/full/db_20240115.dump
# Then apply WAL files to desired point in time

-- 5. Verify backups regularly
pg_restore --list /backup/full/db_20240115.dump
""",
            },
            "tools": [
                {
                    "name": "pgBackRest",
                    "url": "https://pgbackrest.org/",
                    "install": "apt-get install pgbackrest",
                },
                {
                    "name": "Barman",
                    "url": "https://www.pgbarman.org/",
                    "install": "pip install barman",
                },
            ],
        }

    @staticmethod
    def check_database_monitoring() -> Dict[str, Any]:
        """Database monitoring and alerting"""
        return {
            "description": "Essential database metrics to monitor",
            "key_metrics": [
                "Connection count and pool utilization",
                "Query latency (p50, p95, p99)",
                "Lock wait times and deadlocks",
                "Replication lag",
                "Cache hit ratio",
                "Disk usage and I/O",
                "Vacuum and autovacuum activity",
                "Table and index bloat",
            ],
            "examples": {
                "bad": """
-- BAD: No monitoring
-- Discovering issues only when users complain
-- No visibility into database health
-- No capacity planning data
""",
                "good": """
-- GOOD: Comprehensive monitoring queries

-- Connection monitoring
SELECT count(*) as total_connections,
       count(*) FILTER (WHERE state = 'active') as active,
       count(*) FILTER (WHERE state = 'idle') as idle,
       count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_txn
FROM pg_stat_activity;

-- Query performance (requires pg_stat_statements)
SELECT query,
       calls,
       mean_exec_time,
       total_exec_time,
       rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Replication lag
SELECT client_addr,
       state,
       sent_lsn - write_lsn AS write_lag,
       write_lsn - flush_lsn AS flush_lag,
       flush_lsn - replay_lsn AS replay_lag
FROM pg_stat_replication;

-- Cache hit ratio (should be > 99%)
SELECT
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS cache_hit_ratio
FROM pg_statio_user_tables;

-- Table bloat detection
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as total_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
""",
            },
            "tools": [
                {
                    "name": "pganalyze",
                    "url": "https://pganalyze.com/",
                    "description": "PostgreSQL performance monitoring",
                },
                {
                    "name": "Prometheus + postgres_exporter",
                    "url": "https://github.com/prometheus-community/postgres_exporter",
                    "install": "docker run --net=host -e DATA_SOURCE_NAME='postgresql://user:pass@localhost:5432/db?sslmode=disable' quay.io/prometheuscommunity/postgres-exporter",
                },
            ],
        }

    @staticmethod
    def check_vacuum_maintenance() -> Dict[str, Any]:
        """VACUUM and table maintenance"""
        return {
            "description": "PostgreSQL VACUUM and maintenance operations",
            "concepts": [
                "VACUUM - reclaims storage from dead tuples",
                "VACUUM FULL - rewrites entire table, reclaims space",
                "ANALYZE - updates statistics for query planner",
                "REINDEX - rebuilds indexes",
                "Autovacuum - automatic maintenance daemon",
            ],
            "examples": {
                "bad": """
-- BAD: Disabled autovacuum (never do this!)
ALTER TABLE large_table SET (autovacuum_enabled = false);

-- BAD: Running VACUUM FULL during business hours
-- This locks the entire table!
VACUUM FULL large_table;

-- BAD: Never monitoring bloat
-- Tables grow indefinitely, queries slow down
""",
                "good": """
-- GOOD: Proper vacuum configuration

-- Check autovacuum settings
SHOW autovacuum;
SHOW autovacuum_vacuum_threshold;
SHOW autovacuum_vacuum_scale_factor;

-- Tune autovacuum for high-churn tables
ALTER TABLE high_churn_table SET (
    autovacuum_vacuum_threshold = 50,
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.05
);

-- Manual vacuum during maintenance window
VACUUM ANALYZE schema.table_name;

-- Monitor vacuum progress
SELECT relname, n_dead_tup, n_live_tup,
       last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Check for tables needing vacuum
SELECT schemaname, relname,
       n_dead_tup::float / nullif(n_live_tup + n_dead_tup, 0) * 100 as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_pct DESC;
""",
            },
            "tools": [
                {
                    "name": "pg_repack",
                    "url": "https://github.com/reorg/pg_repack",
                    "description": "Online table reorganization without locks",
                    "install": "CREATE EXTENSION pg_repack;",
                },
            ],
        }


if __name__ == "__main__":
    assistant = EnhancedDatabaseAssistant()
    print("=" * 60)
    print("Enhanced Database Schema Reviewer")
    print("=" * 60)
    print(f"Version: {assistant.version}")
    print(f"Standards: {', '.join(assistant.standards)}")

    # Test normalization guide
    norm_guide = assistant.normalization_guide()
    print(f"\nNormalization Forms: {list(norm_guide.keys())}")

    # Test index types
    index_types = assistant.index_types()
    print(f"Index Types: {list(index_types.keys())}")

    # Test partitioning strategies
    partitioning = assistant.partitioning_strategies()
    print(f"Partitioning: {list(partitioning.keys())}")

    # Test sharding patterns
    sharding = assistant.sharding_patterns()
    print(f"Sharding: {list(sharding.keys())}")

    # Test backup strategies
    backup = assistant.check_database_backup_strategies()
    print(f"Backup Strategies: {backup['strategies'][:3]}...")

    # Test monitoring
    monitoring = assistant.check_database_monitoring()
    print(f"Key Metrics: {monitoring['key_metrics'][:3]}...")

    # Generate sample finding
    finding = assistant.generate_finding(
        finding_id="DB-001",
        title="3NF violation: Transitive dependency in employees table",
        severity="MEDIUM",
        category="Normalization",
        table_name="employees",
        issue_description="department_name depends on department_id, not employee_id",
        current_schema="employees(id, name, dept_id, dept_name, dept_budget)",
        improved_schema="employees(id, name, dept_id) + departments(id, name, budget)",
        explanation="Extract department to separate table to eliminate transitive dependency",
    )
    print(f"\nSample Finding: {finding.finding_id} - {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Category: {finding.category}")
