"""
services/meditation_service.py — Generación de meditaciones personalizadas con LangChain + RAG.

Cadena secuencial de 3 nodos:
1. Análisis del estado emocional → selección de técnica
2. Selección de técnica → parámetros de la sesión
3. Generación del guion de meditación personalizado
"""
import logging
from typing import Optional
from app.core.config import settings
from app.services.rag_service import recuperar_evidencia_cientifica
from app.services.preferences_service import get_user_preferences, build_pillar_context

logger = logging.getLogger(__name__)


async def generar_meditacion(
    user_id: str,
    checkin_data: dict,
    supabase,
    objetivo: str = "calma",
    duracion_minutos: int = 10,
) -> dict:
    """
    Genera una meditación personalizada con evidencia científica.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    prefs = await get_user_preferences(user_id, supabase)
    pillar_context = build_pillar_context(prefs)

    profundidad_map = {
        1: "técnicas básicas de respiración y relajación muscular progresiva",
        2: "meditación guiada con visualización y trabajo con pensamientos",
        3: "práctica avanzada con body scan, ecuanimidad y emociones difíciles",
    }
    profundidad = profundidad_map.get(prefs.mente_intensidad, profundidad_map[1])

    # Recuperar evidencia RAG
    estado = checkin_data.get("estado_emocional", 5)
    emocion = checkin_data.get("emocion_principal", "neutral")
    consulta_rag = f"meditación {objetivo} {emocion} estado emocional {estado}/10"

    evidencia = await recuperar_evidencia_cientifica(
        consulta=consulta_rag, pilar="mente", max_papers=2
    )

    # Construir system prompt
    system_prompt = f"""Eres un maestro de meditación y bienestar holístico especializado
en neurociencia contemplativa. Generas sesiones de meditación personalizadas.

CONTEXTO DE PILARES DEL USUARIO:
{pillar_context}

NIVEL DE PRÁCTICA: {profundidad}
DURACIÓN OBJETIVO: {duracion_minutos} minutos

{evidencia['contexto_para_prompt'] if evidencia['num_papers'] > 0 else ''}

Genera un guion de meditación completo en español, en segunda persona (tú),
con instrucciones precisas de respiración y transiciones claras.
Adapta el tono al estado emocional del usuario."""

    human_prompt = (
        f"Estado emocional: {estado}/10\n"
        f"Emoción principal: {emocion}\n"
        f"Energía física: {checkin_data.get('energia_fisica', 5)}/10\n"
        f"Horas de sueño: {checkin_data.get('horas_sueno', 7)}\n"
        f"Objetivo de la sesión: {objetivo}\n"
        f"Duración: {duracion_minutos} minutos\n\n"
        f"Genera el guion completo de meditación."
    )

    try:
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            api_key=settings.openai_api_key,
        )

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ])

        return {
            "guion_meditacion": response.content,
            "tecnica": objetivo,
            "duracion_min": duracion_minutos,
            "objetivo": objetivo,
            "evidencia_cientifica": evidencia.get("citas_apa", []),
            "papers_utilizados": evidencia.get("num_papers", 0),
        }

    except Exception as e:
        logger.error(f"Error generando meditación: {e}")
        raise


async def generar_audio_meditacion(guion: str) -> Optional[str]:
    """
    Genera audio de la meditación usando ElevenLabs.
    Retorna URL del audio o None si ElevenLabs no está configurado.
    """
    if not settings.elevenlabs_api_key:
        logger.info("ElevenLabs no configurado — omitiendo generación de audio")
        return None

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}",
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": guion[:5000],
                    "model_id": "eleven_multilingual_v2",
                },
                timeout=60.0,
            )
            if response.status_code == 200:
                # In production, upload to Supabase Storage and return URL
                logger.info("Audio generado exitosamente")
                return None  # placeholder — would return storage URL
            else:
                logger.warning(f"ElevenLabs returned {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"Error generando audio: {e}")
        return None
