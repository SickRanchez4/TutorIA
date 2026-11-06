"""I-1..I-4: real algorithms, decorators, ORM and local SQL; no provider requests."""
from contextlib import contextmanager
from datetime import datetime
import importlib
import secrets
import unittest

from flask_jwt_extended import create_access_token
from sqlalchemy import text

from testing.cleanup import cleanup_owned
from testing.fixtures import FixtureBuilder
from testing.local_destination import SafetyError, verify_destination
from testing.ownership import OwnershipJournal


LOCAL = None
VERSION = None
EVENTS = []
JOURNALS = []


def configure(local, version):
    """Called only by the opt-in runner, inside the confirmed real app context."""
    global LOCAL, VERSION
    LOCAL, VERSION = local, version
    EVENTS.clear()
    JOURNALS.clear()


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        if LOCAL is None:
            raise SafetyError('Integración requiere ejecutor optativo y destino autorizado.')
        self.local = LOCAL
        self.models = importlib.import_module('models')
        self.quota = importlib.import_module('services.subscription_quota')
        self.coordinator = importlib.import_module('routes.coordinador')

    def record(self, description):
        EVENTS.append(f'{self.id().split(".")[-1]} | {description}')

    @contextmanager
    def dataset(self, case, **options):
        journal = OwnershipJournal.create(self.local.label, VERSION)
        JOURNALS.append(journal)
        self.record('ownership=' + str(journal.path.relative_to(journal.path.parents[2])))
        try:
            yield FixtureBuilder(self.local, journal).prepare(case, **options), journal
        finally:
            cleanup_owned(self.local, journal)
            self.assertEqual(journal.data['state'], 'cleaned')
            self.record('Limpieza SQL confirmada; sin recursos propios restantes.')

    def counts(self, institution_id):
        return self.models.User.query.filter_by(institucion_id=institution_id).count()

    def write_owned(self, item, journal, field, value):
        """Only non-marker fields of an exactly registered fixture may be updated."""
        entity = item.__tablename__
        from testing.cleanup import canonical
        owned = next((resource for resource in journal.data['resources']
                      if resource['entity'] == entity and canonical(resource['id']) == canonical(item.id)), None)
        if owned is None or field in owned['ownership_marker'] or field not in {'max_cuentas', 'is_active'}:
            raise SafetyError('Actualización no atribuible a la ejecución; bloqueada.')
        if verify_destination(self.local.db.session.connection(), self.local.database) != self.local.label:
            raise SafetyError('Destino cambiado; actualización bloqueada.')
        setattr(item, field, value)
        self.local.db.session.commit()

    def test_I1_account_capacity_real_counts(self):
        """Active count includes coordinator but excludes inactive and foreign accounts."""
        with self.dataset('capacity', capacity=3, reference=datetime(2026, 9, 30, 12)) as (data, journal):
            User = self.models.User
            self.assertEqual(self.counts(data.primary.id), 3)
            self.assertEqual(User.query.filter_by(institucion_id=data.primary.id, is_active=True).count(), 2)
            self.assertEqual(User.query.filter_by(institucion_id=data.primary.id, is_active=False).count(), 1)
            self.assertEqual(self.counts(data.other.id), 1)
            self.assertEqual(self.quota.account_creation_allowed(data.primary.id, data.reference), (True, None))
            self.record('Inferior: activas=2, inactiva=1, ajena=1, límite=3; permitido=True.')
            self.write_owned(data.finite, journal, 'max_cuentas', 2)
            self.assertEqual(self.quota.account_creation_allowed(data.primary.id, data.reference),
                             (False, 'Límite de cuentas alcanzado para el plan asignado'))
            self.record('Alcanzada: activas=2, límite=2; permitido=False.')
            self.write_owned(data.finite, journal, 'max_cuentas', None)
            self.assertEqual(self.quota.account_creation_allowed(data.primary.id, data.reference), (True, None))
            self.record('Ilimitada: max_cuentas=NULL; permitido=True.')

    def test_I2_student_creation_and_reuse(self):
        """Caller commits the actual helper's flush and verifies role and uniqueness in SQL."""
        with self.dataset('students') as (data, journal):
            email = journal.name('new-student') + '@example.invalid'
            self.assertIsNone(self.models.User.query.filter_by(email=email).first())
            intent = journal.reserve('users', dict(email=email, institucion_id=data.primary.id))
            before = self.counts(data.primary.id)
            password = secrets.token_urlsafe(24) + 'Aa1!'
            try:
                user, created = self.coordinator._get_or_create_estudiante(
                    email, 'Ficticio', 'Nuevo', '0000000000', password, data.primary.id,
                )
                identifier = user.id
                self.local.db.session.commit()
                journal.committed(intent, identifier)
            except Exception:
                self.local.db.session.rollback()
                raise
            self.local.db.session.expire_all()
            stored = self.models.User.query.filter_by(email=email).one()
            self.assertTrue(created)
            self.assertEqual(str(stored.institucion_id).casefold(), str(data.primary.id).casefold())
            self.assertEqual({role.name for role in stored.roles}, {'estudiante'})
            self.assertEqual(self.counts(data.primary.id), before + 1)
            from testing.cleanup import canonical
            self.assertEqual(canonical(stored.id), canonical(identifier))
            reused, created_again = self.coordinator._get_or_create_estudiante(
                '  ' + email.upper() + '  ', 'Ignorado', 'Ignorado', '0000000000', '', data.primary.id,
            )
            self.local.db.session.commit()
            self.assertFalse(created_again)
            self.assertEqual(canonical(reused.id), canonical(identifier))
            self.assertEqual(self.models.User.query.filter_by(email=email).count(), 1)
            self.assertEqual(self.counts(data.primary.id), before + 1)
            self.record(f'Alta: created=True, cuentas={before}->{before + 1}, rol=estudiante; reutilización: created=False, misma identidad y una fila.')

    def test_I3_student_rejections_without_duplicates(self):
        """Tenant, role and exhausted capacity reject without extra committed accounts."""
        with self.dataset('students', capacity=3) as (data, journal):
            before = self.counts(data.primary.id)
            foreign_before = self.counts(data.other.id)
            scenarios = ((data.foreign.email, self.coordinator.StudentTenantConflict, 'otra institución'),
                         (data.incompatible.email, ValueError, 'rol incompatible'),
                         (journal.name('denied-student') + '@example.invalid', self.coordinator.AccountLimitReached, 'capacidad agotada'))
            for email, error, description in scenarios:
                with self.subTest(reason=description):
                    if error is self.coordinator.AccountLimitReached:
                        self.assertIsNone(self.models.User.query.filter_by(email=email).first())
                        # Reserve even an expected rejection: an unexpected insert is recoverable.
                        journal.reserve('users', dict(email=email, institucion_id=data.primary.id))
                    try:
                        with self.assertRaises(error):
                            self.coordinator._get_or_create_estudiante(
                                email, 'Ficticio', 'Rechazado', '0000000000',
                                secrets.token_urlsafe(24) + 'Aa1!', data.primary.id,
                            )
                    finally:
                        self.local.db.session.rollback()
                    self.assertEqual(self.counts(data.primary.id), before)
                    self.assertEqual(self.counts(data.other.id), foreign_before)
                    if error is self.coordinator.AccountLimitReached:
                        self.assertIsNone(self.models.User.query.filter_by(email=email).first())
                    else:
                        self.assertEqual(self.models.User.query.filter_by(email=email).count(), 1)
                    self.record(f'Rechazo {description}: {error.__name__}, conteos propios/ajenos intactos, sin duplicados.')

    def test_I4_http_conversation_enrollment_variants(self):
        """Real JWT and role decorators plus persisted 201/403 for five independent datasets."""
        for enrollment in ('active', 'absent', 'inactive', 'other-course', 'other-user'):
            with self.subTest(enrollment=enrollment), self.dataset('conversations', enrollment=enrollment) as (data, journal):
                # Store identities before HTTP teardown expires/removes the scoped session.
                user_id, course_id = data.student.id, data.course.id
                token = create_access_token(identity=str(user_id))
                headers = {'Authorization': 'Bearer ' + token}
                self.local.db.session.rollback()
                titles = ('Nueva Conversación', 'Título explícito SPEC001') if enrollment == 'active' else ('Nueva Conversación',)
                for title in titles:
                    self.assertEqual(self.models.SesionChat.query.filter_by(user_id=user_id, curso_id=course_id, titulo=title).count(), 0)
                    intent = journal.reserve('sesiones_chat', dict(user_id=user_id, curso_id=course_id, titulo=title))
                    before = self.models.SesionChat.query.filter_by(user_id=user_id).count()
                    body = {'curso_id': course_id}
                    if title != 'Nueva Conversación':
                        body['titulo'] = '  ' + title + '  '
                    response = self.local.app.test_client().post('/api/estudiante/chat/sesiones', json=body, headers=headers)
                    payload = response.get_json()
                    # Journal the committed identity before any assertion can fail.
                    self.local.db.session.expire_all()
                    persisted = self.models.SesionChat.query.filter_by(user_id=user_id, curso_id=course_id, titulo=title).all()
                    if len(persisted) == 1:
                        journal.committed(intent, persisted[0].id)
                    expected = 201 if enrollment == 'active' else 403
                    self.assertEqual(response.status_code, expected)
                    if expected == 201:
                        self.assertEqual(len(persisted), 1)
                        session = payload['sesion']
                        self.assertEqual(str(session['user_id']).casefold(), str(user_id).casefold())
                        self.assertEqual(session['curso_id'], course_id)
                        self.assertEqual(session['titulo'], title)
                        self.assertEqual(str(session['id']).casefold(), str(persisted[0].id).casefold())
                        self.assertEqual(self.models.SesionChat.query.filter_by(user_id=user_id).count(), before + 1)
                    else:
                        self.assertEqual(payload, {'message': 'No estás inscrito en este curso'})
                        self.assertEqual(len(persisted), 0)
                        self.assertEqual(self.models.SesionChat.query.filter_by(user_id=user_id).count(), before)
                    self.record(f'Matrícula={enrollment}, título={title}; HTTP esperado/obtenido={expected}, persistidas={len(persisted)}.')
                # No message/provider operation belongs to this integration case.
                self.assertEqual(self.local.db.session.execute(text(
                    'SELECT COUNT(*) FROM dbo.mensajes_chat m JOIN dbo.sesiones_chat s ON s.id=m.sesion_chat_id WHERE s.user_id=:user_id'
                ), {'user_id': user_id}).scalar_one(), 0)