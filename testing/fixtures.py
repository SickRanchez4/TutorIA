"""Independent fictitious fixtures, using actual models and exclusive identities."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import importlib
import secrets
from types import SimpleNamespace
import uuid

from sqlalchemy import text
from werkzeug.security import generate_password_hash

from testing.local_destination import SafetyError, verify_destination


class FixtureBuilder:
    """Reserve intent before every insert; commit and journal one resource at a time."""

    def __init__(self, local, journal):
        if journal.data['destination_label'] != local.label or journal.data['state'] != 'preparing':
            raise SafetyError('Preparación no autorizada para este registro/destino.')
        self.local, self.journal = local, journal
        self.models = importlib.import_module('models')
        self.roles = {role.name: role for role in self.models.Role.query.filter(
            self.models.Role.name.in_(['coordinador', 'estudiante'])
        ).all()}
        if set(self.roles) != {'coordinador', 'estudiante'}:
            raise SafetyError('Roles requeridos ausentes; preparación bloqueada.')
        self.password = secrets.token_urlsafe(24) + 'Aa1!'

    def insert(self, entity, model, marker, values, role=None):
        if self.journal.data['state'] != 'preparing':
            raise SafetyError('La preparación de este registro ya terminó.')
        session = self.local.db.session
        try:
            # Revalidate the active connection before each write, not just the initial probe.
            if verify_destination(session.connection(), self.local.database) != self.local.label:
                raise SafetyError('Destino cambiado; preparación bloqueada.')
            session.execute(text(
                f'SELECT TOP (1) 1 FROM dbo.[{entity}] WITH (TABLOCKX, HOLDLOCK)'
            ))
            if model.query.filter_by(**marker).first() is not None:
                raise SafetyError('Marca ficticia ya utilizada; no se modifica el recurso existente.')
            if values.get('id') is not None and session.get(model, values['id']) is not None:
                raise SafetyError('Identidad ficticia ya utilizada; preparación bloqueada.')
            resource = self.journal.reserve(entity, marker, values.get('id'))
            item = model(**values)
            if role is not None:
                item.roles.append(self.roles[role])
            session.add(item)
            session.flush()
            identifier = item.id
            session.commit()
            self.journal.committed(resource, identifier)
            return item
        except Exception:
            session.rollback()
            raise SafetyError('Preparación parcial fallida; conserve el registro y ejecute limpieza.') from None

    def institution(self, suffix):
        identifier, name = str(uuid.uuid4()), self.journal.name(suffix)
        return self.insert('instituciones', self.models.Institucion,
                           dict(id=identifier, nombre=name),
                           dict(id=identifier, nombre=name, is_active=True))

    def plan(self, suffix, capacity):
        if capacity is not None and (type(capacity) is not int or capacity < 0):
            raise SafetyError('Capacidad ficticia inválida.')
        name = self.journal.name(suffix)
        return self.insert('planes', self.models.Plan, dict(nombre=name),
                           dict(nombre=name, max_cuentas=capacity, is_active=True))

    def subscription(self, institution, plan, reference):
        identifier = str(uuid.uuid4())
        marker = dict(id=identifier, institucion_id=institution.id, plan_id=plan.id)
        return self.insert('suscripciones', self.models.Suscripcion, marker,
                           dict(**marker, limite_tokens_mensual=1000,
                                fecha_inicio=reference - timedelta(days=1),
                                fecha_fin=reference + timedelta(days=30), is_active=True))

    def user(self, suffix, institution, role='estudiante', active=True):
        email = self.journal.name(suffix) + '@example.invalid'
        return self.insert('users', self.models.User,
                           dict(email=email, institucion_id=institution.id),
                           dict(id=str(uuid.uuid4()), email=email, institucion_id=institution.id,
                                password_hash=generate_password_hash(self.password),
                                first_name='Ficticio', last_name='SPEC001', phone='0000000000',
                                is_active=active, email_verified=False), role=role)

    def course(self, suffix, institution):
        marker = dict(nombre=self.journal.name(suffix), institucion_id=institution.id)
        return self.insert('cursos', self.models.Curso, marker, dict(**marker, is_active=True))

    def enrollment(self, user, course, active=True):
        return self.insert('estudiante_cursos', self.models.EstudianteCurso,
                           dict(user_id=user.id, curso_id=course.id),
                           dict(id=str(uuid.uuid4()), user_id=user.id, curso_id=course.id,
                                is_active=active))

    def prepare(self, case, capacity=4, reference=None, enrollment='active'):
        """Each call belongs to a new journal; no dependency on another test's data."""
        if case not in {'capacity', 'students', 'conversations'} or self.journal.data['resources']:
            raise SafetyError('Caso inválido o registro ya utilizado; cree una ejecución independiente.')
        if enrollment not in {'active', 'absent', 'inactive', 'other-course', 'other-user'}:
            raise SafetyError('Variante de matrícula inválida.')
        reference = reference or datetime.now(timezone.utc).replace(tzinfo=None)
        if reference.tzinfo is not None:
            raise SafetyError('Use una referencia UTC sin zona, conforme al almacenamiento actual.')
        primary = self.institution('primary')
        other = self.institution('other')
        finite = self.plan('finite', capacity)
        unlimited = self.plan('unlimited', None)
        self.subscription(primary, finite, reference)
        self.subscription(other, unlimited, reference)
        coordinator = self.user('coordinator', primary, 'coordinador')
        student = self.user('student', primary)
        foreign = self.user('foreign-student', other)
        data = SimpleNamespace(primary=primary, other=other, finite=finite, unlimited=unlimited,
                               coordinator=coordinator, student=student, foreign=foreign,
                               reference=reference)
        if case == 'capacity':
            data.inactive = self.user('inactive', primary, active=False)
        if case == 'students':
            data.incompatible = self.user('incompatible', primary, role=None)
        if case == 'conversations':
            data.course = self.course('course', primary)
            data.other_course = self.course('other-course', primary)
            if enrollment != 'absent':
                data.enrollment = self.enrollment(
                    foreign if enrollment == 'other-user' else student,
                    data.other_course if enrollment == 'other-course' else data.course,
                    active=enrollment != 'inactive',
                )
        self.journal.state('ready')
        return data


@contextmanager
def managed_fixtures(local, journal, case, **options):
    """Cleanup is installed before preparation, including partially committed inserts."""
    from testing.cleanup import cleanup_owned
    try:
        yield FixtureBuilder(local, journal).prepare(case, **options)
    finally:
        cleanup_owned(local, journal)