"""Opt-in real SQL integration runner with redacted errors and durable cleanup evidence."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib
import io
import logging
import os
from pathlib import Path
import sys
import unittest
import uuid

from testing.local_destination import SafetyError, authorized_local_backend
from testing.run_tests import ROOT, git_output, test_ids


class PrivateResult(unittest.TextTestResult):
    def _exc_info_to_string(self, err, test):
        # SQL/driver exceptions can contain bound secrets; never render raw tracebacks.
        return f'{test.id()}: {err[0].__name__}; detalle interno omitido por confidencialidad.\n'


@contextmanager
def private_logs():
    original = logging.root.manager.disable
    try:
        logging.disable(logging.CRITICAL)
        yield
    finally:
        logging.disable(original)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Integración SQL real SPEC-001; requiere confirmación exacta interactiva.')
    parser.add_argument('--report', type=Path, help='Nuevo reporte .txt dentro de evidencias SPEC-001.')
    args = parser.parse_args(argv)
    report = (args.report or ROOT / 'docs/specs/spec-001-tests/evidence' /
              ('integration-' + str(uuid.uuid4()) + '.txt')).resolve()
    evidence_root = (ROOT / 'docs/specs/spec-001-tests/evidence').resolve()
    if not report.is_relative_to(evidence_root) or report.suffix != '.txt' or report.exists():
        parser.error('El reporte debe ser nuevo, .txt y dentro de las evidencias de SPEC-001.')
    report.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the evidence BEFORE even reading configuration or opening SQL.
    with report.open('x', encoding='utf-8') as handle:
        handle.write('SPEC-001 | mode=integration | estado=started\n')
    output = io.StringIO()
    run_id = str(uuid.uuid4())
    version = git_output('rev-parse', 'HEAD')
    changes = git_output('status', '--short')
    fixture_version = version + '-dirty' if version != 'unavailable' and changes else version
    print(f'SPEC-001 | mode=integration | run_id={run_id}', file=output)
    print('UTC: ' + datetime.now(timezone.utc).isoformat(), file=output)
    print('Python: ' + sys.version.split()[0], file=output)
    print('Commit: ' + version, file=output)
    print('Local changes (paths only):\n' + changes, file=output)
    for path in ('testing/run_integration.py', 'testing/run_tests.py', 'testing/local_destination.py',
                 'testing/ownership.py', 'testing/fixtures.py', 'testing/cleanup.py',
                 'testing/spec_001/test_integration.py', 'backend/app.py', 'backend/config.py',
                 'backend/routes/auth_multi_tenant.py', 'backend/routes/coordinador.py',
                 'backend/routes/estudiante.py', 'backend/services/subscription_quota.py',
                 'backend/models/institucion.py', 'backend/models/user.py',
                 'backend/models/academia.py', 'backend/models/ia_chat.py'):
        print(path + ' SHA256=' + hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), file=output)
    before_env, before_path = dict(os.environ), sys.path[:]
    code, module, result = 1, None, None
    try:
        with private_logs(), authorized_local_backend() as local:
            print('Destino confirmado: ' + local.label, file=output)
            print('Fábrica, decoradores, JWT, ORM y SQL reales; rate limiting en memoria; sin mensajes/proveedores.', file=output)
            module = importlib.import_module('testing.spec_001.test_integration')
            module.configure(local, fixture_version)
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            identifiers = list(test_ids(suite))
            mandatory = ('test_I1_', 'test_I2_', 'test_I3_', 'test_I4_')
            if len(identifiers) != 4 or any(not any(case in name for name in identifiers) for case in mandatory):
                raise SafetyError('Casos obligatorios de integración ausentes; ejecución bloqueada.')
            result = unittest.TextTestRunner(stream=output, verbosity=2, resultclass=PrivateResult).run(suite)
            cleaned = bool(module.JOURNALS) and all(
                journal.data['state'] == 'cleaned' and not journal.data['cleanup_errors']
                for journal in module.JOURNALS
            )
            code = 0 if result.wasSuccessful() and result.testsRun == 4 and not result.skipped and not result.expectedFailures and cleaned else 1
            print(f'Summary: tests={result.testsRun}, failures={len(result.failures)}, errors={len(result.errors)}, '
                  f'skips={len(result.skipped)}, expected_failures={len(result.expectedFailures)}', file=output)
            print('Cleanup SQL complete: ' + str(cleaned), file=output)
    except SafetyError as error:
        print('BLOQUEADO/FALLIDO: ' + str(error), file=output)
    except Exception:
        print('BLOQUEADO/FALLIDO: error interno; detalle privado omitido.', file=output)
    finally:
        if module is not None:
            print('\nResultados obtenidos y limpieza por conjunto:', file=output)
            for event in module.EVENTS:
                print(event, file=output)
            for journal in module.JOURNALS:
                print(f'Ownership: {journal.path.relative_to(ROOT)} | state={journal.data["state"]} '
                      f'| cleanup_errors={journal.data["cleanup_errors"]}', file=output)
            module.LOCAL = None
        restored = dict(os.environ) == before_env and sys.path == before_path
        print('Environment/path restored: ' + str(restored), file=output)
        if not restored:
            code = 1
        if result is None:
            print('I-1..I-4: no ejecutado; autorización/prerrequisitos incompletos.', file=output)
        print('Exit code: ' + str(code), file=output)
        content = output.getvalue()
        report.write_text(content, encoding='utf-8')
        print(content, end='')
        print('Reporte: ' + str(report.relative_to(ROOT)))
    return code


if __name__ == '__main__':
    raise SystemExit(main())