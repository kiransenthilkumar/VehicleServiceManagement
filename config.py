import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-please-set-in-env'
    # Use SQLite for both local and Render deployment
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'vehicle_service.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Upload folder - use absolute path for Render compatibility
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'bmp', 'svg', 'tiff', 'ico', 'pdf'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Service reminder defaults (days)
    DEFAULT_SERVICE_INTERVAL_DAYS = 180  # 6 months
    DEFAULT_SERVICE_INTERVAL_KM = 10000  # 10,000 km

