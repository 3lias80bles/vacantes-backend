from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.errors import NoEncontrado, Prohibido, ValidacionError
from app.models.usuario_model import Usuario

from app.services.vacantes_service import eliminar_vacante
from app.services.vacantes_service import buscar_vacantes
from app.services.vacantes_service import crear_vacante
from app.services.vacantes_service import listar_vacantes
from app.services.vacantes_service import buscar_vacantes, obtener_vacante_por_id
from app.services.vacantes_service import filtrar_vacantes

from app.utils.respuestas import exito

# Definición del Blueprint (esto es lo que está buscando __init__.py)
vacantes_bp = Blueprint('vacantes_bp', __name__)

@vacantes_bp.post("/api/vacantes")
@jwt_required()
def crear_vacante_endpoint():
    """
    Registra una nueva vacante.
    Solo accesible para los usuarios autenticados con el perfinl de "Administrador"y el estatus "Activo".
    """
    usuario_id = get_jwt_identity()
    usuario = db.session.get(Usuario, int(usuario_id))

    perfil = (usuario.perfil or "").strip().lower() if usuario else ""
    estatus = (usuario.estatus or "").strip().lower() if usuario else ""

    if not usuario or estatus != "activo" or perfil != "administrador":
        return {"status": "error", "mensaje": "No autorizado para crear vacantes."}, 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidacionError(errores=[{"campo": "body", "mensaje": "El cuerpo de la solicitud debe ser un JSON válido."}])

    try: 
        vacante = crear_vacante(data= data, administrador_id=usuario.id)
    except Exception:
        db.session.rollback()
        raise
    return exito(vacante.to_dict(completo=True), "Vacante creada exitosamente.", 201)

"""
    Lista de vacantes con filtros opcionaes: 
    - categoria
    - ubicacion
    - tipo_empleo
"""
@vacantes_bp.route('/api/vacantes', methods=['GET'])
def obtener_vacantes():
    vacantes = filtrar_vacantes(
        categoria=request.args.get("categoria"),
        ubicacion=request.args.get("ubicacion"),
        tipo_empleo=request.args.get("tipo_empleo"),
    )
    data = [v.to_dict() for v in vacantes]
    return exito(data, "Vacantes obtenidas.", meta={"total": len(data)})

@vacantes_bp.get("/api/vacantes/buscar")
def buscar_vacantes_endpoint():
    """
    Busca vacantes mediante el parámetro de consulta 'q'.

    Ejemplo:
    GET /vacantes/buscar?q=Python
    """
    palabra_clave = request.args.get("q", "").strip()

    if not palabra_clave:
        raise ValidacionError(errores=[
            {"campo": "q", "mensaje": "El parámetro 'q' es obligatorio."}
        ])
    if len(palabra_clave) > 100:
        raise ValidacionError(errores=[
            {"campo": "q", "mensaje": "La búsqueda no puede superar los 100 caracteres."}
        ])

    vacantes = buscar_vacantes(palabra_clave)
    data = [v.to_dict() for v in vacantes]
    return exito(data, "Búsqueda realizada.", meta={"total": len(data)})
    
@vacantes_bp.get("/api/vacantes/listar")
def listar_vacantes_endpoint():
    """
    Lista las vacantes disponibles con paginación.

    Ejemplos:
        GET /vacantes/
        GET /vacantes/listar?page=2
    """
    error_page = ValidacionError(errores=[
        {"campo": "page", "mensaje": "Debe ser un número entero mayor o igual a 1."}
    ])

    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        raise error_page

    if page < 1:
        raise error_page

    paginacion = listar_vacantes(page=page)
    data = [v.to_dict() for v in paginacion.items]
    return exito(data, "Vacantes obtenidas.", meta={
        "pagina_actual": paginacion.page,
        "por_pagina": paginacion.per_page,
        "total_resultados": paginacion.total,
        "total_paginas": paginacion.pages,
        "hay_pagina_anterior": paginacion.has_prev,
        "hay_pagina_siguiente": paginacion.has_next,
    })

@vacantes_bp.get("/api/vacantes/<int:vacante_id>")
def obtener_vacante_endpoint(vacante_id):
    """
    Consulta el detalle completo de una vacante por su identificador.

    Ex. GET /api/vacantes/6
    """

    vacante = obtener_vacante_por_id(vacante_id)

    # Una vacante desactivada responde igual que una inexistente.
    if vacante is None:
        raise NoEncontrado("Vacante no encontrada.")

    return exito(vacante.to_dict(completo=True), "Vacante obtenida.") 

@vacantes_bp.delete("/api/vacantes/<int:vacante_id>")
@jwt_required()
def eliminar_vacante_endpoint(vacante_id):
    """
    Elimina una vacante del administrador autenticado (borrado lógico).

    Ex. DELETE /api/vacantes/5
    Header: Authorization: Bearer <token>
    """
    usuario = db.session.get(Usuario, int(get_jwt_identity()))
    if not usuario or usuario.perfil != "administrador" or usuario.estatus != "activo":
        raise Prohibido()

    vacante = eliminar_vacante(vacante_id, usuario.id)
    return exito(
        {"id": vacante.id, "activa": vacante.activa},
        "Vacante eliminada correctamente.",
    )