from datetime import date

from sqlalchemy import or_

from app.models.vacante_model import Vacante


def buscar_vacantes(palabra_clave):
    """
    Busca vacantes por coincidencias parciales en sus campos de texto.

    Args:
        palabra_clave (str): Texto que se desea buscar.

    Returns:
        list[Vacante]: Vacantes que coinciden con la búsqueda.
    """
    termino = palabra_clave.strip()

    if not termino:
        return []

    patron = f"%{termino}%"

    consulta = Vacante.query.filter(
        or_(
            Vacante.nombre.ilike(patron),
            Vacante.descripcion.ilike(patron),
            Vacante.detalle.ilike(patron),
            Vacante.categoria.ilike(patron),
            Vacante.ubicacion.ilike(patron),
            Vacante.tipo_empleo.ilike(patron),
        )
    )

    # Considerar únicamente vacantes que ya tienen fecha de publicación
    # y cuya fecha no es posterior al día actual.
    consulta = consulta.filter(
        Vacante.fecha_publicacion.isnot(None),
        Vacante.fecha_publicacion <= date.today(),
    )

    return consulta.order_by(
        Vacante.fecha_publicacion.desc(),
        Vacante.id.desc(),
    ).all()


def obtener_vacante_por_id(vacante_id):
    """
    Obtiene una vacante visible para el público mediante su identificador.

    Args:
        vacante_id (int): Identificador de la vacante.

    Returns:
        Vacante | None: La vacante encontrada, o None si no existe
        o está desactivada.
    """
    # Las vacantes desactivadas no se muestran en la consulta pública.
    # "IS NOT false" también acepta las que no tienen valor en 'activa'.
    return Vacante.query.filter(
        Vacante.id == vacante_id,
        Vacante.activa.isnot(False),
    ).first()