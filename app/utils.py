from app.models import Battery, PickupRequest, User
from app.ml_model import predict_grade
from flask import flash
from datetime import datetime

def get_battery_stats():
    """Get statistics for admin analytics"""
    total_batteries = Battery.query.count()
    reuse_count = Battery.query.filter_by(status='Reuse').count()
    recycle_count = Battery.query.filter_by(status='Recycle').count()
    pending_count = Battery.query.filter_by(grade='Pending').count()
    
    return {
        'total': total_batteries,
        'reuse': reuse_count,
        'recycle': recycle_count,
        'pending': pending_count
    }

def process_battery_grading(battery_id):
    """Process ML grading for a specific battery"""
    battery = Battery.query.get(battery_id)
    if not battery:
        flash('Battery not found', 'error')
        return None
    
    grade = predict_grade(battery.capacity, battery.usage_years)
    battery.grade = grade
    battery.status = 'Graded'
    return grade

def get_pending_pickups_for_center(center_id):
    """Get pending pickup requests for specific recycling center"""
    return PickupRequest.query.filter_by(
        status='Pending',
        processed_by=None
    ).join(Battery).filter(
        Battery.user_id != center_id
    ).all()

def format_grade_badge(grade):
    """Return Bootstrap badge class for battery grade"""
    badges = {
        'A': 'bg-success',
        'B': 'bg-warning',
        'C': 'bg-danger',
        'Pending': 'bg-secondary'
    }
    return badges.get(grade, 'bg-secondary')
