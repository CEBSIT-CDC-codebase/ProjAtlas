from datetime import datetime
from .. import db


class Session(db.Model):
    __tablename__ = 'Sessions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    # # Foreign key field (using camelCase naming)
    userId = db.Column(db.Integer, db.ForeignKey(
        'Users.id'), nullable=False)

    # Common fields
    createdAt = db.Column(db.DateTime, default=datetime.now)  # Creation time
    updatedAt = db.Column(db.DateTime, default=datetime.now,
                          onupdate=datetime.now)  # Update time
    deleteAt = db.Column(db.DateTime, default=None)  # Soft delete marker

   # Defines the relationship with the User table; SQLAlchemy(ORM) handles the foreign key automatically
    user = db.relationship(
        'User', backref=db.backref('sessions', lazy='dynamic'))

    @classmethod
    def get_active_session(cls, session_id):
        """Model-layer query to get an active session"""
        return cls.query.filter_by(id=session_id, deleteAt=None).first()

    @classmethod
    def validate_create(cls, data):
        """Model-layer create validation"""
        if not data.get('name'):
            raise ValueError("Session name is required")
        if not data.get('userId'):
            raise ValueError("User ID is required")
        return True

    def safe_update(self, data):
        if 'userId' not in data:
            raise ValueError("User ID required")

        if self.userId != data['userId']:
            raise PermissionError("User mismatch")

        for field in ['name']:
            if field in data:
                setattr(self, field, data[field])

        self.updatedAt = datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdAt':self.createdAt.isoformat(),
            'updatedAt':self.updatedAt.isoformat(),
        }

    def __repr__(self):
        return f'<Session {self.name}>'
