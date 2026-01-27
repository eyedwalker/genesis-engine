"""
Genesis Engine Database
Supports both SQLite (local) and PostgreSQL (production)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from urllib.parse import urlparse

# Determine database type from DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# Railway uses postgres:// but psycopg2 needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

USE_POSTGRES = DATABASE_URL.startswith("postgresql://")

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
else:
    import sqlite3
    DB_PATH = Path(__file__).parent.parent / "genesis.db"


def get_connection():
    """Get database connection"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        if USE_POSTGRES:
            conn.autocommit = False
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _param(idx: int = None) -> str:
    """Return parameter placeholder for current database"""
    return "%s" if USE_POSTGRES else "?"


def _params(count: int) -> str:
    """Return multiple parameter placeholders"""
    p = "%s" if USE_POSTGRES else "?"
    return ", ".join([p] * count)


def _row_to_dict(row, cursor=None) -> Dict[str, Any]:
    """Convert database row to dictionary"""
    if USE_POSTGRES:
        if cursor:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return dict(row) if row else None
    else:
        return dict(row) if row else None


def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        if USE_POSTGRES:
            # PostgreSQL schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    assistants TEXT,
                    config TEXT,
                    features_built INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT REFERENCES factories(id),
                    file_name TEXT NOT NULL,
                    language TEXT,
                    code_snippet TEXT,
                    findings TEXT,
                    assistants_used TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS features (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT NOT NULL REFERENCES factories(id),
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    code_path TEXT,
                    review_id TEXT REFERENCES reviews(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    factory_id TEXT REFERENCES factories(id),
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cursor_position TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_tasks (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT NOT NULL REFERENCES factories(id),
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    task_type TEXT DEFAULT 'manual',
                    action_url TEXT,
                    action_command TEXT,
                    required BOOLEAN DEFAULT TRUE,
                    order_index INTEGER DEFAULT 0,
                    metadata TEXT,
                    completed_at TIMESTAMP,
                    completed_by TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    category TEXT NOT NULL,
                    label TEXT NOT NULL,
                    description TEXT,
                    value_type TEXT DEFAULT 'string',
                    is_required BOOLEAN DEFAULT FALSE,
                    is_configured BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        else:
            # SQLite schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    assistants TEXT,
                    config TEXT,
                    features_built INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT,
                    file_name TEXT NOT NULL,
                    language TEXT,
                    code_snippet TEXT,
                    findings TEXT,
                    assistants_used TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (factory_id) REFERENCES factories(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS features (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    code_path TEXT,
                    review_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT,
                    FOREIGN KEY (factory_id) REFERENCES factories(id),
                    FOREIGN KEY (review_id) REFERENCES reviews(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_name TEXT NOT NULL,
                    factory_id TEXT,
                    last_active TEXT DEFAULT CURRENT_TIMESTAMP,
                    cursor_position TEXT,
                    FOREIGN KEY (factory_id) REFERENCES factories(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setup_tasks (
                    id TEXT PRIMARY KEY,
                    factory_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    task_type TEXT DEFAULT 'manual',
                    action_url TEXT,
                    action_command TEXT,
                    required BOOLEAN DEFAULT 1,
                    order_index INTEGER DEFAULT 0,
                    metadata TEXT,
                    completed_at TEXT,
                    completed_by TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (factory_id) REFERENCES factories(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    category TEXT NOT NULL,
                    label TEXT NOT NULL,
                    description TEXT,
                    value_type TEXT DEFAULT 'string',
                    is_required BOOLEAN DEFAULT 0,
                    is_configured BOOLEAN DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Initialize default settings
        default_settings = [
            ("anthropic_api_key", "", "ai", "Anthropic API Key", "Required for AI-powered planning and code review", "secret", True),
            ("ai_model", "claude-sonnet-4-20250514", "ai", "AI Model", "Claude model to use for AI features", "string", False),
            ("openai_api_key", "", "ai", "OpenAI API Key", "Optional: For OpenAI-based features", "secret", False),
            ("stripe_api_key", "", "integrations", "Stripe API Key", "For payment processing in factories", "secret", False),
            ("stripe_webhook_secret", "", "integrations", "Stripe Webhook Secret", "For Stripe webhook verification", "secret", False),
            ("sendgrid_api_key", "", "integrations", "SendGrid API Key", "For email delivery", "secret", False),
            ("auth0_domain", "", "integrations", "Auth0 Domain", "Auth0 tenant domain", "string", False),
            ("auth0_client_id", "", "integrations", "Auth0 Client ID", "Auth0 application client ID", "string", False),
            ("auth0_client_secret", "", "integrations", "Auth0 Client Secret", "Auth0 application secret", "secret", False),
            ("aws_access_key", "", "integrations", "AWS Access Key", "AWS IAM access key", "secret", False),
            ("aws_secret_key", "", "integrations", "AWS Secret Key", "AWS IAM secret key", "secret", False),
            ("aws_region", "us-east-1", "integrations", "AWS Region", "Default AWS region", "string", False),
            ("github_token", "", "integrations", "GitHub Token", "For GitHub integration", "secret", False),
            ("database_url", "", "integrations", "Database URL", "PostgreSQL connection string for factories", "secret", False),
            ("default_assistants", '["security", "performance"]', "defaults", "Default Assistants", "Assistants enabled by default for new factories", "json", False),
            ("default_component_library", "shadcn/ui", "defaults", "Component Library", "Default UI component library", "string", False),
            ("default_architecture", "VBD", "defaults", "Architecture Pattern", "Default architecture pattern", "string", False),
            ("theme", "dark", "ui", "Theme", "Dashboard theme (dark/light)", "string", False),
            ("show_ai_suggestions", "true", "ui", "AI Suggestions", "Show AI-powered suggestions", "boolean", False),
        ]

        for key, value, category, label, description, value_type, is_required in default_settings:
            if USE_POSTGRES:
                cursor.execute("""
                    INSERT INTO settings (key, value, category, label, description, value_type, is_required, is_configured)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (key) DO NOTHING
                """, (key, value, category, label, description, value_type, is_required, bool(value)))
            else:
                cursor.execute("""
                    INSERT OR IGNORE INTO settings (key, value, category, label, description, value_type, is_required, is_configured)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (key, value, category, label, description, value_type, is_required, bool(value)))

        conn.commit()


# =============================================================================
# Factory Operations
# =============================================================================

def create_factory(
    id: str,
    name: str,
    domain: str,
    description: str = "",
    assistants: List[str] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a new factory"""
    created_at = datetime.utcnow().isoformat()
    assistants_list = assistants or ["security", "performance"]
    config_dict = config or {}

    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO factories (id, name, domain, description, assistants, config, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id, name, domain, description, json.dumps(assistants_list), json.dumps(config_dict), created_at, created_at))
        else:
            cursor.execute("""
                INSERT INTO factories (id, name, domain, description, assistants, config, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id, name, domain, description, json.dumps(assistants_list), json.dumps(config_dict), created_at, created_at))

    return {
        "id": id,
        "name": name,
        "domain": domain,
        "description": description,
        "status": "active",
        "assistants": assistants_list,
        "config": config_dict,
        "features_built": 0,
        "created_at": created_at,
        "updated_at": created_at
    }


def get_factory(id: str) -> Optional[Dict[str, Any]]:
    """Get factory by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM factories WHERE id = %s", (id,))
        else:
            cursor.execute("SELECT * FROM factories WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_factory(row, cursor)
        return None


def get_all_factories() -> List[Dict[str, Any]]:
    """Get all factories"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM factories ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [_row_to_factory(row, cursor) for row in rows]


def update_factory(id: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Update factory fields"""
    allowed = ["name", "domain", "description", "status", "assistants", "config", "features_built"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}

    if not updates:
        return get_factory(id)

    if "assistants" in updates:
        updates["assistants"] = json.dumps(updates["assistants"])
    if "config" in updates:
        updates["config"] = json.dumps(updates["config"])

    updates["updated_at"] = datetime.utcnow().isoformat()

    if USE_POSTGRES:
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
    else:
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())

    values = list(updates.values()) + [id]

    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute(f"UPDATE factories SET {set_clause} WHERE id = %s", values)
        else:
            cursor.execute(f"UPDATE factories SET {set_clause} WHERE id = ?", values)

    return get_factory(id)


def delete_factory(id: str) -> bool:
    """Delete factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("DELETE FROM factories WHERE id = %s", (id,))
        else:
            cursor.execute("DELETE FROM factories WHERE id = ?", (id,))
        return cursor.rowcount > 0


def increment_features(factory_id: str) -> None:
    """Increment features_built count"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute(
                "UPDATE factories SET features_built = features_built + 1, updated_at = %s WHERE id = %s",
                (datetime.utcnow().isoformat(), factory_id)
            )
        else:
            cursor.execute(
                "UPDATE factories SET features_built = features_built + 1, updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), factory_id)
            )


def _row_to_factory(row, cursor=None) -> Dict[str, Any]:
    """Convert row to factory dict"""
    if USE_POSTGRES:
        d = _row_to_dict(row, cursor)
        return {
            "id": d["id"],
            "name": d["name"],
            "domain": d["domain"],
            "description": d["description"],
            "status": d["status"],
            "assistants": json.loads(d["assistants"]) if d["assistants"] else [],
            "config": json.loads(d["config"]) if d["config"] else {},
            "features_built": d["features_built"],
            "created_at": str(d["created_at"]) if d["created_at"] else None,
            "updated_at": str(d["updated_at"]) if d["updated_at"] else None
        }
    else:
        return {
            "id": row["id"],
            "name": row["name"],
            "domain": row["domain"],
            "description": row["description"],
            "status": row["status"],
            "assistants": json.loads(row["assistants"]) if row["assistants"] else [],
            "config": json.loads(row["config"]) if row["config"] else {},
            "features_built": row["features_built"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }


# =============================================================================
# Review Operations
# =============================================================================

def create_review(
    id: str,
    file_name: str,
    code_snippet: str,
    findings: List[Dict[str, Any]],
    assistants_used: List[str],
    factory_id: str = None,
    language: str = None
) -> Dict[str, Any]:
    """Create a new code review"""
    with get_db() as conn:
        cursor = conn.cursor()
        lang = language or _detect_language(file_name)
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO reviews (id, factory_id, file_name, language, code_snippet, findings, assistants_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id, factory_id, file_name, lang, code_snippet, json.dumps(findings), json.dumps(assistants_used)))
        else:
            cursor.execute("""
                INSERT INTO reviews (id, factory_id, file_name, language, code_snippet, findings, assistants_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id, factory_id, file_name, lang, code_snippet, json.dumps(findings), json.dumps(assistants_used)))

    return get_review(id)


def get_review(id: str) -> Optional[Dict[str, Any]]:
    """Get review by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM reviews WHERE id = %s", (id,))
        else:
            cursor.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_review(row, cursor)
        return None


def get_reviews_for_factory(factory_id: str) -> List[Dict[str, Any]]:
    """Get all reviews for a factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM reviews WHERE factory_id = %s ORDER BY created_at DESC", (factory_id,))
        else:
            cursor.execute("SELECT * FROM reviews WHERE factory_id = ? ORDER BY created_at DESC", (factory_id,))
        return [_row_to_review(row, cursor) for row in cursor.fetchall()]


def get_recent_reviews(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent reviews"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC LIMIT %s", (limit,))
        else:
            cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?", (limit,))
        return [_row_to_review(row, cursor) for row in cursor.fetchall()]


def _row_to_review(row, cursor=None) -> Dict[str, Any]:
    """Convert row to review dict"""
    if USE_POSTGRES:
        d = _row_to_dict(row, cursor)
        return {
            "id": d["id"],
            "factory_id": d["factory_id"],
            "file_name": d["file_name"],
            "language": d["language"],
            "code_snippet": d["code_snippet"],
            "findings": json.loads(d["findings"]) if d["findings"] else [],
            "assistants_used": json.loads(d["assistants_used"]) if d["assistants_used"] else [],
            "status": d["status"],
            "created_at": str(d["created_at"]) if d["created_at"] else None
        }
    else:
        return {
            "id": row["id"],
            "factory_id": row["factory_id"],
            "file_name": row["file_name"],
            "language": row["language"],
            "code_snippet": row["code_snippet"],
            "findings": json.loads(row["findings"]) if row["findings"] else [],
            "assistants_used": json.loads(row["assistants_used"]) if row["assistants_used"] else [],
            "status": row["status"],
            "created_at": row["created_at"]
        }


def _detect_language(file_name: str) -> str:
    """Detect language from file extension"""
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "typescript",
        ".jsx": "javascript", ".java": "java", ".go": "go", ".rs": "rust", ".rb": "ruby",
        ".php": "php", ".cs": "csharp", ".cpp": "cpp", ".c": "c", ".sql": "sql",
        ".html": "html", ".css": "css",
    }
    ext = Path(file_name).suffix.lower()
    return ext_map.get(ext, "text")


# =============================================================================
# Stats
# =============================================================================

def get_stats() -> Dict[str, Any]:
    """Get overall stats"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM factories")
        total_factories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM factories WHERE status = 'active'")
        active_factories = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(features_built), 0) FROM factories")
        total_features = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]

        cursor.execute("SELECT findings FROM reviews")
        findings_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for row in cursor.fetchall():
            findings = json.loads(row[0]) if row[0] else []
            for finding in findings:
                severity = finding.get("severity", "low")
                if severity in findings_count:
                    findings_count[severity] += 1

        return {
            "total_factories": total_factories,
            "active_factories": active_factories,
            "total_features": total_features,
            "total_reviews": total_reviews,
            "findings": findings_count
        }


# =============================================================================
# Setup Tasks Operations
# =============================================================================

def create_setup_task(
    id: str, factory_id: str, category: str, title: str,
    description: str = "", task_type: str = "manual",
    action_url: str = None, action_command: str = None,
    required: bool = True, order_index: int = 0,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a new setup task"""
    created_at = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO setup_tasks (id, factory_id, category, title, description, task_type,
                                         action_url, action_command, required, order_index, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id, factory_id, category, title, description, task_type, action_url, action_command,
                  required, order_index, json.dumps(metadata or {}), created_at))
        else:
            cursor.execute("""
                INSERT INTO setup_tasks (id, factory_id, category, title, description, task_type,
                                         action_url, action_command, required, order_index, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id, factory_id, category, title, description, task_type, action_url, action_command,
                  required, order_index, json.dumps(metadata or {}), created_at))

    return {
        "id": id, "factory_id": factory_id, "category": category, "title": title,
        "description": description, "status": "pending", "task_type": task_type,
        "action_url": action_url, "action_command": action_command, "required": required,
        "order_index": order_index, "metadata": metadata or {}, "completed_at": None,
        "completed_by": None, "notes": None, "created_at": created_at
    }


def get_setup_task(id: str) -> Optional[Dict[str, Any]]:
    """Get setup task by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM setup_tasks WHERE id = %s", (id,))
        else:
            cursor.execute("SELECT * FROM setup_tasks WHERE id = ?", (id,))
        row = cursor.fetchone()
        return _row_to_setup_task(row, cursor) if row else None


def get_setup_tasks_for_factory(factory_id: str) -> List[Dict[str, Any]]:
    """Get all setup tasks for a factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM setup_tasks WHERE factory_id = %s ORDER BY order_index, created_at", (factory_id,))
        else:
            cursor.execute("SELECT * FROM setup_tasks WHERE factory_id = ? ORDER BY order_index, created_at", (factory_id,))
        return [_row_to_setup_task(row, cursor) for row in cursor.fetchall()]


def update_setup_task(id: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Update setup task fields"""
    allowed = ["status", "notes", "completed_by", "completed_at", "metadata"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}

    if not updates:
        return get_setup_task(id)

    if updates.get("status") == "completed" and "completed_at" not in updates:
        updates["completed_at"] = datetime.utcnow().isoformat()

    if "metadata" in updates:
        updates["metadata"] = json.dumps(updates["metadata"])

    if USE_POSTGRES:
        set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
    else:
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())

    values = list(updates.values()) + [id]

    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute(f"UPDATE setup_tasks SET {set_clause} WHERE id = %s", values)
        else:
            cursor.execute(f"UPDATE setup_tasks SET {set_clause} WHERE id = ?", values)

    return get_setup_task(id)


def delete_setup_tasks_for_factory(factory_id: str) -> int:
    """Delete all setup tasks for a factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("DELETE FROM setup_tasks WHERE factory_id = %s", (factory_id,))
        else:
            cursor.execute("DELETE FROM setup_tasks WHERE factory_id = ?", (factory_id,))
        return cursor.rowcount


def get_setup_progress(factory_id: str) -> Dict[str, Any]:
    """Get setup progress summary for a factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        p = "%s" if USE_POSTGRES else "?"

        cursor.execute(f"SELECT COUNT(*) FROM setup_tasks WHERE factory_id = {p}", (factory_id,))
        total = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM setup_tasks WHERE factory_id = {p} AND status = 'completed'", (factory_id,))
        completed = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM setup_tasks WHERE factory_id = {p} AND required = true", (factory_id,))
        required_total = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM setup_tasks WHERE factory_id = {p} AND required = true AND status = 'completed'", (factory_id,))
        required_completed = cursor.fetchone()[0]

        return {
            "total": total,
            "completed": completed,
            "required_total": required_total,
            "required_completed": required_completed,
            "percent": round((completed / total * 100) if total > 0 else 0),
            "by_category": {}
        }


def _row_to_setup_task(row, cursor=None) -> Dict[str, Any]:
    """Convert row to setup task dict"""
    if USE_POSTGRES:
        d = _row_to_dict(row, cursor)
        return {
            "id": d["id"], "factory_id": d["factory_id"], "category": d["category"],
            "title": d["title"], "description": d["description"], "status": d["status"],
            "task_type": d["task_type"], "action_url": d["action_url"],
            "action_command": d["action_command"], "required": bool(d["required"]),
            "order_index": d["order_index"],
            "metadata": json.loads(d["metadata"]) if d["metadata"] else {},
            "completed_at": str(d["completed_at"]) if d["completed_at"] else None,
            "completed_by": d["completed_by"], "notes": d["notes"],
            "created_at": str(d["created_at"]) if d["created_at"] else None
        }
    else:
        return {
            "id": row["id"], "factory_id": row["factory_id"], "category": row["category"],
            "title": row["title"], "description": row["description"], "status": row["status"],
            "task_type": row["task_type"], "action_url": row["action_url"],
            "action_command": row["action_command"], "required": bool(row["required"]),
            "order_index": row["order_index"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "completed_at": row["completed_at"], "completed_by": row["completed_by"],
            "notes": row["notes"], "created_at": row["created_at"]
        }


# =============================================================================
# Settings Operations
# =============================================================================

def get_setting(key: str) -> Optional[str]:
    """Get a single setting value by key"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT value FROM settings WHERE key = %s", (key,))
        else:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None


def get_settings_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all settings in a category"""
    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM settings WHERE category = %s ORDER BY label", (category,))
        else:
            cursor.execute("SELECT * FROM settings WHERE category = ? ORDER BY label", (category,))
        return [_row_to_setting(row, cursor) for row in cursor.fetchall()]


def get_all_settings() -> Dict[str, List[Dict[str, Any]]]:
    """Get all settings grouped by category"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings ORDER BY category, label")
        rows = cursor.fetchall()

        grouped = {}
        for row in rows:
            setting = _row_to_setting(row, cursor)
            category = setting["category"]
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(setting)

        return grouped


def update_setting(key: str, value: str) -> Optional[Dict[str, Any]]:
    """Update a setting value"""
    updated_at = datetime.utcnow().isoformat()
    is_configured = bool(value and value.strip())

    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("""
                UPDATE settings SET value = %s, is_configured = %s, updated_at = %s WHERE key = %s
            """, (value, is_configured, updated_at, key))
        else:
            cursor.execute("""
                UPDATE settings SET value = ?, is_configured = ?, updated_at = ? WHERE key = ?
            """, (value, is_configured, updated_at, key))

    with get_db() as conn:
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT * FROM settings WHERE key = %s", (key,))
        else:
            cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return _row_to_setting(row, cursor) if row else None


def update_settings_batch(updates: Dict[str, str]) -> Dict[str, Any]:
    """Update multiple settings at once"""
    updated_at = datetime.utcnow().isoformat()
    results = {}

    with get_db() as conn:
        cursor = conn.cursor()
        for key, value in updates.items():
            is_configured = bool(value and str(value).strip())
            if USE_POSTGRES:
                cursor.execute("""
                    UPDATE settings SET value = %s, is_configured = %s, updated_at = %s WHERE key = %s
                """, (str(value), is_configured, updated_at, key))
            else:
                cursor.execute("""
                    UPDATE settings SET value = ?, is_configured = ?, updated_at = ? WHERE key = ?
                """, (str(value), is_configured, updated_at, key))
            results[key] = {"updated": cursor.rowcount > 0}

    return results


def get_settings_status() -> Dict[str, Any]:
    """Get configuration status summary"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM settings WHERE is_required = true")
        required_total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM settings WHERE is_required = true AND is_configured = true")
        required_configured = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM settings")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM settings WHERE is_configured = true")
        configured = cursor.fetchone()[0]

        if USE_POSTGRES:
            cursor.execute("SELECT key, label FROM settings WHERE is_required = true AND is_configured = false")
        else:
            cursor.execute("SELECT key, label FROM settings WHERE is_required = 1 AND is_configured = 0")

        missing_required = []
        for row in cursor.fetchall():
            if USE_POSTGRES:
                d = _row_to_dict(row, cursor)
                missing_required.append({"key": d["key"], "label": d["label"]})
            else:
                missing_required.append({"key": row["key"], "label": row["label"]})

        return {
            "total": total,
            "configured": configured,
            "required_total": required_total,
            "required_configured": required_configured,
            "is_ready": required_configured == required_total,
            "missing_required": missing_required
        }


def _row_to_setting(row, cursor=None) -> Dict[str, Any]:
    """Convert row to setting dict"""
    if USE_POSTGRES:
        d = _row_to_dict(row, cursor)
        setting = {
            "key": d["key"], "value": d["value"], "category": d["category"],
            "label": d["label"], "description": d["description"],
            "value_type": d["value_type"], "is_required": bool(d["is_required"]),
            "is_configured": bool(d["is_configured"]),
            "updated_at": str(d["updated_at"]) if d["updated_at"] else None
        }
    else:
        setting = {
            "key": row["key"], "value": row["value"], "category": row["category"],
            "label": row["label"], "description": row["description"],
            "value_type": row["value_type"], "is_required": bool(row["is_required"]),
            "is_configured": bool(row["is_configured"]), "updated_at": row["updated_at"]
        }

    if setting["value_type"] == "secret" and setting["value"]:
        val = setting["value"]
        setting["display_value"] = val[:4] + "..." + val[-4:] if len(val) > 8 else "••••••••"
    else:
        setting["display_value"] = setting["value"]

    return setting


# Initialize database on import
init_db()
