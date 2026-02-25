from flask import Flask
from flask_login import LoginManager
from .config import Config
from supabase import create_client, Client
import os

db = None  # Keep for compatibility
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Global Supabase client
    @app.before_request
    def setup_supabase():
        app.supabase = Config.get_supabase()
    
    # Flask-Login
    login_manager.init_app(app)
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    return app
