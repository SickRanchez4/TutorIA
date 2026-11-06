"""Opt-in manual system fixtures, private workbook lifecycle and read-only checks."""
from datetime import datetime, timezone
import getpass
import importlib
from pathlib import Path
import warnings
from urllib.parse import urlsplit

from openpyxl import Workbook
from sqlalchemy import MetaData, Table

from testing.cleanup import canonical, resolve_owned, string_uuid_columns
from testing.fixtures import FixtureBuilder
from testing.local_destination import SafetyError, verify_destination
from testing.ownership import ENTITIES, identity_column, validate_record


RUNTIME_ROOT = Path(__file__).resolve().parent / '.system-runtime'
CASES = ('S-1', 'S-2', 'S-3', 'S-3b')


def case_name(journal):
    validate_record(journal.data)
    if journal.data['mode'] != 'system':
        raise SafetyError('Se requiere un registro propio de sistema.')
    names = {r['ownership_marker'].get('nombre') for r in journal.data['resources']
             if r['entity'] == 'instituciones'}
    cases = [case for case in CASES if journal.name(case.lower() + '-institution') in names]
    if len(cases) != 1:
        raise SafetyError('No se puede identificar el escenario de sistema.')
    return cases[0]


def private_password(reader=None):
    """Refuse getpass fallback rather than expose a password on redirected stdin."""
    reader = reader or getpass.getpass
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        try:
            password = reader('Contraseña ficticia temporal (entrada oculta): ')
            repeated = reader('Repita la contraseña ficticia (entrada oculta): ')
        except getpass.GetPassWarning:
            raise SafetyError('No hay entrada oculta disponible; preparación bloqueada.') from None
    valid, _ = importlib.import_module('routes.auth_multi_tenant').validate_password(password)
    if password != repeated or not valid:
        raise SafetyError('Contraseña ficticia no válida o confirmación diferente; sin preparación.')
    return password


def workbook_path(journal):
    validate_record(journal.data)
    root = RUNTIME_ROOT.absolute()
    folder = root / journal.data['run_id']
    # Never follow operator-created links when creating/removing private artifacts.
    if root.resolve() != root or folder.resolve() != folder:
        raise SafetyError('Directorio temporal redirigido; operación bloqueada.')
    return folder / 'students.xlsx'


def write_workbook(journal, new_email, existing_email, password):
    path = workbook_path(journal)
    path.parent.mkdir(parents=True, exist_ok=False)
    book = Workbook()
    try:
        sheet = book.active
        sheet.title = 'Estudiantes'
        sheet.append(['email', 'first_name', 'last_name', 'phone', 'password'])
        sheet.append([new_email, 'Nuevo', 'SPEC001', '0000000000', password])
        sheet.append([existing_email, 'Ficticio', 'SPEC001', '0000000000', ''])
        # A strong password may start with '='; never turn it into an Excel formula.
        for row in sheet:
            for cell in row:
                cell.data_type = 's'
        book.save(path)
    finally:
        book.close()
    return path


def remove_workbook(journal):
    path = workbook_path(journal)
    if path.is_symlink():
        raise SafetyError('Excel temporal redirigido; no se elimina el enlace.')
    if path.exists():
        path.unlink()
    if path.parent.exists():
        path.parent.rmdir()  # Unexpected files block rather than broaden deletion.
    if path.exists() or path.parent.exists():
        raise SafetyError('Artefactos temporales restantes; limpieza incompleta.')


def prepare_system(local, journal, case, password):
    if case not in CASES or journal.data['mode'] != 'system' or journal.data['resources']:
        raise SafetyError('Use un registro de sistema independiente por escenario.')
    valid, _ = importlib.import_module('routes.auth_multi_tenant').validate_password(password)
    if not valid:
        raise SafetyError('Contraseña ficticia inválida; no se crean fixtures.')
    builder = FixtureBuilder(local, journal)
    builder.password = password
    suffix = case.lower()
    institution = builder.institution(suffix + '-institution')
    plan = builder.plan(suffix + '-plan', 2 if case == 'S-1' else 4)
    builder.subscription(institution, plan, datetime.now(timezone.utc).replace(tzinfo=None))
    coordinator = builder.user('coordinator', institution, 'coordinador')
    student = builder.user('student', institution)
    course = builder.course('course', institution)
    if case in {'S-1', 'S-2'}:
        # The real course view creates this row on GET; reserve before UI navigation.
        journal.reserve('configuracion_ia', dict(curso_id=course.id), course.id)
    if case == 'S-3':
        builder.enrollment(student, course)
    new_email = journal.name('new-student') + '@example.invalid'
    if case in {'S-1', 'S-2'}:
        if builder.models.User.query.filter_by(email=new_email).first() is not None:
            raise SafetyError('Email de alta ya existente; no se reserva ni adopta esa cuenta.')
        journal.reserve('users', dict(email=new_email, institucion_id=institution.id))
        journal.reserve('estudiante_cursos', dict(user_email=new_email, curso_id=course.id))
    if case == 'S-2':
        journal.reserve('estudiante_cursos', dict(user_id=student.id, curso_id=course.id))
        write_workbook(journal, new_email, student.email, password)
    if case in {'S-3', 'S-3b'}:
        journal.reserve('sesiones_chat', dict(user_id=student.id, curso_id=course.id,
                                             titulo='Nueva Conversación'))
    journal.state('ready')
    return dict(case=case, coordinator_email=coordinator.email, student_email=student.email,
                course_id=course.id, new_email=new_email if case in {'S-1', 'S-2'} else None)


def read_candidates(local, journal):
    validate_record(journal.data)
    if journal.data['destination_label'] != local.label:
        raise SafetyError('Registro y destino no coinciden.')
    # Independent read connection, including after the cleanup transaction committed.
    with local.db.engine.connect() as connection:
        if verify_destination(connection, local.database) != local.label:
            raise SafetyError('Destino cambiado; verificación bloqueada.')
        metadata = MetaData()
        tables = {('dbo', entity): Table(entity, metadata, schema='dbo',
                                         autoload_with=connection, resolve_fks=False) for entity in ENTITIES}
        string_uuid_columns(tables)
        return resolve_owned(connection, tables, journal)


def verify_system(local, journal):
    case = case_name(journal)
    if journal.data['state'] != 'ready':
        raise SafetyError('La comprobación del recorrido requiere fixtures listos, sin limpiar.')
    candidates = read_candidates(local, journal)
    for resource, row in candidates:
        if resource['state'] == 'planned':
            journal.committed(resource, row[identity_column(resource['entity'])])
    models = importlib.import_module('models')
    institution = next(r['id'] for r in journal.data['resources'] if r['entity'] == 'instituciones')
    course = next(r['id'] for r in journal.data['resources'] if r['entity'] == 'cursos')
    student_resource = next(r for r in journal.data['resources'] if r['entity'] == 'users'
                            and r['ownership_marker']['email'] == journal.name('student') + '@example.invalid')
    student = models.User.query.filter_by(email=student_resource['ownership_marker']['email'],
                                          institucion_id=institution).one()
    total_users = models.User.query.filter_by(institucion_id=institution).count()
    active_users = models.User.query.filter_by(institucion_id=institution, is_active=True).count()
    enrollments = models.EstudianteCurso.query.filter_by(curso_id=course).all()
    sessions = models.SesionChat.query.filter_by(curso_id=course).all()
    messages = models.MensajeChat.query.join(models.SesionChat).filter(models.SesionChat.curso_id == course).count()
    new_users = models.User.query.filter_by(email=journal.name('new-student') + '@example.invalid').all()
    own_ids = {(resource['entity'], canonical(row[identity_column(resource['entity'])])) for resource, row in candidates}
    all_owned = (all(('estudiante_cursos', canonical(row.id)) in own_ids for row in enrollments)
                 and all(('sesiones_chat', canonical(row.id)) in own_ids for row in sessions))
    student_unchanged = canonical(student.id) == canonical(student_resource['id'])
    counts = dict(users=total_users, active_users=active_users, new_users=len(new_users),
                  enrollments=len(enrollments), active_enrollments=sum(bool(e.is_active) for e in enrollments),
                  sessions=len(sessions), messages=messages, student_identity_unchanged=student_unchanged,
                  all_observed_children_owned=all_owned)
    common = student_unchanged and all_owned and messages == 0 and active_users == total_users
    if case == 'S-1':
        sql_matches = total_users == 2 and not new_users and not enrollments and not sessions
    elif case == 'S-2':
        new_owned = (len(new_users) == 1 and canonical(new_users[0].institucion_id) == canonical(institution)
                     and any(role.name == 'estudiante' for role in new_users[0].roles))
        expected_users = {canonical(student.id), canonical(new_users[0].id)} if new_owned else set()
        sql_matches = (total_users == 3 and new_owned and len(enrollments) == 2
                       and all(e.is_active for e in enrollments)
                       and {canonical(e.user_id) for e in enrollments} == expected_users and not sessions)
    elif case == 'S-3':
        sql_matches = (total_users == 2 and len(enrollments) == 1 and enrollments[0].is_active
                       and canonical(enrollments[0].user_id) == canonical(student.id) and len(sessions) == 1
                       and sessions[0].is_active and canonical(sessions[0].user_id) == canonical(student.id)
                       and sessions[0].titulo == 'Nueva Conversación')
    else:
        sql_matches = total_users == 2 and not enrollments and not sessions
    return dict(case=case, counts=counts, sql_condition_matches=bool(common and sql_matches),
                manual_ui_proven=False)


def reserve_course_config(local, journal):
    """Upgrade a ready pre-extension fixture before opening the real course view."""
    if case_name(journal) not in {'S-1', 'S-2'} or journal.data['state'] != 'ready':
        raise SafetyError('Esta reserva requiere un conjunto listo S-1/S-2, antes del recorrido.')
    if any(r['entity'] == 'configuracion_ia' for r in journal.data['resources']):
        raise SafetyError('La configuración ya está reservada; no se duplica el registro.')
    candidates = read_candidates(local, journal)
    courses = [row for resource, row in candidates if resource['entity'] == 'cursos']
    if len(courses) != 1:
        raise SafetyError('No se pudo comprobar la propiedad del curso; reserva bloqueada.')
    course_id = courses[0]['id']
    models = importlib.import_module('models')
    if models.ConfiguracionIA.query.filter_by(curso_id=course_id).first() is not None:
        raise SafetyError('La configuración ya existe sin reserva previa; investigar, no atribuir automáticamente.')
    journal.reserve('configuracion_ia', dict(curso_id=course_id), course_id)
    return dict(case=case_name(journal), course_id=course_id, intent_registered=True,
                sql_writes=False, manual_ui_proven=False)


def local_origin(value):
    parsed = urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname not in {'localhost', '127.0.0.1', '::1'}
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in {'', '/'} or parsed.query or parsed.fragment):
        raise SafetyError('Use únicamente un origen HTTP loopback sin credenciales ni rutas.')
    if parsed.port is None:
        raise SafetyError('Indique explícitamente el puerto HTTP local.')
    return value.rstrip('/')


def denied_http(local, journal, origin, password):
    """Real network login and denial; JWT never leaves the in-memory request headers."""
    import requests
    if case_name(journal) != 'S-3b':
        raise SafetyError('El complemento HTTP requiere un conjunto independiente S-3b.')
    origin = local_origin(origin)
    before = verify_system(local, journal)
    if not before['sql_condition_matches']:
        raise SafetyError('Datos de S-3b alterados; no se solicita la creación.')
    student = next(r for r in journal.data['resources'] if r['entity'] == 'users'
                   and r['ownership_marker']['email'] == journal.name('student') + '@example.invalid')
    course = next(r['id'] for r in journal.data['resources'] if r['entity'] == 'cursos')
    with requests.Session() as client:
        client.trust_env = False  # Do not route a local bearer token through an environment proxy.
        login = client.post(origin + '/api/auth/login', json=dict(
            email=student['ownership_marker']['email'], password=password), timeout=15, allow_redirects=False)
        if login.status_code != 200:
            raise SafetyError('Login ficticio no satisfactorio; no se registra su respuesta privada.')
        credentials = login.json()
        if (canonical(credentials.get('user', {}).get('id')) != canonical(student['id'])
                or not isinstance(credentials.get('token'), str) or not credentials['token']):
            raise SafetyError('La identidad HTTP no coincide con el fixture; petición bloqueada.')
        response = client.post(origin + '/api/estudiante/chat/sesiones', json=dict(curso_id=course),
                               headers={'Authorization': 'Bearer ' + credentials['token']},
                               timeout=15, allow_redirects=False)
        status = response.status_code
        expected_message = response.json().get('message') == 'No estás inscrito en este curso'
    after = verify_system(local, journal)
    return dict(case='S-3b', http_status=status, expected_message_matches=expected_message,
                sql=after, contract_matches=status == 403 and expected_message and after['sql_condition_matches'])