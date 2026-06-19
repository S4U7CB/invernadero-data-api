# -*- coding: utf-8 -*-
"""Entrena y evalúa los modelos, y guarda los .joblib + metrics.json.

Uso:  python scripts/entrenar_modelos.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             precision_score, recall_score, f1_score)

from app.core.config import DATASET_PATH, SAVED_MODELS_DIR

df = pd.read_csv(DATASET_PATH, parse_dates=["fecha_hora"])
hod = df["fecha_hora"].dt.hour.values
df["hora_sin"] = np.sin(2 * np.pi * hod / 24)
df["hora_cos"] = np.cos(2 * np.pi * hod / 24)

# --- Modelos de predicción de temperatura (holdout 80/20) ---
limpio = df[df["is_anomaly"] == 0].reset_index(drop=True)
cols = ["hora_sin", "hora_cos", "temperatura", "humedad", "luminosidad"]
X = limpio[cols].values[:-1]
y = limpio["temperatura"].values[1:]
corte = int(0.8 * len(X))


def evaluar(modelo):
    p = modelo.predict(X[corte:])
    return {
        "MAE": round(mean_absolute_error(y[corte:], p), 3),
        "RMSE": round(mean_squared_error(y[corte:], p) ** 0.5, 3),
        "R2": round(r2_score(y[corte:], p), 3),
    }


rf_eval = evaluar(RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42).fit(X[:corte], y[:corte]))
gb_eval = evaluar(GradientBoostingRegressor(random_state=42).fit(X[:corte], y[:corte]))

# --- Modelo de detección de anomalías (evaluado contra is_anomaly) ---
Xa = df[["temperatura", "humedad", "luminosidad", "hora_sin", "hora_cos"]].values
iso = IsolationForest(contamination=0.02, random_state=42).fit(Xa)
pred = (iso.predict(Xa) == -1).astype(int)
verdad = df["is_anomaly"].values
iso_eval = {
    "precision": round(precision_score(verdad, pred), 3),
    "recall": round(recall_score(verdad, pred), 3),
    "F1": round(f1_score(verdad, pred), 3),
}

# --- Reentrenar con todos los datos limpios y guardar los modelos finales ---
rf_final = RandomForestRegressor(n_estimators=100, max_depth=16, random_state=42).fit(X, y)
gb_final = GradientBoostingRegressor(random_state=42).fit(X, y)

SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(rf_final, SAVED_MODELS_DIR / "randomforest_model.joblib")
joblib.dump(gb_final, SAVED_MODELS_DIR / "gradientboosting_model.joblib")
joblib.dump(iso, SAVED_MODELS_DIR / "isolationforest_model.joblib")

metrics = {
    "randomforest": rf_eval,
    "gradientboosting": gb_eval,
    "isolationforest": iso_eval,
    "nota": "Métricas de evaluación de los modelos (holdout 80/20, semilla 42).",
}
with open(SAVED_MODELS_DIR / "metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print("Modelos y metrics.json generados en", SAVED_MODELS_DIR)
print(json.dumps(metrics, indent=2, ensure_ascii=False))
