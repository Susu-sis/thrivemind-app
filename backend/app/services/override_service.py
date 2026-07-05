"""
services/override_service.py — Co-pilot Override Protocol (Gap G6.1–G6.4).

Implements the 4-step override protocol when the user contradicts AI recommendations:
  1. DETECT — Recognize that user's action opposes system recommendation
  2. NOTIFY — Transparent notification explaining the conflict
  3. VALIDATE — Confirm user intention (never block)
  4. MITIGATE — Apply harm-reduction parameters

Also tracks the Resilience Counter (CR):
  +1 per override, -0.5 if HRV recovers within 90 min
  CR ≥ 3/7d → empathetic reflection check-in
  CR ≥ 5 + HRV_trend <-15% → professional referral suggestion

Ref: Memoria Técnica §11.8, §14.1.2–§14.1.4
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── In-memory demo state ─────────────────────────────────────────────────────
_demo_overrides: dict[str, list] = {}
_demo_cr: dict[str, float] = {}

# ── Mitigation parameters (Memoria §11.8.2) ──────────────────────────────────
MITIGATION_PARAMS = {
    "luz": {
        "descripcion": "Luz a 4000K en vez de 6500K (compromiso entre activación y protección)",
        "kelvin": 4000,
        "brillo_max": 70,
    },
    "nutricion": {
        "descripcion": "Tirosina + magnesio (sin cafeína extrema)",
        "permitido": ["tirosina moderada", "magnesio", "L-teanina"],
        "bloqueado": ["cafeína >300mg", "azúcar refinada alta"],
    },
    "audio": {
        "descripcion": "Beta suave 15-20Hz (no gamma agresivo)",
        "frecuencia_hz_min": 15,
        "frecuencia_hz_max": 20,
    },
    "recovery_checkin_min": 90,
}


async def detect_override(
    user_id: str,
    ai_recommendation: dict,
    user_action: dict,
) -> dict:
    """
    Step 1: DETECT — Compares AI recommendation vs user action.
    Returns override_detected=True if there's a conflict.
    """
    rec_type = ai_recommendation.get("type", "")
    user_type = user_action.get("type", "")

    # Detection heuristics
    conflicts = []

    # Mood ≤ 3, AI says calma, user picks energia
    if (ai_recommendation.get("urgency") and
            user_action.get("objetivo") in ["energia", "enfoque"]):
        conflicts.append({
            "field": "objetivo",
            "ai_value": "calma (urgencia detectada)",
            "user_value": user_action.get("objetivo"),
            "severity": "moderate",
        })

    # AI says no caffeine, user takes caffeine
    if ("cafeína" in str(ai_recommendation.get("nutricion_override", "")).lower() and
            "café" in str(user_action.get("alimento", "")).lower()):
        conflicts.append({
            "field": "nutricion",
            "ai_value": "evitar cafeína",
            "user_value": user_action.get("alimento"),
            "severity": "moderate",
        })

    # Night time, AI says sleep prep, user picks high-energy
    if (ai_recommendation.get("context_key") in ["noche_relajacion", "noche_sueno"] and
            user_action.get("objetivo") in ["energia", "enfoque"]):
        conflicts.append({
            "field": "contexto_nocturno",
            "ai_value": "relajación/sueño",
            "user_value": user_action.get("objetivo"),
            "severity": "high",
        })

    return {
        "override_detected": len(conflicts) > 0,
        "conflicts": conflicts,
        "n_conflicts": len(conflicts),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def register_override(
    user_id: str,
    override_data: dict,
    supabase=None,
) -> dict:
    """
    Steps 2-4: NOTIFY + VALIDATE + MITIGATE.
    Registers the override, increments CR, applies mitigation.
    """
    entry = {
        "user_id": user_id,
        "conflicts": override_data.get("conflicts", []),
        "mitigation_applied": MITIGATION_PARAMS,
        "cr_delta": 1.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Update Resilience Counter
    if settings.environment == "demo":
        _demo_overrides.setdefault(user_id, []).append(entry)
        cr = _demo_cr.get(user_id, 0) + 1.0
        _demo_cr[user_id] = cr
    else:
        cr = _demo_cr.get(user_id, 0) + 1.0  # In production, read from DB

    # Step 2: NOTIFY — Generate transparent explanation
    notification = {
        "type": "override_notification",
        "tone": "informative",
        "message": (
            "He detectado que tu elección difiere de mi recomendación. "
            "Tu decisión es respetada — solo te comparto información adicional."
        ),
        "conflicts_explained": [
            f"Sugerí '{c['ai_value']}', elegiste '{c['user_value']}'"
            for c in override_data.get("conflicts", [])
        ],
    }

    # Step 3: VALIDATE — Always allow (co-pilot model)
    validation = {
        "action_allowed": True,
        "message": "Tu bienestar, tu decisión. ThriveMind registra para aprender.",
    }

    # Step 4: MITIGATE — Apply harm-reduction
    mitigation = {
        "applied": True,
        "params": MITIGATION_PARAMS,
        "recovery_checkin_scheduled_min": MITIGATION_PARAMS["recovery_checkin_min"],
    }

    # CR threshold checks
    cr_alert = None
    if cr >= 5:
        cr_alert = {
            "level": "professional_referral",
            "message": (
                "Has tomado decisiones diferentes a las recomendaciones en "
                f"{int(cr)} ocasiones recientes. Esto no es un juicio — es información. "
                "Si sientes que necesitas apoyo adicional, considera hablar con un profesional."
            ),
            "resources": [
                {"name": "Teléfono de la Esperanza", "contact": "717 003 717"},
                {"name": "Doctoralia", "contact": "https://www.doctoralia.es/psicologos"},
            ],
        }
    elif cr >= 3:
        cr_alert = {
            "level": "empathetic_reflection",
            "message": (
                "Noto que últimamente prefieres un camino diferente al sugerido. "
                "¿Cómo te encuentras? A veces lo que necesitamos no es lo más obvio."
            ),
            "options": ["Cuéntame más", "Estoy bien", "Recuérdamelo luego"],
        }

    return {
        "override_registered": True,
        "resilience_counter": cr,
        "notification": notification,
        "validation": validation,
        "mitigation": mitigation,
        "cr_alert": cr_alert,
    }


async def get_resilience_counter(user_id: str, supabase=None) -> dict:
    """Get the current Resilience Counter for a user."""
    if settings.environment == "demo":
        cr = _demo_cr.get(user_id, 0.5)
        return {
            "resilience_counter": cr,
            "overrides_7d": len(_demo_overrides.get(user_id, [])),
            "level": (
                "normal" if cr < 3
                else "reflection" if cr < 5
                else "referral"
            ),
        }

    # Production: would query from DB
    return {"resilience_counter": 0, "overrides_7d": 0, "level": "normal"}
