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

@router.get("/empenos-activos", response_model=list[schemas.EmpenoActivo])
def reporte_empenos_activos():
    """Empeños vigentes con cliente, joya y días para vencer (vista_empenos_activos).
    Un número negativo en dias_para_vencer indica que el empeño ya venció."""
    with db.pool.connection() as conn:
        return conn.execute(
            "SELECT * FROM vista_empenos_activos ORDER BY dias_para_vencer"
        ).fetchall()