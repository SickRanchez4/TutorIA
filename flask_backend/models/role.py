from models import db, user_roles


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    users = db.relationship('User', secondary=user_roles, back_populates='roles')

    def __repr__(self):
        return f'<Role {self.name}>'
