from flask import Blueprint, render_template, flash, redirect, url_for, current_app, request, send_file
from flask_login import login_required, current_user
from app.models import User, Attendance
from app.utils.qr_generator import generate_qr_code
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

student_bp = Blueprint('student', __name__)

@student_bp.route('/my-qr')
@login_required
def my_qr():
    if current_user.role != 'student':
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        # Create qrcodes directory if it doesn't exist
        qr_dir = os.path.join(current_app.static_folder, 'qrcodes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Check if user already has a QR code
        existing_qr = None
        for file in os.listdir(qr_dir):
            if file.startswith(f'qr_{current_user.username}_'):
                existing_qr = file
                break
        
        if existing_qr:
            qr_code_path = f'qrcodes/{existing_qr}'
            logger.info(f"Using existing QR code: {qr_code_path}")
            return render_template('student_qr.html', qr_code_path=qr_code_path)
        
        # Generate new QR code if none exists
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        qr_filename = f'qr_{current_user.username}_{timestamp}.png'
        qr_path = os.path.join(qr_dir, qr_filename)
        
        # Generate QR code
        logger.info(f"Generating QR code for user {current_user.username}")
        generate_qr_code(current_user.username, qr_path, student_name=current_user.name)
        qr_code_path = f'qrcodes/{qr_filename}'
        
        # Verify the file was created
        if not os.path.exists(qr_path):
            raise FileNotFoundError("QR code file was not created")
        
        logger.info(f"QR code generated successfully at {qr_path}")
        flash('QR code generated successfully!', 'success')
        return render_template('student_qr.html', qr_code_path=qr_code_path)
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        flash('Error generating QR code. Please try again.', 'danger')
        return render_template('student_qr.html', qr_code_path=None)

@student_bp.route('/download-qr/<filename>')
@login_required
def download_qr(filename):
    if current_user.role != 'student':
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        # Ensure the filename only contains safe characters
        if '..' in filename or filename.startswith('/'):
            raise ValueError("Invalid filename")
            
        qr_path = os.path.join(current_app.static_folder, 'qrcodes', filename)
        
        # Verify file exists and is within the qrcodes directory
        if not os.path.exists(qr_path):
            logger.error(f"QR code file not found: {qr_path}")
            flash('QR code file not found.', 'danger')
            return redirect(url_for('student.my_qr'))
            
        # Send the file
        return send_file(
            qr_path,
            as_attachment=True,
            download_name=f"qr_code_{current_user.username}.png",
            mimetype='image/png'
        )
            
    except Exception as e:
        logger.error(f"Error downloading QR code: {str(e)}")
        flash('Error downloading QR code.', 'danger')
        return redirect(url_for('student.my_qr'))

@student_bp.route('/my-attendance')
@login_required
def my_attendance():
    if current_user.role != 'student':
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get date filter from query parameters
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
    except ValueError:
        filter_date = datetime.now()
    
    # Get attendance records for the student
    attendance_records = Attendance.query.filter_by(
        user_id=current_user.id
    ).filter(
        Attendance.date >= filter_date,
        Attendance.date < filter_date + timedelta(days=1)
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('student_attendance.html', 
                         attendance_records=attendance_records,
                         selected_date=date_filter)

@student_bp.route('/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get date range for statistics
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get attendance records
    attendance_records = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    # Calculate statistics using the enhanced utility function
    stats = calculate_attendance_stats(
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get today's attendance status
    today_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=datetime.now().date()
    ).first()
    
    return render_template('student_dashboard.html',
                         attendance_records=attendance_records,
                         stats=stats,
                         today_attendance=today_attendance) 