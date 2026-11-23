from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.errors import Prohibido
from app.models.usuario_model import Usuario
from app.services.vacantes_service import listar_vacantes_admin
from app.utils.respuestas import exito

admin_bp = Blueprint('admin_bp', __name__)


@admin_bp.get("/api/admin/vacantes")
@jwt_required()
def mis_vacantes_endpoint():
    """
    Lista las vacantes del administrador autenticado con su estado.

    Ex. GET /api/admin/vacantes
    Header: Authorization: Bearer <token>
    """
    id_usuario = int(get_jwt_identity())

    usuario = db.session.get(Usuario, id_usuario)
    if not usuario or usuario.perfil != "administrador" or usuario.estatus != "activo":
        raise Prohibido()

    vacantes = listar_vacantes_admin(id_usuario)
    data = [v.to_dict_admin() for v in vacantes]
    activas = sum(1 for v in data if v["activa"])

    return exito(data, "Vacantes del administrador obtenidas.", meta={
        "total": len(data),
        "activas": activas,
        "inactivas": len(data) - activas,
    })