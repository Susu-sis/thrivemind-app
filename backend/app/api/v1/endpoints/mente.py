from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_supabase
from app.core.demo import demo_meditacion
from app.services.meditation_service import generar_meditacion, generar_audio_meditacion

router = APIRouter()


class MeditacionRequest(BaseModel):
    intencion: str
    objetivo: str  # 'calma', 'enfoque', 'gratitud', 'energia', 'sueno', 'ansiedad'
    duracion_min: int = 10
    checkin_id: Optional[str] = None
    generar_audio: bool = False


@router.post("/generar", summary="Generar sesión de meditación personalizada")
async def generar_sesion(
    request: MeditacionRequest,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    # Obtener el último check-in para contexto emocional
    checkin_result = (
        supabase.table("checkins")
        .select("estado_emocional, emocion_principal, energia_fisica")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if checkin_result.data:
        c = checkin_result.data[0]
        estado_emocional = c["estado_emocional"]
        emocion_principal = c.get("emocion_principal", "neutral")
        energia_fisica = c["energia_fisica"]
    else:
        estado_emocional, emocion_principal, energia_fisica = 5, "neutral", 5

    # Demo mode: return pre-written meditation without calling OpenAI
    if settings.environment == "demo":
        demo = demo_meditacion(objetivo=request.objetivo, duracion=request.duracion_min)
        return demo

    checkin_data = {
        "estado_emocional": estado_emocional,
        "emocion_principal": emocion_principal,
        "energia_fisica": energia_fisica,
    }

    resultado = await generar_meditacion(
        user_id=current_user["id"],
        checkin_data=checkin_data,
        supabase=supabase,
        objetivo=request.objetivo,
        duracion_minutos=request.duracion_min,
    )

    audio_url = None
    if request.generar_audio:
        audio_url = await generar_audio_meditacion(resultado.get("guion_meditacion", ""))

    insert_result = (
        supabase.table("meditation_sessions")
        .insert(
            {
                "user_id": current_user["id"],
                "checkin_id": request.checkin_id,
                "intencion": request.intencion,
                "duracion_min": request.duracion_min,
                "objetivo": request.objetivo,
                "tecnica": resultado.get("tecnica", request.objetivo),
                "guion_meditacion": resultado.get("guion_meditacion", ""),
                "audio_url": audio_url,
                "referencias_rag": resultado.get("evidencia_cientifica", []),
            }
        )
        .execute()
    )

    session = insert_result.data[0] if insert_result.data else {}
    return {
        "id": session.get("id", ""),
        "guion": resultado.get("guion_meditacion", ""),
        "tecnica": resultado.get("tecnica", request.objetivo),
        "audio_url": audio_url,
        "duracion_min": request.duracion_min,
        "referencias": resultado.get("evidencia_cientifica", []),
    }


@router.get("/historial", summary="Historial de meditaciones")
async def get_historial(
    limit: int = 10,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    result = (
        supabase.table("meditation_sessions")
        .select(
            "id, intencion, objetivo, tecnica, duracion_min, "
            "completada, valoracion, referencias_rag, created_at"
        )
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
