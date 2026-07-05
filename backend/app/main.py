"""
main.py — Punto de entrada de ThriveMind API
"""
try:
    import truststore
    truststore.inject_into_ssl()  # Use Windows/macOS/Linux system cert store
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🌱 ThriveMind API arrancando en modo {settings.environment}")
    print(f"📖 Documentación: http://localhost:8000/docs")
    yield
    print("👋 ThriveMind API cerrando...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ecosistema de bienestar holístico orquestado por IA",
    lifespan=lifespan,
)

import os as _os
_extra_origins = [o.strip() for o in _os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        *_extra_origins,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
