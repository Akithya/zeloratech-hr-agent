from fastapi import APIRouter, Query
from app.audit import audit_log

router = APIRouter()

@router.get("/audit", summary="Retrieve audit logs")
async def get_audit(
    user_id: str | None = Query(None, description="Filter by user ID"),
    limit:   int        = Query(100, ge=1, le=1000)
):
    return audit_log.fetch_all(user_id=user_id, limit=limit)
