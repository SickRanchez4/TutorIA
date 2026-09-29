"""
Authentication routes supporting multi-tenancy
"""
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app import limiter
from models.user import User
from models import db, Role, Institucion
from services.subscription_quota import account_creation_allowed
from services.validation import is_valid_email, normalize_email
from functools import wraps
import re
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


# =====================================================================
# PASSWORD VALIDATION
# =====================================================================

def validate_password(password):
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one digit
    - Contains at least one special character
    """
    if not isinstance(password, str):
        return False, "La contraseña debe ser texto"
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial"
    return True, ""


# =====================================================================
# AUTHORIZATION DECORATORS
# =====================================================================

def _load_active_user():
    """Load the current principal and reject revoked tenant access."""
    current_user = User.query.get(get_jwt_identity())
    if not current_user:
        return None, (jsonify({'message': 'Usuario no encontrado'}), 401)
    if not current_user.is_active:
        return None, (jsonify({'message': 'Usuario inactivo'}), 403)
    if current_user.institucion and not current_user.institucion.is_active:
        return None, (jsonify({'message': 'Institución no activa'}), 403)
    return current_user, None


def super_admin_required(fn):
    """Restrict endpoint to super_admin users only"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user, error = _load_active_user()
        if error or current_user is None:
            return error
        
        user_roles = [role.name for role in current_user.roles]
        if 'super_admin' not in user_roles:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de super administrador'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def coordinador_required(fn):
    """Restrict tenant-management endpoints to active coordinators."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user, error = _load_active_user()
        if error or current_user is None:
            return error
        
        user_roles = [role.name for role in current_user.roles]
        if 'coordinador' not in user_roles:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de coordinador'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def estudiante_required(fn):
    """Restrict student endpoints to active students in active institutions."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user, error = _load_active_user()
        if error or current_user is None:
            return error
        if 'estudiante' not in {role.name for role in current_user.roles}:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de estudiante'}), 403
        return fn(*args, **kwargs)

    return wrapper


def active_user_required(fn):
    """Reject inactive or removed principals while keeping the endpoint role-neutral."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        _, error = _load_active_user()
        if error:
            return error
        return fn(*args, **kwargs)

    return wrapper


# =====================================================================
# HELPER: Build User Response
# =====================================================================

def build_user_response(user, include_institucion=True):
    """Build user response with roles and institution info"""
    roles = [r.name for r in user.roles]
    primary_role = roles[0] if roles else None
    
    response = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'roles': roles,
        'role': primary_role,
        'is_active': user.is_active
    }
    
    if include_institucion and user.institucion:
        response['institucion'] = {
            'id': user.institucion.id,
            'nombre': user.institucion.nombre,
            'is_active': user.institucion.is_active
        }
    
    return response


# =====================================================================
# AUTHENTICATION ENDPOINTS
# =====================================================================

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5/minute")
def register():
    """
    Register new user as 'estudiante' in specified institution.
    
    Requires:
    - email: str
    - password: str (8+ chars, upper, lower, digit, special)
    - first_name: str
    - last_name: str
    - phone: str
    - institucion_id: str (UUID of target institution)
    """
    if not current_app.config['ALLOW_PUBLIC_REGISTRATION']:
        return jsonify({'message': 'El registro público no está habilitado'}), 403

    data = request.get_json() or {}
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'institucion_id']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    email = normalize_email(data['email'])
    if not is_valid_email(email):
        return jsonify({'message': 'Email inválido'}), 400

    # Validate institution exists and is active
    institucion = Institucion.query.get(data['institucion_id'])
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    if not institucion.is_active:
        return jsonify({'message': 'Institución no activa'}), 403

    can_create, capacity_error = account_creation_allowed(institucion.id)
    if not can_create:
        return jsonify({'message': capacity_error}), 409

    # Validate password strength
    is_valid, error_message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': error_message}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    password_hash = generate_password_hash(data['password'])

    try:
        user = User(
            institucion_id=data['institucion_id'],
            email=email,
            password_hash=password_hash,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email_verified=False,
            is_active=True
        )
        
        db.session.add(user)
        db.session.flush()

        # Assign default role: 'estudiante'
        estudiante_role = Role.query.filter_by(name='estudiante').first()
        if estudiante_role:
            user.roles.append(estudiante_role)
        else:
            db.session.rollback()
            return jsonify({'message': 'Error de configuración: rol de estudiante no encontrado'}), 500

        db.session.commit()

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user_id': str(user.id),
            'institucion_id': data['institucion_id']
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al registrar usuario: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al registrar usuario. Por favor intente nuevamente.'}), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    """
    Authenticate user and return JWT token.
    
    Requires:
    - email: str
    - password: str
    
    Returns:
    - token: JWT access token
    - user: User object with roles and institution info
    """
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email y contraseña requeridos'}), 400

    user = User.query.filter_by(email=normalize_email(data['email'])).first()

    # Prevent user enumeration
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    if not user.is_active:
        return jsonify({'message': 'Usuario inactivo. Contacte al administrador'}), 403
    if user.institucion and not user.institucion.is_active:
        return jsonify({'message': 'Institución no activa. Contacte al administrador'}), 403

    # Verify user has at least one role
    roles = [r.name for r in user.roles]
    if not roles:
        return jsonify({'message': 'Usuario sin rol asignado. Contacte al administrador'}), 403

    user_id = str(user.id)
    access_token = create_access_token(
        identity=user_id,
        additional_claims={
            'institucion_id': user.institucion_id,
            'roles': roles
        }
    )

    return jsonify({
        'token': access_token,
        'user': build_user_response(user)
    }), 200


# =====================================================================
# ADMIN USERS MANAGEMENT
# =====================================================================

@auth_bp.route('/users', methods=['POST'])
@jwt_required()
@super_admin_required
def create_user_admin():
    """
    Super admin: Create new user with custom role assignment.
    """
    data = request.get_json() or {}
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'institucion_id', 'role_names']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos: {", ".join(missing)}'}), 400

    email = normalize_email(data['email'])
    if not is_valid_email(email):
        return jsonify({'message': 'Email inválido'}), 400
    if (
        not isinstance(data['role_names'], list)
        or not data['role_names']
        or not all(isinstance(name, str) and name.strip() for name in data['role_names'])
    ):
        return jsonify({'message': 'role_names debe ser una lista no vacía de nombres'}), 400
    role_names = {name.strip() for name in data['role_names']}

    institucion = Institucion.query.get(data['institucion_id'])
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404

    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    try:
        user = User(
            institucion_id=data['institucion_id'],
            email=email,
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email_verified=False,
            is_active=True
        )
        db.session.add(user)
        db.session.flush()

        roles = Role.query.filter(Role.name.in_(role_names)).all()
        if len(roles) != len(role_names):
            db.session.rollback()
            return jsonify({'message': 'Uno o más roles no son válidos'}), 400
        user.roles.extend(roles)

        db.session.commit()

        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': build_user_response(user)
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear usuario: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al crear usuario'}), 500


@auth_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get the current user, or any user when requested by a super admin."""
    current_user, error = _load_active_user()
    if error or current_user is None:
        return error
    if str(current_user.id) != str(user_id) and 'super_admin' not in {role.name for role in current_user.roles}:
        return jsonify({'message': 'Acceso denegado'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify({'user': build_user_response(user)}), 200


@auth_bp.route('/users/<user_id>/roles', methods=['PATCH'])
@jwt_required()
@super_admin_required
def update_user_roles(user_id):
    """Super admin: Update user's roles"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    data = request.get_json() or {}
    role_names = data.get('role_names')
    if not isinstance(role_names, list) or not role_names or not all(isinstance(name, str) for name in role_names):
        return jsonify({'message': 'role_names debe ser una lista no vacía'}), 400
    normalized_roles = {name.strip() for name in role_names if name.strip()}
    roles = Role.query.filter(Role.name.in_(normalized_roles)).all()
    if not normalized_roles or len(roles) != len(normalized_roles):
        return jsonify({'message': 'Uno o más roles no son válidos'}), 400

    try:
        user.roles = roles

        db.session.commit()

        return jsonify({
            'message': 'Roles actualizados exitosamente',
            'user': build_user_response(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar roles: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar roles'}), 500


@auth_bp.route('/users/<user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@super_admin_required
def toggle_user_status(user_id):
    """Super admin: Toggle user active/inactive"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    try:
        user.is_active = not user.is_active
        db.session.commit()

        action = 'activado' if user.is_active else 'desactivado'
        return jsonify({
            'message': f'Usuario {action} exitosamente',
            'user': build_user_response(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar estado: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al cambiar estado'}), 500


# =====================================================================
# PROFILE ENDPOINTS
# =====================================================================

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@active_user_required
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    
    return jsonify({
        'user': build_user_response(user)
    }), 200


@auth_bp.route('/profile', methods=['PATCH'])
@jwt_required()
@active_user_required
def update_profile():
    """Update current user profile (first_name, last_name, phone)"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    
    data = request.get_json() or {}
    
    try:
        if 'first_name' in data and data['first_name'].strip():
            user.first_name = data['first_name'].strip()
        
        if 'last_name' in data and data['last_name'].strip():
            user.last_name = data['last_name'].strip()
        
        if 'phone' in data and data['phone'].strip():
            user.phone = data['phone'].strip()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil actualizado exitosamente',
            'user': build_user_response(user)
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar perfil: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar perfil'}), 500


@auth_bp.route('/profile/password', methods=['PATCH'])
@jwt_required()
@active_user_required
def update_password():
    """Update current user password"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 401
    
    data = request.get_json() or {}
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Contraseña actual y nueva requeridas'}), 400
    
    # Verify current password
    if not check_password_hash(user.password_hash, data['current_password']):
        return jsonify({'message': 'Contraseña actual incorrecta'}), 401
    
    # Validate new password strength
    is_valid, error_msg = validate_password(data['new_password'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400
    
    try:
        user.password_hash = generate_password_hash(data['new_password'])
        db.session.commit()
        
        return jsonify({
            'message': 'Contraseña actualizada exitosamente'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar contraseña: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al cambiar contraseña'}), 500
