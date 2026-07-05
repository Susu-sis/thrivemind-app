# ThriveMind — Project Overview & Notes

## Project Structure

```
thrivemind-app/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI entry point
│   │   ├── api/v1/
│   │   │   ├── router.py             # Router registering all endpoints
│   │   │   └── endpoints/
│   │   │       ├── auth.py           # /auth/register, /auth/login, /auth/me
│   │   │       ├── checkin.py        # /checkin/, /checkin/dashboard/tendencias, /checkin/correlaciones
│   │   │       ├── mente.py          # /mente/generar, /mente/historial
│   │   │       ├── cuerpo.py         # /cuerpo/nutricion/analizar-imagen, /cuerpo/nutricion/recomendacion
│   │   │       ├── entorno.py        # /entorno/cultivos, /entorno/consejo, /entorno/clima
│   │   │       ├── ambient.py        # /ambient/status, /ambient/apply, /ambient/auto
│   │   │       └── preferences.py    # /preferences/ (GET, PATCH)
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic Settings (reads .env)
│   │   │   ├── database.py           # Supabase sync/async clients
│   │   │   └── auth.py               # JWT get_current_user dependency
│   │   ├── models/
│   │   │   ├── user.py               # UserRegister, UserLogin, Token, etc.
│   │   │   ├── preferences.py        # PillarConfig, UserPreferencesUpdate/Response
│   │   │   └── checkin.py            # CheckinCreate, CheckinResponse
│   │   ├── services/
│   │   │   ├── auth_service.py       # register, login, JWT create/verify
│   │   │   ├── checkin_service.py    # guardar_checkin
│   │   │   ├── preferences_service.py # get/update prefs, build_pillar_context
│   │   │   ├── correlation_service.py # Pearson cross-pilar correlations
│   │   │   ├── rag_service.py        # pgvector search + citation formatting
│   │   │   ├── meditation_service.py # LangChain + RAG meditation generation
│   │   │   ├── nutrition_service.py  # GPT-4o Vision + nutritional recommendations
│   │   │   ├── farming_service.py    # Plant recommendations + harvest checking
│   │   │   ├── weather_service.py    # OpenWeatherMap integration
│   │   │   ├── solar_service.py      # sunrise-sunset.org API
│   │   │   ├── hue_service.py        # Philips Hue IoT with simulation mode
│   │   │   ├── context_engine.py     # HRV classification + context assembly
│   │   │   └── knowledge_base.py     # 5 knowledge dictionaries
│   │   └── data/
│   │       └── thrivemind_rag_corpus_v4.json  # 36 scientific papers
│   ├── tests/
│   │   ├── conftest.py               # Shared fixtures (supabase_mock)
│   │   ├── test_checkin.py           # Check-in creation tests
│   │   └── test_correlation.py       # Correlation engine tests
│   ├── scripts/
│   │   └── seed_dashboard_demo.py    # 14-day demo data generator
│   ├── pyproject.toml                # Python dependencies (uv compatible)
│   └── .env.example                  # Template for .env
├── frontend-src/                     # Custom Next.js files (copy after create-next-app)
│   ├── lib/api.ts                    # Axios client with JWT
│   ├── hooks/useAuth.ts              # Auth hook (login/register/logout)
│   ├── components/theme-provider.tsx # Dark/light theme
│   ├── middleware.ts                 # Route protection
│   └── app/
│       ├── layout.tsx                # Root layout with theme
│       ├── login/page.tsx            # Login page
│       ├── register/page.tsx         # Register page
│       └── dashboard/
│           ├── layout.tsx            # Dashboard with sidebar
│           ├── page.tsx              # Dashboard with charts (Recharts)
│           ├── checkin/page.tsx       # Check-in form
│           ├── mente/page.tsx         # Meditation generator
│           ├── cuerpo/page.tsx        # Nutrition analyzer
│           └── entorno/page.tsx       # Farming module
├── supabase/functions/
│   └── notificaciones-diarias/
│       └── index.ts                  # Edge Function for proactive emails
├── docs/
│   ├── sql/schema.sql                # Complete SQL schema for Supabase
│   └── FRONTEND_SETUP.md             # Steps to initialize Next.js project
└── .gitignore
```

## Windows Compatibility Notes

The guide was written for macOS. These changes were made for Windows:

1. **Shell commands**: All PowerShell — no `bash`, no `brew`, no macOS-specific commands
2. **Path separators**: Python code uses `pathlib.Path` which is cross-platform
3. **Python package manager**: `uv` works on Windows (install: `pip install uv`)
4. **Node.js**: Same commands work on Windows (`npx`, `npm`)
5. **No shebang lines**: Removed `#!/usr/bin/env python3` from scripts
6. **Supabase CLI**: Install via `npm install -g supabase` on Windows (instead of `brew install supabase`)

The Python and TypeScript code itself is fully platform-agnostic.

## Errors Found & Fixed in the Guide

| Location | Issue | Fix Applied |
|----------|-------|-------------|
| §2.3 `.env` | Leading space in `supabase_service_key` and `elevenlabs_api_key` | Fixed in `.env.example` — no leading spaces |
| §5.4 seed script | `os.getenv(" supabase_service_key")` with leading space | Fixed to `os.getenv("supabase_service_key")` |
| §5.2 SQL | `crops` table referenced but later renamed to `cultivos_activos` | Schema uses `cultivos_activos` directly |
| §5.2 SQL | Missing `user_preferences` table definition | Added in consolidated `schema.sql` |
| §6.2 mente.py | Missing `AsyncClient` import, using `supabase` from `create_client` | Endpoint uses `Depends(get_supabase)` consistently |
| §5.7 correlation | Missing `AsyncClient import` | Uses sync `supabase` client as designed |
| §3.2/§3.3 | HRV units inconsistency (beats/min vs ms) | knowledge_base.py uses ms (RMSSD) consistently |
| Edge Function | `Deno.env.get(" supabase_service_key")` with leading space | Fixed to `SUPABASE_SERVICE_ROLE_KEY` (Supabase auto-inject name) |
| §5F/§6B | Two different Motor Context implementations | Consolidated into single `context_engine.py` |

## Transfer to macOS / iOS

When moving to your MacBook Pro:

1. Copy the entire `thrivemind-app/` folder
2. Install Python 3.12 (`brew install python@3.12`)
3. Install Node.js 20+ (`brew install node`)
4. `cd backend && uv sync` (or `pip install -e .`)
5. Run `npx create-next-app@latest frontend` then copy files from `frontend-src/`
6. For iOS (React Native): the backend API stays exactly the same — only the frontend changes

## Manual Steps Required (Internet/Accounts)

These items need your direct action:

1. **Supabase**: Create project at supabase.com, run `docs/sql/schema.sql`
2. **OpenAI**: Get API key from platform.openai.com
3. **ElevenLabs** (optional): Get API key for meditation audio
4. **OpenWeatherMap** (optional): Get free API key
5. **Resend** (optional): Get API key for email notifications
6. **Philips Hue** (optional): Set up Bridge, get Application Key
7. **Fill in** `backend/.env` with your actual keys (copy from `.env.example`)
8. **Run seed script** after Supabase is configured: `cd backend && python scripts/seed_dashboard_demo.py`

## Running the Backend Locally

```bash
cd thrivemind-app/backend

# Create .env from template
copy .env.example .env
# Edit .env with your actual API keys

# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

## Running the Frontend

See `docs/FRONTEND_SETUP.md` for full instructions.
