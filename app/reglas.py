"""Validaciones de negocio compartidas por las funcionalidades (ventas, compras, empeños)."""
from fastapi import HTTPException


def exigir_cliente(conn, id_cliente: int) -> dict:
    """Devuelve el cliente o responde 404 si no existe."""
    fila = conn.execute(
        "SELECT id_cliente, es_vip FROM cliente WHERE id_cliente = %s", (id_cliente,)
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return fila


def exigir_proveedor(conn, id_proveedor: int) -> None:
    """Responde 404 si el proveedor no existe."""
    fila = conn.execute(
        "SELECT 1 FROM proveedor WHERE id_proveedor = %s", (id_proveedor,)
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")


def exigir_empleado_activo(conn, id_empleado: int) -> None:
    """Responde 404 si el empleado no existe y 409 si está inactivo."""
    fila = conn.execute(
        "SELECT activo FROM empleado WHERE id_empleado = %s", (id_empleado,)
    ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if not fila["activo"]:
        raise HTTPException(
            status_code=409,
            detail="El empleado está inactivo y no puede registrar operaciones",
        )