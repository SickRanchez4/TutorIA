"""RAG ingestion lifecycle services used by coordinator REST endpoints."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Iterable

import requests
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from models import Curso, RagIngestionJob, db


class RagIngestionError(Exception):
    """Expected ingestion failure that can be shown safely to an operator."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _storage_root() -> Path:
    configured_path = os.getenv('RAG_UPLOAD_STORAGE_PATH', 'storage/rag_uploads')
    root = Path(configured_path).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _roles(user) -> set[str]:
    return {role.name for role in getattr(user, 'roles', [])}


def can_manage_course(user, curso: Curso) -> bool:
    """Ensure a coordinator only reaches their tenant; super admins may inspect all."""
    roles = _roles(user)
    return 'super_admin' in roles or (
        'coordinador' in roles and str(user.institucion_id) == str(curso.institucion_id)
    )


def get_managed_course(user, curso_id: int) -> Curso | None:
    curso = Curso.query.get(curso_id)
    return curso if curso and can_manage_course(user, curso) else None


def _unique_filename(name: str, used_names: set[str]) -> str:
    sanitized = secure_filename(name) or 'documento.pdf'
    stem = Path(sanitized).stem or 'documento'
    suffix = Path(sanitized).suffix.lower() or '.pdf'
    candidate = f'{stem}{suffix}'
    index = 2
    while candidate.lower() in used_names:
        candidate = f'{stem}_{index}{suffix}'
        index += 1
    used_names.add(candidate.lower())
    return candidate


def create_ingestion_job(user, curso: Curso, uploaded_files: Iterable[FileStorage]) -> RagIngestionJob:
    """Persist received PDFs before dispatching them, enabling safe job history and retry."""
    job = RagIngestionJob(
        institucion_id=curso.institucion_id,
        curso_id=curso.id,
        coordinador_id=user.id,
        estado='queued',
        intento=1,
    )
    db.session.add(job)
    db.session.flush()

    job_directory = _storage_root() / job.id
    job_directory.mkdir(parents=True, exist_ok=True)
    documents = []
    used_names: set[str] = set()

    try:
        for uploaded_file in uploaded_files:
            if not uploaded_file or not uploaded_file.filename:
                continue
            filename = _unique_filename(uploaded_file.filename, used_names)
            content = uploaded_file.read()
            if not content:
                raise RagIngestionError(f'El archivo "{uploaded_file.filename}" está vacío.', 400)
            (job_directory / filename).write_bytes(content)
            documents.append({'archivo': filename, 'tamano_bytes': len(content)})
    except Exception:
        db.session.rollback()
        for path in job_directory.glob('*'):
            path.unlink(missing_ok=True)
        job_directory.rmdir()
        raise

    if not documents:
        db.session.rollback()
        job_directory.rmdir()
        raise RagIngestionError('No se proporcionó ningún archivo PDF válido.', 400)

    job.documentos_json = json.dumps(documents, ensure_ascii=False)
    db.session.commit()
    return job


def _job_files(job: RagIngestionJob) -> list[tuple[str, tuple[str, bytes, str]]]:
    job_directory = _storage_root() / job.id
    payload = []
    missing_files = []
    for document in job.documents():
        filename = document.get('archivo')
        file_path = job_directory / filename if filename else None
        if not file_path or not file_path.is_file():
            missing_files.append(filename or 'desconocido')
            continue
        payload.append(('files', (filename, file_path.read_bytes(), 'application/pdf')))

    if missing_files:
        raise RagIngestionError(
            'No se puede reintentar porque faltan archivos locales: ' + ', '.join(missing_files),
            409,
        )
    if not payload:
        raise RagIngestionError('El trabajo no contiene archivos para procesar.', 409)
    return payload


def _set_failed(job: RagIngestionJob, message: str, state: str = 'failed') -> None:
    job.estado = state
    job.error_message = message[:1000]
    job.completed_at = None
    db.session.commit()


def dispatch_ingestion_job(job: RagIngestionJob) -> RagIngestionJob:
    """Call n8n and persist the normalized result without exposing integration details."""
    webhook_url = os.getenv('N8N_EMBEDDINGS_WEBHOOK_URL', '').strip()
    if not webhook_url:
        _set_failed(job, 'N8N_EMBEDDINGS_WEBHOOK_URL no está configurada.')
        raise RagIngestionError('Sistema de procesamiento no disponible.', 503)

    job.estado = 'processing'
    job.error_message = None
    job.completed_at = None
    db.session.commit()

    try:
        response = requests.post(
            webhook_url,
            params={
                'curso_id': str(job.curso_id),
                'institucion_id': str(job.institucion_id),
                'coordinador_id': str(job.coordinador_id or ''),
                'ingestion_job_id': job.id,
            },
            files=_job_files(job),
            timeout=180,
        )
    except requests.exceptions.Timeout as error:
        # n8n might still complete after this client timeout, so distinguish unknown from failed.
        _set_failed(job, 'Tiempo de espera agotado al consultar n8n.', state='unknown')
        raise RagIngestionError('No fue posible confirmar el resultado; revisa el estado antes de reintentar.', 504) from error
    except requests.exceptions.RequestException as error:
        _set_failed(job, 'No fue posible conectar con el procesador de materiales.')
        raise RagIngestionError('Error al conectar con el procesador de materiales.', 502) from error

    if response.status_code not in (200, 201):
        _set_failed(job, f'El procesador devolvió estado HTTP {response.status_code}.')
        raise RagIngestionError('Error al procesar los archivos.', 502)

    try:
        processor_response = response.json()
    except ValueError:
        processor_response = {}

    job.estado = 'completed'
    job.archivos_procesados = int(processor_response.get('archivos_procesados') or len(job.documents()))
    job.chunks_indexados = int(processor_response.get('chunks_indexados') or 0)
    job.respuesta_procesador_json = json.dumps(processor_response, ensure_ascii=False, default=str)
    job.error_message = None
    job.completed_at = _utcnow()
    db.session.commit()
    return job


def retry_ingestion_job(user, job_id: str) -> RagIngestionJob:
    job = RagIngestionJob.query.get(job_id)
    if not job:
        raise RagIngestionError('Trabajo de indexación no encontrado.', 404)

    curso = get_managed_course(user, job.curso_id)
    if not curso or str(curso.institucion_id) != str(job.institucion_id):
        raise RagIngestionError('No tienes permisos sobre este trabajo de indexación.', 403)
    if job.estado == 'processing':
        raise RagIngestionError('El trabajo ya se está procesando.', 409)

    job.intento += 1
    return dispatch_ingestion_job(job)


def _call_knowledge_admin_webhook(action: str, payload: dict) -> None:
    """Ask the n8n knowledge agent to perform one explicit Pinecone operation."""
    webhook_url = os.getenv('N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL', '').strip()
    if not webhook_url:
        raise RagIngestionError('La operación de limpieza de conocimiento no está configurada.', 503)

    try:
        response = requests.post(webhook_url, json={'action': action, **payload}, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        raise RagIngestionError('No fue posible actualizar la base de conocimiento.', 502) from error


def _remove_local_job_files(job: RagIngestionJob, filenames: set[str] | None = None) -> None:
    """Remove persisted source PDFs after Pinecone has confirmed their deletion."""
    job_directory = _storage_root() / job.id
    if not job_directory.exists():
        return
    if filenames is None:
        for path in job_directory.glob('*'):
            path.unlink(missing_ok=True)
        job_directory.rmdir()
        return
    for filename in filenames:
        (job_directory / filename).unlink(missing_ok=True)


def remove_indexed_document(user, curso_id: int, filename: str) -> None:
    """Delete all vectors for one PDF and remove the document from local job history."""
    curso = get_managed_course(user, curso_id)
    if not curso:
        raise RagIngestionError('Curso no encontrado o sin permisos.', 404)

    filename = secure_filename(filename)
    if not filename:
        raise RagIngestionError('Nombre de documento inválido.', 400)

    jobs = RagIngestionJob.query.filter_by(curso_id=curso.id, institucion_id=curso.institucion_id).all()
    matching_jobs = [job for job in jobs if any(doc.get('archivo') == filename for doc in job.documents())]
    if not matching_jobs:
        raise RagIngestionError('Documento indexado no encontrado.', 404)

    _call_knowledge_admin_webhook(
        'delete_document',
        {'curso_id': curso.id, 'institucion_id': str(curso.institucion_id), 'archivo': filename},
    )

    for job in matching_jobs:
        job.documentos_json = json.dumps(
            [document for document in job.documents() if document.get('archivo') != filename],
            ensure_ascii=False,
        )
        _remove_local_job_files(job, {filename})
    db.session.commit()


def clear_course_knowledge(user, curso_id: int) -> int:
    """Delete every vector in a course namespace and clear its local RAG history."""
    curso = get_managed_course(user, curso_id)
    if not curso:
        raise RagIngestionError('Curso no encontrado o sin permisos.', 404)

    jobs = RagIngestionJob.query.filter_by(curso_id=curso.id, institucion_id=curso.institucion_id).all()
    _call_knowledge_admin_webhook(
        'clear_course',
        {'curso_id': curso.id, 'institucion_id': str(curso.institucion_id)},
    )

    for job in jobs:
        _remove_local_job_files(job)
        db.session.delete(job)
    db.session.commit()
    return len(jobs)


def course_knowledge_overview(user, curso_id: int, limit: int = 5) -> dict:
    curso = get_managed_course(user, curso_id)
    if not curso:
        raise RagIngestionError('Curso no encontrado o sin permisos.', 404)

    jobs = (
        RagIngestionJob.query
        .filter_by(curso_id=curso.id, institucion_id=curso.institucion_id)
        .order_by(RagIngestionJob.created_at.desc())
        .limit(limit)
        .all()
    )

    latest_documents: dict[str, dict] = {}
    for job in jobs:
        if job.estado != 'completed':
            continue
        for document in job.documents():
            latest_documents.setdefault(document.get('archivo', ''), document)

    latest_completed = next((job for job in jobs if job.estado == 'completed'), None)
    active_job = next((job for job in jobs if job.estado in {'queued', 'processing', 'unknown'}), None)

    return {
        'curso_id': curso.id,
        'resumen': {
            'documentos_indexados': len([name for name in latest_documents if name]),
            'ultimo_estado': jobs[0].estado if jobs else 'sin_material',
            'ultimo_procesamiento_at': latest_completed.completed_at.isoformat() if latest_completed and latest_completed.completed_at else None,
            'trabajo_activo_id': active_job.id if active_job else None,
        },
        'documentos': list(latest_documents.values()),
        'trabajos': [job.to_dict() for job in jobs],
    }
