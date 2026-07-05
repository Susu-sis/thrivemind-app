"""
models/preferences.py — Modelos de preferencias de pilares

Pydantic valida automáticamente que los valores sean correctos.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class PillarConfig(BaseModel):
    """Configuración de un pilar individual."""
    activo: bool = True
    intensidad: int = Field(default=1, ge=1, le=3, description="1=básico, 2=intermedio, 3=avanzado")


class UserPreferencesUpdate(BaseModel):
    """Schema para actualizar preferencias — todos los campos son opcionales."""
    mente: Optional[PillarConfig] = None
    cuerpo: Optional[PillarConfig] = None
    entorno: Optional[PillarConfig] = None
    objetivo_principal: Optional[Literal[
        'equilibrio', 'reducir_estres', 'mejorar_sueno',
        'aumentar_energia', 'conexion_naturaleza', 'rendimiento_cognitivo'
    ]] = None
    frecuencia_checkin: Optional[Literal['diario', 'cada_dos_dias', 'semanal']] = None
    # ── Extended fields (Gap E1.4–E1.7) ──
    alergias: Optional[list[str]] = Field(default=None, description="Alergias alimentarias: gluten, lactosa, frutos_secos, mariscos, huevo, soja")
    preferencia_dieta: Optional[Literal[
        'omnivora', 'vegetariana', 'vegana', 'pescatariana', 'sin_restriccion'
    ]] = None
    presupuesto_semanal: Optional[Literal['bajo', 'medio', 'alto']] = Field(default=None, description="bajo=<60€, medio=60-120€, alto=>120€")
    objetivo_fitness: Optional[Literal[
        'mantener', 'perder_peso', 'ganar_musculo', 'tonificar', 'resistencia'
    ]] = None


class UserPreferencesResponse(BaseModel):
    """Schema de respuesta con el estado completo de preferencias."""
    mente_activo: bool
    mente_intensidad: int
    cuerpo_activo: bool
    cuerpo_intensidad: int
    entorno_activo: bool
    entorno_intensidad: int
    objetivo_principal: str
    frecuencia_checkin: str
    # Extended fields
    alergias: list[str] = []
    preferencia_dieta: str = "sin_restriccion"
    presupuesto_semanal: str = "medio"
    objetivo_fitness: str = "mantener"

    @property
    def pilares_activos(self) -> list[str]:
        activos = []
        if self.mente_activo:
            activos.append("mente")
        if self.cuerpo_activo:
            activos.append("cuerpo")
        if self.entorno_activo:
            activos.append("entorno")
        return activos

    @property
    def num_pilares_activos(self) -> int:
        return len(self.pilares_activos)
