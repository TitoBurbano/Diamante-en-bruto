"""CRUD de clientes."""
from fastapi import APIRouter, HTTPException, Response

from app import db
from app.schemas import Cliente, ClienteCrear

router = APIRouter(prefix="/clientes", tags=["Clientes"])

COLUMNAS = "id_cliente, documento, nombre, telefono, email, es_vip, fecha_registro"


def _valores(d: ClienteCrear) -> tuple:
    return (d.documento, d.nombre, d.telefono, d.email, d.es_vip)


@router.get("", response_model=list[Cliente])
def listar_clientes():
    with db.pool.connection() as conn:
        return conn.execute(
            f"SELECT {COLUMNAS} FROM cliente ORDER BY id_cliente"
        ).fetchall()


@router.get("/{id_cliente}", response_model=Cliente)
def obtener_cliente(id_cliente: int):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"SELECT {COLUMNAS} FROM cliente WHERE id_cliente = %s", (id_cliente,)
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return fila


@router.post("", response_model=Cliente, status_code=201)
def crear_cliente(datos: ClienteCrear):
    with db.pool.connection() as conn:
        return conn.execute(
            f"INSERT INTO cliente (documento, nombre, telefono, email, es_vip) "
            f"VALUES (%s, %s, %s, %s, %s) RETURNING {COLUMNAS}",
            _valores(datos),
        ).fetchone()


@router.put("/{id_cliente}", response_model=Cliente)
def actualizar_cliente(id_cliente: int, datos: ClienteCrear):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"UPDATE cliente SET documento = %s, nombre = %s, telefono = %s, "
            f"email = %s, es_vip = %s WHERE id_cliente = %s RETURNING {COLUMNAS}",
            _valores(datos) + (id_cliente,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return fila


@router.delete("/{id_cliente}", status_code=204)
def eliminar_cliente(id_cliente: int):
    with db.pool.connection() as conn:
        cursor = conn.execute(
            "DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return Response(status_code=204)