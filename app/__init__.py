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
    
    @app.route('/')
    def index():
        return "✅ EV Battery Platform LIVE!"
    
    @app.route('/test-supabase')
    def test_supabase():
        try:
            users = app.supabase.table('users').select('count').execute()
            return f"✅ Supabase Connected! {len(users.data)} users"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    return app
