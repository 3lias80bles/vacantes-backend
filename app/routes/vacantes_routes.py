from flask import Blueprint, request, jsonify
from app.models.vacante_model import Vacante

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