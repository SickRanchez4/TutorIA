from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for many-to-many users <-> roles
user_roles = db.Table(
	'user_roles',
	db.Column('user_id', db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
	db.Column('role_id', db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
)

# Import model modules so that classes are registered with SQLAlchemy's metadata
# This allows relationships using string class names (e.g. 'Role') to be resolved.
from .user import User  # noqa: F401
from .role import Role  # noqa: F401