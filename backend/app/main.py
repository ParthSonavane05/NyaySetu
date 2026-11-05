"""
NYAYSETU FastAPI application entry point.

Mounts:
  /api/v1/matters  — Matter management (P06)
  /api/v1/dashboard — Dashboard summary (P06)
  /health           — Health check
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.modules.matters.router import router as matters_router

app = FastAPI(
    title="NYAYSETU API",
    description="Enterprise AI legal workspace for Indian law firms",
    version="0.6.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS — tighten origins in production via environment
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Override in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(matters_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", include_in_schema=False)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "version": "0.6.0"})
