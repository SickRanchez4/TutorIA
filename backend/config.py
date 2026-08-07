import os
from datetime import timedelta
from urllib.parse import quote_plus

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
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def _build_mssql_uri():
        """Return a SQLAlchemy-compatible URI.

        Priority:
        1) Use DATABASE_URL if provided (assumed already valid for SQLAlchemy)
        2) Otherwise build from MSSQL_* env vars.
        Return None if not enough info is present.
        """
        # 1) Allow a full DATABASE_URL provided by user
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url

        # 2) Build from MSSQL_* pieces
        user = os.getenv('MSSQL_USER')
        password = os.getenv('MSSQL_PASSWORD')
        host = os.getenv('MSSQL_HOST', 'localhost')
        port = os.getenv('MSSQL_PORT', '1433')
        db = os.getenv('MSSQL_DB', 'TutoriaDB')
        driver = os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')

        if user and password:
            user_enc = quote_plus(user)
            password_enc = quote_plus(password)
            # encode driver for inclusion in query (spaces -> +)
            driver_enc = quote_plus(driver)
            return f'mssql+pyodbc://{user_enc}:{password_enc}@{host}:{port}/{db}?driver={driver_enc}'

        return None


class DevelopmentConfig(Config):
    """Development config with debug mode enabled"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or Config._build_mssql_uri()


class ProductionConfig(Config):
    """Production config with debug mode disabled"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or Config._build_mssql_uri()


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}