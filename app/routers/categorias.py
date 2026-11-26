"""CRUD de categorías de joyas."""
from fastapi import APIRouter, HTTPException, Response

from app import db
from app.schemas import Categoria, CategoriaCrear

router = APIRouter(prefix="/categorias", tags=["Categorías"])

COLUMNAS = "id_categoria, nombre, descripcion"


@router.get("", response_model=list[Categoria])
def listar_categorias():
    with db.pool.connection() as conn:
        return conn.execute(
            f"SELECT {COLUMNAS} FROM categoria ORDER BY id_categoria"
        ).fetchall()


@router.get("/{id_categoria}", response_model=Categoria)
def obtener_categoria(id_categoria: int):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"SELECT {COLUMNAS} FROM categoria WHERE id_categoria = %s",
            (id_categoria,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return fila


@router.post("", response_model=Categoria, status_code=201)
def crear_categoria(datos: CategoriaCrear):
    with db.pool.connection() as conn:
        return conn.execute(
            f"INSERT INTO categoria (nombre, descripcion) VALUES (%s, %s) RETURNING {COLUMNAS}",
            (datos.nombre, datos.descripcion),
        ).fetchone()


@router.put("/{id_categoria}", response_model=Categoria)
def actualizar_categoria(id_categoria: int, datos: CategoriaCrear):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"UPDATE categoria SET nombre = %s, descripcion = %s "
            f"WHERE id_categoria = %s RETURNING {COLUMNAS}",
            (datos.nombre, datos.descripcion, id_categoria),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return fila


@router.delete("/{id_categoria}", status_code=204)
def eliminar_categoria(id_categoria: int):
    with db.pool.connection() as conn:
        cursor = conn.execute(
            "DELETE FROM categoria WHERE id_categoria = %s", (id_categoria,)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return Response(status_code=204)