"""
services/farming_service.py — Servicio de micro-farming con recomendaciones inteligentes.

Conecta el estado biométrico del usuario (HRV, emoción) con recomendaciones
de plantas específicas del micro-huerto basadas en evidencia.
"""
import logging
from datetime import date, timedelta
from typing import Optional
from app.core.config import settings
from app.services.rag_service import recuperar_evidencia_cientifica

logger = logging.getLogger(__name__)


# Mapeo simplificado de estado emocional a planta recomendada
PLANTA_POR_ESTADO = {
    "ansiedad": "lavanda",
    "estres": "lavanda",
    "fatiga_cognitiva": "menta_piperita",
    "foco_bajo": "romero",
    "insomnio": "lavanda",
    "tristeza": "girasol_microgreen",
    "neutral": "albahaca",
    "calma": "menta_piperita",
    "energia": "romero",
}


async def get_plant_recommendation(
    user_id: str,
    emocion_principal: str,
    estado_emocional: int,
    supabase,
) -> dict:
    """
    Recomienda una planta del micro-huerto basada en el estado emocional.
    """
    planta_key = PLANTA_POR_ESTADO.get(emocion_principal, "albahaca")

    evidencia = await recuperar_evidencia_cientifica(
        consulta=f"planta {planta_key} {emocion_principal} efecto terapéutico",
        pilar="naturaleza",
        max_papers=2,
    )

    return {
        "planta_recomendada": planta_key,
        "razon": f"Basado en tu estado emocional ({emocion_principal}, {estado_emocional}/10)",
        "evidencia_cientifica": evidencia.get("citas_apa", []),
    }


async def check_harvest_readiness(user_id: str, supabase) -> list[dict]:
    """
    Verifica qué cultivos están listos para cosechar.
    """
    result = supabase.table("cultivos_activos") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("activo", True) \
        .execute()

    cultivos = result.data or []
    listos = []

    for cultivo in cultivos:
        if cultivo.get("fecha_cosecha_est"):
            fecha_cosecha = date.fromisoformat(cultivo["fecha_cosecha_est"])
            dias_restantes = (fecha_cosecha - date.today()).days
            if dias_restantes <= 2:
                listos.append({
                    "id": cultivo["id"],
                    "nombre_planta": cultivo["nombre_planta"],
                    "dias_restantes": max(0, dias_restantes),
                    "listo": dias_restantes <= 0,
                })

    return listos


async def generar_consejo_farming(
    user_id: str,
    consulta: str,
    cultivos_activos: list[dict],
) -> dict:
    """
    Genera un consejo de farming personalizado usando LangChain + RAG.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    evidencia = await recuperar_evidencia_cientifica(
        consulta=f"micro-farming {consulta}",
        pilar="naturaleza",
        max_papers=2,
    )

    cultivos_texto = ", ".join([c.get("nombre_planta", "planta") for c in cultivos_activos]) or "ninguno"

    system_prompt = f"""Eres un experto en horticultura urbana y micro-farming terapéutico.
Ayudas a usuarios a mantener su micro-huerto doméstico como intervención de bienestar.

Cultivos activos del usuario: {cultivos_texto}

{evidencia['contexto_para_prompt'] if evidencia['num_papers'] > 0 else ''}

Responde en español, de forma práctica y concreta."""

    try:
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.6,
            api_key=settings.openai_api_key,
        )
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=consulta),
        ])
        return {
            "respuesta": response.content,
            "evidencia_cientifica": evidencia.get("citas_apa", []),
        }
    except Exception as e:
        logger.error(f"Error generando consejo farming: {e}")
        raise
