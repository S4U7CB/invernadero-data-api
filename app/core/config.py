# -*- coding: utf-8 -*-
"""Configuración central del API."""
from pathlib import Path

# Raíz del proyecto (invernadero-data-api/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / "invernadero.db"
DATASET_PATH = BASE_DIR / "data" / "dataset_invernadero_simulado.csv"
SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "models" / "saved_models"

# Rangos físicos válidos para la validación de datos
RANGOS = {
    "temperatura": (-20.0, 50.0),   # °C
    "humedad": (0.0, 100.0),        # %
    "luminosidad": (0.0, 2000.0),   # lux
}

UMBRAL_HELADA = 2.0  # °C: por debajo de este valor se emite alerta de helada
