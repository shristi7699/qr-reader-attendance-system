from datetime import datetime, timedelta
from app.models.attendance import Attendance
from app.models.user import User
from app import db

def mark_attendance(username, check_type='check_in'):
    """
    Mark attendance for a student.
    
    Args:
        username (str): The username of the student
        check_type (str): Either 'check_in' or 'check_out'
    
    Returns:
        tuple: (success, message)
    """
    try:
        # Get the user
        user = User.query.filter_by(username=username).first()
        if not user:
            return False, "User not found"
            
        # Get today's date
        today = datetime.now().date()
        
        # Check if there's already an attendance record for today
        attendance = Attendance.query.filter_by(
            user_id=user.id,
            date=today
        ).first()
        
        if check_type == 'check_in':
            if attendance and attendance.check_in:
                return False, "Check-in already recorded for today"
                
            if not attendance:
                attendance = Attendance(user_id=user.id, date=today)
                db.session.add(attendance)
                
            attendance.check_in = datetime.now()
            message = "Check-in recorded successfully"
            
        else:  # check_out
            if not attendance or not attendance.check_in:
                return False, "No check-in record found for today"
                
            if attendance.check_out:
                return False, "Check-out already recorded for today"
                
            attendance.check_out = datetime.now()
            message = "Check-out recorded successfully"
        
        db.session.commit()
        return True, message
        
    except Exception as e:
        db.session.rollback()
        return False, f"Error recording attendance: {str(e)}"

def get_attendance_report(user_id, start_date=None, end_date=None):
    """
    Get attendance report for a user within a date range.
    
    Args:
        user_id (int): The ID of the user
        start_date (datetime): Start date for the report
        end_date (datetime): End date for the report
    
    Returns:
        list: List of attendance records
    """
    query = Attendance.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
        
    return query.order_by(Attendance.date.desc()).all()

def calculate_attendance_stats(user_id, start_date=None, end_date=None):
    """
    Calculate detailed attendance statistics for a user.
    
    Args:
        user_id (int): The ID of the user
        start_date (datetime): Start date for the stats
        end_date (datetime): End date for the stats
    
    Returns:
        dict: Dictionary containing detailed attendance statistics
    """
    query = Attendance.query.filter_by(user_id=user_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
        
    records = query.all()
    
    total_days = len(records)
    present_days = sum(1 for r in records if r.status == 'present')
    late_days = sum(1 for r in records if r.status == 'late')
    absent_days = sum(1 for r in records if r.status == 'absent')
    
    # Calculate average check-in time for present days
    present_check_ins = [r.check_in for r in records if r.check_in and r.status == 'present']
    avg_check_in = None
    if present_check_ins:
        total_minutes = sum(t.hour * 60 + t.minute for t in present_check_ins)
        avg_minutes = total_minutes / len(present_check_ins)
        avg_check_in = f"{int(avg_minutes // 60):02d}:{int(avg_minutes % 60):02d}"
    
    # Calculate attendance streak
    current_streak = 0
    max_streak = 0
    temp_streak = 0
    
    sorted_records = sorted(records, key=lambda x: x.date)
    for i in range(len(sorted_records)):
        if sorted_records[i].status in ['present', 'late']:
            temp_streak += 1
            if temp_streak > max_streak:
                max_streak = temp_streak
        else:
            temp_streak = 0
    
    # Current streak is the most recent consecutive attendance
    for record in reversed(sorted_records):
        if record.status in ['present', 'late']:
            current_streak += 1
        else:
            break
    
    return {
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'attendance_percentage': (present_days / total_days * 100) if total_days > 0 else 0,
        'avg_check_in': avg_check_in,
        'current_streak': current_streak,
        'max_streak': max_streak,
        'on_time_percentage': (present_days / (present_days + late_days) * 100) if (present_days + late_days) > 0 else 0
    } 