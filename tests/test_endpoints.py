"""
Integration tests for all 5 API endpoints.
Run: pytest tests/test_endpoints.py -v
Requires: ANTHROPIC_API_KEY in environment (or .env)
"""
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()
os.environ.setdefault("DB_PATH", ":memory:")  # use in-memory DB for tests

from app.main import app

client = TestClient(app)

# ── 1. Health ─────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert "database" in body
    assert "llm_available" in body

# ── 2. POST /request ──────────────────────────────────────────────────────────

@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="No API key")
def test_post_request_leave():
    r = client.post("/api/v1/request", json={
        "user_id": "emp_001",
        "message": "I need to take 3 days of sick leave next week."
    })
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] in ("leave", "scheduling", "compliance", "clarification")
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["response"]
    assert body["request_id"]

@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="No API key")
def test_post_request_scheduling():
    r = client.post("/api/v1/request", json={
        "user_id": "emp_002",
        "message": "Can you schedule a performance review meeting for Friday?"
    })
    assert r.status_code == 200
    body = r.json()
    assert body["agent_used"].endswith("_agent")

# ── 3. GET /audit ─────────────────────────────────────────────────────────────

def test_get_audit():
    r = client.get("/api/v1/audit")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_get_audit_filtered():
    r = client.get("/api/v1/audit?user_id=emp_001&limit=10")
    assert r.status_code == 200

# ── 4. Memory endpoints ───────────────────────────────────────────────────────

def test_memory_set_and_get():
    # Set LTM
    r = client.post("/api/v1/memory/emp_003/ltm", json={
        "key": "department", "value": "Engineering"
    })
    assert r.status_code == 200

    # Get memory
    r = client.get("/api/v1/memory/emp_003")
    assert r.status_code == 200
    body = r.json()
    assert body["ltm"]["department"] == "Engineering"

def test_memory_delete_ltm():
    client.post("/api/v1/memory/emp_004/ltm", json={"key": "role", "value": "Dev"})
    r = client.delete("/api/v1/memory/emp_004/ltm/role")
    assert r.status_code == 200

def test_memory_clear_stm():
    r = client.delete("/api/v1/memory/emp_005/stm")
    assert r.status_code == 200
