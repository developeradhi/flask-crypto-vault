from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True) # Optional if registered via old method, but needed for password reset
    password_hash = db.Column(db.String(256), nullable=True) # Nullable for OAuth users
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    
    # Advanced Security: Per-user encryption keys stored securely
    aes_key = db.Column(db.String(100), nullable=False)
    rsa_public_key = db.Column(db.Text, nullable=False)
    rsa_private_key = db.Column(db.Text, nullable=False)
    
    # 2FA
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    action = db.Column(db.String(50)) # e.g. "LOGIN_SUCCESS", "LOGIN_FAILED"

class EphemeralMessage(db.Model):
    id = db.Column(db.String(36), primary_key=True) # UUID
    encrypted_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
