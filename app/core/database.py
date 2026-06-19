# -*- coding: utf-8 -*-
"""Conexión e inicialización de la base de datos SQLite."""
import sqlite3

from app.core.config import DB_PATH
from app.models.tablas import TABLAS


def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos con filas tipo diccionario."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea las tablas si no existen."""
    conn = get_connection()
    try:
        for ddl in TABLAS:
            conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()
