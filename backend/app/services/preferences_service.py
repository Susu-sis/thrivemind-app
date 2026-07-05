"""
services/preferences_service.py — Lógica de negocio de preferencias de pilares.
"""
from supabase import Client
from app.models.preferences import UserPreferencesUpdate, UserPreferencesResponse
import logging

logger = logging.getLogger(__name__)


async def get_user_preferences(user_id: str, supabase) -> UserPreferencesResponse:
    """Obtiene las preferencias del usuario, creándolas si no existen."""
    result = supabase.table("user_preferences") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    if not result.data:
        default_prefs = {
            "user_id": user_id,
            "mente_activo": True,
            "cuerpo_activo": True,
            "entorno_activo": True,
            "mente_intensidad": 1,
            "cuerpo_intensidad": 1,
            "entorno_intensidad": 1,
            "objetivo_principal": "equilibrio",
            "frecuencia_checkin": "diario",
            "alergias": [],
            "preferencia_dieta": "sin_restriccion",
            "presupuesto_semanal": "medio",
            "objetivo_fitness": "mantener",
        }
        result = supabase.table("user_preferences").insert(default_prefs).execute()
        return UserPreferencesResponse(**result.data[0])

    return UserPreferencesResponse(**result.data[0])


async def update_user_preferences(
    user_id: str, updates: UserPreferencesUpdate, supabase
) -> UserPreferencesResponse:
    """Actualiza las preferencias del usuario."""
    update_data = {}

    if updates.mente is not None:
        update_data["mente_activo"] = updates.mente.activo
        update_data["mente_intensidad"] = updates.mente.intensidad
    if updates.cuerpo is not None:
        update_data["cuerpo_activo"] = updates.cuerpo.activo
        update_data["cuerpo_intensidad"] = updates.cuerpo.intensidad
    if updates.entorno is not None:
        update_data["entorno_activo"] = updates.entorno.activo
        update_data["entorno_intensidad"] = updates.entorno.intensidad
    if updates.objetivo_principal is not None:
        update_data["objetivo_principal"] = updates.objetivo_principal
    if updates.frecuencia_checkin is not None:
        update_data["frecuencia_checkin"] = updates.frecuencia_checkin
    if updates.alergias is not None:
        update_data["alergias"] = updates.alergias
    if updates.preferencia_dieta is not None:
        update_data["preferencia_dieta"] = updates.preferencia_dieta
    if updates.presupuesto_semanal is not None:
        update_data["presupuesto_semanal"] = updates.presupuesto_semanal
    if updates.objetivo_fitness is not None:
        update_data["objetivo_fitness"] = updates.objetivo_fitness

    if not update_data:
        return await get_user_preferences(user_id, supabase)

    result = supabase.table("user_preferences") \
        .update(update_data) \
        .eq("user_id", user_id) \
        .execute()

    return UserPreferencesResponse(**result.data[0])


def build_pillar_context(prefs: UserPreferencesResponse) -> str:
    """Construye el contexto de pilares activos para inyectar en los prompts de IA."""
    intensidad_labels = {1: "básica", 2: "intermedia", 3: "avanzada"}
    objetivo_labels = {
        "equilibrio": "equilibrio holístico",
        "reducir_estres": "reducción del estrés",
        "mejorar_sueno": "mejora del sueño",
        "aumentar_energia": "aumento de energía",
        "conexion_naturaleza": "conexión con la naturaleza",
        "rendimiento_cognitivo": "rendimiento cognitivo",
    }

    partes_activas = []
    partes_inactivas = []

    for pilar, label in [("mente", "Mente"), ("cuerpo", "Cuerpo"), ("entorno", "Entorno")]:
        activo = getattr(prefs, f"{pilar}_activo")
        if activo:
            nivel = intensidad_labels[getattr(prefs, f"{pilar}_intensidad")]
            partes_activas.append(f"{label} (intensidad {nivel})")
        else:
            partes_inactivas.append(label)

    objetivo = objetivo_labels.get(prefs.objetivo_principal, prefs.objetivo_principal)
    activos_str = " y ".join(partes_activas) if partes_activas else "ninguno"

    context = f"El usuario tiene activos los pilares: {activos_str}. "
    context += f"Objetivo principal: {objetivo}. "

    if partes_inactivas:
        inactivos_str = ", ".join(partes_inactivas)
        context += (
            f"Los siguientes pilares están DESACTIVADOS: {inactivos_str}. "
            f"NO hagas referencias a estos pilares en tus respuestas."
        )

    return context
