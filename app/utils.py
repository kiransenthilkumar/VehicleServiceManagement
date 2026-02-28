from flask import current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_image(file):
    """
    Save uploaded image to static/uploads/vehicles/ and return filename only
    
    Args:
        file: File object from form.image.data
        
    Returns:
        filename string (e.g., 'car_20250214_120000.jpg') or None on failure
    """
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        current_app.logger.warning(f"File rejected - invalid extension: {file.filename}")
        return None
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # Get absolute path to static/uploads/vehicles folder
        uploads_dir = current_app.config.get('VEHICLE_UPLOAD_FOLDER')
        
        # Create directory if it doesn't exist
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir, exist_ok=True)
            current_app.logger.info(f"Created uploads directory: {uploads_dir}")
        
        # Full path to save file
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save the file
        file.seek(0)
        file.save(file_path)
        
        current_app.logger.info(f"Image saved successfully: {unique_filename}")
        return unique_filename
        
    except Exception as e:
        current_app.logger.error(f"Error saving image: {str(e)}")
        return None

def delete_uploaded_image(filename):
    """
    Delete uploaded image from static/uploads/vehicles/
    
    Args:
        filename: Filename string stored in database
        
    Returns:
        True if deleted, False otherwise
    """
    if not filename:
        return False
    
    try:
        uploads_dir = current_app.config.get('VEHICLE_UPLOAD_FOLDER')
        file_path = os.path.join(uploads_dir, secure_filename(filename))
        
        if os.path.exists(file_path):
            os.remove(file_path)
            current_app.logger.info(f"Image deleted: {filename}")
            return True
        else:
            current_app.logger.warning(f"Image file not found: {file_path}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"Error deleting image: {str(e)}")
        return False

def delete_file(file_path):
    """Legacy function - redirects to delete_uploaded_image"""
    if file_path:
        return delete_uploaded_image(file_path)
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
    if hasattr(service_records, 'order_by') and not isinstance(service_records, (list, tuple)):
        try:
            count = service_records.count()
            if count == 0:
                return 50
            last_service = service_records.order_by(ServiceRecord.service_date.desc()).first()
            total_services = count
        except (TypeError, AttributeError):
            service_list = list(service_records) if service_records else []
            if not service_list:
                return 50
            total_services = len(service_list)
            last_service = max(service_list, key=lambda r: r.service_date if r.service_date else datetime.min.date())
    else:
        service_list = list(service_records) if service_records else []
        if not service_list:
            return 50
        total_services = len(service_list)
        last_service = max(service_list, key=lambda r: r.service_date if r.service_date else datetime.min.date())
    
    if not last_service or not last_service.service_date:
        return 50
    
    days_since_service = (datetime.now().date() - last_service.service_date).days
    
    count_score = min(40, total_services * 5)
    
    if days_since_service <= 90:
        recency_score = 40
    elif days_since_service <= 180:
        recency_score = 30
    elif days_since_service <= 365:
        recency_score = 20
    else:
        recency_score = 10
    
    regularity_score = 10
    
    total_score = count_score + recency_score + regularity_score
    return min(100, max(0, total_score))


