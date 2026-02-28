from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    # Specify template and static folders relative to project root
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(basedir, 'templates')
    static_dir = os.path.join(basedir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Create upload directories (with error handling for Render)
    try:
        upload_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'vehicles'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents')
        ]
        for directory in upload_dirs:
            os.makedirs(directory, exist_ok=True)
    except Exception as e:
        app.logger.warning(f"Could not create upload directories: {e}")
    
    # Register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.vehicle import bp as vehicle_bp
    app.register_blueprint(vehicle_bp, url_prefix='/vehicle')
    
    from app.service import bp as service_bp
    app.register_blueprint(service_bp, url_prefix='/service')
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.document import bp as document_bp
    app.register_blueprint(document_bp, url_prefix='/document')
    
    return app

from app import models

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

