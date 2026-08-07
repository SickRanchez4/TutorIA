"""Module 2: Academic Structure Models (Curso-centric)."""
from datetime import datetime, timezone
import uuid

from models import db


class Curso(db.Model):
    """Institution course catalog entry."""
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    institucion_id = db.Column(db.String(36), db.ForeignKey('instituciones.id', ondelete='CASCADE'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    codigo = db.Column(db.String(50), nullable=True)
    descripcion = db.Column(db.String(1000), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'institucion_id': self.institucion_id,
            'nombre': self.nombre,
            'codigo': self.codigo,
            'descripcion': self.descripcion,
            'is_active': self.is_active,
        }


class EstudianteCurso(db.Model):
    """Student enrollment in a course - direct course assignment (no groups)."""
    __tablename__ = 'estudiante_cursos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='NO ACTION'), nullable=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='NO ACTION'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    
    # Unique constraint: one student per course
    __table_args__ = (db.UniqueConstraint('user_id', 'curso_id', name='uq_estudiante_curso'),)
    
    # Relationships
    user = db.relationship('User', backref='estudiante_cursos', foreign_keys=[user_id])
    curso = db.relationship('Curso', backref='estudiantes', foreign_keys=[curso_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'curso_id': self.curso_id,
            'is_active': self.is_active,
            'fecha_inscripcion': self.fecha_inscripcion.isoformat()
        }
