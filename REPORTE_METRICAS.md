# Reporte de Métricas — API de Pipeline de Datos

**Proyecto:** Sistema de Monitoreo Ambiental Inteligente para Invernadero
**Métricas obtenidas con:** `python scripts/benchmark.py` (dataset de 1 440 registros, semilla fija)

---

## 1. Rendimiento (tiempo de respuesta)

Todos los endpoints responden **muy por debajo del objetivo de 200 ms**.

| Endpoint | Promedio | p95 | Máximo |
|---|---|---|---|
| `POST /api/data/ingest` | 2,6 ms | 3,5 ms | 4,7 ms |
| `POST /api/data/process` | 54,7 ms (1 728 registros) | — | — |
| `GET /api/data/results` | < 0,1 ms | < 0,1 ms | 0,2 ms |
| `POST /api/ml/predecir` | 7,7 ms | 9,4 ms | 14,3 ms |

**Resultado:** ✓ Respuesta < 200 ms de forma constante en todos los endpoints.

---

## 2. Calidad de datos

| Métrica | Resultado | Objetivo | Estado |
|---|---|---|---|
| Validación de datos | 99,17 % válidos | > 98 % | ✓ |
| Procesamiento correcto | 100 % procesados | > 98 % | ✓ |
| Tasa de error | 0 % | < 1 % | ✓ |

Anomalías detectadas durante el procesamiento: **48**.

---

## 3. Modelos de Machine Learning (`metrics.json`)

| Modelo | Tarea | Métricas |
|---|---|---|
| Random Forest | Predicción de temperatura | MAE = 1,27 °C · RMSE = 1,59 °C · R² = 0,931 |
| Gradient Boosting | Predicción de temperatura | MAE = 1,18 °C · RMSE = 1,47 °C · R² = 0,941 |
| Isolation Forest | Detección de anomalías | Precisión = 0,69 · Recall = 0,71 · F1 = 0,70 |

---

## Metodología

Las mediciones se realizaron sobre la lógica de cada endpoint (ingestión, validación,
procesamiento ETL, consulta e inferencia de los modelos). La capa HTTP de FastAPI añade
un sobrecosto mínimo (pocos milisegundos), por lo que el tiempo total se mantiene muy por
debajo de los 200 ms. Todas las métricas son **reproducibles** ejecutando
`python scripts/benchmark.py`.
