"""Opt-in local SQL authorization; no configuration is read at import time."""
from contextlib import ExitStack, contextmanager
import importlib
import ipaddress
import os
import re
import socket
import sys
from types import SimpleNamespace
from unittest.mock import patch

import dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from backend.database_config import DATABASE_ENV_KEYS, build_database_url, configure_database_engine
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
    """Accept only explicit local PostgreSQL targets without routing overrides."""
    try:
        url = make_url(value)
        if url.drivername != "postgresql+psycopg":
            raise ValueError()
        if set(url.query) - {'sslmode', 'connect_timeout'}:
            raise ValueError()
        host, database = url.host, url.database
        if not host or not database or '${' in str(url):
            raise ValueError()
        host = host.casefold()
        if host not in local_names() | {"localhost", "127.0.0.1", "::1"}:
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
    for key in DATABASE_ENV_KEYS:
        if key in values and key in os.environ and values[key] != os.environ[key]:
            raise SafetyError("La configuración DB_* del proceso y del backend difiere; resuelva el conflicto.")
    merged = dict(values)
    merged.update(os.environ)
    if any(key.startswith('PG') for key in merged):
        raise SafetyError("Variables libpq PG* no evaluadas; use solo DB_* para el destino local.")
    try:
        connection_target(build_database_url(merged))
    except RuntimeError:
        raise SafetyError("Configuración PostgreSQL incompleta o inválida; revise DB_*.") from None
    if not merged.get("JWT_SECRET_KEY"):
        raise SafetyError("La configuración existente carece de JWT_SECRET_KEY.")
    merged.update(RATELIMIT_STORAGE_URI="memory://", FLASK_ENV="development", TRUSTED_PROXY_COUNT="0")
    return merged


def verify_destination(connection, database):
    """Read identity and schema, including metadata visibility, before any DML."""
    row = connection.execute(text("""
        SELECT inet_server_addr()::text AS server,
               inet_server_port() AS port,
               current_database() AS database_name,
               has_schema_privilege('public', 'USAGE') AS metadata_access,
               current_schema() AS schema_name,
               current_setting('server_version_num')::integer AS version
    """)).mappings().one()
    local_addresses = {
        address[4][0] for address in socket.getaddrinfo(socket.gethostname(), None)
    } | {'127.0.0.1', '::1'}
    if (row["server"] not in local_addresses
            or row["database_name"] != database or not row["metadata_access"]
            or row['schema_name'] != 'public' or not 180000 <= row['version'] < 190000):
        raise SafetyError("Identidad SQL local o visibilidad de esquema no comprobada.")
    ipaddress.ip_address(row['server'])
    inspector = inspect(connection)
    actual_tables = set(inspector.get_table_names(schema='public'))
    for table, required in REQUIRED_COLUMNS.items():
        if table not in actual_tables:
            raise SafetyError("Esquema requerido incompleto; no se crean tablas ni se ejecuta seed.")
        if not required <= {column["name"] for column in inspector.get_columns(table, schema="public")}:
            raise SafetyError("Columnas requeridas ausentes; operación bloqueada.")
        primary_key = set(inspector.get_pk_constraint(table, schema='public')['constrained_columns'])
        expected_key = ({'user_id', 'role_id'} if table == 'user_roles'
                else {'curso_id'} if table == 'configuracion_ia' else {'id'})
        if primary_key != expected_key:
            raise SafetyError('Identidad de tablas no verificable; operación bloqueada.')
        references = {
            (source, fk['referred_table'], target)
            for fk in inspector.get_foreign_keys(table, schema='public')
            if fk.get('referred_schema') in {None, 'public'}
            for source, target in zip(fk['constrained_columns'], fk['referred_columns'])
        }
        if not REQUIRED_FKS.get(table, set()) <= references:
            raise SafetyError('Relaciones requeridas ausentes; operación bloqueada.')
    if connection.execute(text("""
        SELECT COUNT(*) FROM pg_trigger tr
        JOIN pg_class t ON t.oid = tr.tgrelid
        JOIN pg_namespace s ON s.oid = t.relnamespace
        WHERE NOT tr.tgisinternal AND tr.tgenabled <> 'D' AND s.nspname = 'public'
          AND t.relname IN ('planes','instituciones','suscripciones','users','user_roles',
                         'cursos','estudiante_cursos','sesiones_chat','configuracion_ia')
    """)).scalar_one():
        raise SafetyError('Triggers de escritura no evaluados; operación bloqueada.')
    if connection.execute(text("""
        SELECT COUNT(*) FROM
          (VALUES ('planes'),('instituciones'),('suscripciones'),('users'),('user_roles'),
                  ('cursos'),('estudiante_cursos'),('sesiones_chat'),('configuracion_ia')) AS t(name)
        CROSS JOIN (VALUES ('SELECT'),('INSERT'),('UPDATE'),('DELETE')) AS p(permission)
        WHERE NOT has_table_privilege('public.' || t.name, p.permission)
           OR EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                      WHERE n.nspname = 'public' AND c.relname = t.name AND c.relrowsecurity)
           OR CASE WHEN t.name IN ('planes', 'cursos') THEN
               NOT COALESCE(has_sequence_privilege(pg_get_serial_sequence('public.' || t.name, 'id'), 'USAGE'), false)
               ELSE false END
    """)).scalar_one():
        raise SafetyError('Permisos de preparación y limpieza insuficientes; escrituras bloqueadas.')
    roles = connection.execute(text(
        "SELECT name FROM public.roles WHERE name IN ('coordinador', 'estudiante')"
    )).scalars().all()
    if set(roles) != {"coordinador", "estudiante"}:
        raise SafetyError("Faltan roles compartidos; no se modifica su configuración.")
    return f"{row['server']}:{row['port']} / {row['database_name']}"


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
    url = build_database_url(environment)
    _, database = connection_target(url)
    probe = None
    original_path = sys.path[:]
    application = None
    try:
        probe = create_engine(url, echo=False, hide_parameters=True)
        configure_database_engine(probe)
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
                if application.config["SQLALCHEMY_DATABASE_URI"] != url:
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