from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.models import User, Vehicle, ServiceRequest, ServiceRecord, Invoice
from datetime import datetime, timedelta
from sqlalchemy import func, extract

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_vehicles = Vehicle.query.filter_by(is_deleted=False).count()
    total_customers = User.query.filter_by(role='customer', is_deleted=False).count()
    
    # Today's requests
    today = datetime.now().date()
    today_requests = ServiceRequest.query.filter(
        func.date(ServiceRequest.created_at) == today,
        ServiceRequest.is_deleted == False
    ).count()
    
    # Pending requests
    pending_requests = ServiceRequest.query.filter_by(status='pending', is_deleted=False).count()
    
    # In progress services
    in_progress = ServiceRequest.query.filter_by(status='in_progress', is_deleted=False).count()
    
    # Monthly revenue (current month)
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = db.session.query(func.sum(Invoice.amount)).filter(
        extract('month', Invoice.created_at) == current_month,
        extract('year', Invoice.created_at) == current_year,
        Invoice.payment_status == 'paid',
        Invoice.is_deleted == False
    ).scalar() or 0
    
    # Pending payments
    pending_payments = db.session.query(func.sum(Invoice.amount)).filter(
        Invoice.payment_status == 'pending',
        Invoice.is_deleted == False
    ).scalar() or 0
    
    # Total invoices
    total_invoices = Invoice.query.filter_by(is_deleted=False).count()
    
    # Total revenue (all time)
    total_revenue = db.session.query(func.sum(Invoice.amount)).filter(
        Invoice.payment_status == 'paid',
        Invoice.is_deleted == False
    ).scalar() or 0
    
    # Completion rate (completed vs total)
    total_requests = ServiceRequest.query.filter_by(is_deleted=False).count()
    completed_requests = ServiceRequest.query.filter_by(status='completed', is_deleted=False).count()
    completion_rate = round((completed_requests / total_requests * 100) if total_requests > 0 else 0)
    
    # Average rating
    avg_rating = 4.5  # You can calculate from actual ratings if you have them
    
    # Recent service requests
    recent_requests = ServiceRequest.query.filter_by(is_deleted=False).order_by(
        ServiceRequest.created_at.desc()
    ).limit(10).all()
    
    # Revenue chart data (last 6 months)
    revenue_data = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - timedelta(days=30*i)
        month_revenue = db.session.query(func.sum(Invoice.amount)).filter(
            extract('month', Invoice.created_at) == month_date.month,
            extract('year', Invoice.created_at) == month_date.year,
            Invoice.payment_status == 'paid',
            Invoice.is_deleted == False
        ).scalar() or 0
        revenue_data.append({
            'month': month_date.strftime('%b %Y'),
            'revenue': float(month_revenue)
        })
    
    return render_template('admin/dashboard.html',
                         total_vehicles=total_vehicles,
                         total_customers=total_customers,
                         today_requests=today_requests,
                         pending_requests=pending_requests,
                         in_progress=in_progress,
                         monthly_revenue=float(monthly_revenue),
                         pending_payments=float(pending_payments),
                         total_invoices=total_invoices,
                         total_revenue=f"₹{total_revenue:,.0f}",
                         completion_rate=completion_rate,
                         avg_rating=avg_rating,
                         recent_requests=recent_requests,
                         revenue_data=revenue_data)

@bp.route('/requests')
@login_required
@admin_required
def requests():
    status_filter = request.args.get('status', 'all')
    query = ServiceRequest.query.filter_by(is_deleted=False)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    requests = query.order_by(ServiceRequest.created_at.desc()).all()
    return render_template('admin/requests.html', requests=requests, status_filter=status_filter)

@bp.route('/vehicles')
@login_required
@admin_required
def vehicles():
    vehicles = Vehicle.query.filter_by(is_deleted=False).order_by(Vehicle.created_at.desc()).all()
    return render_template('admin/vehicles.html', vehicles=vehicles)

@bp.route('/vehicles/<int:vehicle_id>')
@login_required
@admin_required
def view_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.is_deleted:
        flash('Vehicle not found.', 'error')
        return redirect(url_for('admin.vehicles'))
    service_records = ServiceRecord.query.filter_by(vehicle_id=vehicle_id, is_deleted=False).all()
    return render_template('admin/vehicle_view.html', vehicle=vehicle, service_records=service_records, now=datetime.now)

@bp.route('/customers')
@login_required
@admin_required
def customers():
    customers = User.query.filter_by(role='customer', is_deleted=False).order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customers)

@bp.route('/invoices')
@login_required
@admin_required
def invoices():
    payment_filter = request.args.get('payment', 'all')
    query = Invoice.query.filter_by(is_deleted=False)
    
    if payment_filter != 'all':
        query = query.filter_by(payment_status=payment_filter)
    
    invoices = query.order_by(Invoice.created_at.desc()).all()
    return render_template('admin/invoices.html', invoices=invoices, payment_filter=payment_filter)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    # Yearly maintenance cost report
    current_year = datetime.now().year
    yearly_data = db.session.query(
        extract('month', ServiceRecord.service_date).label('month'),
        func.sum(ServiceRecord.total_amount).label('total')
    ).filter(
        extract('year', ServiceRecord.service_date) == current_year,
        ServiceRecord.is_deleted == False
    ).group_by(extract('month', ServiceRecord.service_date)).all()
    
    monthly_totals = [0] * 12
    for month, total in yearly_data:
        monthly_totals[int(month) - 1] = float(total)
    
    # Vehicle-wise expense summary
    vehicle_expenses = db.session.query(
        Vehicle.registration_number,
        Vehicle.brand,
        Vehicle.model,
        func.sum(ServiceRecord.total_amount).label('total_expense'),
        func.count(ServiceRecord.id).label('service_count')
    ).join(
        ServiceRecord, Vehicle.id == ServiceRecord.vehicle_id
    ).filter(
        Vehicle.is_deleted == False,
        ServiceRecord.is_deleted == False
    ).group_by(Vehicle.id).order_by(func.sum(ServiceRecord.total_amount).desc()).limit(10).all()
    
    return render_template('admin/reports.html',
                         monthly_totals=monthly_totals,
                         vehicle_expenses=vehicle_expenses)

@bp.route('/invoice/<int:invoice_id>/mark-paid', methods=['GET'])
@login_required
@admin_required
def mark_invoice_paid(invoice_id):
    """Mark invoice as paid via cash payment (admin only)"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    if invoice.payment_status != 'paid':
        invoice.payment_status = 'paid'
        invoice.payment_date = datetime.now()
        db.session.commit()
        flash(f'✓ Invoice #{invoice.invoice_number} marked as paid (Cash). Amount: ₹{invoice.amount:.2f}', 'success')
    else:
        flash('Invoice is already marked as paid.', 'info')
    
    return redirect(url_for('admin.invoices'))

