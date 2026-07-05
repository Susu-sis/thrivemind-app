"""
core/demo.py — Demo mode support for running without real API keys.

When environment=demo in .env, the app uses mock data instead of hitting
Supabase, OpenAI, etc. This lets you explore the UI and API structure.
"""
from datetime import datetime, timedelta
import uuid
import random

DEMO_USER_ID = "demo-user-00000000-0000-0000-0000-000000000001"

DEMO_USER = {
    "id": DEMO_USER_ID,
    "email": "demo@thrivemind.app",
    "nombre": "Demo User",
    "created_at": "2025-01-01T00:00:00Z",
}

EMOCIONES = ["sereno", "energético", "ansioso", "neutral", "motivado", "cansado", "agradecido"]

NOTAS_DEMO = [
    "Hoy me sentí muy tranquilo después de meditar por la mañana.",
    "Día estresante en el trabajo, necesito desconectar.",
    "La caminata al aire libre me ayudó a despejar la mente.",
    "Dormí muy bien anoche, me siento con mucha energía.",
    "Algo ansioso por la presentación de mañana.",
    "Estoy agradecido por el tiempo con mi familia hoy.",
    None,
    "Regar las plantas me relajó bastante esta tarde.",
    "Me costó concentrarme, quizás dormí poco.",
    None,
    "Sesión de yoga increíble, cuerpo y mente en paz.",
    "Día productivo, logré completar varias metas.",
    None,
    "La lluvia me puso melancólico pero aproveché para leer.",
]


def demo_checkins(days: int = 14) -> list:
    """Generate fake check-in data for the last N days."""
    data = []
    for i in range(days):
        dt = datetime.utcnow() - timedelta(days=days - 1 - i)
        data.append({
            "id": str(uuid.uuid4()),
            "user_id": DEMO_USER_ID,
            "estado_emocional": random.randint(4, 9),
            "energia_fisica": random.randint(3, 9),
            "claridad_mental": random.randint(4, 9),
            "conexion_entorno": random.randint(3, 8),
            "horas_sueno": round(random.uniform(5.5, 8.5), 1),
            "emocion_principal": random.choice(EMOCIONES),
            "tipo_checkin": "diario",
            "nota_personal": NOTAS_DEMO[i % len(NOTAS_DEMO)],
            "created_at": dt.isoformat() + "Z",
        })
    return data


def demo_meditacion(objetivo: str = "calma", duracion: int = 10) -> dict:
    """Return a pre-written demo meditation."""
    return {
        "id": str(uuid.uuid4()),
        "guion": (
            f"Bienvenido a esta sesión de {duracion} minutos enfocada en {objetivo}.\n\n"
            "Cierra los ojos suavemente. Siente cómo tu cuerpo se apoya en la superficie "
            "donde estás sentado. Toma una respiración profunda... inhala contando hasta 4... "
            "sostén... y exhala lentamente contando hasta 6.\n\n"
            "Observa tus pensamientos sin juzgarlos. Imagina que son nubes que pasan por "
            "un cielo azul infinito. No necesitas aferrarte a ninguno.\n\n"
            "Con cada exhalación, libera cualquier tensión en tus hombros... tu mandíbula... "
            "tus manos. Permite que la calma se expanda desde tu centro hacia todo tu cuerpo.\n\n"
            "[Este es un guion de demostración. Con una API key de OpenAI configurada, "
            "se generará una meditación personalizada basada en tu estado emocional.]"
        ),
        "tecnica": objetivo,
        "audio_url": None,
        "duracion_min": duracion,
        "referencias": [],
    }


def demo_nutricion() -> dict:
    """Return a demo nutrition analysis."""
    return {
        "descripcion": "Plato de avena con frutas frescas, miel y semillas de chía",
        "calorias_estimadas": 420,
        "proteinas_g": 12,
        "carbohidratos_g": 62,
        "grasas_g": 14,
        "fibra_g": 8,
        "recomendaciones": [
            "Excelente fuente de fibra soluble para la salud digestiva",
            "Los antioxidantes de las frutas apoyan la función cerebral",
            "Considera añadir una fuente de proteína (yogur griego) para mayor saciedad",
        ],
    }


def demo_cultivos() -> list:
    """Return demo active crops."""
    base = datetime.utcnow() - timedelta(days=30)
    return [
        {
            "id": str(uuid.uuid4()),
            "user_id": DEMO_USER_ID,
            "nombre_planta": "Albahaca",
            "tipo": "aromática",
            "estado": "crecimiento",
            "fecha_siembra": (base - timedelta(days=20)).date().isoformat(),
            "activo": True,
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": DEMO_USER_ID,
            "nombre_planta": "Tomate cherry",
            "tipo": "hortaliza",
            "estado": "floración",
            "fecha_siembra": (base - timedelta(days=45)).date().isoformat(),
            "activo": True,
        },
    ]


def demo_clima() -> dict:
    """Return demo weather data."""
    return {
        "ciudad": "Amsterdam",
        "temperatura": 18,
        "sensacion_termica": 16,
        "humedad": 65,
        "descripcion": "parcialmente nublado",
        "condicion": "clouds",
        "nubosidad": 55,
        "viento_kmh": 12.5,
        "presion": 1018,
        "clasificacion_kb": "soleado",
    }
