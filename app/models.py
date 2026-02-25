from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from supabase import Client

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def get_by_email(self, email):
        return self.supabase.table('users').select('*').eq('email', email).execute()
    
    def create(self, email, password, role):
        return self.supabase.table('users').insert({
            'email': email, 'password': password, 'role': role, 'approved': True
        }).execute()


class Battery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    battery_id = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    usage_years = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(10), default='Pending')
    status = db.Column(db.String(20), default='Active')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ✅ Check if pickup requested
    @property
    def has_request(self):
        return self.requests and len(self.requests) > 0


class PickupRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    battery_id = db.Column(db.Integer, db.ForeignKey('battery.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    battery = db.relationship('Battery', backref='requests')
    center = db.relationship('User', foreign_keys=[processed_by])
