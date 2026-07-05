"""
models/checkin.py — Modelos de datos para check-ins de bienestar.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class CheckinCreate(BaseModel):
    """Schema para crear un check-in diario."""
    estado_emocional: int = Field(..., ge=1, le=10)
    energia_fisica: int = Field(..., ge=1, le=10)
    horas_sueno: Optional[float] = Field(None, ge=0, le=24)
    conexion_entorno: Optional[int] = Field(None, ge=1, le=10)
    emocion_principal: Optional[str] = None
    nota: Optional[str] = None
    tipo_checkin: Literal[
        'diario', 'pre_meditacion', 'post_meditacion',
        'pre_comida', 'post_comida', 'post_cosecha'
    ] = 'diario'
    referencia_id: Optional[str] = None
    hambre: Optional[int] = Field(None, ge=1, le=10)
    saciedad: Optional[int] = Field(None, ge=1, le=10)
    hrv_estimado: Optional[float] = None


class CheckinResponse(BaseModel):
    """Schema de respuesta de un check-in."""
    id: str
    user_id: str
    estado_emocional: int
    energia_fisica: int
    horas_sueno: Optional[float] = None
    conexion_entorno: Optional[int] = None
    emocion_principal: Optional[str] = None
    nota: Optional[str] = None
    tipo_checkin: str
    created_at: datetime
