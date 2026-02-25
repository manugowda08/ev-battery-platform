from flask import Flask, session, request
import os
from supabase import create_client, Client

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    # Supabase client
    @app.before_request
    def setup_supabase():
        app.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
    
    # Test route
    @app.route('/')
    def index():
        return "✅ EV Battery Platform LIVE!"
    
    @app.route('/test')
    def test():
        try:
            users = app.supabase.table('users').select('count').execute()
            return f"✅ Supabase OK! {len(users.data)} users"
        except:
            return "❌ Supabase config missing"
    
    return app
