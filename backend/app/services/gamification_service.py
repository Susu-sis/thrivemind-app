"""
services/gamification_service.py — Sistema de puntos y hitos para ThriveMind.

Otorga puntos por acciones saludables y desbloquea hitos.
En modo demo, mantiene los puntos en memoria.
"""
from datetime import datetime, timezone
from app.core.config import settings

POINTS_CONFIG = {
    "checkin_diario": 10,
    "meditacion_completada": 25,
    "receta_analizada": 15,
    "cosecha_registrada": 50,
    "racha_7_dias": 100,
    "racha_30_dias": 500,
}

MILESTONES = [
    {"key": "primer_paso", "name": "Primer Paso", "emoji": "🌱", "points_required": 10},
    {"key": "explorador", "name": "Explorador", "emoji": "🔍", "points_required": 50},
    {"key": "constante", "name": "Constante", "emoji": "⭐", "points_required": 100},
    {"key": "meditador", "name": "Meditador", "emoji": "🧘", "points_required": 250},
    {"key": "cultivador", "name": "Cultivador Avanzado", "emoji": "🌿", "points_required": 500},
    {"key": "campeon", "name": "Campeón de Bienestar", "emoji": "🏆", "points_required": 1000},
]

# ── In-memory demo state ─────────────────────────────────────────────────────
_demo_points: dict[str, int] = {}
_demo_history: dict[str, list] = {}
_demo_milestones: dict[str, list[str]] = {}


async def award_points(user_id: str, action: str, supabase=None, referencia_id: str | None = None) -> dict:
    """Award points for an action. Works in demo and production."""
    if action not in POINTS_CONFIG:
        return {"error": f"Acción desconocida: {action}"}

    points = POINTS_CONFIG[action]

    if settings.environment == "demo":
        return _demo_award(user_id, action, points)

    # Production: read from profiles, write to gamification_history
    profile = supabase.table("profiles").select("gamification_points").eq("id", user_id).single().execute()
    current = (profile.data or {}).get("gamification_points", 0)
    new_total = current + points

    supabase.table("profiles").update({"gamification_points": new_total}).eq("id", user_id).execute()
    supabase.table("gamification_history").insert({
        "user_id": user_id,
        "action": action,
        "points": points,
        "referencia_id": referencia_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    unlocked = _check_milestones(new_total, user_id, supabase)
    return {"points_awarded": points, "total_points": new_total, "milestones_unlocked": unlocked}


async def get_user_gamification(user_id: str, supabase=None) -> dict:
    """Return current points, milestones, and history."""
    if settings.environment == "demo":
        total = _demo_points.get(user_id, 75)  # Start with some demo points
        unlocked = [m for m in MILESTONES if m["points_required"] <= total]
        next_m = next((m for m in MILESTONES if m["points_required"] > total), None)
        return {
            "total_points": total,
            "milestones_unlocked": unlocked,
            "next_milestone": next_m,
            "history": _demo_history.get(user_id, [
                {"action": "checkin_diario", "points": 10, "created_at": "2026-05-01T10:00:00Z"},
                {"action": "meditacion_completada", "points": 25, "created_at": "2026-05-01T11:00:00Z"},
                {"action": "checkin_diario", "points": 10, "created_at": "2026-05-02T10:00:00Z"},
                {"action": "receta_analizada", "points": 15, "created_at": "2026-05-02T13:00:00Z"},
                {"action": "checkin_diario", "points": 10, "created_at": "2026-05-03T09:00:00Z"},
            ])[-10:],
        }

    profile = supabase.table("profiles").select("gamification_points").eq("id", user_id).single().execute()
    total = (profile.data or {}).get("gamification_points", 0)
    unlocked = [m for m in MILESTONES if m["points_required"] <= total]
    next_m = next((m for m in MILESTONES if m["points_required"] > total), None)

    hist = (
        supabase.table("gamification_history")
        .select("action, points, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    return {
        "total_points": total,
        "milestones_unlocked": unlocked,
        "next_milestone": next_m,
        "history": hist.data or [],
    }


def _demo_award(user_id: str, action: str, points: int) -> dict:
    _demo_points[user_id] = _demo_points.get(user_id, 75) + points
    total = _demo_points[user_id]
    if user_id not in _demo_history:
        _demo_history[user_id] = []
    _demo_history[user_id].append({
        "action": action, "points": points,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    unlocked = [m for m in MILESTONES if m["points_required"] <= total]
    return {"points_awarded": points, "total_points": total, "milestones_unlocked": unlocked}


def _check_milestones(total: int, user_id: str, supabase) -> list:
    unlocked = []
    for m in MILESTONES:
        if m["points_required"] <= total:
            # Check if already unlocked
            existing = (
                supabase.table("user_milestones")
                .select("id")
                .eq("user_id", user_id)
                .eq("milestone_key", m["key"])
                .execute()
            )
            if not existing.data:
                supabase.table("user_milestones").insert({
                    "user_id": user_id,
                    "milestone_key": m["key"],
                    "unlocked_at": datetime.now(timezone.utc).isoformat(),
                }).execute()
                unlocked.append(m)
    return unlocked
