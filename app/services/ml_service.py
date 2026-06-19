# -*- coding: utf-8 -*-
"""Servicio de Machine Learning: carga/entrena los modelos y realiza inferencias."""
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest

from app.core.config import SAVED_MODELS_DIR, DATASET_PATH, UMBRAL_HELADA

_modelos = {}
COLS_TEMP = ["hora_sin", "hora_cos", "temperatura", "humedad", "luminosidad"]


def _features_hora(hora):
    ang = 2 * np.pi * np.asarray(hora, dtype=float) / 24.0
    return np.sin(ang), np.cos(ang)


def _entrenar_y_guardar():
    """Entrena los tres modelos desde el dataset y los guarda en disco."""
    df = pd.read_csv(DATASET_PATH, parse_dates=["fecha_hora"])
    hod = df["fecha_hora"].dt.hour.values
    df["hora_sin"], df["hora_cos"] = _features_hora(hod)

    limpio = df[df["is_anomaly"] == 0].reset_index(drop=True)
    X = limpio[COLS_TEMP].values[:-1]
    y = limpio["temperatura"].values[1:]
    rf = RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42).fit(X, y)
    gb = GradientBoostingRegressor(random_state=42).fit(X, y)

    Xa = df[["temperatura", "humedad", "luminosidad", "hora_sin", "hora_cos"]].values
    iso = IsolationForest(contamination=0.02, random_state=42).fit(Xa)

    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, SAVED_MODELS_DIR / "randomforest_model.joblib")
    joblib.dump(gb, SAVED_MODELS_DIR / "gradientboosting_model.joblib")
    joblib.dump(iso, SAVED_MODELS_DIR / "isolationforest_model.joblib")
    return rf, gb, iso


def cargar_modelos():
    """Carga los modelos guardados; si no existen o fallan, los entrena."""
    global _modelos
    if _modelos:
        return _modelos
    try:
        rf = joblib.load(SAVED_MODELS_DIR / "randomforest_model.joblib")
        gb = joblib.load(SAVED_MODELS_DIR / "gradientboosting_model.joblib")
        iso = joblib.load(SAVED_MODELS_DIR / "isolationforest_model.joblib")
    except Exception:
        rf, gb, iso = _entrenar_y_guardar()
    _modelos = {"rf": rf, "gb": gb, "iso": iso}
    return _modelos


def predecir_temperatura(hora, temperatura, humedad, luminosidad):
    """Predice la temperatura de la próxima hora a partir de una lectura."""
    m = cargar_modelos()
    hs, hc = _features_hora(hora)
    X = [[hs, hc, temperatura, humedad, luminosidad]]
    pred = float(m["rf"].predict(X)[0])
    return round(pred, 2), bool(pred < UMBRAL_HELADA)


def detectar_anomalia(hora, temperatura, humedad, luminosidad):
    """Indica si una lectura es anómala (posible fallo de sensor)."""
    m = cargar_modelos()
    hs, hc = _features_hora(hora)
    X = [[temperatura, humedad, luminosidad, hs, hc]]
    es = bool(m["iso"].predict(X)[0] == -1)
    score = float(m["iso"].score_samples(X)[0])
    return es, round(score, 4)


def contar_anomalias(df: pd.DataFrame) -> int:
    """Cuenta cuántas lecturas de un DataFrame son anómalas."""
    m = cargar_modelos()
    fh = pd.to_datetime(df["fecha_hora"], errors="coerce")
    hod = fh.dt.hour.fillna(12).values
    hs, hc = _features_hora(hod)
    X = np.column_stack([df["temperatura"].values, df["humedad"].values,
                         df["luminosidad"].values, hs, hc])
    preds = m["iso"].predict(X)
    return int((preds == -1).sum())
