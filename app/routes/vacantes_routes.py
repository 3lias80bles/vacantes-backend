from flask import Blueprint, request, jsonify
from app.models.vacante_model import Vacante
from app.services.vacantes_service import buscar_vacantes


# Definición del Blueprint (esto es lo que está buscando __init__.py)
vacantes_bp = Blueprint('vacantes_bp', __name__)

@vacantes_bp.route('/api/vacantes', methods=['GET'])
def obtener_vacantes():
    try:
        categoria = request.args.get('categoria')
        ubicacion = request.args.get('ubicacion')
        tipo_empleo = request.args.get('tipo_empleo')

        query = Vacante.query

        if categoria:
            query = query.filter(Vacante.categoria.ilike(f"%{categoria}%"))
        if ubicacion:
            query = query.filter(Vacante.ubicacion.ilike(f"%{ubicacion}%"))
        if tipo_empleo:
            query = query.filter(Vacante.tipo_empleo.ilike(f"%{tipo_empleo}%"))

        vacantes = query.all()

        resultado = [{
            "id": v.id,
            "nombre": v.nombre,
            "descripcion": v.descripcion,
            "detalle": v.detalle,
            "categoria": v.categoria,
            "ubicacion": v.ubicacion,
            "tipo_empleo": v.tipo_empleo,
            "fecha_publicacion": str(v.fecha_publicacion) if v.fecha_publicacion else None
        } for v in vacantes]

        return jsonify({"status": "success", "total": len(resultado), "data": resultado}), 200

    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400


@vacantes_bp.get("/api/vacantes/buscar")
def buscar_vacantes_endpoint():
    """
    Busca vacantes mediante el parámetro de consulta 'q'.

    Ejemplo:
    GET /vacantes/buscar?q=Python
    """
    palabra_clave = request.args.get("q", "")

    if not palabra_clave.strip():
        return jsonify({
            "error": "El parámetro 'q' es obligatorio.",
            "resultados": []
        }), 400

    if len(palabra_clave.strip()) > 100:
        return jsonify({
            "error": "La búsqueda no puede superar los 100 caracteres.",
            "resultados": []
        }), 400

    try:
        vacantes = buscar_vacantes(palabra_clave)

        resultados = [
            {
                "id": vacante.id,
                "nombre": vacante.nombre,
                "descripcion": vacante.descripcion,
                "detalle": vacante.detalle,
                "categoria": vacante.categoria,
                "ubicacion": vacante.ubicacion,
                "tipo_empleo": vacante.tipo_empleo,
                "fecha_publicacion": (
                    vacante.fecha_publicacion.isoformat()
                    if vacante.fecha_publicacion
                    else None
                ),
            }
            for vacante in vacantes
        ]

        return jsonify({
            "total": len(resultados),
            "resultados": resultados
        }), 200

    except Exception:
        # Registra el error real en el servidor sin exponer detalles internos
        # de la base de datos en la respuesta HTTP.
        from flask import current_app

        current_app.logger.exception(
            "Error al buscar vacantes."
        )

        return jsonify({
            "error": "No fue posible realizar la búsqueda.",
            "resultados": []
        }), 500