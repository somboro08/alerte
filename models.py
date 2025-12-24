from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    signalements = db.relationship('Signalement', backref='author', lazy='dynamic')
    messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Signalement(db.Model):
    __tablename__ = 'signalements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Type de signalement
    type = db.Column(db.String(20), nullable=False)  # 'lost', 'missing', 'stolen'
    category = db.Column(db.String(50))  # Électronique, Documents, Bijoux, etc.
    
    # Informations principales
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Localisation
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Date et heure
    incident_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Contact et récompense
    contact_info = db.Column(db.String(200))
    reward = db.Column(db.String(100))
    
    # Statut
    status = db.Column(db.String(20), default='active')  # active, found, closed
    is_urgent = db.Column(db.Boolean, default=False)
    
    # Images
    image_url = db.Column(db.String(500))
    
    # Métadonnées
    view_count = db.Column(db.Integer, default=0)
    match_count = db.Column(db.Integer, default=0)
    
    # Relations
    messages = db.relationship('Message', backref='signalement', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'incident_date': self.incident_date.isoformat() if self.incident_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'contact_info': self.contact_info,
            'reward': self.reward,
            'status': self.status,
            'is_urgent': self.is_urgent,
            'image_url': self.image_url,
            'view_count': self.view_count,
            'match_count': self.match_count,
            'author': self.author.to_dict() if self.author else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    signalement_id = db.Column(db.Integer, db.ForeignKey('signalements.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation pour le receiver
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Match(db.Model):
    __tablename__ = 'matches'
    
    id = db.Column(db.Integer, primary_key=True)
    signalement1_id = db.Column(db.Integer, db.ForeignKey('signalements.id'), nullable=False)
    signalement2_id = db.Column(db.Integer, db.ForeignKey('signalements.id'), nullable=False)
    similarity_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    signalement1 = db.relationship('Signalement', foreign_keys=[signalement1_id])
    signalement2 = db.relationship('Signalement', foreign_keys=[signalement2_id])

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    type = db.Column(db.String(50), nullable=False)  # match, message, status_change
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Lien vers l'élément concerné
    related_id = db.Column(db.Integer)
    related_type = db.Column(db.String(50))
    
    user = db.relationship('User', backref='notifications')