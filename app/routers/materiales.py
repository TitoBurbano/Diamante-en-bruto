"""Listado de materiales (solo lectura; alimenta los formularios)."""
from fastapi import APIRouter

from app import db
from app.schemas import Material

router = APIRouter(prefix="/materiales", tags=["Materiales"])


@router.get("", response_model=list[Material])
def listar_materiales():
    with db.pool.connection() as conn:
        return conn.execute(
            "SELECT id_material, nombre, pureza FROM material ORDER BY id_material"
        ).fetchall()