import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "hr_agent.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Audit log table (append-only)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id  TEXT NOT NULL,
            user_id     TEXT NOT NULL,
            intent      TEXT NOT NULL,
            confidence  REAL NOT NULL,
            agent_used  TEXT NOT NULL,
            request     TEXT NOT NULL,
            response    TEXT NOT NULL,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Short-term memory (STM) – recent context per user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stm (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            timestamp   TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Long-term memory (LTM) – persistent user facts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ltm (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT NOT NULL,
            key         TEXT NOT NULL,
            value       TEXT NOT NULL,
            updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, key)
        )
    """)

    conn.commit()
    conn.close()
