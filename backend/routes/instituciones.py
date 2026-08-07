"""
Super Admin Routes: Institution & Plan Management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Institucion, Plan, Suscripcion, User, Role
from routes.auth_multi_tenant import super_admin_required
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
import logging
import uuid

instituciones_bp = Blueprint('instituciones', __name__)
logger = logging.getLogger(__name__)


def _get_coordinador_role():
    return Role.query.filter_by(name='coordinador').first()


def _get_suscripcion_activa(institucion_id):
    return Suscripcion.query.filter_by(institucion_id=institucion_id, is_active=True).first()


# =====================================================================
# INSTITUTIONAL MANAGEMENT
# =====================================================================

@instituciones_bp.route('/instituciones', methods=['POST'])
@jwt_required()
@super_admin_required
def create_institucion():
    """
    Create a new institution (tenant).    
    Payload:
    - nombre: str
    - dominio_permitido: str (optional)
    - is_active: bool (optional, default: True)
    """
    data = request.get_json() or {}
    
    if not data.get('nombre'):
        return jsonify({'message': 'nombre es requerido'}), 400
    
    try:
        institucion = Institucion(
            nombre=data['nombre'],
            dominio_permitido=data.get('dominio_permitido'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(institucion)
        db.session.commit()
        
        return jsonify({
            'message': 'Institución creada exitosamente',
            'institucion': institucion.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear institución: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al crear institución'}), 500


@instituciones_bp.route('/instituciones', methods=['GET'])
@jwt_required()
@super_admin_required
def list_instituciones():
    """List all institutions with optional filtering by is_active status"""
    is_active = request.args.get('is_active')
    
    query = Institucion.query
    
    # Filter by is_active if specified (true, false, True, False, 1, 0)
    if is_active is not None:
        is_active_bool = is_active.lower() in ('true', '1', 'yes')
        query = query.filter_by(is_active=is_active_bool)
    
    instituciones = query.all()
    
    return jsonify({
        'instituciones': [i.to_dict() for i in instituciones],
        'total': len(instituciones)
    }), 200


@instituciones_bp.route('/instituciones/<institucion_id>', methods=['GET'])
@jwt_required()
@super_admin_required
def get_institucion(institucion_id):
    """Get institution details"""
    institucion = Institucion.query.get(institucion_id)
    
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    
    response = institucion.to_dict()
    
    # Include subscription info if exists
    suscripcion = Suscripcion.query.filter_by(institucion_id=institucion_id).first()
    if suscripcion:
        response['suscripcion'] = suscripcion.to_dict()
    
    return jsonify({'institucion': response}), 200


@instituciones_bp.route('/instituciones/<institucion_id>', methods=['PATCH'])
@jwt_required()
@super_admin_required
def update_institucion(institucion_id):
    """Update institution details"""
    institucion = Institucion.query.get(institucion_id)
    
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    
    data = request.get_json() or {}
    
    try:
        if 'nombre' in data:
            institucion.nombre = data['nombre']
        
        if 'dominio_permitido' in data:
            institucion.dominio_permitido = data['dominio_permitido']
        
        if 'is_active' in data:
            if not isinstance(data['is_active'], bool):
                return jsonify({'message': 'is_active debe ser boolean'}), 400
            institucion.is_active = data['is_active']
        
        institucion.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()
        
        return jsonify({
            'message': 'Institución actualizada exitosamente',
            'institucion': institucion.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar institución: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar institución'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>', methods=['DELETE'])
@jwt_required()
@super_admin_required
def delete_institucion(institucion_id):
    """Delete institution (tenant) and all related data."""
    institucion = Institucion.query.get(institucion_id)

    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404

    try:
        nombre = institucion.nombre
        db.session.delete(institucion)
        db.session.commit()

        return jsonify({
            'message': f'Institución {nombre} eliminada exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar institución: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al eliminar institución'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/toggle-active', methods=['PATCH'])
@jwt_required()
@super_admin_required
def toggle_institucion_active(institucion_id):
    """Toggle institution active/inactive status"""
    institucion = Institucion.query.get(institucion_id)
    
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    
    try:
        institucion.is_active = not institucion.is_active
        institucion.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()
        
        status_text = 'activada' if institucion.is_active else 'desactivada'
        return jsonify({
            'message': f'Institución {status_text} exitosamente',
            'institucion': institucion.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar estado: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al cambiar estado'}), 500


# =====================================================================
# CU-02: PLAN & SUBSCRIPTION MANAGEMENT
# =====================================================================

@instituciones_bp.route('/planes', methods=['GET'])
@jwt_required()
@super_admin_required
def list_planes():
    """List all subscription plans"""
    is_active = request.args.get('is_active', type=lambda x: x.lower() == 'true')
    
    query = Plan.query
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    planes = query.all()
    
    return jsonify({
        'planes': [p.to_dict() for p in planes],
        'total': len(planes)
    }), 200


@instituciones_bp.route('/planes', methods=['POST'])
@jwt_required()
@super_admin_required
def create_plan():
    """
    Create subscription plan
    
    CU-02: Asignar Licencias y Planes (Configuración de cuotas)
    """
    data = request.get_json() or {}
    required = ['nombre', 'max_cuentas', 'max_almacenamiento_gb']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos: {", ".join(missing)}'}), 400
    
    try:
        plan = Plan(
            nombre=data['nombre'],
            max_cuentas=data['max_cuentas'],
            max_almacenamiento_gb=data['max_almacenamiento_gb'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'message': 'Plan creado exitosamente',
            'plan': plan.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear plan: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al crear plan'}), 500


@instituciones_bp.route('/planes/<plan_id>', methods=['PATCH'])
@jwt_required()
@super_admin_required
def update_plan(plan_id):
    """Update plan"""
    plan = Plan.query.get(plan_id)
    
    if not plan:
        return jsonify({'message': 'Plan no encontrado'}), 404
    
    data = request.get_json() or {}
    
    try:
        if 'nombre' in data:
            plan.nombre = data['nombre']
        if 'max_cuentas' in data:
            plan.max_cuentas = data['max_cuentas']
        if 'max_almacenamiento_gb' in data:
            plan.max_almacenamiento_gb = data['max_almacenamiento_gb']
        if 'is_active' in data:
            plan.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Plan actualizado exitosamente',
            'plan': plan.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar plan: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar plan'}), 500


@instituciones_bp.route('/planes/<plan_id>', methods=['DELETE'])
@jwt_required()
@super_admin_required
def delete_plan(plan_id):
    """Delete plan if not used by active subscriptions."""
    plan = Plan.query.get(plan_id)

    if not plan:
        return jsonify({'message': 'Plan no encontrado'}), 404

    active_refs = Suscripcion.query.filter_by(plan_id=plan.id, is_active=True).count()
    if active_refs > 0:
        return jsonify({'message': 'No se puede eliminar un plan con suscripciones activas'}), 409

    try:
        nombre = plan.nombre
        db.session.delete(plan)
        db.session.commit()

        return jsonify({
            'message': f'Plan {nombre} eliminado exitosamente'
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar plan: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al eliminar plan'}), 500


@instituciones_bp.route('/suscripciones', methods=['GET'])
@jwt_required()
@super_admin_required
def list_suscripciones():
    """List all subscriptions with optional active filter."""
    is_active = request.args.get('is_active', type=lambda x: x.lower() == 'true')

    query = Suscripcion.query
    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    suscripciones = query.all()

    return jsonify({
        'suscripciones': [s.to_dict() for s in suscripciones],
        'total': len(suscripciones)
    }), 200


@instituciones_bp.route('/instituciones/<institucion_id>/suscripcion', methods=['POST'])
@jwt_required()
@super_admin_required
def create_suscripcion(institucion_id):
    """
    Assign subscription (plan + token quota) to institution
    
    CU-02: Asignar Licencias y Planes (Asignación de cuotas de tokens)
    
    Payload:
    - plan_id: int
    - limite_tokens_mensual: int
    - fecha_inicio: ISO datetime
    - fecha_fin: ISO datetime (optional, default: +1 year)
    """
    institucion = Institucion.query.get(institucion_id)
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    
    # Check if already has subscription
    if institucion.suscripciones:
        return jsonify({'message': 'Institución ya tiene suscripción activa'}), 409
    
    data = request.get_json() or {}
    required = ['plan_id', 'limite_tokens_mensual']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos: {", ".join(missing)}'}), 400
    
    try:
        plan = Plan.query.get(data['plan_id'])
        if not plan:
            return jsonify({'message': 'Plan no encontrado'}), 404
        
        # Parse dates
        fecha_inicio = datetime.fromisoformat(data.get('fecha_inicio', datetime.now(timezone.utc).replace(tzinfo=None).isoformat()))
        fecha_fin = data.get('fecha_fin')
        
        if fecha_fin:
            fecha_fin = datetime.fromisoformat(fecha_fin)
        else:
            # Default: 1 year from start
            fecha_fin = fecha_inicio + timedelta(days=365)
        
        suscripcion = Suscripcion(
            institucion_id=institucion_id,
            plan_id=data['plan_id'],
            limite_tokens_mensual=data['limite_tokens_mensual'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            is_active=True
        )
        
        db.session.add(suscripcion)
        db.session.commit()
        
        return jsonify({
            'message': 'Suscripción creada exitosamente',
            'suscripcion': suscripcion.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'message': f'Formato de fecha inválido: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear suscripción: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al crear suscripción'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/suscripcion', methods=['GET'])
@jwt_required()
@super_admin_required
def get_suscripcion(institucion_id):
    """Get institution's subscription"""
    institucion = Institucion.query.get(institucion_id)
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404
    
    suscripcion = Suscripcion.query.filter_by(institucion_id=institucion_id).first()
    
    if not suscripcion:
        return jsonify({'message': 'Suscripción no encontrada'}), 404
    
    return jsonify({'suscripcion': suscripcion.to_dict()}), 200


@instituciones_bp.route('/instituciones/<institucion_id>/suscripcion', methods=['PATCH'])
@jwt_required()
@super_admin_required
def update_suscripcion(institucion_id):
    """Update institution's subscription"""
    suscripcion = Suscripcion.query.filter_by(institucion_id=institucion_id).first()
    
    if not suscripcion:
        return jsonify({'message': 'Suscripción no encontrada'}), 404
    
    data = request.get_json() or {}
    
    try:
        if 'plan_id' in data:
            plan = Plan.query.get(data['plan_id'])
            if not plan:
                return jsonify({'message': 'Plan no encontrado'}), 404
            suscripcion.plan_id = data['plan_id']

        if 'limite_tokens_mensual' in data:
            suscripcion.limite_tokens_mensual = data['limite_tokens_mensual']

        if 'fecha_inicio' in data:
            suscripcion.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        
        if 'fecha_fin' in data:
            suscripcion.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
        
        if 'is_active' in data:
            suscripcion.is_active = data['is_active']
        
        suscripcion.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.session.commit()
        
        return jsonify({
            'message': 'Suscripción actualizada exitosamente',
            'suscripcion': suscripcion.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'message': f'Formato inválido: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar suscripción: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar suscripción'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/suscripcion', methods=['DELETE'])
@jwt_required()
@super_admin_required
def delete_suscripcion(institucion_id):
    """Delete institution's subscription."""
    suscripcion = Suscripcion.query.filter_by(institucion_id=institucion_id).first()

    if not suscripcion:
        return jsonify({'message': 'Suscripción no encontrada'}), 404

    try:
        db.session.delete(suscripcion)
        db.session.commit()

        return jsonify({'message': 'Suscripción eliminada exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar suscripción: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al eliminar suscripción'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/coordinadores', methods=['GET'])
@jwt_required()
@super_admin_required
def list_coordinadores_institucion(institucion_id):
    """List coordinators assigned to an institution."""
    institucion = Institucion.query.get(institucion_id)
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404

    coordinador_role = _get_coordinador_role()
    if not coordinador_role:
        return jsonify({'message': 'Rol coordinador no encontrado'}), 404

    coordinadores = (
        User.query
        .join(User.roles)
        .filter(User.institucion_id == institucion_id, Role.id == coordinador_role.id)
        .all()
    )

    return jsonify({
        'coordinadores': [
            {
                'id': c.id,
                'email': c.email,
                'first_name': c.first_name,
                'last_name': c.last_name,
                'full_name': c.full_name,
                'phone': c.phone,
                'is_active': c.is_active
            }
            for c in coordinadores
        ],
        'total': len(coordinadores)
    }), 200


@instituciones_bp.route('/instituciones/<institucion_id>/coordinadores', methods=['POST'])
@jwt_required()
@super_admin_required
def create_coordinador_institucion(institucion_id):
    """Create coordinator under an institution constrained by assigned plan."""
    institucion = Institucion.query.get(institucion_id)
    if not institucion:
        return jsonify({'message': 'Institución no encontrada'}), 404

    suscripcion = _get_suscripcion_activa(institucion_id)
    if not suscripcion or not suscripcion.plan:
        return jsonify({'message': 'La institución no tiene suscripción activa'}), 409

    coordinador_role = _get_coordinador_role()
    if not coordinador_role:
        return jsonify({'message': 'Rol coordinador no encontrado'}), 404

    data = request.get_json() or {}
    required = ['email', 'first_name', 'last_name', 'phone']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'Faltan campos: {", ".join(missing)}'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'El email ya está registrado'}), 409

    # Count all active user accounts in the institution (coordinators + students)
    cuentas_actuales = User.query.filter_by(
        institucion_id=institucion_id, 
        is_active=True
    ).count()
    
    limite_plan = suscripcion.plan.max_cuentas
    if limite_plan is not None and cuentas_actuales >= limite_plan:
        return jsonify({'message': 'Límite de cuentas alcanzado para el plan asignado'}), 409

    try:
        # Use default password "password" for coordinators created from admin panel
        user = User(
            institucion_id=institucion_id,
            email=data['email'],
            password_hash=generate_password_hash('password'),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email_verified=False,
            is_active=True
        )
        user.roles.append(coordinador_role)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'Coordinador creado exitosamente',
            'coordinador': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_active': user.is_active
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear coordinador: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al crear coordinador'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/coordinadores/<user_id>', methods=['PATCH'])
@jwt_required()
@super_admin_required
def update_coordinador_institucion(institucion_id, user_id):
    """Edit coordinator profile and status."""
    coordinador_role = _get_coordinador_role()
    if not coordinador_role:
        return jsonify({'message': 'Rol coordinador no encontrado'}), 404

    user = User.query.get(user_id)
    if not user or user.institucion_id != institucion_id or coordinador_role not in user.roles:
        return jsonify({'message': 'Coordinador no encontrado'}), 404

    data = request.get_json() or {}

    try:
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'message': 'El email ya está registrado'}), 409
            user.email = data['email']
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])

        db.session.commit()

        return jsonify({
            'message': 'Coordinador actualizado exitosamente',
            'coordinador': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_active': user.is_active
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar coordinador: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al actualizar coordinador'}), 500


@instituciones_bp.route('/instituciones/<institucion_id>/coordinadores/<user_id>', methods=['DELETE'])
@jwt_required()
@super_admin_required
def delete_coordinador_institucion(institucion_id, user_id):
    """Remove coordinator from institution."""
    coordinador_role = _get_coordinador_role()
    if not coordinador_role:
        return jsonify({'message': 'Rol coordinador no encontrado'}), 404

    user = User.query.get(user_id)
    if not user or user.institucion_id != institucion_id or coordinador_role not in user.roles:
        return jsonify({'message': 'Coordinador no encontrado'}), 404

    try:
        nombre = user.full_name
        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': f'Coordinador {nombre} eliminado exitosamente'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar coordinador: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error al eliminar coordinador'}), 500
