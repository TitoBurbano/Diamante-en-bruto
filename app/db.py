"""Conexión a PostgreSQL con un pool de conexiones (psycopg 3, SQL directo, sin ORM)."""
import os

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

load_dotenv()

# open=False: el pool se abre al arrancar la aplicación (ver lifespan en main.py).
# dict_row: cada fila llega como diccionario {columna: valor}.
pool = ConnectionPool(
    conninfo="",
    kwargs={
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "joyeria"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "row_factory": dict_row,
    },
    min_size=1,
    max_size=5,
    open=False,
)


def abrir_pool() -> None:
    """Abre el pool y falla rápido (10 s) si no logra conectarse a la base de datos."""
    pool.open(wait=True, timeout=10)


def cerrar_pool() -> None:
    pool.close()