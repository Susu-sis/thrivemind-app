"""
services/intervention_service.py — Logging de intervenciones para ciclo MLOps.

Registra cada intervención generada por el sistema junto con el estado
emocional del usuario y su feedback. Cierra el ciclo:
   Estado → Intervención → Feedback → Reentrenamiento

Tabla: intervention_logs (ver docs/SUPABASE_SETUP.md)
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── In-memory demo state ─────────────────────────────────────────────────────
_demo_logs: dict[str, list] = {}


async def log_intervention(
    user_id: str,
    emotional_state: str,
    confidence: float,
    intervention_type: str,
    intervention_detail: dict,
    context_snapshot: Optional[dict] = None,
    supabase=None,
) -> dict:
    """
    Registra una intervención del sistema.
    Llamado automáticamente por orchestration, meditation, nutrition endpoints.
    """
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "emotional_state": emotional_state,
        "confidence": round(confidence, 3),
        "intervention_type": intervention_type,
        "intervention_detail": intervention_detail,
        "context_snapshot": context_snapshot or {},
        "user_feedback_score": None,  # 1-5, filled later by user
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if settings.environment == "demo":
        _demo_logs.setdefault(user_id, []).append(entry)
        return entry

    try:
        result = supabase.table("intervention_logs").insert(entry).execute()
        return result.data[0] if result.data else entry
    except Exception as e:
        logger.error(f"Error logging intervention: {e}")
        return entry


async def update_feedback(
    user_id: str,
    intervention_id: str,
    score: int,
    supabase=None,
) -> dict:
    """
    El usuario valora la intervención (1-5). Cierra el triplete MLOps.
    """
    if score < 1 or score > 5:
        return {"error": "Score debe ser entre 1 y 5"}

    if settings.environment == "demo":
        for log in _demo_logs.get(user_id, []):
            if log["id"] == intervention_id:
                log["user_feedback_score"] = score
                return log
        return {"error": "Intervención no encontrada"}

    try:
        result = (
            supabase.table("intervention_logs")
            .update({"user_feedback_score": score})
            .eq("id", intervention_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else {"error": "No encontrada"}
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        return {"error": str(e)}


async def get_intervention_history(
    user_id: str,
    limit: int = 20,
    supabase=None,
) -> list:
    """Historial de intervenciones con feedback."""
    if settings.environment == "demo":
        logs = _demo_logs.get(user_id, [])
        if not logs:
            return [
                {
                    "id": str(uuid.uuid4()),
                    "emotional_state": "estres_elevado",
                    "confidence": 0.82,
                    "intervention_type": "holistic_recommendation",
                    "intervention_detail": {"context": "tarde_desconexion", "pilares": ["mente", "cuerpo", "entorno"]},
                    "user_feedback_score": 4,
                    "created_at": "2026-05-01T18:30:00Z",
                },
                {
                    "id": str(uuid.uuid4()),
                    "emotional_state": "equilibrio",
                    "confidence": 0.91,
                    "intervention_type": "meditation",
                    "intervention_detail": {"objetivo": "calma", "duracion": 10},
                    "user_feedback_score": 5,
                    "created_at": "2026-05-02T09:00:00Z",
                },
                {
                    "id": str(uuid.uuid4()),
                    "emotional_state": "activacion",
                    "confidence": 0.76,
                    "intervention_type": "nutrition",
                    "intervention_detail": {"recomendacion": "proteína + omega-3"},
                    "user_feedback_score": None,
                    "created_at": "2026-05-03T13:00:00Z",
                },
            ]
        return logs[-limit:]

    try:
        result = (
            supabase.table("intervention_logs")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        logger.error(f"Error getting intervention history: {e}")
        return []


async def get_acceptance_rate(user_id: str, supabase=None) -> dict:
    """
    Calcula la tasa de aceptación por tipo de intervención.
    Triplete MLOps: estado + intervención + feedback → concept drift detection.
    """
    if settings.environment == "demo":
        return {
            "total_interventions": 12,
            "rated_interventions": 8,
            "average_score": 3.9,
            "acceptance_rate": 0.75,
            "by_type": {
                "holistic_recommendation": {"count": 5, "avg_score": 4.2, "acceptance": 0.80},
                "meditation": {"count": 4, "avg_score": 4.5, "acceptance": 0.90},
                "nutrition": {"count": 3, "avg_score": 3.0, "acceptance": 0.55},
            },
        }

    try:
        result = (
            supabase.table("intervention_logs")
            .select("intervention_type, user_feedback_score")
            .eq("user_id", user_id)
            .execute()
        )
        logs = result.data or []
        if not logs:
            return {"total_interventions": 0}

        rated = [l for l in logs if l.get("user_feedback_score") is not None]
        by_type: dict = {}
        for l in logs:
            t = l["intervention_type"]
            by_type.setdefault(t, {"scores": [], "count": 0})
            by_type[t]["count"] += 1
            if l.get("user_feedback_score"):
                by_type[t]["scores"].append(l["user_feedback_score"])

        type_stats = {}
        for t, data in by_type.items():
            scores = data["scores"]
            avg = sum(scores) / len(scores) if scores else 0
            type_stats[t] = {
                "count": data["count"],
                "avg_score": round(avg, 1),
                "acceptance": round(sum(1 for s in scores if s >= 3) / len(scores), 2) if scores else 0,
            }

        all_scores = [l["user_feedback_score"] for l in rated]
        return {
            "total_interventions": len(logs),
            "rated_interventions": len(rated),
            "average_score": round(sum(all_scores) / len(all_scores), 1) if all_scores else 0,
            "acceptance_rate": round(sum(1 for s in all_scores if s >= 3) / len(all_scores), 2) if all_scores else 0,
            "by_type": type_stats,
        }
    except Exception as e:
        logger.error(f"Error calculating acceptance rate: {e}")
        return {"total_interventions": 0, "error": str(e)}
