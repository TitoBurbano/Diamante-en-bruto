"""Ventas: consulta, registro (funcionalidad 1) y anulación (funcionalidad 5)."""
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException

from app import db, schemas
from app.reglas import exigir_cliente, exigir_empleado_activo

router = APIRouter(prefix="/ventas", tags=["Ventas"])

DESCUENTO_VIP = Decimal("0.10")  # 10 % para clientes VIP

SELECT_VENTA = """
    SELECT v.id_venta, v.id_cliente, c.nombre AS cliente,
           v.id_empleado, e.nombre AS empleado,
           v.fecha, v.descuento, v.total, v.estado, v.motivo_anulacion
    FROM venta v
    JOIN cliente c  ON c.id_cliente  = v.id_cliente
    JOIN empleado e ON e.id_empleado = v.id_empleado
"""


def _venta_con_detalle(conn, id_venta: int):
    """Devuelve la venta con la lista de joyas vendidas, o None si no existe."""
    venta = conn.execute(SELECT_VENTA + " WHERE v.id_venta = %s", (id_venta,)).fetchone()
    if venta is None:
        return None
    venta["detalle"] = conn.execute(
        """
        SELECT d.id_joya, j.codigo, j.nombre AS joya, d.precio_unitario
        FROM detalle_venta d
        JOIN joya j ON j.id_joya = d.id_joya
        WHERE d.id_venta = %s
        ORDER BY d.id_detalle_venta
        """,
        (id_venta,),
    ).fetchall()
    return venta


@router.get("", response_model=list[schemas.Venta])
def listar_ventas():
    with db.pool.connection() as conn:
        return conn.execute(SELECT_VENTA + " ORDER BY v.id_venta DESC").fetchall()


@router.get("/{id_venta}", response_model=schemas.VentaDetallada)
def obtener_venta(id_venta: int):
    with db.pool.connection() as conn:
        venta = _venta_con_detalle(conn, id_venta)
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta