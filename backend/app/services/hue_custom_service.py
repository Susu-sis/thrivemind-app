"""
services/hue_custom_service.py — Perfiles personalizados de iluminación Philips Hue.

Permite a usuarios crear, aplicar y listar perfiles custom además de los predefinidos.
"""
from app.core.config import settings

# Predefined profiles (always available)
PREDEFINED_PROFILES = [
    {"id": "meditacion_calma", "name": "Meditación Calma", "kelvin": 2700, "brightness": 40, "is_custom": False},
    {"id": "meditacion_enfoque", "name": "Meditación Enfoque", "kelvin": 4000, "brightness": 60, "is_custom": False},
    {"id": "meditacion_energia", "name": "Meditación Energía", "kelvin": 5500, "brightness": 70, "is_custom": False},
    {"id": "lectura_nocturna", "name": "Lectura Nocturna", "kelvin": 2500, "brightness": 30, "is_custom": False},
    {"id": "despertar_suave", "name": "Despertar Suave", "kelvin": 3500, "brightness": 50, "is_custom": False},
    {"id": "trabajo_productivo", "name": "Trabajo Productivo", "kelvin": 5000, "brightness": 80, "is_custom": False},
    {"id": "relajacion_profunda", "name": "Relajación Profunda", "kelvin": 2200, "brightness": 20, "is_custom": False},
    {"id": "yoga_ambiente", "name": "Yoga Ambiente", "kelvin": 3000, "brightness": 35, "is_custom": False},
    {"id": "cena_social", "name": "Cena Social", "kelvin": 2700, "brightness": 50, "is_custom": False},
    {"id": "naturaleza_indoor", "name": "Naturaleza Indoor", "kelvin": 4500, "brightness": 65, "is_custom": False},
    {"id": "noche_estrellada", "name": "Noche Estrellada", "kelvin": 2000, "brightness": 15, "is_custom": False},
]

# Demo custom profiles
_demo_custom: dict[str, list] = {}


async def get_all_profiles(user_id: str, supabase=None) -> list:
    """Return predefined + user custom profiles."""
    custom = []
    if settings.environment == "demo":
        custom = _demo_custom.get(user_id, [])
    else:
        resp = (
            supabase.table("hue_profiles")
            .select("*")
            .eq("user_id", user_id)
            .eq("is_custom", True)
            .execute()
        )
        custom = resp.data or []

    return PREDEFINED_PROFILES + custom


async def create_custom_profile(
    user_id: str,
    name: str,
    kelvin: int,
    brightness: int,
    color_hex: str | None = None,
    description: str = "",
    supabase=None,
) -> dict:
    """Create a user custom profile."""
    if not (2000 <= kelvin <= 6500):
        return {"error": "Kelvin debe estar entre 2000 y 6500"}
    if not (0 <= brightness <= 100):
        return {"error": "Brightness debe estar entre 0 y 100"}

    profile = {
        "user_id": user_id,
        "name": name,
        "kelvin": kelvin,
        "brightness": brightness,
        "color_hex": color_hex,
        "description": description,
        "is_custom": True,
    }

    if settings.environment == "demo":
        import uuid
        profile["id"] = str(uuid.uuid4())
        _demo_custom.setdefault(user_id, []).append(profile)
        return {"profile": profile, "message": "Perfil personalizado creado"}

    resp = supabase.table("hue_profiles").insert(profile).execute()
    return {"profile": resp.data[0] if resp.data else profile, "message": "Perfil personalizado creado"}


async def delete_custom_profile(user_id: str, profile_id: str, supabase=None) -> dict:
    """Delete a user custom profile."""
    if settings.environment == "demo":
        profiles = _demo_custom.get(user_id, [])
        _demo_custom[user_id] = [p for p in profiles if p.get("id") != profile_id]
        return {"message": "Perfil eliminado"}

    supabase.table("hue_profiles").delete().eq("id", profile_id).eq("user_id", user_id).execute()
    return {"message": "Perfil eliminado"}
