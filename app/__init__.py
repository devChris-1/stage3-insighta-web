from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    csrf.init_app(app)

    from app.auth import auth_bp
    from app.routes import routes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    return app
