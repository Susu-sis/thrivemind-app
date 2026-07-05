"""
services/orchestration_service.py — Holistic Recommendation Engine.

Closes the loop: Check-in → Context → 3-Pillar Action.
Combines the context engine, weather, knowledge base, and heuristics
to produce a unified, actionable recommendation across all pillars.
"""
import logging
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.services.context_engine import build_context, obtener_ventana_circadiana
from app.services.knowledge_base import WEATHER_MOOD_BASELINE

logger = logging.getLogger(__name__)

# ── Context resolution ───────────────────────────────────────────────────────

CONTEXT_LABELS = {
    "noche_sueno":         "Preparación para dormir",
    "amanecer_activacion": "Activación matutina",
    "enfoque_trabajo":     "Enfoque y productividad",
    "mediodia_reset":      "Pausa de mediodía",
    "tarde_desconexion":   "Desconexión vespertina",
    "noche_relajacion":    "Relajación nocturna",
}


def resolve_context_label(hour: int, mood: int, energy: int, weather_cond: str = "") -> str:
    if hour >= 22 or hour < 6:
        return "noche_sueno"
    if 6 <= hour < 9:
        return "amanecer_activacion"
    if 9 <= hour < 12:
        return "enfoque_trabajo"
    if 12 <= hour < 14:
        return "mediodia_reset"
    if 14 <= hour < 18:
        if mood <= 4:
            return "tarde_desconexion"
        return "enfoque_trabajo"
    return "noche_relajacion"


# ── Pillar heuristics ────────────────────────────────────────────────────────

HUE_PROFILE_MAP = {
    "amanecer_activacion": {"perfil": "meditacion_energia", "kelvin": 5500, "brillo": 70},
    "enfoque_trabajo":     {"perfil": "meditacion_enfoque", "kelvin": 5000, "brillo": 80},
    "mediodia_reset":      {"perfil": "meditacion_enfoque", "kelvin": 4000, "brillo": 60},
    "tarde_desconexion":   {"perfil": "meditacion_calma",   "kelvin": 2700, "brillo": 40},
    "noche_relajacion":    {"perfil": "meditacion_calma",   "kelvin": 2200, "brillo": 30},
    "noche_sueno":         {"perfil": "descanso_nocturno",  "kelvin": 1800, "brillo": 10},
}

MEDITATION_MAP = {
    "amanecer_activacion": {"objetivo": "energia",  "titulo": "Despertar con energía"},
    "enfoque_trabajo":     {"objetivo": "enfoque",  "titulo": "Concentración profunda"},
    "mediodia_reset":      {"objetivo": "calma",    "titulo": "Pausa consciente"},
    "tarde_desconexion":   {"objetivo": "calma",    "titulo": "Soltar el día"},
    "noche_relajacion":    {"objetivo": "sueno",    "titulo": "Relajación pre-sueño"},
    "noche_sueno":         {"objetivo": "sueno",    "titulo": "Preparación para dormir"},
}

NUTRITION_MAP = {
    "amanecer_activacion": {"grupo": "proteína + carbohidratos complejos",
                            "ejemplo": "Avena con nueces y plátano",
                            "razon": "Activa serotonina y dopamina matutinas"},
    "enfoque_trabajo":     {"grupo": "ácidos grasos omega-3 + antioxidantes",
                            "ejemplo": "Salmón con verduras de hoja verde",
                            "razon": "Apoya la función cognitiva y concentración"},
    "mediodia_reset":      {"grupo": "proteína magra + fibra",
                            "ejemplo": "Pollo a la plancha con quinoa y brócoli",
                            "razon": "Evita el bajón post-almuerzo"},
    "tarde_desconexion":   {"grupo": "magnesio + triptófano",
                            "ejemplo": "Yogur con semillas de calabaza",
                            "razon": "Prepara el cuerpo para la relajación"},
    "noche_relajacion":    {"grupo": "carbohidratos ligeros + magnesio",
                            "ejemplo": "Infusión de manzanilla con galletas integrales",
                            "razon": "Favorece la producción de melatonina"},
    "noche_sueno":         {"grupo": "evitar estimulantes",
                            "ejemplo": "Leche tibia con miel",
                            "razon": "Promueve el sueño reparador"},
}

PLANT_ACTION_MAP = {
    "amanecer_activacion": "Regar tus plantas (actividad mindful matutina)",
    "enfoque_trabajo":     "Observar el crecimiento de tu planta (pausa visual)",
    "mediodia_reset":      "Verificar humedad del sustrato",
    "tarde_desconexion":   "Podar hojas secas (actividad terapéutica)",
    "noche_relajacion":    "Disfrutar el aroma de tus hierbas",
    "noche_sueno":         "Planificar el riego de mañana",
}


async def generate_holistic_recommendation(
    user_id: str,
    checkin_data: Optional[dict] = None,
    clima: Optional[dict] = None,
    hora: Optional[int] = None,
) -> dict:
    """
    Produce an integrated 3-pillar recommendation from user state + context.
    Works completely offline (no LLM call) using heuristic maps.
    """
    if hora is None:
        hora = datetime.now().hour

    mood = (checkin_data or {}).get("estado_emocional", 5)
    energy = (checkin_data or {}).get("energia_fisica", 5)
    sleep = (checkin_data or {}).get("horas_sueno", 7)
    emotion = (checkin_data or {}).get("emocion_principal", "neutral")
    weather_cond = (clima or {}).get("condicion", "")

    ctx_key = resolve_context_label(hora, mood, energy, weather_cond)
    ctx_label = CONTEXT_LABELS.get(ctx_key, ctx_key)

    # Weather insight
    weather_insight = None
    if clima:
        kb_key = clima.get("clasificacion_kb", "")
        wb = WEATHER_MOOD_BASELINE.get(kb_key)
        if wb:
            weather_insight = wb.get("consejo")

    # Build response
    med = MEDITATION_MAP.get(ctx_key, MEDITATION_MAP["noche_relajacion"])
    hue = HUE_PROFILE_MAP.get(ctx_key, HUE_PROFILE_MAP["noche_relajacion"])
    nut = NUTRITION_MAP.get(ctx_key, NUTRITION_MAP["noche_relajacion"])
    plant_action = PLANT_ACTION_MAP.get(ctx_key, "Cuidar tus plantas")

    # Mood-specific overrides
    urgency = None
    if mood <= 3:
        med = {"objetivo": "calma", "titulo": "Meditación de calma urgente"}
        hue = {"perfil": "meditacion_calma", "kelvin": 2200, "brillo": 30}
        urgency = "Tu estado emocional es bajo. Se priorizaron acciones de calma."
    if energy <= 3 and mood > 3:
        nut = {
            "grupo": "proteína + carbohidratos complejos",
            "ejemplo": "Batido de proteínas con plátano y avena",
            "razon": "Te ayudará a recuperar energía rápidamente",
        }

    return {
        "context_key": ctx_key,
        "context_label": ctx_label,
        "hora": hora,
        "urgency": urgency,
        "weather_insight": weather_insight,
        "estado": {
            "emocional": mood,
            "energia": energy,
            "sueno": sleep,
            "emocion": emotion,
        },
        "pillar_mente": {
            "meditacion": {
                "titulo": med["titulo"],
                "objetivo": med["objetivo"],
                "duracion_min": 10,
            },
            "hue": {
                "perfil": hue["perfil"],
                "kelvin": hue["kelvin"],
                "brillo_pct": hue["brillo"],
                "descripcion": f"Luz {hue['kelvin']}K al {hue['brillo']}%",
            },
        },
        "pillar_cuerpo": {
            "nutricion": {
                "grupo_alimenticio": nut["grupo"],
                "ejemplo_comida": nut["ejemplo"],
                "razon": nut["razon"],
            },
        },
        "pillar_entorno": {
            "planta_accion": plant_action,
            "clima": {
                "descripcion": (clima or {}).get("descripcion", "No disponible"),
                "temperatura": (clima or {}).get("temperatura"),
            },
        },
        "timestamp": datetime.now().isoformat(),
    }
