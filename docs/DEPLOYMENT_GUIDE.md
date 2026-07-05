# 🚀 ThriveMind — Guía de Despliegue Paso a Paso

> Esta guía te lleva desde demo local hasta producción online.
> Sigue las fases en orden.

---

## Fase 0: Lo que ya tienes funcionando (modo demo local)

- ✅ Backend en `http://localhost:8000` (FastAPI + datos demo en memoria)
- ✅ Frontend en `http://localhost:3000` (Next.js)
- ✅ Todas las funcionalidades visibles con datos simulados
- ✅ No necesitas API keys ni base de datos para explorar

---

## Fase 1: Configurar Supabase (Base de Datos)

### Paso 1.1 — Crear proyecto en Supabase
1. Ve a [https://supabase.com](https://supabase.com) y regístrate/inicia sesión
2. Click **"New Project"**
3. Elige un nombre: `thrivemind`
4. Elige una contraseña para la base de datos (guárdala)
5. Selecciona la región más cercana a ti
6. Click **"Create new project"** y espera ~2 minutos

### Paso 1.2 — Obtener las credenciales
1. En tu proyecto, ve a **Settings → API** (en el menú lateral izquierdo)
2. Copia estos 3 valores (los necesitarás luego):
   - **Project URL** → es tu `SUPABASE_URL` (ej: `https://xyz.supabase.co`)
   - **anon public key** → es tu `SUPABASE_KEY`
   - **service_role secret** → es tu `SUPABASE_SERVICE_KEY` ⚠️ nunca expongas esta

### Paso 1.3 — Crear las tablas base
1. En Supabase, ve a **SQL Editor** (icono en el menú lateral)
2. Click **"New Query"**
3. Abre el archivo `docs/sql/schema.sql` de tu proyecto
4. Copia **TODO** el contenido y pégalo en el SQL Editor
5. Click **"Run"** (botón verde arriba a la derecha)
6. Deberías ver: ✅ Success. No rows returned
7. Ve a **Table Editor** y verifica que existen las tablas:
   - `profiles`, `checkins`, `user_preferences`, `meditation_sessions`,
   - `nutrition_analyses`, `cultivos_activos`, `farming_chat_messages`, `papers`

### Paso 1.4 — Crear las tablas de las mejoras
1. Todavía en **SQL Editor**, click **"New Query"** de nuevo
2. Abre `docs/SUPABASE_SETUP.md` y copia **TODO** el SQL de las secciones 1-7
   (empieza en `ALTER TABLE cultivos_activos` y termina en las políticas RLS)
3. Pégalo y click **"Run"**
4. Verifica en **Table Editor** que ahora también existen:
   - `gamification_history`, `user_milestones`, `hue_profiles`,
   - `meal_plans`, `notifications`

### Paso 1.5 — Verificar RLS
1. Ve a **Authentication → Policies** en el menú lateral
2. Cada tabla debería tener un candado verde (RLS habilitado)
3. Cada tabla debería tener al menos 1 política visible

---

## Fase 2: Configurar API Keys Externas

### Paso 2.1 — OpenAI (para meditaciones IA y nutrición)
1. Ve a [https://platform.openai.com](https://platform.openai.com)
2. Crea una cuenta / inicia sesión
3. Ve a **API Keys** → **Create new secret key**
4. Copia la key (empieza con `sk-...`)
5. Necesitarás: `OPENAI_API_KEY`

> Sin esta key, las funciones de IA (meditación, nutrición) usarán los datos demo.
> Todo lo demás funciona sin ella.

### Paso 2.2 — OpenWeather (para clima en pilar Entorno)
1. Ve a [https://openweathermap.org/api](https://openweathermap.org/api)
2. Crea una cuenta gratuita
3. Ve a **API keys** en tu perfil
4. Copia tu key
5. Necesitarás: `OPENWEATHER_API_KEY`

> Sin esta key, el clima usará datos de fallback (Amsterdam, 18°C).

### Paso 2.3 — (Opcional) ElevenLabs (audio de meditaciones)
- Solo si quieres audio generado para las meditaciones
- `ELEVENLABS_API_KEY` y `ELEVENLABS_VOICE_ID`

---

## Fase 3: Conectar el Backend a Supabase

### Paso 3.1 — Actualizar el archivo .env
1. Abre `backend/.env`
2. Cambia estos valores con tus credenciales reales:

```env
# Cambiar de "demo" a "production"
environment=production

# Supabase (de Paso 1.2)
supabase_url=https://TU-PROYECTO.supabase.co
supabase_key=eyJ...tu_anon_key...
supabase_service_key=eyJ...tu_service_role_key...

# OpenAI (de Paso 2.1)
openai_api_key=sk-...tu_key...

# OpenWeather (de Paso 2.2)
openweather_api_key=tu_key_aqui

# JWT (cambia esto a algo único y seguro)
jwt_secret_key=genera-un-string-random-largo-y-seguro-aqui
```

> 🔑 Para generar un jwt_secret_key seguro, ejecuta en terminal:
> `python -c "import secrets; print(secrets.token_urlsafe(64))"`

### Paso 3.2 — Reiniciar el backend
```bash
# Parar el servidor actual (Ctrl+C) y reiniciar:
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --port 8000
```

Ahora deberías ver el mensaje de inicio SIN "modo demo".

### Paso 3.3 — Probar el registro
```bash
# En otra terminal:
$body = '{"email":"tu@email.com","nombre":"Tu Nombre","password":"test123456"}'
Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/register -Method POST -ContentType "application/json" -Body $body
```

Si ves un `access_token` en la respuesta, ¡la conexión con Supabase funciona!

---

## Fase 4: Configurar el Frontend para Producción

### Paso 4.1 — Actualizar .env.local
1. Abre `frontend/.env.local`
2. Cambia la URL del API a tu URL de producción (si es local, déjalo igual):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para despliegue en Vercel, esto será:
```env
NEXT_PUBLIC_API_URL=https://tu-backend.railway.app
```

---

## Fase 5: Desplegar el Backend Online

### Opción A: Railway (recomendado, plan gratuito)
1. Ve a [https://railway.app](https://railway.app) y regístrate con GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Selecciona tu repo de ThriveMind
4. En **Settings**, configura:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Ve a **Variables** y añade TODAS las variables de tu `backend/.env`:
   - `environment=production`
   - `supabase_url=...`
   - `supabase_key=...`
   - `supabase_service_key=...`
   - `openai_api_key=...`
   - `openweather_api_key=...`
   - `jwt_secret_key=...`
6. Click **Deploy** — Railway te dará una URL como `https://thrivemind-backend-xxx.railway.app`

### Opción B: Render (alternativa gratuita)
1. Ve a [https://render.com](https://render.com)
2. **New → Web Service** → conecta tu repo de GitHub
3. Root Directory: `backend`
4. Build Command: `pip install -e ".[dev]"`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Añade las mismas variables de entorno
7. Deploy

---

## Fase 6: Desplegar el Frontend Online

### Vercel (recomendado para Next.js)
1. Ve a [https://vercel.com](https://vercel.com) y regístrate con GitHub
2. Click **"Add New Project"** → importa tu repo
3. En configuración:
   - **Framework Preset**: Next.js (auto-detectado)
   - **Root Directory**: `frontend`
4. En **Environment Variables**, añade:
   - `NEXT_PUBLIC_API_URL` = la URL de tu backend (de Fase 5)
5. Click **Deploy**
6. Vercel te da una URL como `https://thrivemind.vercel.app`

---

## Fase 7: Verificación Final

Después de desplegar, verifica estas rutas:

| Test | URL | Esperado |
|------|-----|----------|
| Backend health | `https://tu-backend/docs` | Swagger UI |
| Frontend login | `https://tu-frontend/login` | Página de login |
| Registro | Crear cuenta desde el frontend | Redirección al dashboard |
| Dashboard | Hacer un check-in | Gráficos actualizados |
| Meditación | Generar meditación en Mente | Guion generado por IA |

---

## 📋 Resumen de Archivos de Referencia

| Archivo | Qué contiene |
|---------|-------------|
| `docs/sql/schema.sql` | Tablas base del proyecto (Fase 1.3) |
| `docs/SUPABASE_SETUP.md` | Tablas de las mejoras (Fase 1.4) |
| `docs/FRONTEND_SETUP.md` | Configuración local del frontend |
| `docs/DEPLOYMENT_GUIDE.md` | Esta guía (despliegue completo) |
| `backend/.env` | Variables de entorno del backend |
| `frontend/.env.local` | Variables de entorno del frontend |

---

## ❓ Troubleshooting

| Problema | Solución |
|----------|---------|
| "supabase_url must be configured" | Verificar que `.env` tiene `supabase_url` correcto |
| "401 Unauthorized" en el frontend | Verificar que `jwt_secret_key` es el mismo en backend |
| "CORS error" en el navegador | Añadir URL del frontend a `allowed_origins` en `backend/app/main.py` |
| Meditación dice "datos demo" | Verificar `OPENAI_API_KEY` y que `environment=production` |
| Tablas no existen en Supabase | Re-ejecutar `schema.sql` en SQL Editor |
