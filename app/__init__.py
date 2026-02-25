from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from supabase import create_client, Client
import bcrypt

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
    
    @app.before_request
    def setup_supabase():
        try:
            app.supabase = create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_ANON_KEY')
            )
        except Exception as e:
            app.supabase = None
            print(f"Supabase init error: {e}")
    
    # Routes
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
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password'].encode('utf-8')
            
            if not app.supabase:
                flash('❌ Database not connected!')
                return render_template('login.html')
            
            try:
                response = app.supabase.table('users').select('*').eq('email', email).execute()
                user_data = response.data[0] if response.data else None
                
                # ✅ FIXED BCRYPT - Safe handling
                if user_data and user_data.get('password_hash'):
                    try:
                        stored_hash = user_data['password_hash'].encode('utf-8') if isinstance(user_data['password_hash'], str) else user_data['password_hash']
                        if bcrypt.checkpw(password, stored_hash):
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
                    except:
                        pass
                
                flash('❌ Invalid credentials!')
            except Exception as e:
                flash('❌ Login error!')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('✅ Logged out!')
        return redirect('/login')
    
    @app.route('/admin')
    def admin_dashboard():
        if session.get('role') != 'admin':
            return redirect('/login')
        centers = []
        if app.supabase:
            try:
                centers = app.supabase.table('centers').eq('status', 'pending').execute().data or []
            except:
                pass
        return render_template('dashboard_admin.html', pending_centers=centers)
    
    @app.route('/owner-dashboard')
    def owner_dashboard():
        if session.get('role') != 'owner':
            return redirect('/login')
        batteries = []
        if app.supabase:
            try:
                batteries = app.supabase.table('batteries').eq('user_id', session['user_id']).execute().data or []
            except:
                pass
        return render_template('dashboard_owner.html', batteries=batteries)
    
    @app.route('/center-dashboard')
    def center_dashboard():
        if session.get('role') != 'center':
            return redirect('/login')
        requests = []
        if app.supabase:
            try:
                requests = app.supabase.table('pickup_requests').eq('status', 'Pending').execute().data or []
            except:
                pass
        return render_template('dashboard_center.html', requests=requests)
    
    return app
