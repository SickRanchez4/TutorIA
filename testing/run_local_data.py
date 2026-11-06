"""Explicit authorization, fixture preparation and recovery; no integration suite yet."""
import argparse
from pathlib import Path

from testing.cleanup import cleanup_owned
from testing.fixtures import FixtureBuilder
from testing.local_destination import SafetyError, authorized_local_backend
from testing.ownership import OwnershipJournal
from testing.run_tests import git_output


def main(argv=None):
    parser = argparse.ArgumentParser(description='Datos ficticios locales SPEC-001; requiere confirmación interactiva.')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('check', help='Validar y confirmar destino; no preparar datos.')
    prepare = commands.add_parser('prepare', help='Preparar fixtures propios y conservar registro para su limpieza.')
    prepare.add_argument('--case', choices=('capacity', 'students', 'conversations'), required=True)
    recover = commands.add_parser('cleanup', help='Revalidar y limpiar solo una ejecución registrada.')
    recover.add_argument('--ownership', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # Validate journal BEFORE reading any backend secret or opening a connection.
        journal = OwnershipJournal.load(args.ownership) if args.command == 'cleanup' else None
        with authorized_local_backend() as local:
            if args.command == 'prepare':
                version = git_output('rev-parse', 'HEAD')
                if version != 'unavailable' and git_output('status', '--porcelain'):
                    version += '-dirty'
                journal = OwnershipJournal.create(local.label, version)
                print('Registro de recuperación: ' + str(journal.path.relative_to(Path(__file__).resolve().parents[1])))
                try:
                    FixtureBuilder(local, journal).prepare(args.case)
                except Exception:
                    cleanup_owned(local, journal)
                    raise
                print('Fixtures ficticios preparados; requieren limpieza explícita. No se ejecutó integración.')
            elif args.command == 'cleanup':
                cleanup_owned(local, journal)
                print('Limpieza propia confirmada; registro conservado como evidencia.')
            else:
                print('Destino confirmado; sin creación ni borrado de fixtures.')
        return 0
    except SafetyError as error:
        print(str(error))
        return 1
    except Exception:
        print('Operación bloqueada; detalle privado no registrado. Conserve el registro si existe.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())