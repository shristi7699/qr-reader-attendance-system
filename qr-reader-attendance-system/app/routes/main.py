from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.attendance import Attendance
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from flask import current_app
from app.utils.qr_generator import generate_qr_code
from app.models.user import User
from app import db

bp = Blueprint('main', __name__)

@bp.route('/test')
def test():
    return jsonify({"status": "ok", "message": "Server is running"})

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_portal'))
        return redirect(url_for('main.student_dashboard'))
    return render_template('index.html')

@bp.route('/register/options')
def register_options():
    return render_template('register_options.html')

@bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_portal'))
        
    # Get today's date
    today = datetime.now().date()
    
    # Get attendance history for the last 30 days
    start_date = today - timedelta(days=30)
    attendance_history = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_date,
        Attendance.date <= today
    ).order_by(Attendance.date.desc()).all()
    
    # Calculate attendance statistics
    total_days = len(attendance_history)
    present_days = sum(1 for record in attendance_history if record.status == 'present')
    late_days = sum(1 for record in attendance_history if record.status == 'late')
    absent_days = total_days - present_days - late_days
    
    # Calculate attendance rate and on-time percentage
    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
    on_time_percentage = (present_days / (present_days + late_days) * 100) if (present_days + late_days) > 0 else 0
    
    stats = {
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'attendance_rate': attendance_rate,
        'on_time_percentage': on_time_percentage
    }
    
    # Get today's attendance
    today_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('student_dashboard.html',
                         today=today,
                         attendance_history=attendance_history,
                         stats=stats,
                         today_attendance=today_attendance)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get today's attendance
    today = datetime.now().date()
    attendance = Attendance.get_user_attendance(current_user.id, today)
    
    # Get attendance statistics
    start_date = today - timedelta(days=30)
    attendance_history = Attendance.get_user_attendance_report(
        current_user.id, start_date, today
    )
    
    # Calculate statistics
    total_days = len(attendance_history)
    present_days = sum(1 for a in attendance_history if a.status == 'present')
    late_days = sum(1 for a in attendance_history if a.status == 'late')
    absent_days = total_days - present_days - late_days
    
    stats = {
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'attendance_rate': (present_days / total_days * 100) if total_days > 0 else 0
    }
    
    return render_template('dashboard.html',
                         attendance=attendance,
                         stats=stats,
                         attendance_history=attendance_history)

@bp.route('/my_attendance')
@login_required
def my_attendance():
    if current_user.role == 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_portal'))
        
    # Get date range from request
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
    
    # Get attendance records
    attendances = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    # Calculate statistics
    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == 'present')
    late_days = sum(1 for a in attendances if a.status == 'late')
    absent_days = total_days - present_days - late_days
    
    stats = {
        'total_days': total_days,
        'present_days': present_days,
        'late_days': late_days,
        'absent_days': absent_days,
        'attendance_rate': (present_days / total_days * 100) if total_days > 0 else 0
    }
    
    return render_template('main/my_attendance.html',
                         attendances=attendances,
                         stats=stats,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))

@bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Update user profile
        current_user.name = name
        current_user.email = email
        
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                # Save the file
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_picture = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.student_dashboard'))
        
    return render_template('update_profile.html')

@bp.route('/student/qr-code')
@login_required
def student_qr_code():
    if current_user.role != 'student':
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Create qr_codes directory if it doesn't exist
    qr_dir = os.path.join(current_app.static_folder, 'qr_codes')
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    # Generate QR code if it doesn't exist
    qr_path = os.path.join(qr_dir, f'{current_user.username}.png')
    if not os.path.exists(qr_path):
        generate_qr_code(current_user.username, qr_path)
    
    return render_template('student_qr_code.html')

@bp.route('/student/analytics')
@login_required
def student_analytics():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_portal'))
    
    # Get attendance data for analytics
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    attendance_data = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date).all()
    
    return render_template('student_analytics.html', attendance_data=attendance_data)

@bp.route('/student/settings', methods=['GET', 'POST'])
@login_required
def student_settings():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_portal'))
    
    if request.method == 'POST':
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            
        return redirect(url_for('main.student_settings'))
    
    return render_template('student_settings.html')

@bp.route('/admin/scan', methods=['GET', 'POST'])
@login_required
def admin_scan():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        student_username = request.form.get('student_username')
        if not student_username:
            flash('No student username provided.', 'danger')
            return redirect(url_for('main.admin_scan'))
        
        student = User.query.filter_by(username=student_username, role='student').first()
        if not student:
            flash('Student not found.', 'danger')
            return redirect(url_for('main.admin_scan'))
        
        # Create attendance record
        attendance = Attendance(
            user_id=student.id,
            date=datetime.now().date()
        )
        attendance.check_in = datetime.now()
        attendance.update_status()
        db.session.add(attendance)
        db.session.commit()
        
        flash(f'Attendance marked for {student.name}.', 'success')
        return redirect(url_for('main.admin_scan'))
    
    return render_template('admin_scan.html')

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'danger')
    elif new_password != confirm_password:
        flash('New passwords do not match', 'danger')
    elif len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully!', 'success')
    
    return redirect(url_for('main.student_dashboard')) 