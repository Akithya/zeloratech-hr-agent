from fastapi import APIRouter, HTTPException
from app.models.schemas import MemoryEntry
from app.memory import memory_store

router = APIRouter()

@router.get("/memory/{user_id}", summary="Get all memory for a user")
async def get_memory(user_id: str):
    return {
        "user_id": user_id,
        "ltm": memory_store.ltm_get(user_id),
        "stm": memory_store.stm_get(user_id),
    }

@router.post("/memory/{user_id}/ltm", summary="Set a long-term memory fact")
async def set_ltm(user_id: str, entry: MemoryEntry):
    memory_store.ltm_set(user_id, entry.key, entry.value)
    return {"status": "ok", "user_id": user_id, "key": entry.key}

@router.delete("/memory/{user_id}/ltm/{key}", summary="Delete a long-term memory key")
async def delete_ltm(user_id: str, key: str):
    memory_store.ltm_delete(user_id, key)
    return {"status": "deleted", "user_id": user_id, "key": key}

@router.delete("/memory/{user_id}/stm", summary="Clear short-term memory for a user")
async def clear_stm(user_id: str):
    memory_store.stm_clear(user_id)
    return {"status": "cleared", "user_id": user_id}
