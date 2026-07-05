"""
Módulo centralizado de conexión a Supabase.

Patrón Singleton: una sola instancia de cada cliente en toda la aplicación.

Dos clientes:
1. supabase (Client síncrono) — para auth.py, rag_service.py
2. _async_client (AsyncClient asíncrono) — para servicios con await
"""

from supabase import create_client, Client
from app.core.config import settings

# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE SÍNCRONO — Para operaciones sin await (auth, RAG)
# ─────────────────────────────────────────────────────────────────────────────

_sync_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Devuelve el cliente síncrono de Supabase (singleton).
    Usado por auth_service.py, rag_service.py, correlation_service.py, etc.
    En modo demo, retorna DemoSupabaseClient.
    """
    if settings.environment == "demo":
        return DemoSupabaseClient()

    global _sync_client
    if _sync_client is None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError(
                "supabase_url y supabase_service_key deben estar configurados en .env"
            )
        _sync_client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
    return _sync_client


# Alias for backward compatibility
supabase: Client | None = None


def _get_sync_supabase() -> Client:
    """Lazy initialization of the sync client module-level variable."""
    global supabase
    if supabase is None:
        try:
            supabase = get_supabase_client()
        except ValueError:
            pass  # Will be None if not configured yet
    return supabase


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE ASÍNCRONO — Para operaciones con await (servicios, endpoints)
# ─────────────────────────────────────────────────────────────────────────────

_async_client = None


async def get_supabase():
    """
    Dependencia de FastAPI que devuelve el cliente Supabase síncrono.
    Todos los endpoints llaman a .execute() sin await, así que usamos el cliente síncrono.
    En modo demo, retorna un mock client con datos de prueba.
    """
    if settings.environment == "demo":
        return DemoSupabaseClient()

    return get_supabase_client()


# ─────────────────────────────────────────────────────────────────────────────
# DEMO MOCK CLIENT — Returns fake data for exploration without Supabase
# ─────────────────────────────────────────────────────────────────────────────

class _MockResult:
    def __init__(self, data):
        self.data = data


class _MockQuery:
    def __init__(self, table_name: str):
        self._table = table_name

    def select(self, *args, **kwargs): return self
    def insert(self, data, **kwargs):
        self._insert_data = data
        return self
    def update(self, data, **kwargs):
        self._update_data = data
        return self
    def delete(self, **kwargs): return self
    def eq(self, *args, **kwargs): return self
    def neq(self, *args, **kwargs): return self
    def gt(self, *args, **kwargs): return self
    def gte(self, *args, **kwargs): return self
    def lt(self, *args, **kwargs): return self
    def lte(self, *args, **kwargs): return self
    def is_(self, *args, **kwargs): return self
    def ilike(self, *args, **kwargs): return self
    def in_(self, *args, **kwargs): return self
    def order(self, *args, **kwargs): return self
    def limit(self, *args, **kwargs): return self
    def range(self, *args, **kwargs): return self
    def single(self, **kwargs): return self

    def execute(self):
        from app.core.demo import (
            demo_checkins, demo_cultivos, DEMO_USER, DEMO_USER_ID,
        )
        import uuid
        if self._table == "checkins":
            return _MockResult(demo_checkins())
        elif self._table == "cultivos_activos":
            return _MockResult(demo_cultivos())
        elif self._table == "profiles":
            return _MockResult([DEMO_USER])
        elif self._table == "meditation_sessions":
            if hasattr(self, '_insert_data'):
                row = {**self._insert_data, "id": str(uuid.uuid4())}
                return _MockResult([row])
            return _MockResult([])
        elif self._table == "nutrition_analyses":
            if hasattr(self, '_insert_data'):
                row = {**self._insert_data, "id": str(uuid.uuid4())}
                return _MockResult([row])
            return _MockResult([])
        elif self._table == "user_preferences":
            return _MockResult([{
                "user_id": DEMO_USER_ID,
                "mente_activo": True, "mente_intensidad": 2,
                "cuerpo_activo": True, "cuerpo_intensidad": 2,
                "entorno_activo": True, "entorno_intensidad": 2,
                "objetivo_principal": "equilibrio",
                "frecuencia_checkin": "diario",
            }])
        return _MockResult([])


class DemoSupabaseClient:
    """Lightweight mock that quacks like a Supabase client for demo endpoints."""
    def table(self, name: str):
        return _MockQuery(name)
