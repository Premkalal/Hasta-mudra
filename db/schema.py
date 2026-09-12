"""
db/schema.py — SQLite Database Schema for HastaAI
Defines the 4 core relational tables:
1. users
2. mudras
3. practice_sessions
4. recognition_results
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    auth_provider TEXT NOT NULL DEFAULT 'local',
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mudras (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    sanskrit      TEXT NOT NULL,
    description   TEXT NOT NULL,
    significance  TEXT NOT NULL,
    instructions  TEXT,
    category      TEXT NOT NULL DEFAULT 'Asamyuta',
    image_ref     TEXT
);

CREATE TABLE IF NOT EXISTS practice_sessions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id            INTEGER NOT NULL,
    mudra_id           INTEGER,
    start_time         TEXT NOT NULL,
    end_time           TEXT,
    duration           REAL DEFAULT 0.0,
    average_confidence REAL DEFAULT 0.0,
    performance_score  REAL DEFAULT 0.0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (mudra_id) REFERENCES mudras(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS recognition_results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL,
    mudra_id    INTEGER,
    confidence  REAL NOT NULL,
    timestamp   TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (mudra_id) REFERENCES mudras(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON practice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_results_session ON recognition_results(session_id);
"""
