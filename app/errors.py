"""
Módulo de errores personalizados para la API.

-- Como se usa:

raise NoEncontrado("Vacante no encontrada.")
raise ValidacionError(errores=[
    {"campo": "page", "mensaje": "Debe ser un número entero mayor o igual a 1."}
])
raise NoAutorizado()   # usa el mensaje por defecto

"""


class ApiError(Exception):
    codigo = 400
    mensaje = "Error en la solicitud."

    def __init__(self, mensaje=None, errores=None):
        super().__init__(mensaje or self.mensaje)
        if mensaje:
            self.mensaje = mensaje
        self.errores = errores or []


class ValidacionError(ApiError):
    codigo = 400
    mensaje = "Los datos enviados no son válidos."


class NoAutorizado(ApiError):
    codigo = 401
    mensaje = "Se requiere autenticación."


class Prohibido(ApiError):
    codigo = 403
    mensaje = "No tienes permiso para realizar esta operación."


class NoEncontrado(ApiError):
    codigo = 404
    mensaje = "El recurso solicitado no existe."