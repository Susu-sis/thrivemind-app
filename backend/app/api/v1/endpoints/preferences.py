from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.models.preferences import UserPreferencesUpdate, UserPreferencesResponse
from app.services.preferences_service import get_user_preferences, update_user_preferences

router = APIRouter()


@router.get(
    "/",
    response_model=UserPreferencesResponse,
    summary="Obtener configuración de pilares del usuario",
)
async def get_preferences(
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await get_user_preferences(current_user["id"], supabase)


@router.patch(
    "/",
    response_model=UserPreferencesResponse,
    summary="Actualizar configuración de pilares",
)
async def update_preferences(
    updates: UserPreferencesUpdate,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    return await update_user_preferences(current_user["id"], updates, supabase)
