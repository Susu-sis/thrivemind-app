from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.models.user import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import register_user, login_user, refresh_access_token
from app.core.auth import get_current_user

router = APIRouter()


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=Token, summary="Registrar nuevo usuario")
async def register(user_data: UserRegister):
    return await register_user(user_data)


@router.post("/login", response_model=Token, summary="Iniciar sesión")
async def login(credentials: UserLogin):
    return await login_user(credentials)


@router.post("/refresh", summary="Refrescar access token")
async def refresh(body: RefreshRequest):
    new_access = refresh_access_token(body.refresh_token)
    return {"access_token": new_access, "token_type": "bearer", "expires_in": 900}


@router.get("/me", response_model=UserResponse, summary="Obtener perfil propio")
async def get_me(current_user=Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        nombre=current_user["nombre"],
        apellido=current_user.get("apellido"),
        created_at=current_user["created_at"],
    )
