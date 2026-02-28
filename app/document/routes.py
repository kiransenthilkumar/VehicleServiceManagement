from flask import render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.document import bp
from app.models import Vehicle, Document
from app.forms import DocumentForm
from app.utils import delete_uploaded_image
from datetime import datetime
import os

@bp.route('/upload/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def upload(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = DocumentForm()
    if form.validate_on_submit():
        if form.file.data:
            # Get absolute path to static/uploads folder
            basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            uploads_dir = os.path.join(basedir, 'static', 'uploads')
            
            # Create directory if it doesn't exist
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir, exist_ok=True)
            
            # Save document
            from werkzeug.utils import secure_filename
            filename = secure_filename(form.file.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(uploads_dir, unique_filename)
            form.file.data.seek(0)
            form.file.data.save(file_path)
            
            document = Document(
                vehicle_id=vehicle_id,
                document_type=form.document_type.data,
                file_path=unique_filename,  # Store filename only
                expiry_date=form.expiry_date.data,
                description=form.description.data
            )
            db.session.add(document)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('vehicle.view', vehicle_id=vehicle_id))
    
    return render_template('document/upload.html', form=form, vehicle=vehicle)

@bp.route('/download/<int:document_id>')
@login_required
def download(document_id):
    document = Document.query.get_or_404(document_id)
    vehicle = document.vehicle
    
    # Check access
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(basedir, 'static', 'uploads', document.file_path)
    
    if os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        flash('File not found.', 'error')
        return redirect(url_for('vehicle.view', vehicle_id=vehicle.id))

@bp.route('/delete/<int:document_id>', methods=['POST'])
@login_required
def delete_document(document_id):
    document = Document.query.get_or_404(document_id)
    vehicle = document.vehicle
    
    # Check access
    if vehicle.user_id != current_user.id and not current_user.is_admin():
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Delete file from filesystem (only for local legacy files)
    if document.file_path and not document.file_path.startswith('http'):
        delete_file(document.file_path)
    # Note: Cloudinary files are deleted by Cloudinary's retention policy or manual cleanup
    
    vehicle_id = vehicle.id
    db.session.delete(document)
    db.session.commit()
    current_app.logger.info(f"Document deleted: {document.file_path}")
    flash('Document deleted successfully!', 'success')
    return redirect(url_for('vehicle.view', vehicle_id=vehicle_id))

@bp.route('/expiring')
@login_required
def expiring_documents():
    if current_user.is_admin():
        vehicles = Vehicle.query.filter_by(is_deleted=False).all()
    else:
        vehicles = Vehicle.query.filter_by(user_id=current_user.id, is_deleted=False).all()
    
    expiring_docs = []
    for vehicle in vehicles:
        docs = Document.query.filter_by(vehicle_id=vehicle.id, is_deleted=False).all()
        for doc in docs:
            if doc.is_expiring_soon(days=30) or doc.is_expired():
                days_until = None
                if doc.expiry_date:
                    days_until = (doc.expiry_date - datetime.now().date()).days
                expiring_docs.append({
                    'vehicle': vehicle,
                    'document': doc,
                    'days_until_expiry': days_until,
                    'is_expired': doc.is_expired()
                })
    
    # Sort by expiry date
    expiring_docs.sort(key=lambda x: x['document'].expiry_date or datetime.max.date())
    
    return render_template('document/expiring.html', expiring_docs=expiring_docs)

