"""Scoped backend imports for isolated tests; never initialize a database."""
from contextlib import ExitStack, contextmanager
import importlib
import os
from pathlib import Path
import secrets
import sys
from types import SimpleNamespace
from unittest.mock import patch

import dotenv
from flask import Flask
import pyodbc
import requests
from sqlalchemy.engine import Engine


BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
BACKEND_MODULES = ("app", "config", "models", "routes", "services")


def _backend_name(name):
    return any(name == root or name.startswith(root + ".") for root in BACKEND_MODULES)


@contextmanager
def isolated_backend():
    """Import real algorithms with restored environment, modules and I/O guards."""
    if any(_backend_name(name) for name in sys.modules):
        raise RuntimeError("Use un proceso independiente para las pruebas aisladas.")
    original_path = sys.path[:]
    try:
        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {
                "JWT_SECRET_KEY": secrets.token_urlsafe(48),
                "DATABASE_URL": "",
                "RATELIMIT_STORAGE_URI": "memory://",
                "TRUSTED_PROXY_COUNT": "0",
                "FLASK_ENV": "development",
            }))
            # Suppress automatic dotenv reads before config/app can import them.
            stack.enter_context(patch.object(dotenv, "load_dotenv", return_value=False))
            stack.enter_context(patch("dotenv.main.load_dotenv", return_value=False))
            guards = {
                "dotenv_read": stack.enter_context(patch(
                    "dotenv.main.DotEnv.dict",
                    side_effect=AssertionError("Secret file access blocked"),
                )),
                "sqlalchemy_connect": stack.enter_context(patch.object(
                    Engine, "connect", side_effect=AssertionError("SQL access blocked"),
                )),
                "odbc_connect": stack.enter_context(patch.object(
                    pyodbc, "connect", side_effect=AssertionError("ODBC access blocked"),
                )),
                "http_request": stack.enter_context(patch.object(
                    requests.sessions.Session, "request",
                    side_effect=AssertionError("External HTTP access blocked"),
                )),
            }
            sys.path.insert(0, str(BACKEND_PATH))
            application = importlib.import_module("app")
            quota = importlib.import_module("services.subscription_quota")
            coordinator = importlib.import_module("routes.coordinador")
            student = importlib.import_module("routes.estudiante")
            flask_app = Flask("isolated_tests")
            flask_app.config.update(TESTING=True)
            try:
                yield SimpleNamespace(
                    application=application, quota=quota, coordinator=coordinator,
                    student=student, flask_app=flask_app, guards=guards,
                )
            finally:
                # Detect attempts even when an application handler swallowed the error.
                attempted = [name for name, guard in guards.items() if guard.called]
                if attempted:
                    raise AssertionError("Blocked isolated I/O attempts: " + ", ".join(attempted))
    finally:
        for name in list(sys.modules):
            if _backend_name(name):
                del sys.modules[name]
        sys.path[:] = original_path