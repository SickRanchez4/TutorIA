"""Explicit ownership cleanup; unknown dependents block, never become delete targets."""
from collections import defaultdict

from sqlalchemy import MetaData, Table, Uuid, and_, delete, select, text

from testing.local_destination import SafetyError, verify_destination
from testing.ownership import ENTITIES, identity_column, validate_record


DELETE_ORDER = ('sesiones_chat', 'estudiante_cursos', 'configuracion_ia', 'users', 'cursos',
                'suscripciones', 'instituciones', 'planes')
FK_QUERY = """
SELECT fk.object_id AS constraint_id, fk.is_disabled, fk.is_not_trusted,
       cs.name AS child_schema, ct.name AS child_table, cc.name AS child_column,
       ps.name AS parent_schema, pt.name AS parent_table, pc.name AS parent_column
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc ON fkc.constraint_object_id = fk.object_id
JOIN sys.tables ct ON ct.object_id = fk.parent_object_id
JOIN sys.schemas cs ON cs.schema_id = ct.schema_id
JOIN sys.columns cc ON cc.object_id = ct.object_id AND cc.column_id = fkc.parent_column_id
JOIN sys.tables pt ON pt.object_id = fk.referenced_object_id
JOIN sys.schemas ps ON ps.schema_id = pt.schema_id
JOIN sys.columns pc ON pc.object_id = pt.object_id AND pc.column_id = fkc.referenced_column_id
ORDER BY fk.object_id, fkc.constraint_column_id
"""


def canonical(value):
    return str(value).casefold() if value is not None else None


def string_uuid_columns(tables):
    """Reflected SQL Server UUIDs must bind the journal's strings, not UUID objects."""
    for table in tables.values():
        for column in table.columns:
            if isinstance(column.type, Uuid):
                column.type = column.type.copy()
                column.type.as_uuid = False


def matches(row, marker):
    return all(canonical(row[key]) == canonical(value) for key, value in marker.items())


def database_marker(resource, users):
    """Resolve a system import's pre-registered email through an already owned user."""
    marker = dict(resource['ownership_marker'])
    if 'user_email' in marker:
        user_id = users.get(marker.pop('user_email'))
        if user_id is None:
            return None
        marker['user_id'] = user_id
    return marker


def resolve_owned(connection, tables, journal):
    """Match BOTH exact identity and full marker; no prefix-only recovery."""
    candidates = []
    seen = set()
    users = {}
    # Resolve parents first even if reservations were made after an existing course.
    resources = sorted(journal.data['resources'], key=lambda r: ENTITIES.index(r['entity']))
    for resource in resources:
        table = tables[('dbo', resource['entity'])]
        identity_key = identity_column(resource['entity'])
        marker = database_marker(resource, users)
        if marker is None:
            if resource['id'] is not None:
                exact = connection.execute(select(table).where(table.c[identity_key] == resource['id'])).mappings().first()
                if exact is not None:
                    raise SafetyError('El usuario previsto no es propio; limpieza bloqueada.')
            continue
        marked = connection.execute(select(table).where(and_(
            *(table.c[key] == value for key, value in marker.items())
        ))).mappings().all()
        identifier = resource['id']
        exact = None
        if identifier is not None:
            exact = connection.execute(select(table).where(table.c[identity_key] == identifier)).mappings().first()
        if (len(marked) > 1 or (exact is not None and not matches(exact, marker))
                or (marked and identifier is not None
                    and canonical(marked[0][identity_key]) != canonical(identifier))):
            raise SafetyError('Identidad ambigua o recurso ajeno; no se permite el borrado.')
        row = marked[0] if marked else None
        if resource['state'] == 'deleted' and row is not None:
            raise SafetyError('Recurso reaparecido; requiere investigación, no borrado automático.')
        if row is not None:
            key = (resource['entity'], canonical(row[identity_key]))
            if key in seen:
                raise SafetyError('Identidad duplicada en el registro; limpieza bloqueada.')
            seen.add(key)
            candidates.append((resource, row))
            if resource['entity'] == 'users':
                users[resource['ownership_marker']['email']] = row['id']
    # Child markers must point to parents that STILL match their own markers.
    owned_ids = {entity: {canonical(row[identity_column(entity)]) for resource, row in candidates
                         if resource['entity'] == entity} for entity in ENTITIES}
    for resource, row in candidates:
        for field, parent in (('institucion_id', 'instituciones'), ('plan_id', 'planes'),
                              ('user_id', 'users'), ('curso_id', 'cursos')):
            if ((field in resource['ownership_marker'] or
                 (field == 'user_id' and 'user_email' in resource['ownership_marker']))
                    and canonical(row[field]) not in owned_ids[parent]):
                raise SafetyError('El padre no es atribuible a la ejecución; limpieza bloqueada.')
    return candidates


def check_dependents(connection, tables, foreign_keys, candidates):
    """Inventory every incoming FK, including cascades and cross-schema children."""
    owned = {(r['entity'], canonical(row[identity_column(r['entity'])])) for r, row in candidates}
    associations = []
    for resource, parent in candidates:
        entity = resource['entity']
        for columns in foreign_keys.values():
            first = columns[0]
            if first['parent_schema'] != 'dbo' or first['parent_table'] != entity:
                continue
            if first['is_disabled'] or first['is_not_trusted']:
                raise SafetyError('Restricción FK no verificable; limpieza bloqueada.')
            table = tables[(first['child_schema'], first['child_table'])]
            rows = connection.execute(select(table).where(and_(
                *(table.c[column['child_column']] == parent[column['parent_column']]
                  for column in columns)
            ))).mappings().all()
            for row in rows:
                if (first['child_schema'] == 'dbo' and first['child_table'] == 'user_roles'
                        and entity == 'users' and canonical(row['user_id']) == canonical(parent['id'])):
                    associations.append(dict(row))
                elif (first['child_schema'] != 'dbo'
                      or identity_column(first['child_table']) not in row
                      or (first['child_table'], canonical(row[identity_column(first['child_table'])])) not in owned):
                    raise SafetyError('Dependencia inesperada o ajena; se conserva y se registra residuo.')
    return associations


def cleanup_owned(local, journal):
    """Revalidate destination, lock, preflight all deletes, commit, then update journal."""
    validate_record(journal.data)
    if journal.data['destination_label'] != local.label:
        raise SafetyError('El destino confirmado no coincide con el registro; limpieza bloqueada.')
    journal.state('cleaning')
    try:
        local.db.session.rollback()
        local.db.session.remove()
        with local.db.engine.connect().execution_options(isolation_level='SERIALIZABLE') as connection:
            with connection.begin():
                if verify_destination(connection, local.database) != local.label:
                    raise SafetyError('Destino cambiado; limpieza bloqueada.')
                foreign_keys = defaultdict(list)
                original_fks = [dict(row) for row in connection.execute(text(FK_QUERY)).mappings()]
                for row in original_fks:
                    if row['parent_schema'] == 'dbo' and row['parent_table'] == 'user_roles':
                        raise SafetyError('Dependencia de asociación compartida no evaluada; limpieza bloqueada.')
                    if row['parent_schema'] == 'dbo' and row['parent_table'] in ENTITIES:
                        foreign_keys[row['constraint_id']].append(dict(row))
                keys = {('dbo', name) for name in (*ENTITIES, 'user_roles')}
                keys.update((rows[0]['child_schema'], rows[0]['child_table'])
                            for rows in foreign_keys.values())
                metadata = MetaData()
                tables = {key: Table(key[1], metadata, schema=key[0],
                                     autoload_with=connection, resolve_fks=False) for key in sorted(keys)}
                string_uuid_columns(tables)
                # Retain exclusive table locks through preflight and deletes, avoiding cascade races.
                # These are short-lived LOCAL maintenance locks, not claims of nonblocking cleanup.
                preparer = connection.dialect.identifier_preparer
                for schema, name in sorted(keys):
                    qualified = preparer.quote_schema(schema) + '.' + preparer.quote(name)
                    connection.execute(text(f'SELECT TOP (1) 1 FROM {qualified} WITH (TABLOCKX, HOLDLOCK)'))
                if [dict(row) for row in connection.execute(text(FK_QUERY)).mappings()] != original_fks:
                    raise SafetyError('El esquema cambió durante la verificación; limpieza bloqueada.')
                if verify_destination(connection, local.database) != local.label:
                    raise SafetyError('Destino o esquema cambiado después del bloqueo.')
                candidates = resolve_owned(connection, tables, journal)
                associations = check_dependents(connection, tables, foreign_keys, candidates)
                users = {r['ownership_marker']['email']: row['id'] for r, row in candidates
                         if r['entity'] == 'users'}
                roles = tables[('dbo', 'user_roles')]
                for association in {tuple(sorted(row.items())) for row in associations}:
                    values = dict(association)
                    connection.execute(delete(roles).where(and_(
                        *(roles.c[key] == value for key, value in values.items())
                    )))
                for entity in DELETE_ORDER:
                    table = tables[('dbo', entity)]
                    for resource, row in candidates:
                        if resource['entity'] == entity:
                            result = connection.execute(delete(table).where(and_(
                                table.c[identity_column(entity)] == row[identity_column(entity)],
                                *(table.c[key] == value for key, value in database_marker(resource, users).items())
                            )))
                            if result.rowcount != 1:
                                raise SafetyError('Borrado no confirmado; se revierte la limpieza.')
                if resolve_owned(connection, tables, journal):
                    raise SafetyError('Quedan recursos propios; se revierte la limpieza.')
        # If the process dies here, replay finds absence and safely completes this journal.
        for resource in journal.data['resources']:
            resource['state'] = 'deleted'
        journal.data['cleanup_errors'] = []
        journal.state('cleaned')
    except Exception as error:
        journal.data['state'] = 'cleanup_failed'
        journal.data['cleanup_errors'] = ['cleanup_blocked' if isinstance(error, SafetyError) else 'cleanup_failed']
        journal.save()
        raise SafetyError('Limpieza no completada; recursos conservados o estado pendiente de recuperación.') from None