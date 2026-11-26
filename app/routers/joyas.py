"""CRUD de joyas (piezas únicas del inventario)."""
from fastapi import APIRouter, HTTPException, Response

from app import db
from app.schemas import EstadoJoya, Joya, JoyaCrear 

router = APIRouter(prefix="/joyas", tags=["Joyas"])

COLUMNAS = (
    "id_joya, codigo, nombre, id_categoria, id_material, id_proveedor, "
    "peso_gramos, quilates, precio_compra, precio_venta, estado, fecha_ingreso"
)


def _valores(d: JoyaCrear) -> tuple:
    return (
        d.codigo, d.nombre, d.id_categoria, d.id_material, d.id_proveedor,
        d.peso_gramos, d.quilates, d.precio_compra, d.precio_venta,
        d.estado, d.fecha_ingreso,
    )


@router.get("", response_model=list[Joya])
def listar_joyas(estado: EstadoJoya | None = None):
    """Lista las joyas. Con ?estado=DISPONIBLE (u otro estado) filtra por estado."""
    with db.pool.connection() as conn:
        return conn.execute(
            f"SELECT {COLUMNAS} FROM joya "
            f"WHERE (%s::text IS NULL OR estado = %s) ORDER BY id_joya",
            (estado, estado),
        ).fetchall()


@router.get("/{id_joya}", response_model=Joya)
def obtener_joya(id_joya: int):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"SELECT {COLUMNAS} FROM joya WHERE id_joya = %s", (id_joya,)
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Joya no encontrada")
    return fila


@router.post("", response_model=Joya, status_code=201)
def crear_joya(datos: JoyaCrear):
    with db.pool.connection() as conn:
        return conn.execute(
            f"INSERT INTO joya (codigo, nombre, id_categoria, id_material, id_proveedor, "
            f"peso_gramos, quilates, precio_compra, precio_venta, estado, fecha_ingreso) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_DATE)) "
            f"RETURNING {COLUMNAS}",
            _valores(datos),
        ).fetchone()


@router.put("/{id_joya}", response_model=Joya)
def actualizar_joya(id_joya: int, datos: JoyaCrear):
    with db.pool.connection() as conn:
        fila = conn.execute(
            f"UPDATE joya SET codigo = %s, nombre = %s, id_categoria = %s, "
            f"id_material = %s, id_proveedor = %s, peso_gramos = %s, quilates = %s, "
            f"precio_compra = %s, precio_venta = %s, estado = %s, "
            f"fecha_ingreso = COALESCE(%s, fecha_ingreso) "
            f"WHERE id_joya = %s RETURNING {COLUMNAS}",
            _valores(datos) + (id_joya,),
        ).fetchone()
    if fila is None:
        raise HTTPException(status_code=404, detail="Joya no encontrada")
    return fila


@router.delete("/{id_joya}", status_code=204)
def eliminar_joya(id_joya: int):
    with db.pool.connection() as conn:
        cursor = conn.execute("DELETE FROM joya WHERE id_joya = %s", (id_joya,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Joya no encontrada")
    return Response(status_code=204)