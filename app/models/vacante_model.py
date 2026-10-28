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