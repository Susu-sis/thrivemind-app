"""
services/correlation_service.py — Motor de Correlación Cross-Pilar de ThriveMind.

Analiza los check-ins históricos y calcula correlaciones estadísticas entre
las variables de bienestar usando el coeficiente de Pearson.
"""

from app.core.database import get_supabase_client

P_VALUE_THRESHOLD = 0.05
MIN_CHECKINS_PARA_CORRELACION = 7

NOMBRES_VARIABLES = {
    "estado_emocional": "tu estado emocional",
    "energia_fisica": "tu energía física",
    "horas_sueno": "tus horas de sueño",
    "conexion_entorno": "tu conexión con el entorno",
}

PARES_ANALISIS = [
    ("horas_sueno", "energia_fisica"),
    ("horas_sueno", "estado_emocional"),
    ("estado_emocional", "energia_fisica"),
    ("conexion_entorno", "estado_emocional"),
    ("conexion_entorno", "energia_fisica"),
    ("horas_sueno", "conexion_entorno"),
]


def interpretar_correlacion(r: float) -> dict:
    abs_r = abs(r)
    if abs_r >= 0.7:
        fuerza = "fuerte"
        emoji = "🔴" if r < 0 else "🟢"
    elif abs_r >= 0.4:
        fuerza = "moderada"
        emoji = "🟡"
    elif abs_r >= 0.1:
        fuerza = "débil"
        emoji = "⚪"
    else:
        fuerza = "sin correlación"
        emoji = "⚫"
    direccion = "positiva" if r >= 0 else "negativa"
    return {"fuerza": fuerza, "direccion": direccion, "emoji": emoji}


def generar_insight_texto(var_x: str, var_y: str, r: float) -> str:
    nombre_x = NOMBRES_VARIABLES.get(var_x, var_x)
    nombre_y = NOMBRES_VARIABLES.get(var_y, var_y)
    interpretacion = interpretar_correlacion(r)
    r_redondeado = round(r, 2)

    primera_frase = (
        f"{nombre_x.capitalize()} tiene una correlación "
        f"{interpretacion['fuerza']} {interpretacion['direccion']} "
        f"(r={r_redondeado}) con {nombre_y}."
    )

    if r >= 0.4:
        segunda_frase = f"Cuando {nombre_x} sube, {nombre_y} también tiende a subir."
    elif r <= -0.4:
        segunda_frase = f"Cuando {nombre_x} sube, {nombre_y} tiende a bajar."
    else:
        segunda_frase = "No hay una relación clara entre estas dos variables en tus datos."

    return f"{primera_frase} {segunda_frase}"


def calcular_correlaciones_usuario(user_id: str, dias: int = 30) -> dict:
    import numpy as np
    from scipy import stats
    supabase = get_supabase_client()

    response = supabase.table("checkins") \
        .select("estado_emocional, energia_fisica, horas_sueno, conexion_entorno, created_at") \
        .eq("user_id", user_id) \
        .order("created_at", desc=False) \
        .limit(dias) \
        .execute()

    checkins = response.data if response.data else []
    n = len(checkins)

    if n < MIN_CHECKINS_PARA_CORRELACION:
        return {
            "correlaciones": [],
            "resumen": (
                f"Necesitas al menos {MIN_CHECKINS_PARA_CORRELACION} check-ins para "
                f"descubrir tus patrones. Llevas {n} — ¡sigue así!"
            ),
            "n_checkins": n,
            "suficientes_datos": False,
        }

    variables = {}
    for key in ("estado_emocional", "energia_fisica", "horas_sueno", "conexion_entorno"):
        variables[key] = np.array(
            [float(c[key]) if c.get(key) is not None else np.nan for c in checkins],
            dtype=float,
        )

    correlaciones_significativas = []

    for var_x, var_y in PARES_ANALISIS:
        x = variables[var_x]
        y = variables[var_y]

        mascara_valida = ~(np.isnan(x) | np.isnan(y))
        x_limpio = x[mascara_valida]
        y_limpio = y[mascara_valida]

        if len(x_limpio) < 5:
            continue

        r, p_value = stats.pearsonr(x_limpio, y_limpio)

        if p_value >= P_VALUE_THRESHOLD:
            continue
        if abs(r) < 0.1:
            continue

        interpretacion = interpretar_correlacion(r)
        insight = generar_insight_texto(var_x, var_y, r)

        correlaciones_significativas.append({
            "variable_x": var_x,
            "variable_y": var_y,
            "r": round(r, 3),
            "p_value": round(p_value, 4),
            "fuerza": interpretacion["fuerza"],
            "direccion": interpretacion["direccion"],
            "emoji": interpretacion["emoji"],
            "insight": insight,
        })

    correlaciones_significativas.sort(key=lambda c: abs(c["r"]), reverse=True)

    if not correlaciones_significativas:
        resumen = (
            f"Con {n} check-ins analizados, no se encontraron correlaciones "
            f"significativas todavía. Sigue haciendo check-ins."
        )
    else:
        top = correlaciones_significativas[0]
        resumen = (
            f"Analizando tus {n} check-ins, encontré {len(correlaciones_significativas)} "
            f"correlación(es) significativa(s). La más fuerte: {top['insight']}"
        )

    return {
        "correlaciones": correlaciones_significativas,
        "resumen": resumen,
        "n_checkins": n,
        "suficientes_datos": True,
    }


# ── Lag Analysis ──────────────────────────────────────────────────────────────

def calcular_correlaciones_con_lag(user_id: str, dias: int = 30, max_lag: int = 3) -> dict:
    """
    Calcula correlaciones incluyendo efectos retrasados (lag 0-3 días).
    Detecta patrones como 'meditación hoy → mejor sueño mañana'.
    """
    import numpy as np
    from scipy import stats
    supabase = get_supabase_client()
    response = (
        supabase.table("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, conexion_entorno, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .limit(dias)
        .execute()
    )
    checkins = response.data or []
    n = len(checkins)

    if n < 7:
        return {"error": "Datos insuficientes", "n_checkins": n}

    fields = ["estado_emocional", "energia_fisica", "horas_sueno", "conexion_entorno"]
    arrays = {}
    for f in fields:
        arrays[f] = np.array([float(c[f]) if c.get(f) is not None else np.nan for c in checkins], dtype=float)

    correlations: dict = {}

    # Lag 0 (same day)
    lag0 = {}
    for i, v1 in enumerate(fields):
        for v2 in fields[i + 1:]:
            mask = ~(np.isnan(arrays[v1]) | np.isnan(arrays[v2]))
            if mask.sum() >= 5:
                r, p = stats.pearsonr(arrays[v1][mask], arrays[v2][mask])
                lag0[f"{v1}_vs_{v2}"] = {"r": round(float(r), 3), "p": round(float(p), 4), "significant": bool(p < 0.05)}
    correlations["lag_0"] = lag0

    # Lagged correlations
    for lag in range(1, max_lag + 1):
        lag_dict = {}
        for v1 in fields:
            for v2 in fields:
                if v1 == v2:
                    continue
                a = arrays[v1][:-lag]
                b = arrays[v2][lag:]
                mask = ~(np.isnan(a) | np.isnan(b))
                if mask.sum() >= 5:
                    r, p = stats.pearsonr(a[mask], b[mask])
                    key = f"{v1}_predice_{v2}_en_{lag}d"
                    lag_dict[key] = {
                        "r": round(float(r), 3),
                        "p": round(float(p), 4),
                        "significant": bool(p < 0.05),
                        "interpretation": f"{NOMBRES_VARIABLES.get(v1, v1)} hoy predice {NOMBRES_VARIABLES.get(v2, v2)} en {lag} día(s)",
                    }
        correlations[f"lag_{lag}"] = lag_dict

    # Find best lag per pair
    best_lags = {}
    for v1 in fields:
        for v2 in fields:
            if v1 == v2:
                continue
            best_r, best_lag_n = 0.0, 0
            for lag_key, lag_data in correlations.items():
                for ckey, cval in lag_data.items():
                    if (f"{v1}_predice_{v2}" in ckey or f"{v1}_vs_{v2}" in ckey) and cval.get("significant"):
                        if abs(cval["r"]) > abs(best_r):
                            best_r = cval["r"]
                            best_lag_n = int(lag_key.split("_")[1])
            if abs(best_r) >= 0.2:
                timing = "hoy mismo" if best_lag_n == 0 else f"en {best_lag_n} día(s)"
                fuerza = "fuerte" if abs(best_r) > 0.6 else "moderada" if abs(best_r) > 0.3 else "débil"
                n1 = NOMBRES_VARIABLES.get(v1, v1)
                n2 = NOMBRES_VARIABLES.get(v2, v2)
                best_lags[f"{v1}_→_{v2}"] = {
                    "lag_days": best_lag_n,
                    "r": float(best_r),
                    "interpretation": f"Cuando {n1} mejora, {n2} mejora {timing} (correlación {fuerza}: r={best_r})",
                }

    return {
        "correlations": correlations,
        "best_lags": best_lags,
        "n_checkins": n,
    }
