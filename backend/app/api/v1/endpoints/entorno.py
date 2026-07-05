from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.services.farming_service import (
    get_plant_recommendation,
    check_harvest_readiness,
    generar_consejo_farming,
)
from app.services.weather_service import obtener_clima

router = APIRouter()


@router.get("/planta-recomendada", summary="Recomendar planta según emoción")
async def recomendar_planta(
    emocion_principal: str = "neutral",
    current_user=Depends(get_current_user),
):
    return get_plant_recommendation(emocion_principal)


@router.get("/cultivos", summary="Listar cultivos activos del usuario")
async def listar_cultivos(
    include_deleted: bool = False,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    query = (
        supabase.table("cultivos_activos")
        .select("*")
        .eq("user_id", current_user["id"])
        .eq("activo", True)
        .order("fecha_siembra", desc=False)
    )
    if not include_deleted:
        query = query.is_("deleted_at", "null")
    result = query.execute()
    return result.data


@router.delete("/cultivos/{cultivo_id}", summary="Soft-delete un cultivo")
async def eliminar_cultivo(
    cultivo_id: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    from datetime import datetime, timezone
    result = (
        supabase.table("cultivos_activos")
        .update({
            "deleted_at": datetime.now(timezone.utc).isoformat(),
            "deleted_by": current_user["id"],
        })
        .eq("id", cultivo_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    return {"message": "Cultivo marcado como eliminado", "can_restore": True, "crop": result.data[0] if result.data else None}


@router.post("/cultivos/{cultivo_id}/restore", summary="Restaurar cultivo eliminado")
async def restaurar_cultivo(
    cultivo_id: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    result = (
        supabase.table("cultivos_activos")
        .update({"deleted_at": None, "deleted_by": None})
        .eq("id", cultivo_id)
        .eq("user_id", current_user["id"])
        .execute()
    )
    return {"message": "Cultivo restaurado", "crop": result.data[0] if result.data else None}


@router.get("/cosecha-lista", summary="Verificar qué cultivos están listos para cosechar")
async def verificar_cosecha(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await check_harvest_readiness(current_user["id"], supabase)


@router.post("/consejo", summary="Consejo de farming personalizado con IA")
async def consejo_farming(
    consulta: str,
    estado_emocional: int = 5,
    emocion_principal: str = "neutral",
    current_user=Depends(get_current_user),
):
    return await generar_consejo_farming(
        consulta=consulta,
        estado_emocional=estado_emocional,
        emocion_principal=emocion_principal,
        user_id=current_user["id"],
    )


@router.get("/clima", summary="Clima actual para el usuario")
async def clima_actual(
    lat: float = 52.3676,
    lon: float = 4.9041,
    current_user=Depends(get_current_user),
):
    return await obtener_clima(lat, lon)


@router.post("/cultivos", summary="Añadir nuevo cultivo")
async def agregar_cultivo(
    nombre_planta: str,
    tipo: str,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    from datetime import date

    result = (
        supabase.table("cultivos_activos")
        .insert(
            {
                "user_id": current_user["id"],
                "nombre_planta": nombre_planta,
                "tipo": tipo,
                "estado": "semilla",
                "fecha_siembra": date.today().isoformat(),
                "activo": True,
            }
        )
        .execute()
    )
    return result.data[0] if result.data else {"error": "No se pudo crear el cultivo"}
