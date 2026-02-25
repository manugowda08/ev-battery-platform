from flask import Flask
import os
from supabase import create_client, Client

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    # Global Supabase client - TRY/EXCEPT to avoid proxy error
    @app.before_request
    def setup_supabase():
        try:
            app.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except:
            app.supabase = None
    
    # Basic routes
    @app.route('/')
    def index():
        return "✅ EV Battery Platform LIVE!"
    
    @app.route('/test-supabase')
    def test_supabase():
        if not app.supabase:
            return "❌ Supabase not configured - Check ENV vars"
        try:
            users = app.supabase.table('users').select('count').execute()
            count = users.data[0]['count'] if users.data else 0
            return f"✅ Supabase Connected! {count} users"
        except Exception as e:
            return f"❌ Supabase Error: {str(e)}"
    
    # Register blueprints AFTER routes
    from app.auth import auth_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
