from flask import Flask
import os
from supabase import create_client, Client

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    # Global Supabase client
    @app.before_request
    def setup_supabase():
        app.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
    
    # Register blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
