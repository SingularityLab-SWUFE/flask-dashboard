from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # hashed password
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    # generated once registered
    access_token = db.Column(db.String(100), nullable=False, default=str(uuid.uuid4()))
    role = db.Column(db.String(50), nullable=False, default='user')
    
    submissions = db.relationship(
        'Submission',
        back_populates='user',
        lazy='dynamic'
    )
    
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'role': self.role
        }


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    max_score = db.Column(db.Integer, nullable=False, default=100)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    deadline = db.Column(db.DateTime, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    
    submissions = db.relationship(
        'Submission',
        back_populates='assignment',
        lazy='dynamic'
    )
    
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_score': self.max_score,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'deadline': self.deadline.strftime('%Y-%m-%d %H:%M:%S'),
            'is_published': self.is_published
        }


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey(
        'assignments.id'), nullable=False)
    
    content = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)

    user = db.relationship(
        'User',
        back_populates='submissions',
        foreign_keys='Submission.user_id'
    )
    assignment = db.relationship(
        'Assignment',
        back_populates='submissions',
        foreign_keys='Submission.assignment_id'
    )

    def to_json(self):
        return {
            'id': self.id,
            'username': self.user.username,
            'assignment_name': self.assignment.name,
            'score': self.score,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }