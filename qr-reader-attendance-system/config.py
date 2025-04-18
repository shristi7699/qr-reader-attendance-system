import os

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance', 'attendance.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    QR_CODE_FOLDER = os.path.join('app', 'static', 'qrcodes')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Admin configuration
    ADMIN_REGISTRATION_KEY = os.environ.get('ADMIN_REGISTRATION_KEY') or 'admin123'  # Default key for development
    
    # Attendance configuration
    LATE_THRESHOLD_HOUR = 9  # 9:00 AM
    LATE_THRESHOLD_MINUTE = 0
    EARLY_LEAVE_THRESHOLD_HOUR = 17  # 5:00 PM
    EARLY_LEAVE_THRESHOLD_MINUTE = 0
    
    # Application settings
    DEBUG = True
    TESTING = False 