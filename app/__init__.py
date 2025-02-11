from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from app.auth import auth_bp
    from app.routes import routes_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(routes_bp, url_prefix="/api")

    return app
