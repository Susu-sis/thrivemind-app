"""
endpoints/meal_planner.py — Planificador de menú semanal.
"""
from fastapi import APIRouter, Depends
from typing import Optional

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.meal_planner_service import generate_weekly_plan

router = APIRouter()


@router.get("/weekly", summary="Generar plan nutricional semanal")
async def get_weekly_plan(
    objetivo: str = "equilibrio",
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await generate_weekly_plan(
        user_id=current_user["id"],
        objetivo=objetivo,
        supabase=supabase,
    )
