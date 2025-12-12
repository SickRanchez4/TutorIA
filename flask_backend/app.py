from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from config import config
import os

from dotenv import load_dotenv
load_dotenv()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enforce that a real database URI is configured.
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError(
            "No database configured. Set `DATABASE_URL` or the MSSQL_* environment variables: "
            "MSSQL_USER, MSSQL_PASSWORD, MSSQL_HOST, MSSQL_PORT, MSSQL_DB, MSSQL_DRIVER."
        )

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # CORS configuration: apply to all routes and blueprints, including error responses
    frontend_origin = 'http://localhost:5173'
    CORS(app, resources={r"/*": {"origins": frontend_origin}})

    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)