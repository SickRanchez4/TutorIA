from models import db, user_roles


class Role(db.Model):
    """
    User roles in multi-tenancy system:
    - super_admin: Global platform administrator
    - coordinador: Institutional coordinator (manages courses, RAG, etc.)
    - estudiante: Student user
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    users = db.relationship('User', secondary=user_roles, back_populates='roles')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f'<Role {self.name}>'
