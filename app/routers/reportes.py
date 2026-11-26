"""Reportes: consumen las vistas (R4) y las subconsultas (R3)."""
from fastapi import APIRouter

from app import db, schemas

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/inventario", response_model=list[schemas.InventarioItem])
def reporte_inventario():
    """Joyas a la venta con su categoría, material y proveedor (vista_inventario_disponible)."""
    with db.pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM vista_inventario_disponible ORDER BY id_joya"
        ).fetchall()