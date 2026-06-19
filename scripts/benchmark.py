# -*- coding: utf-8 -*-
"""Mide las métricas de rendimiento y calidad del pipeline.

Uso:  python scripts/benchmark.py
"""
import sys
import time
import types
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app.core import config
from app.core.database import init_db, get_connection
from app.services import data_service, ml_service


def resumen(tiempos):
    ordenados = sorted(tiempos)
    p95 = ordenados[max(0, int(0.95 * len(ordenados)) - 1)]
    return statistics.mean(tiempos), p95, max(tiempos)


if config.DB_PATH.exists():
    config.DB_PATH.unlink()

ml_service.cargar_modelos()  # precarga (calentamiento)
init_db()
conn = get_connection()
errores = 0


def L(t, h, l):
    return types.SimpleNamespace(temperatura=t, humedad=h, luminosidad=l, fecha_hora=None)


# 1) Ingestión: tiempo por petición
t_ingest = []
for i in range(300):
    try:
        t0 = time.perf_counter()
        data_service.ingestar(conn, [L(18.0 + (i % 12), 60.0, 500.0)])
        t_ingest.append((time.perf_counter() - t0) * 1000)
    except Exception:
        errores += 1

# 2) Validación: tasa de registros válidos sobre el dataset
df = pd.read_csv(config.DATASET_PATH)
validos = sum(1 for _, r in df.iterrows()
              if data_service.es_valida(float(r["temperatura"]), float(r["humedad"]), float(r["luminosidad"])))
tasa_validacion = validos / len(df) * 100

# 3) Procesamiento (ETL): tiempo y tasa de procesamiento
data_service.cargar_csv(conn)
pendientes = conn.execute("SELECT COUNT(*) FROM lecturas WHERE procesada=0 AND valida=1").fetchone()[0]
t0 = time.perf_counter()
res = data_service.procesar(conn)
t_process = (time.perf_counter() - t0) * 1000
tasa_proceso = res["registros_procesados"] / pendientes * 100

# 4) Consulta de resultados: tiempo por petición
t_results = []
for _ in range(200):
    t0 = time.perf_counter()
    data_service.obtener_resultados(conn, 10)
    t_results.append((time.perf_counter() - t0) * 1000)

# 5) Inferencia de ML: tiempo por petición
t_ml = []
for _ in range(300):
    t0 = time.perf_counter()
    ml_service.predecir_temperatura(14, 22.0, 55.0, 800.0)
    t_ml.append((time.perf_counter() - t0) * 1000)

conn.close()

total_ops = len(t_ingest) + len(t_results) + len(t_ml) + 1
tasa_error = errores / total_ops * 100

print("=== MÉTRICAS DE RENDIMIENTO (ms por petición) ===")
for nombre, ts in [("POST /api/data/ingest", t_ingest), ("GET  /api/data/results", t_results),
                   ("POST /api/ml/predecir ", t_ml)]:
    m, p95, mx = resumen(ts)
    print(f"{nombre}:  promedio={m:.2f}  p95={p95:.2f}  max={mx:.2f}")
print(f"POST /api/data/process:  {t_process:.2f} ms ({res['registros_procesados']} registros)")
print()
print("=== MÉTRICAS DE CALIDAD ===")
print(f"Validación de datos: {tasa_validacion:.2f} % de registros válidos")
print(f"Procesamiento correcto: {tasa_proceso:.2f} % de registros procesados")
print(f"Tasa de error: {tasa_error:.2f} %")
print(f"Anomalías detectadas en el procesamiento: {res['anomalias_detectadas']}")
