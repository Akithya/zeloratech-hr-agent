import uuid
from fastapi import APIRouter, HTTPException
from app.models.schemas import HRRequest, AgentResponse
from app.agents.orchestrator import orchestrate
from app.audit import audit_log

router = APIRouter()

@router.post("/request", response_model=AgentResponse, summary="Submit an HR request")
async def handle_request(payload: HRRequest):
    try:
        request_id = str(uuid.uuid4())
        result = orchestrate(payload.user_id, payload.message)

        audit_log.append(
            request_id=request_id,
            user_id=payload.user_id,
            intent=result["intent"],
            confidence=result["confidence"],
            agent_used=result["agent_used"],
            request=payload.message,
            response=result["response"],
        )

        return AgentResponse(
            request_id=request_id,
            user_id=payload.user_id,
            **result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
