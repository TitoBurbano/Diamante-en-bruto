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



@router.post("", response_model=schemas.VentaDetallada, status_code=201)
def registrar_venta(datos: schemas.VentaCrear):
    """Funcionalidad 1: registrar una venta (transacción atómica).

    Todo ocurre dentro de UNA transacción: la cabecera de la venta, cada joya
    marcada como VENDIDA y cada línea del detalle. Si cualquier joya no está
    disponible, se lanza una excepción y PostgreSQL deshace TODO (ROLLBACK):
    no queda ni la venta ni ninguna joya a medias."""
    if len(set(datos.ids_joyas)) != len(datos.ids_joyas):
        raise HTTPException(status_code=422, detail="La lista de joyas tiene ids repetidos")

    with db.pool.connection() as conn:
        cliente = exigir_cliente(conn, datos.id_cliente)
        exigir_empleado_activo(conn, datos.id_empleado)

        id_venta = conn.execute(
            "INSERT INTO venta (id_cliente, id_empleado, descuento, total) "
            "VALUES (%s, %s, 0, 0) RETURNING id_venta",
            (datos.id_cliente, datos.id_empleado),
        ).fetchone()["id_venta"]

        subtotal = Decimal("0")
        for id_joya in datos.ids_joyas:
            # UPDATE condicional: solo cambia la joya si sigue DISPONIBLE. Es atómico,
            # así dos ventas simultáneas no pueden vender la misma pieza.
            joya = conn.execute(
                "UPDATE joya SET estado = 'VENDIDA' "
                "WHERE id_joya = %s AND estado = 'DISPONIBLE' RETURNING precio_venta",
                (id_joya,),
            ).fetchone()
            if joya is None:
                raise HTTPException(
                    status_code=409,
                    detail=f"La joya {id_joya} no existe o no está disponible; "
                           f"no se registró la venta",
                )
            conn.execute(
                "INSERT INTO detalle_venta (id_venta, id_joya, precio_unitario) "
                "VALUES (%s, %s, %s)",
                (id_venta, id_joya, joya["precio_venta"]),
            )
            subtotal += joya["precio_venta"]

        if cliente["es_vip"]:
            descuento = (subtotal * DESCUENTO_VIP).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            descuento = Decimal("0.00")
        conn.execute(
            "UPDATE venta SET descuento = %s, total = %s WHERE id_venta = %s",
            (descuento, subtotal - descuento, id_venta),
        )
        return _venta_con_detalle(conn, id_venta)