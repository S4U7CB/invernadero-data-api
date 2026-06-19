# -*- coding: utf-8 -*-
"""API de Pipeline de Datos con Machine Learning — Invernadero Inteligente.

Cubre el flujo completo de Big Data: ingestión, procesamiento (ETL) y consulta
de datos ambientales, con análisis mediante Machine Learning.

Ejecutar:
    uvicorn app.main:app --reload

Documentación interactiva (Swagger UI):
    http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.services import ml_service
from app.api import data, ml


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar: crear las tablas y precargar los modelos de ML.
    init_db()
    ml_service.cargar_modelos()
    yield


app = FastAPI(
    title="API de Pipeline de Datos - Invernadero Inteligente",
    description=(
        "API REST para la **ingestión, procesamiento y consulta** de datos ambientales "
        "del invernadero del Colegio Club de Leones, con análisis de **Machine Learning**. "
        "Proyecto de Tecnologías Emergentes I."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def inicio():
    """Información general del API."""
    return {
        "mensaje": "API de Pipeline de Datos - Invernadero Inteligente",
        "documentacion": "/docs",
        "flujo": {
            "1_ingestion": "POST /api/data/ingest  ·  POST /api/data/ingest/csv",
            "2_procesamiento": "POST /api/data/process",
            "3_consulta": "GET /api/data/results",
            "analisis_ml": "POST /api/ml/predecir  ·  POST /api/ml/detectar-anomalia",
        },
    }


@app.get("/salud", tags=["General"])
def salud():
    """Estado del servicio."""
    return {"estado": "ok"}


app.include_router(data.router)
app.include_router(ml.router)
