"""
Tests del módulo de check-ins de ThriveMind.

Ejecutar: cd backend && pytest tests/test_checkin.py -v
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from app.services.checkin_service import guardar_checkin, calcular_racha


class TestCheckinCreation:

    def test_checkin_creation(self, supabase_mock):
        datos_checkin = {
            "user_id": "test-user-123",
            "estado_emocional": 4,
            "energia_fisica": 5,
            "horas_sueno": 5.5,
            "conexion_entorno": 6,
            "emocion_principal": "ansiedad",
            "tipo_checkin": "diario",
            "nota": "Semana difícil en el trabajo",
        }

        with patch("app.services.checkin_service.get_supabase_client", return_value=supabase_mock):
            resultado = guardar_checkin(datos_checkin)

        supabase_mock.table.assert_called_with("checkins")
        insert_call = supabase_mock.table.return_value.insert
        insert_call.assert_called_once()

        args_insert = insert_call.call_args[0][0]
        assert args_insert["user_id"] == "test-user-123"
        assert args_insert["estado_emocional"] == 4
        assert args_insert["horas_sueno"] == 5.5
        assert args_insert["emocion_principal"] == "ansiedad"

        assert resultado is not None
        assert "id" in resultado

    def test_checkin_campos_opcionales(self, supabase_mock):
        datos_sin_nota = {
            "user_id": "test-user-123",
            "estado_emocional": 7,
            "energia_fisica": 8,
            "horas_sueno": 7.5,
            "conexion_entorno": 7,
            "emocion_principal": "calma",
            "tipo_checkin": "diario",
        }

        with patch("app.services.checkin_service.get_supabase_client", return_value=supabase_mock):
            resultado = guardar_checkin(datos_sin_nota)

        assert resultado is not None

    def test_checkin_valores_limite(self, supabase_mock):
        datos_maximo = {
            "user_id": "test-user-123",
            "estado_emocional": 10,
            "energia_fisica": 10,
            "horas_sueno": 9.0,
            "conexion_entorno": 10,
            "emocion_principal": "alegría",
            "tipo_checkin": "diario",
        }

        with patch("app.services.checkin_service.get_supabase_client", return_value=supabase_mock):
            resultado = guardar_checkin(datos_maximo)

        assert resultado is not None


class TestCalcularRacha:

    def _checkin(self, dias_atras: int) -> dict:
        """Helper: genera un check-in con fecha relativa a hoy."""
        fecha = datetime.now(timezone.utc) - timedelta(days=dias_atras)
        return {"created_at": fecha.isoformat()}

    def test_racha_lista_vacia(self):
        assert calcular_racha([]) == 0

    def test_racha_un_dia_hoy(self):
        checkins = [self._checkin(0)]
        assert calcular_racha(checkins) == 1

    def test_racha_tres_dias_consecutivos(self):
        checkins = [self._checkin(0), self._checkin(1), self._checkin(2)]
        assert calcular_racha(checkins) == 3

    def test_racha_interrumpida(self):
        # Hoy + hace 2 días (sin ayer) → racha = 1
        checkins = [self._checkin(0), self._checkin(2)]
        assert calcular_racha(checkins) == 1

    def test_racha_solo_pasado(self):
        # Ningún check-in hoy → racha = 0
        checkins = [self._checkin(1), self._checkin(2)]
        assert calcular_racha(checkins) == 0
