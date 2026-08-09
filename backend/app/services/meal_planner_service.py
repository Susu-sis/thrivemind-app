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


# Keywords that signal a food is rich in key neuronutrients (used for nota_hoy matching)
_NUTRIENT_SIGNALS = {
    "serotonina": ["salmón", "pavo", "avena", "espinaca", "huevo", "yogur", "plátano", "miso", "edamame", "sopa"],
    "dopamina":   ["pollo", "lentejas", "quinoa", "tofu", "arroz", "pizza", "asado"],
    "energia":    ["pasta", "arroz", "quinoa", "patatas", "paella", "pan", "pancake"],
}

_STATE_RULES = [
    # (condición, nutriente_objetivo, mensaje_accion)
    (lambda e, em: e <= 4 or em in ["estres", "ansiedad", "tristeza"],
     "serotonina", "Dado tu estrés actual, prioriza este plato — es rico en triptófano, precursor directo de serotonina. Añade una pequeña porción de nueces o chocolate 85% como postre."),
    (lambda e, em: e <= 4 or em in ["cansancio", "fatiga", "agotamiento"],
     "dopamina", "Tu energía está baja. Este plato aporta tirosina para recuperar dopamina. Asegúrate de comer completo y añade un café o té verde si lo necesitas."),
    (lambda e, em: e >= 7,
     "energia", "Tu estado es óptimo. Aprovecha para comer bien y mantener el rendimiento — este plato tiene los carbohidratos complejos que necesitas."),
]


def _generate_state_note(plan: dict, last_checkin: dict | None) -> dict | None:
    """Cross today's plan meals with last check-in state to produce a personalised nota_hoy."""
    if not last_checkin:
        return None
    estado = last_checkin.get("estado_emocional", 5)
    energia = last_checkin.get("energia_fisica", 5)
    emocion = (last_checkin.get("emocion_principal") or "neutral").lower()

    # Pick the first matching rule
    objetivo_nutriente = None
    mensaje = None
    for condicion, nutriente, msg in _STATE_RULES:
        if condicion(estado if estado is not None else 5, emocion):
            objetivo_nutriente = nutriente
            mensaje = msg
            break

    if not objetivo_nutriente:
        return None

    # Find today's best matching meal from the plan
    hoy_nombre = datetime.now(timezone.utc).strftime("%A")
    dias_es = {"Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
               "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"}
    hoy_es = dias_es.get(hoy_nombre, "Lunes")
    hoy_meals = plan.get(hoy_es, {})

    keywords = _NUTRIENT_SIGNALS.get(objetivo_nutriente, [])
    plato_destacado = None
    slot_destacado = None
    for slot in ["cena", "almuerzo", "desayuno"]:
        meal = hoy_meals.get(slot)
        if not meal:
            continue
        nombre_lower = meal["nombre"].lower()
        if any(kw in nombre_lower for kw in keywords):
            plato_destacado = meal["nombre"]
            slot_destacado = slot
            break

    # Fallback: just use cena
    if not plato_destacado and "cena" in hoy_meals:
        plato_destacado = hoy_meals["cena"]["nombre"]
        slot_destacado = "cena"

    if not plato_destacado:
        return None

    slots_es = {"desayuno": "desayuno", "almuerzo": "almuerzo", "cena": "cena"}
    return {
        "dia": hoy_es,
        "slot": slots_es.get(slot_destacado, slot_destacado),
        "plato": plato_destacado,
        "estado_emocional": estado,
        "emocion": emocion,
        "nutriente_objetivo": objetivo_nutriente,
        "mensaje": mensaje,
    }


async def generate_weekly_plan(
    user_id: str,
    objetivo: str = "equilibrio",
    alergias: list[str] | None = None,
    supabase=None,
    target_kcal: int | None = None,
    last_checkin: dict | None = None,
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
            "nota_hoy": _generate_state_note(plan, last_checkin),
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
            "nota_hoy": _generate_state_note(plan, last_checkin),
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
        "nota_hoy": _generate_state_note(fallback_plan, last_checkin),
        "semana_inicio": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "semana_fin": (datetime.now(timezone.utc) + timedelta(days=6)).strftime("%Y-%m-%d"),
    }
