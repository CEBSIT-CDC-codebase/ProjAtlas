from datetime import datetime
from .. import db


class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique required field
    name = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(255), nullable=True)
    department = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), nullable=True)

    # Timestamp fields
    createdAt = db.Column(db.DateTime, default=datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.now,
                          onupdate=datetime.now)
    deleteAt = db.Column(db.DateTime, default=None)

    @classmethod
    def get_active_user(cls, user_id):
        """Model-layer query to get an active user"""
        return cls.query.filter_by(id=user_id, deleteAt=None).first()

    @classmethod
    def validate_email(cls, email):
        """Simple email format check"""
        if '@' not in email:
            raise ValueError("邮箱格式无效")

    def safe_update(self, data):
        """Safe update method (only updates fields that are present)"""
        if 'email' in data:
            self.validate_email(data['email'])
            self.email = data['email']

        for field in ['name', 'title', 'department', 'role']:
            if field in data:
                setattr(self, field, data[field])

        self.updatedAt = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'title': self.title,
            'department': self.department,
            'role': self.role,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat()
        }

    def __repr__(self):
        return f'<User {self.email}>'
