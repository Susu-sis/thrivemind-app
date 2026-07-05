"""
Capture all API endpoint responses for thesis evidence.
Saves JSON results to docs/resultados/api_evidence/
"""
import urllib.request
import json
import os
import sys
from datetime import datetime

BASE = "http://127.0.0.1:8000/api/v1"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs", "resultados", "api_evidence")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def api(method, path, headers=None, data=None):
    url = BASE + path
    if data:
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        body = json.loads(resp.read())
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body

def save(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"  Saved: {filename}")

# Auth
s, body = api("POST", "/auth/login", data={"email": "demo@thrivemind.app", "password": "demo123"})
token = body["access_token"]
auth = {"Authorization": f"Bearer {token}"}
save("00_auth_login.json", {"status": s, "response": {k: v for k, v in body.items() if k != "access_token"}})

print("\n=== CAPTURING ALL ENDPOINT EVIDENCE ===\n")
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"Mode: demo (ENVIRONMENT=demo)")
print(f"Base URL: {BASE}\n")

# === GAP 10: XGBoost Classifier ===
print("--- GAP 10: XGBoost / Cold-Start Classifier ---")
s, b = api("GET", "/insights/classify", auth)
save("gap10_classify.json", {"status": s, "endpoint": "GET /insights/classify", "response": b})

# === GAP 7: Intervention Logging ===
print("--- GAP 7: Intervention Logging (MLOps) ---")
s, b = api("GET", "/insights/interventions", auth)
save("gap07_interventions_history.json", {"status": s, "endpoint": "GET /insights/interventions", "response": b})

s, b = api("GET", "/insights/interventions/acceptance-rate", auth)
save("gap07_acceptance_rate.json", {"status": s, "endpoint": "GET /insights/interventions/acceptance-rate", "response": b})

s, b = api("POST", "/insights/interventions/test-1/feedback?score=4", auth)
save("gap07_feedback.json", {"status": s, "endpoint": "POST /insights/interventions/{id}/feedback?score=4", "response": b})

# === GAP 9: Override Co-pilot ===
print("--- GAP 9: Override Co-pilot Protocol ---")
s, b = api("POST", "/insights/override/detect", auth, data={
    "ai_recommendation": {"tipo": "meditacion_nocturna", "intensidad": "suave"},
    "user_action": {"tipo": "ejercicio_intenso", "intensidad": "alta"}
})
save("gap09_override_detect.json", {"status": s, "endpoint": "POST /insights/override/detect", "request_body": {
    "ai_recommendation": {"tipo": "meditacion_nocturna", "intensidad": "suave"},
    "user_action": {"tipo": "ejercicio_intenso", "intensidad": "alta"}
}, "response": b})

s, b = api("POST", "/insights/override/register", auth, data={
    "override_data": {
        "ai_recommendation": {"tipo": "relajacion"},
        "user_action": {"tipo": "cafeina"},
        "context": {"hora": 22}
    }
})
save("gap09_override_register.json", {"status": s, "endpoint": "POST /insights/override/register", "response": b})

s, b = api("GET", "/insights/override/resilience-counter", auth)
save("gap09_resilience_counter.json", {"status": s, "endpoint": "GET /insights/override/resilience-counter", "response": b})

# === Core insight endpoints ===
print("--- Core Insight Endpoints ---")
s, b = api("GET", "/insights/holistic", auth)
save("core_holistic.json", {"status": s, "endpoint": "GET /insights/holistic", "response": b})

s, b = api("GET", "/insights/recommendations", auth)
save("core_recommendations.json", {"status": s, "endpoint": "GET /insights/recommendations", "response": b})

s, b = api("GET", "/insights/convergence", auth)
save("core_convergence.json", {"status": s, "endpoint": "GET /insights/convergence", "response": b})

s, b = api("GET", "/insights/matrix", auth)
save("core_matrix.json", {"status": s, "endpoint": "GET /insights/matrix", "response": b})

s, b = api("GET", "/insights/sentiment", auth)
save("core_sentiment.json", {"status": s, "endpoint": "GET /insights/sentiment", "response": b})

s, b = api("GET", "/insights/context-history", auth)
save("core_context_history.json", {"status": s, "endpoint": "GET /insights/context-history", "response": b})

# === Pillar: Mente ===
print("--- Pilar Mente ---")
s, b = api("POST", "/mente/generar", auth, data={
    "intencion": "relajacion", "duracion_min": 10, "objetivo": "reducir_estres"
})
save("mente_meditacion.json", {"status": s, "endpoint": "POST /mente/generar", "response": b})

# === Pillar: Cuerpo ===
print("--- Pilar Cuerpo ---")
s, b = api("POST", "/cuerpo/nutricion/recomendacion", auth, data={
    "estado_emocional": "ansioso", "hora_del_dia": "noche"
})
save("cuerpo_recomendacion.json", {"status": s, "endpoint": "POST /cuerpo/nutricion/recomendacion", "response": b})

s, b = api("GET", "/meal-planner/weekly", auth)
save("cuerpo_meal_plan.json", {"status": s, "endpoint": "GET /meal-planner/weekly", "response": b})

# === Pillar: Entorno ===
print("--- Pilar Entorno ---")
s, b = api("GET", "/entorno/planta-recomendada?estado_emocional=ansioso", auth)
save("entorno_planta.json", {"status": s, "endpoint": "GET /entorno/planta-recomendada", "response": b})

s, b = api("GET", "/entorno/cultivos", auth)
save("entorno_cultivos.json", {"status": s, "endpoint": "GET /entorno/cultivos", "response": b})

s, b = api("GET", "/entorno/clima", auth)
save("entorno_clima.json", {"status": s, "endpoint": "GET /entorno/clima", "response": b})

# === Check-in ===
print("--- Check-in ---")
s, b = api("GET", "/checkin/dashboard/tendencias", auth)
save("checkin_tendencias.json", {"status": s, "endpoint": "GET /checkin/dashboard/tendencias", "response": b})

s, b = api("GET", "/checkin/correlaciones", auth)
save("checkin_correlaciones.json", {"status": s, "endpoint": "GET /checkin/correlaciones", "response": b})

# === IoT ===
print("--- IoT Ambient ---")
s, b = api("GET", "/ambient/status", auth)
save("iot_status.json", {"status": s, "endpoint": "GET /ambient/status", "response": b})

s, b = api("GET", "/ambient/profiles", auth)
save("iot_profiles.json", {"status": s, "endpoint": "GET /ambient/profiles", "response": b})

# === Gamification ===
print("--- Gamification ---")
s, b = api("GET", "/gamification/", auth)
save("gamification.json", {"status": s, "endpoint": "GET /gamification/", "response": b})

# === Preferences ===
print("--- Preferences ---")
s, b = api("GET", "/preferences/", auth)
save("preferences.json", {"status": s, "endpoint": "GET /preferences/", "response": b})

# === Search ===
print("--- Search ---")
s, b = api("GET", "/search/global?q=meditacion", auth)
save("search_global.json", {"status": s, "endpoint": "GET /search/global?q=meditacion", "response": b})

print(f"\n=== EVIDENCE CAPTURE COMPLETE ===")
print(f"Files saved to: {OUTPUT_DIR}")
print(f"Total evidence files: {len(os.listdir(OUTPUT_DIR))}")
