from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=None):
    """Create and configure the Flask application."""
    logger.info("Creating Flask application...")
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['QR_CODE_FOLDER'], exist_ok=True)
    
    logger.info("Initializing extensions...")
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models here to avoid circular imports
    from app.models.user import User
    from app.models.attendance import Attendance
    
    logger.info("Registering blueprints...")
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main.bp)
    
    from app.routes import auth
    app.register_blueprint(auth.bp)
    
    from app.routes import attendance
    app.register_blueprint(attendance.bp)
    
    from app.routes import admin
    app.register_blueprint(admin.bp)
    
    from app.routes import student
    app.register_blueprint(student.student_bp)

    logger.info("Creating database tables...")
    with app.app_context():
        db.create_all()
    logger.info("Database tables created successfully")

    return app 