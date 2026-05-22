from pydantic import BaseModel, Field
from typing import Optional, Any

class HRRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the employee")
    message: str = Field(..., description="Natural language HR request")

class AgentResponse(BaseModel):
    request_id: str
    user_id: str
    intent: str
    confidence: float
    agent_used: str
    response: str
    memory_injected: bool

class AuditEntry(BaseModel):
    id: int
    request_id: str
    user_id: str
    intent: str
    confidence: float
    agent_used: str
    request: str
    response: str
    timestamp: str

class MemoryEntry(BaseModel):
    key: str
    value: str

class HealthStatus(BaseModel):
    status: str
    database: str
    llm_available: bool
    version: str = "1.0.0"
