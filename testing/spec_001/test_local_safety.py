"""T14 controlled safety checks; all SQL/configuration boundaries are simulated."""
import copy
import getpass
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import uuid
import warnings

from openpyxl import load_workbook

from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.dialects.mssql import dialect
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.dialects.mssql.pyodbc import MSDialect_pyodbc
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.dml import Delete

from testing import cleanup, fixtures, local_destination, ownership, system_support
from testing.local_destination import SafetyError
from testing.support import isolated_backend


class Result:
    def __init__(self, rows=(), rowcount=0):
        self.rows, self.rowcount = list(rows), rowcount

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None

    def __iter__(self):
        return iter(self.rows)


class ControlledSQL:
    """Evaluate only Core equality selects/deletes, not a SQL Server substitute."""
    def __init__(self, rows, foreign_keys):
        self.dialect = dialect()
        self.rows = copy.deepcopy(rows)
        self.foreign_keys = foreign_keys
        self.deletes = []
        self.fail_entity = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execution_options(self, **options):
        return self

    @contextmanager
    def begin(self):
        before = copy.deepcopy(self.rows)
        try:
            yield
        except Exception:
            self.rows = before
            raise

    def accepts(self, expression, row):
        if expression is None:
            return True
        if isinstance(expression, BooleanClauseList):
            return all(self.accepts(clause, row) for clause in expression.clauses)
        if isinstance(expression, BinaryExpression):
            return cleanup.canonical(row[expression.left.name]) == cleanup.canonical(expression.right.value)
        raise AssertionError('Unexpected controlled predicate')

    def execute(self, statement):
        if isinstance(statement, (Select, Delete)):
            table = statement.get_final_froms()[0] if isinstance(statement, Select) else statement.table
            key = (table.schema, table.name)
            matches = [row for row in self.rows.get(key, []) if self.accepts(statement.whereclause, row)]
            if isinstance(statement, Select):
                return Result(matches)
            if table.name == self.fail_entity:
                raise RuntimeError('Injected deletion failure')
            self.deletes.append(table.name)
            self.rows[key] = [row for row in self.rows.get(key, []) if row not in matches]
            return Result(rowcount=len(matches))
        if 'sys.foreign_keys' in str(statement):
            return Result(self.foreign_keys)
        if 'TABLOCKX' in str(statement):
            return Result()
        raise AssertionError('Unexpected controlled SQL')


class SafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(temporary)
        self.enterContext(patch.object(ownership, 'EVIDENCE_ROOT', self.root))
        self.enterContext(patch.object(local_destination, 'local_names', return_value={'machine'}))
        self.journal = ownership.OwnershipJournal.create('machine / test-db', 'a' * 40)

    def test_T10_accept_only_verified_local_url_forms(self):
        for value in ('mssql+pyodbc://localhost/test-db?driver=ODBC+Driver+18+for+SQL+Server',
                      'mssql+pyodbc://machine/test-db',
                      'mssql+pyodbc://[::1]/test-db',
                      'mssql+pyodbc:///?odbc_connect=DRIVER%3DX%3BSERVER%3Dmachine%5CLOCAL%3BDATABASE%3Dtest-db%3BTrusted_Connection%3Dyes'):
            with self.subTest(form=value.split('?')[0]):
                self.assertEqual(local_destination.connection_target(value)[1], 'test-db')

    def test_T10_reject_remote_ambiguous_or_redirected_connections(self):
        values = ('sqlite:///local.db', 'mssql+pyodbc://remote/test-db',
                  'mssql+pyodbc://localhost/test-db?Failover_Partner=remote',
                  'mssql+pyodbc:///?odbc_connect=SERVER%3Dlocalhost%3BSERVER%3Dremote%3BDATABASE%3Dtest-db',
                  'mssql+pyodbc:///?odbc_connect=SERVER%3Dlocalhost%3BDATABASE%3Dtest-db%3BFailover_Partner%3Dremote',
                  'mssql+pyodbc:///?odbc_connect=SERVER%3Dlocalhost%2C123%2Cremote%3BDATABASE%3Dtest-db')
        for value in values:
            with self.subTest(form=value.split('?')[0]), self.assertRaises(SafetyError):
                local_destination.connection_target(value)

    def test_T10_environment_conflict_prevents_connection(self):
        with patch.dict('os.environ', {'DATABASE_URL': 'other'}, clear=True), \
                patch.object(local_destination.dotenv, 'dotenv_values', return_value={'DATABASE_URL': 'local'}), \
                patch.object(local_destination, 'create_engine') as engine:
            with self.assertRaises(SafetyError):
                with local_destination.authorized_local_backend():
                    self.fail('Unauthorized context entered')
            engine.assert_not_called()

    def test_T10_existing_environment_precedes_factory_configuration(self):
        values = {'DATABASE_URL': 'mssql+pyodbc://localhost/test-db', 'JWT_SECRET_KEY': 'synthetic-only'}
        with patch.dict('os.environ', {}, clear=True), \
                patch.object(local_destination.dotenv, 'dotenv_values', return_value=values):
            result = local_destination.read_existing_environment()
        self.assertEqual(result['DATABASE_URL'], values['DATABASE_URL'])
        self.assertEqual(result['RATELIMIT_STORAGE_URI'], 'memory://')

    def test_T10_refusal_prevents_factory_import(self):
        probe = Mock()
        probe.connect.return_value.__enter__ = Mock(return_value=Mock())
        probe.connect.return_value.__exit__ = Mock(return_value=False)
        with patch.object(local_destination, 'read_existing_environment', return_value={
                'DATABASE_URL': 'mssql+pyodbc://localhost/test-db'}), \
                patch.object(local_destination, 'create_engine', return_value=probe), \
                patch.object(local_destination, 'verify_destination', return_value='machine / test-db'), \
                patch.object(local_destination.importlib, 'import_module') as factory:
            with self.assertRaises(SafetyError):
                with local_destination.authorized_local_backend(confirm=lambda _: ''):
                    self.fail('Unauthorized writes')
            factory.assert_not_called()
            probe.dispose.assert_called_once()

    def test_T10_confirmation_requires_exact_destination(self):
        for response in ('yes', '', 'AUTORIZO machine / other-db', None):
            with self.subTest(response=response), self.assertRaises(SafetyError):
                local_destination.confirm_destination('machine / test-db', lambda _: response)
        local_destination.confirm_destination('machine / test-db', lambda _: 'AUTORIZO machine / test-db')

    def schema_probe(self, **overrides):
        row = dict(machine='machine', server='machine', database_name='test-db', metadata_access=1)
        row.update(overrides)
        connection, inspector = Mock(), Mock()
        identity = Mock()
        identity.mappings.return_value.one.return_value = row
        triggers, permissions, roles = Mock(), Mock(), Mock()
        triggers.scalar_one.return_value = 0
        permissions.scalar_one.return_value = 0
        roles.scalars.return_value.all.return_value = ['coordinador', 'estudiante']
        connection.execute.side_effect = [identity, triggers, permissions, roles]
        inspector.get_table_names.return_value = list(local_destination.REQUIRED_COLUMNS)
        inspector.get_columns.side_effect = lambda table, **_: [dict(name=name) for name in local_destination.REQUIRED_COLUMNS[table]]
        inspector.get_pk_constraint.side_effect = lambda table, **_: dict(
            constrained_columns=(['user_id', 'role_id'] if table == 'user_roles'
                                 else ['curso_id'] if table == 'configuracion_ia' else ['id']))
        inspector.get_foreign_keys.side_effect = lambda table, **_: [dict(
            constrained_columns=[source], referred_columns=[target], referred_table=parent,
            referred_schema='dbo') for source, parent, target in local_destination.REQUIRED_FKS.get(table, ())]
        return connection, inspector, triggers, roles

    def test_T10_read_only_identity_schema_and_roles(self):
        connection, inspector, _, _ = self.schema_probe()
        with patch.object(local_destination, 'inspect', return_value=inspector):
            self.assertEqual(local_destination.verify_destination(connection, 'test-db'), 'machine / test-db')
        self.assertTrue(all(str(call.args[0]).lstrip().startswith('SELECT') for call in connection.execute.call_args_list))

    def test_T10_wrong_identity_database_or_metadata_blocks(self):
        for override in ({'machine': 'remote'}, {'database_name': 'other'}, {'metadata_access': 0}):
            connection, inspector, _, _ = self.schema_probe(**override)
            with patch.object(local_destination, 'inspect', return_value=inspector), self.assertRaises(SafetyError):
                local_destination.verify_destination(connection, 'test-db')

    def test_T10_missing_schema_roles_fk_or_trigger_blocks(self):
        for defect in ('tables', 'columns', 'pk', 'fk', 'roles', 'triggers'):
            connection, inspector, triggers, roles = self.schema_probe()
            if defect == 'tables':
                inspector.get_table_names.return_value = []
            if defect == 'columns':
                inspector.get_columns.side_effect = lambda *a, **k: []
            if defect == 'pk':
                inspector.get_pk_constraint.side_effect = lambda *a, **k: {'constrained_columns': []}
            if defect == 'fk':
                inspector.get_foreign_keys.side_effect = lambda *a, **k: []
            if defect == 'roles':
                roles.scalars.return_value.all.return_value = ['estudiante']
            if defect == 'triggers':
                triggers.scalar_one.return_value = 1
            with self.subTest(defect=defect), patch.object(local_destination, 'inspect', return_value=inspector), self.assertRaises(SafetyError):
                local_destination.verify_destination(connection, 'test-db')

    def test_T10_insufficient_cleanup_permission_blocks(self):
        connection, inspector, _, _ = self.schema_probe()
        responses = list(connection.execute.side_effect)
        responses[2].scalar_one.return_value = 1
        connection.execute.side_effect = responses
        with patch.object(local_destination, 'inspect', return_value=inspector), self.assertRaises(SafetyError):
            local_destination.verify_destination(connection, 'test-db')

    def test_T11_intent_survives_before_commit_and_reload(self):
        item = self.journal.reserve('planes', {'nombre': self.journal.name('finite')})
        loaded = ownership.OwnershipJournal.load(self.journal.path)
        self.assertIsNone(loaded.data['resources'][0]['id'])
        self.assertEqual(loaded.data['resources'][0]['state'], 'planned')
        self.journal.committed(item, 10)
        self.assertEqual(ownership.OwnershipJournal.load(self.journal.path).data['resources'][0]['id'], 10)

    def test_T11_atomic_replace_failure_preserves_previous_json(self):
        previous = self.journal.path.read_bytes()
        with patch.object(ownership.os, 'replace', side_effect=OSError('Injected replace failure')):
            with self.assertRaises(SafetyError):
                self.journal.reserve('planes', {'nombre': self.journal.name('finite')})
        self.assertEqual(self.journal.path.read_bytes(), previous)
        self.assertFalse(list(self.journal.path.parent.glob('.ownership-*')))

    def test_T11_rejects_secret_fields_unowned_parent_and_unknown_entities(self):
        with self.assertRaises(SafetyError):
            self.journal.reserve('roles', {'nombre': self.journal.name('role')})
        with self.assertRaises(SafetyError):
            self.journal.reserve('users', {'email': self.journal.name('user') + '@example.invalid',
                                          'institucion_id': str(uuid.uuid4())})
        data = copy.deepcopy(self.journal.data)
        data['password'] = 'not-a-real-secret'
        with self.assertRaises(SafetyError):
            ownership.validate_record(data)

    def test_T11_duplicate_json_keys_and_wrong_paths_block(self):
        self.journal.path.write_text('{"spec_id":"SPEC-001","spec_id":"SPEC-001"}', encoding='utf-8')
        with self.assertRaises(SafetyError):
            ownership.OwnershipJournal.load(self.journal.path)
        with self.assertRaises(SafetyError):
            ownership.OwnershipJournal.load(self.root / 'other.json')

    def data_world(self, include_session=True):
        institution_id, user_id = str(uuid.uuid4()), str(uuid.uuid4())
        resources = [
            ('planes', 10, {'nombre': self.journal.name('finite')}),
            ('instituciones', institution_id, {'id': institution_id, 'nombre': self.journal.name('primary')}),
            ('suscripciones', str(uuid.uuid4()), {'institucion_id': institution_id, 'plan_id': 10}),
            ('users', user_id, {'email': self.journal.name('student') + '@example.invalid', 'institucion_id': institution_id}),
            ('cursos', 20, {'nombre': self.journal.name('course'), 'institucion_id': institution_id}),
            ('estudiante_cursos', str(uuid.uuid4()), {'user_id': user_id, 'curso_id': 20}),
        ]
        if include_session:
            resources.append(('sesiones_chat', str(uuid.uuid4()), {'user_id': user_id, 'curso_id': 20, 'titulo': 'Nueva Conversación'}))
        rows = {}
        for entity, identifier, marker in resources:
            if entity == 'suscripciones':
                marker = dict(marker, id=identifier)
            item = self.journal.reserve(entity, marker, identifier)
            self.journal.committed(item, identifier)
            rows[('dbo', entity)] = [dict(marker, id=identifier)]
        rows[('dbo', 'user_roles')] = [{'user_id': user_id, 'role_id': 2}]
        self.journal.state('ready')
        foreign_keys = []
        for entity, references in local_destination.REQUIRED_FKS.items():
            for source, parent, target in references:
                foreign_keys.append(dict(constraint_id=len(foreign_keys), is_disabled=False, is_not_trusted=False,
                                         child_schema='dbo', child_table=entity, child_column=source,
                                         parent_schema='dbo', parent_table=parent, parent_column=target))
        return rows, foreign_keys

    @contextmanager
    def controlled_cleanup(self, rows, foreign_keys):
        connection = ControlledSQL(rows, foreign_keys)
        metadata = MetaData()
        tables = {}
        keys = {('dbo', entity) for entity in (*ownership.ENTITIES, 'user_roles')} | set(rows)
        for schema, name in keys:
            fields = set().union(*(row.keys() for row in rows.get((schema, name), [])))
            fields |= ({'user_id', 'role_id'} if name == 'user_roles' else {ownership.identity_column(name)})
            fields |= ownership.MARKER_KEYS.get(name, set())
            tables[(schema, name)] = Table(name, metadata, *(Column(field, Integer if field in {'role_id', 'curso_id', 'plan_id'}
                                                  or (field == 'id' and name in {'planes', 'cursos'}) else String)
                                                  for field in sorted(fields)), schema=schema)
        local = SimpleNamespace(label='machine / test-db', database='test-db', db=Mock())
        local.db.engine.connect.return_value = connection
        with patch.object(cleanup, 'verify_destination', return_value=local.label), \
                patch.object(cleanup, 'Table', side_effect=lambda name, *args, schema, **kwargs: tables[(schema, name)]):
            yield local, connection

    def test_T13_cleanup_in_fk_order_without_shared_role_delete(self):
        rows, foreign_keys = self.data_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, self.journal)
            for row_list in connection.rows.values():
                self.assertEqual(row_list, [])
            self.assertNotIn('roles', connection.deletes)
            self.assertLess(connection.deletes.index('sesiones_chat'), connection.deletes.index('users'))
            self.assertLess(connection.deletes.index('estudiante_cursos'), connection.deletes.index('cursos'))
            self.assertEqual(self.journal.data['state'], 'cleaned')
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))

    def test_T13_recovery_after_commit_before_identity_record(self):
        marker = {'nombre': self.journal.name('finite')}
        self.journal.reserve('planes', marker)
        # A crash before recording a parent's ID cannot have already created its children.
        rows, foreign_keys = {('dbo', 'planes'): [dict(marker, id=10)]}, []
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))
            self.assertFalse(any(connection.rows.values()))

    def test_T13_session_recovery_from_owned_pair_and_title(self):
        rows, foreign_keys = self.data_world()
        resource = self.journal.data['resources'][-1]
        resource.update(id=None, state='planned')
        self.journal.save()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))
            self.assertFalse(connection.rows[('dbo', 'sesiones_chat')])

    def test_T13_unexpected_cascade_dependent_blocks_all_deletes(self):
        rows, foreign_keys = self.data_world()
        session_id = rows[('dbo', 'sesiones_chat')][0]['id']
        rows[('dbo', 'mensajes_chat')] = [{'id': str(uuid.uuid4()), 'sesion_chat_id': session_id}]
        foreign_keys.append(dict(constraint_id=100, is_disabled=False, is_not_trusted=False,
                                 child_schema='dbo', child_table='mensajes_chat', child_column='sesion_chat_id',
                                 parent_schema='dbo', parent_table='sesiones_chat', parent_column='id'))
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])
        self.assertEqual(connection.rows, rows)
        self.assertEqual(self.journal.data['state'], 'cleanup_failed')

    def test_T13_unowned_cross_schema_child_blocks(self):
        rows, foreign_keys = self.data_world()
        user_id = rows[('dbo', 'users')][0]['id']
        rows[('other', 'audit')] = [{'id': 1, 'user_id': user_id}]
        foreign_keys.append(dict(constraint_id=100, is_disabled=False, is_not_trusted=False,
                                 child_schema='other', child_table='audit', child_column='user_id',
                                 parent_schema='dbo', parent_table='users', parent_column='id'))
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T13_disabled_or_untrusted_fk_blocks(self):
        rows, foreign_keys = self.data_world()
        for flag in ('is_disabled', 'is_not_trusted'):
            altered = copy.deepcopy(foreign_keys)
            altered[0][flag] = True
            with self.subTest(flag=flag), self.controlled_cleanup(rows, altered) as (local, connection), self.assertRaises(SafetyError):
                cleanup.cleanup_owned(local, self.journal)
            self.assertEqual(connection.deletes, [])

    def test_T13_changed_schema_during_locking_blocks(self):
        rows, foreign_keys = self.data_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            execute = connection.execute
            snapshots = 0
            def changed(statement):
                nonlocal snapshots
                if 'sys.foreign_keys' in str(statement):
                    snapshots += 1
                    if snapshots == 2:
                        return Result([])
                return execute(statement)
            connection.execute = changed
            with self.assertRaises(SafetyError):
                cleanup.cleanup_owned(local, self.journal)
            self.assertEqual(connection.deletes, [])

    def test_T13_altered_marker_or_duplicate_identity_blocks(self):
        rows, foreign_keys = self.data_world()
        rows[('dbo', 'users')][0]['email'] = 'foreign@example.invalid'
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T13_ambiguous_session_recovery_blocks(self):
        rows, foreign_keys = self.data_world()
        rows[('dbo', 'sesiones_chat')].append(dict(rows[('dbo', 'sesiones_chat')][0], id=str(uuid.uuid4())))
        self.journal.data['resources'][-1].update(id=None, state='planned')
        self.journal.save()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T13_mismatched_destination_blocks_before_dml(self):
        rows, foreign_keys = self.data_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            local.label = 'machine / other-db'
            with self.assertRaises(SafetyError):
                cleanup.cleanup_owned(local, self.journal)
            self.assertEqual(connection.deletes, [])

    def test_T13_cleanup_failure_rolls_back_and_can_recover(self):
        rows, foreign_keys = self.data_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            connection.fail_entity = 'users'
            with self.assertRaises(SafetyError):
                cleanup.cleanup_owned(local, self.journal)
            self.assertEqual(connection.rows, rows)
            self.assertEqual(ownership.OwnershipJournal.load(self.journal.path).data['state'], 'cleanup_failed')
            connection.fail_entity = None
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))
            self.assertFalse(any(connection.rows.values()))

    def test_T13_reflected_uuid_columns_accept_journal_strings(self):
        identifier = str(uuid.uuid4())
        table = Table('uuid_check', MetaData(), Column('id', UNIQUEIDENTIFIER(as_uuid=True)))
        cleanup.string_uuid_columns({('dbo', 'uuid_check'): table})
        processor = table.c.id.type.bind_processor(MSDialect_pyodbc())
        self.assertEqual(processor(identifier), identifier.replace('-', ''))

    def fixture_builder(self, backend):
        real_models = __import__('models')
        models = SimpleNamespace()
        for name in ('Institucion', 'Plan', 'Suscripcion', 'User', 'Curso', 'EstudianteCurso'):
            model = Mock(side_effect=getattr(real_models, name))
            model.query.filter_by.return_value.first.return_value = None
            setattr(models, name, model)
        roles = [real_models.Role(name=name) for name in ('coordinador', 'estudiante')]
        models.Role = Mock()
        models.Role.query.filter.return_value.all.return_value = roles
        local = SimpleNamespace(label='machine / test-db', database='test-db', db=Mock())
        local.db.session.get.return_value = None
        inserted = []
        local.db.session.add.side_effect = inserted.append
        def flush():
            if inserted[-1].id is None:
                inserted[-1].id = len(inserted)
        local.db.session.flush.side_effect = flush
        return models, local, inserted

    def test_T12_real_model_fields_exclusive_markers_and_read_only_roles(self):
        with isolated_backend() as backend:
            models, local, inserted = self.fixture_builder(backend)
            with patch.object(fixtures.importlib, 'import_module', return_value=models), \
                    patch.object(fixtures, 'verify_destination', return_value=local.label):
                builder = fixtures.FixtureBuilder(local, self.journal)
                data = builder.prepare('conversations', reference=datetime(2026, 9, 30, 12))
            self.assertNotEqual(data.primary.id, data.other.id)
            self.assertTrue(data.student.email.endswith('@example.invalid'))
            self.assertEqual(data.student.roles[0].name, 'estudiante')
            self.assertEqual(data.coordinator.roles[0].name, 'coordinador')
            self.assertEqual(data.enrollment.user_id, data.student.id)
            self.assertTrue(all(type(item).__name__ != 'Role' for item in inserted))
            self.assertEqual(self.journal.data['state'], 'ready')
            self.assertEqual(len(inserted), len(self.journal.data['resources']))
            content = self.journal.path.read_text(encoding='utf-8')
            self.assertNotIn(builder.password, content)
            self.assertNotIn('password_hash', content)

    def test_T12_partial_prepare_cleans_previously_committed_resources(self):
        rows, foreign_keys = self.data_world(include_session=False)
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), \
                patch.object(fixtures, 'FixtureBuilder') as builder:
            builder.return_value.prepare.side_effect = SafetyError('Controlled partial preparation failure')
            with self.assertRaises(SafetyError):
                with fixtures.managed_fixtures(local, self.journal, 'students'):
                    self.fail('Incomplete setup entered')
            self.assertFalse(any(connection.rows.values()))
            self.assertEqual(self.journal.data['state'], 'cleaned')

    def test_T12_test_body_failure_still_cleans(self):
        rows, foreign_keys = self.data_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), patch.object(fixtures, 'FixtureBuilder'):
            with self.assertRaisesRegex(AssertionError, 'Controlled case failure'):
                with fixtures.managed_fixtures(local, self.journal, 'conversations'):
                    raise AssertionError('Controlled case failure')
            self.assertFalse(any(connection.rows.values()))

    def test_T12_failed_insert_keeps_durable_planned_marker(self):
        with isolated_backend() as backend:
            models, local, _ = self.fixture_builder(backend)
            local.db.session.commit.side_effect = RuntimeError('Injected commit failure')
            with patch.object(fixtures.importlib, 'import_module', return_value=models), \
                    patch.object(fixtures, 'verify_destination', return_value=local.label):
                builder = fixtures.FixtureBuilder(local, self.journal)
                with self.assertRaises(SafetyError):
                    builder.institution('partial')
            self.assertEqual(ownership.OwnershipJournal.load(self.journal.path).data['resources'][0]['state'], 'planned')
            local.db.session.rollback.assert_called_once()

    def test_T12_preexisting_marker_is_never_reserved_or_written(self):
        with isolated_backend() as backend:
            models, local, _ = self.fixture_builder(backend)
            models.Plan.query.filter_by.return_value.first.return_value = object()
            with patch.object(fixtures.importlib, 'import_module', return_value=models), \
                    patch.object(fixtures, 'verify_destination', return_value=local.label):
                builder = fixtures.FixtureBuilder(local, self.journal)
                with self.assertRaises(SafetyError):
                    builder.plan('finite', 4)
            self.assertEqual(self.journal.data['resources'], [])
            local.db.session.add.assert_not_called()
            local.db.session.commit.assert_not_called()


    def natural_world(self):
        rows, foreign_keys = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        user = next(r for r in self.journal.data['resources'] if r['entity'] == 'users')
        enrollment = next(r for r in self.journal.data['resources'] if r['entity'] == 'estudiante_cursos')
        enrollment['ownership_marker'] = dict(user_email=user['ownership_marker']['email'], curso_id=20)
        enrollment.update(id=None, state='planned')
        user.update(id=None, state='planned')
        self.journal.save()
        return rows, foreign_keys

    def test_T20_import_reservation_recovers_generated_user_and_enrollment_ids(self):
        rows, foreign_keys = self.natural_world()
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))
            self.assertFalse(any(connection.rows.values()))
            self.assertLess(connection.deletes.index('estudiante_cursos'), connection.deletes.index('users'))

    def test_T20_natural_import_not_committed_can_be_cleaned(self):
        rows, foreign_keys = self.natural_world()
        for name in ('users', 'estudiante_cursos', 'user_roles'):
            rows[('dbo', name)] = []
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, self.journal)
            self.assertFalse(any(connection.rows.values()))

    def test_T20_natural_marker_rejects_unowned_parent_and_integration_mode(self):
        self.natural_world()
        valid = copy.deepcopy(self.journal.data)
        for defect in ('mode', 'email', 'ambiguous-parent'):
            invalid = copy.deepcopy(valid)
            if defect == 'mode':
                invalid['mode'] = 'integration'
            elif defect == 'email':
                invalid['resources'][-1]['ownership_marker']['user_email'] = self.journal.name('unknown') + '@example.invalid'
            else:
                duplicate = copy.deepcopy(next(r for r in invalid['resources'] if r['entity'] == 'users'))
                duplicate['ownership_marker']['institucion_id'] = str(uuid.uuid4())
                invalid['resources'].append(duplicate)
            with self.subTest(defect=defect), self.assertRaises(SafetyError):
                ownership.validate_record(invalid)

    def test_T20_natural_marker_never_adopts_a_changed_tenant(self):
        rows, foreign_keys = self.natural_world()
        rows[('dbo', 'users')][0]['institucion_id'] = str(uuid.uuid4())
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T20_natural_marker_known_child_requires_still_owned_user(self):
        rows, foreign_keys = self.natural_world()
        child = self.journal.data['resources'][-1]
        child.update(id=rows[('dbo', 'estudiante_cursos')][0]['id'], state='created')
        self.journal.save()
        rows[('dbo', 'users')] = []
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T20_duplicate_natural_and_uuid_enrollment_block(self):
        rows, foreign_keys = self.natural_world()
        user = next(r for r in self.journal.data['resources'] if r['entity'] == 'users')
        self.journal.committed(user, rows[('dbo', 'users')][0]['id'])
        self.journal.reserve('estudiante_cursos', dict(user_id=user['id'], curso_id=20))
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T20_workbook_exactly_two_rows_and_password_is_not_a_formula(self):
        with patch.object(system_support, 'RUNTIME_ROOT', self.root / 'runtime'):
            password = '=TemporaryAa1!'
            path = system_support.write_workbook(self.journal, 'new@example.invalid', 'existing@example.invalid', password)
            book = load_workbook(path)
            try:
                self.assertEqual(book.active.max_row, 3)
                self.assertEqual(book.active.max_column, 5)
                self.assertEqual(book.active['E2'].value, password)
                self.assertEqual(book.active['E2'].data_type, 's')
                self.assertIsNone(book.active['E3'].value)
            finally:
                book.close()
            self.assertNotIn(password, self.journal.path.read_text(encoding='utf-8'))
            with self.assertRaises(FileExistsError):
                system_support.write_workbook(self.journal, 'new@example.invalid', 'existing@example.invalid', password)
            system_support.remove_workbook(self.journal)
            self.assertFalse(path.parent.exists())
            system_support.remove_workbook(self.journal)

    def test_T22_artifact_cleanup_never_deletes_unknown_files(self):
        with patch.object(system_support, 'RUNTIME_ROOT', self.root / 'runtime'):
            path = system_support.write_workbook(self.journal, 'new@example.invalid', 'existing@example.invalid', 'TemporaryAa1!')
            extra = path.parent / 'unknown.txt'
            extra.write_text('synthetic', encoding='utf-8')
            with self.assertRaises(OSError):
                system_support.remove_workbook(self.journal)
            self.assertTrue(extra.exists())
            self.assertFalse(path.exists())

    def test_T20_hidden_password_validates_existing_rule_without_recording_it(self):
        with isolated_backend():
            password = 'TemporaryAa1!'
            self.assertEqual(system_support.private_password(Mock(side_effect=[password, password])), password)
            for answers in ([password, 'different'], ['weak', 'weak']):
                with self.subTest(valid=False), self.assertRaises(SafetyError):
                    system_support.private_password(Mock(side_effect=answers))
            self.assertNotIn(password, self.journal.path.read_text(encoding='utf-8'))

    def test_T20_hidden_password_refuses_echo_fallback(self):
        def reader(_):
            warnings.warn('Synthetic fallback', getpass.GetPassWarning)
            self.fail('Echo fallback must stop before collecting a secret')
        with self.assertRaises(SafetyError):
            system_support.private_password(reader)

    def test_T20_prepare_all_cases_with_real_models_and_owned_intents(self):
        with isolated_backend() as backend:
            auth = __import__('routes.auth_multi_tenant', fromlist=['validate_password'])
            for case in system_support.CASES:
                journal = ownership.OwnershipJournal.create('machine / test-db', 'a' * 40, mode='system')
                models, local, inserted = self.fixture_builder(backend)
                with self.subTest(case=case), patch.object(system_support, 'RUNTIME_ROOT', self.root / 'runtime'), \
                        patch.object(fixtures.importlib, 'import_module', side_effect=lambda name: models if name == 'models' else auth), \
                        patch.object(fixtures, 'verify_destination', return_value=local.label):
                    data = system_support.prepare_system(local, journal, case, 'TemporaryAa1!')
                    self.assertEqual(system_support.case_name(journal), case)
                    self.assertEqual(journal.data['state'], 'ready')
                    self.assertEqual(data['case'], case)
                    self.assertEqual(len([item for item in inserted if type(item).__name__ == 'User']), 2)
                    plan = next(item for item in inserted if type(item).__name__ == 'Plan')
                    self.assertEqual(plan.max_cuentas, 2 if case == 'S-1' else 4)
                    planned = [r for r in journal.data['resources'] if r['state'] == 'planned']
                    self.assertTrue(planned)
                    self.assertNotIn('TemporaryAa1!', journal.path.read_text(encoding='utf-8'))
                    self.assertEqual(system_support.workbook_path(journal).exists(), case == 'S-2')
                    system_support.remove_workbook(journal)

    def test_T22_http_origin_rejects_remote_credentials_and_redirectable_urls(self):
        for value in ('https://localhost:5000', 'http://remote:5000', 'http://user:secret@localhost:5000',
                      'http://localhost:5000/api', 'http://localhost:5000/?x=y', 'http://localhost'):
            with self.subTest(url=value.split('@')[-1]), self.assertRaises(SafetyError):
                system_support.local_origin(value)
        self.assertEqual(system_support.local_origin('http://127.0.0.1:5000/'), 'http://127.0.0.1:5000')

    def test_T21_sql_verifier_checks_each_case_and_never_proves_manual_ui(self):
        with isolated_backend() as backend:
            auth = __import__('routes.auth_multi_tenant', fromlist=['validate_password'])
            real_models = __import__('models')
            for case in system_support.CASES:
                journal = ownership.OwnershipJournal.create('machine / test-db', 'a' * 40, mode='system')
                models, local, inserted = self.fixture_builder(backend)
                with patch.object(system_support, 'RUNTIME_ROOT', self.root / 'runtime'), \
                        patch.object(fixtures.importlib, 'import_module', side_effect=lambda name: models if name == 'models' else auth), \
                        patch.object(fixtures, 'verify_destination', return_value=local.label):
                    data = system_support.prepare_system(local, journal, case, 'TemporaryAa1!')
                    student = next(item for item in inserted if type(item).__name__ == 'User' and item.email == data['student_email'])
                    new_users, enrollments, sessions = [], [], []
                    if case == 'S-2':
                        new = real_models.User(id=str(uuid.uuid4()), email=data['new_email'],
                                              institucion_id=student.institucion_id, is_active=True)
                        new.roles.append(student.roles[0])
                        new_users.append(new)
                        for user in (student, new):
                            enrollments.append(real_models.EstudianteCurso(id=str(uuid.uuid4()),
                                               user_id=user.id, curso_id=data['course_id'], is_active=True))
                    if case == 'S-3':
                        enrollments = [item for item in inserted if type(item).__name__ == 'EstudianteCurso']
                        sessions.append(real_models.SesionChat(id=str(uuid.uuid4()), user_id=student.id,
                                        curso_id=data['course_id'], titulo='Nueva Conversación', is_active=True))
                    users = [item for item in inserted if type(item).__name__ == 'User'] + new_users
                    candidates = []
                    for resource in journal.data['resources']:
                        marker = resource['ownership_marker']
                        identifier = resource['id']
                        if identifier is None:
                            if resource['entity'] == 'users' and new_users:
                                identifier = new_users[0].id
                            elif resource['entity'] == 'estudiante_cursos' and enrollments:
                                target = new_users[0].id if 'user_email' in marker else marker['user_id']
                                identifier = next(e.id for e in enrollments if e.user_id == target)
                            elif resource['entity'] == 'sesiones_chat' and sessions:
                                identifier = sessions[0].id
                        if identifier is not None:
                            candidates.append((resource, dict(marker, id=identifier)))
                    def filtered_users(**fields):
                        rows = [u for u in users if all(cleanup.canonical(getattr(u, k)) == cleanup.canonical(v)
                                                      for k, v in fields.items())]
                        return SimpleNamespace(one=lambda: rows[0], count=lambda: len(rows), all=lambda: rows)
                    models.User.query.filter_by.side_effect = filtered_users
                    models.EstudianteCurso.query.filter_by.return_value.all.return_value = enrollments
                    models.SesionChat = Mock()
                    models.SesionChat.query.filter_by.return_value.all.return_value = sessions
                    models.MensajeChat = Mock()
                    counter = models.MensajeChat.query.join.return_value.filter.return_value.count
                    counter.return_value = 0
                    with self.subTest(case=case), patch.object(system_support, 'read_candidates', return_value=candidates):
                        result = system_support.verify_system(local, journal)
                        self.assertTrue(result['sql_condition_matches'])
                        self.assertFalse(result['manual_ui_proven'])
                        counter.return_value = 1
                        self.assertFalse(system_support.verify_system(local, journal)['sql_condition_matches'])
                    system_support.remove_workbook(journal)

    def test_T22_http_denial_disables_proxies_redirects_and_hides_token(self):
        self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        institution = next(r for r in self.journal.data['resources'] if r['entity'] == 'instituciones')
        institution['ownership_marker']['nombre'] = self.journal.name('s-3b-institution')
        self.journal.save()
        student = next(r for r in self.journal.data['resources'] if r['entity'] == 'users')
        client = Mock()
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        login, denial = Mock(), Mock()
        login.status_code = 200
        login.json.return_value = dict(token='synthetic-private-token', user=dict(id=student['id']))
        denial.status_code = 403
        denial.json.return_value = dict(message='No estás inscrito en este curso')
        client.post.side_effect = [login, denial]
        with patch('requests.Session', return_value=client), \
                patch.object(system_support, 'verify_system', return_value=dict(sql_condition_matches=True)):
            result = system_support.denied_http(Mock(), self.journal, 'http://localhost:5000', 'TemporaryAa1!')
        self.assertFalse(client.trust_env)
        self.assertTrue(all(call.kwargs['allow_redirects'] is False for call in client.post.call_args_list))
        self.assertTrue(result['contract_matches'])
        self.assertNotIn('synthetic-private-token', str(result))
        self.assertNotIn('TemporaryAa1!', str(result))

    def test_T22_http_mismatched_login_identity_blocks_authenticated_write(self):
        self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        institution = next(r for r in self.journal.data['resources'] if r['entity'] == 'instituciones')
        institution['ownership_marker']['nombre'] = self.journal.name('s-3b-institution')
        self.journal.save()
        client = Mock()
        client.__enter__ = Mock(return_value=client)
        client.__exit__ = Mock(return_value=False)
        client.post.return_value.status_code = 200
        client.post.return_value.json.return_value = dict(token='synthetic-private-token', user=dict(id=str(uuid.uuid4())))
        with patch('requests.Session', return_value=client), \
                patch.object(system_support, 'verify_system', return_value=dict(sql_condition_matches=True)), \
                self.assertRaises(SafetyError):
            system_support.denied_http(Mock(), self.journal, 'http://localhost:5000', 'TemporaryAa1!')
        self.assertEqual(client.post.call_count, 1)

    def test_T20_auto_config_reserved_on_own_course_can_be_recovered(self):
        rows, foreign_keys = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        self.journal.save()
        resource = self.journal.reserve('configuracion_ia', dict(curso_id=20), 20)
        rows[('dbo', 'configuracion_ia')] = [dict(curso_id=20)]
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, ownership.OwnershipJournal.load(self.journal.path))
            self.assertFalse(any(connection.rows.values()))
            self.assertLess(connection.deletes.index('configuracion_ia'), connection.deletes.index('cursos'))
        self.assertEqual(resource['state'], 'planned')  # Loaded journal was cleaned, not this instance.
        self.assertEqual(ownership.OwnershipJournal.load(self.journal.path).data['state'], 'cleaned')

    def test_T20_auto_config_absent_before_ui_does_not_block_cleanup(self):
        rows, foreign_keys = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        self.journal.save()
        self.journal.reserve('configuracion_ia', dict(curso_id=20), 20)
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, self.journal)
            self.assertFalse(any(connection.rows.values()))
            self.assertNotIn('configuracion_ia', connection.deletes)

    def test_T20_unregistered_config_still_blocks_all_cleanup(self):
        rows, foreign_keys = self.data_world(include_session=False)
        rows[('dbo', 'configuracion_ia')] = [dict(curso_id=20)]
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection), self.assertRaises(SafetyError):
            cleanup.cleanup_owned(local, self.journal)
        self.assertEqual(connection.deletes, [])

    def test_T20_auto_config_requires_system_mode_owned_course_and_matching_pk(self):
        self.data_world(include_session=False)
        for mode, course, identifier in (('integration', 20, 20), ('system', 21, 21), ('system', 20, 21)):
            self.journal.data['mode'] = mode
            self.journal.save()
            with self.subTest(mode=mode, course=course, identity=identifier), self.assertRaises(SafetyError):
                self.journal.reserve('configuracion_ia', dict(curso_id=course), identifier)

    def test_T20_config_own_pk_never_adopts_another_course(self):
        rows, foreign_keys = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        self.journal.save()
        self.journal.reserve('configuracion_ia', dict(curso_id=20), 20)
        rows[('dbo', 'configuracion_ia')] = [dict(curso_id=21)]
        with self.controlled_cleanup(rows, foreign_keys) as (local, connection):
            cleanup.cleanup_owned(local, self.journal)
            self.assertEqual(connection.rows[('dbo', 'configuracion_ia')], [dict(curso_id=21)])
            self.assertNotIn('configuracion_ia', connection.deletes)

    def test_T20_config_upgrade_only_reserves_absent_config_on_verified_owned_course(self):
        rows, _ = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        institution = next(r for r in self.journal.data['resources'] if r['entity'] == 'instituciones')
        institution['ownership_marker']['nombre'] = self.journal.name('s-1-institution')
        self.journal.save()
        course = next(r for r in self.journal.data['resources'] if r['entity'] == 'cursos')
        models = Mock()
        models.ConfiguracionIA.query.filter_by.return_value.first.return_value = None
        with patch.object(system_support, 'read_candidates', return_value=[(course, rows[('dbo', 'cursos')][0])]), \
                patch.object(system_support.importlib, 'import_module', return_value=models):
            result = system_support.reserve_course_config(Mock(), self.journal)
            self.assertTrue(result['intent_registered'])
            self.assertFalse(result['sql_writes'])
            with self.assertRaises(SafetyError):
                system_support.reserve_course_config(Mock(), self.journal)
        models.db.session.commit.assert_not_called()

    def test_T20_config_upgrade_rejects_preexisting_config_without_reservation(self):
        rows, _ = self.data_world(include_session=False)
        self.journal.data['mode'] = 'system'
        institution = next(r for r in self.journal.data['resources'] if r['entity'] == 'instituciones')
        institution['ownership_marker']['nombre'] = self.journal.name('s-1-institution')
        self.journal.save()
        course = next(r for r in self.journal.data['resources'] if r['entity'] == 'cursos')
        before = copy.deepcopy(self.journal.data)
        models = Mock()
        models.ConfiguracionIA.query.filter_by.return_value.first.return_value = object()
        with patch.object(system_support, 'read_candidates', return_value=[(course, rows[('dbo', 'cursos')][0])]), \
                patch.object(system_support.importlib, 'import_module', return_value=models), self.assertRaises(SafetyError):
            system_support.reserve_course_config(Mock(), self.journal)
        self.assertEqual(self.journal.data, before)


if __name__ == '__main__':
    unittest.main(verbosity=2)