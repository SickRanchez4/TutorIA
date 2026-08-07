"""
Authentication routes supporting multi-tenancy
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app import limiter
from models.user import User
from models import db, Role, Institucion
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

def super_admin_required(fn):
    """Restrict endpoint to super_admin users only"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 401
        
        user_roles = [role.name for role in current_user.roles]
        if 'super_admin' not in user_roles:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de super administrador'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def coordinador_required(fn):
    """Restrict endpoint to coordinador or super_admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 401
        
        user_roles = [role.name for role in current_user.roles]
        if 'coordinador' not in user_roles and 'super_admin' not in user_roles:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de coordinador'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper


def admin_required(fn):
    """LEGACY: Backwards compatibility - accept admin, coordinador, super_admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 401
        
        user_roles = [role.name for role in current_user.roles]
        if 'admin' not in user_roles and 'coordinador' not in user_roles and 'super_admin' not in user_roles:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de administrador'}), 403
        
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
    data = request.get_json() or {}
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'institucion_id']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    # Validate institution exists and is active
    institucion = Institucion.query.get(data['institucion_id'])
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    if not institucion.is_active:
        return jsonify({'message': 'Institución no activa'}), 403

    # Validate password strength
    is_valid, error_message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': error_message}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    password_hash = generate_password_hash(data['password'])

    try:
        user = User(
            institucion_id=data['institucion_id'],
            email=data['email'],
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

    user = User.query.filter_by(email=data['email']).first()

    # Prevent user enumeration
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    if not user.is_active:
        return jsonify({'message': 'Usuario inactivo. Contacte al administrador'}), 403

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

    institucion = Institucion.query.get(data['institucion_id'])
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404

    is_valid, error_msg = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': error_msg}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    try:
        user = User(
            institucion_id=data['institucion_id'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email_verified=False,
            is_active=True
        )
        db.session.add(user)
        db.session.flush()

        for role_name in data['role_names']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)

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
    """Get user by ID"""
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
    if not data.get('role_names'):
        return jsonify({'message': 'role_names requerido'}), 400

    try:
        user.roles = []
        
        for role_name in data['role_names']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)

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
# LEGACY ENDPOINTS (backwards compatibility with 'professor' -> 'coordinador')
# =====================================================================

@auth_bp.route('/professors', methods=['GET'])
@jwt_required()
@admin_required
def get_professors():
    """LEGACY: Get all coordinators"""
    try:
        coordinador_role = Role.query.filter_by(name='coordinador').first()
        if not coordinador_role:
            return jsonify({'message': 'Rol de coordinador no encontrado'}), 404
        
        coordinators = User.query.join(User.roles).filter(Role.id == coordinador_role.id).all()
        
        coordinators_list = [
            {
                'id': str(c.id),
                'first_name': c.first_name,
                'last_name': c.last_name,
                'email': c.email,
                'phone': c.phone,
                'is_active': c.is_active,
                'email_verified': c.email_verified
            }
            for c in coordinators
        ]
        
        return jsonify({
            'professors': coordinators_list,
            'count': len(coordinators_list)
        }), 200
    
    except Exception as e:
        logger.error(f"Error al obtener coordinadores: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al obtener coordinadores'}), 500


@auth_bp.route('/professors/<user_id>/toggle-status', methods=['PATCH'])
@jwt_required()
@admin_required
def toggle_professor_status(user_id):
    """LEGACY: Toggle coordinator status"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        coordinador_role = Role.query.filter_by(name='coordinador').first()
        if not coordinador_role or coordinador_role not in user.roles:
            return jsonify({'message': 'Usuario no es coordinador'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        action = 'activado' if user.is_active else 'desactivado'
        return jsonify({
            'message': f'Usuario {action} exitosamente',
            'professor': {
                'id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al cambiar estado'}), 500


@auth_bp.route('/professors/<user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_professor(user_id):
    """LEGACY: Delete coordinator"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        coordinador_role = Role.query.filter_by(name='coordinador').first()
        if not coordinador_role or coordinador_role not in user.roles:
            return jsonify({'message': 'Usuario no es coordinador'}), 400
        
        user_name = f"{user.first_name} {user.last_name}"
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'Usuario {user_name} eliminado permanentemente',
            'success': True
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al eliminar usuario'}), 500


# =====================================================================
# PROFILE ENDPOINTS
# =====================================================================

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
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
