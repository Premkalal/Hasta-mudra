"""
db/database.py — SQLite Connection & Operations for HastaAI
Manages the 4 core relational tables:
1. users
2. mudras
3. practice_sessions
4. recognition_results
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from db.schema import SCHEMA_SQL
from config import cfg
from data.mudra_registry import get_all_mudras


def _get_connection() -> sqlite3.Connection:
    db_path = Path(cfg.database.path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA cache_size = 10000;")
    return conn


_DB_INITIALIZED = False


def init_db():
    """Create tables if they don't exist and seed mudras. Call at app startup."""
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return

    with _get_connection() as conn:
        conn.executescript(SCHEMA_SQL)

        # Seed mudras table if empty
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM mudras")
        row = cur.fetchone()
        if row and row["cnt"] == 0:
            seed_list = get_all_mudras()
            conn.executemany(
                """
                INSERT OR IGNORE INTO mudras (name, sanskrit, description, significance, instructions, category, image_ref)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        m.name,
                        m.sanskrit,
                        m.description,
                        m.significance,
                        m.instructions,
                        m.category,
                        m.image_ref,
                    )
                    for m in seed_list
                ],
            )
            conn.commit()
    _DB_INITIALIZED = True


# ── User Operations ────────────────────────────────────────────────────────────

def create_user(name: str, email: str, password_hash: str, auth_provider: str = "local") -> Optional[int]:
    """Register a new user. Returns user_id or None if email exists."""
    sql = """
        INSERT INTO users (name, email, password_hash, auth_provider, created_at)
        VALUES (?, ?, ?, ?, ?)
    """
    now = datetime.now().isoformat()
    try:
        with _get_connection() as conn:
            cur = conn.execute(sql, (name.strip(), email.strip().lower(), password_hash, auth_provider, now))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch user dict by email."""
    sql = "SELECT * FROM users WHERE email = ?"
    with _get_connection() as conn:
        row = conn.execute(sql, (email.strip().lower(),)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user dict by ID."""
    sql = "SELECT * FROM users WHERE id = ?"
    with _get_connection() as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
        return dict(row) if row else None


def update_user_name(user_id: int, new_name: str) -> bool:
    """Update user's display name."""
    sql = "UPDATE users SET name = ? WHERE id = ?"
    with _get_connection() as conn:
        cur = conn.execute(sql, (new_name.strip(), user_id))
        conn.commit()
        return cur.rowcount > 0


def update_user_password(email: str, new_password_hash: str) -> bool:
    """Update a user's password hash by email. Returns True if a row was updated."""
    sql = "UPDATE users SET password_hash = ? WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))"
    with _get_connection() as conn:
        cur = conn.execute(sql, (new_password_hash, email.strip().lower()))
        conn.commit()
        return cur.rowcount > 0


def update_user_password_by_id(user_id: int, new_password_hash: str) -> bool:
    """Update a user's password hash by user ID. Returns True if a row was updated."""
    sql = "UPDATE users SET password_hash = ? WHERE id = ?"
    with _get_connection() as conn:
        cur = conn.execute(sql, (new_password_hash, user_id))
        conn.commit()
        return cur.rowcount > 0


# ── Mudra Operations ───────────────────────────────────────────────────────────

def get_all_mudras_db() -> List[Dict[str, Any]]:
    """Fetch all mudras from database."""
    with _get_connection() as conn:
        rows = conn.execute("SELECT * FROM mudras ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]


def get_mudra_by_name_db(name: str) -> Optional[Dict[str, Any]]:
    """Fetch a mudra by its English or Sanskrit name."""
    sql = "SELECT * FROM mudras WHERE LOWER(name) = LOWER(?) OR LOWER(sanskrit) = LOWER(?)"
    with _get_connection() as conn:
        row = conn.execute(sql, (name.strip(), name.strip())).fetchone()
        return dict(row) if row else None


def get_mudra_by_id_db(mudra_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a mudra by ID."""
    sql = "SELECT * FROM mudras WHERE id = ?"
    with _get_connection() as conn:
        row = conn.execute(sql, (mudra_id,)).fetchone()
        return dict(row) if row else None


# ── Session & Recognition Operations ───────────────────────────────────────────

def start_practice_session(user_id: int, mudra_id: Optional[int] = None) -> int:
    """Create a new practice session record."""
    now = datetime.now().isoformat()
    sql = """
        INSERT INTO practice_sessions (user_id, mudra_id, start_time, duration, average_confidence, performance_score)
        VALUES (?, ?, ?, 0.0, 0.0, 0.0)
    """
    with _get_connection() as conn:
        cur = conn.execute(sql, (user_id, mudra_id, now))
        return cur.lastrowid


def end_practice_session(
    session_id: int,
    duration: float,
    average_confidence: float,
    performance_score: float,
    dominant_mudra_id: Optional[int] = None,
):
    """Finalize a practice session with duration, average confidence, and score."""
    now = datetime.now().isoformat()
    sql = """
        UPDATE practice_sessions
        SET end_time = ?,
            duration = ?,
            average_confidence = ?,
            performance_score = ?,
            mudra_id = COALESCE(?, mudra_id)
        WHERE id = ?
    """
    with _get_connection() as conn:
        conn.execute(sql, (now, duration, average_confidence, performance_score, dominant_mudra_id, session_id))


def log_recognition_result(session_id: int, mudra_id: Optional[int], confidence: float):
    """Record an individual recognition event during a session."""
    now = datetime.now().isoformat()
    sql = """
        INSERT INTO recognition_results (session_id, mudra_id, confidence, timestamp)
        VALUES (?, ?, ?, ?)
    """
    with _get_connection() as conn:
        conn.execute(sql, (session_id, mudra_id, round(confidence, 3), now))


def get_user_sessions(user_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch completed practice sessions for a user, ordered by start time desc."""
    sql = """
        SELECT s.id, s.user_id, s.mudra_id, s.start_time, s.end_time,
               s.duration, s.average_confidence, s.performance_score,
               m.name AS mudra_name, m.sanskrit AS mudra_sanskrit
        FROM practice_sessions s
        LEFT JOIN mudras m ON s.mudra_id = m.id
        WHERE s.user_id = ?
        ORDER BY s.start_time DESC
        LIMIT ?
    """
    with _get_connection() as conn:
        rows = conn.execute(sql, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_session_details(session_id: int) -> Optional[Dict[str, Any]]:
    """Fetch session row with associated mudra details."""
    sql = """
        SELECT s.*, m.name AS mudra_name, m.sanskrit AS mudra_sanskrit
        FROM practice_sessions s
        LEFT JOIN mudras m ON s.mudra_id = m.id
        WHERE s.id = ?
    """
    with _get_connection() as conn:
        row = conn.execute(sql, (session_id,)).fetchone()
        return dict(row) if row else None


def get_session_results(session_id: int) -> List[Dict[str, Any]]:
    """Fetch all recognition points for a given session."""
    sql = """
        SELECT r.*, m.name AS mudra_name
        FROM recognition_results r
        LEFT JOIN mudras m ON r.mudra_id = m.id
        WHERE r.session_id = ?
        ORDER BY r.timestamp ASC
    """
    with _get_connection() as conn:
        rows = conn.execute(sql, (session_id,)).fetchall()
        return [dict(r) for r in rows]
