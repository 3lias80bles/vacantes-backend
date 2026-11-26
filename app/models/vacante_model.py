from app import db

class Vacante(db.Model):
    __tablename__ = 'vacante'

    id = db.Column(db.Integer, primary_key=True)
    fecha_publicacion = db.Column(db.Date)
    nombre = db.Column(db.String(250))
    descripcion = db.Column(db.Text)
    detalle = db.Column(db.Text)
    categoria = db.Column(db.String(100))
    ubicacion = db.Column(db.String(150))
    tipo_empleo = db.Column(db.String(50))
    sueldo = db.Column(db.Float)
    contacto = db.Column(db.String)
    activa = db.Column(db.Boolean)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    # Método para convertir el objeto Vacante a un diccionario
    def to_dict(self, completo=False):
        datos = {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "detalle": self.detalle, 
            "categoria": self.categoria,
            "ubicacion": self.ubicacion,
            "tipo_empleo": self.tipo_empleo,
            "sueldo": self.sueldo,
            "contacto": self.contacto,
            "activa": self.activa,
            "fecha_publicacion": (
                self.fecha_publicacion.isoformat()
                if self.fecha_publicacion
                else None
            ),
        }
        if completo:
            datos["sueldo"] = self.sueldo
            datos["contacto"] = self.contacto
        return datos
    
    # Datos básicos más el estado, para la consulta del administrador
    def to_dict_admin(self):
        datos = self.to_dict()
        activa = self.activa is not False
        datos["activa"] = activa
        datos["estado"] = "activa" if activa else "inactiva"
        datos["id_usuario"] = self.id_usuario
        return datos