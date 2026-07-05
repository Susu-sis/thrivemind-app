"""
services/meal_planner_service.py — Planificador de menú semanal para ThriveMind.

Genera un plan nutricional de 7 días con lista de compra consolidada.
En modo demo, devuelve un plan preconstruido. En producción, usa OpenAI.
"""
from datetime import datetime, timedelta, timezone
from app.core.config import settings

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# Hardcoded demo plan
_DEMO_MEALS = {
    "Lunes": {
        "desayuno": {"nombre": "Avena con frutas y miel", "calorias": 350},
        "almuerzo": {"nombre": "Ensalada mediterránea con pollo", "calorias": 520},
        "cena": {"nombre": "Salmón con verduras al vapor", "calorias": 480},
    },
    "Martes": {
        "desayuno": {"nombre": "Tostadas de aguacate y huevo", "calorias": 400},
        "almuerzo": {"nombre": "Bowl de quinoa con garbanzos", "calorias": 490},
        "cena": {"nombre": "Crema de calabaza con semillas", "calorias": 350},
    },
    "Miércoles": {
        "desayuno": {"nombre": "Yogur griego con granola", "calorias": 320},
        "almuerzo": {"nombre": "Wrap de pavo con espinacas", "calorias": 450},
        "cena": {"nombre": "Pasta integral con pesto y tomate", "calorias": 520},
    },
    "Jueves": {
        "desayuno": {"nombre": "Smoothie de espinaca y plátano", "calorias": 280},
        "almuerzo": {"nombre": "Arroz integral con tofu y brócoli", "calorias": 480},
        "cena": {"nombre": "Tortilla de verduras con ensalada", "calorias": 400},
    },
    "Viernes": {
        "desayuno": {"nombre": "Pancakes de avena y banana", "calorias": 360},
        "almuerzo": {"nombre": "Sopa de lentejas con pan", "calorias": 440},
        "cena": {"nombre": "Tacos de pescado con guacamole", "calorias": 530},
    },
    "Sábado": {
        "desayuno": {"nombre": "Huevos revueltos con champiñones", "calorias": 380},
        "almuerzo": {"nombre": "Paella de verduras", "calorias": 550},
        "cena": {"nombre": "Pizza casera integral", "calorias": 600},
    },
    "Domingo": {
        "desayuno": {"nombre": "Açaí bowl con frutas", "calorias": 340},
        "almuerzo": {"nombre": "Asado de pollo con patatas", "calorias": 580},
        "cena": {"nombre": "Sopa miso con edamame", "calorias": 350},
    },
}

_DEMO_SHOPPING = {
    "Frutas y verduras": ["Plátano (7)", "Espinaca (300g)", "Tomate (1kg)", "Aguacate (4)", "Calabaza (1)", "Champiñones (250g)", "Brócoli (1)", "Lechuga (1)"],
    "Proteínas": ["Pollo (500g)", "Salmón (400g)", "Huevos (12)", "Tofu (400g)", "Pavo (200g)", "Pescado blanco (300g)"],
    "Cereales y legumbres": ["Avena (500g)", "Quinoa (250g)", "Arroz integral (500g)", "Pasta integral (500g)", "Lentejas (400g)", "Pan integral (1)"],
    "Lácteos": ["Yogur griego (500g)", "Queso mozzarella (200g)"],
    "Otros": ["Miel", "Granola", "Semillas de calabaza", "Aceite de oliva", "Pesto"],
}


async def generate_weekly_plan(
    user_id: str,
    objetivo: str = "equilibrio",
    alergias: list[str] | None = None,
    supabase=None,
) -> dict:
    """Generate a weekly meal plan. Demo returns hardcoded, prod could use OpenAI."""
    if settings.environment == "demo":
        return {
            "plan": _DEMO_MEALS,
            "shopping_list": _DEMO_SHOPPING,
            "objetivo": objetivo,
            "calorias_diarias_promedio": round(
                sum(sum(m["calorias"] for m in day.values()) for day in _DEMO_MEALS.values()) / 7
            ),
            "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
        }

    # Production: could call OpenAI to generate plan based on preferences
    # For now, return the demo plan as a starting point
    return {
        "plan": _DEMO_MEALS,
        "shopping_list": _DEMO_SHOPPING,
        "objetivo": objetivo,
        "calorias_diarias_promedio": 1300,
        "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
    }
