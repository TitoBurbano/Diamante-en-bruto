"""Punto de entrada de la API de la joyería Diamante en Bruto."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import db
from app.errors import registrar_manejadores
from app.routers import categorias, clientes, empenos, empleados, joyas
from app.routers import materiales, ordenes_compra, proveedores, reportes, ventas

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


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

for modulo in (categorias, materiales, proveedores, clientes, empleados, joyas,
               reportes, ventas, ordenes_compra, empenos):
    app.include_router(modulo.router)

# Interfaz web: archivos estáticos en /static y la página principal en /
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/salud", tags=["Sistema"])
def salud():
    """Comprueba que la API está arriba y que la base de datos responde."""
    with db.pool.connection() as conn:
        fila = conn.execute(
            "SELECT current_database() AS base_de_datos, now() AS hora"
        ).fetchone()
    return {"estado": "ok", "base_de_datos": fila["base_de_datos"], "hora": fila["hora"]}