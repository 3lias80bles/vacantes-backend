from app import db

class Usuario(db.Model):
    __tablename__ = 'Usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    perfil = db.Column(db.String(100))
    estatus = db.Column(db.String(50))