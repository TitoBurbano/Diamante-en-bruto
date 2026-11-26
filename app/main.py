"""Punto de entrada de la API de la joyería Diamante en Bruto."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import db

# ---- IMPORTS DE ROUTERS ----
from app.errors import registrar_manejadores
from app.routers import categorias
from app.routers import materiales
from app.routers import proveedores
from app.routers import clientes
from app.routers import empleados
from app.routers import joyas
from app.routers import reportes
from app.routers import ventas

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
registrar_manejadores(app)
# ---- REGISTRO DE ROUTERS ----
app.include_router(categorias.router)
app.include_router(materiales.router)
app.include_router(proveedores.router)
app.include_router(clientes.router)
app.include_router(empleados.router)
app.include_router(joyas.router)
app.include_router(reportes.router)
app.include_router(ventas.router)

@app.get("/salud", tags=["Sistema"])
def salud():
    """Comprueba que la API está arriba y que la base de datos responde."""
    with db.pool.connection() as conn:
        fila = conn.execute(
            "SELECT current_database() AS base_de_datos, now() AS hora"
        ).fetchone()
    return {"estado": "ok", "base_de_datos": fila["base_de_datos"], "hora": fila["hora"]}