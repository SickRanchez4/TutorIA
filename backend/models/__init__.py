from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for many-to-many users <-> roles
user_roles = db.Table(
	'user_roles',
	db.Column('user_id', db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
	db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)

# Import model modules so that classes are registered with SQLAlchemy's metadata
# This allows relationships using string class names to be resolved.

# === Multi-Tenancy & Institutional ===
from .institucion import Institucion, Plan, Suscripcion  # noqa: F401

# === Academic Structure ===
from .academia import Curso, EstudianteCurso  # noqa: F401

# === RAG/AI & Chat ===
from .ia_chat import ConfiguracionIA, RagIngestionJob, SesionChat, MensajeChat  # noqa: F401

# === Agenda, Notifications, Tracking ===
from .agenda_notificaciones import ActividadAgenda, LogNotificacion, ConsumoTokens  # noqa: F401

# === Identity & Access ===
from .user import User  # noqa: F401
from .role import Role  # noqa: F401