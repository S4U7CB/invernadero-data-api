# -*- coding: utf-8 -*-
"""Definición de las tablas de la base de datos (SQLite)."""

SQL_LECTURAS = """
CREATE TABLE IF NOT EXISTS lecturas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora  TEXT,
    temperatura REAL    NOT NULL,
    humedad     REAL    NOT NULL,
    luminosidad REAL    NOT NULL,
    valida      INTEGER NOT NULL DEFAULT 1,
    procesada   INTEGER NOT NULL DEFAULT 0,
    creado_en   TEXT    NOT NULL
);
"""

SQL_RESULTADOS = """
CREATE TABLE IF NOT EXISTS resultados (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    calculado_en  TEXT    NOT NULL,
    n_registros   INTEGER NOT NULL,
    temp_promedio REAL,
    temp_min      REAL,
    temp_max      REAL,
    hum_promedio  REAL,
    lum_promedio  REAL,
    n_anomalias   INTEGER
);
"""

TABLAS = [SQL_LECTURAS, SQL_RESULTADOS]
