"""Empeños: registro (funcionalidad 3), saldo (4) y vencimiento (6)."""
from decimal import ROUND_HALF_UP, Decimal

from fastapi import APIRouter, HTTPException

from app import db, schemas
from app.reglas import exigir_cliente, exigir_empleado_activo

router = APIRouter(prefix="/empenos", tags=["Empeños"])

PRESTAMO_MAXIMO = Decimal("0.60")  # el préstamo no puede superar el 60 % del avalúo

SELECT_EMPENO = """
    SELECT e.id_empeno, e.id_cliente, c.nombre AS cliente,
           e.id_joya, j.codigo AS codigo_joya, j.nombre AS joya,
           e.id_empleado, em.nombre AS empleado,
           e.monto_prestamo, e.tasa_interes, e.fecha_inicio, e.fecha_vencimiento,
           e.estado, e.fecha_cierre, e.monto_pagado
    FROM empeno e
    JOIN cliente c   ON c.id_cliente  = e.id_cliente
    JOIN joya j      ON j.id_joya     = e.id_joya
    JOIN empleado em ON em.id_empleado = e.id_empleado
"""


def _empeno(conn, id_empeno: int):
    return conn.execute(SELECT_EMPENO + " WHERE e.id_empeno = %s", (id_empeno,)).fetchone()


@router.get("", response_model=list[schemas.Empeno])
def listar_empenos(estado: schemas.EstadoEmpeno | None = None):
    """Lista los empeños. Con ?estado=ACTIVO (u otro estado) filtra por estado."""
    with db.pool.connection() as conn:
        return conn.execute(
            SELECT_EMPENO + " WHERE (%s::text IS NULL OR e.estado = %s) ORDER BY e.id_empeno",
            (estado, estado),
        ).fetchall()


@router.post("", response_model=schemas.Empeno, status_code=201)
def registrar_empeno(datos: schemas.EmpenoCrear):
    """Funcionalidad 3: registrar un empeño (transacción atómica).

    Da de alta la joya que deja el cliente en garantía (estado EMPENADA) y
    registra el préstamo. Reglas: el monto no puede superar el 60 % del precio
    de venta de la joya y el vencimiento debe ser posterior a hoy."""
    with db.pool.connection() as conn:
        exigir_cliente(conn, datos.id_cliente)
        exigir_empleado_activo(conn, datos.id_empleado)

        monto = Decimal(str(datos.monto_prestamo))
        maximo = (Decimal(str(datos.joya.precio_venta)) * PRESTAMO_MAXIMO).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if monto > maximo:
            raise HTTPException(
                status_code=409,
                detail=f"El préstamo máximo para esta joya es {maximo} (60 % de su precio de venta)",
            )
        hoy = conn.execute("SELECT CURRENT_DATE AS hoy").fetchone()["hoy"]
        if datos.fecha_vencimiento <= hoy:
            raise HTTPException(
                status_code=422, detail="La fecha de vencimiento debe ser posterior a hoy"
            )

        j = datos.joya
        id_joya = conn.execute(
            "INSERT INTO joya (codigo, nombre, id_categoria, id_material, id_proveedor, "
            "peso_gramos, quilates, precio_compra, precio_venta, estado) "
            "VALUES (%s, %s, %s, %s, NULL, %s, %s, %s, %s, 'EMPENADA') RETURNING id_joya",
            (j.codigo, j.nombre, j.id_categoria, j.id_material,
             j.peso_gramos, j.quilates, monto, j.precio_venta),
        ).fetchone()["id_joya"]
        id_empeno = conn.execute(
            "INSERT INTO empeno (id_cliente, id_joya, id_empleado, monto_prestamo, "
            "tasa_interes, fecha_vencimiento) VALUES (%s, %s, %s, %s, %s, %s) "
            "RETURNING id_empeno",
            (datos.id_cliente, id_joya, datos.id_empleado, monto,
             datos.tasa_interes, datos.fecha_vencimiento),
        ).fetchone()["id_empeno"]
        return _empeno(conn, id_empeno)