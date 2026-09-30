import os
from datetime import timedelta

# Ensure environment variables from a local .env are loaded
from dotenv import load_dotenv
load_dotenv()


class Config:
    """Base config"""
    # Require JWT_SECRET_KEY to be set explicitly
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY must be set in environment variables. "
        )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    # Única fuente de configuración de la conexión, en todos los entornos.
    SQLALCHEMY_DATABASE_URI = (os.getenv('DATABASE_URL') or '').strip() or None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', str(64 * 1024 * 1024)))
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    ALLOW_PUBLIC_REGISTRATION = os.getenv('ALLOW_PUBLIC_REGISTRATION', 'false').strip().lower() == 'true'

class DevelopmentConfig(Config):
    """Development config with debug mode enabled"""
    DEBUG = True


class ProductionConfig(Config):
    """Production config with debug mode disabled"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}