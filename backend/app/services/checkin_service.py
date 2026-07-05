"""
services/checkin_service.py — Lógica de negocio de check-ins de bienestar.
"""
import uuid
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.core.database import get_supabase_client


def calcular_racha(checkins: list) -> int:
    """
    Calcula la racha de días consecutivos con check-in.
    Recibe check-ins ordenados por created_at DESC.
    """
    if not checkins:
        return 0

    hoy = datetime.now(timezone.utc).date()
    racha = 0
    dia_esperado = hoy

    for c in checkins:
        created = c.get("created_at", "")
        if isinstance(created, str) and len(created) >= 10:
            dia_checkin = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
        else:
            continue

        if dia_checkin == dia_esperado:
            racha += 1
            dia_esperado -= timedelta(days=1)
        elif dia_checkin < dia_esperado:
            break

    return racha


def guardar_checkin(datos: dict) -> dict | None:
    """
    Guarda un check-in de bienestar en Supabase.

    Parámetros:
        datos: Diccionario con los campos del check-in.
    Devuelve:
        El registro creado (con su ID) o None si hubo un error.
    """
    if settings.environment == "demo":
        from datetime import datetime, timezone
        return {**datos, "id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat()}

    try:
        supabase = get_supabase_client()
        response = supabase.table("checkins").insert(datos).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error al guardar check-in: {e}")
        return None
