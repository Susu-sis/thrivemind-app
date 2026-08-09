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


def _scale_plan_to_target(plan: dict, target_kcal: int) -> dict:
    """Scale each meal's calories so the daily average matches target_kcal."""
    demo_avg = sum(sum(m["calorias"] for m in day.values()) for day in plan.values()) / len(plan)
    if demo_avg == 0:
        return plan
    ratio = target_kcal / demo_avg
    scaled = {}
    for day, meals in plan.items():
        scaled[day] = {slot: {**meal, "calorias": round(meal["calorias"] * ratio)} for slot, meal in meals.items()}
    return scaled


async def generate_weekly_plan(
    user_id: str,
    objetivo: str = "equilibrio",
    alergias: list[str] | None = None,
    supabase=None,
    target_kcal: int | None = None,
) -> dict:
    """Generate a weekly meal plan. Demo returns hardcoded, prod could use OpenAI."""
    if settings.environment == "demo":
        plan = _scale_plan_to_target(_DEMO_MEALS, target_kcal) if target_kcal else _DEMO_MEALS
        actual_avg = round(sum(sum(m["calorias"] for m in day.values()) for day in plan.values()) / 7)
        return {
            "plan": plan,
            "shopping_list": _DEMO_SHOPPING,
            "objetivo": objetivo,
            "calorias_diarias_promedio": actual_avg,
            "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
        }

    # Production: call OpenAI to generate a personalised plan
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        import json

        llm = ChatOpenAI(model=settings.openai_model, temperature=0.8, api_key=settings.openai_api_key)
        system = """Eres un nutricionista experto en alimentación funcional y bienestar holístico.
Genera un plan de comidas semanal variado y equilibrado en JSON con exactamente esta estructura:
{
  "Lunes": {"desayuno": {"nombre": "...", "calorias": 000}, "almuerzo": {...}, "cena": {...}},
  "Martes": {...}, "Miércoles": {...}, "Jueves": {...}, "Viernes": {...}, "Sábado": {...}, "Domingo": {...}
}
Solo devuelve el JSON, sin texto adicional."""
        response = await llm.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Genera un plan semanal para objetivo: {objetivo}. Sé creativo y variado."),
        ])
        plan = json.loads(response.content)
        cal_avg = round(sum(
            sum(m.get("calorias", 400) for m in day.values())
            for day in plan.values()
        ) / 7)
        cal_avg = target_kcal if target_kcal else cal_avg
        return {
            "plan": plan,
            "shopping_list": _DEMO_SHOPPING,
            "objetivo": objetivo,
            "calorias_diarias_promedio": cal_avg,
            "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
            "generado_por": "gpt-4o",
        }
    except Exception:
        pass

    # Fallback to demo plan
    fallback_plan = _scale_plan_to_target(_DEMO_MEALS, target_kcal) if target_kcal else _DEMO_MEALS
    fallback_avg = target_kcal or round(
        sum(sum(m["calorias"] for m in day.values()) for day in fallback_plan.values()) / 7
    )
    return {
        "plan": fallback_plan,
        "shopping_list": _DEMO_SHOPPING,
        "objetivo": objetivo,
        "calorias_diarias_promedio": fallback_avg,
        "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
    }
