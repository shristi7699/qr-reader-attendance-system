from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # 'admin' or 'student'
    qr_code = db.Column(db.String(128))
    qr_code_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New fields for enhanced features
    profile_picture = db.Column(db.String(128))
    email_notifications = db.Column(db.Boolean, default=True)
    attendance_reminders = db.Column(db.Boolean, default=True)
    weekly_reports = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(20), default='UTC')
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def regenerate_qr_code(self):
        """Regenerate the user's QR code"""
        from app.utils.qr_generator import generate_qr_code
        import os
        from datetime import datetime
        
        # Generate new QR code
        qr_filename = f'qr_{self.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        qr_path = os.path.join('app', 'static', 'qrcodes', qr_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        
        # Generate QR code
        generate_qr_code(self.username, qr_path)
        
        # Delete old QR code if it exists
        if self.qr_code:
            old_qr_path = os.path.join('app', 'static', 'qrcodes', self.qr_code)
            if os.path.exists(old_qr_path):
                os.remove(old_qr_path)
        
        # Update user record
        self.qr_code = qr_filename
        self.qr_code_created_at = datetime.utcnow()
        db.session.commit()
        
        return qr_filename

    def update_profile_picture(self, filename):
        """Update the user's profile picture"""
        self.profile_picture = filename
        db.session.commit()

    def update_notification_settings(self, email_notifications, attendance_reminders, weekly_reports):
        """Update notification settings"""
        self.email_notifications = email_notifications
        self.attendance_reminders = attendance_reminders
        self.weekly_reports = weekly_reports
        db.session.commit()

    def update_language_settings(self, language, timezone):
        """Update language and timezone settings"""
        self.language = language
        self.timezone = timezone
        db.session.commit()

    def record_login_attempt(self, success):
        """Record a login attempt and handle account locking"""
        from datetime import datetime, timedelta
        
        if success:
            self.login_attempts = 0
            self.account_locked_until = None
            self.last_login = datetime.utcnow()
        else:
            self.login_attempts += 1
            if self.login_attempts >= 5:
                # Lock account for 15 minutes
                self.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        db.session.commit()

    def is_account_locked(self):
        """Check if the account is locked"""
        if self.account_locked_until and self.account_locked_until > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f'<User {self.username}>' 