"""
services/nutrition_service.py — Análisis nutricional con GPT-4o Vision + recomendaciones.

Funcionalidades:
1. Análisis de imagen de plato con GPT-4o Vision (multimodal)
2. Recomendaciones nutricionales personalizadas basadas en KB
3. Nutrición compensatoria según clima
"""
import base64
import logging
from typing import Optional
from app.core.config import settings
from app.services.rag_service import recuperar_evidencia_cientifica

logger = logging.getLogger(__name__)


async def analizar_imagen_nutricional(
    imagen_base64: str,
    descripcion: Optional[str] = None,
    user_context: Optional[dict] = None,
) -> dict:
    """
    Analiza una imagen de comida usando GPT-4o Vision.
    Devuelve estimaciones nutricionales y recomendaciones.
    """
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    evidencia = await recuperar_evidencia_cientifica(
        consulta="análisis nutricional alimentos neurotransmisores",
        pilar="nutricion",
        max_papers=2,
    )

    system_prompt = """Eres un nutricionista especializado en nutrición funcional
y neurociencia. Analiza la imagen del plato y proporciona:

1. IDENTIFICACIÓN: Nombre del plato y lista de ingredientes visibles
2. ESTIMACIÓN NUTRICIONAL (por porción):
   - Calorías estimadas
   - Proteínas (g)
   - Carbohidratos (g)
   - Grasas (g)
   - Fibra (g)
3. ANÁLISIS NEUROQUÍMICO: Qué neurotransmisores favorece este plato
4. RECOMENDACIONES: Cómo mejorar el plato para optimizar el bienestar

Responde en español. Sé específico con las cantidades.
Formato JSON con campos: nombre_plato, ingredientes, calorias_est,
proteinas_g, carbohidratos_g, grasas_g, fibra_g, analisis_texto, recomendaciones."""

    if evidencia["num_papers"] > 0:
        system_prompt += f"\n\n{evidencia['contexto_para_prompt']}"

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Analiza este plato. {descripcion or 'Sin descripción adicional.'}",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imagen_base64}",
                        "detail": "high",
                    },
                },
            ],
        },
    ]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1500,
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        import json
        resultado = json.loads(response.choices[0].message.content)
        resultado["evidencia_cientifica"] = evidencia.get("citas_apa", [])
        return resultado

    except Exception as e:
        logger.error(f"Error analizando imagen: {e}")
        raise


async def generar_recomendacion_nutricional(
    user_id: str,
    checkin_data: dict,
    clima: Optional[str] = None,
    hora_actual: Optional[str] = None,
) -> dict:
    """
    Genera una recomendación nutricional personalizada basada en el estado del
    usuario, el clima actual y la hora del día (crononutrición).
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    evidencia = await recuperar_evidencia_cientifica(
        consulta=f"nutrición {checkin_data.get('emocion_principal', 'bienestar')} "
                 f"estado emocional {checkin_data.get('estado_emocional', 5)}/10",
        pilar="nutricion",
        max_papers=2,
    )

    system_prompt = f"""Eres un experto en nutrición funcional y neurobiología.
Genera recomendaciones nutricionales personalizadas basadas en el estado del usuario.

Estado emocional: {checkin_data.get('estado_emocional', 5)}/10
Emoción principal: {checkin_data.get('emocion_principal', 'neutral')}
Energía física: {checkin_data.get('energia_fisica', 5)}/10
Hora del día: {hora_actual or 'no especificada'}
Clima actual: {clima or 'no disponible'}

{evidencia['contexto_para_prompt'] if evidencia['num_papers'] > 0 else ''}

Responde en español con recomendaciones específicas: qué comer, por qué
(mecanismo bioquímico), y cuándo. Incluye referencias si están disponibles."""

    try:
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.5,
            api_key=settings.openai_api_key,
        )
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Genera mi recomendación nutricional personalizada para hoy."),
        ])

        return {
            "recomendacion": response.content,
            "evidencia_cientifica": evidencia.get("citas_apa", []),
            "clima_considerado": clima,
            "hora_considerada": hora_actual,
        }
    except Exception as e:
        logger.error(f"Error en recomendación nutricional: {e}")
        raise
