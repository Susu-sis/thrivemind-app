from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.models.checkin import CheckinCreate
from app.services.checkin_service import guardar_checkin
from app.services.correlation_service import calcular_correlaciones_usuario, calcular_correlaciones_con_lag

router = APIRouter()


@router.post("/", response_model=dict, summary="Crear check-in diario")
async def crear_checkin(
    checkin_data: CheckinCreate,
    current_user=Depends(get_current_user),
):
    datos = checkin_data.model_dump()
    datos["user_id"] = current_user["id"]
    resultado = guardar_checkin(datos)
    if resultado:
        return {"success": True, "checkin": resultado}
    return {"success": False, "error": "Error al guardar el check-in"}


@router.get("/dashboard/tendencias", response_model=dict)
async def obtener_tendencias_dashboard(
    dias: int = Query(default=14, ge=7, le=90),
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    fecha_inicio = (datetime.utcnow() - timedelta(days=dias)).isoformat()

    response = (
        supabase.table("checkins")
        .select(
            "estado_emocional, energia_fisica, horas_sueno, conexion_entorno, "
            "emocion_principal, tipo_checkin, created_at"
        )
        .eq("user_id", current_user["id"])
        .eq("tipo_checkin", "diario")
        .gte("created_at", fecha_inicio)
        .order("created_at", desc=False)
        .execute()
    )

    checkins = response.data or []

    if not checkins:
        return {
            "serie_temporal": [],
            "promedios_pilares": [],
            "correlacion_sueno_emocional": [],
            "estadisticas": {},
            "mensaje": "Aún no hay datos. Completa al menos 3 check-ins diarios para ver tendencias.",
        }

    # Serie temporal
    serie_temporal = []
    for c in checkins:
        fecha = c["created_at"][:10]
        serie_temporal.append({
            "fecha": fecha,
            "fecha_corta": fecha[5:],
            "estado_emocional": c["estado_emocional"],
            "energia_fisica": c.get("energia_fisica"),
            "horas_sueno": c.get("horas_sueno"),
            "conexion_entorno": c.get("conexion_entorno"),
            "emocion_principal": c.get("emocion_principal", ""),
        })

    # Promedios por pilar
    def promedio(campo: str) -> float:
        valores = [c[campo] for c in checkins if c.get(campo) is not None]
        return round(sum(valores) / len(valores), 1) if valores else 0.0

    promedios_pilares = [
        {"pilar": "Mente", "valor": promedio("estado_emocional"), "fullMark": 10},
        {"pilar": "Cuerpo", "valor": promedio("energia_fisica"), "fullMark": 10},
        {"pilar": "Entorno", "valor": promedio("conexion_entorno"), "fullMark": 10},
        {"pilar": "Sueño", "valor": min(round(promedio("horas_sueno") * 10 / 8, 1), 10), "fullMark": 10},
    ]

    # Pares para ScatterChart
    correlacion = [
        {
            "sueno": c["horas_sueno"],
            "estado_emocional": c["estado_emocional"],
            "fecha": c["created_at"][:10],
        }
        for c in checkins
        if c.get("horas_sueno") is not None and c.get("estado_emocional") is not None
    ]

    # Estadísticas
    estados = [c["estado_emocional"] for c in checkins]
    mejor_dia = max(checkins, key=lambda c: c["estado_emocional"])
    peor_dia = min(checkins, key=lambda c: c["estado_emocional"])

    mitad = len(estados) // 2
    if mitad > 0:
        prom_primera = sum(estados[:mitad]) / mitad
        prom_segunda = sum(estados[mitad:]) / (len(estados) - mitad)
        tendencia = round(prom_segunda - prom_primera, 1)
        tendencia_texto = (
            f"↑ Mejorando {tendencia} puntos" if tendencia > 0.3
            else f"↓ Bajando {abs(tendencia)} puntos" if tendencia < -0.3
            else "→ Estable"
        )
    else:
        tendencia = 0
        tendencia_texto = "Datos insuficientes"

    # Pearson sueño-emocional
    correlacion_pearson = None
    correlacion_texto = "Necesitas al menos 3 check-ins"
    if len(correlacion) >= 3:
        n = len(correlacion)
        xs = [p["sueno"] for p in correlacion]
        ys = [p["estado_emocional"] for p in correlacion]
        media_x = sum(xs) / n
        media_y = sum(ys) / n
        numerador = sum((xs[i] - media_x) * (ys[i] - media_y) for i in range(n))
        denom_x = (sum((x - media_x) ** 2 for x in xs)) ** 0.5
        denom_y = (sum((y - media_y) ** 2 for y in ys)) ** 0.5
        if denom_x * denom_y > 0:
            correlacion_pearson = round(numerador / (denom_x * denom_y), 2)
        correlacion_texto = (
            "Correlación fuerte: dormir más mejora tu bienestar emocional"
            if correlacion_pearson and correlacion_pearson > 0.5
            else "Correlación moderada: el sueño influye en tu bienestar"
            if correlacion_pearson and correlacion_pearson > 0.2
            else "Correlación débil: otros factores dominan tu estado emocional"
            if correlacion_pearson and correlacion_pearson >= 0
            else "Correlación inversa — patrón inusual"
        )

    estadisticas = {
        "total_checkins": len(checkins),
        "promedio_emocional": promedio("estado_emocional"),
        "promedio_energia": promedio("energia_fisica"),
        "promedio_sueno": promedio("horas_sueno"),
        "mejor_dia": {"fecha": mejor_dia["created_at"][:10], "valor": mejor_dia["estado_emocional"]},
        "peor_dia": {"fecha": peor_dia["created_at"][:10], "valor": peor_dia["estado_emocional"]},
        "tendencia": tendencia,
        "tendencia_texto": tendencia_texto,
        "correlacion_sueno_emocional": correlacion_pearson,
        "correlacion_texto": correlacion_texto,
    }

    return {
        "serie_temporal": serie_temporal,
        "promedios_pilares": promedios_pilares,
        "correlacion_sueno_emocional": correlacion,
        "estadisticas": estadisticas,
    }


@router.get("/correlaciones", summary="Correlaciones cross-pilar del usuario")
async def get_correlaciones(
    dias: int = 30,
    current_user: dict = Depends(get_current_user),
):
    dias_limitados = min(dias, 90)
    return calcular_correlaciones_usuario(
        user_id=current_user["id"],
        dias=dias_limitados,
    )


@router.get("/correlaciones/lag", summary="Correlaciones con efecto retrasado")
async def get_correlaciones_lag(
    dias: int = 30,
    max_lag: int = 3,
    current_user: dict = Depends(get_current_user),
):
    return calcular_correlaciones_con_lag(
        user_id=current_user["id"],
        dias=min(dias, 90),
        max_lag=min(max_lag, 5),
    )


@router.post("/contextual", response_model=dict)
async def crear_checkin_contextual(
    tipo_checkin: str,
    estado_emocional: int,
    energia_fisica: int = None,
    emocion_principal: str = None,
    nota: str = None,
    hambre: int = None,
    saciedad: int = None,
    referencia_id: str = None,
    current_user: dict = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    data = {
        "user_id": current_user["id"],
        "tipo_checkin": tipo_checkin,
        "estado_emocional": estado_emocional,
        "energia_fisica": energia_fisica,
        "emocion_principal": emocion_principal,
        "nota": nota,
        "hambre": hambre,
        "saciedad": saciedad,
        "referencia_id": referencia_id,
    }
    data = {k: v for k, v in data.items() if v is not None}

    response = supabase.table("checkins").insert(data).execute()
    resultado = {"checkin": response.data[0] if response.data else {}}

    if tipo_checkin in ("post_meditacion", "post_comida") and referencia_id:
        tipo_pre = tipo_checkin.replace("post_", "pre_")
        pre_response = (
            supabase.table("checkins")
            .select("estado_emocional, energia_fisica")
            .eq("referencia_id", referencia_id)
            .eq("tipo_checkin", tipo_pre)
            .eq("user_id", current_user["id"])
            .execute()
        )
        if pre_response.data:
            pre = pre_response.data[0]
            estado_pre = pre["estado_emocional"]
            delta = estado_emocional - estado_pre

            delta_energia = None
            if energia_fisica is not None and pre.get("energia_fisica") is not None:
                delta_energia = energia_fisica - pre["energia_fisica"]

            evento_nombres = {
                "post_meditacion": "Meditación",
                "post_comida": "Comida",
                "post_cosecha": "Cosecha",
                "post_respiracion": "Respiración",
            }
            nombre_evento = evento_nombres.get(tipo_checkin, tipo_checkin.replace("post_", ""))

            if delta > 0:
                mensaje = f"🎉 ¡Excelente! Tu estado mejoró {delta} puntos después de {nombre_evento}."
                emoji = "📈"
            elif delta == 0:
                mensaje = f"➡️ Tu estado se mantuvo estable después de {nombre_evento}."
                emoji = "➡️"
            else:
                mensaje = f"🔄 Registramos un descenso de {abs(delta)} puntos — es normal después de introspección profunda."
                emoji = "📉"

            resultado["delta_emocional"] = delta
            resultado["delta_energia"] = delta_energia
            resultado["mensaje_impacto"] = mensaje
            resultado["emoji"] = emoji
            resultado["nombre_evento"] = nombre_evento

    return resultado
