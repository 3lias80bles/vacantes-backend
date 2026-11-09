"""
Funciones de utilidad para la generación de respuestas JSON en la API.
"""

from flask import jsonify

# Para solicitudes exitosas
def exito(data=None, mensaje="Operación exitosa.", codigo=200, meta=None):
    cuerpo = {"status": "success", "mensaje": mensaje, "data": data}
    if meta is not None:
        cuerpo["meta"] = meta
    return jsonify(cuerpo), codigo

# Para solicitudes con error
def error(mensaje, codigo=400, errores=None):
    return jsonify({"status": "error", "mensaje": mensaje, "errores": errores or []}), codigo