"""
services/rag_service.py — Retrieval-Augmented Generation para ThriveMind.

Busca papers científicos relevantes en Supabase pgvector antes de que
los agentes de IA generen recomendaciones, anclando todo en evidencia.
"""
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

_openai_client: Optional[AsyncOpenAI] = None


def _get_openai_client() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        if not settings.openai_api_key:
            raise ValueError("openai_api_key no está configurada")
        _openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _openai_client


async def _generar_embedding(texto: str) -> list[float]:
    client = _get_openai_client()
    response = await client.embeddings.create(
        input=texto,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def _formatear_cita(paper: dict) -> str:
    autores = paper.get("authors", "Autores desconocidos")
    año = paper.get("year", "s.f.")
    titulo = paper.get("title", "Sin título")
    revista = paper.get("journal", "")
    doi = paper.get("doi", "")

    cita = f"{autores} ({año}). {titulo}."
    if revista:
        cita += f" {revista}."
    if doi:
        cita += f" DOI: {doi}"
    return cita


async def recuperar_evidencia_cientifica(
    consulta: str,
    pilar: Optional[str] = None,
    max_papers: int = 2,
) -> dict:
    """
    Busca los papers científicos más relevantes para una consulta dada.
    """
    from app.core.database import get_supabase_client

    try:
        logger.info(f"RAG: Generando embedding para: '{consulta[:60]}...'")
        query_embedding = await _generar_embedding(consulta)

        supabase = get_supabase_client()
        response = supabase.rpc(
            "match_papers",
            {
                "query_embedding": query_embedding,
                "match_count": max_papers,
                "filter_pillar": pilar,
            },
        ).execute()

        papers = response.data or []

        if not papers:
            return {"papers": [], "contexto_para_prompt": "", "citas_apa": [], "num_papers": 0}

        lineas_contexto = [
            "EVIDENCIA CIENTÍFICA RELEVANTE PARA ESTA RECOMENDACIÓN:",
            "Basa tu respuesta en la siguiente literatura científica verificada:",
            "",
        ]
        citas_apa = []

        for i, paper in enumerate(papers, 1):
            similitud = paper.get("similarity", 0)
            if similitud < 0.3:
                continue

            cita = _formatear_cita(paper)
            citas_apa.append(cita)
            lineas_contexto.extend([
                f"[{i}] {cita}",
                f"    Relevancia: {paper.get('relevance_for_prompt', '')}",
                f"    Abstract: {paper.get('abstract', '')[:300]}...",
                "",
            ])

        lineas_contexto.extend([
            "INSTRUCCIÓN: Menciona la evidencia científica cuando sea relevante.",
            "Usa el formato: 'Según [Autor, Año], ...'",
            "No inventes referencias — solo usa las proporcionadas arriba.",
        ])

        return {
            "papers": papers,
            "contexto_para_prompt": "\n".join(lineas_contexto),
            "citas_apa": citas_apa,
            "num_papers": len(papers),
        }
    except Exception as e:
        logger.error(f"RAG: Error para '{consulta[:40]}': {e}")
        return {"papers": [], "contexto_para_prompt": "", "citas_apa": [], "num_papers": 0, "error": str(e)}
