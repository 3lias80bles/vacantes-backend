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