"""
services/sentiment_service.py — Lightweight sentiment/emotion extraction.

Uses keyword matching for the demo and optionally GPT for production.
Extracts dominant emotions and keyword clouds from check-in notes.
"""
import re
import logging
from collections import Counter
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Keyword dictionaries (Spanish) ───────────────────────────────────────────

EMOTION_KEYWORDS: dict[str, list[str]] = {
    "ansiedad":     ["ansiedad", "ansioso", "nervioso", "preocupado", "preocupación", "tenso", "agobio", "angustia"],
    "calma":        ["calma", "tranquilo", "sereno", "paz", "relajado", "calmado"],
    "alegría":      ["alegría", "feliz", "contento", "emocionado", "bien", "genial", "estupendo"],
    "tristeza":     ["triste", "tristeza", "desanimado", "melancólico", "solo", "soledad"],
    "cansancio":    ["cansado", "cansancio", "agotado", "exhausto", "sin energía", "fatigado"],
    "energía":      ["energía", "energético", "activo", "motivado", "productivo", "fuerte"],
    "gratitud":     ["agradecido", "gratitud", "agradecer", "bendecido", "afortunado"],
    "frustración":  ["frustrado", "frustración", "molesto", "enojado", "impotencia"],
    "esperanza":    ["esperanza", "ilusión", "optimismo", "optimista", "mejorar"],
}


def analyze_text(text: str) -> dict:
    """
    Analyze a single text and return emotion scores and keywords.
    """
    if not text or not text.strip():
        return {"emotions": {}, "keywords": [], "dominant_emotion": None}

    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)

    # Score each emotion
    scores: dict[str, int] = {}
    matched_kw: list[str] = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = 0
        for kw in keywords:
            if kw in text_lower:
                count += 1
                matched_kw.append(kw)
        if count > 0:
            scores[emotion] = count

    dominant = max(scores, key=scores.get) if scores else None

    return {
        "emotions": scores,
        "keywords": matched_kw,
        "dominant_emotion": dominant,
    }


def analyze_weekly_notes(notes: list[str]) -> dict:
    """
    Aggregate emotion analysis across multiple check-in notes.
    Returns keyword cloud data, emotion distribution, and insights.
    """
    all_emotions: Counter = Counter()
    all_keywords: Counter = Counter()
    total_notes = 0

    for note in notes:
        if not note:
            continue
        total_notes += 1
        result = analyze_text(note)
        for emotion, count in result["emotions"].items():
            all_emotions[emotion] += count
        for kw in result["keywords"]:
            all_keywords[kw] += 1

    if total_notes == 0:
        return {
            "total_notes_analyzed": 0,
            "emotion_distribution": {},
            "keyword_cloud": [],
            "top_emotions": [],
            "insight": "No hay notas con texto para analizar esta semana.",
        }

    # Normalize to percentages
    total_hits = sum(all_emotions.values()) or 1
    distribution = {k: round(v / total_hits * 100, 1) for k, v in all_emotions.most_common()}

    keyword_cloud = [{"word": w, "count": c} for w, c in all_keywords.most_common(15)]
    top_emotions = [{"emotion": e, "score": s, "pct": round(s / total_hits * 100, 1)}
                    for e, s in all_emotions.most_common(3)]

    # Generate insight
    if top_emotions:
        top = top_emotions[0]
        insight = f"Esta semana la emoción predominante fue **{top['emotion']}** ({top['pct']}%). "
        if len(top_emotions) > 1:
            insight += f"También apareció **{top_emotions[1]['emotion']}**."
    else:
        insight = "No se detectaron emociones específicas en las notas."

    return {
        "total_notes_analyzed": total_notes,
        "emotion_distribution": distribution,
        "keyword_cloud": keyword_cloud,
        "top_emotions": top_emotions,
        "insight": insight,
    }
