"""
services/auth_service.py — Lógica de negocio de autenticación.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt as _bcrypt_lib
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import UserRegister, UserLogin, Token, UserResponse, TokenData
from fastapi import HTTPException, status
from app.core.database import get_supabase_client


def hash_password(password: str) -> str:
    return _bcrypt_lib.hashpw(password.encode(), _bcrypt_lib.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt_lib.checkpw(plain_password.encode(), hashed_password.encode())


ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def refresh_access_token(refresh_token: str) -> str:
    """Validate refresh token and return a new access token."""
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        if payload.get("type") != "refresh":
            raise JWTError("Not a refresh token")
        new_token = create_access_token({"sub": payload["sub"], "email": payload.get("email")})
        return new_token
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")


def verify_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise credentials_exception


def _build_tokens(user_id: str, email: str) -> tuple[str, str]:
    payload = {"sub": user_id, "email": email}
    return create_access_token(payload), create_refresh_token(payload)


async def register_user(user_data: UserRegister) -> Token:
    if settings.environment == "demo":
        return _demo_token(user_data.email, user_data.nombre)

    supabase = get_supabase_client()

    existing = supabase.table("profiles").select("id").eq("email", user_data.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Este email ya está registrado")

    hashed_pw = hash_password(user_data.password)
    result = supabase.table("profiles").insert({
        "email": user_data.email,
        "password_hash": hashed_pw,
        "nombre": user_data.nombre,
        "apellido": user_data.apellido,
    }).execute()

    user = result.data[0]
    access_token, refresh_tok = _build_tokens(user["id"], user["email"])

    return Token(
        access_token=access_token,
        refresh_token=refresh_tok,
        expires_in=ACCESS_TOKEN_MINUTES * 60,
        user=UserResponse(
            id=user["id"], email=user["email"], nombre=user["nombre"],
            apellido=user.get("apellido"), created_at=user["created_at"],
        ),
    )


async def login_user(credentials: UserLogin) -> Token:
    if settings.environment == "demo":
        return _demo_token(credentials.email, "Demo User")

    supabase = get_supabase_client()
    result = supabase.table("profiles").select("*").eq("email", credentials.email).execute()

    if not result.data or not verify_password(credentials.password, result.data[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    user = result.data[0]
    access_token, refresh_tok = _build_tokens(user["id"], user["email"])

    return Token(
        access_token=access_token,
        refresh_token=refresh_tok,
        expires_in=ACCESS_TOKEN_MINUTES * 60,
        user=UserResponse(
            id=user["id"], email=user["email"], nombre=user["nombre"],
            apellido=user.get("apellido"), created_at=user["created_at"],
        ),
    )


def _demo_token(email: str, nombre: str) -> Token:
    """Generate a demo token without hitting Supabase."""
    from app.core.demo import DEMO_USER_ID
    at, rt = _build_tokens(DEMO_USER_ID, email)
    return Token(
        access_token=at,
        refresh_token=rt,
        expires_in=ACCESS_TOKEN_MINUTES * 60,
        user=UserResponse(
            id=DEMO_USER_ID,
            email=email,
            nombre=nombre,
            created_at="2025-01-01T00:00:00Z",
        ),
    )
