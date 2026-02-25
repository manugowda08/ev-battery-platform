from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from supabase import create_client, Client
import bcrypt

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    @app.before_request
    def setup_supabase():
        try:
            app.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except:
            app.supabase = None
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
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
    
    # LOGIN - Uses your login.html
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
                    
                    if user_data['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    elif user_data['role'] == 'owner':
                        return redirect(url_for('owner_dashboard'))
                    elif user_data['role'] == 'center':
                        return redirect(url_for('center_dashboard'))
                
                flash('❌ Invalid credentials!')
            except:
                flash('❌ Database error!')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('✅ Logged out!')
        return redirect(url_for('login'))
    
    # DASHBOARDS - Use your existing templates
    @app.route('/admin')
    def admin_dashboard():
        if session.get('role') != 'admin':
            return redirect(url_for('login'))
        try:
            centers = app.supabase.table('centers').eq('status', 'pending').execute().data or []
            return render_template('dashboard_admin.html', pending_centers=centers)
        except:
            return render_template('dashboard_admin.html', pending_centers=[])
    
    @app.route('/owner-dashboard')
    def owner_dashboard():
        if session.get('role') != 'owner':
            return redirect(url_for('login'))
        try:
            batteries = app.supabase.table('batteries').eq('user_id', session['user_id']).execute().data or []
            return render_template('dashboard_owner.html', batteries=batteries)
        except:
            return render_template('dashboard_owner.html', batteries=[])
    
    @app.route('/center-dashboard')
    def center_dashboard():
        if session.get('role') != 'center':
            return redirect(url_for('login'))
        try:
            requests = app.supabase.table('pickup_requests').eq('status', 'Pending').execute().data or []
            return render_template('dashboard_center.html', requests=requests)
        except:
            return render_template('dashboard_center.html', requests=[])
        # Register blueprints (your existing files)
    try:
        from app.auth import auth_bp
        from app.routes import main_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
    except ImportError:
        pass  # Skip if blueprints missing
    
    return app

