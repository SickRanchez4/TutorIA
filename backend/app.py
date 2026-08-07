import json
import logging
import os
import sys
import time
import uuid

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import text
from models import db
from config import config

from dotenv import load_dotenv
load_dotenv()


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


class JsonLogFormatter(logging.Formatter):
    """Formato compacto para logs que puedan ser consultados por el proveedor."""

    def format(self, record):
        payload = {
            'timestamp': self.formatTime(record, '%Y-%m-%dT%H:%M:%SZ'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        for field in (
            'event', 'request_id', 'method', 'path', 'endpoint',
            'status_code', 'duration_ms', 'remote_addr', 'exception_type',
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload['exception'] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(app):
    """Configura logs estructurados a stdout sin modificar los endpoints."""
    logger = app.logger
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO').upper())
    logger.propagate = False

    if any(getattr(handler, '_tutoria_json_handler', False) for handler in logger.handlers):
        return

    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler._tutoria_json_handler = True
    handler.setFormatter(JsonLogFormatter())
    logger.addHandler(handler)


def register_request_logging(app):
    """Registra metadatos de cada solicitud; no registra payloads ni cabeceras."""
    @app.before_request
    def start_request_log():
        incoming_id = request.headers.get('X-Request-ID', '').strip()
        g.request_id = incoming_id[:128] if incoming_id else str(uuid.uuid4())
        g.request_started_at = time.perf_counter()

    @app.after_request
    def complete_request_log(response):
        duration_ms = round((time.perf_counter() - getattr(g, 'request_started_at', time.perf_counter())) * 1000, 2)
        response.headers['X-Request-ID'] = g.request_id
        app.logger.info(
            'request_completed',
            extra={
                'event': 'http_request',
                'request_id': g.request_id,
                'method': request.method,
                'path': request.path,
                'endpoint': request.endpoint,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'remote_addr': request.remote_addr,
            },
        )
        return response

    @app.teardown_request
    def log_unhandled_exception(error):
        if error is not None:
            app.logger.exception(
                'request_failed',
                extra={
                    'event': 'unhandled_exception',
                    'request_id': getattr(g, 'request_id', None),
                    'method': request.method,
                    'path': request.path,
                    'endpoint': request.endpoint,
                    'exception_type': type(error).__name__,
                },
            )


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    configure_logging(app)
    register_request_logging(app)

    # Enforce that a real database URI is configured.
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError(
            "No database configured. Set `DATABASE_URL` or the MSSQL_* environment variables: "
            "MSSQL_USER, MSSQL_PASSWORD, MSSQL_HOST, MSSQL_PORT, MSSQL_DB, MSSQL_DRIVER."
        )

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    limiter.init_app(app)

    # CORS configuration: apply to all routes and blueprints, including error responses
    frontend_origin = os.getenv('FRONTEND_URL', 'http://localhost:5173,http://localhost:5174')
    origins = [o.strip() for o in frontend_origin.split(',') if o.strip()]
    CORS(app, 
         resources={r"/*": {
             "origins": origins,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }},
         expose_headers=["Content-Type"]
    )

    @app.get('/healthz')
    def health_check():
        """Liveness probe: confirma que el proceso Flask está disponible."""
        return jsonify({'status': 'ok'}), 200

    @app.get('/readyz')
    def readiness_check():
        """Readiness probe: confirma la conectividad con SQL Server."""
        try:
            db.session.execute(text('SELECT 1'))
        except Exception:
            app.logger.exception('database_readiness_failed')
            return jsonify({'status': 'unavailable'}), 503
        return jsonify({'status': 'ready'}), 200

    # Register blueprints
    from routes.auth_multi_tenant import auth_bp
    from routes.instituciones import instituciones_bp
    from routes.coordinador import coordinador_bp
    from routes.estudiante import estudiante_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(instituciones_bp, url_prefix='/api/admin')
    app.register_blueprint(coordinador_bp, url_prefix='/api/coordinador')
    app.register_blueprint(estudiante_bp, url_prefix='/api/estudiante')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)