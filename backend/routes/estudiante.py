"""
Student routes
"""
import os
import json
import logging
import base64
import re
from datetime import datetime, timezone

import requests as http_requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, EstudianteCurso, Curso, ConsumoTokens
from models.ia_chat import SesionChat, MensajeChat, ConfiguracionIA
from models.agenda_notificaciones import ActividadAgenda
from services.model_pricing import DEFAULT_MODEL, DEFAULT_PROVIDER, calculate_cost_usd, get_active_model_price
from services.subscription_quota import request_is_allowed
from services.token_counting import count_tokens

logger = logging.getLogger(__name__)

estudiante_bp = Blueprint('estudiante', __name__)

N8N_CHAT_WEBHOOK_URL = os.environ.get('N8N_CHAT_WEBHOOK_URL', '')

CHAT_SERVICE_UNAVAILABLE_MESSAGE = (
    'No puedo responder en este momento porque el servicio de IA no está disponible. '
    'Inténtalo de nuevo en unos minutos.'
)

# The reserve includes a bounded reply plus a conservative estimate of the prompt.
# It is included in the n8n payload so its model invocation can honor the same cap.
MAX_COMPLETION_TOKENS = 1024
MIN_REQUEST_RESERVATION_TOKENS = 1152
MAX_CHAT_IMAGE_BYTES = 4 * 1024 * 1024
ALLOWED_CHAT_IMAGE_TYPES = {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}


# ============================================================================
# HELPERS
# ============================================================================

def _is_enrolled(user_id, curso_id):
    """Return True if the student has an active enrollment in the course."""
    return EstudianteCurso.query.filter_by(
        user_id=user_id, curso_id=curso_id, is_active=True
    ).first() is not None


def _modo_habilitado(curso_id, modo):
    """Return True if the given chat mode ('chat', 'practicar', 'recursos') is enabled for the course."""
    config = ConfiguracionIA.query.get(curso_id)
    if not config:
        return True
    modos = [m.strip() for m in (config.modos_permitidos or '').split(',') if m.strip()]
    return modo in modos


def _get_session_for_user(sesion_id, user_id):
    """Return the active chat session owned by user_id, or None."""
    return SesionChat.query.filter_by(
        id=sesion_id, user_id=user_id, is_active=True
    ).first()


def _build_n8n_chat_payload(sesion, message, requested_mode, student_id, max_tokens, image=None):
    """Build the exact payload contract expected by the n8n student-chat webhook."""
    curso = Curso.query.get(sesion.curso_id)
    config = ConfiguracionIA.query.get(sesion.curso_id)

    payload = {
        'institucion_id': str(curso.institucion_id) if curso else None,
        'curso_id': sesion.curso_id,
        'curso_nombre': curso.nombre if curso else None,
        # Debe coincidir con upload-to-pinecone.json para preservar el
        # aislamiento de vectores por institución y curso.
        'pinecone_namespace': f'inst_{curso.institucion_id}_curso_{sesion.curso_id}' if curso else None,
        'chatbot_prompt': config.system_prompt if config else '',
        'chatbot_temperature': float(config.temperatura) if config else 0.2,
        'extend_knowledge': bool(config.extender_conocimiento) if config else False,
        'requested_mode': requested_mode,
        'student_id': student_id,
        'conversation_id': sesion.id,
        'message': message,
        'max_tokens': max_tokens,
    }
    if image:
        payload['image'] = image
    return payload


def _validated_chat_image(data):
    """Validate an optional browser data URL without storing the image on the server."""
    image = data.get('image')
    if image is None:
        return None
    if not isinstance(image, dict):
        raise ValueError('La imagen adjunta no tiene un formato válido.')

    mime_type = str(image.get('mime_type') or '').lower()
    data_url = str(image.get('data_url') or '')
    if mime_type not in ALLOWED_CHAT_IMAGE_TYPES:
        raise ValueError('Solo se admiten imágenes PNG, JPG, WEBP o GIF.')
    match = re.fullmatch(r'data:([^;,]+);base64,([A-Za-z0-9+/=]+)', data_url)
    if not match or match.group(1).lower() != mime_type:
        raise ValueError('La imagen adjunta no tiene un formato válido.')
    try:
        image_bytes = base64.b64decode(match.group(2), validate=True)
    except (ValueError, base64.binascii.Error):
        raise ValueError('La imagen adjunta no tiene un formato válido.')
    if not image_bytes or len(image_bytes) > MAX_CHAT_IMAGE_BYTES:
        raise ValueError('La imagen no puede superar los 4 MB.')

    return {
        'mime_type': mime_type,
        'data_url': data_url,
        'name': str(image.get('name') or 'imagen').strip()[:255],
    }


def _parse_n8n_chat_response(data):
    """Normalize n8n response shapes into text, citations, usage and applied mode."""
    if isinstance(data, list):
        data = data[0] if data else {}

    if isinstance(data, str):
        return data, None, None, None

    if not isinstance(data, dict):
        return str(data), None, None, None

    nested = data.get('data', {})
    if not isinstance(nested, dict):
        nested = {}
    resource = data.get('resource') or nested.get('resource')
    if not isinstance(resource, dict):
        resource = {}

    resource_title = str(resource.get('title') or '').strip()
    resource_graphic = str(resource.get('graphic') or '').strip()
    if resource_graphic:
        # MermaidMessage.vue detects this fenced block and renders the diagram.
        # Keep the title as regular message text above the diagram.
        text = '\n\n'.join(part for part in (
            resource_title,
            f'```mermaid\n{resource_graphic}\n```',
        ) if part)
    else:
        text = (
            data.get('respuesta')
            or data.get('response')
            or data.get('answer')
            or data.get('output')
            or data.get('message')
            or nested.get('respuesta')
            or nested.get('response')
            or nested.get('answer')
            or nested.get('output')
            or nested.get('message')
        )
    citas = (
        data.get('citas')
        or data.get('citations')
        or data.get('sources')
        or nested.get('citas')
        or nested.get('citations')
        or nested.get('sources')
    )
    citas_json = json.dumps(citas) if citas else None
    usage = data.get('usage') or data.get('token_usage') or nested.get('usage') or nested.get('token_usage')
    if not isinstance(usage, dict):
        usage = {}
    prompt_tokens = usage.get('prompt_tokens', data.get('prompt_tokens', nested.get('prompt_tokens')))
    completion_tokens = usage.get('completion_tokens', data.get('completion_tokens', nested.get('completion_tokens')))
    try:
        usage = {
            'prompt_tokens': max(int(prompt_tokens or 0), 0),
            'completion_tokens': max(int(completion_tokens or 0), 0),
        }
    except (TypeError, ValueError):
        usage = None
    if usage and not (usage['prompt_tokens'] or usage['completion_tokens']):
        usage = None
    modo_aplicado = data.get('modo_aplicado') or nested.get('modo_aplicado')
    return text or str(data), citas_json, usage, modo_aplicado


def _call_n8n_chat(payload):
    """
    Call the n8n chat webhook.
    Returns (response_text, citas_json_str, usage_dict_or_none, applied_mode_or_none).
    """
    if not N8N_CHAT_WEBHOOK_URL:
        raise RuntimeError('N8N_CHAT_WEBHOOK_URL no está configurado en el backend')

    resp = http_requests.post(N8N_CHAT_WEBHOOK_URL, json=payload, timeout=60)
    resp.raise_for_status()
    return _parse_n8n_chat_response(resp.json())


def _token_reservation(message):
    """Bound one request before calling the external model service."""
    return max(MIN_REQUEST_RESERVATION_TOKENS, count_tokens(message) + MAX_COMPLETION_TOKENS)


def _quota_error(curso, reservation_tokens):
    allowed, summary = request_is_allowed(curso.institucion_id, reservation_tokens)
    if allowed:
        return None, summary
    if not summary:
        return (jsonify({'message': 'La institución no tiene una suscripción de tokens habilitada.'}), 403), None
    message = summary['motivo_no_disponible'] or 'La institución no tiene tokens suficientes para realizar esta consulta.'
    return (jsonify({'message': message, 'code': 'token_quota_exceeded', 'suscripcion': summary}), 429), summary


def _record_consumption(curso, user_id, tipo_operacion, message, response, usage):
    """Record provider usage, falling back to tiktoken counts of the exchanged text."""
    prompt_tokens = int((usage or {}).get('prompt_tokens') or 0)
    completion_tokens = int((usage or {}).get('completion_tokens') or 0)
    if prompt_tokens + completion_tokens <= 0:
        prompt_tokens = count_tokens(message)
        completion_tokens = count_tokens(response)

    price = get_active_model_price(DEFAULT_PROVIDER, DEFAULT_MODEL)
    cost = calculate_cost_usd(prompt_tokens, completion_tokens, price)

    db.session.add(ConsumoTokens(
        institucion_id=curso.institucion_id,
        curso_id=curso.id,
        user_id=user_id,
        tipo_operacion=tipo_operacion,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        costo_estimado_usd=cost,
        precio_modelo_ia_id=price.id if price else None,
        proveedor_modelo=DEFAULT_PROVIDER,
        modelo_ia=DEFAULT_MODEL,
        precio_prompt_por_millon_usd=price.precio_prompt_por_millon_usd if price else None,
        precio_completion_por_millon_usd=price.precio_completion_por_millon_usd if price else None,
    ))


def _save_chat_exchange(sesion, contenido, respuesta_text, citas_json, tipo_interaccion, image_name=None):
    """Persist a student message and its assistant reply, including fallback replies."""
    msg_user = MensajeChat(
        sesion_chat_id=sesion.id,
        rol='user',
        contenido=contenido,
        imagen_nombre=image_name,
        tipo_interaccion=tipo_interaccion,
    )
    msg_assistant = MensajeChat(
        sesion_chat_id=sesion.id,
        rol='assistant',
        contenido=respuesta_text,
        citas_contexto_json=citas_json,
        tipo_interaccion=tipo_interaccion,
    )
    db.session.add(msg_user)
    db.session.add(msg_assistant)
    db.session.commit()
    return msg_user, msg_assistant


# ============================================================================
# ENROLLED COURSES
# ============================================================================

@estudiante_bp.route('/cursos', methods=['GET'])
@jwt_required()
def get_cursos():
    """List all courses the authenticated student is enrolled in."""
    user_id = get_jwt_identity()
    enrollments = EstudianteCurso.query.filter_by(user_id=user_id, is_active=True).all()

    cursos = []
    for e in enrollments:
        if e.curso:
            c = e.curso.to_dict()
            c['fecha_inscripcion'] = e.fecha_inscripcion.isoformat()
            cursos.append(c)

    return jsonify({'cursos': cursos, 'total': len(cursos)}), 200


# ============================================================================
# CHAT SESSIONS
# ============================================================================

@estudiante_bp.route('/chat/sesiones', methods=['GET'])
@jwt_required()
def list_sesiones():
    """List active chat sessions for the current student, optionally filtered by curso_id."""
    user_id = get_jwt_identity()
    curso_id = request.args.get('curso_id', type=int)

    query = SesionChat.query.filter_by(user_id=user_id, is_active=True)
    if curso_id:
        query = query.filter_by(curso_id=curso_id)

    sesiones = query.order_by(SesionChat.updated_at.desc()).all()
    return jsonify({'sesiones': [s.to_dict() for s in sesiones], 'total': len(sesiones)}), 200


@estudiante_bp.route('/chat/sesiones', methods=['POST'])
@jwt_required()
def create_sesion():
    """Create a new chat session for a course the student is enrolled in."""
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    curso_id = data.get('curso_id')
    logger.info(f'Creating sesión: user_id={user_id}, curso_id={curso_id}, data={data}')
    
    if not curso_id:
        return jsonify({'message': 'curso_id es requerido'}), 400

    # Asegurar que curso_id es int
    try:
        curso_id = int(curso_id)
    except (ValueError, TypeError):
        logger.error(f'Invalid curso_id type: {type(curso_id)}, value={curso_id}')
        return jsonify({'message': 'curso_id debe ser un número'}), 400

    if not _is_enrolled(user_id, curso_id):
        logger.warning(f'User {user_id} not enrolled in curso {curso_id}')
        return jsonify({'message': 'No estás inscrito en este curso'}), 403

    try:
        titulo = (data.get('titulo') or '').strip() or 'Nueva Conversación'
        sesion = SesionChat(user_id=user_id, curso_id=curso_id, titulo=titulo)
        db.session.add(sesion)
        db.session.commit()
        logger.info(f'✓ Sesión creada: {sesion.id}')
        return jsonify({'sesion': sesion.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        logger.exception(f'Error creando sesión: user_id={user_id}, curso_id={curso_id}, error={str(e)}')
        return jsonify({'message': 'Error al crear la sesión', 'error': str(e)}), 500


@estudiante_bp.route('/chat/sesiones/<string:sesion_id>', methods=['PATCH'])
@jwt_required()
def rename_sesion(sesion_id):
    """Rename a chat session title."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    data = request.get_json() or {}
    titulo = (data.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'message': 'titulo es requerido'}), 400

    sesion.titulo = titulo
    db.session.commit()
    return jsonify({'sesion': sesion.to_dict()}), 200


@estudiante_bp.route('/chat/sesiones/<string:sesion_id>', methods=['DELETE'])
@jwt_required()
def delete_sesion(sesion_id):
    """Soft-delete a chat session (sets is_active=False)."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    sesion.is_active = False
    db.session.commit()
    return jsonify({'message': 'Sesión eliminada'}), 200


# ============================================================================
# MESSAGES
# ============================================================================

@estudiante_bp.route('/chat/sesiones/<string:sesion_id>/mensajes', methods=['GET'])
@jwt_required()
def get_mensajes(sesion_id):
    """Get all messages in a chat session in chronological order."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    mensajes = sesion.mensajes.order_by(MensajeChat.created_at.asc()).all()
    return jsonify({'mensajes': [m.to_dict() for m in mensajes], 'total': len(mensajes)}), 200


@estudiante_bp.route('/chat/sesiones/<string:sesion_id>/contexto', methods=['GET'])
@jwt_required()
def get_sesion_contexto(sesion_id):
    """Get context information for a chat session (course info, enabled modes, etc)."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    curso = Curso.query.get(sesion.curso_id)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    config = ConfiguracionIA.query.get(sesion.curso_id)
    modos = []
    if config and config.modos_permitidos:
        modos = [m.strip() for m in config.modos_permitidos.split(',') if m.strip()]

    contexto = {
        'sesion_id': sesion.id,
        'curso_id': curso.id,
        'materia_nombre': curso.nombre,
        'codigo_curso': curso.codigo,
        'modos_permitidos': modos,
    }
    return jsonify({'contexto': contexto}), 200


@estudiante_bp.route('/chat/sesiones/<string:sesion_id>/mensaje', methods=['POST'])
@jwt_required()
def send_mensaje(sesion_id):
    """Send a user message and receive an AI response via n8n."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if not _is_enrolled(user_id, sesion.curso_id):
        return jsonify({'message': 'No estás inscrito en este curso'}), 403

    if not _modo_habilitado(sesion.curso_id, 'chat'):
        return jsonify({'message': 'El chat está deshabilitado para este curso'}), 403

    data = request.get_json() or {}
    contenido = (data.get('contenido') or '').strip()
    try:
        image = _validated_chat_image(data)
    except ValueError as exc:
        return jsonify({'message': str(exc)}), 400
    if not contenido and not image:
        return jsonify({'message': 'contenido o imagen es requerido'}), 400
    contenido = contenido or 'Analiza la imagen adjunta.'

    curso = Curso.query.get(sesion.curso_id)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404
    reservation_tokens = _token_reservation(contenido)
    quota_error, quota = _quota_error(curso, reservation_tokens)
    if quota_error:
        return quota_error
    if not quota:
        return jsonify({'message': 'No fue posible verificar la cuota de tokens.'}), 503

    payload = _build_n8n_chat_payload(
        sesion=sesion,
        message=contenido,
        requested_mode='chat',
        student_id=user_id,
        max_tokens=min(MAX_COMPLETION_TOKENS, quota['tokens_disponibles']),
        image=image,
    )

    service_unavailable = False
    try:
        respuesta_text, citas_json, usage, modo_aplicado = _call_n8n_chat(payload)
    except Exception:
        logger.exception('student_chat_n8n_unavailable', extra={'event': 'student_chat_n8n_unavailable'})
        respuesta_text = CHAT_SERVICE_UNAVAILABLE_MESSAGE
        citas_json = None
        usage = None
        modo_aplicado = None
        service_unavailable = True

    msg_user, msg_assistant = _save_chat_exchange(
        sesion, contenido, respuesta_text, citas_json, 'consulta', image.get('name') if image else None,
    )
    if not service_unavailable:
        _record_consumption(curso, user_id, 'chat_rag', contenido, respuesta_text, usage)
        db.session.commit()

    return jsonify({
        'mensaje_usuario': msg_user.to_dict(),
        'mensaje_asistente': msg_assistant.to_dict(),
        'modo_solicitado': 'chat',
        'modo_aplicado': modo_aplicado,
        'service_unavailable': service_unavailable,
    }), 200


# ============================================================================
# AGENDA
# ============================================================================

@estudiante_bp.route('/agenda', methods=['GET'])
@jwt_required()
def get_agenda():
    """Get upcoming activities for all courses the student is enrolled in."""
    user_id = get_jwt_identity()
    enrollments = EstudianteCurso.query.filter_by(user_id=user_id, is_active=True).all()
    curso_ids = [e.curso_id for e in enrollments]

    if not curso_ids:
        return jsonify({'actividades': [], 'total': 0}), 200

    estado = request.args.get('estado', 'vigente')
    actividades = (
        ActividadAgenda.query
        .filter(
            ActividadAgenda.curso_id.in_(curso_ids),
            ActividadAgenda.estado == estado,
        )
        .order_by(ActividadAgenda.fecha_limite.asc())
        .all()
    )

    return jsonify({'actividades': [a.to_dict() for a in actividades], 'total': len(actividades)}), 200


# ============================================================================
# SYNTHETIC RESOURCES (CU-10)
# ============================================================================

@estudiante_bp.route('/chat/sesiones/<string:sesion_id>/recurso-sintetico', methods=['POST'])
@jwt_required()
def recurso_sintetico(sesion_id):
    """Request a synthetic resource (summary, concept map, etc.) for the session topic."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if not _is_enrolled(user_id, sesion.curso_id):
        return jsonify({'message': 'No estás inscrito en este curso'}), 403

    if not _modo_habilitado(sesion.curso_id, 'recursos'):
        return jsonify({'message': 'Los recursos sintéticos están deshabilitados para este curso'}), 403

    data = request.get_json() or {}
    contenido = (data.get('contenido') or '').strip() or 'Generar recurso sintético'
    tipo_recurso = (data.get('tipo_recurso') or 'resumen').strip()
    try:
        image = _validated_chat_image(data)
    except ValueError as exc:
        return jsonify({'message': str(exc)}), 400
    curso = Curso.query.get(sesion.curso_id)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404
    reservation_tokens = _token_reservation(contenido)
    quota_error, quota = _quota_error(curso, reservation_tokens)
    if quota_error:
        return quota_error
    if not quota:
        return jsonify({'message': 'No fue posible verificar la cuota de tokens.'}), 503

    payload = _build_n8n_chat_payload(
        sesion=sesion,
        message=contenido,
        requested_mode='recursos',
        student_id=user_id,
        max_tokens=min(MAX_COMPLETION_TOKENS, quota['tokens_disponibles']),
        image=image,
    )

    try:
        respuesta_text, citas_json, usage, modo_aplicado = _call_n8n_chat(payload)
    except Exception as e:
        return jsonify({'message': f'Error al generar recurso: {str(e)}'}), 502

    msg_user, msg_assistant = _save_chat_exchange(
        sesion,
        contenido,
        respuesta_text,
        citas_json,
        'recurso_sintetico',
        image.get('name') if image else None,
    )
    _record_consumption(curso, user_id, 'resumen_sintetico', contenido, respuesta_text, usage)
    db.session.commit()

    return jsonify({
        'recurso': msg_assistant.to_dict(),
        'mensaje_usuario': msg_user.to_dict(),
        'mensaje_asistente': msg_assistant.to_dict(),
        'modo_aplicado': modo_aplicado,
    }), 200


# ============================================================================
# PRACTICE HELP (CU-11)
# ============================================================================

@estudiante_bp.route('/chat/sesiones/<string:sesion_id>/practicar', methods=['POST'])
@jwt_required()
def ayuda_practica(sesion_id):
    """Guide the student through practicing an exercise or problem."""
    user_id = get_jwt_identity()
    sesion = _get_session_for_user(sesion_id, user_id)
    if not sesion:
        return jsonify({'message': 'Sesión no encontrada'}), 404

    if not _is_enrolled(user_id, sesion.curso_id):
        return jsonify({'message': 'No estás inscrito en este curso'}), 403

    if not _modo_habilitado(sesion.curso_id, 'practicar'):
        return jsonify({'message': 'El modo práctica está deshabilitado para este curso'}), 403

    data = request.get_json() or {}
    ejercicio = (data.get('ejercicio') or data.get('contenido') or data.get('mensaje') or '').strip()
    try:
        image = _validated_chat_image(data)
    except ValueError as exc:
        return jsonify({'message': str(exc)}), 400
    if not ejercicio and not image:
        return jsonify({'message': 'ejercicio o imagen es requerido'}), 400
    ejercicio = ejercicio or 'Ayúdame a resolver el ejercicio de la imagen adjunta.'

    curso = Curso.query.get(sesion.curso_id)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404
    reservation_tokens = _token_reservation(ejercicio)
    quota_error, quota = _quota_error(curso, reservation_tokens)
    if quota_error:
        return quota_error
    if not quota:
        return jsonify({'message': 'No fue posible verificar la cuota de tokens.'}), 503

    payload = _build_n8n_chat_payload(
        sesion=sesion,
        message=ejercicio,
        requested_mode='practicar',
        student_id=user_id,
        max_tokens=min(MAX_COMPLETION_TOKENS, quota['tokens_disponibles']),
        image=image,
    )

    service_unavailable = False
    try:
        respuesta_text, citas_json, usage, modo_aplicado = _call_n8n_chat(payload)
    except Exception:
        logger.exception('student_practice_n8n_unavailable', extra={'event': 'student_practice_n8n_unavailable'})
        respuesta_text = CHAT_SERVICE_UNAVAILABLE_MESSAGE
        citas_json = None
        usage = None
        modo_aplicado = None
        service_unavailable = True

    msg_user, msg_assistant = _save_chat_exchange(
        sesion, ejercicio, respuesta_text, citas_json, 'practicar', image.get('name') if image else None,
    )
    if not service_unavailable:
        _record_consumption(curso, user_id, 'practicar', ejercicio, respuesta_text, usage)
        db.session.commit()

    return jsonify({
        'mensaje_usuario': msg_user.to_dict(),
        'mensaje_asistente': msg_assistant.to_dict(),
        'modo_solicitado': 'practicar',
        'modo_aplicado': modo_aplicado,
        'service_unavailable': service_unavailable,
    }), 200

