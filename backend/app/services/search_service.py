"""
services/search_service.py — Búsqueda global en todos los módulos de ThriveMind.
"""
from app.core.config import settings


async def global_search(user_id: str, query: str, supabase, limit: int = 10) -> dict:
    """Search across meditations, crops, checkins, and knowledge base."""
    results: dict[str, list] = {}
    q = query.strip()
    if not q:
        return results

    # Demo mode: return synthetic matches
    if settings.environment == "demo":
        return _demo_search(q)

    # Meditaciones
    try:
        resp = (
            supabase.table("meditation_sessions")
            .select("id, titulo, tecnica")
            .eq("user_id", user_id)
            .ilike("titulo", f"%{q}%")
            .limit(limit)
            .execute()
        )
        if resp.data:
            results["meditaciones"] = [
                {"id": r["id"], "title": r.get("titulo", ""), "icon": "🧘", "type": "meditacion",
                 "url": "/dashboard/mente"}
                for r in resp.data
            ]
    except Exception:
        pass

    # Cultivos
    try:
        resp = (
            supabase.table("cultivos_activos")
            .select("id, nombre_planta, tipo, estado")
            .eq("user_id", user_id)
            .ilike("nombre_planta", f"%{q}%")
            .limit(limit)
            .execute()
        )
        if resp.data:
            results["cultivos"] = [
                {"id": r["id"], "title": r["nombre_planta"], "icon": "🌱", "type": "cultivo",
                 "url": "/dashboard/entorno"}
                for r in resp.data
            ]
    except Exception:
        pass

    # Check-ins (by emocion_principal or nota)
    try:
        resp = (
            supabase.table("checkins")
            .select("id, emocion_principal, created_at, nota_personal")
            .eq("user_id", user_id)
            .ilike("emocion_principal", f"%{q}%")
            .limit(limit)
            .execute()
        )
        if resp.data:
            results["checkins"] = [
                {"id": r["id"], "title": f"{r.get('emocion_principal', '')} — {r['created_at'][:10]}",
                 "icon": "✍️", "type": "checkin", "url": "/dashboard/checkin"}
                for r in resp.data
            ]
    except Exception:
        pass

    return {k: v for k, v in results.items() if v}


# ── Demo helpers ──────────────────────────────────────────────────────────────

_DEMO_ITEMS = {
    "meditaciones": [
        {"id": "d1", "title": "Meditación de calma matutina", "icon": "🧘", "type": "meditacion", "url": "/dashboard/mente"},
        {"id": "d2", "title": "Meditación de enfoque", "icon": "🧘", "type": "meditacion", "url": "/dashboard/mente"},
        {"id": "d3", "title": "Respiración 4-7-8 para dormir", "icon": "🧘", "type": "meditacion", "url": "/dashboard/mente"},
    ],
    "cultivos": [
        {"id": "c1", "title": "Lavanda", "icon": "🌱", "type": "cultivo", "url": "/dashboard/entorno"},
        {"id": "c2", "title": "Albahaca", "icon": "🌱", "type": "cultivo", "url": "/dashboard/entorno"},
        {"id": "c3", "title": "Romero", "icon": "🌱", "type": "cultivo", "url": "/dashboard/entorno"},
        {"id": "c4", "title": "Menta", "icon": "🌱", "type": "cultivo", "url": "/dashboard/entorno"},
    ],
    "nutricion": [
        {"id": "n1", "title": "Avena con frutas y miel", "icon": "🍽️", "type": "receta", "url": "/dashboard/cuerpo"},
        {"id": "n2", "title": "Ensalada mediterránea", "icon": "🍽️", "type": "receta", "url": "/dashboard/cuerpo"},
        {"id": "n3", "title": "Smoothie de espinaca y plátano", "icon": "🍽️", "type": "receta", "url": "/dashboard/cuerpo"},
    ],
}


def _demo_search(query: str) -> dict:
    q = query.lower()
    results: dict[str, list] = {}
    for category, items in _DEMO_ITEMS.items():
        matches = [i for i in items if q in i["title"].lower()]
        if matches:
            results[category] = matches
    # If nothing matched, return all items (show demo content)
    if not results:
        return {k: v[:2] for k, v in _DEMO_ITEMS.items()}
    return results
