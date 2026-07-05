"""
services/emotional_classifier.py — XGBoost Emotional State Classifier (Capa 1).

Implements the 2-phase classification system from Memoria Técnica §11.2:
  Phase A (cold-start, <30 check-ins): Rule-based heuristic thresholds
  Phase B (trained, ≥30 check-ins): XGBoost with 13 features → 5 classes

5 emotional states (output classes):
  0 = recuperacion_activa — Recovery from stress
  1 = estres_agudo        — Acute stress
  2 = equilibrio           — Balance / homeostasis
  3 = activacion           — Positive activation / flow
  4 = fatiga_cronica       — Chronic fatigue

13 input features:
  F1:  hrv_last_reading (RMSSD ms)
  F2:  hrv_7day_avg
  F3:  hrv_delta (current - avg)
  F4:  sleep_score (0-100)
  F5:  sleep_duration (hours)
  F6:  activity_calories (kcal, 0 if no wearable)
  F7:  hour_of_day (0-23)
  F8:  day_of_week (0-6, Mon=0)
  F9:  checkin_text_sentiment (-1 to 1)
  F10: keyword_anxiety (0/1)
  F11: keyword_fatigue (0/1)
  F12: days_since_meditation (int)
  F13: outdoor_temp (°C)

Ref: Memoria Técnica §11.2.1, §9.5 (Graceful Degradation)
"""
import logging
import math
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Class labels ──────────────────────────────────────────────────────────────
EMOTIONAL_STATES = {
    0: "recuperacion_activa",
    1: "estres_agudo",
    2: "equilibrio",
    3: "activacion",
    4: "fatiga_cronica",
}

STATE_DESCRIPTIONS = {
    "recuperacion_activa": {
        "label": "Recuperación Activa",
        "descripcion": "Transición positiva desde estrés. El sistema se está regulando.",
        "color": "#4CAF50",
    },
    "estres_agudo": {
        "label": "Estrés Agudo",
        "descripcion": "Activación simpática elevada. Necesita intervención calmante.",
        "color": "#F44336",
    },
    "equilibrio": {
        "label": "Equilibrio",
        "descripcion": "Balance autonómico. Estado ideal para actividades cognitivas.",
        "color": "#2196F3",
    },
    "activacion": {
        "label": "Activación Positiva",
        "descripcion": "Estado de alta energía y motivación. Posible flow.",
        "color": "#FF9800",
    },
    "fatiga_cronica": {
        "label": "Fatiga Crónica",
        "descripcion": "Agotamiento sostenido. Priorizar descanso y nutrición reparadora.",
        "color": "#9C27B0",
    },
}

# ── Feature extraction ────────────────────────────────────────────────────────

def extract_features(
    checkin_data: dict,
    checkin_history: Optional[list] = None,
    clima: Optional[dict] = None,
    hora: Optional[int] = None,
) -> dict:
    """
    Extracts 13 features from available data.
    Missing values are set to float('nan') — XGBoost handles NaN natively.
    """
    history = checkin_history or []
    now = datetime.now()
    h = hora if hora is not None else now.hour

    # F1: HRV last reading
    hrv_last = checkin_data.get("hrv_estimado")
    f1 = float(hrv_last) if hrv_last is not None else float("nan")

    # F2: HRV 7-day average
    hrv_vals = [c.get("hrv_estimado") for c in history[:7] if c.get("hrv_estimado") is not None]
    f2 = sum(hrv_vals) / len(hrv_vals) if hrv_vals else float("nan")

    # F3: HRV delta
    f3 = f1 - f2 if not (math.isnan(f1) or math.isnan(f2)) else float("nan")

    # F4: Sleep score (derived: hours/8 * 100, capped at 100)
    sleep_h = checkin_data.get("horas_sueno")
    f4 = min(100.0, (sleep_h / 8.0) * 100) if sleep_h is not None else float("nan")

    # F5: Sleep duration
    f5 = float(sleep_h) if sleep_h is not None else float("nan")

    # F6: Activity calories (no wearable → NaN)
    f6 = float("nan")

    # F7: Hour of day
    f7 = float(h)

    # F8: Day of week
    f8 = float(now.weekday())

    # F9: Sentiment (-1 to 1) from text
    nota = checkin_data.get("nota_personal", "") or checkin_data.get("nota", "")
    f9 = _quick_sentiment(nota) if nota else float("nan")

    # F10: keyword_anxiety
    f10 = 1.0 if _has_anxiety_keywords(nota) else 0.0

    # F11: keyword_fatigue
    f11 = 1.0 if _has_fatigue_keywords(nota) else 0.0

    # F12: Days since last meditation
    med_days = _days_since_meditation(history)
    f12 = float(med_days) if med_days is not None else float("nan")

    # F13: Outdoor temp
    temp = (clima or {}).get("temperatura")
    f13 = float(temp) if temp is not None else float("nan")

    return {
        "features": [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13],
        "feature_names": [
            "hrv_last_reading", "hrv_7day_avg", "hrv_delta",
            "sleep_score", "sleep_duration", "activity_calories",
            "hour_of_day", "day_of_week", "checkin_text_sentiment",
            "keyword_anxiety", "keyword_fatigue",
            "days_since_meditation", "outdoor_temp",
        ],
        "n_available": sum(1 for f in [f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13]
                          if not math.isnan(f)),
        "n_total": 13,
        "degradation_level": _degradation_level(f1, f5, f6),
    }


def _quick_sentiment(text: str) -> float:
    """Quick Spanish sentiment score (-1 to 1) based on keyword matching."""
    positive = ["feliz", "contento", "bien", "genial", "tranquilo", "relajado",
                 "motivado", "energía", "agradecido", "paz", "alegría"]
    negative = ["mal", "triste", "ansioso", "estresado", "cansado", "agotado",
                 "nervioso", "preocupado", "frustrado", "dolor", "insomnio"]
    text_l = text.lower()
    pos = sum(1 for w in positive if w in text_l)
    neg = sum(1 for w in negative if w in text_l)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 2)


def _has_anxiety_keywords(text: str) -> bool:
    keywords = ["ansioso", "ansiedad", "nervioso", "pánico", "angustia", "preocupado"]
    return any(k in text.lower() for k in keywords)


def _has_fatigue_keywords(text: str) -> bool:
    keywords = ["cansado", "agotado", "fatiga", "exhausto", "sin energía", "dormido"]
    return any(k in text.lower() for k in keywords)


def _days_since_meditation(history: list) -> Optional[int]:
    """Check history for meditation-related check-ins."""
    for i, c in enumerate(history):
        if c.get("tipo_checkin") in ("post_meditacion", "pre_meditacion"):
            return i
    return None


def _degradation_level(hrv, sleep, activity) -> str:
    """
    Graceful Degradation Level (Memoria §9.5):
      L1: Only check-in (4 features available)
      L2: +circadian (8 features — no wearable)
      L3: +wearable (13 features — full)
    """
    has_hrv = not math.isnan(hrv) if isinstance(hrv, float) else hrv is not None
    has_activity = not math.isnan(activity) if isinstance(activity, float) else activity is not None

    if has_hrv and has_activity:
        return "L3_full"
    elif has_hrv:
        return "L2_circadian"
    return "L1_checkin_only"


# ── Cold-start heuristic classifier (Phase A: <30 check-ins) ─────────────────

def classify_cold_start(features: dict) -> dict:
    """
    Rule-based classification when insufficient data for ML model.
    Uses simple thresholds on available features.
    """
    vals = features["features"]
    hrv = vals[0]        # F1
    sleep_dur = vals[4]  # F5
    mood = None          # Not in feature vector; caller can pass separately
    sentiment = vals[8]  # F9
    anxiety = vals[9]    # F10
    fatigue = vals[10]   # F11

    # Priority rules (highest severity first)
    if anxiety == 1.0:
        state = "estres_agudo"
        confidence = 0.65
    elif fatigue == 1.0:
        state = "fatiga_cronica"
        confidence = 0.60
    elif not math.isnan(hrv) and hrv < 20:
        state = "estres_agudo"
        confidence = 0.70
    elif not math.isnan(hrv) and hrv > 75:
        state = "activacion"
        confidence = 0.55
    elif not math.isnan(sleep_dur) and sleep_dur < 5:
        state = "fatiga_cronica"
        confidence = 0.60
    elif not math.isnan(sentiment) and sentiment > 0.5:
        state = "activacion"
        confidence = 0.50
    elif not math.isnan(sentiment) and sentiment < -0.3:
        state = "estres_agudo"
        confidence = 0.55
    else:
        state = "equilibrio"
        confidence = 0.45

    return {
        "state": state,
        "state_code": {v: k for k, v in EMOTIONAL_STATES.items()}[state],
        "confidence": confidence,
        "method": "cold_start_heuristic",
        "description": STATE_DESCRIPTIONS[state],
        "probabilities": _synthetic_probs(state, confidence),
        "degradation_level": features["degradation_level"],
        "features_available": features["n_available"],
    }


def _synthetic_probs(dominant: str, conf: float) -> dict:
    """Generate synthetic probability distribution centered on dominant class."""
    remaining = 1.0 - conf
    per_other = remaining / 4
    return {
        s: round(conf if s == dominant else per_other, 3)
        for s in EMOTIONAL_STATES.values()
    }


# ── XGBoost classifier (Phase B: ≥30 check-ins) ─────────────────────────────

_model = None


def _get_or_train_model(training_data: Optional[list] = None):
    """
    Returns trained XGBoost model. Trains on first call or when
    new data is provided. In demo mode, trains on synthetic data.
    """
    global _model

    if _model is not None and training_data is None:
        return _model

    try:
        import numpy as np
        from xgboost import XGBClassifier
        from sklearn.model_selection import StratifiedKFold, cross_val_score
    except ImportError:
        logger.warning("xgboost/sklearn not installed. Using cold-start only.")
        return None

    # Generate synthetic training data for demo/initial training
    if training_data is None:
        np.random.seed(42)
        n = 200
        X = np.random.randn(n, 13)

        # Make features realistic
        X[:, 0] = np.random.uniform(15, 90, n)   # HRV
        X[:, 3] = np.random.uniform(30, 100, n)   # sleep_score
        X[:, 4] = np.random.uniform(4, 9, n)      # sleep_hours
        X[:, 6] = np.random.uniform(6, 23, n)     # hour
        X[:, 7] = np.random.randint(0, 7, n)      # day_of_week
        X[:, 8] = np.random.uniform(-1, 1, n)     # sentiment
        X[:, 9] = np.random.binomial(1, 0.15, n)  # anxiety
        X[:, 10] = np.random.binomial(1, 0.12, n) # fatigue
        X[:, 12] = np.random.uniform(5, 35, n)    # temp

        # Generate labels based on feature patterns
        y = np.zeros(n, dtype=int)
        for i in range(n):
            if X[i, 0] < 25 or X[i, 9] == 1:       # low HRV or anxiety
                y[i] = 1  # estres_agudo
            elif X[i, 10] == 1 or X[i, 4] < 5:      # fatigue keyword or low sleep
                y[i] = 4  # fatiga_cronica
            elif X[i, 0] > 65 and X[i, 8] > 0.3:    # high HRV + positive
                y[i] = 3  # activacion
            elif X[i, 0] > 50 and X[i, 8] < -0.2:   # recovering from stress
                y[i] = 0  # recuperacion_activa
            else:
                y[i] = 2  # equilibrio

        # Inject NaN randomly (XGBoost handles this natively)
        mask = np.random.random((n, 13)) < 0.1
        X[mask] = float("nan")
    else:
        X = np.array([d["features"] for d in training_data])
        y = np.array([d["label"] for d in training_data])

    # Train XGBoost
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        eval_metric="mlogloss",
        random_state=42,
    )
    model.fit(X, y)

    # Cross-validation score (StratifiedKFold 5-fold)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="f1_weighted")
    logger.info(f"XGBoost CV F1-weighted: {scores.mean():.3f} ± {scores.std():.3f}")

    _model = {
        "classifier": model,
        "f1_score": round(float(scores.mean()), 3),
        "n_samples": len(y),
        "feature_importances": dict(zip(
            ["hrv_last", "hrv_7d_avg", "hrv_delta", "sleep_score", "sleep_dur",
             "activity_cal", "hour", "day", "sentiment", "anxiety", "fatigue",
             "meditation_gap", "outdoor_temp"],
            [round(float(x), 4) for x in model.feature_importances_]
        )),
    }
    return _model


def classify_xgboost(features: dict) -> dict:
    """
    Full XGBoost classification (Phase B).
    Returns predicted state + confidence + probabilities.
    """
    model_data = _get_or_train_model()
    if model_data is None:
        return classify_cold_start(features)

    try:
        import numpy as np
        X = np.array([features["features"]])
        clf = model_data["classifier"]

        pred = int(clf.predict(X)[0])
        probs = clf.predict_proba(X)[0]
        state = EMOTIONAL_STATES[pred]

        return {
            "state": state,
            "state_code": pred,
            "confidence": round(float(probs[pred]), 3),
            "method": "xgboost",
            "description": STATE_DESCRIPTIONS[state],
            "probabilities": {
                EMOTIONAL_STATES[i]: round(float(p), 3)
                for i, p in enumerate(probs)
            },
            "degradation_level": features["degradation_level"],
            "features_available": features["n_available"],
            "model_f1": model_data["f1_score"],
            "feature_importances": model_data["feature_importances"],
        }
    except Exception as e:
        logger.error(f"XGBoost prediction failed: {e}. Falling back to cold-start.")
        return classify_cold_start(features)


# ── Unified classifier (auto-selects phase A or B) ──────────────────────────

def classify_emotional_state(
    checkin_data: dict,
    checkin_history: Optional[list] = None,
    clima: Optional[dict] = None,
    hora: Optional[int] = None,
    force_method: Optional[str] = None,
) -> dict:
    """
    Main entry point. Automatically selects:
      - cold_start (heuristic) if <30 check-ins
      - xgboost if ≥30 check-ins

    Args:
        force_method: "cold_start" or "xgboost" to override auto-selection
    """
    features = extract_features(checkin_data, checkin_history, clima, hora)
    n_history = len(checkin_history) if checkin_history else 0

    if force_method == "cold_start" or (force_method is None and n_history < 30):
        result = classify_cold_start(features)
        result["reason"] = f"Cold-start mode ({n_history} check-ins, need ≥30 for ML)"
    else:
        result = classify_xgboost(features)
        result["reason"] = f"XGBoost trained on {n_history} check-ins"

    result["n_checkins_available"] = n_history
    result["threshold_for_ml"] = 30
    return result
