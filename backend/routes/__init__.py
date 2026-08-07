"""
Routes package - Register all blueprint modules
"""
from .auth_multi_tenant import auth_bp
from .instituciones import instituciones_bp
from .coordinador import coordinador_bp
from .estudiante import estudiante_bp

__all__ = ['auth_bp', 'instituciones_bp', 'coordinador_bp', 'estudiante_bp']
