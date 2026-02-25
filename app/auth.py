from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import app
import bcrypt
from supabase import Client

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        # Get user from Supabase
        response = app.supabase.table('users').select('*').eq('email', email).execute()
        user = response.data[0] if response.data else None
        
        if user and bcrypt.checkpw(password, user['password_hash'].encode('utf-8')):
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'owner':
                return redirect(url_for('owner_dashboard'))
            elif user['role'] == 'center':
                return redirect(url_for('center_dashboard'))
        
        flash('❌ Invalid email or password!')
    
    return render_template('login.html')

app.register_blueprint(auth)
