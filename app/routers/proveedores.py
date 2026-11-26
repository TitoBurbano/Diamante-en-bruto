"""CRUD de proveedores."""
from fastapi import APIRouter, HTTPException, Response

from app import db
from app.schemas import Proveedor, ProveedorCrear

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

COLUMNAS = "id_proveedor, nombre, nit, telefono, email, ciudad"


def _valores(d: ProveedorCrear) -> tuple:
    return (d.nombre, d.nit, d.telefono, d.email, d.ciudad)


@router.get("", response_model=list[Proveedor])
def listar_proveedores():
    with db.pool.connection() as conn:
        return conn.execute(
            f"SELECT {COLUMNAS} FROM proveedor ORDER BY id_proveedor"
        ).fetchall()


@router.get("/{id_proveedor}", response_model=Proveedor)
def obtener_proveedor(id_proveedor: int):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"SELECT {COLUMNAS} FROM proveedor WHERE id_proveedor = %s",
            (id_proveedor,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return fila


@router.post("", response_model=Proveedor, status_code=201)
def crear_proveedor(datos: ProveedorCrear):
    with db.pool.connection() as conn:
        return conn.execute(
            f"INSERT INTO proveedor (nombre, nit, telefono, email, ciudad) "
            f"VALUES (%s, %s, %s, %s, %s) RETURNING {COLUMNAS}",
            _valores(datos),
        ).fetchone()


@router.put("/{id_proveedor}", response_model=Proveedor)
def actualizar_proveedor(id_proveedor: int, datos: ProveedorCrear):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"UPDATE proveedor SET nombre = %s, nit = %s, telefono = %s, "
            f"email = %s, ciudad = %s WHERE id_proveedor = %s RETURNING {COLUMNAS}",
            _valores(datos) + (id_proveedor,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return fila


@router.delete("/{id_proveedor}", status_code=204)
def eliminar_proveedor(id_proveedor: int):
    with db.pool.connection() as conn:
        cursor = conn.execute(
            "DELETE FROM proveedor WHERE id_proveedor = %s", (id_proveedor,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return Response(status_code=204)