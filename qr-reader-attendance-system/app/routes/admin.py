from flask import Blueprint, render_template, jsonify, request, redirect, url_for, send_file, flash, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.attendance import Attendance
from app import db
from datetime import datetime, timedelta
import pandas as pd
import io
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You must be an admin to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/admin-portal')
@admin_required
def admin_portal():
    """Admin portal dashboard."""
    # Get today's attendance count
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    # Get total students
    total_students = User.query.filter_by(role='student').count()
    
    # Get attendance statistics
    start_date = today - timedelta(days=30)
    attendance_stats = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= today
    ).count()
    
    # Get recent attendance records
    recent_attendance = Attendance.query.order_by(Attendance.date.desc(), Attendance.check_in.desc()).limit(5).all()
    
    stats = {
        'today_attendance': today_attendance,
        'total_students': total_students,
        'monthly_attendance': attendance_stats
    }
    
    return render_template('admin/portal.html', stats=stats, recent_attendance=recent_attendance)

@bp.route('/scan')
@admin_required
def scan_attendance():
    """QR code scanning page for attendance."""
    return render_template('admin/scan.html')

@bp.route('/view-attendance')
@admin_required
def view_attendance():
    """View attendance records for a specific date."""
    try:
        date_str = request.args.get('date')
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'danger')
                selected_date = datetime.now().date()
        else:
            selected_date = datetime.now().date()

        attendance_records = Attendance.query.filter_by(date=selected_date).all()
        return render_template('admin/view_attendance.html', 
                             attendance_records=attendance_records,
                             selected_date=selected_date)
    except Exception as e:
        logger.error(f"Error viewing attendance: {str(e)}")
        flash('An error occurred while viewing attendance', 'danger')
        return redirect(url_for('admin.admin_portal'))

@bp.route('/student-list')
@admin_required
def student_list():
    """View list of all students."""
    students = User.query.filter_by(role='student').all()
    return render_template('admin/students.html', students=students)

@bp.route('/generate-report', methods=['GET', 'POST'])
@admin_required
def generate_report():
    """Generate attendance report for a date range."""
    if request.method == 'POST':
        try:
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
            
            if start_date > end_date:
                flash('Start date must be before end date', 'danger')
                return redirect(url_for('admin.generate_report'))

            attendance_records = Attendance.query.filter(
                Attendance.date.between(start_date, end_date)
            ).all()

            return render_template('admin/report.html',
                                 attendance_records=attendance_records,
                                 start_date=start_date,
                                 end_date=end_date)
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('admin.generate_report'))
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            flash('An error occurred while generating the report', 'danger')
            return redirect(url_for('admin.generate_report'))

    return render_template('admin/generate_report.html')

@bp.route('/export_attendance')
@admin_required
def export_attendance():
    # Get date range
    start_date = request.args.get('start_date', 
                                 (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Query attendance records
    attendances = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    # Create DataFrame
    data = []
    for record in attendances:
        data.append({
            'Date': record.date.strftime('%Y-%m-%d'),
            'Student Name': record.user.name,
            'Check In': record.check_in.strftime('%H:%M:%S') if record.check_in else 'N/A',
            'Check Out': record.check_out.strftime('%H:%M:%S') if record.check_out else 'N/A',
            'Status': record.status
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Attendance', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'attendance_report_{start_date}_to_{end_date}.xlsx'
    )

@bp.route('/mark-attendance', methods=['POST'])
@admin_required
def mark_attendance():
    """API endpoint to mark attendance for a student."""
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'action' not in data:
            return jsonify({'success': False, 'message': 'Invalid request data'}), 400

        username = data['username']
        action = data['action']

        if action not in ['check-in', 'check-out']:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if user.role != 'student':
            return jsonify({'success': False, 'message': 'Only students can be marked for attendance'}), 400

        today = datetime.now().date()
        attendance = Attendance.query.filter_by(
            user_id=user.id,
            date=today
        ).first()

        if not attendance:
            attendance = Attendance(user_id=user.id, date=today)
            db.session.add(attendance)

        current_time = datetime.now()
        
        if action == 'check-in':
            if attendance.check_in:
                return jsonify({'success': False, 'message': 'Already checked in today'}), 400
            attendance.check_in = current_time
            message = f'Check-in recorded for {user.name}'
        else:  # check-out
            if not attendance.check_in:
                return jsonify({'success': False, 'message': 'Must check in before checking out'}), 400
            if attendance.check_out:
                return jsonify({'success': False, 'message': 'Already checked out today'}), 400
            attendance.check_out = current_time
            message = f'Check-out recorded for {user.name}'

        attendance.update_status()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': message,
            'attendance': attendance.to_dict()
        })

    except Exception as e:
        logger.error(f"Error marking attendance: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while marking attendance'}), 500 