"""Explicit manual-system operations; never auto-run UI cases or accept SQL consent."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid

from testing.cleanup import cleanup_owned
from testing.local_destination import SafetyError, authorized_local_backend
from testing.ownership import EVIDENCE_ROOT, OwnershipJournal
from testing.run_integration import private_logs
from testing.run_tests import ROOT, git_output
from testing.system_support import (CASES, case_name, denied_http, local_origin, prepare_system,
                                    private_password, read_candidates, remove_workbook, workbook_path,
                                    verify_system, reserve_course_config)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sistema manual SPEC-001; SQL optativo y contraseña oculta.')
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare', help='Crear un conjunto propio; conserva datos hasta cleanup.')
    prepare.add_argument('--case', choices=CASES, required=True)
    for name in ('verify', 'deny-http', 'cleanup', 'reserve-config'):
        command = commands.add_parser(name)
        command.add_argument('--ownership', type=Path, required=True)
        if name == 'deny-http':
            command.add_argument('--origin', required=True, help='Origen HTTP loopback con puerto explícito.')
    args = parser.parse_args(argv)
    journal = None
    # Reject arbitrary journals and HTTP destinations before loading backend configuration.
    try:
        if args.command != 'prepare':
            journal = OwnershipJournal.load(args.ownership)
            case_name(journal)
        if args.command == 'deny-http':
            local_origin(args.origin)
    except (SafetyError, ValueError):
        print('Argumentos o registro no válidos; no se leyó configuración ni se conectó.')
        return 1
    version = git_output('rev-parse', 'HEAD')
    changes = git_output('status', '--short')
    fixture_version = version + '-dirty' if version != 'unavailable' and changes else version
    report = EVIDENCE_ROOT / ('system-' + args.command + '-' + str(uuid.uuid4()) + '.txt')
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open('x', encoding='utf-8') as handle:
        handle.write('SPEC-001 | mode=system | operación iniciada; sin resultado todavía.\n')
    lines = ['SPEC-001 | mode=system | command=' + args.command,
             'UTC: ' + datetime.now(timezone.utc).isoformat(), 'Commit: ' + version,
             'Cambios locales (rutas):\n' + changes,
             'Una preparación/verificación SQL no demuestra recorrido manual de interfaz.']
    for source in ('testing/run_system.py', 'testing/system_support.py', 'testing/ownership.py',
                   'testing/cleanup.py', 'testing/fixtures.py', 'testing/local_destination.py',
                   'backend/routes/coordinador.py', 'backend/routes/estudiante.py',
                   'backend/routes/auth_multi_tenant.py', 'frontend/src/views/EstudianteDashboard.vue'):
        lines.append(source + ' SHA256=' + hashlib.sha256((ROOT / source).read_bytes()).hexdigest())
    code = 1
    try:
        with private_logs(), authorized_local_backend() as local:
            lines.append('Destino confirmado: ' + local.label)
            if args.command == 'prepare':
                password = private_password()
                journal = OwnershipJournal.create(local.label, fixture_version, mode='system')
                print('Registro de recuperación: ' + str(journal.path.relative_to(ROOT)))
                try:
                    data = prepare_system(local, journal, args.case, password)
                except BaseException:
                    # The artifact contains a temporary password: try its removal even if SQL blocks.
                    try:
                        cleanup_owned(local, journal)
                    finally:
                        remove_workbook(journal)
                    raise
                finally:
                    password = None
                lines.append('Datos ficticios preparados: ' + json.dumps(data, ensure_ascii=False))
                lines.append('Recorridos S-1/S-2/S-3/S-3b: no ejecutado.')
                if args.case == 'S-2':
                    print('Excel local temporal (NO adjuntar como evidencia): ' + str(workbook_path(journal)))
                code = 0
            elif args.command == 'reserve-config':
                result = reserve_course_config(local, journal)
                lines.append('Reserva previa a interfaz: ' + json.dumps(result, ensure_ascii=False))
                code = 0
            elif args.command == 'verify':
                result = verify_system(local, journal)
                lines.append('Verificación SQL: ' + json.dumps(result, ensure_ascii=False))
                code = 0 if result['sql_condition_matches'] else 1
            elif args.command == 'deny-http':
                password = private_password()
                try:
                    result = denied_http(local, journal, args.origin, password)
                finally:
                    password = None
                lines.append('HTTP local saneado: ' + json.dumps(result, ensure_ascii=False))
                code = 0 if result['contract_matches'] else 1
            else:
                try:
                    cleanup_owned(local, journal)
                finally:
                    remove_workbook(journal)
                remaining = read_candidates(local, journal)
                if remaining:
                    raise SafetyError('Verificación posterior encontró filas propias; investigar.')
                lines.append('SQL postcommit (conexión independiente): cero recursos propios restantes.')
                lines.append('Excel/carpeta temporal: ausentes. Journal conservado.')
                code = 0
    except SafetyError as error:
        lines.append('BLOQUEADO/FALLIDO: ' + str(error))
    except (KeyboardInterrupt, EOFError):
        lines.append('INTERRUMPIDO: revisar el registro y recuperar la limpieza antes de continuar.')
    except Exception:
        lines.append('BLOQUEADO/FALLIDO: detalle privado omitido; revisar registro y artefactos temporales.')
    finally:
        if journal is not None:
            lines.append('Ownership: ' + str(journal.path.relative_to(ROOT)))
            lines.append('Estado del registro: ' + journal.data['state'])
            lines.append('Errores de limpieza: ' + json.dumps(journal.data['cleanup_errors']))
            try:
                lines.append('Excel temporal presente: ' + str(workbook_path(journal).exists()))
            except SafetyError:
                code = 1
                lines.append('Artefacto temporal no verificable; requiere investigación.')
        lines.append('Exit code: ' + str(code))
        report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print('\n'.join(lines))
        print('Reporte saneado: ' + str(report.relative_to(ROOT)))
    return code


if __name__ == '__main__':
    raise SystemExit(main())