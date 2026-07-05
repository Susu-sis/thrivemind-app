"""
endpoints/gamification.py — Puntos, hitos y progresión del usuario.
"""
from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.gamification_service import award_points, get_user_gamification

router = APIRouter()


@router.get("/", summary="Obtener puntos y hitos del usuario")
async def get_gamification(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await get_user_gamification(current_user["id"], supabase)


@router.post("/award", summary="Otorgar puntos por acción")
async def post_award(
    action: str,
    referencia_id: str = None,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await award_points(current_user["id"], action, supabase, referencia_id)
