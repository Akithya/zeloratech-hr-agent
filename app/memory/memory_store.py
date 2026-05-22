"""
Two-Tier Memory System
- STM (Short-Term Memory): last N conversation turns per user
- LTM (Long-Term Memory): persistent key-value facts per user
"""
from app.database import get_connection

STM_LIMIT = 10  # keep last 10 messages per user

# ── STM ──────────────────────────────────────────────────────────────────────

def stm_add(user_id: str, role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO stm (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()
    _stm_trim(user_id)

def stm_get(user_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT role, content FROM stm
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (user_id, STM_LIMIT)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

def stm_clear(user_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM stm WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def _stm_trim(user_id: str):
    conn = get_connection()
    conn.execute(
        """
        DELETE FROM stm WHERE id IN (
            SELECT id FROM stm WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT -1 OFFSET ?
        )
        """,
        (user_id, STM_LIMIT)
    )
    conn.commit()
    conn.close()

# ── LTM ──────────────────────────────────────────────────────────────────────

def ltm_set(user_id: str, key: str, value: str):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO ltm (user_id, key, value, updated_at)
        VALUES (?, ?, ?, datetime('now'))
        ON CONFLICT(user_id, key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """,
        (user_id, key, value)
    )
    conn.commit()
    conn.close()

def ltm_get(user_id: str) -> dict[str, str]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT key, value FROM ltm WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

def ltm_delete(user_id: str, key: str):
    conn = get_connection()
    conn.execute("DELETE FROM ltm WHERE user_id = ? AND key = ?", (user_id, key))
    conn.commit()
    conn.close()

# ── Combined context builder ──────────────────────────────────────────────────

def build_memory_context(user_id: str) -> str:
    """Return a formatted string to inject into an agent prompt."""
    ltm = ltm_get(user_id)
    stm = stm_get(user_id)

    parts = []
    if ltm:
        facts = "\n".join(f"  - {k}: {v}" for k, v in ltm.items())
        parts.append(f"[Long-term facts about this employee]\n{facts}")

    if stm:
        history = "\n".join(f"  {m['role'].upper()}: {m['content']}" for m in stm)
        parts.append(f"[Recent conversation history]\n{history}")

    return "\n\n".join(parts) if parts else ""
