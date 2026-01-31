from flask import current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, subfolder=''):
    """Save uploaded file and return the file path"""
    if not file:
        return None
    
    if not allowed_file(file.filename):
        current_app.logger.warning(f"File rejected - invalid extension: {file.filename}")
        return None
    
    try:
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        if subfolder:
            # Ensure subdirectory exists
            subfolder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
            if not os.path.exists(subfolder_path):
                os.makedirs(subfolder_path, exist_ok=True)
            upload_path = os.path.join(subfolder_path, filename)
            # Return relative path with forward slashes for URL generation
            relative_path = f"{subfolder}/{filename}"
        else:
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            relative_path = filename
        
        file.save(upload_path)
        current_app.logger.info(f"File saved successfully: {upload_path}")
        current_app.logger.info(f"Relative path stored in DB: {relative_path}")
        
        # Return relative path with forward slashes for database storage (URL compatible)
        return relative_path
    except Exception as e:
        current_app.logger.error(f"Error saving file: {str(e)}")
        return None

def delete_file(file_path):
    """Delete a file from the uploads directory"""
    if file_path:
        # Convert forward slashes to backslashes for Windows path operations
        # file_path might be stored with forward slashes (URL format)
        normalized_path = file_path.replace('/', os.sep)
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], normalized_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                current_app.logger.info(f"File deleted: {full_path}")
                return True
            except Exception as e:
                current_app.logger.error(f"Error deleting file: {str(e)}")
                return False
    return False

def generate_invoice_number(service_record_id):
    """Generate a unique invoice number"""
    timestamp = datetime.now().strftime('%Y%m%d')
    return f"INV-{timestamp}-{service_record_id:06d}"

def calculate_next_service_date(last_service_date, interval_days=180):
    """Calculate next service date based on interval"""
    if last_service_date:
        if isinstance(last_service_date, str):
            last_service_date = datetime.strptime(last_service_date, '%Y-%m-%d').date()
        return last_service_date + timedelta(days=interval_days)
    return None

def calculate_next_service_odometer(last_odometer, interval_km=10000):
    """Calculate next service odometer reading"""
    if last_odometer:
        return last_odometer + interval_km
    return None

def calculate_vehicle_health_score(vehicle, service_records):
    """Calculate vehicle health score based on service regularity (0-100)"""
    from app.models import ServiceRecord
    
    # Handle both list and query object
    # Check if it's a SQLAlchemy Query object by checking for order_by method (lists don't have this)
    if hasattr(service_records, 'order_by') and not isinstance(service_records, (list, tuple)):
        try:
            # It's a query object - can call count() without arguments
            count = service_records.count()
            if count == 0:
                return 50
            last_service = service_records.order_by(ServiceRecord.service_date.desc()).first()
            total_services = count
        except (TypeError, AttributeError):
            # Fallback to list handling
            service_list = list(service_records) if service_records else []
            if not service_list:
                return 50
            total_services = len(service_list)
            last_service = max(service_list, key=lambda r: r.service_date if r.service_date else datetime.min.date())
    else:
        # It's a list or other iterable - use len() and max()
        service_list = list(service_records) if service_records else []
        if not service_list:
            return 50
        total_services = len(service_list)
        last_service = max(service_list, key=lambda r: r.service_date if r.service_date else datetime.min.date())
    
    if not last_service or not last_service.service_date:
        return 50
    
    # Factors:
    # 1. Service frequency (regular services = higher score)
    # 2. Recency of last service
    # 3. Number of services
    
    days_since_service = (datetime.now().date() - last_service.service_date).days
    
    # Base score from service count (max 40 points)
    count_score = min(40, total_services * 5)
    
    # Recency score (max 40 points) - better if serviced recently
    if days_since_service <= 90:
        recency_score = 40
    elif days_since_service <= 180:
        recency_score = 30
    elif days_since_service <= 365:
        recency_score = 20
    else:
        recency_score = 10
    
    # Regularity bonus (max 20 points) - if services are spaced reasonably
    regularity_score = 10  # Base regularity
    
    total_score = count_score + recency_score + regularity_score
    return min(100, max(0, total_score))


