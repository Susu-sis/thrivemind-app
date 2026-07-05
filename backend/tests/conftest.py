"""
conftest.py — Fixtures compartidas para todos los tests de ThriveMind.
"""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def supabase_mock():
    """
    Mock del cliente Supabase que simula las operaciones de base de datos.
    Devuelve un MagicMock configurado para la cadena de llamadas típica:
    supabase.table("x").insert({...}).execute() → data[0]
    """
    mock = MagicMock()

    # Configurar la cadena de llamadas por defecto
    mock_execute = MagicMock()
    mock_execute.data = [{"id": "test-id-123", "created_at": "2026-01-01T00:00:00Z"}]

    # table().insert().execute()
    mock.table.return_value.insert.return_value.execute.return_value = mock_execute
    # table().select().eq().execute()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute
    # table().select().eq().order().limit().execute()
    mock.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = mock_execute
    # table().update().eq().execute()
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_execute

    return mock
