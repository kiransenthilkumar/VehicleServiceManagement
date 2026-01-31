from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.service import bp
from app.models import Vehicle, ServiceRequest, ServiceRecord, Invoice, ServiceReminder
from app.forms import ServiceRequestForm, ServiceRecordForm, ServiceStatusUpdateForm, PaymentForm
from app.utils import generate_invoice_number, calculate_next_service_date, calculate_next_service_odometer
from datetime import datetime, timedelta
from decimal import Decimal
from config import Config

@bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_service():
    form = ServiceRequestForm()
    # Populate vehicle choices
    vehicles = Vehicle.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    form.vehicle_id.choices = [(v.id, f"{v.registration_number} - {v.brand} {v.model}") for v in vehicles]
    
    if not form.vehicle_id.choices:
        flash('Please register a vehicle first.', 'info')
        return redirect(url_for('vehicle.register'))
    
    if form.validate_on_submit():
        service_request = ServiceRequest(
            vehicle_id=form.vehicle_id.data,
            user_id=current_user.id,
            service_type=form.service_type.data,
            custom_service_description=form.custom_service_description.data if form.service_type.data == 'Custom' else None,
            preferred_date=form.preferred_date.data,
            preferred_time=form.preferred_time.data,
            status='pending'
        )
        db.session.add(service_request)
        db.session.commit()
        flash('Service request submitted successfully!', 'success')
        return redirect(url_for('service.view_request', request_id=service_request.id))
    
    return render_template('service/request.html', form=form)

@bp.route('/request/<int:request_id>')
@login_required
def view_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('service/view_request.html', service_request=service_request)

@bp.route('/list')
@login_required
def list_requests():
    if current_user.is_admin():
        requests = ServiceRequest.query.filter_by(is_deleted=False).order_by(ServiceRequest.created_at.desc()).all()
    else:
        requests = ServiceRequest.query.filter_by(user_id=current_user.id, is_deleted=False).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('service/list.html', requests=requests)

@bp.route('/update_status/<int:request_id>', methods=['GET', 'POST'])
@login_required
def update_status(request_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    form = ServiceStatusUpdateForm(obj=service_request)
    
    if form.validate_on_submit():
        service_request.status = form.status.data
        service_request.admin_notes = form.admin_notes.data
        service_request.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Service status updated successfully!', 'success')
        return redirect(url_for('service.view_request', request_id=request_id))
    
    return render_template('service/update_status.html', form=form, service_request=service_request)

@bp.route('/complete/<int:request_id>', methods=['GET', 'POST'])
@login_required
def complete_service(request_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if already completed
    if service_request.service_record:
        flash('Service already completed.', 'info')
        return redirect(url_for('service.view_request', request_id=request_id))
    
    form = ServiceRecordForm()
    
    if form.validate_on_submit():
        # Calculate total amount
        total_amount = Decimal(str(form.labor_charge.data)) + Decimal(str(form.additional_cost.data))
        
        # Create service record
        service_record = ServiceRecord(
            service_request_id=service_request.id,
            vehicle_id=service_request.vehicle_id,
            service_date=datetime.now().date(),
            service_type=form.service_type.data,
            parts_replaced=form.parts_replaced.data,
            labor_charge=form.labor_charge.data,
            additional_cost=form.additional_cost.data,
            total_amount=total_amount,
            service_notes=form.service_notes.data,
            odometer_reading=form.odometer_reading.data
        )
        db.session.add(service_record)
        
        # Update service request status
        service_request.status = 'completed'
        service_request.updated_at = datetime.utcnow()
        
        # Update vehicle odometer if provided
        if form.odometer_reading.data:
            vehicle = Vehicle.query.get(service_request.vehicle_id)
            if vehicle:
                vehicle.current_odometer = form.odometer_reading.data
        
        db.session.flush()  # To get the service_record.id
        
        # Generate invoice
        invoice_number = generate_invoice_number(service_record.id)
        invoice = Invoice(
            service_record_id=service_record.id,
            invoice_number=invoice_number,
            amount=total_amount,
            payment_status='pending'
        )
        db.session.add(invoice)
        
        # Create or update service reminder
        vehicle = Vehicle.query.get(service_request.vehicle_id)
        last_reminder = ServiceReminder.query.filter_by(
            vehicle_id=vehicle.id,
            is_deleted=False
        ).order_by(ServiceReminder.created_at.desc()).first()
        
        next_service_date = calculate_next_service_date(service_record.service_date, Config.DEFAULT_SERVICE_INTERVAL_DAYS)
        next_service_odometer = None
        if form.odometer_reading.data:
            next_service_odometer = calculate_next_service_odometer(form.odometer_reading.data, Config.DEFAULT_SERVICE_INTERVAL_KM)
        
        if last_reminder:
            last_reminder.last_service_date = service_record.service_date
            last_reminder.last_service_odometer = form.odometer_reading.data
            last_reminder.next_service_date = next_service_date
            last_reminder.next_service_odometer = next_service_odometer
            last_reminder.is_notified = False
        else:
            reminder = ServiceReminder(
                vehicle_id=vehicle.id,
                last_service_date=service_record.service_date,
                last_service_odometer=form.odometer_reading.data,
                next_service_date=next_service_date,
                next_service_odometer=next_service_odometer,
                reminder_type='both'
            )
            db.session.add(reminder)
        
        db.session.commit()
        flash('Service completed and invoice generated!', 'success')
        return redirect(url_for('service.view_request', request_id=request_id))
    
    # Pre-populate form with service request details
    form.service_type.data = service_request.service_type
    return render_template('service/complete.html', form=form, service_request=service_request)

@bp.route('/history/<int:vehicle_id>')
@login_required
def history(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    records = ServiceRecord.query.filter_by(
        vehicle_id=vehicle_id,
        is_deleted=False
    ).order_by(ServiceRecord.service_date.desc()).all()
    
    return render_template('service/history.html', records=records, vehicle=vehicle)

@bp.route('/invoice/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    service_record = invoice.service_record
    
    # Check access
    if not current_user.is_admin() and service_record.vehicle.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('service/invoice.html', invoice=invoice, service_record=service_record)

@bp.route('/pay/<int:invoice_id>', methods=['GET', 'POST'])
@login_required
def pay_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    service_record = invoice.service_record
    
    # Check access
    if not current_user.is_admin() and service_record.vehicle.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if invoice.payment_status == 'paid':
        flash('Invoice already paid.', 'info')
        return redirect(url_for('service.view_invoice', invoice_id=invoice_id))
    
    form = PaymentForm()
    form.invoice_id.data = invoice_id
    
    if form.validate_on_submit():
        # Mock payment processing - simulate successful payment
        invoice.payment_status = 'paid'
        invoice.payment_date = datetime.utcnow()
        db.session.commit()
        
        # Success message with payment details
        flash(f'✓ Payment of ₹{invoice.amount:.2f} processed successfully via {dict(form.payment_method.choices).get(form.payment_method.data, "Selected Method")}! Invoice #{invoice.invoice_number} is now paid.', 'success')
        return redirect(url_for('service.view_invoice', invoice_id=invoice_id))
    
    return render_template('service/pay.html', form=form, invoice=invoice)

@bp.route('/request/<int:request_id>/mark-paid', methods=['POST'])
@login_required
def mark_request_paid(request_id):
    if not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    service_request = ServiceRequest.query.get_or_404(request_id)
    
    # Check if service has an invoice
    if not service_request.service_record or not service_request.service_record.invoice:
        flash('No invoice found for this service request.', 'error')
        return redirect(url_for('service.view_request', request_id=request_id))
    
    invoice = service_request.service_record.invoice
    
    if invoice.payment_status == 'paid':
        flash('Invoice already marked as paid.', 'info')
    else:
        invoice.payment_status = 'paid'
        invoice.payment_date = datetime.utcnow()
        db.session.commit()
        flash(f'✓ Cash payment of ₹{invoice.amount:.2f} recorded successfully! Invoice #{invoice.invoice_number} is now marked as paid.', 'success')
    
    return redirect(url_for('service.view_request', request_id=request_id))

