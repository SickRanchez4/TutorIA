from models import db, user_roles
from sqlalchemy import text

class User(db.Model):
    __tablename__ = 'users'

    # DB uses UNIQUEIDENTIFIER / NEWID() — represent as string here
    # server_default indicates the DB will generate the UUID
    id = db.Column(db.String(36), primary_key=True, server_default=text('NEWID()'))
    email = db.Column(db.String(255), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # many-to-many relationship with Role
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.email}>'