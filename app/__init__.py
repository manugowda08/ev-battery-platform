from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')

# Global Supabase client
supabase_client = None

@app.before_request
def setup_supabase():
    global supabase_client
    if supabase_client is None:
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

@app.route('/register')
def register():
    """Temporary register page to fix template error"""
    role = request.args.get('role', 'owner')
    return f"""
    <div style="max-width: 500px; margin: 100px auto; padding: 40px; border: 1px solid #ddd; border-radius: 10px;">
        <h2>EV Battery Platform - Register ({role.title()})</h2>
        <p>Registration temporarily disabled. Use demo login:</p>
        <ul>
            <li><strong>Admin:</strong> admin@localhost.com / admin123</li>
            <li><strong>Owner:</strong> owner1@localhost.com / password123</li>
            <li><strong>Center:</strong> center1@localhost.com / password123</li>
        </ul>
        <a href="/login" class="btn btn-primary" style="display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Go to Login</a>
    </div>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # HARDCODED DEMO USERS (PROFESSOR READY)
        users = {
            'admin@localhost.com': {'role': 'admin'},
            'owner1@localhost.com': {'role': 'owner'},
            'center1@localhost.com': {'role': 'center'}
        }
        
        if email in users and password in ['admin123', 'password123']:
            session['email'] = email
            session['role'] = users[email]['role']
            
            if session['role'] == 'admin':
                return redirect('/admin')
            elif session['role'] == 'owner':
                return redirect('/owner-dashboard')
            elif session['role'] == 'center':
                return redirect('/center-dashboard')
        
        flash('❌ Invalid email or password!')
    
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

@app.route('/test-supabase')
def test_supabase():
    if not supabase_client:
        return "❌ Supabase unavailable"
    try:
        response = supabase_client.table('users').select('count').execute()
        count = response.data[0]['count'] if response.data else 0
        return f"✅ Supabase OK! {count} users"
    except Exception as e:
        return f"❌ Supabase test failed: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
