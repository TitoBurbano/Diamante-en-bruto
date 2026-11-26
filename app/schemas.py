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



# --------------------------------------------------------------- Proveedores
class ProveedorCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    nit: str = Field(min_length=1, max_length=20)
    telefono: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=150, pattern=EMAIL)
    ciudad: str | None = Field(default=None, max_length=80)


class Proveedor(ProveedorCrear):
    id_proveedor: int    



# ------------------------------------------------------------------ Clientes
class ClienteCrear(BaseModel):
    documento: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=120)
    telefono: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=150, pattern=EMAIL)
    es_vip: bool = False


class Cliente(ClienteCrear):
    id_cliente: int
    fecha_registro: date



# ----------------------------------------------------------------- Empleados
class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    cargo: Literal["VENDEDOR", "ADMINISTRADOR", "AVALUADOR"]
    email: str = Field(max_length=150, pattern=EMAIL)
    activo: bool = True


class Empleado(EmpleadoCrear):
    id_empleado: int



# --------------------------------------------------------------------- Joyas
EstadoJoya = Literal["DISPONIBLE", "VENDIDA", "EMPENADA", "DEVUELTA"]


class JoyaCrear(BaseModel):
    codigo: str = Field(min_length=1, max_length=30)
    nombre: str = Field(min_length=1, max_length=120)
    id_categoria: int
    id_material: int
    id_proveedor: int | None = None
    peso_gramos: float = Field(gt=0)
    quilates: float | None = Field(default=None, gt=0)
    precio_compra: float = Field(ge=0)
    precio_venta: float = Field(ge=0)
    estado: EstadoJoya = "DISPONIBLE"
    fecha_ingreso: date | None = None


class Joya(JoyaCrear):
    id_joya: int
    fecha_ingreso: date



# ------------------------------------------------------------------ Reportes
class InventarioItem(BaseModel):
    id_joya: int
    codigo: str
    joya: str
    categoria: str
    material: str
    pureza: str
    peso_gramos: float
    quilates: float | None
    precio_venta: float
    proveedor: str | None
    fecha_ingreso: date