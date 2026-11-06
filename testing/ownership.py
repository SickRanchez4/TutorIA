"""Small, strict, atomic fixture ownership journal; not an authorization token."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile
import uuid

from testing.local_destination import SafetyError


EVIDENCE_ROOT = Path(__file__).resolve().parents[1] / 'docs/specs/spec-001-tests/evidence'
ENTITIES = ('planes', 'instituciones', 'suscripciones', 'users', 'cursos',
            'estudiante_cursos', 'sesiones_chat', 'configuracion_ia')
INTEGER_ENTITIES = {'planes', 'cursos', 'configuracion_ia'}


def identity_column(entity):
    return 'curso_id' if entity == 'configuracion_ia' else 'id'


MARKER_KEYS = {
    'planes': {'nombre'}, 'instituciones': {'id', 'nombre'},
    'suscripciones': {'id', 'institucion_id', 'plan_id'},
    'users': {'email', 'institucion_id'}, 'cursos': {'nombre', 'institucion_id'},
    'estudiante_cursos': {'user_id', 'curso_id'},
    'sesiones_chat': {'user_id', 'curso_id', 'titulo'},
    'configuracion_ia': {'curso_id'},
}
STATES = {'preparing', 'ready', 'cleaning', 'cleaned', 'cleanup_failed'}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def valid_id(entity, value):
    if value is None:
        return True
    if entity in INTEGER_ENTITIES:
        return type(value) is int and value > 0
    try:
        return str(uuid.UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


def validate_record(data):
    """Reject arbitrary fields, ambiguous markers and unowned parent references."""
    fields = {'spec_id', 'run_id', 'started_at', 'updated_at', 'version', 'mode',
              'destination_label', 'state', 'resources', 'cleanup_errors'}
    if (set(data) != fields or data['spec_id'] != 'SPEC-001'
            or data['mode'] not in {'integration', 'system'} or data['state'] not in STATES):
        raise SafetyError('Registro de propiedad inválido; recuperación bloqueada.')
    try:
        if str(uuid.UUID(data['run_id'])) != data['run_id']:
            raise ValueError()
        for key in ('started_at', 'updated_at'):
            if datetime.fromisoformat(data[key]).utcoffset() is None:
                raise ValueError()
        if not re.fullmatch(r'[a-f0-9]{40}(?:-dirty)?|unavailable', data['version']):
            raise ValueError()
        if not re.fullmatch(r'[\w .\\/-]{1,260}', data['destination_label']):
            raise ValueError()
        if not isinstance(data['resources'], list) or not isinstance(data['cleanup_errors'], list):
            raise ValueError()
        if any(error not in {'cleanup_blocked', 'cleanup_failed', 'journal_update_failed'}
               for error in data['cleanup_errors']):
            raise ValueError()
        prefix = 'spec001-' + data['run_id'] + '-'
        seen = set()
        for resource in data['resources']:
            if set(resource) != {'entity', 'id', 'ownership_marker', 'state'}:
                raise ValueError()
            entity, marker = resource['entity'], resource['ownership_marker']
            natural_enrollment = (data['mode'] == 'system' and entity == 'estudiante_cursos'
                                  and set(marker) == {'user_email', 'curso_id'})
            if (entity not in ENTITIES or not valid_id(entity, resource['id'])
                    or resource['state'] not in {'planned', 'created', 'deleted'}
                    or (set(marker) != MARKER_KEYS[entity] and not natural_enrollment)):
                raise ValueError()
            if resource['state'] == 'created' and resource['id'] is None:
                raise ValueError()
            if entity == 'configuracion_ia' and (
                    data['mode'] != 'system' or resource['id'] != marker['curso_id']):
                raise ValueError()
            for key in ('nombre', 'email', 'user_email'):
                if key in marker:
                    value = marker[key]
                    if not isinstance(value, str) or not value.startswith(prefix):
                        raise ValueError()
                    if not re.fullmatch(re.escape(prefix) + r'[a-z0-9-]{1,50}(?:@example\.invalid)?', value):
                        raise ValueError()
                    if key in {'email', 'user_email'} and not value.endswith('@example.invalid'):
                        raise ValueError()
            if 'id' in marker and (not valid_id(entity, marker['id']) or marker['id'] != resource['id']):
                raise ValueError()
            if 'titulo' in marker and (not isinstance(marker['titulo'], str) or len(marker['titulo']) > 200):
                raise ValueError()
            identity = (entity, json.dumps(marker, sort_keys=True))
            if identity in seen:
                raise ValueError()
            seen.add(identity)
        ids = {entity: {r['id'] for r in data['resources']
                        if r['entity'] == entity and r['id'] is not None} for entity in ENTITIES}
        for resource in data['resources']:
            if 'user_email' in resource['ownership_marker']:
                parents = [r for r in data['resources'] if r['entity'] == 'users'
                           and r['ownership_marker']['email'] == resource['ownership_marker']['user_email']]
                if len(parents) != 1:
                    raise ValueError()
            for field, parent in (('institucion_id', 'instituciones'), ('plan_id', 'planes'),
                                  ('user_id', 'users'), ('curso_id', 'cursos')):
                if field in resource['ownership_marker'] and resource['ownership_marker'][field] not in ids[parent]:
                    raise ValueError()
    except (ValueError, TypeError, KeyError, AttributeError):
        raise SafetyError('Marca, identidad o pertenencia inválida; recuperación bloqueada.') from None


class OwnershipJournal:
    """Persist intent before writes and identities after commit, using atomic replace."""

    def __init__(self, path, data):
        self.path, self.data = Path(path).resolve(), data
        validate_record(data)
        if self.path != EVIDENCE_ROOT.resolve() / data['run_id'] / 'ownership.json':
            raise SafetyError('El registro debe residir en la evidencia de su run_id.')

    @classmethod
    def create(cls, label, version, mode='integration'):
        now, run_id = timestamp(), str(uuid.uuid4())
        data = dict(spec_id='SPEC-001', run_id=run_id, started_at=now, updated_at=now,
                    version=version, mode=mode, destination_label=label, state='preparing',
                    resources=[], cleanup_errors=[])
        journal = cls(EVIDENCE_ROOT / run_id / 'ownership.json', data)
        journal.path.parent.mkdir(parents=True, exist_ok=False)
        journal.save()
        return journal

    @classmethod
    def load(cls, path):
        try:
            path = Path(path).resolve()
            if not path.is_relative_to(EVIDENCE_ROOT.resolve()) or path.name != 'ownership.json':
                raise ValueError()
            if path.stat().st_size > 1_000_000:
                raise ValueError()
            def unique_object(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError()
                    result[key] = value
                return result
            return cls(path, json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object))
        except SafetyError:
            raise
        except Exception:
            raise SafetyError('No se puede validar el registro; no se borra ningún recurso.') from None

    def save(self):
        self.data['updated_at'] = timestamp()
        validate_record(self.data)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             prefix='.ownership-', delete=False) as handle:
                temporary = handle.name
                json.dump(self.data, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except Exception:
            raise SafetyError('No se pudo guardar el registro durable; detenga las escrituras.') from None
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)

    def reserve(self, entity, marker, resource_id=None):
        if self.data['state'] not in {'preparing', 'ready'}:
            raise SafetyError('El registro no admite nuevas reservas.')
        marker = dict(marker)
        try:
            for key in ('institucion_id', 'user_id'):
                if key in marker:
                    marker[key] = str(uuid.UUID(str(marker[key])))
            if entity not in INTEGER_ENTITIES:
                if resource_id is not None:
                    resource_id = str(uuid.UUID(str(resource_id)))
                if 'id' in marker:
                    marker['id'] = str(uuid.UUID(str(marker['id'])))
        except (ValueError, TypeError, AttributeError):
            raise SafetyError('Identidad UUID no válida; reserva bloqueada.') from None
        resource = dict(entity=entity, id=resource_id, ownership_marker=marker, state='planned')
        self.data['resources'].append(resource)
        try:
            self.save()
        except Exception:
            self.data['resources'].pop()
            raise
        return resource

    def committed(self, resource, resource_id):
        if not any(item is resource for item in self.data['resources']):
            raise SafetyError('Recurso no registrado antes de su creación.')
        if resource['entity'] not in INTEGER_ENTITIES:
            try:
                resource_id = str(uuid.UUID(str(resource_id)))
            except (ValueError, TypeError, AttributeError):
                raise SafetyError('Identidad confirmada no válida; conserve el registro.') from None
        resource.update(id=resource_id, state='created')
        self.save()

    def state(self, value):
        self.data['state'] = value
        self.save()

    def name(self, suffix):
        if not re.fullmatch(r'[a-z0-9-]{1,50}', suffix):
            raise SafetyError('Etiqueta ficticia inválida.')
        return 'spec001-' + self.data['run_id'] + '-' + suffix