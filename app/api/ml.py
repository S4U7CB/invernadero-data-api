# -*- coding: utf-8 -*-
"""Endpoints de Machine Learning: predicción y detección de anomalías."""
from fastapi import APIRouter

from app.schemas.ml import LecturaML, RespuestaPrediccion, RespuestaAnomalia
from app.services import ml_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning (Análisis)"])


@router.post("/predecir", response_model=RespuestaPrediccion, summary="Predicción de temperatura")
def predecir(lectura: LecturaML):
    """Predice la temperatura de la próxima hora a partir de una lectura actual."""
    temperatura, alerta = ml_service.predecir_temperatura(
        lectura.hora, lectura.temperatura, lectura.humedad, lectura.luminosidad)
    return RespuestaPrediccion(temperatura_predicha=temperatura, alerta_helada=alerta)


@router.post("/detectar-anomalia", response_model=RespuestaAnomalia, summary="Detección de anomalías")
def detectar_anomalia(lectura: LecturaML):
    """Detecta si una lectura ambiental es anómala (posible fallo de sensor)."""
    es_anomalia, puntuacion = ml_service.detectar_anomalia(
        lectura.hora, lectura.temperatura, lectura.humedad, lectura.luminosidad)
    return RespuestaAnomalia(es_anomalia=es_anomalia, puntuacion=puntuacion)
