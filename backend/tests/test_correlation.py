"""
Tests del Motor de Correlación Cross-Pilar de ThriveMind.

Ejecutar: cd backend && pytest tests/test_correlation.py -v
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.services.correlation_service import (
    calcular_correlaciones_usuario,
    interpretar_correlacion,
    generar_insight_texto,
)


class TestCorrelationEngine:

    def test_correlacion_perfecta_positiva(self):
        resultado = interpretar_correlacion(1.0)
        assert resultado["fuerza"] == "fuerte"
        assert resultado["direccion"] == "positiva"

    def test_correlacion_negativa_fuerte(self):
        resultado = interpretar_correlacion(-0.85)
        assert resultado["fuerza"] == "fuerte"
        assert resultado["direccion"] == "negativa"

    def test_sin_correlacion(self):
        resultado = interpretar_correlacion(0.05)
        assert resultado["fuerza"] == "sin correlación"

    def test_insight_texto_positivo(self):
        insight = generar_insight_texto("horas_sueno", "energia_fisica", 0.81)
        assert "sueño" in insight.lower() or "horas" in insight.lower()
        assert "energía" in insight.lower() or "energia" in insight.lower()
        assert "0.81" in insight

    def test_correlaciones_insuficientes_datos(self, supabase_mock):
        supabase_mock.table.return_value.select.return_value \
            .eq.return_value.order.return_value.limit.return_value \
            .execute.return_value.data = [
                {"estado_emocional": 5, "energia_fisica": 6, "horas_sueno": 7.0, "conexion_entorno": 5},
                {"estado_emocional": 6, "energia_fisica": 7, "horas_sueno": 7.5, "conexion_entorno": 6},
                {"estado_emocional": 4, "energia_fisica": 5, "horas_sueno": 6.0, "conexion_entorno": 4},
            ]

        with patch("app.services.correlation_service.supabase", supabase_mock):
            resultado = calcular_correlaciones_usuario("test-user-123", dias=30)

        assert resultado["suficientes_datos"] is False
        assert resultado["n_checkins"] == 3

    def test_correlaciones_datos_suficientes(self, supabase_mock):
        checkins_demo = []
        for i in range(14):
            horas = 5.0 + (i % 4) * 0.75
            energia = 4 + int((horas - 5.0) * 1.5)
            checkins_demo.append({
                "estado_emocional": 5 + (i % 3),
                "energia_fisica": min(10, energia),
                "horas_sueno": horas,
                "conexion_entorno": 5 + (i % 4),
            })

        supabase_mock.table.return_value.select.return_value \
            .eq.return_value.order.return_value.limit.return_value \
            .execute.return_value.data = checkins_demo

        with patch("app.services.correlation_service.supabase", supabase_mock):
            resultado = calcular_correlaciones_usuario("test-user-123", dias=30)

        assert resultado["suficientes_datos"] is True
        assert resultado["n_checkins"] == 14
        assert len(resultado["correlaciones"]) >= 1

        correlacion_top = resultado["correlaciones"][0]
        for campo in ["variable_x", "variable_y", "r", "p_value", "fuerza", "insight"]:
            assert campo in correlacion_top
