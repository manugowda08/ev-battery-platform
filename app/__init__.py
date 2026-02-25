from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# Global Supabase client
supabase_client = None

@app.before_first_request
def setup_supabase():
    global supabase_client
    try:
        from supabase import create_client
        supabase_client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
    except:
        supabase_client = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-supabase')
def test_supabase():
    if not supabase_client:
        return "❌ Supabase not available"
    try:
        response = supabase_client.table('users').select('count').execute()
        count = response.data[0]['count'] if response.data else 0
        return f"✅ Supabase OK! {count} users"
    except Exception as e:
        return f"❌ Test failed: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        # HARDCODED DEMO USERS (WORKS 100%)
        users = {
            'admin@localhost.com': {'role': 'admin', 'id': '1'},
            'owner1@localhost.com': {'role': 'owner', 'id': '2'},
            'center1@localhost.com': {'role': 'center', 'id': '3'}
        }
        
        if email in users and password in ['admin123', 'password123']:
            session['user_id'] = users[email]['id']
            session['email'] = email
            session['role'] = users[email]['role']
            
            if session['role'] == 'admin':
                return redirect('/admin')
            elif session['role'] == 'owner':
                return redirect('/owner-dashboard')
            elif session['role'] == 'center':
                return redirect('/center-dashboard')
        
        flash('❌ Wrong email/password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('dashboard_admin.html')

@app.route('/owner-dashboard')
def owner_dashboard():
    if session.get('role') != 'owner':
        return redirect('/login')
    return render_template('dashboard_owner.html')

@app.route('/center-dashboard')
def center_dashboard():
    if session.get('role') != 'center':
        return redirect('/login')
    return render_template('dashboard_center.html')

if __name__ == '__main__':
    app.run(debug=True)
