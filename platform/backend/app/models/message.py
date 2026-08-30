from datetime import datetime
from .. import db
import json

JSON_LIST_FIELDS = {'neurons', 'regions', 'matrix'}

class Message(db.Model):
    __tablename__ = 'Messages'

    id = db.Column(db.Integer, primary_key=True)
    toolCalls = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    task = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(40), nullable=False)
    neurons = db.Column(db.Text, nullable=True)
    regions = db.Column(db.Text, nullable=True)
    matrix = db.Column(db.Text, nullable=True)

    # # Foreign key field (using camelCase naming)
    sessionId = db.Column(db.Integer, db.ForeignKey(
        'Sessions.id'), nullable=False)  # Foreign key referencing the Session table

    # Common fields
    createdAt = db.Column(db.DateTime, default=datetime.now)  # Creation time
    updatedAt = db.Column(db.DateTime, default=datetime.now,
                          onupdate=datetime.now)  # Update time
    deleteAt = db.Column(db.DateTime, default=None)  # Soft delete marker

    session = db.relationship(
        'Session', backref=db.backref('messages', lazy='dynamic'))

    @classmethod
    def get_active_message(cls, message_id):
        """Model-layer query to get an active message"""
        return cls.query.filter_by(id=message_id, deleteAt=None).first()

    @classmethod
    def validate_create(cls, data):
        """Model-layer create validation"""
        if not data.get('sessionId'):
            raise ValueError("sessionId is required")
        if not data.get('role'):
            raise ValueError("role is required")
        return True

    def safe_update(self, data):
        if 'sessionId' not in data:
            raise ValueError("Session ID required")

        if self.sessionId != data['sessionId']:
            raise PermissionError("Session mismatch")

        for field in ['content', 'toolCalls', 'task', 'neurons', 'regions', 'matrix', 'role']:
            if field in data:
                if field in JSON_LIST_FIELDS:
                    setattr(self, field, json.dumps(data[field]))
                else:
                    setattr(self, field, data[field])

        self.updatedAt = datetime.now()

    def to_dict(self):

        return {
            'id': self.id,
            'content': self.content,
            'task': self.task,
            'neurons': self.neurons,
            'matrix': self.matrix,
            'toolCalls': self.toolCalls,
            'regions': self.regions,
            'role': self.role,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat(),
        }

    def __repr__(self):
        return f'<Message {self.content}>'
