"""
services/solar_service.py — Datos de amanecer/atardecer para contexto circadiano.

Usa la API gratuita sunrise-sunset.org (sin autenticación).
"""
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


async def obtener_datos_solares(lat: float = 52.37, lon: float = 4.90) -> dict:
    """
    Obtiene horarios de amanecer/atardecer para una ubicación.
    Default: Amsterdam (52.37, 4.90).
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.sunrise-sunset.org/json",
                params={"lat": lat, "lng": lon, "formatted": 0},
            )
            response.raise_for_status()
            data = response.json()

        if data.get("status") != "OK":
            return _solar_fallback()

        results = data["results"]
        return {
            "amanecer": results["sunrise"],
            "atardecer": results["sunset"],
            "mediodia_solar": results["solar_noon"],
            "duracion_dia": results["day_length"],
            "crepusculo_civil_inicio": results["civil_twilight_begin"],
            "crepusculo_civil_fin": results["civil_twilight_end"],
            "lat": lat,
            "lon": lon,
        }

    except Exception as e:
        logger.error(f"Error obteniendo datos solares: {e}")
        return _solar_fallback()


def _solar_fallback() -> dict:
    return {
        "amanecer": "07:00:00+00:00",
        "atardecer": "19:00:00+00:00",
        "mediodia_solar": "13:00:00+00:00",
        "duracion_dia": 43200,
        "lat": 52.37,
        "lon": 4.90,
    }
