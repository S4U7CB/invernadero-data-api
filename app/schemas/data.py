# -*- coding: utf-8 -*-
"""Esquemas (Pydantic) para la ingestión, procesamiento y consulta de datos."""
from typing import Optional
from pydantic import BaseModel, Field


class LecturaIn(BaseModel):
    """Lectura ambiental que se envía al endpoint de ingestión."""
    temperatura: float = Field(..., description="Temperatura en grados Celsius")
    humedad: float = Field(..., description="Humedad relativa en porcentaje")
    luminosidad: float = Field(..., description="Luminosidad en lux")
    fecha_hora: Optional[str] = Field(None, description="Marca de tiempo ISO (opcional)")

    model_config = {
        "json_schema_extra": {
            "example": {"temperatura": 18.4, "humedad": 62.0, "luminosidad": 540.0,
                        "fecha_hora": "2026-05-01T08:00:00"}
        }
    }


class RespuestaIngesta(BaseModel):
    recibidos: int = Field(..., description="Total de lecturas recibidas")
    validos: int = Field(..., description="Lecturas válidas almacenadas")
    rechazados: int = Field(..., description="Lecturas rechazadas por la validación")
    mensaje: str


class RespuestaProcesamiento(BaseModel):
    registros_procesados: int
    anomalias_detectadas: int
    temp_promedio: float
    mensaje: str


class Resultado(BaseModel):
    id: int
    calculado_en: str
    n_registros: int
    temp_promedio: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    hum_promedio: Optional[float] = None
    lum_promedio: Optional[float] = None
    n_anomalias: Optional[int] = None
