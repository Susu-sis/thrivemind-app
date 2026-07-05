"""
router.py — Router principal que registra todos los endpoints de la API v1.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, checkin, mente, cuerpo, entorno, ambient, preferences,
    insights, search, gamification, hue, meal_planner,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(checkin.router, prefix="/checkin", tags=["Check-in Diario"])
api_router.include_router(mente.router, prefix="/mente", tags=["Pilar Mente"])
api_router.include_router(cuerpo.router, prefix="/cuerpo", tags=["Pilar Cuerpo"])
api_router.include_router(entorno.router, prefix="/entorno", tags=["Pilar Entorno"])
api_router.include_router(ambient.router, prefix="/ambient", tags=["Ambient IoT"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["Preferencias"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights & Recomendaciones"])
api_router.include_router(search.router, prefix="/search", tags=["Búsqueda Global"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamificación"])
api_router.include_router(hue.router, prefix="/hue", tags=["Iluminación HUE"])
api_router.include_router(meal_planner.router, prefix="/meal-planner", tags=["Planificador de Menú"])
