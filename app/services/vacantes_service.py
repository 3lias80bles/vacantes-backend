from datetime import date, datetime

from sqlalchemy import or_

from app import db
from app.utils.errors import ValidacionError
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
    consulta = Vacante.query

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
        raise ValidacionError("El cuerpo de la solicitud debe ser un objeto JSON válido.")

    nombre = (data.get("nombre") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()

    if not nombre:
        raise ValidacionError("El nombre es obligatorio.")
    if len(nombre) > 250:
        raise ValidacionError("El nombre no puede superar los 250 caracteres.")

    if not descripcion:
        raise ValidacionError("La descripción es obligatoria.")

    sueldo = data.get("sueldo")
    sueldo_val = None
    if sueldo is not None and sueldo != "":
        if isinstance(sueldo, bool):
            raise ValidacionError("El sueldo debe ser un número válido.")
        try:
            sueldo_val = float(sueldo)
        except (ValueError, TypeError):
            raise ValidacionError("El sueldo debe ser un número válido.")
        if sueldo_val < 0:
            raise ValidacionError("El sueldo no puede ser negativo.")

    fecha_raw = data.get("fecha_publicacion")
    fecha_pub = date.today()
    if fecha_raw is not None and fecha_raw != "":
        if not isinstance(fecha_raw, str):
            raise ValidacionError("La fecha de publicación debe tener el formato YYYY-MM-DD.")
        try:
            fecha_pub = datetime.strptime(fecha_raw.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValidacionError("La fecha de publicación debe tener el formato YYYY-MM-DD.")

    activa_raw = data.get("activa", True)
    if isinstance(activa_raw, bool):
        activa = activa_raw
    elif isinstance(activa_raw, str) and activa_raw.strip().lower() in ("true", "false"):
        activa = activa_raw.strip().lower() == "true"
    else:
        raise ValidacionError("El valor de 'activa' debe ser booleano (true o false).")

    nueva_vacante = Vacante(
        fecha_publicacion=fecha_pub,
        nombre=nombre,
        descripcion=descripcion,
        detalle=(data.get("detalle") or "").strip() or None,
        categoria=(data.get("categoria") or "").strip() or None,
        ubicacion=(data.get("ubicacion") or "").strip() or None,
        tipo_empleo=(data.get("tipo_empleo") or "").strip() or None,
        sueldo=sueldo_val,
        contacto=(data.get("contacto") or "").strip() or None,
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
