# -*- coding: utf-8 -*-
"""Endpoints del flujo de datos: ingestión, procesamiento y consulta."""
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_connection
from app.schemas.data import LecturaIn, RespuestaIngesta, RespuestaProcesamiento, Resultado
from app.services import data_service

router = APIRouter(prefix="/api/data", tags=["Flujo de Datos (Big Data)"])


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@router.post("/ingest", response_model=RespuestaIngesta, summary="Ingestión de datos")
def ingestar(lecturas: Union[LecturaIn, List[LecturaIn]], db=Depends(get_db)):
    """Recibe una lectura o una lista de lecturas (JSON), las valida y las almacena."""
    if isinstance(lecturas, LecturaIn):
        lecturas = [lecturas]
    validos, rechazados = data_service.ingestar(db, lecturas)
    return RespuestaIngesta(
        recibidos=len(lecturas), validos=validos, rechazados=rechazados,
        mensaje=f"{validos} lecturas válidas almacenadas; {rechazados} rechazadas por validación.")


@router.post("/ingest/csv", response_model=RespuestaIngesta, summary="Ingestión masiva desde CSV")
def ingestar_csv(db=Depends(get_db)):
    """Carga el dataset CSV incluido en el proyecto (ingestión masiva de datos)."""
    validos, rechazados = data_service.cargar_csv(db)
    return RespuestaIngesta(
        recibidos=validos + rechazados, validos=validos, rechazados=rechazados,
        mensaje=f"CSV ingerido: {validos} lecturas válidas; {rechazados} rechazadas.")


@router.post("/process", response_model=RespuestaProcesamiento, summary="Procesamiento (ETL)")
def procesar(db=Depends(get_db)):
    """Limpia, transforma y agrega las lecturas no procesadas, y calcula métricas."""
    resultado = data_service.procesar(db)
    if resultado is None:
        raise HTTPException(status_code=400, detail="No hay lecturas nuevas para procesar.")
    return RespuestaProcesamiento(**resultado, mensaje="Procesamiento completado correctamente.")


@router.get("/results", response_model=List[Resultado], summary="Consulta de resultados")
def resultados(limite: int = 10, db=Depends(get_db)):
    """Devuelve los resultados procesados (métricas agregadas) para su visualización."""
    return data_service.obtener_resultados(db, limite)
