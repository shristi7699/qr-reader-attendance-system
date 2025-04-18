from datetime import datetime, time
from app import db
from flask import current_app

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='absent')  # 'present', 'late', 'absent', 'early_leave'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, user_id, date, status='absent'):
        self.user_id = user_id
        self.date = date
        self.status = status

    @classmethod
    def get_user_attendance(cls, user_id, date):
        """Get or create attendance record for a user on a specific date."""
        attendance = cls.query.filter_by(user_id=user_id, date=date).first()
        if not attendance:
            attendance = cls(user_id=user_id, date=date)
            db.session.add(attendance)
            db.session.flush()
        return attendance

    def update_status(self):
        """Update attendance status based on check-in and check-out times."""
        if not self.check_in:
            self.status = 'absent'
            return
        
        # Get thresholds from config
        late_hour = current_app.config.get('LATE_THRESHOLD_HOUR', 9)
        late_minute = current_app.config.get('LATE_THRESHOLD_MINUTE', 0)
        early_hour = current_app.config.get('EARLY_LEAVE_THRESHOLD_HOUR', 17)
        early_minute = current_app.config.get('EARLY_LEAVE_THRESHOLD_MINUTE', 0)
        
        # Define time thresholds
        LATE_THRESHOLD = time(late_hour, late_minute)
        EARLY_LEAVE_THRESHOLD = time(early_hour, early_minute)
        
        check_in_time = self.check_in.time()
        check_out_time = self.check_out.time() if self.check_out else None
        
        if check_in_time > LATE_THRESHOLD:
            self.status = 'late'
        elif check_out_time and check_out_time < EARLY_LEAVE_THRESHOLD:
            self.status = 'early_leave'
        else:
            self.status = 'present'

    def __repr__(self):
        return f'<Attendance {self.date} - User {self.user_id}>'

    @staticmethod
    def get_user_attendance_report(user_id, start_date, end_date):
        """Get attendance records for a user within a date range."""
        return Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date).all()

    def to_dict(self):
        """Convert attendance record to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'check_in': self.check_in.isoformat() if self.check_in else None,
            'check_out': self.check_out.isoformat() if self.check_out else None,
            'status': self.status
        } 