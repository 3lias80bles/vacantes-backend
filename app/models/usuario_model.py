import hashlib
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(255))
    perfil = db.Column(db.String(30))
    estatus = db.Column(db.String(20))

    def set_password(self, password_raw):
        self.password = generate_password_hash(password_raw)

    def check_password(self, password_raw):
        if len(self.password) == 32 and '$' not in self.password:
            return self.password == hashlib.md5(password_raw.encode()).hexdigest()
        return check_password_hash(self.password, password_raw)