from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.vehicle import bp
from app.models import Vehicle
from app.forms import VehicleForm
from app.utils import save_uploaded_image, delete_uploaded_image

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = VehicleForm()
    if form.validate_on_submit():
        # Check if registration number already exists
        existing = Vehicle.query.filter_by(
            registration_number=form.registration_number.data,
            is_deleted=False
        ).first()
        if existing:
            flash('A vehicle with this registration number already exists.', 'error')
            return render_template('vehicle/register.html', form=form)
        
        vehicle = Vehicle(
            user_id=current_user.id,
            registration_number=form.registration_number.data,
            brand=form.brand.data,
            model=form.model.data,
            fuel_type=form.fuel_type.data,
            manufacturing_year=form.manufacturing_year.data,
            current_odometer=form.current_odometer.data
        )
        
        # Upload image if provided
        if form.image.data:
            image_filename = save_uploaded_image(form.image.data)
            if image_filename:
                vehicle.image_path = image_filename
        
        db.session.add(vehicle)
        db.session.commit()
        flash('Vehicle registered successfully!', 'success')
        return redirect(url_for('vehicle.view', vehicle_id=vehicle.id))
    
    return render_template('vehicle/register.html', form=form)

@bp.route('/view/<int:vehicle_id>')
@login_required
def view(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.models import ServiceRecord, ServiceRequest, Document, ServiceReminder
    from app.utils import calculate_vehicle_health_score
    
    service_records = ServiceRecord.query.filter_by(
        vehicle_id=vehicle_id,
        is_deleted=False
    ).order_by(ServiceRecord.service_date.desc()).all()
    
    service_requests = ServiceRequest.query.filter_by(
        vehicle_id=vehicle_id,
        is_deleted=False
    ).order_by(ServiceRequest.created_at.desc()).all()
    
    documents = Document.query.filter_by(
        vehicle_id=vehicle_id,
        is_deleted=False
    ).order_by(Document.created_at.desc()).all()
    
    reminders = ServiceReminder.query.filter_by(
        vehicle_id=vehicle_id,
        is_deleted=False
    ).order_by(ServiceReminder.created_at.desc()).all()
    
    # Calculate vehicle health score
    health_score = calculate_vehicle_health_score(vehicle, service_records)
    
    # Calculate total expenses
    total_expenses = sum(float(record.total_amount) for record in service_records)
    
    return render_template('vehicle/view.html',
                         vehicle=vehicle,
                         service_records=service_records,
                         service_requests=service_requests,
                         documents=documents,
                         reminders=reminders,
                         health_score=health_score,
                         total_expenses=total_expenses)

@bp.route('/list')
@login_required
def list_vehicles():
    if current_user.is_admin():
        vehicles = Vehicle.query.filter_by(is_deleted=False).all()
    else:
        vehicles = Vehicle.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    return render_template('vehicle/list.html', vehicles=vehicles)

@bp.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def edit(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = VehicleForm(obj=vehicle)
    if form.validate_on_submit():
        # Check registration number uniqueness if changed
        if form.registration_number.data != vehicle.registration_number:
            existing = Vehicle.query.filter_by(
                registration_number=form.registration_number.data,
                is_deleted=False
            ).first()
            if existing:
                flash('A vehicle with this registration number already exists.', 'error')
                return render_template('vehicle/edit.html', form=form, vehicle=vehicle)
        
        vehicle.registration_number = form.registration_number.data
        vehicle.brand = form.brand.data
        vehicle.model = form.model.data
        vehicle.fuel_type = form.fuel_type.data
        vehicle.manufacturing_year = form.manufacturing_year.data
        vehicle.current_odometer = form.current_odometer.data
        
        if form.image.data:
            current_app.logger.info(f"Processing image upload for vehicle {vehicle_id}")
            # Delete old image if exists
            if vehicle.image_path:
                current_app.logger.info(f"Deleting old image: {vehicle.image_path}")
                delete_uploaded_image(vehicle.image_path)
            
            # Upload new image
            image_filename = save_uploaded_image(form.image.data)
            if image_filename:
                current_app.logger.info(f"Image uploaded successfully: {image_filename}")
                vehicle.image_path = image_filename
            else:
                current_app.logger.warning("Image upload failed")
                flash('Image upload failed. Please ensure the file is a valid image format.', 'warning')
        
        db.session.commit()
        flash('Vehicle updated successfully!', 'success')
        return redirect(url_for('vehicle.view', vehicle_id=vehicle.id))
    
    # Log form validation errors if they exist
    if form.errors:
        current_app.logger.warning(f"Form validation errors: {form.errors}")
    
    return render_template('vehicle/edit.html', form=form, vehicle=vehicle)

@bp.route('/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def delete(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vehicle.is_deleted = True
    db.session.commit()
    flash('Vehicle deleted successfully!', 'success')
    return redirect(url_for('vehicle.list_vehicles'))

