# -*- coding: utf-8 -*-
"""Esquemas (Pydantic) para los endpoints de Machine Learning."""
from pydantic import BaseModel, Field


class LecturaML(BaseModel):
    """Lectura para predicción / detección de anomalías."""
    hora: int = Field(..., ge=0, le=23, description="Hora del día (0 a 23)")
    temperatura: float = Field(..., description="Temperatura actual en °C")
    humedad: float = Field(..., ge=0, le=100, description="Humedad relativa en %")
    luminosidad: float = Field(..., ge=0, description="Luminosidad en lux")

    model_config = {
        "json_schema_extra": {
            "example": {"hora": 14, "temperatura": 22.5, "humedad": 55.0, "luminosidad": 800.0}
        }
    }


class RespuestaPrediccion(BaseModel):
    temperatura_predicha: float
    unidad: str = "°C"
    alerta_helada: bool


class RespuestaAnomalia(BaseModel):
    es_anomalia: bool
    puntuacion: float
