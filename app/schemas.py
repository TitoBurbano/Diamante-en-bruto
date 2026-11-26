"""Modelos Pydantic: validan lo que entra a la API y describen lo que sale."""
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

EMAIL = r"^[^@\s]+@[^@\s]+$"


# ---------------------------------------------------------------- Categorías
class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=60)
    descripcion: str | None = None


class Categoria(CategoriaCrear):
    id_categoria: int


# ---------------------------------------------------------------- Materiales
class Material(BaseModel):
    id_material: int
    nombre: str
    pureza: str