"""Órdenes de compra a proveedores (funcionalidad 2)."""
from fastapi import APIRouter

from app import db, schemas
from app.reglas import exigir_empleado_activo, exigir_proveedor

router = APIRouter(prefix="/ordenes-compra", tags=["Órdenes de compra"])

SELECT_ORDEN = """
    SELECT o.id_orden, o.id_proveedor, p.nombre AS proveedor,
           o.id_empleado, e.nombre AS empleado, o.fecha, o.total
    FROM orden_compra o
    JOIN proveedor p ON p.id_proveedor = o.id_proveedor
    JOIN empleado e  ON e.id_empleado  = o.id_empleado
"""


def _orden_con_detalle(conn, id_orden: int):
    orden = conn.execute(SELECT_ORDEN + " WHERE o.id_orden = %s", (id_orden,)).fetchone()
    orden["detalle"] = conn.execute(
        """
        SELECT d.id_joya, j.codigo, j.nombre AS joya, d.costo
        FROM detalle_orden_compra d
        JOIN joya j ON j.id_joya = d.id_joya
        WHERE d.id_orden = %s
        ORDER BY d.id_detalle_orden
        """,
        (id_orden,),
    ).fetchall()
    return orden


@router.get("", response_model=list[schemas.OrdenCompra])
def listar_ordenes():
    with db.pool.connection() as conn:
        return conn.execute(SELECT_ORDEN + " ORDER BY o.id_orden DESC").fetchall()


@router.post("", response_model=schemas.OrdenCompraDetallada, status_code=201)
def recibir_orden_compra(datos: schemas.OrdenCompraCrear):
    """Funcionalidad 2: recibir mercancía de un proveedor (transacción atómica).

    Crea la orden, da de alta cada joya en el inventario como DISPONIBLE y
    registra su costo. Si una joya falla (por ejemplo, un código repetido),
    PostgreSQL deshace TODA la orden: no queda ninguna joya a medias."""
    with db.pool.connection() as conn:
        exigir_proveedor(conn, datos.id_proveedor)
        exigir_empleado_activo(conn, datos.id_empleado)

        id_orden = conn.execute(
            "INSERT INTO orden_compra (id_proveedor, id_empleado, total) "
            "VALUES (%s, %s, 0) RETURNING id_orden",
            (datos.id_proveedor, datos.id_empleado),
        ).fetchone()["id_orden"]

        for j in datos.joyas:
            id_joya = conn.execute(
                "INSERT INTO joya (codigo, nombre, id_categoria, id_material, id_proveedor, "
                "peso_gramos, quilates, precio_compra, precio_venta, estado) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'DISPONIBLE') RETURNING id_joya",
                (j.codigo, j.nombre, j.id_categoria, j.id_material, datos.id_proveedor,
                 j.peso_gramos, j.quilates, j.costo, j.precio_venta),
            ).fetchone()["id_joya"]
            conn.execute(
                "INSERT INTO detalle_orden_compra (id_orden, id_joya, costo) VALUES (%s, %s, %s)",
                (id_orden, id_joya, j.costo),
            )

        # El total se calcula en SQL con los costos ya guardados (sin errores de redondeo).
        conn.execute(
            "UPDATE orden_compra SET total = ("
            "SELECT COALESCE(SUM(costo), 0) FROM detalle_orden_compra WHERE id_orden = %s"
            ") WHERE id_orden = %s",
            (id_orden, id_orden),
        )
        return _orden_con_detalle(conn, id_orden)