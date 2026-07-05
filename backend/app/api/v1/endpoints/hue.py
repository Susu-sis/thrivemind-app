"""
endpoints/hue.py — Perfiles de iluminación Philips Hue.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.hue_custom_service import get_all_profiles, create_custom_profile, delete_custom_profile

router = APIRouter()


class HueProfileCreate(BaseModel):
    name: str
    kelvin: int
    brightness: int
    color_hex: Optional[str] = None
    description: str = ""


@router.get("/profiles", summary="Listar perfiles predefinidos + custom")
async def list_profiles(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await get_all_profiles(current_user["id"], supabase)


@router.post("/profiles/custom", summary="Crear perfil personalizado")
async def create_profile(
    body: HueProfileCreate,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await create_custom_profile(
        user_id=current_user["id"],
        name=body.name,
        kelvin=body.kelvin,
        brightness=body.brightness,
        color_hex=body.color_hex,
        description=body.description,
        supabase=supabase,
    )


@router.delete("/profiles/{profile_id}", summary="Eliminar perfil custom")
async def delete_profile(
    profile_id: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await delete_custom_profile(current_user["id"], profile_id, supabase)
