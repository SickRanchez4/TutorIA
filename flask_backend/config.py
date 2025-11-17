import os
from datetime import timedelta
from urllib.parse import quote_plus


class Config:
    """Base config"""
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def _build_mssql_uri():
        """Attempt to build a SQL Server URI from environment variables.

        Priority order:
        Build a pyodbc-based SQLAlchemy URI using the MSSQL_* environment
        the caller must provide the individual MSSQL_* values.
        Return None if not enough information is available.
        """
        user = os.getenv('MSSQL_USER')
        password = os.getenv('MSSQL_PASSWORD')
        host = os.getenv('MSSQL_HOST', 'localhost')
        port = os.getenv('MSSQL_PORT', '1433')
        db = os.getenv('MSSQL_DB', 'university')
        driver = os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server')

        # Require explicit user and password (no DATABASE_URL support)
        if user and password:
            # Quote password and driver for inclusion in the URL
            user_enc = quote_plus(user)
            password_enc = quote_plus(password)
            driver_enc = quote_plus(driver)
            return f'mssql+pyodbc://{user_enc}:{password_enc}@{host}:{port}/{db}?driver={driver_enc}'

        return None


class DevelopmentConfig(Config):
    """Development"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or Config._build_mssql_uri()


class ProductionConfig(Config):
    """Production"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or Config._build_mssql_uri()


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}