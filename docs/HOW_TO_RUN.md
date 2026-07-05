# ThriveMind — How to Run the App

> This guide covers running the app in **Demo Mode** (no credentials needed)
> and **Production Mode** (real Supabase + API keys), plus a full index of
> every readable file in the project and what it contains.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Demo Mode — Run Locally Without Any Credentials](#2-demo-mode)
3. [Production Mode — Run With Real Credentials](#3-production-mode)
4. [All Required Credentials Explained](#4-credentials-reference)
5. [Running Tests](#5-running-tests)
6. [Complete File Index](#6-complete-file-index)

---

## 1. Prerequisites

| Tool | Version | How to install |
|------|---------|----------------|
| Python | ≥ 3.11 | [python.org](https://python.org) |
| Node.js | ≥ 20 LTS | Portable zip from [nodejs.org/download](https://nodejs.org/en/download/) |
| uv (optional) | any | `pip install uv` |

**Windows note:** If Node.js is installed as a portable zip (no system installer),
set your PATH each session:
```powershell
$env:PATH = "C:\Users\Suha.Saad\Proyectos\node-v24.17.0-win-x64;" + $env:PATH
```
Use `npm.cmd` instead of `npm` in all commands (org policy blocks unsigned `.ps1`).

---

## 2. Demo Mode — Run Locally Without Any Credentials

In demo mode the backend uses **hardcoded fake data** — no Supabase, no OpenAI,
no weather API. You can log in with any email/password and explore the full UI.

### Step 1 — Ensure `.env` is in demo mode

Open `backend/.env` and make sure this line reads:

```env
environment=demo
```

Everything else in the file can stay as placeholder text.

### Step 2 — Start the Backend

```powershell
cd C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

You should see:
```
🌱 ThriveMind API arrancando en modo demo
📖 Documentación: http://localhost:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000
```

> **Do NOT use `--reload`** unless you need live reloads during development.
> The `--reload` flag spawns a watcher process that can leave a zombie on port 8000
> if killed improperly. If port 8000 is stuck, run:
> `Stop-Process -Name python -Force`

### Step 3 — Start the Frontend

Open a **second** PowerShell terminal:

```powershell
$env:PATH = "C:\Users\Suha.Saad\Proyectos\node-v24.17.0-win-x64;" + $env:PATH
cd C:\Users\Suha.Saad\Proyectos\thrivemind-app\frontend
npm.cmd run dev
```

You should see:
```
▲ Next.js 14.x
- Local: http://localhost:3000
✓ Ready in ~22s
```

### Step 4 — Open the App

- **Frontend:** http://localhost:3000 (redirects to `/login`)
- **API docs:** http://localhost:8000/docs

Log in with **any email and any password** — demo mode accepts all credentials
and returns a valid JWT token with fake user data.

### What works in Demo Mode

| Feature | Demo behaviour |
|---------|---------------|
| Login / Register | ✅ Accepts any credentials |
| Dashboard charts | ✅ 14 days of fake check-in data |
| Correlations | ✅ Pre-computed Pearson coefficients |
| Insights & Recommendations | ✅ Static knowledge-base responses |
| Meditation generator | ✅ Returns a pre-built meditation text |
| Nutrition analysis | ✅ Returns a mock nutritional breakdown |
| Farming module | ✅ Returns sample plant recommendations |
| Weather (Entorno) | ✅ Returns Amsterdam fallback data (18 °C) |
| Philips Hue IoT | ✅ Simulation mode (no real bridge needed) |
| Gamification | ✅ Fake points and milestones |
| Search | ✅ Searches the bundled RAG corpus |

---

## 3. Production Mode — Run With Real Credentials

Production mode connects to a real Supabase database, calls OpenAI for AI
features, and uses live weather data.

### Step 1 — Set Up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor → New Query**, paste the contents of `docs/sql/schema.sql`,
   and click **Run**
3. Run a second query with all the SQL in `docs/SUPABASE_SETUP.md` (sections 1–8)
4. Verify the following tables exist in **Table Editor**:
   `profiles`, `checkins`, `user_preferences`, `meditation_sessions`,
   `nutrition_analyses`, `cultivos_activos`, `farming_chat_messages`, `papers`,
   `gamification_history`, `user_milestones`, `hue_profiles`, `meal_plans`,
   `notifications`, `intervention_logs`, `user_overrides`

### Step 2 — Fill in `backend/.env`

```env
# ── General ──────────────────────────────────────────────────────────────────
app_name=ThriveMind
app_version=0.1.0
environment=production          # <-- change from "demo"

# ── Supabase (required) ───────────────────────────────────────────────────────
supabase_url=https://YOUR-PROJECT.supabase.co
supabase_anon_key=eyJ...        # "anon public" key from Supabase Settings → API
supabase_service_key=eyJ...     # "service_role secret" — never expose publicly

# ── JWT (required) ────────────────────────────────────────────────────────────
secret_key=GENERATE-64-CHAR-RANDOM-STRING
algorithm=HS256
access_token_expire_minutes=10080

# ── OpenAI (required for AI features) ────────────────────────────────────────
openai_api_key=sk-...

# ── OpenWeatherMap (optional — fallback: Amsterdam 18°C) ─────────────────────
openweathermap_api_key=YOUR_KEY

# ── ElevenLabs (optional — audio meditations) ────────────────────────────────
elevenlabs_api_key=
elevenlabs_voice_id=21m00Tcm4TlvDq8ikWAM

# ── Philips Hue (optional — simulation mode if empty) ────────────────────────
hue_bridge_ip=
hueappkey=
```

Generate a secure JWT secret:
```powershell
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Step 3 — Seed Demo Data (optional)

If you want pre-populated chart data:
```powershell
cd C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe scripts/seed_dashboard_demo.py
```

### Step 4 — Start Backend and Frontend

Same commands as Demo Mode (Step 2 and 3 above).
The backend will now read from Supabase and call external APIs.

---

## 4. Credentials Reference

| Variable | Required | Where to get it | What it does |
|----------|----------|-----------------|--------------|
| `supabase_url` | Production only | Supabase → Settings → API → Project URL | Database endpoint |
| `supabase_anon_key` | Production only | Supabase → Settings → API → anon public | Client-side auth |
| `supabase_service_key` | Production only | Supabase → Settings → API → service_role | Admin DB access (never expose) |
| `secret_key` | Both modes | Generate with `secrets.token_urlsafe(64)` | Signs JWT tokens |
| `openai_api_key` | For AI features | [platform.openai.com](https://platform.openai.com) → API Keys | Meditation + nutrition AI |
| `openweathermap_api_key` | Optional | [openweathermap.org/api](https://openweathermap.org/api) | Live weather in Entorno |
| `elevenlabs_api_key` | Optional | [elevenlabs.io](https://elevenlabs.io) | Audio meditation voice |
| `elevenlabs_voice_id` | Optional | ElevenLabs dashboard | Default: Rachel voice |
| `hue_bridge_ip` | Optional | Philips Hue app → Bridge info | IoT light control |
| `hueappkey` | Optional | Philips Hue developer portal | IoT auth key |

---

## 5. Running Tests

```powershell
cd C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -m pytest tests/ -v
```

Tests run with mock Supabase fixtures — no real credentials needed.

---

## 6. Complete File Index

Every readable file in the project, grouped by area. Scripts (`.py` automation)
are noted but not detailed since they are not meant for reading.

---

### 6.1 Root Level

| File | Description |
|------|-------------|
| `README.md` | Project overview, folder structure, Windows compatibility notes, and a table of errors found and fixed in the original guide |
| `.gitignore` | Git ignore rules (venv, node_modules, .env, .next, __pycache__) |
| `.github/workflows/ci.yml` | GitHub Actions CI pipeline — runs pytest on backend and `next build` on frontend on every push to `main`/`develop` |

---

### 6.2 Backend — Configuration & Entry Point

| File | Description |
|------|-------------|
| `backend/.env` | **Active** environment variables file. Controls which mode the app runs in and holds all credentials. Never commit this. |
| `backend/.env.example` | Template showing all available variables with placeholder values. Copy to `.env` to get started. |
| `backend/pyproject.toml` | Python project definition — lists all dependencies (FastAPI, Uvicorn, Supabase, LangChain, OpenAI, scipy, XGBoost, etc.) and dev/IoT extras. |
| `backend/app/main.py` | FastAPI application entry point. Creates the app, adds CORS middleware (allows `localhost:3000` and `localhost:5173`), and registers the API router. |

---

### 6.3 Backend — Core Layer (`backend/app/core/`)

| File | Description |
|------|-------------|
| `core/config.py` | Pydantic Settings class that reads `.env` and exposes all configuration values. Uses `@lru_cache` so settings are loaded only once per process. |
| `core/database.py` | Singleton factory for Supabase clients — one sync client (`get_supabase_client`) and one async client (`get_async_supabase`). In demo mode, returns `DemoSupabaseClient` instead of connecting. |
| `core/auth.py` | FastAPI dependency `get_current_user` — decodes the JWT from the `Authorization` header and returns the user payload. Used by protected endpoints. |
| `core/demo.py` | All hardcoded fake data for demo mode: a demo user ID, 14 days of check-in records, sample meditations, meal plans, correlations, and farming responses. This is what the app serves when `environment=demo`. |

---

### 6.4 Backend — Models (`backend/app/models/`)

| File | Description |
|------|-------------|
| `models/user.py` | Pydantic schemas for auth: `UserRegister`, `UserLogin`, `Token` (the JWT response), `UserResponse`, `TokenData`. |
| `models/checkin.py` | Pydantic schemas for daily check-ins: `CheckinCreate` (the 8-pillar input form) and `CheckinResponse`. |
| `models/preferences.py` | Schemas for user preferences: `PillarConfig`, `UserPreferencesUpdate`, `UserPreferencesResponse`. Includes diet, allergies, fitness goal, weekly budget. |

---

### 6.5 Backend — API Endpoints (`backend/app/api/v1/endpoints/`)

| File | Prefix | Description |
|------|--------|-------------|
| `router.py` | `/api/v1` | Registers all 12 routers. The single source of truth for API URL structure. |
| `auth.py` | `/auth` | `POST /register`, `POST /login`, `POST /refresh`, `GET /me` |
| `checkin.py` | `/checkin` | `POST /` (save check-in), `GET /dashboard/tendencias` (14-day trends), `GET /correlaciones` (cross-pillar Pearson matrix) |
| `mente.py` | `/mente` | `POST /generar` (AI meditation), `GET /historial` (past sessions), `POST /respiracion` (breathing guide), `POST /feedback` |
| `cuerpo.py` | `/cuerpo` | `POST /nutricion/analizar-imagen` (GPT-4o Vision food analysis), `GET /nutricion/recomendacion`, `POST /nutricion/feedback` |
| `entorno.py` | `/entorno` | `GET /cultivos` (active plants), `POST /cultivos` (add plant), `GET /consejo` (farming advice), `GET /clima` (weather) |
| `ambient.py` | `/ambient` | `GET /status` (Hue bridge status), `POST /apply` (apply light scene), `POST /auto` (auto-adjust based on check-in) |
| `preferences.py` | `/preferences` | `GET /` (current preferences), `PATCH /` (update preferences) |
| `insights.py` | `/insights` | Holistic analysis — `GET /recomendaciones`, `GET /convergencia`, `GET /matriz-correlacion`, `GET /holistic`, `GET /historial-contexto` |
| `search.py` | `/search` | `GET /` — global semantic search across the RAG corpus (36 scientific papers) |
| `gamification.py` | `/gamification` | `GET /status` (points, streaks, milestones), `POST /award` (give points for an action) |
| `hue.py` | `/hue` | `GET /profiles` (custom light profiles), `POST /profiles` (save profile), `DELETE /profiles/{id}` |
| `meal_planner.py` | `/meal-planner` | `POST /generar` (weekly meal plan), `GET /historial` (past plans), `POST /feedback` |

---

### 6.6 Backend — Services (`backend/app/services/`)

| File | Description |
|------|-------------|
| `auth_service.py` | Handles register/login logic, bcrypt password hashing, JWT creation (access + refresh tokens), and the `_demo_token()` shortcut for demo mode. |
| `checkin_service.py` | Saves check-ins to Supabase, calculates streaks (`calcular_racha()`), and triggers point awards after each submission. |
| `correlation_service.py` | Computes Pearson cross-pillar correlations from the last 30 check-ins. Returns a matrix of coefficients with significance labels. |
| `meditation_service.py` | LangChain + GPT-4o pipeline that generates personalized meditations using the RAG corpus and user context. Falls back to a static text in demo mode. |
| `nutrition_service.py` | GPT-4o Vision endpoint for food image analysis. Also generates nutrient-based recommendations via neuronutrition knowledge base. |
| `farming_service.py` | Recommends plants based on user location, season, and emotional state. Checks harvest readiness for active crops. |
| `weather_service.py` | Calls OpenWeatherMap API. Returns Amsterdam fallback (18 °C, cloudy) when no API key is configured. |
| `solar_service.py` | Fetches sunrise/sunset times from `sunrise-sunset.org` for circadian rhythm calculations. |
| `rag_service.py` | pgvector semantic search over 36 indexed scientific papers. Returns top-k chunks with paper title, authors, and DOI as citations. |
| `context_engine.py` | Assembles the 5-layer user context: (1) latest check-in, (2) HRV classification, (3) correlations, (4) user preferences, (5) recent history. Fed into all AI services. |
| `knowledge_base.py` | Five hardcoded scientific dictionaries: neurotransmitter precursors (T3), chronobiology rules, farming stress-relief map, HRV bands, and circadian lighting profiles. No external calls. |
| `preferences_service.py` | CRUD for user preferences. `build_pillar_context()` converts preferences into a plain-English string for LLM prompts. |
| `gamification_service.py` | Tracks points, streaks, and unlocks milestones. `award_points()` is called automatically by checkin, meditation, and nutrition services. |
| `emotional_classifier.py` | Two-phase ML classifier: rule-based cold-start for users with < 30 check-ins, XGBoost model (F1=0.845) for users with ≥ 30 entries. |
| `sentiment_service.py` | VADER-based sentiment analysis on free-text journal notes from check-ins. Returns compound score + emotion label. |
| `intervention_service.py` | Logs AI interventions and tracks acceptance rates (MLOps). Triggers professional referral when mood ≤ 3 for 3+ of the last 7 days. |
| `override_service.py` | Override Co-pilot — 4-step protocol that lets users override AI recommendations. Tracks a Resilience Counter and applies CIRCADIAN_AUTONOMIC_MATRIX override rules. |
| `orchestration_service.py` | Master orchestrator — calls context engine, then routes to the appropriate services and combines outputs into a holistic response. |
| `recommendation_service.py` | Generates cross-pillar recommendations (e.g. "your low sleep is correlated with poor nutrition scores — try this..."). |
| `hue_service.py` | Philips Hue bridge control. Runs in simulation mode (logs actions, no real API call) when `hue_bridge_ip` is not set. |
| `hue_custom_service.py` | CRUD for user-defined custom Hue light profiles stored in Supabase. |
| `meal_planner_service.py` | GPT-4o weekly meal plan generator. Respects allergies, diet preference, budget, and nutritional goals from user preferences. |
| `search_service.py` | Global search — queries the RAG corpus and returns matching papers and app content. |

---

### 6.7 Backend — Data

| File | Description |
|------|-------------|
| `backend/app/data/thrivemind_rag_corpus_v4.json` | The scientific knowledge base — 36 peer-reviewed papers on meditation, nutrition, chronobiology, and stress. Pre-chunked and indexed by `rag_service.py` via pgvector. |

---

### 6.8 Backend — Tests (`backend/tests/`)

| File | Description |
|------|-------------|
| `tests/conftest.py` | Pytest fixtures — provides a `supabase_mock` fixture that patches the Supabase client so tests run without real credentials. |
| `tests/test_checkin.py` | Unit tests for check-in creation: validates schema, score ranges, and streak detection logic. |
| `tests/test_correlation.py` | Unit tests for the Pearson correlation engine: tests coefficient calculation and significance thresholds. |

---

### 6.9 Database

| File | Description |
|------|-------------|
| `docs/sql/schema.sql` | **Full SQL schema** — creates all base tables with RLS enabled: `profiles`, `checkins`, `user_preferences`, `meditation_sessions`, `nutrition_analyses`, `cultivos_activos`, `farming_chat_messages`, `papers`. Run this first in Supabase SQL Editor. |
| `docs/SUPABASE_SETUP.md` | **Extended SQL** — adds columns and tables for v2 features: gamification, HUE profiles, meal plans, notifications, intervention logs, override tracking, refresh tokens, and extended user preferences. Run this second. |

---

### 6.10 Frontend — App Pages (`frontend/src/app/`)

| File | Route | Description |
|------|-------|-------------|
| `app/page.tsx` | `/` | Root redirect to `/login` |
| `app/layout.tsx` | all | Root layout — sets dark theme, loads Sonner toast provider |
| `app/globals.css` | all | Tailwind base styles and CSS custom properties |
| `app/login/page.tsx` | `/login` | Login form with email/password, JWT storage to localStorage and cookie |
| `app/register/page.tsx` | `/register` | Registration form with email, password, nombre, apellido |
| `app/dashboard/layout.tsx` | `/dashboard/*` | Dashboard shell — sidebar navigation with all pillar links |
| `app/dashboard/page.tsx` | `/dashboard` | Main dashboard — Recharts line graphs for all 8 check-in metrics over 14 days |
| `app/dashboard/checkin/page.tsx` | `/dashboard/checkin` | Daily check-in form — 8 sliders (emotion, energy, sleep, stress, etc.) + free-text note |
| `app/dashboard/mente/page.tsx` | `/dashboard/mente` | Meditation generator — calls `/mente/generar`, displays result + audio player placeholder |
| `app/dashboard/cuerpo/page.tsx` | `/dashboard/cuerpo` | Nutrition — image upload for food analysis + nutrient recommendations |
| `app/dashboard/entorno/page.tsx` | `/dashboard/entorno` | Farming module — active crops list, add plant form, weather widget |
| `app/dashboard/correlaciones/page.tsx` | `/dashboard/correlaciones` | Cross-pillar correlation matrix with color-coded Pearson coefficients |
| `app/dashboard/insights/page.tsx` | `/dashboard/insights` | Holistic insights — recommendations, convergence score, context history |
| `app/dashboard/convergencia/page.tsx` | `/dashboard/convergencia` | Pillar convergence radar chart |
| `app/dashboard/sentimiento/page.tsx` | `/dashboard/sentimiento` | Emotional sentiment trend from journal notes |
| `app/dashboard/historial/page.tsx` | `/dashboard/historial` | Full check-in history table |
| `app/dashboard/gamificacion/page.tsx` | `/dashboard/gamificacion` | Points, streak counter, milestone badges |
| `app/dashboard/meal-planner/page.tsx` | `/dashboard/meal-planner` | Weekly AI meal plan generator |
| `app/dashboard/perfiles-hue/page.tsx` | `/dashboard/perfiles-hue` | Philips Hue custom profile manager |
| `app/dashboard/configuracion/page.tsx` | `/dashboard/configuracion` | User preferences form (diet, allergies, fitness goal, budget) |

---

### 6.11 Frontend — Shared Code

| File | Description |
|------|-------------|
| `src/lib/api.ts` | Axios client pre-configured with `baseURL = NEXT_PUBLIC_API_URL + /api/v1`. Automatically attaches JWT from localStorage on every request. Handles 401 errors by attempting a token refresh before failing. |
| `src/hooks/useAuth.ts` | React hook exposing `login()`, `register()`, `logout()`, `user`, `isAuthenticated`. Stores JWT and user data in both localStorage and a cookie (for middleware). |
| `src/middleware.ts` | Next.js middleware that checks for the `thrivemind_token` cookie on every request to `/dashboard/*` — redirects to `/login` if missing. |
| `src/components/GlobalSearch.tsx` | Search bar component that calls `/search` and displays results inline. Used in the dashboard header. |
| `src/components/theme-provider.tsx` | `next-themes` wrapper for dark/light mode toggle. |
| `frontend/.env.local` | Frontend environment — sets `NEXT_PUBLIC_API_URL=http://localhost:8000`. Change to your production backend URL for deployment. |
| `frontend/next.config.js` | Next.js config — currently default settings. |
| `frontend/tailwind.config.js` | Tailwind CSS config — extends with custom colors for the ThriveMind brand palette. |
| `frontend/tsconfig.json` | TypeScript config — sets `@/` path alias pointing to `src/`. |
| `frontend/package.json` | Frontend dependencies: Next.js 14, React 18, Axios, Recharts, next-themes, Sonner, lucide-react. |

---

### 6.12 Frontend-Src (Reference Copies)

`frontend-src/` is a **snapshot** of the original source files before they were
merged into `frontend/`. It exists as a reference if something in `frontend/`
gets overwritten. The files mirror the same structure:
`app/`, `hooks/useAuth.ts`, `lib/api.ts`, `components/theme-provider.tsx`, `middleware.ts`.

---

### 6.13 Supabase Edge Functions

| File | Description |
|------|-------------|
| `supabase/functions/notificaciones-diarias/index.ts` | Deno Edge Function that runs on a cron schedule. Queries users who haven't checked in today and sends a motivational email reminder via Supabase's built-in email service. Deploy via `supabase functions deploy notificaciones-diarias`. |

---

### 6.14 Documentation Files

| File | Description |
|------|-------------|
| `docs/HOW_TO_RUN.md` | **This file** — complete run guide for demo and production modes + file index |
| `README.md` | High-level project overview, folder map, Windows compatibility notes, and errors fixed during development |
| `docs/DEPLOYMENT_GUIDE.md` | Step-by-step guide from local demo → full production on Supabase + Railway/Vercel. Covers all phases: Supabase setup, API keys, env config, deployment commands |
| `docs/FRONTEND_SETUP.md` | Steps to bootstrap the Next.js frontend from scratch using `create-next-app`, install shadcn/ui, and copy the custom source files |
| `docs/SUPABASE_SETUP.md` | All SQL for the extended database schema (v2 features). Run after `schema.sql`. |
| `docs/sql/schema.sql` | Base database schema — all tables, indexes, and RLS policies |
| `docs/GAP_ANALYSIS.md` | Detailed comparison of implemented features vs. the original 95 MVP requirements. Shows 85% coverage with notes on what's partial or missing |
| `docs/GUIA_TECNICA_FINAL.md` | Full technical methodology guide — architecture diagrams, AI model descriptions, data flow, security design, and evidence for academic submission |
| `docs/resultados/RESULTADOS_DOCUMENTADOS.md` | Documented test results captured in demo mode — screenshots inventory, API JSON responses, and feature validation table |

---

### 6.15 Screenshots & API Evidence

| Location | Description |
|----------|-------------|
| `docs/resultados/*.png` | 15 screenshots of the running frontend (login, dashboard, each pillar page, gamification, meal planner, HUE profiles, check-in form) |
| `docs/resultados/api_evidence/*.json` | 28 raw JSON responses captured from real API calls in demo mode — covers auth, check-in, correlations, all pillars, IoT, gamification, search, and gap-filling endpoints |

---

## Quick Reference — Common Commands

```powershell
# Kill a stuck backend (port 8000 occupied)
Stop-Process -Name python -Force

# Start backend (demo mode, no reload)
Set-Location C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000

# Start frontend
$env:PATH = "C:\Users\Suha.Saad\Proyectos\node-v24.17.0-win-x64;" + $env:PATH
Set-Location C:\Users\Suha.Saad\Proyectos\thrivemind-app\frontend
npm.cmd run dev

# Run tests
Set-Location C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -m pytest tests/ -v

# Generate secure JWT secret
C:\Users\Suha.Saad\Proyectos\thrivemind-app\backend\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(64))"
```
