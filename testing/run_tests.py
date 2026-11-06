"""Run only the explicit SPEC-001 isolated suite and preserve honest results."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
import uuid
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "testing.spec_001.test_account_capacity",
    "testing.spec_001.test_student_creation",
    "testing.spec_001.test_session_creation",
)
REQUIRED_PATHS = {
    f"A{algorithm}_P{number}"
    for algorithm, count in ((1, 5), (2, 8), (3, 5))
    for number in range(1, count + 1)
}


def test_ids(suite):
    """Flatten test identifiers without performing broad filesystem discovery."""
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from test_ids(test)
        else:
            yield test.id()


def git_output(*arguments):
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), *arguments], text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def execute_suite(suite, stream):
    """Treat zero cases, skips and expected failures as incomplete verification."""
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    complete = (
        result.testsRun > 0 and result.wasSuccessful()
        and not result.skipped and not result.expectedFailures
    )
    return result, 0 if complete else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ejecutar solo pruebas aisladas de SPEC-001.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--safety', action='store_true', help='Verificar seguridad y soporte de sistema con SQL/configuración simulados; nunca conecta al backend.')
    modes.add_argument('--integration', action='store_true', help='Integración SQL real, proceso independiente y confirmación interactiva obligatoria.')
    parser.add_argument("--report", type=Path, help="Nuevo reporte .txt dentro de la carpeta de evidencias de esta spec.")
    args = parser.parse_args(argv)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    if args.integration:
        from testing.run_integration import main as integration_main
        return integration_main(['--report', str(args.report)] if args.report else [])

    report = None
    if args.report:
        report = args.report.resolve()
        evidence_root = ROOT / "docs" / "specs" / "spec-001-tests" / "evidence"
        if not report.is_relative_to(evidence_root.resolve()) or report.suffix != ".txt":
            parser.error("El reporte debe ser .txt dentro de las evidencias de SPEC-001.")
        if report.exists():
            parser.error("El reporte ya existe; elija otro nombre para conservar la evidencia anterior.")
        report.parent.mkdir(parents=True, exist_ok=True)

    from testing.support import BACKEND_MODULES
    import dotenv
    import pyodbc
    import requests
    from sqlalchemy.engine import Engine

    before_env, before_path = dict(os.environ), sys.path[:]
    original_guards = (dotenv.load_dotenv, Engine.connect, pyodbc.connect, requests.sessions.Session.request)
    output = io.StringIO()
    modules = ('testing.spec_001.test_local_safety',) if args.safety else MODULES
    mode = 'controlled-safety' if args.safety else 'isolated'
    print(f"SPEC-001 | mode={mode} | run_id=" + str(uuid.uuid4()), file=output)
    print("UTC: " + datetime.now(timezone.utc).isoformat(), file=output)
    print("Python: " + sys.version.split()[0], file=output)
    print("Commit: " + git_output("rev-parse", "HEAD"), file=output)
    print("Local changes (paths only):\n" + git_output("status", "--short"), file=output)
    sources = (
        "backend/services/subscription_quota.py", "backend/routes/coordinador.py",
        "backend/routes/estudiante.py", "testing/support.py", "testing/run_tests.py",
          *(module.replace(".", "/") + ".py" for module in modules),
          *(['testing/local_destination.py', 'testing/ownership.py', 'testing/fixtures.py',
              'testing/cleanup.py', 'testing/run_local_data.py', 'testing/system_support.py',
              'testing/run_system.py'] if args.safety else []),
    )
    for source in sources:
        print(source + " SHA256=" + hashlib.sha256((ROOT / source).read_bytes()).hexdigest(), file=output)
    print("No real persistence, decorators or external providers are verified.\n", file=output)

    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    identifiers = list(test_ids(suite))
    required = () if args.safety else REQUIRED_PATHS
    missing = sorted(case for case in required if not any("test_" + case + "_" in name for name in identifiers))
    if missing:
        print("Missing mandatory paths: " + ", ".join(missing), file=output)
        exit_code = 1
    else:
        with ExitStack() as stack:
            safety_guards = []
            if args.safety:
                for owner, name in ((Engine, 'connect'), (pyodbc, 'connect'),
                                    (requests.sessions.Session, 'request'), (dotenv.main.DotEnv, 'dict')):
                    safety_guards.append(stack.enter_context(patch.object(
                        owner, name, side_effect=AssertionError('Real I/O blocked in controlled safety suite'),
                    )))
            result, exit_code = execute_suite(suite, output)
            if any(guard.called for guard in safety_guards):
                print('Unexpected real I/O attempt in controlled suite.', file=output)
                exit_code = 1
        print(f"Summary: tests={result.testsRun}, failures={len(result.failures)}, errors={len(result.errors)}, "
              f"skips={len(result.skipped)}, expected_failures={len(result.expectedFailures)}", file=output)

    leaked = any(name == root or name.startswith(root + ".")
                 for name in sys.modules for root in BACKEND_MODULES)
    restored = (
        dict(os.environ) == before_env and sys.path == before_path and not leaked
        and (dotenv.load_dotenv, Engine.connect, pyodbc.connect, requests.sessions.Session.request) == original_guards
    )
    print("Isolation state restored: " + str(restored), file=output)
    if not restored:
        exit_code = 1
    print("Real SQL/HTTP/secret-file access: blocked; any guarded attempt fails the case.", file=output)
    print("Cleanup: no persistent fixtures created; scoped mocks and imports released.", file=output)
    print("Exit code: " + str(exit_code), file=output)
    content = output.getvalue()
    if report:
        with report.open("x", encoding="utf-8") as handle:
            handle.write(content)
    print(content, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())