from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
def check_health():
    # Check if we have our Gemini key
    llm_status = bool(os.getenv("GEMINI_API_KEY"))
    status = "ok" if llm_status else "degraded"
    
    return {
        "status": status,
        "database": "ok",
        "llm_available": llm_status,
        "version": "1.0.0"
    }