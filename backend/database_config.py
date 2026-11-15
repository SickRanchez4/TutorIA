"""Build the PostgreSQL connection without interpolating credentials into a URI."""
import os
from collections.abc import Mapping

from sqlalchemy import event
from sqlalchemy.engine import Connection, Engine, URL


DATABASE_ENV_KEYS = (
    'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_SSLMODE',
)


def build_database_url(environment: Mapping[str, str] | None = None) -> URL:
    values = os.environ if environment is None else environment
    if values.get('DATABASE_URL'):
        raise RuntimeError('Remove DATABASE_URL and configure the separate DB_* variables.')
    required = ('DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD')
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise RuntimeError('Missing database configuration: ' + ', '.join(missing))
    try:
        port = int(values.get('DB_PORT', '5432'))
    except ValueError:
        raise RuntimeError('DB_PORT must be an integer between 1 and 65535.') from None
    if not 1 <= port <= 65535:
        raise RuntimeError('DB_PORT must be an integer between 1 and 65535.')
    sslmode = values.get('DB_SSLMODE', 'prefer')
    if sslmode not in {'disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'}:
        raise RuntimeError('DB_SSLMODE is not a valid PostgreSQL SSL mode.')
    return URL.create(
        'postgresql+psycopg',
        username=values['DB_USER'],
        password=values['DB_PASSWORD'],
        host=values['DB_HOST'],
        port=port,
        database=values['DB_NAME'],
        query={
            'sslmode': sslmode,
            'connect_timeout': '10',
        },
    )


def configure_database_engine(engine: Engine) -> None:
    # Transaction-local settings also work with transaction-pooling proxies.
    @event.listens_for(engine, 'begin')
    def configure_transaction(connection: Connection) -> None:
        connection.exec_driver_sql(
            "SELECT set_config('TimeZone', 'UTC', true), set_config('search_path', 'public', true)"
        ).close()
