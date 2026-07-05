"""
endpoints/search.py — Búsqueda global cross-módulo.
"""
from fastapi import APIRouter, Depends, Query

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.search_service import global_search

router = APIRouter()


@router.get("/global", summary="Búsqueda global en todos los módulos")
async def search_global(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=30),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await global_search(
        user_id=current_user["id"],
        query=q,
        supabase=supabase,
        limit=limit,
    )
