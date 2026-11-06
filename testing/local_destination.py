"""Opt-in local SQL authorization; no configuration is read at import time."""
from contextlib import ExitStack, contextmanager
import importlib
import os
import re
import socket
import sys
from types import SimpleNamespace
from unittest.mock import patch

import dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from testing.support import BACKEND_PATH, _backend_name


class SafetyError(RuntimeError):
    """A redacted, operator-facing refusal; never wrap a raw connection error."""


REQUIRED_COLUMNS = {
    "roles": {"id", "name"},
    "planes": {"id", "nombre", "max_cuentas", "is_active"},
    "instituciones": {"id", "nombre", "is_active"},
    "suscripciones": {"id", "institucion_id", "plan_id", "limite_tokens_mensual",
                      "fecha_inicio", "fecha_fin", "is_active"},
    "users": {"id", "institucion_id", "email", "password_hash", "first_name",
              "last_name", "phone", "is_active"},
    "user_roles": {"user_id", "role_id"},
    "cursos": {"id", "institucion_id", "nombre", "is_active"},
    "estudiante_cursos": {"id", "user_id", "curso_id", "is_active"},
    "sesiones_chat": {"id", "user_id", "curso_id", "titulo", "is_active"},
    "configuracion_ia": {"curso_id"},
}
REQUIRED_FKS = {
    'suscripciones': {('institucion_id', 'instituciones', 'id'), ('plan_id', 'planes', 'id')},
    'users': {('institucion_id', 'instituciones', 'id')},
    'user_roles': {('user_id', 'users', 'id'), ('role_id', 'roles', 'id')},
    'cursos': {('institucion_id', 'instituciones', 'id')},
    'estudiante_cursos': {('user_id', 'users', 'id'), ('curso_id', 'cursos', 'id')},
    'sesiones_chat': {('user_id', 'users', 'id'), ('curso_id', 'cursos', 'id')},
    'configuracion_ia': {('curso_id', 'cursos', 'id')},
}


def local_names():
    """Only OS machine identities; do not infer locality through DNS aliases."""
    return {socket.gethostname().casefold(), socket.gethostname().split('.')[0].casefold()}


def connection_target(value):
    """Parse SQLAlchemy/ODBC without returning or printing credentials."""
    try:
        url = make_url(value)
        if url.drivername != "mssql+pyodbc":
            raise ValueError()
        if "odbc_connect" in url.query:
            if set(url.query) != {"odbc_connect"} or url.host or url.database:
                raise ValueError()
            # Braced values can contain semicolons; duplicates/ambiguous syntax fail closed.
            raw = url.query["odbc_connect"]
            parts = re.findall(r"(?:[^;{}]|\{(?:[^}]|\}\})*\})+(?:;|$)", raw)
            if ''.join(parts) != raw:
                raise ValueError()
            fields = {}
            allowed = {"driver", "server", "database", "uid", "pwd", "trusted_connection",
                       "encrypt", "trustservercertificate", "connection timeout", "timeout",
                       "applicationintent", "mars_connection"}
            for part in parts:
                key, content = part.rstrip(';').split('=', 1)
                key = key.strip().casefold()
                if key not in allowed or key in fields:
                    raise ValueError()
                content = content.strip()
                if content.startswith('{') and content.endswith('}'):
                    content = content[1:-1].replace('}}', '}')
                fields[key] = content
            host, database = fields["server"], fields["database"]
        else:
            if set(url.query) - {"driver", "TrustServerCertificate", "Encrypt",
                                 "trusted_connection", "timeout", "connection_timeout"}:
                raise ValueError()
            host, database = url.host, url.database
        if not host or not database or '${' in value:
            raise ValueError()
        host = re.sub(r"^tcp:", "", host, flags=re.I)
        if not re.fullmatch(r'(?:[\w().-]+|\[?::1\]?)(?:\\[\w-]+)?(?:,\d{1,5})?', host):
            raise ValueError()
        host = host.split('\\', 1)[0].split(',', 1)[0].strip('[]').casefold()
        if host not in local_names() | {"localhost", "127.0.0.1", "::1", ".", "(local)"}:
            raise ValueError()
        if not re.fullmatch(r"[\w .-]{1,128}", database):
            raise ValueError()
        return host, database
    except Exception:
        raise SafetyError("Conexión SQL local no verificable; operación bloqueada.") from None


def read_existing_environment():
    """Read the existing backend configuration only after explicit opt-in."""
    values = {key: value for key, value in dotenv.dotenv_values(
        BACKEND_PATH / '.env', interpolate=False,
    ).items() if value is not None}
    configured = (values.get("DATABASE_URL") or '').strip()
    inherited = (os.environ.get("DATABASE_URL") or '').strip()
    if configured and inherited and configured != inherited:
        raise SafetyError("DATABASE_URL del proceso y del backend difieren; resuelva el conflicto.")
    merged = dict(values)
    merged.update(os.environ)
    merged["DATABASE_URL"] = inherited or configured
    connection_target(merged["DATABASE_URL"])
    if not merged.get("JWT_SECRET_KEY"):
        raise SafetyError("La configuración existente carece de JWT_SECRET_KEY.")
    merged.update(RATELIMIT_STORAGE_URI="memory://", FLASK_ENV="development", TRUSTED_PROXY_COUNT="0")
    return merged


def verify_destination(connection, database):
    """Read identity and schema, including metadata visibility, before any DML."""
    row = connection.execute(text("""
        SELECT CAST(SERVERPROPERTY('MachineName') AS nvarchar(128)) AS machine,
               CAST(SERVERPROPERTY('ServerName') AS nvarchar(128)) AS server,
               DB_NAME() AS database_name,
               HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'VIEW DEFINITION') AS metadata_access
    """)).mappings().one()
    if (str(row["machine"]).casefold() not in local_names()
            or row["database_name"] != database or row["metadata_access"] != 1):
        raise SafetyError("Identidad SQL local o visibilidad de esquema no comprobada.")
    if not re.fullmatch(r"[\w .\\-]{1,128}", str(row["server"])):
        raise SafetyError("Identidad de servidor no verificable.")
    inspector = inspect(connection)
    actual_tables = set(inspector.get_table_names(schema='dbo'))
    for table, required in REQUIRED_COLUMNS.items():
        if table not in actual_tables:
            raise SafetyError("Esquema requerido incompleto; no se crean tablas ni se ejecuta seed.")
        if not required <= {column["name"] for column in inspector.get_columns(table, schema="dbo")}:
            raise SafetyError("Columnas requeridas ausentes; operación bloqueada.")
        primary_key = set(inspector.get_pk_constraint(table, schema='dbo')['constrained_columns'])
        expected_key = ({'user_id', 'role_id'} if table == 'user_roles'
                else {'curso_id'} if table == 'configuracion_ia' else {'id'})
        if primary_key != expected_key:
            raise SafetyError('Identidad de tablas no verificable; operación bloqueada.')
        references = {
            (source, fk['referred_table'], target)
            for fk in inspector.get_foreign_keys(table, schema='dbo')
            if fk.get('referred_schema') in {None, 'dbo'}
            for source, target in zip(fk['constrained_columns'], fk['referred_columns'])
        }
        if not REQUIRED_FKS.get(table, set()) <= references:
            raise SafetyError('Relaciones requeridas ausentes; operación bloqueada.')
    if connection.execute(text("""
        SELECT COUNT(*) FROM sys.triggers tr
        JOIN sys.tables t ON t.object_id = tr.parent_id
        JOIN sys.schemas s ON s.schema_id = t.schema_id
        WHERE tr.is_disabled = 0 AND s.name = 'dbo'
          AND t.name IN ('planes','instituciones','suscripciones','users','user_roles',
                         'cursos','estudiante_cursos','sesiones_chat','configuracion_ia')
    """)).scalar_one():
        raise SafetyError('Triggers de escritura no evaluados; operación bloqueada.')
    if connection.execute(text("""
        SELECT COUNT(*) FROM
          (VALUES ('planes'),('instituciones'),('suscripciones'),('users'),('user_roles'),
                  ('cursos'),('estudiante_cursos'),('sesiones_chat'),('configuracion_ia')) AS t(name)
        CROSS JOIN (VALUES ('SELECT'),('INSERT'),('UPDATE'),('DELETE')) AS p(permission)
        WHERE ISNULL(HAS_PERMS_BY_NAME('dbo.' + t.name, 'OBJECT', p.permission), 0) <> 1
    """)).scalar_one():
        raise SafetyError('Permisos de preparación y limpieza insuficientes; escrituras bloqueadas.')
    roles = connection.execute(text(
        "SELECT name FROM dbo.roles WHERE name IN ('coordinador', 'estudiante')"
    )).scalars().all()
    if set(roles) != {"coordinador", "estudiante"}:
        raise SafetyError("Faltan roles compartidos; no se modifica su configuración.")
    return f"{row['server']} / {row['database_name']}"


def confirm_destination(label, confirm=input):
    """Exact interactive confirmation; there is no unattended yes flag."""
    expected = f"AUTORIZO {label}"
    try:
        accepted = confirm(f"Destino local verificado: {label}\nEscriba '{expected}' para autorizar datos ficticios: ")
    except (EOFError, KeyboardInterrupt):
        accepted = None
    if accepted != expected:
        raise SafetyError("Confirmación ausente o incorrecta; escrituras bloqueadas.")


@contextmanager
def authorized_local_backend(confirm=input):
    """Verify through a separate read transaction, confirm, then import the factory."""
    if any(_backend_name(name) for name in sys.modules):
        raise SafetyError("Use un proceso independiente para la modalidad local.")
    environment = read_existing_environment()
    _, database = connection_target(environment["DATABASE_URL"])
    probe = None
    original_path = sys.path[:]
    application = None
    try:
        probe = create_engine(environment["DATABASE_URL"], echo=False, hide_parameters=True)
        with probe.connect() as connection:
            label = verify_destination(connection, database)
            connection.rollback()
        confirm_destination(label, confirm)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, environment))
            stack.enter_context(patch.object(dotenv, "load_dotenv", return_value=False))
            stack.enter_context(patch("dotenv.main.load_dotenv", return_value=False))
            sys.path.insert(0, str(BACKEND_PATH))
            module = importlib.import_module("app")
            application = module.create_app("development")
            application.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
            with application.app_context():
                db = importlib.import_module("models").db
                db.engine.echo = False
                db.engine.hide_parameters = True
                # Match the factory's effective destination before yielding write capability.
                if application.config["SQLALCHEMY_DATABASE_URI"] != environment["DATABASE_URL"]:
                    raise SafetyError("La fábrica cambió el destino; escrituras bloqueadas.")
                try:
                    with db.engine.connect() as connection:
                        if verify_destination(connection, database) != label:
                            raise SafetyError("El destino cambió después de confirmar.")
                    yield SimpleNamespace(app=application, db=db, label=label, database=database)
                finally:
                    db.session.remove()
                    db.engine.dispose()
    except SafetyError:
        raise
    except Exception:
        raise SafetyError("Operación SQL local bloqueada o fallida; detalle privado no registrado.") from None
    finally:
        if probe is not None:
            probe.dispose()
        for name in list(sys.modules):
            if _backend_name(name):
                del sys.modules[name]
        sys.path[:] = original_path