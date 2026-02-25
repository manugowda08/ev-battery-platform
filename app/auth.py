from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt
from .. import app  # Global app with supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        # Query Supabase users table
        response = app.supabase.table('users').select('*').eq('email', email).execute()
        user_data = response.data[0] if response.data else None
        
        if user_data and bcrypt.checkpw(password, user_data['password_hash'].encode('utf-8')):
            session['user_id'] = str(user_data['id'])
            session['email'] = user_data['email']
            session['role'] = user_data['role']
            
            if user_data['role'] == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user_data['role'] == 'owner':
                return redirect(url_for('main.owner_dashboard'))
            elif user_data['role'] == 'center':
                return redirect(url_for('main.center_dashboard'))
        
        flash('❌ Invalid credentials!')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('✅ Logged out!')
    return redirect(url_for('auth.login'))
