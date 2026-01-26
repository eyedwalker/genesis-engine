"""
Genesis Engine Database
SQLite-based persistence for factories, reviews, and sessions
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Database file location
DB_PATH = Path(__file__).parent.parent / "genesis.db"


def get_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Factories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                domain TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                assistants TEXT,  -- JSON array
                config TEXT,  -- JSON object
                features_built INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Code reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                factory_id TEXT,
                file_name TEXT NOT NULL,
                language TEXT,
                code_snippet TEXT,
                findings TEXT,  -- JSON array
                assistants_used TEXT,  -- JSON array
                status TEXT DEFAULT 'completed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (factory_id) REFERENCES factories(id)
            )
        """)

        # Features table
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

        # Sessions table (for real-time collaboration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_name TEXT NOT NULL,
                factory_id TEXT,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP,
                cursor_position TEXT,  -- JSON {line, column}
                FOREIGN KEY (factory_id) REFERENCES factories(id)
            )
        """)

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
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO factories (id, name, domain, description, assistants, config)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id,
            name,
            domain,
            description,
            json.dumps(assistants or ["security", "performance"]),
            json.dumps(config or {})
        ))
        return get_factory(id)


def get_factory(id: str) -> Optional[Dict[str, Any]]:
    """Get factory by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM factories WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_factory(row)
        return None


def get_all_factories() -> List[Dict[str, Any]]:
    """Get all factories"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM factories ORDER BY created_at DESC")
        return [_row_to_factory(row) for row in cursor.fetchall()]


def update_factory(id: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Update factory fields"""
    allowed = ["name", "domain", "description", "status", "assistants", "config", "features_built"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}

    if not updates:
        return get_factory(id)

    # JSON encode list/dict fields
    if "assistants" in updates:
        updates["assistants"] = json.dumps(updates["assistants"])
    if "config" in updates:
        updates["config"] = json.dumps(updates["config"])

    updates["updated_at"] = datetime.utcnow().isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [id]

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE factories SET {set_clause} WHERE id = ?", values)
        return get_factory(id)


def delete_factory(id: str) -> bool:
    """Delete factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM factories WHERE id = ?", (id,))
        return cursor.rowcount > 0


def increment_features(factory_id: str) -> None:
    """Increment features_built count"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE factories SET features_built = features_built + 1, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), factory_id)
        )


def _row_to_factory(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert row to factory dict"""
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
        cursor.execute("""
            INSERT INTO reviews (id, factory_id, file_name, language, code_snippet, findings, assistants_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            id,
            factory_id,
            file_name,
            language or _detect_language(file_name),
            code_snippet,
            json.dumps(findings),
            json.dumps(assistants_used)
        ))
        return get_review(id)


def get_review(id: str) -> Optional[Dict[str, Any]]:
    """Get review by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return _row_to_review(row)
        return None


def get_reviews_for_factory(factory_id: str) -> List[Dict[str, Any]]:
    """Get all reviews for a factory"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reviews WHERE factory_id = ? ORDER BY created_at DESC",
            (factory_id,)
        )
        return [_row_to_review(row) for row in cursor.fetchall()]


def get_recent_reviews(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent reviews"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [_row_to_review(row) for row in cursor.fetchall()]


def _row_to_review(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert row to review dict"""
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
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "csharp",
        ".cpp": "cpp",
        ".c": "c",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
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

        # Factory counts
        cursor.execute("SELECT COUNT(*) FROM factories")
        total_factories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM factories WHERE status = 'active'")
        active_factories = cursor.fetchone()[0]

        # Features count
        cursor.execute("SELECT SUM(features_built) FROM factories")
        total_features = cursor.fetchone()[0] or 0

        # Review counts
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]

        # Findings by severity
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


# Initialize database on import
init_db()
