from flask import render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.main import bp
from app.models import Vehicle, ServiceRequest, ServiceRecord, ServiceReminder, Document
from app.utils import calculate_vehicle_health_score
from datetime import datetime, timedelta
import os

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Get user's vehicles
    vehicles = Vehicle.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    
    # Get upcoming service reminders
    reminders = []
    for vehicle in vehicles:
        vehicle_reminders = ServiceReminder.query.filter_by(
            vehicle_id=vehicle.id, 
            is_deleted=False
        ).all()
        for reminder in vehicle_reminders:
            if reminder.is_due_soon(days=30) or reminder.is_due():
                reminders.append({
                    'vehicle': vehicle,
                    'reminder': reminder,
                    'is_due': reminder.is_due()
                })
    
    # Get recent service requests
    recent_requests = ServiceRequest.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(ServiceRequest.created_at.desc()).limit(5).all()
    
    # Get recent service records
    recent_services = []
    for vehicle in vehicles:
        records = ServiceRecord.query.filter_by(
            vehicle_id=vehicle.id,
            is_deleted=False
        ).order_by(ServiceRecord.service_date.desc()).limit(3).all()
        recent_services.extend(records)
    recent_services.sort(key=lambda x: x.service_date, reverse=True)
    recent_services = recent_services[:5]
    
    # Calculate statistics
    total_expenses = 0
    for vehicle in vehicles:
        records = ServiceRecord.query.filter_by(vehicle_id=vehicle.id, is_deleted=False).all()
        total_expenses += sum(float(record.total_amount) for record in records)
    
    # Get expiring documents
    expiring_docs = []
    for vehicle in vehicles:
        docs = Document.query.filter_by(vehicle_id=vehicle.id, is_deleted=False).all()
        for doc in docs:
            if doc.is_expiring_soon(days=30):
                expiring_docs.append({
                    'vehicle': vehicle,
                    'document': doc,
                    'days_until_expiry': (doc.expiry_date - datetime.now().date()).days if doc.expiry_date else None
                })
    
    return render_template('main/dashboard.html',
                         vehicles=vehicles,
                         reminders=reminders,
                         recent_requests=recent_requests,
                         recent_services=recent_services,
                         total_expenses=total_expenses,
                         expiring_docs=expiring_docs)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from app.forms import ChangePasswordForm
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
        else:
            # Update password
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully!', 'success')
            return redirect(url_for('main.profile'))
    return render_template('main/profile.html', user=current_user, form=form)

@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files - accessible to anyone who has the filename"""
    try:
        # Try vehicle uploads folder first
        vehicle_folder = current_app.config.get('VEHICLE_UPLOAD_FOLDER')
        if vehicle_folder and os.path.exists(os.path.join(vehicle_folder, secure_filename(filename))):
            return send_from_directory(vehicle_folder, secure_filename(filename))
        # Fall back to general uploads folder
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
    except Exception as e:
        from flask import abort
        current_app.logger.error(f"File not found or error: {e}")
        abort(404)
