from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from .. import app
from .ml_model import predict_grade

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    role = session.get('role')
    if not role:
        return redirect(url_for('auth.login'))
    
    if role == 'owner':
        batteries = app.supabase.table('batteries').eq('user_id', session['user_id']).execute().data or []
        return render_template('dashboard_owner.html', batteries=batteries)
    
    elif role == 'center':
        requests = app.supabase.table('pickup_requests').eq('status', 'Pending').execute().data or []
        return render_template('dashboard_center.html', requests=requests)
    
    elif role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    
    return redirect(url_for('auth.login'))

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    # ✅ FIXES "Loading centers..."
    pending_centers = app.supabase.table('centers').eq('status', 'pending').execute().data or []
    return render_template('dashboard_admin.html', pending_centers=pending_centers)

@main_bp.route('/admin/approve/<center_id>')
def approve_center(center_id):
    if session.get('role') != 'admin':
        return redirect(url_for('main.admin_dashboard'))
    
    app.supabase.table('centers').update({'status': 'approved'}).eq('id', center_id).execute()
    flash('✅ Center approved!')
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/add_battery', methods=['GET', 'POST'])
def add_battery():
    if session.get('role') != 'owner':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = {
            'battery_id': request.form['battery_id'],
            'vehicle_model': request.form['vehicle_model'],
            'capacity': float(request.form['capacity']),
            'usage_years': float(request.form['usage_years']),
            'user_id': session['user_id'],
            'grade': 'Pending',
            'status': 'Pending'
        }
        app.supabase.table('batteries').insert(data).execute()
        flash('✅ Battery added!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_battery.html')

@main_bp.route('/request_pickup/<battery_id>', methods=['POST'])
def request_pickup(battery_id):
    if session.get('role') != 'owner':
        return jsonify({'error': 'Access denied'}), 403
    
    battery = app.supabase.table('batteries').eq('id', battery_id).eq('user_id', session['user_id']).execute().data
    if not battery:
        return jsonify({'error': 'Battery not found'}), 404
    
    existing = app.supabase.table('pickup_requests').eq('battery_id', battery_id).execute().data
    if existing:
        return jsonify({'error': 'Already requested'}), 400
    
    app.supabase.table('pickup_requests').insert({
        'battery_id': battery_id,
        'status': 'Pending'
    }).execute()
    
    return jsonify({'success': True, 'message': '✅ Pickup requested!'})

@main_bp.route('/process_request/<request_id>', methods=['POST'])
def process_request(request_id):
    if session.get('role') != 'center':
        return jsonify({'error': 'Access denied'}), 403
    
    request_obj = app.supabase.table('pickup_requests').eq('id', request_id).eq('status', 'Pending').execute().data
    if not request_obj:
        return jsonify({'error': 'Request not found'}), 404
    
    battery = app.supabase.table('batteries').eq('id', request_obj[0]['battery_id']).execute().data[0]
    decision = request.form.get('decision')
    
    grade = predict_grade(battery['capacity'], battery['usage_years'])
    
    app.supabase.table('batteries').update({
        'grade': grade,
        'status': decision
    }).eq('id', battery['id']).execute()
    
    app.supabase.table('pickup_requests').update({
        'status': decision
    }).eq('id', request_id).execute()
    
    return jsonify({'success': True, 'grade': grade})

@main_bp.route('/analytics')
def analytics():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    
    total = app.supabase.table('batteries').select('count').execute().data[0]['count']
    return render_template('analytics.html', total=total)
