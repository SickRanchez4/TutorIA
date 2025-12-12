from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from models import db, Role
import re


auth_bp = Blueprint('auth', __name__)


def validate_password(password):
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    return True, ""


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    required_fields = ['email', 'password', 'first_name', 'last_name', 'phone']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos requeridos: {", ".join(missing)}'}), 400

    # Validate password strength
    is_valid, error_message = validate_password(data['password'])
    if not is_valid:
        return jsonify({'message': error_message}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    # Hash password
    password_hash = generate_password_hash(data['password'])

    try:
        # Create user - SQLAlchemy will handle UUID generation via DB default
        user = User(
            email=data['email'],
            password_hash=password_hash,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email_verified=False,
            is_active=True
        )

        # Add user to session first
        db.session.add(user)
        
        # Flush to generate the user ID before adding roles
        db.session.flush()

        # Assign default role (professor = id 2)
        # Only professors can self-register; admins are created manually
        professor_role = Role.query.get(2)
        if professor_role:
            user.roles.append(professor_role)
        else:
            # This should never happen if DB is properly seeded
            db.session.rollback()
            return jsonify({'message': 'Error de configuración: rol de profesor no encontrado'}), 500

        # Commit the transaction
        db.session.commit()

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user_id': str(user.id)
        }), 201
    
    except Exception as e:
        db.session.rollback()
        # Log the error for debugging
        print(f"Error al registrar usuario: {str(e)}")
        return jsonify({'message': 'Error al registrar usuario. Por favor intente nuevamente.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email y contraseña requeridos'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'Credenciales inválidas'}), 401

    if not user.is_active:
        return jsonify({'message': 'Usuario inactivo. Contacte al administrador'}), 403

    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Create access token with user ID as identity
    user_id = str(user.id)
    access_token = create_access_token(identity=user_id)

    # Get user roles
    roles = [r.name for r in user.roles]
    
    # Primary role for routing (first role in list, or None if no roles)
    primary_role = roles[0] if roles else None
    
    if not primary_role:
        return jsonify({'message': 'Usuario sin rol asignado. Contacte al administrador'}), 403

    return jsonify({
        'token': access_token,
        'user': {
            'id': user_id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.full_name,
            'roles': roles,
            'role': primary_role,
            'is_active': user.is_active
        }
    }), 200


@auth_bp.route('/professors', methods=['GET'])
@jwt_required()
def get_professors():
    """
    Get all users with professor role.
    Requires authentication. Should be restricted to admin users.
    """
    try:
        # Get professor role
        professor_role = Role.query.filter_by(name='professor').first()
        
        if not professor_role:
            return jsonify({'message': 'Rol de profesor no encontrado'}), 404
        
        # Get all users with professor role
        professors = User.query.join(User.roles).filter(Role.id == professor_role.id).all()
        
        # Format response
        professors_list = [
            {
                'id': str(prof.id),
                'first_name': prof.first_name,
                'last_name': prof.last_name,
                'email': prof.email,
                'phone': prof.phone,
                'is_active': prof.is_active,
                'email_verified': prof.email_verified
            }
            for prof in professors
        ]
        
        return jsonify({
            'professors': professors_list,
            'count': len(professors_list)
        }), 200
    
    except Exception as e:
        print(f"Error al obtener profesores: {str(e)}")
        return jsonify({'message': 'Error al obtener profesores'}), 500


@auth_bp.route('/professors/<professor_id>/toggle-status', methods=['PATCH'])
@jwt_required()
def toggle_professor_status(professor_id):
    """
    Toggle the active status of a professor.
    Requires authentication. Should be restricted to admin users.
    """
    try:
        # Find the professor
        professor = User.query.get(professor_id)
        
        if not professor:
            return jsonify({'message': 'Profesor no encontrado'}), 404
        
        # Verify user has professor role
        professor_role = Role.query.filter_by(name='professor').first()
        if not professor_role or professor_role not in professor.roles:
            return jsonify({'message': 'Usuario no es un profesor'}), 400
        
        # Toggle the is_active status
        professor.is_active = not professor.is_active
        db.session.commit()
        
        action = 'activado' if professor.is_active else 'desactivado'
        
        return jsonify({
            'message': f'Profesor {action} exitosamente',
            'professor': {
                'id': str(professor.id),
                'first_name': professor.first_name,
                'last_name': professor.last_name,
                'is_active': professor.is_active
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error al cambiar estado del profesor: {str(e)}")
        return jsonify({'message': 'Error al cambiar estado del profesor'}), 500
