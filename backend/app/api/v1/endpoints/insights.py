"""
endpoints/insights.py — Unified insights & recommendations endpoints.

Combines:
- Holistic contextual recommendations (3-pillar orchestration)
- Personalized rule-based recommendations
- Convergence dashboard (pillar health + cross-correlations)
- Interdependency matrix (pillar×pillar Pearson)
- Context history
- Sentiment analysis on check-in notes
"""
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
import random
import uuid

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_supabase
from app.services.orchestration_service import generate_holistic_recommendation
from app.services.recommendation_service import get_personalized_recommendations
from app.services.sentiment_service import analyze_weekly_notes
from app.services.weather_service import obtener_clima_actual
from app.services.intervention_service import (
    log_intervention, update_feedback, get_intervention_history, get_acceptance_rate,
)
from app.services.override_service import (
    detect_override, register_override, get_resilience_counter,
)
from app.services.emotional_classifier import classify_emotional_state
from app.services.rag_service import recuperar_evidencia_cientifica

router = APIRouter()


# ── 1. Holistic Recommendation ───────────────────────────────────────────────

@router.get("/holistic", summary="Recomendación holística de 3 pilares")
async def holistic_recommendation(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """
    Cierra el loop: Check-in → Contexto → Acción en 3 pilares.
    """
    # Get latest check-in
    checkin_resp = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, emocion_principal, conexion_entorno")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    checkin_data = checkin_resp.data[0] if checkin_resp.data else None

    # Get weather (best effort)
    clima = None
    try:
        clima = await obtener_clima_actual()
    except Exception:
        pass

    return await generate_holistic_recommendation(
        user_id=current_user["id"],
        checkin_data=checkin_data,
        clima=clima,
    )


# ── 2. Personalized Recommendations ──────────────────────────────────────────

@router.get("/evidencia", summary="Evidencia científica RAG para las recomendaciones")
async def evidencia_cientifica(
    tema: str = Query(default="bienestar mindfulness nutricion", max_length=100),
    current_user=Depends(get_current_user),
):
    resultado = await recuperar_evidencia_cientifica(consulta=tema, pilar="general", max_papers=6)
    papers = [
        {
            "titulo": p.get("title", ""),
            "autores": p.get("authors", ""),
            "año": p.get("year", ""),
            "pilar": p.get("pilar", p.get("pillar", "")),
            "doi": p.get("doi", ""),
        }
        for p in resultado.get("papers", [])
    ]

    # Fallback: read directly from local JSON corpus if pgvector returned nothing
    if not papers:
        import json, pathlib, random
        corpus_path = pathlib.Path(__file__).parent.parent.parent.parent / "app" / "data" / "thrivemind_rag_corpus_v4.json"
        if corpus_path.exists():
            data = json.loads(corpus_path.read_text(encoding="utf-8"))
            all_papers = data if isinstance(data, list) else data.get("papers", [])
            sample = random.sample(all_papers, min(6, len(all_papers)))
            papers = [
                {
                    "titulo": p.get("title", p.get("titulo", "")),
                    "autores": p.get("authors", p.get("autores", "")),
                    "año": p.get("year", p.get("año", "")),
                    "pilar": p.get("pillar", p.get("pilar", "")),
                    "doi": p.get("doi", ""),
                }
                for p in sample
            ]

    return {"papers": papers, "total": len(papers)}


@router.get("/recommendations", summary="Recomendaciones personalizadas")
async def personalized_recommendations(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    checkins_resp = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, conexion_entorno, emocion_principal, created_at")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(7)
        .execute()
    )
    cultivos_resp = (
        supabase.table("cultivos_activos")
        .select("nombre_planta, estado, activo")
        .eq("user_id", current_user["id"])
        .eq("activo", True)
        .execute()
    )
    recs = await get_personalized_recommendations(
        user_id=current_user["id"],
        checkins=checkins_resp.data or [],
        cultivos=cultivos_resp.data or [],
    )
    return {"recommendations": recs}


# ── 3. Convergence Dashboard ─────────────────────────────────────────────────

@router.get("/convergence", summary="Dashboard de convergencia de 3 pilares")
async def convergence_dashboard(
    dias: int = Query(default=14, ge=7, le=90),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """
    Returns pillar health scores, cross-pillar correlations,
    and convergence insights.
    """
    fecha_inicio = (datetime.utcnow() - timedelta(days=dias)).isoformat()

    resp = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, conexion_entorno, created_at")
        .eq("user_id", current_user["id"])
        .gte("created_at", fecha_inicio)
        .order("created_at", desc=False)
        .execute()
    )
    checkins = resp.data or []
    n = len(checkins)

    if n < 3:
        return {"insufficient_data": True, "n_checkins": n, "min_required": 3}

    def avg(field):
        vals = [c[field] for c in checkins if c.get(field) is not None]
        return round(sum(vals) / len(vals), 1) if vals else 0

    mente_score = avg("estado_emocional")
    cuerpo_score = avg("energia_fisica")
    entorno_score = avg("conexion_entorno")
    sleep_score = min(round(avg("horas_sueno") * 10 / 8, 1), 10)

    # Per-day series for convergence chart
    daily = {}
    for c in checkins:
        d = c["created_at"][:10]
        if d not in daily:
            daily[d] = {"mente": [], "cuerpo": [], "entorno": []}
        daily[d]["mente"].append(c.get("estado_emocional", 5))
        daily[d]["cuerpo"].append(c.get("energia_fisica", 5))
        daily[d]["entorno"].append(c.get("conexion_entorno", 5))

    convergence_series = []
    for d in sorted(daily.keys()):
        v = daily[d]
        convergence_series.append({
            "fecha": d,
            "fecha_corta": d[5:],
            "mente": round(sum(v["mente"]) / len(v["mente"]), 1),
            "cuerpo": round(sum(v["cuerpo"]) / len(v["cuerpo"]), 1),
            "entorno": round(sum(v["entorno"]) / len(v["entorno"]), 1),
        })

    # Cross-pillar Pearson correlations
    import numpy as np
    from scipy.stats import pearsonr

    arrays = {
        "mente": np.array([c.get("estado_emocional", 5) for c in checkins], dtype=float),
        "cuerpo": np.array([c.get("energia_fisica", 5) for c in checkins], dtype=float),
        "entorno": np.array([c.get("conexion_entorno", 5) for c in checkins], dtype=float),
    }

    matrix = {}
    pairs = [("mente", "cuerpo"), ("mente", "entorno"), ("cuerpo", "entorno")]
    for a, b in pairs:
        mask = ~(np.isnan(arrays[a]) | np.isnan(arrays[b]))
        if mask.sum() >= 3:
            r, p = pearsonr(arrays[a][mask], arrays[b][mask])
            matrix[f"{a}_{b}"] = {"r": round(r, 3), "p": round(p, 4)}
        else:
            matrix[f"{a}_{b}"] = {"r": 0, "p": 1}

    # Insights
    insights = []
    mc = matrix.get("mente_cuerpo", {})
    me = matrix.get("mente_entorno", {})
    ce = matrix.get("cuerpo_entorno", {})

    if mc.get("r", 0) > 0.4:
        insights.append(f"Cuando tu estado emocional mejora, tu energía también sube (r={mc['r']})")
    if me.get("r", 0) > 0.4:
        insights.append(f"Tu conexión con el entorno está ligada a tu bienestar mental (r={me['r']})")
    if ce.get("r", 0) > 0.4:
        insights.append(f"Cuidar tu entorno impulsa tu energía física (r={ce['r']})")
    if not insights:
        insights.append("Sigue registrando check-ins para descubrir conexiones entre tus pilares.")

    return {
        "pillar_scores": {
            "mente": mente_score,
            "cuerpo": cuerpo_score,
            "entorno": entorno_score,
            "sueno": sleep_score,
        },
        "convergence_series": convergence_series,
        "interdependency_matrix": matrix,
        "insights": insights,
        "n_checkins": n,
        "dias": dias,
    }


# ── 4. Interdependency Matrix (standalone) ───────────────────────────────────

@router.get("/matrix", summary="Matriz de interdependencias entre pilares")
async def interdependency_matrix(
    dias: int = Query(default=30, ge=7, le=90),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    resp = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, conexion_entorno")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(dias)
        .execute()
    )
    checkins = resp.data or []
    n = len(checkins)

    if n < 5:
        return {"insufficient_data": True, "n": n}

    import numpy as np
    from scipy.stats import pearsonr

    fields = ["estado_emocional", "energia_fisica", "conexion_entorno", "horas_sueno"]
    labels = {"estado_emocional": "Mente", "energia_fisica": "Cuerpo",
              "conexion_entorno": "Entorno", "horas_sueno": "Sueño"}

    arrays = {f: np.array([c.get(f, np.nan) for c in checkins], dtype=float) for f in fields}

    cells = []
    for i, f1 in enumerate(fields):
        for j, f2 in enumerate(fields):
            if i == j:
                cells.append({"row": labels[f1], "col": labels[f2], "r": 1.0, "p": 0.0})
                continue
            mask = ~(np.isnan(arrays[f1]) | np.isnan(arrays[f2]))
            if mask.sum() >= 3:
                r, p = pearsonr(arrays[f1][mask], arrays[f2][mask])
                cells.append({"row": labels[f1], "col": labels[f2], "r": round(r, 3), "p": round(p, 4)})
            else:
                cells.append({"row": labels[f1], "col": labels[f2], "r": None, "p": None})

    return {
        "labels": list(labels.values()),
        "cells": cells,
        "n_checkins": n,
    }


# ── 5. Context History ────────────────────────────────────────────────────────

@router.get("/context-history", summary="Historial de contextos aplicados")
async def context_history(
    limit: int = Query(default=10, ge=1, le=50),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """
    Returns logged context resolutions showing what was recommended
    and how the user's state changed afterward.
    """
    # In demo mode, generate synthetic history
    if settings.environment == "demo":
        return {"history": _demo_context_history(limit)}

    resp = (
        supabase.table("context_log")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return {"history": resp.data or []}


# ── 6. Sentiment Analysis on Notes ───────────────────────────────────────────

@router.get("/sentiment", summary="Análisis de sentimiento de las notas")
async def sentiment_analysis(
    dias: int = Query(default=7, ge=1, le=30),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    fecha_inicio = (datetime.utcnow() - timedelta(days=dias)).isoformat()

    resp = (
        supabase.table("checkins")
        .select("nota_personal, emocion_principal, created_at")
        .eq("user_id", current_user["id"])
        .gte("created_at", fecha_inicio)
        .order("created_at", desc=False)
        .execute()
    )
    checkins = resp.data or []
    notes = [c.get("nota_personal", "") for c in checkins if c.get("nota_personal")]

    # Also include emocion_principal as implicit text
    for c in checkins:
        ep = c.get("emocion_principal")
        if ep:
            notes.append(ep)

    result = analyze_weekly_notes(notes)
    return result


# ── Demo helpers ──────────────────────────────────────────────────────────────

_DEMO_CONTEXTS = [
    ("amanecer_activacion", "Activación matutina", "meditacion_energia"),
    ("enfoque_trabajo", "Enfoque y productividad", "meditacion_enfoque"),
    ("tarde_desconexion", "Desconexión vespertina", "meditacion_calma"),
    ("noche_relajacion", "Relajación nocturna", "meditacion_calma"),
    ("mediodia_reset", "Pausa de mediodía", "meditacion_enfoque"),
]


def _demo_context_history(limit: int) -> list:
    history = []
    now = datetime.utcnow()
    for i in range(min(limit, 10)):
        ctx = _DEMO_CONTEXTS[i % len(_DEMO_CONTEXTS)]
        dt = now - timedelta(days=i, hours=random.randint(0, 12))
        mood_before = random.randint(3, 6)
        mood_after = min(10, mood_before + random.randint(1, 3))
        history.append({
            "id": str(uuid.uuid4()),
            "context_key": ctx[0],
            "context_label": ctx[1],
            "hue_profile": ctx[2],
            "mood_before": mood_before,
            "energy_before": random.randint(3, 6),
            "mood_after": mood_after,
            "energy_after": min(10, random.randint(4, 7)),
            "meditation_completed": random.choice([True, True, False]),
            "created_at": dt.isoformat() + "Z",
        })
    return history


# ── 7. Intervention Logging (MLOps cycle) ────────────────────────────────────

@router.get("/interventions", summary="Historial de intervenciones del sistema")
async def intervention_history(
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Historial de intervenciones generadas con feedback del usuario."""
    return {
        "interventions": await get_intervention_history(
            user_id=current_user["id"], limit=limit, supabase=supabase
        )
    }


@router.post("/interventions/{intervention_id}/feedback", summary="Valorar una intervención")
async def rate_intervention(
    intervention_id: str,
    score: int = Query(ge=1, le=5, description="Valoración 1-5"),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """El usuario valora la intervención (1-5). Cierra el triplete MLOps."""
    return await update_feedback(
        user_id=current_user["id"],
        intervention_id=intervention_id,
        score=score,
        supabase=supabase,
    )


@router.get("/interventions/acceptance-rate", summary="Tasa de aceptación de intervenciones")
async def acceptance_rate(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """
    Métricas de aceptación por tipo de intervención.
    Triplete MLOps para detección de concept drift.
    """
    return await get_acceptance_rate(
        user_id=current_user["id"], supabase=supabase
    )


# ── 8. Override Co-pilot Protocol ────────────────────────────────────────────

@router.post("/override/detect", summary="Detectar si el usuario contradice la IA")
async def detect_user_override(
    ai_recommendation: dict,
    user_action: dict,
    current_user=Depends(get_current_user),
):
    """Step 1: Detect if user action conflicts with AI recommendation."""
    return await detect_override(
        user_id=current_user["id"],
        ai_recommendation=ai_recommendation,
        user_action=user_action,
    )


@router.post("/override/register", summary="Registrar override con mitigación")
async def register_user_override(
    override_data: dict,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Steps 2-4: Notify + Validate + Mitigate. Respeta siempre la decisión del usuario."""
    return await register_override(
        user_id=current_user["id"],
        override_data=override_data,
        supabase=supabase,
    )


@router.get("/override/resilience-counter", summary="Resilience Counter del usuario")
async def user_resilience_counter(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """CR: +1/override, -0.5 si HRV recupera. ≥3 → reflexión, ≥5 → derivación."""
    return await get_resilience_counter(
        user_id=current_user["id"], supabase=supabase
    )


# ── 9. Emotional State Classification (XGBoost / Cold-start) ─────────────────

@router.get("/classify", summary="Clasificar estado emocional (Capa 1 Motor IA)")
async def classify_state(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """
    Capa 1 del Motor de IA: clasifica el estado emocional del usuario.
    Auto-selecciona cold-start (<30 check-ins) o XGBoost (≥30).
    Retorna: estado, confianza, probabilidades, features, method.
    """
    # Get latest check-in
    checkin_resp = (
        supabase.table("checkins")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    checkin_data = checkin_resp.data[0] if checkin_resp.data else {}

    # Get check-in history
    history_resp = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, hrv_estimado, tipo_checkin, nota_personal, created_at")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(60)
        .execute()
    )

    # Get weather
    clima = None
    try:
        clima = await obtener_clima_actual()
    except Exception:
        pass

    result = classify_emotional_state(
        checkin_data=checkin_data,
        checkin_history=history_resp.data or [],
        clima=clima,
    )

    return result
