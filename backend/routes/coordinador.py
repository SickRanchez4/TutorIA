"""
Coordinator routes - Academic Management
- Course management (CRUD)
- Student enrollment (direct course assignment)
- Analytics and monitoring
- RAG and AI configuration
"""
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json
import os
import logging
import requests as http_requests
from sqlalchemy.orm import joinedload
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from openpyxl import load_workbook

logger = logging.getLogger(__name__)

from models import (
    db,
    Institucion,
    Curso,
    EstudianteCurso,
    ConfiguracionIA,
    ConsumoTokens,
    SesionChat,
    MensajeChat,
    LogNotificacion,
    RagIngestionJob,
)
from models.user import User
from models.role import Role
from werkzeug.security import generate_password_hash
from routes.auth_multi_tenant import coordinador_required
from services.subscription_quota import subscription_summary
from services.rag_ingestion import (
    RagIngestionError,
    course_knowledge_overview,
    create_ingestion_job,
    dispatch_ingestion_job,
    clear_course_knowledge,
    get_managed_course,
    remove_indexed_document,
    retry_ingestion_job,
)

coordinador_bp = Blueprint('coordinador', __name__)

N8N_EMBEDDINGS_WEBHOOK_URL = os.environ.get('N8N_EMBEDDINGS_WEBHOOK_URL', '')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _current_user():
    """Get the current authenticated user."""
    user = User.query.get(get_jwt_identity())
    return user

def _normalize_key(s):
    """Normalize string for key matching (lowercase, remove accents, etc)."""
    if s is None:
        return ''
    key = str(s).strip().lower()
    key = key.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    key = key.replace('-', '_').replace(' ', '_')
    return key

def _pick_by_alias(row, aliases):
    """Extract value from dict using multiple possible key names (aliases)."""
    if not isinstance(row, dict):
        return ''
    normalized = {_normalize_key(k): v for k, v in row.items()}
    for alias in aliases:
        val = normalized.get(_normalize_key(alias))
        if val is not None and str(val).strip() != '':
            return str(val).strip()
    return ''

def _split_full_name(full_name):
    """Split full name into first name and last name."""
    parts = [p for p in (full_name or '').strip().split() if p]
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    return ' '.join(parts[:-1]), parts[-1]

def _normalize_student_row(row):
    """Normalize student data from Excel row."""
    email = _pick_by_alias(row, ['email', 'correo', 'correo_electronico', 'mail'])
    first_name = _pick_by_alias(row, ['first_name', 'nombre', 'nombres', 'name'])
    last_name = _pick_by_alias(row, ['last_name', 'apellido', 'apellidos', 'surname'])
    phone = _pick_by_alias(row, ['phone', 'telefono', 'celular', 'movil', 'phone_number'])

    # Excel often serializes phone numbers as floats (e.g. 71234567.0).
    # Normalize this format to plain digits when the decimal part is .0.
    phone_clean = (str(phone) if phone else '').strip()
    if phone_clean.endswith('.0'):
        base = phone_clean[:-2]
        if base.replace('+', '', 1).isdigit():
            phone_clean = base

    # Try to extract from full_name if first/last not found separately
    if (not first_name or not last_name) and isinstance(row, dict):
        full_name = _pick_by_alias(row, ['full_name', 'nombre_completo', 'student_name'])
        if full_name:
            f, l = _split_full_name(full_name)
            first_name = first_name or f
            last_name = last_name or l

    return {
        'email': (email or '').strip().lower(),
        'first_name': (first_name or '').strip(),
        'last_name': (last_name or '').strip(),
        'phone': phone_clean,
    }

DEFAULT_STUDENT_PASSWORD = 'password'

def _get_or_create_estudiante(email, first_name, last_name, phone, institucion_id):
    """
    Find an existing user by email or create a new one with the 'estudiante' role.
    New accounts get the default password DEFAULT_STUDENT_PASSWORD.
    Returns (user, created_bool). Does not commit; caller must commit/flush.
    """
    usuario = User.query.filter_by(email=email).first()
    if usuario:
        return usuario, False

    usuario = User(
        email=email,
        first_name=first_name or 'Alumno',
        last_name=last_name or '',
        phone=phone or '',
        institucion_id=institucion_id,
        password_hash=generate_password_hash(DEFAULT_STUDENT_PASSWORD),
        is_active=True,
    )
    estudiante_role = Role.query.filter_by(name='estudiante').first()
    if estudiante_role:
        usuario.roles.append(estudiante_role)
    db.session.add(usuario)
    db.session.flush()  # Get the ID before commit
    return usuario, True

def _validate_institucion_scope(user, institucion_id):
    """Validate that user belongs to the specified institution."""
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    if not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion asignada'}), 403
    if str(user.institucion_id) != str(institucion_id):
        return jsonify({'message': 'Acceso denegado para otra institucion'}), 403
    return None

def _read_excel_rows(file_storage):
    """Read and parse Excel file into list of dicts."""
    wb = load_workbook(file_storage, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() if h is not None else '' for h in rows[0]]
    result = []
    for r in rows[1:]:
        row_dict = {}
        for idx, cell in enumerate(r):
            key = headers[idx] if idx < len(headers) else f'col_{idx}'
            row_dict[key] = '' if cell is None else str(cell).strip()
        result.append(row_dict)
    return result

# ============================================================================
# COURSE MANAGEMENT ENDPOINTS
# ============================================================================

@coordinador_bp.route('/cursos', methods=['GET'])
@jwt_required()
@coordinador_required
def list_cursos():
    """List all courses for the coordinator's institution, including student counts."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    cursos = Curso.query.filter_by(institucion_id=user.institucion_id).all()
    cursos_data = []
    for c in cursos:
        curso_dict = c.to_dict()
        # Count enrolled students
        count_estudiantes = EstudianteCurso.query.filter_by(curso_id=c.id, is_active=True).count()
        curso_dict['estudiantes_count'] = count_estudiantes
        cursos_data.append(curso_dict)
    return jsonify({'cursos': cursos_data}), 200

@coordinador_bp.route('/cursos', methods=['POST'])
@jwt_required()
@coordinador_required
def create_curso():
    """Create a new course."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    data = request.get_json() or {}
    required = ['nombre', 'codigo']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos: {", ".join(missing)}'}), 400

    # Check for duplicate codigo
    existing = Curso.query.filter_by(
        institucion_id=user.institucion_id,
        codigo=data['codigo'].strip()
    ).first()
    if existing:
        return jsonify({'message': f'Ya existe un curso con codigo {data["codigo"]}'}), 409

    curso = Curso(
        institucion_id=user.institucion_id,
        nombre=data['nombre'].strip(),
        codigo=data['codigo'].strip(),
        descripcion=(data.get('descripcion') or '').strip() or None,
        is_active=data.get('is_active', True)
    )
    db.session.add(curso)
    db.session.commit()
    return jsonify({'message': 'Curso creado', 'curso': curso.to_dict()}), 201

@coordinador_bp.route('/cursos/importar/excel', methods=['POST'])
@jwt_required()
@coordinador_required
def import_cursos_excel():
    """Bulk-create courses from an Excel file (columns: nombre, codigo)."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    try:
        rows = _read_excel_rows(file)
    except Exception as e:
        return jsonify({'message': f'Error reading Excel: {str(e)}'}), 400

    if not rows:
        return jsonify({'message': 'Excel file is empty', 'created': 0, 'skipped': []}), 200

    existing_codes = {
        c.codigo for c in Curso.query.filter_by(institucion_id=user.institucion_id).all()
    }

    created = 0
    skipped = []
    for row in rows:
        nombre = _pick_by_alias(row, ['nombre', 'name', 'curso'])
        codigo = _pick_by_alias(row, ['codigo', 'code', 'código'])
        descripcion = _pick_by_alias(row, ['descripcion', 'description', 'descripción']) or None
        if not nombre or not codigo:
            skipped.append({'row': row, 'reason': 'Missing nombre or codigo'})
            continue
        if codigo in existing_codes:
            skipped.append({'row': row, 'reason': f'Codigo duplicado: {codigo}'})
            continue

        db.session.add(Curso(
            institucion_id=user.institucion_id,
            nombre=nombre,
            codigo=codigo,
            descripcion=descripcion,
            is_active=True,
        ))
        existing_codes.add(codigo)
        created += 1

    db.session.commit()
    return jsonify({'message': 'Cursos importados', 'created': created, 'skipped': skipped}), 200

@coordinador_bp.route('/cursos/<int:curso_id>', methods=['GET'])
@jwt_required()
@coordinador_required
def get_curso(curso_id):
    """Get a single course with enrollment count."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    curso_dict = curso.to_dict()
    curso_dict['estudiantes_count'] = EstudianteCurso.query.filter_by(curso_id=curso.id, is_active=True).count()
    return jsonify({'curso': curso_dict}), 200

@coordinador_bp.route('/cursos/<int:curso_id>', methods=['PUT'])
@jwt_required()
@coordinador_required
def update_curso(curso_id):
    """Update an existing course."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    data = request.get_json() or {}
    if 'nombre' in data:
        curso.nombre = data['nombre'].strip()
    if 'codigo' in data:
        new_code = data['codigo'].strip()
        exists = Curso.query.filter(
            Curso.institucion_id == user.institucion_id,
            Curso.id != curso.id,
            Curso.codigo == new_code
        ).first()
        if exists:
            return jsonify({'message': f'Ya existe otro curso con codigo {new_code}'}), 409
        curso.codigo = new_code
    if 'descripcion' in data:
        curso.descripcion = (data['descripcion'] or '').strip() or None
    if 'is_active' in data:
        curso.is_active = bool(data['is_active'])

    db.session.commit()
    return jsonify({'message': 'Curso actualizado', 'curso': curso.to_dict()}), 200

@coordinador_bp.route('/cursos/<int:curso_id>', methods=['DELETE'])
@jwt_required()
@coordinador_required
def delete_curso(curso_id):
    """Permanently delete a course from the database (irreversible)."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    try:
        nombre = curso.nombre
        # Dependent rows without ON DELETE CASCADE must be removed explicitly first
        EstudianteCurso.query.filter_by(curso_id=curso.id).delete()
        RagIngestionJob.query.filter_by(curso_id=curso.id).delete()
        db.session.delete(curso)
        db.session.commit()
        return jsonify({'message': f'Curso {nombre} eliminado permanentemente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar curso: {str(e)}'}), 500

# ============================================================================
# STUDENT ENROLLMENT ENDPOINTS
# ============================================================================

@coordinador_bp.route('/estudiantes', methods=['GET'])
@jwt_required()
@coordinador_required
def list_estudiantes():
    """List all student accounts for the coordinator's institution.

    Includes accounts that are not currently enrolled in any course, so
    coordinators can manage (edit/delete) every student account, not just
    those with active enrollments. Each account is flagged 'matriculado'
    (true/false) based on whether it has at least one active enrollment.
    """
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    estudiante_role = Role.query.filter_by(name='estudiante').first()
    if not estudiante_role:
        return jsonify({'estudiantes': []}), 200

    estudiantes_users = [
        u for u in estudiante_role.users
        if u.institucion_id and str(u.institucion_id) == str(user.institucion_id)
    ]

    curso_ids = [c.id for c in Curso.query.filter_by(institucion_id=user.institucion_id).all()]
    enrollments = (
        EstudianteCurso.query.filter(EstudianteCurso.curso_id.in_(curso_ids)).all()
        if curso_ids else []
    )
    enrollments_by_user = defaultdict(list)
    for e in enrollments:
        enrollments_by_user[e.user_id].append(e)

    estudiantes_data = []
    for u in estudiantes_users:
        active_enrollments = [e for e in enrollments_by_user.get(u.id, []) if e.is_active]
        estudiantes_data.append({
            'id': u.id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'full_name': u.full_name,
            'phone': u.phone,
            'is_active': u.is_active,
            'matriculado': len(active_enrollments) > 0,
            'cursos': [
                {'id': e.curso.id, 'nombre': e.curso.nombre, 'codigo': e.curso.codigo}
                for e in active_enrollments if e.curso
            ],
        })

    estudiantes_data.sort(key=lambda x: (x['full_name'] or '').lower())
    
    # Apply search filter if provided
    search_query = (request.args.get('search') or '').strip().lower()
    if search_query:
        estudiantes_data = [
            e for e in estudiantes_data 
            if search_query in (e.get('email') or '').lower() or 
               search_query in (e.get('full_name') or '').lower()
        ]
    
    return jsonify({'estudiantes': estudiantes_data}), 200

@coordinador_bp.route('/estudiantes/<string:user_id>', methods=['PUT'])
@jwt_required()
@coordinador_required
def update_estudiante(user_id):
    """Edit a student account's basic info (name, phone, email, status, password)."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    estudiante = User.query.filter_by(id=user_id, institucion_id=user.institucion_id).first()
    if not estudiante:
        return jsonify({'message': 'Alumno no encontrado'}), 404

    data = request.get_json() or {}
    if 'first_name' in data:
        estudiante.first_name = (data['first_name'] or '').strip() or estudiante.first_name
    if 'last_name' in data:
        estudiante.last_name = (data['last_name'] or '').strip()
    if 'phone' in data:
        estudiante.phone = (data['phone'] or '').strip()
    if 'email' in data:
        new_email = (data['email'] or '').strip().lower()
        if new_email and new_email != estudiante.email:
            exists = User.query.filter(User.email == new_email, User.id != estudiante.id).first()
            if exists:
                return jsonify({'message': 'Ya existe una cuenta con ese email'}), 409
            estudiante.email = new_email
    if 'is_active' in data:
        estudiante.is_active = bool(data['is_active'])
    if data.get('password'):
        estudiante.password_hash = generate_password_hash(data['password'])

    db.session.commit()
    return jsonify({
        'message': 'Cuenta actualizada',
        'estudiante': {
            'id': estudiante.id,
            'email': estudiante.email,
            'first_name': estudiante.first_name,
            'last_name': estudiante.last_name,
            'full_name': estudiante.full_name,
            'phone': estudiante.phone,
            'is_active': estudiante.is_active,
        },
    }), 200

@coordinador_bp.route('/estudiantes/<string:user_id>', methods=['DELETE'])
@jwt_required()
@coordinador_required
def delete_estudiante(user_id):
    """Permanently delete a student account and all of its related data."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    estudiante = User.query.filter_by(id=user_id, institucion_id=user.institucion_id).first()
    if not estudiante:
        return jsonify({'message': 'Alumno no encontrado'}), 404

    try:
        nombre = estudiante.full_name
        EstudianteCurso.query.filter_by(user_id=estudiante.id).delete()
        ConsumoTokens.query.filter_by(user_id=estudiante.id).delete()
        LogNotificacion.query.filter_by(user_id=estudiante.id).delete()
        sesion_ids = [s.id for s in SesionChat.query.filter_by(user_id=estudiante.id).all()]
        if sesion_ids:
            MensajeChat.query.filter(MensajeChat.sesion_chat_id.in_(sesion_ids)).delete(synchronize_session=False)
            SesionChat.query.filter_by(user_id=estudiante.id).delete()
        db.session.delete(estudiante)
        db.session.commit()
        return jsonify({'message': f'Cuenta de {nombre} eliminada permanentemente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar cuenta: {str(e)}'}), 500

@coordinador_bp.route('/cursos/<int:curso_id>/estudiantes', methods=['GET'])
@jwt_required()
@coordinador_required
def list_estudiantes_curso(curso_id):
    """List students enrolled in a single course."""
    try:
        user = _current_user()
        curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
        if not curso:
            return jsonify({'message': 'Curso no encontrado'}), 404

        # Eager load user relation to avoid N+1 queries when rendering students.
        enrollments = (
            EstudianteCurso.query
            .options(joinedload(EstudianteCurso.user))
            .filter_by(curso_id=curso.id, is_active=True)
            .all()
        )
        estudiantes = []
        for e in enrollments:
            est = {
                'enrollment_id': e.id,
                'user_id': e.user_id,
                'email': e.user.email if e.user else None,
                'full_name': e.user.full_name if e.user else 'Unknown',
                'fecha_inscripcion': e.fecha_inscripcion.isoformat() if e.fecha_inscripcion else None,
            }
            estudiantes.append(est)
        return jsonify({'estudiantes': estudiantes}), 200
    except Exception as ex:
        logger.error(f'Error loading students for course {curso_id}: {str(ex)}', exc_info=True)
        return jsonify({'message': 'Error loading students', 'error': str(ex)}), 500

@coordinador_bp.route('/cursos/<int:curso_id>/estudiantes', methods=['POST'])
@jwt_required()
@coordinador_required
def add_estudiante_curso(curso_id):
    """Enroll a single student in a course (creates the user if the email doesn't exist yet)."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({'message': 'El email es requerido'}), 400

    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    phone = (data.get('phone') or '').strip()

    # Si solo viene email (sin first_name/last_name/phone), es inscripción de alumno existente
    # Si vienen otros campos, es creación de nuevo alumno
    if not first_name and not last_name and not phone:
        # Buscar alumno existente - no crear si no existe
        usuario = User.query.filter_by(email=email, institucion_id=user.institucion_id).first()
        if not usuario:
            return jsonify({'message': 'El alumno con este email no existe. Usa la opción "Crear nuevo" para registrar un alumno nuevo'}), 404
    else:
        # Crear o actualizar alumno existente
        usuario, _created = _get_or_create_estudiante(email, first_name, last_name, phone, user.institucion_id)

    existing = EstudianteCurso.query.filter_by(user_id=usuario.id, curso_id=curso.id).first()
    if existing:
        if existing.is_active:
            return jsonify({'message': 'El alumno ya está inscrito en este curso'}), 409
        existing.is_active = True
    else:
        db.session.add(EstudianteCurso(user_id=usuario.id, curso_id=curso.id, is_active=True))

    db.session.commit()
    return jsonify({'message': 'Alumno inscrito', 'user_id': usuario.id}), 201

@coordinador_bp.route('/cursos/<int:curso_id>/estudiantes/<string:user_id>', methods=['DELETE'])
@jwt_required()
@coordinador_required
def remove_estudiante_curso(curso_id, user_id):
    """Unenroll a student from a course."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    enrollment = EstudianteCurso.query.filter_by(curso_id=curso.id, user_id=user_id).first()
    if not enrollment:
        return jsonify({'message': 'Inscripción no encontrada'}), 404

    enrollment.is_active = False
    db.session.commit()
    return jsonify({'message': 'Alumno desinscrito del curso'}), 200

@coordinador_bp.route('/cursos/<int:curso_id>/estudiantes/importar/excel', methods=['POST'])
@jwt_required()
@coordinador_required
def import_estudiantes_curso_excel(curso_id):
    """Import students from Excel and enroll them all in a single given course."""
    user = _current_user()
    curso = Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    try:
        rows = _read_excel_rows(file)
    except Exception as e:
        return jsonify({'message': f'Error reading Excel: {str(e)}'}), 400

    created = 0
    enrolled = 0
    skipped = []

    for row in rows:
        normalized = _normalize_student_row(row)
        email = normalized['email']
        first_name = normalized['first_name']
        last_name = normalized['last_name']
        phone = normalized['phone']

        if not email or not first_name or not last_name:
            skipped.append({'row': row, 'reason': 'Missing email, first_name, or last_name'})
            continue

        usuario, was_created = _get_or_create_estudiante(email, first_name, last_name, phone, user.institucion_id)
        if was_created:
            created += 1

        existing = EstudianteCurso.query.filter_by(user_id=usuario.id, curso_id=curso.id).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                enrolled += 1
        else:
            db.session.add(EstudianteCurso(user_id=usuario.id, curso_id=curso.id, is_active=True))
            enrolled += 1

    db.session.commit()
    return jsonify({
        'message': 'Alumnos importados',
        'created': created,
        'enrolled': enrolled,
        'skipped': skipped,
    }), 200

@coordinador_bp.route('/estudiantes/importar/excel', methods=['POST'])
@jwt_required()
@coordinador_required
def import_alumnos_cursos_excel():
    """Import students and enroll them in courses from Excel file."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    try:
        rows = _read_excel_rows(file)
    except Exception as e:
        return jsonify({'message': f'Error reading Excel: {str(e)}'}), 400

    if not rows:
        return jsonify({'message': 'Excel file is empty', 'created': 0, 'enrolled': 0, 'skipped': []}), 200

    # Build mapping of course codes to curso objects
    cursos = Curso.query.filter_by(institucion_id=user.institucion_id).all()
    cursos_by_code = {c.codigo: c for c in cursos}

    created = 0
    enrolled = 0
    skipped = []

    for row in rows:
        normalized = _normalize_student_row(row)
        email = normalized['email']
        first_name = normalized['first_name']
        last_name = normalized['last_name']
        phone = normalized['phone']

        if not email or not first_name or not last_name:
            skipped.append({
                'row': row,
                'reason': 'Missing email, first_name, or last_name'
            })
            continue

        # Create or get user
        usuario, was_created = _get_or_create_estudiante(
            email, first_name, last_name, phone, user.institucion_id
        )
        if was_created:
            created += 1

        # Extract course codes from the row (look for columns like 'curso_1', 'curso_2', etc.)
        target_codes = []
        for key, value in row.items():
            if key.lower().startswith('curso') and value and str(value).strip():
                code = str(value).strip()
                if code:
                    target_codes.append(code)

        # Enroll student in courses (direct EstudianteCurso)
        for code in target_codes:
            curso = cursos_by_code.get(code)
            if not curso:
                skipped.append({
                    'email': email,
                    'reason': f'Course code not found: {code}'
                })
                continue

            # Create enrollment if it doesn't already exist
            existing = EstudianteCurso.query.filter_by(
                user_id=usuario.id,
                curso_id=curso.id
            ).first()
            if not existing:
                db.session.add(EstudianteCurso(
                    user_id=usuario.id,
                    curso_id=curso.id,
                    is_active=True
                ))
                enrolled += 1

    db.session.commit()
    
    return jsonify({
        'message': 'Students imported successfully',
        'created': created,
        'enrolled': enrolled,
        'skipped': skipped
    }), 200

# ============================================================================
# CONFIGURATION & ANALYTICS ENDPOINTS
# ============================================================================

@coordinador_bp.route('/institucion/config', methods=['GET'])
@jwt_required()
@coordinador_required
def get_institucion_config():
    """Get institution configuration."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    institucion = Institucion.query.get(user.institucion_id)
    if not institucion:
        return jsonify({'message': 'Institucion no encontrada'}), 404

    return jsonify({
        'institucion': institucion.to_dict(),
        'suscripcion': subscription_summary(institucion.id),
    }), 200

@coordinador_bp.route('/institucion/config', methods=['PATCH'])
@jwt_required()
@coordinador_required
def update_institucion_config():
    """Update institution configuration."""
    user = _current_user()
    if not user or not user.institucion_id:
        return jsonify({'message': 'Usuario sin institucion'}), 403

    institucion = Institucion.query.get(user.institucion_id)
    if not institucion:
        return jsonify({'message': 'Institucion no encontrada'}), 404

    data = request.get_json() or {}
    
    # Update fields
    if 'nombre' in data and data['nombre']:
        institucion.nombre = data['nombre'].strip()
    if 'dominio_permitido' in data:
        institucion.dominio_permitido = (data['dominio_permitido'] or '').strip() or None
    
    db.session.commit()
    return jsonify({'message': 'Configuración actualizada', 'institucion': institucion.to_dict()}), 200

# ============================================================================
# AGENTE IA (ConfiguracionIA) PER COURSE
# ============================================================================

DEFAULT_SYSTEM_PROMPT = 'Eres un tutor académico. Responde de forma clara y basada en el material del curso.'

def _get_curso_or_404(curso_id, user):
    return Curso.query.filter_by(id=curso_id, institucion_id=user.institucion_id).first()

@coordinador_bp.route('/cursos/<int:curso_id>/agente', methods=['GET'])
@jwt_required()
@coordinador_required
def get_agente_curso(curso_id):
    """Get the AI agent configuration for a course (creates a default one if missing)."""
    user = _current_user()
    curso = _get_curso_or_404(curso_id, user)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    config = ConfiguracionIA.query.get(curso_id)
    if not config:
        config = ConfiguracionIA(curso_id=curso_id, system_prompt=DEFAULT_SYSTEM_PROMPT)
        db.session.add(config)
        db.session.commit()

    return jsonify({'agente': config.to_dict()}), 200

@coordinador_bp.route('/cursos/<int:curso_id>/agente', methods=['PUT'])
@jwt_required()
@coordinador_required
def update_agente_curso(curso_id):
    """Update the AI agent configuration for a course."""
    user = _current_user()
    curso = _get_curso_or_404(curso_id, user)
    if not curso:
        return jsonify({'message': 'Curso no encontrado'}), 404

    config = ConfiguracionIA.query.get(curso_id)
    if not config:
        config = ConfiguracionIA(curso_id=curso_id, system_prompt=DEFAULT_SYSTEM_PROMPT)
        db.session.add(config)

    data = request.get_json() or {}
    if 'system_prompt' in data:
        config.system_prompt = (data['system_prompt'] or '').strip() or DEFAULT_SYSTEM_PROMPT
    if 'temperatura' in data:
        try:
            temp = float(data['temperatura'])
        except (TypeError, ValueError):
            return jsonify({'message': 'Temperatura inválida'}), 400
        if not (0 <= temp <= 2):
            return jsonify({'message': 'Temperatura debe estar entre 0 y 2'}), 400
        config.temperatura = temp
    if 'modos_permitidos' in data:
        modos = data['modos_permitidos']
        config.modos_permitidos = ','.join(modos) if isinstance(modos, list) else str(modos)
    if 'extender_conocimiento' in data:
        config.extender_conocimiento = bool(data['extender_conocimiento'])

    db.session.commit()
    return jsonify({'message': 'Configuración del agente actualizada', 'agente': config.to_dict()}), 200

# ============================================================================
# CONOCIMIENTO (RAG) PER COURSE - Multiple PDF upload and processing
# ============================================================================

@coordinador_bp.route('/cursos/<int:curso_id>/conocimiento', methods=['GET'])
@jwt_required()
@coordinador_required
def get_conocimiento_curso(curso_id):
    """Return concise, tenant-scoped operational data for a course knowledge base."""
    try:
        return jsonify(course_knowledge_overview(_current_user(), curso_id)), 200
    except RagIngestionError as error:
        return jsonify({'message': str(error)}), error.status_code


@coordinador_bp.route('/cursos/<int:curso_id>/subir-materiales', methods=['POST'])
@jwt_required()
@coordinador_required
def subir_materiales_curso(curso_id):
    """Persist PDFs, dispatch them to n8n and retain an auditable ingestion job."""
    user = _current_user()
    curso = get_managed_course(user, curso_id) if user else None
    if not curso:
        return jsonify({'message': 'Curso no encontrado o sin permisos'}), 404

    archivos_subidos = [archivo for archivo in request.files.getlist('files') if archivo and archivo.filename]
    if not archivos_subidos:
        return jsonify({'message': 'No se proporcionó ningún archivo PDF'}), 400
    if any(not archivo.filename.lower().endswith('.pdf') for archivo in archivos_subidos):
        return jsonify({'message': 'Solo se permiten archivos PDF'}), 400

    try:
        job = create_ingestion_job(user, curso, archivos_subidos)
        dispatch_ingestion_job(job)
        return jsonify({
            'message': 'Material procesado correctamente',
            'trabajo': job.to_dict(),
        }), 200
    except RagIngestionError as error:
        return jsonify({'message': str(error)}), error.status_code
    except Exception:
        logger.exception('rag_ingestion_failed', extra={'event': 'rag_ingestion_failed'})
        return jsonify({'message': 'Error inesperado al procesar el material'}), 500


@coordinador_bp.route('/cursos/<int:curso_id>/conocimiento/trabajos/<string:job_id>/reintentar', methods=['POST'])
@jwt_required()
@coordinador_required
def reintentar_conocimiento_curso(curso_id, job_id):
    """Retry a failed or unknown ingestion while preserving the same auditable job."""
    try:
        job = RagIngestionJob.query.get(job_id)
        if not job or job.curso_id != curso_id:
            return jsonify({'message': 'Trabajo de indexación no encontrado'}), 404
        retried_job = retry_ingestion_job(_current_user(), job_id)
        return jsonify({'message': 'Indexación reintentada', 'trabajo': retried_job.to_dict()}), 200
    except RagIngestionError as error:
        return jsonify({'message': str(error)}), error.status_code


@coordinador_bp.route('/cursos/<int:curso_id>/conocimiento/operaciones', methods=['POST'])
@jwt_required()
@coordinador_required
def operar_conocimiento_curso(curso_id):
    """Execute one authorized knowledge-base operation through the n8n agent."""
    data = request.get_json() or {}
    action = (data.get('action') or '').strip()
    try:
        if action == 'delete_document':
            filename = data.get('archivo') or ''
            remove_indexed_document(_current_user(), curso_id, filename)
            return jsonify({'message': 'Documento eliminado de la base de conocimiento'}), 200
        if action == 'clear_course':
            deleted_jobs = clear_course_knowledge(_current_user(), curso_id)
            return jsonify({'message': 'Base de conocimiento vaciada', 'trabajos_eliminados': deleted_jobs}), 200
        return jsonify({'message': 'Operación de conocimiento no válida'}), 400
    except RagIngestionError as error:
        return jsonify({'message': str(error)}), error.status_code

@coordinador_bp.route('/analiticas/consumo', methods=['GET'])
@jwt_required()
@coordinador_required
def analytics_consumo():
    """Get token consumption analytics plus operational/quality KPIs for the institution."""
    user = _current_user()
    
    # Support both window (days) and custom date range
    days = request.args.get('days', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Determine time range
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if start_date_str and end_date_str:
        try:
            from_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
            # The date picker sends a date without a time. Use an exclusive
            # upper bound so the coordinator receives the full final day.
            to_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            to_date = to_date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        except (ValueError, AttributeError):
            return jsonify({'message': 'Invalid date format. Use ISO 8601 (YYYY-MM-DD).'}), 400
    else:
        # Fall back to days (default 30)
        days = days or 30
        from_date = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    tipo = (request.args.get('tipo') or '').strip()
    user_search = (request.args.get('user') or '').strip().lower()
    curso_id = request.args.get('curso_id', type=int)

    query = (
        ConsumoTokens.query
        .filter(ConsumoTokens.institucion_id == user.institucion_id)
        .filter(ConsumoTokens.fecha >= from_date)
        .filter(ConsumoTokens.fecha < to_date)
    )

    if tipo:
        query = query.filter(ConsumoTokens.tipo_operacion == tipo)

    if curso_id:
        query = query.filter(ConsumoTokens.curso_id == curso_id)

    rows = query.order_by(ConsumoTokens.fecha.asc()).all()

    if user_search:
        rows = [r for r in rows if r.user and user_search in (r.user.full_name or '').lower()]

    total_prompt = sum(r.prompt_tokens for r in rows)
    total_completion = sum(r.completion_tokens for r in rows)
    total_cost = sum(float(r.costo_estimado_usd) for r in rows)
    total_operaciones = len(rows)

    by_tipo = {}
    by_day = {}
    series_day = from_date.date()
    while series_day < to_date.date():
        by_day[series_day.isoformat()] = {'count': 0, 'tokens': 0, 'cost_usd': 0.0}
        series_day += timedelta(days=1)
    by_user = defaultdict(lambda: {'count': 0, 'tokens': 0, 'cost_usd': 0.0})
    by_curso = defaultdict(lambda: {'count': 0, 'tokens': 0, 'cost_usd': 0.0})
    operaciones_sin_curso = 0

    for r in rows:
        by_tipo.setdefault(r.tipo_operacion, {'tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0, 'cost_usd': 0.0, 'count': 0})
        by_tipo[r.tipo_operacion]['tokens'] += r.total_tokens
        by_tipo[r.tipo_operacion]['prompt_tokens'] += r.prompt_tokens
        by_tipo[r.tipo_operacion]['completion_tokens'] += r.completion_tokens
        by_tipo[r.tipo_operacion]['cost_usd'] += float(r.costo_estimado_usd)
        by_tipo[r.tipo_operacion]['count'] += 1

        day_key = r.fecha.strftime('%Y-%m-%d')
        by_day.setdefault(day_key, {'count': 0, 'tokens': 0, 'cost_usd': 0.0})
        by_day[day_key]['count'] += 1
        by_day[day_key]['tokens'] += r.total_tokens
        by_day[day_key]['cost_usd'] += float(r.costo_estimado_usd)

        user_name = r.user.full_name if r.user and r.user.full_name else 'Sin nombre'
        by_user[user_name]['count'] += 1
        by_user[user_name]['tokens'] += r.total_tokens
        by_user[user_name]['cost_usd'] += float(r.costo_estimado_usd)

        if r.curso_id:
            curso_key = str(r.curso_id)
            by_curso[curso_key]['count'] += 1
            by_curso[curso_key]['tokens'] += r.total_tokens
            by_curso[curso_key]['cost_usd'] += float(r.costo_estimado_usd)
        else:
            # Historic events without a course remain part of the institution
            # totals, but cannot be attributed to a course adoption report.
            operaciones_sin_curso += 1

    top_users = sorted(
        [{'user_nombre': k, **v} for k, v in by_user.items()],
        key=lambda x: x['cost_usd'],
        reverse=True,
    )[:5]

    curso_ids_in_rows = [int(k) for k in by_curso.keys()]
    cursos_lookup = {
        c.id: c for c in Curso.query.filter(Curso.id.in_(curso_ids_in_rows)).all()
    } if curso_ids_in_rows else {}
    breakdown_curso = sorted(
        [
            {
                'curso_id': int(k),
                'curso_nombre': cursos_lookup.get(int(k)).nombre if cursos_lookup.get(int(k)) else f'Curso #{k}',
                **v,
                'porcentaje_actividad': round((v['count'] / total_operaciones) * 100, 1) if total_operaciones else 0.0,
            }
            for k, v in by_curso.items()
        ],
        key=lambda x: x['cost_usd'],
        reverse=True,
    )

    # ------------------------------------------------------------------
    # Comparativa vs. periodo anterior (misma duracion, ventana previa)
    # ------------------------------------------------------------------
    # Calculate the window size in days
    window_days = (to_date - from_date).days
    if window_days == 0:
        window_days = 1  # Minimum 1 day window
    
    prev_from_date = from_date - timedelta(days=window_days)
    prev_query = (
        ConsumoTokens.query
        .filter(ConsumoTokens.institucion_id == user.institucion_id)
        .filter(ConsumoTokens.fecha >= prev_from_date)
        .filter(ConsumoTokens.fecha < from_date)
    )
    if tipo:
        prev_query = prev_query.filter(ConsumoTokens.tipo_operacion == tipo)
    if curso_id:
        prev_query = prev_query.filter(ConsumoTokens.curso_id == curso_id)
    prev_rows = prev_query.all()

    prev_total_tokens = sum(r.total_tokens for r in prev_rows)
    prev_total_cost = sum(float(r.costo_estimado_usd) for r in prev_rows)
    current_user_ids = {r.user_id for r in rows if r.user_id}
    prev_user_ids = {r.user_id for r in prev_rows if r.user_id}

    def _pct_delta(curr, prev):
        if not prev:
            return None
        return round(((curr - prev) / prev) * 100, 1)

    comparativa_periodo_anterior = {
        'operaciones_delta_pct': _pct_delta(total_operaciones, len(prev_rows)),
        'tokens_delta_pct': _pct_delta(total_prompt + total_completion, prev_total_tokens),
        'costo_delta_pct': _pct_delta(total_cost, prev_total_cost),
    }

    usuarios_recurrentes = len(current_user_ids & prev_user_ids)
    retencion = {
        'usuarios_periodo_anterior': len(prev_user_ids),
        'usuarios_recurrentes': usuarios_recurrentes,
        'porcentaje': round((usuarios_recurrentes / len(prev_user_ids)) * 100, 1) if prev_user_ids else None,
    }

    # ------------------------------------------------------------------
    # Sesiones de chat, mensajes y cobertura documental (RAG)
    # ------------------------------------------------------------------
    sesiones_query = (
        SesionChat.query
        .join(User, SesionChat.user_id == User.id)
        .filter(User.institucion_id == user.institucion_id)
        .filter(SesionChat.created_at >= from_date)
    )
    if curso_id:
        sesiones_query = sesiones_query.filter(SesionChat.curso_id == curso_id)
    sesiones_chat_iniciadas = sesiones_query.count()

    mensajes_query = (
        MensajeChat.query
        .join(SesionChat, MensajeChat.sesion_chat_id == SesionChat.id)
        .join(User, SesionChat.user_id == User.id)
        .filter(User.institucion_id == user.institucion_id)
        .filter(MensajeChat.created_at >= from_date)
    )
    if curso_id:
        mensajes_query = mensajes_query.filter(SesionChat.curso_id == curso_id)
    mensajes_totales = mensajes_query.count()

    mensajes_asistente = mensajes_query.filter(MensajeChat.rol == 'assistant').all()
    con_fuentes = 0
    for m in mensajes_asistente:
        if m.citas_contexto_json:
            try:
                if json.loads(m.citas_contexto_json):
                    con_fuentes += 1
            except (ValueError, TypeError):
                pass
    total_asistente = len(mensajes_asistente)
    cobertura_documental = {
        'respuestas_con_fuentes': con_fuentes,
        'respuestas_totales': total_asistente,
        'porcentaje': round((con_fuentes / total_asistente) * 100, 1) if total_asistente else None,
    }

    # ------------------------------------------------------------------
    # Fotografia institucional (no depende de la ventana de dias)
    # ------------------------------------------------------------------
    total_cursos = Curso.query.filter_by(institucion_id=user.institucion_id).count()
    cursos_activos = Curso.query.filter_by(institucion_id=user.institucion_id, is_active=True).count()
    total_estudiantes_matriculados = (
        db.session.query(EstudianteCurso.user_id)
        .join(Curso, EstudianteCurso.curso_id == Curso.id)
        .filter(Curso.institucion_id == user.institucion_id)
        .filter(EstudianteCurso.is_active == True)
        .distinct()
        .count()
    )
    estudiantes_habilitados = (
        db.session.query(User.id)
        .join(EstudianteCurso, EstudianteCurso.user_id == User.id)
        .join(Curso, EstudianteCurso.curso_id == Curso.id)
        .filter(Curso.institucion_id == user.institucion_id)
        .filter(EstudianteCurso.is_active == True)
        .filter(User.is_active == True)
        .distinct()
        .count()
    )

    resumen_institucion = {
        'total_cursos': total_cursos,
        'cursos_activos': cursos_activos,
        'total_estudiantes_matriculados': total_estudiantes_matriculados,
        'estudiantes_habilitados': estudiantes_habilitados,
    }

    participacion = {
        'estudiantes_activos': len(current_user_ids),
        'estudiantes_habilitados': estudiantes_habilitados,
        'porcentaje': round((len(current_user_ids) / estudiantes_habilitados) * 100, 1) if estudiantes_habilitados else None,
    }

    costo_promedio_operacion = round(total_cost / total_operaciones, 6) if total_operaciones else 0.0

    return jsonify({
        'window_days': window_days,
        'filters': {'tipo': tipo or None, 'user': user_search or None, 'curso_id': curso_id or None},
        'total_operaciones': total_operaciones,
        'total_prompt_tokens': total_prompt,
        'total_completion_tokens': total_completion,
        'total_tokens': total_prompt + total_completion,
        'total_cost_usd': round(total_cost, 6),
        'costo_promedio_operacion': costo_promedio_operacion,
        'alumnos_activos': len(current_user_ids),
        'participacion': participacion,
        'sesiones_chat_iniciadas': sesiones_chat_iniciadas,
        'mensajes_intercambiados': mensajes_totales,
        'cobertura_documental': cobertura_documental,
        'retencion': retencion,
        'comparativa_periodo_anterior': comparativa_periodo_anterior,
        'resumen_institucion': resumen_institucion,
        'breakdown_tipo_operacion': by_tipo,
        'daily_series': by_day,
        'top_users': top_users,
        'breakdown_curso': breakdown_curso,
        'operaciones_sin_curso': operaciones_sin_curso,
    }), 200

