"""Test all gap endpoints in demo mode."""
import urllib.request
import json
import sys

BASE = "http://127.0.0.1:8001/api/v1"
results = []

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

def test(label, status, body, expected_status=200):
    ok = status == expected_status
    results.append((label, ok, status))
    tag = "OK" if ok else "FAIL"
    detail = ""
    if isinstance(body, dict):
        detail = str(body)[:120]
    elif isinstance(body, list):
        detail = f"{len(body)} items"
    else:
        detail = str(body)[:120]
    print(f"  [{tag}] {status} {label} -> {detail}")
    return ok

# Auth
status, body = api("POST", "/auth/login", data={"email": "demo@thrivemind.app", "password": "demo123"})
if status != 200:
    print(f"AUTH FAIL: {status} {body}")
    sys.exit(1)
token = body["access_token"]
auth = {"Authorization": f"Bearer {token}"}
print("[OK] AUTH login -> token obtained\n")

# ---- GAP 10: XGBoost Classifier ----
print("--- GAP 10: XGBoost Emotional Classifier ---")
s, b = api("GET", "/insights/classify", auth)
test("GET /insights/classify", s, b)
if isinstance(b, dict):
    print(f"       state={b.get('state','?')}, method={b.get('method','?')}, confidence={b.get('confidence','?')}")
    print(f"       degradation={b.get('degradation_level','?')}, features={b.get('features_available','?')}")

# ---- GAP 7: Intervention Logging ----
print("\n--- GAP 7: Intervention Logging (MLOps) ---")
s, b = api("GET", "/insights/interventions", auth)
test("GET /insights/interventions", s, b)

s, b = api("GET", "/insights/interventions/acceptance-rate", auth)
test("GET /insights/acceptance-rate", s, b)

# Feedback uses score as query param
s, b = api("POST", "/insights/interventions/test-id-1/feedback?score=4", auth)
test("POST /insights/.../feedback", s, b)

# ---- GAP 9: Override Co-pilot ----
print("\n--- GAP 9: Override Co-pilot Protocol ---")
s, b = api("POST", "/insights/override/detect", auth, data={
    "ai_recommendation": {"tipo": "meditacion_nocturna", "intensidad": "suave"},
    "user_action": {"tipo": "ejercicio_intenso", "intensidad": "alta"}
})
test("POST /insights/override/detect", s, b)

s, b = api("POST", "/insights/override/register", auth, data={
    "override_data": {
        "ai_recommendation": {"tipo": "relajacion"},
        "user_action": {"tipo": "cafeina"},
        "context": {"hora": 22}
    }
})
test("POST /insights/override/register", s, b)

s, b = api("GET", "/insights/override/resilience-counter", auth)
test("GET /insights/resilience-counter", s, b)
if isinstance(b, dict):
    print(f"       CR={b.get('resilience_counter','?')}, level={b.get('level','?')}")

# ---- Original endpoints (verify still working) ----
print("\n--- Original 6 insight endpoints ---")
for path in ["/insights/holistic", "/insights/recommendations", "/insights/convergence",
             "/insights/matrix", "/insights/sentiment", "/insights/context-history"]:
    s, b = api("GET", path, auth)
    test(f"GET {path}", s, b)

print("\n--- Core endpoints ---")
for path in ["/checkin/dashboard/tendencias", "/gamification/", "/meal-planner/weekly",
             "/preferences/", "/entorno/clima", "/ambient/status"]:
    s, b = api("GET", path, auth)
    test(f"GET {path}", s, b)

print("\n--- POST endpoints ---")
s, b = api("POST", "/checkin/", auth, data={
    "estado_emocional": 7, "energia_fisica": 6, "horas_sueno": 7.5,
    "emocion_principal": "calma", "nota": "Test gap demo"
})
test("POST /checkin/", s, b)

s, b = api("POST", "/mente/generar", auth, data={
    "intencion": "relajacion", "duracion_min": 10, "objetivo": "reducir_estres"
})
test("POST /mente/generar", s, b)

s, b = api("POST", "/cuerpo/nutricion/recomendacion", auth, data={
    "estado_emocional": "ansioso", "hora_del_dia": "noche"
})
test("POST /cuerpo/nutricion/recomendacion", s, b)

# Summary
print("\n" + "="*60)
ok_count = sum(1 for _, ok, _ in results if ok)
fail_count = len(results) - ok_count
print(f"TOTAL: {ok_count}/{len(results)} passed, {fail_count} failed")
if fail_count > 0:
    print("\nFailed endpoints:")
    for label, ok, status in results:
        if not ok:
            print(f"  [{status}] {label}")
print("="*60)
