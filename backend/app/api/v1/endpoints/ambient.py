from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from app.core.auth import get_current_user
from app.services.hue_service import hue_service, PERFILES_TERAPEUTICOS

router = APIRouter()


class AmbientAutoRequest(BaseModel):
    mood_score: int
    energy_score: int
    objetivo: str


@router.get("/status", summary="Estado de la conexión con Philips Hue Bridge")
async def get_hue_status(current_user=Depends(get_current_user)):
    return hue_service.get_status()


@router.post("/apply/{profile_name}", summary="Aplicar perfil de iluminación específico")
async def apply_profile(
    profile_name: str,
    current_user=Depends(get_current_user),
):
    return hue_service.apply_profile(profile_name)


@router.post("/auto", summary="Selección automática de perfil basada en estado del usuario")
async def auto_ambient(
    request: AmbientAutoRequest,
    current_user=Depends(get_current_user),
):
    hora_actual = datetime.now().hour
    profile_name = hue_service.auto_select_profile(
        mood_score=request.mood_score,
        energy_score=request.energy_score,
        objetivo=request.objetivo,
        hora=hora_actual,
    )
    result = hue_service.apply_profile(profile_name)
    result["selected_profile"] = profile_name
    return result


@router.get("/profiles", summary="Lista todos los perfiles terapéuticos disponibles")
async def list_profiles(current_user=Depends(get_current_user)):
    return [
        {
            "name": name,
            "description": profile["descripcion"],
            "justificacion": profile["justificacion"],
        }
        for name, profile in PERFILES_TERAPEUTICOS.items()
    ]
