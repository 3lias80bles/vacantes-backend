import re

from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from app.errors import ValidacionError
from app.models.usuario_model import Usuario

auth_bp = Blueprint('auth_bp', __name__)

_EMAIL_RE = re.compile(
    r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}"
)


def _error_validacion(campo, mensaje):
    return ValidacionError(errores=[{"campo": campo, "mensaje": mensaje}])


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            raise _error_validacion("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

        email = data.get('email')
        if not isinstance(email, str) or not email.strip():
            raise _error_validacion("email", "El correo electrónico es obligatorio.")
        email = email.strip()
        parte_local = email.split("@", 1)[0]
        if (
            len(email) > 100
            or not _EMAIL_RE.fullmatch(email)
            or parte_local.startswith(".")
            or parte_local.endswith(".")
            or ".." in parte_local
        ):
            raise _error_validacion("email", "Debe tener un formato de correo electrónico válido.")

        password = data.get('password')
        if not isinstance(password, str) or not password:
            raise _error_validacion("password", "La contraseña es obligatoria.")

        # Buscar al usuario por correo electrónico
        usuario = Usuario.query.filter_by(email=email).first()

        # Validar si existe el usuario, si la contraseña coincide y si su estatus es activo
        if not usuario or not usuario.check_password(password) or usuario.estatus != 'activo' or usuario.perfil != 'administrador':
            return jsonify({
                "status": "error",
                "mensaje": "Credenciales incorrectas "
            }), 401

        #Genera el token de acceso JWT
        access_token = create_access_token(identity=str(usuario.id))

        # Responde sin exponer las contraseñas ni los hashes de las contraseñas 
        return jsonify({
            "status": "success",
            "mensaje": "Autenticación exitosa.",
            "access_token": access_token,
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "perfil": usuario.perfil
            }
        }), 200

    except ValidacionError:
        raise
    except Exception:
        current_app.logger.exception("Error interno durante la autenticación.")
        return jsonify({
            "status": "error",
            "mensaje": "Ocurrió un error interno. Intenta más tarde."
        }), 500

    @auth_bp.route('/api/auth/perfil', methods=['GET'])
    @jwt_required()
    def perfil_protegido():
        usuario_id = get_jwt_identity()
        return jsonify({
            "status": "success",
            "mensaje": "Acceso a la ruta protegida exitoso.",
            "usuario_id": usuario_id
        }), 200
    