"""
core/auth.py — Dependencia de autenticación JWT para endpoints protegidos.

Extrae el JWT del header Authorization: Bearer <token> y devuelve el usuario.
En modo demo, retorna un usuario de prueba sin validar el token.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Dependencia de FastAPI: extrae y verifica el JWT, devuelve el usuario.
    En modo demo, retorna un usuario mock.
    """
    if settings.environment == "demo":
        from app.core.demo import DEMO_USER
        return DEMO_USER

    if credentials is None:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    from app.services.auth_service import verify_token
    from app.core.database import get_supabase_client

    token = credentials.credentials
    token_data = verify_token(token)

    supabase = get_supabase_client()
    result = supabase.table("profiles").select("*").eq("id", token_data.user_id).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return result.data[0]
