# Philips Hue Local Control — ThriveMind

Bridge IP: `192.168.2.8`  
App key stored in: `backend/.env` → `hueappkey`

---

## Step 1 — Start the backend (python terminal)

```powershell
cd c:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
python -m uvicorn app.main:app --reload --port 8000
```

Wait for:
```
🌱 ThriveMind API arrancando en modo production
INFO:     Application startup complete.
```

Leave this terminal running.

---

## Step 2 — Login and get token (second terminal)

```powershell
$body = '{"email":"demo@thrivemind.app","password":"demo123"}'
$login = Invoke-RestMethod "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"
$token = $login.access_token
```

Run this again any time you get `"No se pudo validar las credenciales"` — the token expires.

---

## Step 3 — Verify bridge is connected

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/status" -Headers @{Authorization="Bearer $token"}
```

Expected output:
```
connected : True
mode      : live
bridge_ip : 192.168.2.8
lights    : {Hue Essential lamp living room}
```

---

## Step 4 — Apply lighting profiles

### Meditation — warm dim (2200K)
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/meditacion_calma" -Method Post -Headers @{Authorization="Bearer $token"}
```

### Focus — neutral medium (4000K)
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/meditacion_enfoque" -Method Post -Headers @{Authorization="Bearer $token"}
```

### Morning energy — cold bright (6500K)
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/meditacion_energia" -Method Post -Headers @{Authorization="Bearer $token"}
```

### Sleep prep — minimal ultra-warm (2000K)
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/descanso_nocturno" -Method Post -Headers @{Authorization="Bearer $token"}
```

### Nature green (color)
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/naturaleza_verde" -Method Post -Headers @{Authorization="Bearer $token"}
```

### Turn off
```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/apply/apagado" -Method Post -Headers @{Authorization="Bearer $token"}
```

---

## All available profiles

| Profile name        | Color Temp | Effect                        |
|---------------------|-----------|-------------------------------|
| `meditacion_calma`  | 2200K     | Warm dim — deep meditation    |
| `meditacion_enfoque`| 4000K     | Neutral medium — focus        |
| `meditacion_energia`| 6500K     | Cold bright — morning energy  |
| `descanso_nocturno` | 2000K     | Minimal warm — sleep prep     |
| `naturaleza_verde`  | Green     | Color — nature / calm         |
| `apagado`           | —         | Lights off                    |

---

## Auto mode (state-based selection)

Automatically picks the best profile based on mood, energy and time of day:

```powershell
$body = '{"mood_score":4,"energy_score":3,"objetivo":"calma"}'
Invoke-RestMethod "http://localhost:8000/api/v1/ambient/auto" -Method Post -Body $body -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
```
