"""
endpoints/meal_planner.py — Planificador de menú semanal.
"""
from fastapi import APIRouter, Depends
from typing import Optional

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.meal_planner_service import generate_weekly_plan
from app.services.preferences_service import get_user_preferences

router = APIRouter()


@router.get("/weekly", summary="Generar plan nutricional semanal")
async def get_weekly_plan(
    objetivo: str = "equilibrio",
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    prefs = await get_user_preferences(current_user["id"], supabase)
    target_kcal = prefs.tdee

    # Fetch last check-in for state-aware nota_hoy
    last_checkin = None
    try:
        result = supabase.table("checkins") \
            .select("estado_emocional,energia_fisica,emocion_principal") \
            .eq("user_id", current_user["id"]) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        if result.data:
            last_checkin = result.data[0]
    except Exception:
        pass

    return await generate_weekly_plan(
        user_id=current_user["id"],
        objetivo=objetivo,
        supabase=supabase,
        target_kcal=target_kcal,
        last_checkin=last_checkin,
    )
