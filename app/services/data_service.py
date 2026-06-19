# -*- coding: utf-8 -*-
"""Servicio de datos: ingestión, procesamiento (ETL) y consulta de resultados."""
import sqlite3
from datetime import datetime

import pandas as pd

from app.core.config import RANGOS, DATASET_PATH
from app.services import ml_service


# ----------------------------- Validación -----------------------------
def es_valida(temperatura, humedad, luminosidad) -> bool:
    """Valida que los tres valores estén dentro de rangos físicos plausibles."""
    valores = {"temperatura": temperatura, "humedad": humedad, "luminosidad": luminosidad}
    for campo, (lo, hi) in RANGOS.items():
        v = valores[campo]
        if v is None or not (lo <= v <= hi):
            return False
    return True


# ----------------------------- Ingestión -----------------------------
def ingestar(conn: sqlite3.Connection, lecturas) -> tuple:
    """Valida y almacena una lista de lecturas. Devuelve (validos, rechazados)."""
    ahora = datetime.now().isoformat(timespec="seconds")
    validos = rechazados = 0
    for lec in lecturas:
        t = getattr(lec, "temperatura", None)
        h = getattr(lec, "humedad", None)
        l = getattr(lec, "luminosidad", None)
        if es_valida(t, h, l):
            fh = getattr(lec, "fecha_hora", None) or ahora
            conn.execute(
                "INSERT INTO lecturas (fecha_hora, temperatura, humedad, luminosidad, valida, procesada, creado_en) "
                "VALUES (?, ?, ?, ?, 1, 0, ?)",
                (fh, t, h, l, ahora))
            validos += 1
        else:
            rechazados += 1
    conn.commit()
    return validos, rechazados


def cargar_csv(conn: sqlite3.Connection, ruta=None) -> tuple:
    """Carga el dataset CSV completo en la base de datos (ingestión masiva)."""
    df = pd.read_csv(ruta or DATASET_PATH)
    ahora = datetime.now().isoformat(timespec="seconds")
    validos = rechazados = 0
    filas = []
    for _, r in df.iterrows():
        t, h, l = float(r["temperatura"]), float(r["humedad"]), float(r["luminosidad"])
        if es_valida(t, h, l):
            filas.append((str(r["fecha_hora"]), t, h, l, 1, 0, ahora))
            validos += 1
        else:
            rechazados += 1
    conn.executemany(
        "INSERT INTO lecturas (fecha_hora, temperatura, humedad, luminosidad, valida, procesada, creado_en) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", filas)
    conn.commit()
    return validos, rechazados


# ----------------------------- Procesamiento (ETL) -----------------------------
def procesar(conn: sqlite3.Connection):
    """Limpia, transforma y agrega las lecturas no procesadas. Guarda un resultado."""
    rows = conn.execute("SELECT * FROM lecturas WHERE procesada = 0 AND valida = 1").fetchall()
    if not rows:
        return None

    df = pd.DataFrame([dict(r) for r in rows])

    # Limpieza: eliminar nulos y duplicados
    df = df.dropna(subset=["temperatura", "humedad", "luminosidad"]).drop_duplicates(subset=["id"])

    # Agregación / cálculo de métricas
    n = int(len(df))
    temp_prom = float(df["temperatura"].mean())
    temp_min = float(df["temperatura"].min())
    temp_max = float(df["temperatura"].max())
    hum_prom = float(df["humedad"].mean())
    lum_prom = float(df["luminosidad"].mean())

    # Análisis con Machine Learning: conteo de anomalías
    n_anom = ml_service.contar_anomalias(df)

    ahora = datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO resultados (calculado_en, n_registros, temp_promedio, temp_min, temp_max, "
        "hum_promedio, lum_promedio, n_anomalias) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (ahora, n, round(temp_prom, 2), round(temp_min, 2), round(temp_max, 2),
         round(hum_prom, 2), round(lum_prom, 2), n_anom))

    # Marcar las lecturas como procesadas
    ids = [int(i) for i in df["id"].tolist()]
    conn.executemany("UPDATE lecturas SET procesada = 1 WHERE id = ?", [(i,) for i in ids])
    conn.commit()

    return {"registros_procesados": n, "anomalias_detectadas": n_anom,
            "temp_promedio": round(temp_prom, 2)}


# ----------------------------- Consulta -----------------------------
def obtener_resultados(conn: sqlite3.Connection, limite: int = 10) -> list:
    """Devuelve los resultados procesados, del más reciente al más antiguo."""
    rows = conn.execute(
        "SELECT * FROM resultados ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
    return [dict(r) for r in rows]
