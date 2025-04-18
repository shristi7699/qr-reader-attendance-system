from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.attendance import Attendance
from app.models.user import User
from app import db
from datetime import datetime, timedelta
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import base64

bp = Blueprint('attendance', __name__)

@bp.route('/scan')
@login_required
def scan():
    return render_template('attendance/scan.html')

@bp.route('/process_qr', methods=['POST'])
@login_required
def process_qr():
    try:
        # Get the image data from the request
        image_data = request.json['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Decode QR code
        qr_codes = decode(img)
        
        if not qr_codes:
            return jsonify({'success': False, 'message': 'No QR code detected'})
        
        qr_data = qr_codes[0].data.decode('utf-8')
        user = User.query.filter_by(username=qr_data).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid QR code'})
        
        # Process attendance
        today = datetime.now().date()
        current_time = datetime.now()
        
        # Check if already marked attendance for today
        attendance = Attendance.get_user_attendance(user.id, today)
        
        if attendance:
            if not attendance.check_out:
                attendance.check_out = current_time
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Check-out recorded for {user.name}',
                    'type': 'checkout'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Attendance already marked for today'
                })
        else:
            # Create new attendance record
            attendance = Attendance(
                user_id=user.id,
                check_in=current_time,
                date=today,
                status='present' if current_time.hour < 9 else 'late'
            )
            db.session.add(attendance)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Check-in recorded for {user.name}',
                'type': 'checkin'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/attendance_report')
@login_required
def attendance_report():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
        
    start_date = request.args.get('start_date', 
                                 (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', 
                               datetime.now().strftime('%Y-%m-%d'))
    
    attendances = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    ).order_by(Attendance.date.desc()).all()
    
    return render_template('attendance/report.html',
                         attendances=attendances,
                         start_date=start_date,
                         end_date=end_date)

@bp.route('/my_qr')
@login_required
def my_qr():
    if current_user.role == 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('admin.admin_portal'))
    return render_template('attendance/my_qr.html') 