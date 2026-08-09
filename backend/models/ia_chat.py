"""
Module 2 & 3: RAG/AI and Chat Models
- ConfiguracionIA, SesionesChat, MensajesChat
"""
from models import db
from datetime import datetime, timezone
import json
import uuid


class ConfiguracionIA(db.Model):
    """LLM behavior configuration per course"""
    __tablename__ = 'configuracion_ia'
    
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), primary_key=True)
    system_prompt = db.Column(db.String(2000), nullable=False)
    temperatura = db.Column(db.Numeric(3, 2), default=0.2, nullable=False)
    modos_permitidos = db.Column(db.String(200), default='chat,practicar,recursos', nullable=False)  # CSV: chat, practicar, recursos
    extender_conocimiento = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    def to_dict(self):
        return {
            'curso_id': self.curso_id,
            'system_prompt': self.system_prompt,
            'temperatura': float(self.temperatura),
            'modos_permitidos': self.modos_permitidos.split(','),
            'extender_conocimiento': self.extender_conocimiento,
            'updated_at': self.updated_at.isoformat()
        }


class RagIngestionJob(db.Model):
    """Auditable RAG ingestion request and its n8n processing outcome."""
    __tablename__ = 'rag_ingestion_jobs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False, index=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='NO ACTION'), nullable=False, index=True)
    coordinador_id = db.Column(db.String(36), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='queued', index=True)
    intento = db.Column(db.Integer, nullable=False, default=1)
    documentos_json = db.Column(db.Text, nullable=False, default='[]')
    chunks_indexados = db.Column(db.Integer, nullable=False, default=0)
    archivos_procesados = db.Column(db.Integer, nullable=False, default=0)
    respuesta_procesador_json = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.String(1000), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    curso = db.relationship('Curso', backref=db.backref('rag_ingestion_jobs', lazy='dynamic', cascade='all, delete-orphan'))

    def documents(self):
        try:
            return json.loads(self.documentos_json or '[]')
        except (TypeError, ValueError):
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'curso_id': self.curso_id,
            'estado': self.estado,
            'intento': self.intento,
            'documentos': self.documents(),
            'chunks_indexados': self.chunks_indexados,
            'archivos_procesados': self.archivos_procesados,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


class SesionChat(db.Model):
    """Chat thread/conversation"""
    __tablename__ = 'sesiones_chat'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), nullable=False)
    titulo = db.Column(db.String(200), default='Nueva Conversación')
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Relationships
    mensajes = db.relationship('MensajeChat', backref='sesion', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref='sesiones_chat', foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'curso_id': self.curso_id,
            'titulo': self.titulo,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }



class MensajeChat(db.Model):
    """Individual message in chat thread with RAG citations"""
    __tablename__ = 'mensajes_chat'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sesion_chat_id = db.Column(db.String(36), db.ForeignKey('sesiones_chat.id', ondelete='CASCADE'), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    contenido = db.Column(db.String(3000), nullable=False)
    citas_contexto_json = db.Column(db.String(1000), nullable=True)  # Array of {archivo, pagina}
    imagen_nombre = db.Column(db.String(255), nullable=True)
    tipo_interaccion = db.Column(db.String(50), default='consulta', nullable=False)  # consulta, practicar, recurso_sintetico
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    def to_dict(self):
        citas = None
        if self.citas_contexto_json:
            try:
                citas = json.loads(self.citas_contexto_json)
            except:
                citas = []
        
        return {
            'id': self.id,
            'sesion_chat_id': self.sesion_chat_id,
            'rol': self.rol,
            'contenido': self.contenido,
            'citas_contexto': citas,
            'image_name': self.imagen_nombre,
            'tipo_interaccion': self.tipo_interaccion,
            'created_at': self.created_at.isoformat()
        }
