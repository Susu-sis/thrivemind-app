from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional
import base64

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_supabase
from app.core.demo import demo_nutricion
from app.services.nutrition_service import (
    analizar_imagen_nutricional,
    generar_recomendacion_nutricional,
)

router = APIRouter()


@router.post("/nutricion/analizar-imagen", summary="Analizar imagen de plato con GPT-4o Vision")
async def analizar_plato(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    # Demo mode: return pre-built analysis without calling GPT-4o
    if settings.environment == "demo":
        return {
            "nombre_plato": demo_nutricion()["descripcion"],
            "calorias_est": demo_nutricion()["calorias_estimadas"],
            "proteinas_g": demo_nutricion()["proteinas_g"],
            "carbohidratos_g": demo_nutricion()["carbohidratos_g"],
            "grasas_g": demo_nutricion()["grasas_g"],
            "fibra_g": demo_nutricion()["fibra_g"],
            "analisis_texto": "Plato equilibrado con buena proporción de macronutrientes. Rico en fibra y antioxidantes.\n\n[Análisis de demostración — con una API key de OpenAI, GPT-4o Vision analizará tu foto real.]",
            "recomendaciones": "\n".join(demo_nutricion()["recomendaciones"]),
        }

    contents = await file.read()
    imagen_base64 = base64.b64encode(contents).decode("utf-8")

    analisis = await analizar_imagen_nutricional(imagen_base64)

    # Guardar en base de datos
    supabase.table("nutrition_analyses").insert(
        {
            "user_id": current_user["id"],
            "nombre_plato": analisis.get("nombre_plato", "Plato analizado"),
            "calorias_est": analisis.get("calorias_est"),
            "proteinas_g": analisis.get("proteinas_g"),
            "carbohidratos_g": analisis.get("carbohidratos_g"),
            "grasas_g": analisis.get("grasas_g"),
            "fibra_g": analisis.get("fibra_g"),
            "analisis_texto": analisis.get("analisis_texto", ""),
            "recomendaciones": analisis.get("recomendaciones", ""),
        }
    ).execute()

    return analisis


@router.post("/nutricion/recomendacion", summary="Recomendación nutricional personalizada")
async def recomendacion_nutricional(
    estado_emocional: int = 5,
    emocion_principal: str = "neutral",
    energia_fisica: int = 5,
    horas_sueno: float = 7.0,
    objetivo: str = "equilibrio",
    current_user=Depends(get_current_user),
):
    if settings.environment == "demo":
        return {
            "recomendacion": (
                "Para mantener el equilibrio emocional y energético, te recomendamos:\n\n"
                "🥗 **Desayuno**: Avena con frutas frescas, nueces y miel — fibra y energía sostenida\n"
                "🍗 **Almuerzo**: Proteína magra con verduras de hoja verde — triptófano para el ánimo\n"
                "🍵 **Cena**: Sopa ligera con legumbres — magnesio para relajación\n\n"
                "💡 Tu energía está en {}/10, prueba incluir alimentos ricos en hierro y B12.\n\n"
                "[Recomendación de demostración — con OpenAI, será personalizada a tu estado.]"
            ).format(energia_fisica),
            "objetivo": objetivo,
            "alimentos_sugeridos": ["Avena", "Salmón", "Espinaca", "Plátano", "Nueces", "Yogur griego"],
        }

    resultado = await generar_recomendacion_nutricional(
        user_id=current_user["id"],
        checkin_data={
            "estado_emocional": estado_emocional,
            "emocion_principal": emocion_principal,
            "energia_fisica": energia_fisica,
            "horas_sueno": horas_sueno,
            "objetivo": objetivo,
        },
    )
    return resultado


@router.get("/nutricion/historial", summary="Historial de análisis nutricionales")
async def historial_nutricion(
    limit: int = 10,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    result = (
        supabase.table("nutrition_analyses")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
