from flask import Flask, render_template, request, redirect, session, flash, jsonify
import os
import bcrypt
from supabase import create_client, Client

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    # Safe Supabase setup
    @app.before_request
    def setup_supabase():
        try:
            app.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except:
            app.supabase = None
    
    # HOME - Login page
    @app.route('/')
    def index():
        return redirect('/login')
    
    # TEST Supabase
    @app.route('/test-supabase')
    def test_supabase():
        if not app.supabase:
            return "❌ Supabase ENV vars missing"
        try:
            users = app.supabase.table('users').select('count').execute()
            count = users.data[0]['count'] if users.data else 0
            return f"✅ Supabase Connected! {count} users found"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # LOGIN PAGE + AUTH
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password'].encode('utf-8')
            
            try:
                response = app.supabase.table('users').select('*').eq('email', email).execute()
                user_data = response.data[0] if response.data else None
                
                if user_data and bcrypt.checkpw(password, user_data['password_hash'].encode('utf-8')):
                    session['user_id'] = str(user_data['id'])
                    session['email'] = user_data['email']
                    session['role'] = user_data['role']
                    flash('✅ Login successful!')
                    if user_data['role'] == 'admin':
                        return redirect('/admin')
                    elif user_data['role'] == 'owner':
                        return redirect('/owner-dashboard')
                    elif user_data['role'] == 'center':
                        return redirect('/center-dashboard')
                
                flash('❌ Invalid credentials!')
            except:
                flash('❌ Database error!')
        
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>EV Battery Login</title>
        <style>
        body { font-family: Arial; max-width: 400px; margin: 100px auto; padding: 20px; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 10px; width: 100%; border: none; cursor: pointer; }
        .demo { background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }
        </style>
        </head>
        <body>
            <h2>🔋 EV Battery Platform</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login 🚀</button>
            </form>
            <div class="demo">
                <strong>Demo Logins:</strong><br>
                admin@localhost.com / admin123 → Admin<br>
                owner1@localhost.com / password123 → Owner<br>
                center1@localhost.com / password123 → Center
            </div>
        </body>
        </html>
        '''
    
    # DASHBOARDS
    @app.route('/admin')
    def admin_dashboard():
        if session.get('role') != 'admin':
            return redirect('/login')
        try:
            centers = app.supabase.table('centers').eq('status', 'pending').execute().data or []
            return f'<h1>Admin Dashboard</h1><p>Pending centers: {len(centers)}</p><a href="/logout">Logout</a>'
        except:
            return '<h1>Admin Dashboard</h1><p>Database error</p><a href="/logout">Logout</a>'
    
    @app.route('/owner-dashboard')
    def owner_dashboard():
        if session.get('role') != 'owner':
            return redirect('/login')
        return '<h1>Owner Dashboard</h1><form method="POST" action="/add-battery"><input name="battery_id" placeholder="Battery ID"><button>Add Battery</button></form><a href="/logout">Logout</a>'
    
    @app.route('/center-dashboard')
    def center_dashboard():
        if session.get('role') != 'center':
            return redirect('/login')
        return '<h1>Center Dashboard</h1><p>Process pickup requests here</p><a href="/logout">Logout</a>'
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('✅ Logged out!')
        return redirect('/login')
    
    return app
