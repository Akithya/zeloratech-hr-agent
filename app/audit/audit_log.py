"""Append-only audit log stored in SQLite."""
from app.database import get_connection

def append(
    request_id: str,
    user_id: str,
    intent: str,
    confidence: float,
    agent_used: str,
    request: str,
    response: str,
):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO audit_log
            (request_id, user_id, intent, confidence, agent_used, request, response)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (request_id, user_id, intent, confidence, agent_used, request, response),
    )
    conn.commit()
    conn.close()

def fetch_all(user_id: str | None = None, limit: int = 100) -> list[dict]:
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
