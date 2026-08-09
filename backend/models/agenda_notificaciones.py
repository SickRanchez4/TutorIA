"""
Module 3 & 4: Agenda, Notifications, and Token Tracking Models
- ActividadesAgenda, LogNotificaciones, ConsumoTokens
"""
from models import db
from datetime import datetime, timezone
import uuid


class ActividadAgenda(db.Model):
    """Academic deadlines and events"""
    __tablename__ = 'actividades_agenda'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(1000), nullable=True)
    tipo = db.Column(db.String(50), nullable=False)  # examen, tarea, proyecto
    fecha_limite = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(50), default='vigente')  # vigente, completada, cancelada
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relationships
    logs_notificaciones = db.relationship('LogNotificacion', backref='actividad', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'curso_id': self.curso_id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'fecha_limite': self.fecha_limite.isoformat(),
            'estado': self.estado,
            'created_at': self.created_at.isoformat()
        }


class LogNotificacion(db.Model):
    """Notification delivery audit log"""
    __tablename__ = 'log_notificaciones'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='NO ACTION'), nullable=False)
    actividad_agenda_id = db.Column(db.String(36), db.ForeignKey('actividades_agenda.id', ondelete='NO ACTION'), nullable=False)
    tipo_notificacion = db.Column(db.String(50), nullable=False)  # recordatorio_7_dias, alerta_24_horas
    estado_envio = db.Column(db.String(50), nullable=False)  # enviado, fallido
    fecha_ejecucion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relationships
    user = db.relationship('User', backref='logs_notificaciones', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'actividad_agenda_id': self.actividad_agenda_id,
            'tipo_notificacion': self.tipo_notificacion,
            'estado_envio': self.estado_envio,
            'fecha_ejecucion': self.fecha_ejecucion.isoformat()
        }


class PrecioModeloIA(db.Model):
    """Versioned USD token pricing for an AI provider model."""
    __tablename__ = 'precios_modelo_ia'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proveedor = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    precio_prompt_por_millon_usd = db.Column(db.Numeric(12, 6), nullable=False)
    precio_completion_por_millon_usd = db.Column(db.Numeric(12, 6), nullable=False)
    vigente_desde = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    vigente_hasta = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class ConsumoTokens(db.Model):
    """Token consumption audit trail + cost tracking"""
    __tablename__ = 'consumo_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tipo_operacion = db.Column(db.String(50), nullable=False)  # chat_rag, resumen_sintetico, practicar
    prompt_tokens = db.Column(db.Integer, nullable=False)
    completion_tokens = db.Column(db.Integer, nullable=False)
    costo_estimado_usd = db.Column(db.Numeric(10, 6), nullable=False)
    precio_modelo_ia_id = db.Column(db.Integer, db.ForeignKey('precios_modelo_ia.id', ondelete='SET NULL'), nullable=True)
    proveedor_modelo = db.Column(db.String(50), nullable=True)
    modelo_ia = db.Column(db.String(100), nullable=True)
    precio_prompt_por_millon_usd = db.Column(db.Numeric(12, 6), nullable=True)
    precio_completion_por_millon_usd = db.Column(db.Numeric(12, 6), nullable=True)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relationships
    user = db.relationship('User', backref='consumo_tokens', foreign_keys=[user_id])
    precio_modelo = db.relationship('PrecioModeloIA', backref='consumos_tokens')
    
    @property
    def total_tokens(self):
        """Total tokens used in this operation"""
        return self.prompt_tokens + self.completion_tokens
    
    def to_dict(self):
        return {
            'id': self.id,
            'institucion_id': self.institucion_id,
            'curso_id': self.curso_id,
            'user_id': self.user_id,
            'tipo_operacion': self.tipo_operacion,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'costo_estimado_usd': float(self.costo_estimado_usd),
            'proveedor_modelo': self.proveedor_modelo,
            'modelo_ia': self.modelo_ia,
            'fecha': self.fecha.isoformat()
        }
