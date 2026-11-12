"""
Módulo de errores personalizados para la API.

-- Como se usa:

raise NoEncontrado("Vacante no encontrada.")
raise ValidacionError(errores=[
    {"campo": "page", "mensaje": "Debe ser un número entero mayor o igual a 1."}
])
raise NoAutorizado()   # usa el mensaje por defecto

"""
from flask import current_app
from werkzeug.exceptions import HTTPException

from app.utils.respuestas import error

# Las clases de error personalizadas heredan de ApiError, que a su vez hereda de Exception.
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

# Mensajes de error para códigos HTTP
MENSAJES_HTTP = {
    400: "La solicitud no es válida.",
    401: "Se requiere autenticación.",
    403: "No tienes permiso para realizar esta operación.",
    404: "El recurso solicitado no existe.",
    405: "Método no permitido para esta ruta.",
}


# Esta función registra los manejadores de errores en la aplicación Flask.
def registrar_manejadores(app):

    @app.errorhandler(ApiError)
    def manejar_api_error(e):
        return error(e.mensaje, e.codigo, e.errores)

    @app.errorhandler(HTTPException)
    def manejar_http(e):
        mensaje = MENSAJES_HTTP.get(e.code, "Error en la solicitud.")
        return error(mensaje, e.code)

    @app.errorhandler(Exception)
    def manejar_inesperado(e):
        current_app.logger.exception("Error interno no controlado.")
        return error("Ocurrió un error interno. Intenta más tarde.", 500)