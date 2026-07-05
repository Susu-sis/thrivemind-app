"""
config.py — Configuración central de ThriveMind

Pydantic Settings lee automáticamente las variables del archivo .env
y las valida. Si falta una variable obligatoria, el servidor no arranca
y te dice exactamente qué falta, en lugar de fallar silenciosamente.
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Metadatos de la aplicación
    app_name: str = "ThriveMind API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # JWT
    secret_key: str = "change-me-to-a-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 días

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Voz Rachel (calmada)

    # Philips Hue
    hue_bridge_ip: str = ""
    hueappkey: str = ""

    # Weather
    openweathermap_api_key: str = ""
    weather_default_city: str = "Amsterdam"

    model_config = {
        "env_file": str(_BACKEND_DIR / ".env"),
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """
    @lru_cache() hace que esta función solo cree el objeto Settings una vez
    y lo reutilice en todas las peticiones.
    """
    return Settings()


settings = get_settings()
