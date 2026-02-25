from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        # Query Supabase
        response = app.supabase.table('users').select('*').eq('email', email).execute()
        user_data = response.data[0] if response.data else None
        
        if user_data and bcrypt.checkpw(password, user_data['password_hash'].encode('utf-8')):
            session['user_id'] = str(user_data['id'])
            session['email'] = user_data['email']
            session['role'] = user_data['role']
            flash('✅ Login successful!')
            return redirect('/dashboard')
        
        flash('❌ Invalid credentials!')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('✅ Logged out!')
    return redirect('/login')
