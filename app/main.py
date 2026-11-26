"""Punto de entrada de la API de la joyería Diamante en Bruto."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db
# ---- IMPORTS DE ROUTERS ----


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.abrir_pool()
    yield
    db.cerrar_pool()


app = FastAPI(
    title="Diamante en Bruto - API de joyería",
    description="Gestión de joyas, clientes, proveedores, ventas, compras y empeños.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---- REGISTRO DE ROUTERS ----


@app.get("/salud", tags=["Sistema"])
def salud():
    """Comprueba que la API está arriba y que la base de datos responde."""
    with db.pool.connection() as conn:
        fila = conn.execute(
            "SELECT current_database() AS base_de_datos, now() AS hora"
        ).fetchone()
    return {"estado": "ok", "base_de_datos": fila["base_de_datos"], "hora": fila["hora"]}