"""
services/context_engine.py — Motor de Contexto de ThriveMind (5 capas).

Clasifica el estado HRV del usuario y ensambla el contexto bioquímico
completo que se inyecta en los prompts de todos los agentes de IA.

5-Layer Context Architecture (Proyecto §A):
  L1: Fisiológica (HRV/autonómico) — peso máximo
  L2: Emocional/Cognitiva — peso alto
  L3: Intencional (objetivo del usuario) — peso alto
  L4: Temporal (ventana circadiana) — peso medio
  L5: Ambiental (clima + preferencias históricas) — peso bajo-medio

Regla de oro: las variables internas definen la necesidad terapéutica;
las externas modulan la entrega.
"""
from datetime import datetime
from typing import Optional
from app.services.knowledge_base import (
    HRV_THRESHOLDS, CHRONO_NUTRITION_MATRIX, get_override,
)


def clasificar_hrv(rmssd: float) -> dict:
    """
    Clasifica un valor RMSSD en uno de los 5 estados autonómicos.
    """
    if rmssd < 20:
        return HRV_THRESHOLDS["E1_CRITICAL"]
    elif rmssd < 40:
        return HRV_THRESHOLDS["E2_STRESSED"]
    elif rmssd < 55:
        return HRV_THRESHOLDS["E3_MIXED"]
    elif rmssd < 75:
        return HRV_THRESHOLDS["E4_OPTIMAL"]
    else:
        return HRV_THRESHOLDS["E5_HIGH"]


def obtener_ventana_circadiana(hora: Optional[int] = None) -> dict:
    """
    Determina la ventana circadiana actual basada en la hora.
    """
    if hora is None:
        hora = datetime.now().hour

    if 6 <= hora < 9:
        return CHRONO_NUTRITION_MATRIX["manana_temprana"]
    elif 9 <= hora < 13:
        return CHRONO_NUTRITION_MATRIX["pico_cognitivo"]
    elif 15 <= hora < 20:
        return CHRONO_NUTRITION_MATRIX["tarde"]
    else:
        return CHRONO_NUTRITION_MATRIX["noche"]


def build_context(
    checkin_data: dict,
    hrv_rmssd: Optional[float] = None,
    clima: Optional[dict] = None,
    hora: Optional[int] = None,
    user_preferences: Optional[dict] = None,
    checkin_history: Optional[list] = None,
) -> dict:
    """
    Ensambla el contexto completo para los agentes de IA (5 capas).

    L1: Fisiológica — HRV
    L2: Emocional — estado_emocional + emocion_principal
    L3: Intencional — objetivo del usuario (preferences)
    L4: Temporal — ventana circadiana
    L5: Ambiental — clima + historial de preferencias
    """
    # ── L2: Emocional ──
    context = {
        "estado_emocional": checkin_data.get("estado_emocional", 5),
        "energia_fisica": checkin_data.get("energia_fisica", 5),
        "horas_sueno": checkin_data.get("horas_sueno"),
        "emocion_principal": checkin_data.get("emocion_principal", "neutral"),
    }

    # ── L1: Fisiológica (HRV) ──
    hrv_state_key = None
    if hrv_rmssd is not None:
        hrv_estado = clasificar_hrv(hrv_rmssd)
        hrv_state_key = _get_hrv_key(hrv_rmssd)
        context["hrv"] = {
            "rmssd": hrv_rmssd,
            "estado": hrv_estado["label"],
            "estado_key": hrv_state_key,
            "protocolo": hrv_estado["protocolo_inmediato"],
            "descripcion": hrv_estado["descripcion"],
        }

    # ── L4: Temporal (ventana circadiana) ──
    ventana = obtener_ventana_circadiana(hora)
    ventana_key = _get_ventana_key(hora)
    context["ventana_circadiana"] = {
        "horario": ventana["horario"],
        "key": ventana_key,
        "neurotransmisor_prioritario": ventana["neurotransmisor_prioritario"],
        "alimentos_recomendados": [a["nombre"] for a in ventana["alimentos_recomendados"]],
    }

    # ── L5: Ambiental (clima) ──
    if clima:
        context["clima"] = {
            "condicion": clima.get("descripcion", "desconocido"),
            "temperatura": clima.get("temperatura"),
            "clasificacion_kb": clima.get("clasificacion_kb", "soleado"),
        }

    # ── L3: Intencional (preferencias del usuario) ──
    if user_preferences:
        context["preferencias"] = {
            "objetivo_principal": user_preferences.get("objetivo_principal", "equilibrio"),
            "objetivo_fitness": user_preferences.get("objetivo_fitness", "mantener"),
            "preferencia_dieta": user_preferences.get("preferencia_dieta", "sin_restriccion"),
            "alergias": user_preferences.get("alergias", []),
            "pilares_activos": [
                p for p in ["mente", "cuerpo", "entorno"]
                if user_preferences.get(f"{p}_activo", True)
            ],
        }

    # ── L5 extended: Historial (tendencia últimos 7 check-ins) ──
    if checkin_history and len(checkin_history) >= 3:
        moods = [c.get("estado_emocional", 5) for c in checkin_history[:7]]
        energies = [c.get("energia_fisica", 5) for c in checkin_history[:7]]
        context["tendencia_reciente"] = {
            "mood_promedio_7d": round(sum(moods) / len(moods), 1),
            "energia_promedio_7d": round(sum(energies) / len(energies), 1),
            "mood_tendencia": "mejorando" if moods[0] > moods[-1] else "estable" if moods[0] == moods[-1] else "bajando",
            "n_checkins": len(checkin_history),
        }

    # ── T7×T8 Override check ──
    if hrv_state_key and ventana_key:
        override = get_override(ventana_key, hrv_state_key)
        if override:
            context["override_activo"] = {
                "tipo": "T7xT8",
                "razon": override["razon"],
                "luz_override": override.get("luz"),
                "nutricion_override": override.get("nutricion"),
                "meditacion_override": override.get("meditacion"),
            }

    return context


def _get_hrv_key(rmssd: float) -> str:
    """Retorna la key del estado HRV para lookup en matrices."""
    if rmssd < 20:
        return "E1_CRITICAL"
    elif rmssd < 40:
        return "E2_STRESSED"
    elif rmssd < 55:
        return "E3_MIXED"
    elif rmssd < 75:
        return "E4_OPTIMAL"
    return "E5_HIGH"


def _get_ventana_key(hora: Optional[int] = None) -> str:
    """Retorna la key de la ventana circadiana."""
    if hora is None:
        hora = datetime.now().hour
    if 6 <= hora < 9:
        return "manana_temprana"
    elif 9 <= hora < 13:
        return "pico_cognitivo"
    elif 15 <= hora < 20:
        return "tarde"
    return "noche"


def context_to_prompt(context: dict) -> str:
    """
    Convierte el contexto estructurado en texto para inyectar en un prompt.
    """
    lines = ["CONTEXTO BIOMÉTRICO DEL USUARIO:"]
    lines.append(f"- Estado emocional: {context['estado_emocional']}/10")
    lines.append(f"- Energía física: {context['energia_fisica']}/10")
    lines.append(f"- Emoción principal: {context['emocion_principal']}")

    if context.get("horas_sueno"):
        lines.append(f"- Horas de sueño: {context['horas_sueno']}")

    if "hrv" in context:
        hrv = context["hrv"]
        lines.append(f"\nESTADO HRV: {hrv['estado']} (RMSSD: {hrv['rmssd']}ms)")
        lines.append(f"Protocolo: {hrv['protocolo']}")

    if "ventana_circadiana" in context:
        vc = context["ventana_circadiana"]
        lines.append(f"\nVENTANA CIRCADIANA: {vc['horario']}")
        lines.append(f"Neurotransmisor prioritario: {vc['neurotransmisor_prioritario']}")

    if "clima" in context:
        c = context["clima"]
        lines.append(f"\nCLIMA: {c['condicion']} ({c.get('temperatura', '?')}°C)")

    return "\n".join(lines)
