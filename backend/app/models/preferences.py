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
    # Perfil biométrico básico — Nivel 1 TMB (Mifflin-St Jeor)
    peso_kg: Optional[float] = Field(default=None, ge=30, le=300)
    altura_cm: Optional[int] = Field(default=None, ge=100, le=250)
    edad: Optional[int] = Field(default=None, ge=10, le=120)
    sexo_biologico: Optional[Literal['hombre', 'mujer']] = None
    nivel_actividad: Optional[Literal[
        'sedentario', 'moderado', 'activo', 'muy_activo'
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
    # Perfil biométrico básico
    peso_kg: Optional[float] = None
    altura_cm: Optional[int] = None
    edad: Optional[int] = None
    sexo_biologico: Optional[str] = None
    nivel_actividad: Optional[str] = None

    @property
    def tdee(self) -> Optional[int]:
        """TDEE = TMB Mifflin-St Jeor × factor actividad ± ajuste objetivo."""
        if not all([self.peso_kg, self.altura_cm, self.edad, self.sexo_biologico]):
            return None
        if self.sexo_biologico == 'hombre':
            tmb = 10 * self.peso_kg + 6.25 * self.altura_cm - 5 * self.edad + 5
        else:
            tmb = 10 * self.peso_kg + 6.25 * self.altura_cm - 5 * self.edad - 161
        factores = {'sedentario': 1.2, 'moderado': 1.375, 'activo': 1.55, 'muy_activo': 1.725}
        factor = factores.get(self.nivel_actividad or 'moderado', 1.375)
        ajustes = {'mantener': 0, 'perder_peso': -500, 'ganar_musculo': 300, 'tonificar': 200, 'resistencia': 400}
        ajuste = ajustes.get(self.objetivo_fitness, 0)
        return round(tmb * factor + ajuste)

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
