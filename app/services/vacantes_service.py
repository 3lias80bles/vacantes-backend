from datetime import date, datetime
from math import isfinite

from sqlalchemy import or_

from app import db
from app.errors import NoEncontrado, Prohibido, ValidacionError
from app.models.vacante_model import Vacante


def _error_validacion(campo, mensaje):
    return ValidacionError(errores=[{"campo": campo, "mensaje": mensaje}])


def _texto_opcional(data, campo, limite=None):
    valor = data.get(campo)
    if valor is None or valor == "":
        return None
    if not isinstance(valor, str):
        raise _error_validacion(campo, "Debe ser texto.")

    valor = valor.strip()
    if not valor:
        return None
    if limite is not None and len(valor) > limite:
        raise _error_validacion(campo, f"No puede superar los {limite} caracteres.")
    return valor


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
        Vacante.activa.isnot(False),
    )

    return consulta.order_by(
        Vacante.fecha_publicacion.desc(),
        Vacante.id.desc(),
    ).all()

def listar_vacantes(page=1):
    """
    Obtiene el listado paginado de vacantes publicadas.

    Args:
        page (int): Número de página solicitada.

    Returns:
        Pagination: Objeto de paginación de Flask-SQLAlchemy.
    """
    limite = 4

    consulta = Vacante.query.filter(
        Vacante.fecha_publicacion.isnot(None),
        Vacante.fecha_publicacion <= date.today(),
        Vacante.activa.isnot(False),
    )

    consulta = consulta.order_by(
        Vacante.fecha_publicacion.desc(),
        Vacante.id.desc(),
    )

    return consulta.paginate(
        page=page,
        per_page=limite,
        error_out=False,
    )

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

def filtrar_vacantes(categoria=None, ubicacion=None, tipo_empleo=None):
    """
    Obtiene las vacantes que coinciden con los filtros indicados.
    Los filtros vacíos se ignoran.
    """
    consulta = Vacante.query.filter(Vacante.activa.isnot(False))

    if categoria:
        consulta = consulta.filter(Vacante.categoria.ilike(f"%{categoria}%"))
    if ubicacion:
        consulta = consulta.filter(Vacante.ubicacion.ilike(f"%{ubicacion}%"))
    if tipo_empleo:
        consulta = consulta.filter(Vacante.tipo_empleo.ilike(f"%{tipo_empleo}%"))

    return consulta.all()

def listar_vacantes_admin(id_usuario):
    """
    Obtiene todas las vacantes del administrador indicado,
    activas e inactivas. Lista vacía si no tiene ninguna.
    """
    return Vacante.query.filter(
        Vacante.id_usuario == id_usuario,
    ).order_by(Vacante.id.desc()).all()

def crear_vacante(data, administrador_id=None):
    """
    Valida y registra una nueva vacante en la base de datos.
    """
    if not isinstance(data, dict):
        raise _error_validacion("body", "El cuerpo de la solicitud debe ser un objeto JSON válido.")

    nombre = data.get("nombre")
    if not isinstance(nombre, str) or not nombre.strip():
        raise _error_validacion("nombre", "El nombre es obligatorio y debe ser texto.")
    nombre = nombre.strip()

    if len(nombre) > 250:
        raise _error_validacion("nombre", "No puede superar los 250 caracteres.")

    descripcion = data.get("descripcion")
    if not isinstance(descripcion, str) or not descripcion.strip():
        raise _error_validacion("descripcion", "La descripción es obligatoria y debe ser texto.")
    descripcion = descripcion.strip()

    sueldo = data.get("sueldo")
    sueldo_val = None
    if sueldo is not None and sueldo != "":
        if isinstance(sueldo, bool):
            raise _error_validacion("sueldo", "Debe ser un número válido.")
        try:
            sueldo_val = float(sueldo)
        except (ValueError, TypeError, OverflowError):
            raise _error_validacion("sueldo", "Debe ser un número válido.")
        if not isfinite(sueldo_val):
            raise _error_validacion("sueldo", "Debe ser un número finito.")
        if sueldo_val < 0:
            raise _error_validacion("sueldo", "No puede ser negativo.")

    fecha_raw = data.get("fecha_publicacion")
    fecha_pub = date.today()
    if fecha_raw is not None and fecha_raw != "":
        if not isinstance(fecha_raw, str):
            raise _error_validacion("fecha_publicacion", "Debe tener el formato YYYY-MM-DD.")
        try:
            fecha_pub = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
        except ValueError:
            raise _error_validacion("fecha_publicacion", "Debe tener el formato YYYY-MM-DD.")
        if fecha_pub.isoformat() != fecha_raw:
            raise _error_validacion("fecha_publicacion", "Debe tener el formato YYYY-MM-DD.")

    activa_raw = data.get("activa", True)
    if isinstance(activa_raw, bool):
        activa = activa_raw
    elif isinstance(activa_raw, str) and activa_raw.strip().lower() in ("true", "false"):
        activa = activa_raw.strip().lower() == "true"
    else:
        raise _error_validacion("activa", "Debe ser booleano (true o false).")

    detalle = _texto_opcional(data, "detalle")
    categoria = _texto_opcional(data, "categoria", 100)
    ubicacion = _texto_opcional(data, "ubicacion", 150)
    tipo_empleo = _texto_opcional(data, "tipo_empleo", 50)
    contacto = _texto_opcional(data, "contacto")

    nueva_vacante = Vacante(
        fecha_publicacion=fecha_pub,
        nombre=nombre,
        descripcion=descripcion,
        detalle=detalle,
        categoria=categoria,
        ubicacion=ubicacion,
        tipo_empleo=tipo_empleo,
        sueldo=sueldo_val,
        contacto=contacto,
        activa=activa,
        id_usuario=administrador_id,
    )

    try:
        db.session.add(nueva_vacante)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return nueva_vacante

def eliminar_vacante(vacante_id, id_usuario):
    """
    Elimina una vacante del administrador indicado (borrado lógico).
    La vacante queda con activa = False y deja de verse en las consultas públicas.
    """
    vacante = obtener_vacante_por_id(vacante_id)

    # Inexistente o ya eliminada responden igual.
    if vacante is None:
        raise NoEncontrado("Vacante no encontrada.")
    if vacante.id_usuario != id_usuario:
        raise Prohibido("No tienes permiso para eliminar esta vacante.")

    try:
        vacante.activa = False
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return vacante
