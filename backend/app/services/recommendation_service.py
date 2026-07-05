"""
services/recommendation_service.py — Personalized rule-based recommendations.

Analyzes recent check-in history and generates actionable suggestions
per pillar, including plant care reminders and trend-based advice.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


async def get_personalized_recommendations(
    user_id: str, checkins: list, cultivos: list
) -> list:
    """
    Generate recommendations from the last 7 check-ins + active crops.
    Pure heuristic — no LLM or API calls.
    """
    recs: list[dict] = []

    if not checkins:
        recs.append({
            "type": "checkin",
            "icon": "✍️",
            "title": "Completa tu primer check-in",
            "reason": "Aún no tenemos datos. Tu primer registro activa todo el sistema.",
            "action_label": "Ir a Check-in",
            "action_href": "/dashboard/checkin",
        })
        return recs

    # Averages from recent check-ins (up to 7)
    recent = checkins[:7]
    n = len(recent)
    avg_mood = sum(c.get("estado_emocional", 5) for c in recent) / n
    avg_energy = sum(c.get("energia_fisica", 5) for c in recent) / n
    avg_sleep = sum(c.get("horas_sueno", 7) for c in recent) / n
    avg_entorno = sum(c.get("conexion_entorno", 5) for c in recent) / n

    # Mood-based
    if avg_mood <= 4:
        recs.append({
            "type": "meditation",
            "icon": "🧘",
            "title": "Meditación de calma recomendada",
            "reason": f"Tu estado emocional promedio fue {avg_mood:.1f}/10 esta semana.",
            "action_label": "Generar meditación",
            "action_href": "/dashboard/mente",
        })
    elif avg_mood >= 7:
        recs.append({
            "type": "meditation",
            "icon": "🙏",
            "title": "Meditación de gratitud",
            "reason": "Tu bienestar ha sido alto — refuérzalo con gratitud.",
            "action_label": "Generar meditación",
            "action_href": "/dashboard/mente",
        })

    # Energy-based
    if avg_energy <= 4:
        recs.append({
            "type": "nutrition",
            "icon": "🥗",
            "title": "Aumentar proteína y carbohidratos complejos",
            "reason": f"Tu energía promedio fue {avg_energy:.1f}/10. La nutrición puede ayudar.",
            "action_label": "Analizar comida",
            "action_href": "/dashboard/cuerpo",
        })

    # Sleep-based
    if avg_sleep < 6:
        recs.append({
            "type": "sleep",
            "icon": "😴",
            "title": "Mejorar higiene del sueño",
            "reason": f"Dormiste un promedio de {avg_sleep:.1f}h. Se recomiendan 7-8h.",
            "action_label": "Ver meditación de sueño",
            "action_href": "/dashboard/mente",
        })

    # Entorno connection
    if avg_entorno <= 4:
        recs.append({
            "type": "farming",
            "icon": "🌱",
            "title": "Reconecta con tu entorno",
            "reason": f"Tu conexión con el entorno fue {avg_entorno:.1f}/10. Cuidar plantas ayuda.",
            "action_label": "Ver cultivos",
            "action_href": "/dashboard/entorno",
        })

    # Crop reminders (simple: if there are active crops, remind)
    if cultivos:
        for cult in cultivos[:2]:
            recs.append({
                "type": "farming",
                "icon": "💧",
                "title": f"Cuida tu {cult.get('nombre_planta', 'planta')}",
                "reason": f"Estado: {cult.get('estado', 'activo')}. Revisa si necesita riego.",
                "action_label": "Ver entorno",
                "action_href": "/dashboard/entorno",
            })

    # Trend detection (first half vs second half)
    if n >= 4:
        mid = n // 2
        first_half = sum(c.get("estado_emocional", 5) for c in recent[:mid]) / mid
        second_half = sum(c.get("estado_emocional", 5) for c in recent[mid:]) / (n - mid)
        diff = second_half - first_half
        if diff >= 1.0:
            recs.append({
                "type": "trend",
                "icon": "📈",
                "title": "Tu ánimo está mejorando",
                "reason": f"+{diff:.1f} puntos en la segunda mitad de la semana. ¡Sigue así!",
            })
        elif diff <= -1.0:
            recs.append({
                "type": "trend",
                "icon": "📉",
                "title": "Tu ánimo ha bajado",
                "reason": f"{diff:.1f} puntos. Considera una pausa de autocuidado.",
                "action_label": "Ir a Check-in",
                "action_href": "/dashboard/checkin",
            })

    # ── Professional referral (Gap N4) ────────────────────────────────────
    # If mood ≤ 3 sustained for ≥ 3 of last 7 days → suggest professional
    low_mood_days = sum(1 for c in recent if c.get("estado_emocional", 5) <= 3)
    if low_mood_days >= 3:
        recs.insert(0, {
            "type": "professional_referral",
            "icon": "🩺",
            "title": "Considera hablar con un profesional",
            "reason": (
                f"Tu estado emocional ha sido bajo ({low_mood_days} de los últimos {n} días ≤ 3/10). "
                "ThriveMind es un co-piloto de bienestar, no sustituye a un profesional de salud mental. "
                "Te animamos a considerar estas opciones:"
            ),
            "resources": [
                {"name": "Teléfono de la Esperanza", "contact": "717 003 717", "country": "España"},
                {"name": "Doctoralia", "contact": "https://www.doctoralia.es/psicologos", "country": "España"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "country": "International"},
            ],
            "is_critical": True,
        })

    # ── Streak-based recommendation ───────────────────────────────────────
    from app.services.checkin_service import calcular_racha
    racha = calcular_racha(checkins)
    if racha >= 7:
        recs.append({
            "type": "streak",
            "icon": "🔥",
            "title": f"¡Racha de {racha} días consecutivos!",
            "reason": "Tu constancia es tu mayor herramienta. La adherencia multiplica los beneficios.",
        })
    elif racha >= 3:
        recs.append({
            "type": "streak",
            "icon": "⚡",
            "title": f"Racha de {racha} días — ¡sigue así!",
            "reason": f"Faltan {7 - racha} días para tu racha de 7. La consistencia construye hábitos.",
        })

    return recs
