from flask import Flask, request, redirect, session
import os
import traceback

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        try:
            return f"<h1>✅ Flask Working!</h1><a href='/debug'>Debug Info</a>"
        except Exception as e:
            return f"ERROR in /: {str(e)}<br>{traceback.format_exc()}"
    
    @app.route('/debug')
    def debug():
        info = {
            'cwd': os.getcwd(),
            'files': os.listdir('app/templates') if os.path.exists('app/templates') else 'MISSING',
            'env_vars': ['SUPABASE_URL', 'SUPABASE_ANON_KEY'] if os.getenv('SUPABASE_URL') else 'MISSING'
        }
        return f"<pre>{info}</pre>"
    
    return app
