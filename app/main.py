from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import requests, audit, memory, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="ZeloraTech HR Automation Engine",
    description="Multi-agent task routing and memory engine for HR automation",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(requests.router, prefix="/api/v1", tags=["Requests"])
app.include_router(audit.router,    prefix="/api/v1", tags=["Audit"])
app.include_router(memory.router,   prefix="/api/v1", tags=["Memory"])
app.include_router(health.router,   prefix="/api/v1", tags=["Health"])
