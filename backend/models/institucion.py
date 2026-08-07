"""
Module 1: Multi-Tenancy & Institutional Models
- Instituciones, Suscripciones.quiero Planes
"""
from models import db
from datetime import datetime, timezone
import uuid


class Plan(db.Model):
    """Service tiers for subscriptions. Nullable limits = unlimited."""
    __tablename__ = 'planes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    max_cuentas = db.Column(db.Integer, nullable=True)  # Total accounts limit (coordinators + students)
    max_almacenamiento_gb = db.Column(db.Numeric(5, 2), nullable=True)  # NULL = unlimited
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relationships
    suscripciones = db.relationship('Suscripcion', backref='plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'max_cuentas': self.max_cuentas,
            'max_almacenamiento_gb': float(self.max_almacenamiento_gb) if self.max_almacenamiento_gb is not None else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Institucion(db.Model):
    """Tenant organizations in multi-tenancy system"""
    __tablename__ = 'instituciones'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    dominio_permitido = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))



    # Relationships - ALL CASCADE for data integrity on institution deletion
    suscripciones = db.relationship('Suscripcion', backref='institucion', cascade='all, delete-orphan', uselist=False)
    users = db.relationship('User', backref='institucion', lazy='dynamic', cascade='all, delete-orphan')
    consumo_tokens = db.relationship('ConsumoTokens', backref='institucion', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'dominio_permitido': self.dominio_permitido,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Suscripcion(db.Model):
    """Subscription management with token quotas"""
    __tablename__ = 'suscripciones'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False, unique=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    limite_tokens_mensual = db.Column(db.BigInteger, nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    def to_dict(self):
        return {
            'id': self.id,
            'institucion_id': self.institucion_id,
            'plan_id': self.plan_id,
            'plan_nombre': self.plan.nombre if self.plan else None,
            'limite_tokens_mensual': self.limite_tokens_mensual,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_fin': self.fecha_fin.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
