from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Registrar las rutas
    from app.routes.vacantes_routes import vacantes_bp
    app.register_blueprint(vacantes_bp)

    return app