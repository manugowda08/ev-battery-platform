from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Battery, PickupRequest
from app.ml_model import predict_grade

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'owner':
        batteries = Battery.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard_owner.html', batteries=batteries)
    elif current_user.role == 'center':
        requests = PickupRequest.query.filter_by(status='Pending').all()
        return render_template('dashboard_center.html', requests=requests)
    elif current_user.role == 'admin':
        return render_template('dashboard_admin.html')
    flash('Invalid role')
    return redirect(url_for('main.index'))

@main_bp.route('/pickup_requests')
@login_required
def pickup_requests():
    """✅ MISSING ROUTE - All pickup requests page"""
    if current_user.role != 'center':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
    
    all_requests = PickupRequest.query.all()
    return render_template('pickup_requests.html', requests=all_requests)

@main_bp.route('/add_battery', methods=['GET', 'POST'])
@login_required
def add_battery():
    if request.method == 'POST':
        battery = Battery(
            battery_id=request.form['battery_id'],
            vehicle_model=request.form['vehicle_model'],
            capacity=float(request.form['capacity']),
            usage_years=float(request.form['usage_years']),
            user_id=current_user.id
        )
        db.session.add(battery)
        db.session.commit()
        flash('Battery added successfully!')
        return redirect(url_for('main.dashboard'))
    return render_template('add_battery.html')

# AJAX Owner Request Pickup
@main_bp.route('/request_pickup/<int:battery_id>', methods=['POST'])
@login_required
def request_pickup(battery_id):
    battery = Battery.query.filter_by(id=battery_id, user_id=current_user.id).first()
    if not battery:
        return jsonify({'error': 'Battery not found'}), 404
    
    existing_request = PickupRequest.query.filter_by(battery_id=battery_id).first()
    if existing_request:
        return jsonify({'error': 'Pickup already requested'}), 400
    
    request_obj = PickupRequest(battery_id=battery_id)
    db.session.add(request_obj)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'✅ Pickup requested for {battery.battery_id}!',
        'request_id': request_obj.id
    })

# Center Process Request (with ML)
@main_bp.route('/process_request/<int:request_id>', methods=['POST'])
@login_required
def process_request(request_id):
    request_obj = PickupRequest.query.get_or_404(request_id)
    battery = request_obj.battery
    
    if current_user.role != 'center':
        return jsonify({'error': 'Access denied'}), 403
    
    decision = request.form.get('decision')
    if decision not in ['Reuse', 'Recycle']:
        return jsonify({'error': 'Invalid decision'}), 400
    
    # ML Grade prediction
    grade = predict_grade(battery.capacity, battery.usage_years)
    battery.grade = grade
    battery.status = decision
    request_obj.status = decision
    request_obj.processed_by = current_user.id
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'✅ {battery.battery_id}: Grade {grade} → {decision}',
        'grade': grade
    })

@main_bp.route('/analytics')
@login_required
def analytics():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
    
    total = Battery.query.count()
    reuse = Battery.query.filter_by(status='Reuse').count()
    recycle = Battery.query.filter_by(status='Recycle').count()
    pending = Battery.query.filter_by(grade='Pending').count()
    grade_a = Battery.query.filter_by(grade='A').count()
    grade_b = Battery.query.filter_by(grade='B').count()
    grade_c = Battery.query.filter_by(grade='C').count()
    
    return render_template('analytics.html', 
                         total=total, reuse=reuse, recycle=recycle,
                         pending=pending, grade_a=grade_a, grade_b=grade_b, grade_c=grade_c)
