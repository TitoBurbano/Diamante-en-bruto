"""CRUD de empleados."""
from fastapi import APIRouter, HTTPException, Response

from app import db
from app.schemas import Empleado, EmpleadoCrear

router = APIRouter(prefix="/empleados", tags=["Empleados"])

COLUMNAS = "id_empleado, nombre, cargo, email, activo"


def _valores(d: EmpleadoCrear) -> tuple:
    return (d.nombre, d.cargo, d.email, d.activo)


@router.get("", response_model=list[Empleado])
def listar_empleados():
    with db.pool.connection() as conn:
        return conn.execute(
            f"SELECT {COLUMNAS} FROM empleado ORDER BY id_empleado"
        ).fetchall()


@router.get("/{id_empleado}", response_model=Empleado)
def obtener_empleado(id_empleado: int):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"SELECT {COLUMNAS} FROM empleado WHERE id_empleado = %s", (id_empleado,)
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return fila


@router.post("", response_model=Empleado, status_code=201)
def crear_empleado(datos: EmpleadoCrear):
    with db.pool.connection() as conn:
        return conn.execute(
            f"INSERT INTO empleado (nombre, cargo, email, activo) "
            f"VALUES (%s, %s, %s, %s) RETURNING {COLUMNAS}",
            _valores(datos),
        ).fetchone()


@router.put("/{id_empleado}", response_model=Empleado)
def actualizar_empleado(id_empleado: int, datos: EmpleadoCrear):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"UPDATE empleado SET nombre = %s, cargo = %s, email = %s, activo = %s "
            f"WHERE id_empleado = %s RETURNING {COLUMNAS}",
            _valores(datos) + (id_empleado,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return fila


@router.delete("/{id_empleado}", status_code=204)
def eliminar_empleado(id_empleado: int):
    with db.pool.connection() as conn:
        cursor = conn.execute(
            "DELETE FROM empleado WHERE id_empleado = %s", (id_empleado,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return Response(status_code=204)