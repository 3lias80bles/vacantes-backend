from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.usuario_model import Usuario

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Buscar al usuario por correo electrónico
        usuario = Usuario.query.filter_by(email=email).first()

        # Validar si existe el usuario, si la contraseña coincide y si su estatus es activo
        if not usuario or not usuario.check_password(password) or usuario.estatus != 'activo' or usuario.perfil != 'administrador':
            return jsonify({
                "status": "error",
                "mensaje": "Credenciales incorrectas "
            }), 401

        #Genera el token de acceso JWT
        access_token = create_access_token(identity=usuario.id)

        # Responde sin exponer las contraseñas ni los hashes de las contraseñas 
        return jsonify({
            "status": "success",
            "mensaje": "Autenticación exitosa.",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "perfil": usuario.perfil
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "mensaje": "Ocurrió un error en el servidor.",
            "detalles": str(e)
        }), 400

    @auth_bp.route('/api/auth/perfil', methods=['GET'])
    @jwt_required()
    def perfil_protegido():
        usuario_id = get_jwt_identity()
        return jsonify({
            "status": "success",
            "mensaje": "Acceso a la ruta protegida exitoso.",
            "usuario_id": usuario_id
        }), 200
    