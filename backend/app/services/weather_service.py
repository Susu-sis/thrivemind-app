"""
services/weather_service.py — Integración con OpenWeatherMap para contexto climático.

El clima afecta directamente a los neurotransmisores del usuario.
Este servicio obtiene el clima actual y lo inyecta en el contexto de la IA.
"""
import logging
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache simple para no llamar a la API en cada request
_weather_cache: dict = {}
_cache_timestamps: dict = {}
CACHE_TTL_SECONDS = 300  # 5 minutos (era 30 min, reducido para datos más frescos)


async def obtener_clima_actual(
    ciudad: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> dict:
    """
    Obtiene el clima actual desde OpenWeatherMap.
    """
    import time

    global _weather_cache, _cache_timestamps

    # Check cache (per-key TTL)
    now = time.time()
    cache_key = f"{ciudad or ''}{lat or ''}{lon or ''}"
    if cache_key in _weather_cache and (now - _cache_timestamps.get(cache_key, 0)) < CACHE_TTL_SECONDS:
        logger.debug("Weather cache HIT for key=%s", cache_key)
        return _weather_cache[cache_key]

    if not settings.openweathermap_api_key:
        return _clima_fallback()

    ciudad_query = ciudad or settings.weather_default_city

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if lat and lon:
                url = (
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?lat={lat}&lon={lon}"
                    f"&appid={settings.openweathermap_api_key}"
                    f"&units=metric&lang=es"
                )
            else:
                url = (
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?q={ciudad_query}"
                    f"&appid={settings.openweathermap_api_key}"
                    f"&units=metric&lang=es"
                )

            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        resultado = {
            "ciudad": data.get("name", ciudad_query),
            "temperatura": data["main"]["temp"],
            "sensacion_termica": data["main"]["feels_like"],
            "humedad": data["main"]["humidity"],
            "descripcion": data["weather"][0]["description"],
            "icono": data["weather"][0]["icon"],
            "condicion": data["weather"][0]["main"].lower(),
            "nubosidad": data["clouds"]["all"],
            "viento_kmh": round(data["wind"]["speed"] * 3.6, 1),
            "presion": data["main"]["pressure"],
        }

        # Clasificar para la KB
        resultado["clasificacion_kb"] = _clasificar_clima(resultado)

        _weather_cache[cache_key] = resultado
        _cache_timestamps[cache_key] = now
        return resultado

    except Exception as e:
        logger.error(f"Error obteniendo clima: {e}")
        return _clima_fallback()


def _clasificar_clima(clima: dict) -> str:
    """Clasifica el clima en una de las categorías de WEATHER_MOOD_BASELINE."""
    condicion = clima.get("condicion", "")
    temp = clima.get("temperatura", 20)
    humedad = clima.get("humedad", 50)
    nubosidad = clima.get("nubosidad", 0)

    if temp > 30:
        return "ola_calor"
    if temp < 5:
        return "invierno_riguroso"
    if "rain" in condicion or "drizzle" in condicion:
        return "lluvia"
    if humedad > 70 and temp > 20:
        return "alta_humedad"
    if nubosidad > 80:
        return "nublado_prolongado" if nubosidad > 90 else "nublado_leve"
    if clima.get("viento_kmh", 0) > 40:
        return "viento_fohn"
    return "soleado"


def _clima_fallback() -> dict:
    """Datos de clima por defecto cuando la API no está disponible."""
    return {
        "ciudad": "No disponible",
        "temperatura": 20,
        "sensacion_termica": 20,
        "humedad": 50,
        "descripcion": "Datos climáticos no disponibles",
        "condicion": "unknown",
        "nubosidad": 50,
        "viento_kmh": 10,
        "presion": 1013,
        "clasificacion_kb": "soleado",
    }


# Alias used by entorno endpoint
async def obtener_clima(lat: float = None, lon: float = None) -> dict:
    return await obtener_clima_actual(lat=lat, lon=lon)
