from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["JWT_SECRET_KEY"] = "Clave_Secreta"

    db.init_app(app)
    jwt.init_app(app)

    # Registrar manejadores de errores    
    from app.errors import registrar_manejadores
    registrar_manejadores(app)

    # Registrar las rutas (después de inicializar db)
    from app.routes.vacantes_routes import vacantes_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(vacantes_bp)
    app.register_blueprint(auth_bp)

    return app