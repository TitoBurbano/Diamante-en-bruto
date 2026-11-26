"""Traduce los errores de integridad de PostgreSQL a respuestas HTTP claras."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from psycopg import errors


def _respuesta(status: int, mensaje: str, exc) -> JSONResponse:
    # constraint_name es el nombre de la restricción violada (uq_..., fk_..., chk_...)
    return JSONResponse(
        status_code=status,
        content={"detail": mensaje, "restriccion": exc.diag.constraint_name},
    )


def registrar_manejadores(app: FastAPI) -> None:
    @app.exception_handler(errors.UniqueViolation)
    async def valor_duplicado(request: Request, exc: errors.UniqueViolation):
        return _respuesta(409, "Ya existe un registro con ese valor único.", exc)

    @app.exception_handler(errors.ForeignKeyViolation)
    async def llave_foranea(request: Request, exc: errors.ForeignKeyViolation):
        if request.method == "DELETE":
            return _respuesta(
                409, "No se puede eliminar: otros registros dependen de este.", exc
            )
        return _respuesta(
            422, "Referencia inválida: el registro relacionado no existe.", exc
        )

    @app.exception_handler(errors.CheckViolation)
    async def regla_incumplida(request: Request, exc: errors.CheckViolation):
        return _respuesta(422, "Un valor no cumple las reglas de validación.", exc)

    @app.exception_handler(errors.NotNullViolation)
    async def campo_obligatorio(request: Request, exc: errors.NotNullViolation):
        return _respuesta(422, "Falta un campo obligatorio.", exc)