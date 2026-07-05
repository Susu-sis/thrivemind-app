"""
Script de datos de prueba para el Dashboard del TFM.

Ejecutar una sola vez después de crear las tablas en Supabase:
  cd backend
  python scripts/seed_dashboard_demo.py

IMPORTANTE: Cambia DEMO_USER_ID por el UUID de tu usuario de prueba.
"""
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import asyncio
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("supabase_url"),
    os.getenv("supabase_service_key"),  # Service role para saltarse RLS
)

# ⚠️ CAMBIA ESTO por el UUID de tu usuario de prueba (Supabase → Authentication → Users)
DEMO_USER_ID = "8628d3c4-64ce-40eb-8069-37c410970cb0"

# Curva de 14 días: semana de estrés → mejora con ThriveMind
DATOS_DEMO = [
    (3, 4, 5.0, 3, "ansiedad"),
    (4, 3, 4.5, 3, "estrés"),
    (3, 4, 5.5, 4, "agobio"),
    (4, 5, 6.0, 4, "cansancio"),
    (5, 5, 6.5, 5, "neutral"),
    (6, 6, 7.0, 6, "calma"),
    (6, 6, 7.5, 6, "calma"),
    (7, 7, 7.5, 7, "gratitud"),
    (7, 7, 8.0, 7, "energía"),
    (8, 8, 8.0, 8, "bienestar"),
    (7, 7, 7.5, 7, "calma"),
    (8, 8, 8.5, 8, "gratitud"),
    (9, 8, 8.0, 9, "alegría"),
    (8, 9, 8.5, 8, "bienestar"),
]


async def seed():
    print(f"\n🌱 Generando 14 días de datos de demo para el usuario {DEMO_USER_ID[:8]}...\n")
    hoy = datetime.utcnow()

    for i, (emocional, energia, sueno, entorno, emocion) in enumerate(DATOS_DEMO):
        fecha = hoy - timedelta(days=13 - i)
        supabase.table("checkins").insert({
            "user_id": DEMO_USER_ID,
            "estado_emocional": emocional,
            "energia_fisica": energia,
            "horas_sueno": sueno,
            "conexion_entorno": entorno,
            "emocion_principal": emocion,
            "tipo_checkin": "diario",
            "created_at": fecha.isoformat(),
        }).execute()

        barra = "█" * emocional + "░" * (10 - emocional)
        print(f"  Día {i+1:2d} ({fecha.strftime('%d/%m')}): [{barra}] {emocional}/10 — {emocion}")

    print(f"\n✅ 14 check-ins generados correctamente.")


asyncio.run(seed())
