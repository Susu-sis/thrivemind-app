"""
services/hue_service.py — Orquestación Ambiental con Philips Hue

Controla la iluminación de forma terapéutica basándose en el estado
del usuario y el módulo activo de ThriveMind. Incluye modo simulación
para cuando el Bridge no está disponible.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Perfiles neurobiológicos calibrados
PERFILES_TERAPEUTICOS = {
    "meditacion_calma": {
        "bri": 77,
        "ct": 454,
        "descripcion": "Luz cálida y tenue para meditación profunda",
        "justificacion": "2200K suprime cortisol y activa el nervio vago",
    },
    "meditacion_enfoque": {
        "bri": 178,
        "ct": 250,
        "descripcion": "Luz neutra media para concentración y enfoque",
        "justificacion": "4000K mejora rendimiento cognitivo (Viola et al.)",
    },
    "meditacion_energia": {
        "bri": 254,
        "ct": 153,
        "descripcion": "Luz fría brillante para activación y energía",
        "justificacion": "6500K suprime melatonina y activa cortisol matutino",
    },
    "nutricion_comida": {
        "bri": 200,
        "ct": 350,
        "descripcion": "Luz cálida-media para acompañar la comida consciente",
        "justificacion": "3000K promueve la relajación digestiva parasimpática",
    },
    "farming_cuidado": {
        "bri": 150,
        "ct": 300,
        "descripcion": "Luz natural simulada para cuidado de plantas",
        "justificacion": "Estimula ritmo circadiano natural del usuario",
    },
    "descanso_nocturno": {
        "bri": 38,
        "ct": 500,
        "descripcion": "Luz mínima ultra-cálida para preparar el sueño",
        "justificacion": "2000K maximiza producción de melatonina (Czeisler)",
    },
}

# Mapeo del Motor de Contexto a perfiles reales
MAPA_CONTEXTO_A_PERFIL = {
    "amanecer_activacion": "meditacion_energia",
    "enfoque_trabajo": "meditacion_enfoque",
    "mediodia_reset": "meditacion_enfoque",
    "tarde_desconexion": "meditacion_calma",
    "noche_relajacion": "meditacion_calma",
    "noche_sueno": "descanso_nocturno",
    "tormenta_anclaje": "meditacion_calma",
    "lluvia_introspeccion": "meditacion_calma",
    "calor_extremo": "meditacion_energia",
    "neutro": "meditacion_calma",
}


class HueAmbientService:
    """Servicio de orquestación ambiental con Philips Hue."""

    def __init__(self, bridge_ip: Optional[str] = None, modo_fallback: str = "simulacion"):
        self.bridge_ip = bridge_ip or settings.hue_bridge_ip
        self.bridge = None
        self.modo = "simulacion"

        if self.bridge_ip:
            try:
                from phue import Bridge
                self.bridge = Bridge(self.bridge_ip)
                self.bridge.connect()
                self.modo = "live"
                logger.info(f"Hue Bridge conectado en {self.bridge_ip}")
            except Exception as e:
                logger.warning(f"Hue Bridge no disponible: {e}. Modo simulación activado.")
                self.modo = "simulacion"

    def get_status(self) -> dict:
        if self.modo == "live" and self.bridge:
            try:
                lights = self.bridge.get_light_objects("name")
                return {
                    "connected": True,
                    "mode": "live",
                    "bridge_ip": self.bridge_ip,
                    "lights": list(lights.keys()),
                }
            except Exception:
                pass
        return {
            "connected": False,
            "mode": "simulation",
            "bridge_ip": self.bridge_ip,
            "message": "Bridge no disponible. Perfiles se aplican en modo simulación.",
        }

    def apply_profile(self, profile_name: str) -> dict:
        # Resolver alias del Motor de Contexto
        resolved = MAPA_CONTEXTO_A_PERFIL.get(profile_name, profile_name)

        if resolved not in PERFILES_TERAPEUTICOS:
            return {"success": False, "error": f"Perfil '{profile_name}' no encontrado"}

        perfil = PERFILES_TERAPEUTICOS[resolved]

        if self.modo == "live" and self.bridge:
            try:
                lights = self.bridge.get_light_objects("name")
                command = {"bri": perfil["bri"], "ct": perfil["ct"], "on": True}
                for light in lights.values():
                    light.brightness = perfil["bri"]
                    light.colortemp_k = None  # use mired
                self.bridge.set_light([l.name for l in lights.values()], command)
                return {
                    "success": True,
                    "modo": "live",
                    "perfil_aplicado": resolved,
                    "descripcion": perfil["descripcion"],
                }
            except Exception as e:
                logger.error(f"Error al aplicar perfil Hue: {e}")

        # Modo simulación
        return {
            "success": True,
            "modo": "simulacion",
            "perfil_aplicado": resolved,
            "descripcion": perfil["descripcion"],
            "justificacion": perfil["justificacion"],
            "valores_simulados": {
                "brillo": perfil["bri"],
                "temperatura_color": perfil["ct"],
            },
        }

    def auto_select_profile(
        self,
        mood_score: int,
        energy_score: int,
        objetivo: str,
        hora: int,
    ) -> str:
        """Selección automática de perfil basada en estado del usuario."""
        # Noche: siempre descanso
        if hora >= 22 or hora < 6:
            return "descanso_nocturno"

        # Por objetivo
        if objetivo == "sueno":
            return "descanso_nocturno"
        if objetivo in ("enfoque", "rendimiento_cognitivo"):
            return "meditacion_enfoque"

        # Por estado emocional y energía
        if mood_score <= 4:
            return "meditacion_calma"
        if energy_score <= 4:
            return "meditacion_calma"
        if energy_score >= 8:
            return "meditacion_energia"

        return "meditacion_enfoque"


# Singleton
hue_service = HueAmbientService()
