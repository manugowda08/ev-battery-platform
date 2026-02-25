from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    # Safe Supabase client setup
    @app.before_request
    def setup_supabase():
        try:
            from supabase import create_client
            app.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except Exception as e:
            print(f"Supabase setup error: {e}")
            app.supabase = None
    
    @app.route('/')
    def index():
        return "✅ EV Battery Platform LIVE!"
    
    @app.route('/test-supabase')
    def test_supabase():
        if not hasattr(app, 'supabase') or app.supabase is None:
            return "❌ Supabase not configured"
        try:
            users = app.supabase.table('users').select('count').execute()
            count = users.data[0]['count'] if users.data else 0
            return f"✅ Supabase Connected! {count} users found"
        except Exception as e:
            return f"❌ Supabase Error: {str(e)}"
    
    # Import blueprints AFTER app creation
    from app.auth import auth_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
