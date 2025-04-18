from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
import qrcode
import os
from datetime import datetime
from flask import current_app

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, name=name)
        user.set_password(password)

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(username)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_filename = f'qr_{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        qr_path = os.path.join('app', 'static', 'qrcodes', qr_filename)
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr_image.save(qr_path)
        
        user.qr_code = qr_filename
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.args.get('role', 'student')  # Default to student if not specified
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Check if user is trying to access admin portal but is not an admin
            if role == 'admin' and user.role != 'admin':
                flash('Access denied. Admin privileges required.', 'danger')
                return redirect(url_for('auth.login', role='student'))
            
            # Check if user is trying to access student portal but is an admin
            if role == 'student' and user.role == 'admin':
                flash('Please use the admin portal for admin access.', 'info')
                return redirect(url_for('auth.login', role='admin'))
            
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.admin_portal'))
            return redirect(url_for('main.student_dashboard'))
        
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', role=request.args.get('role', 'student'))

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.admin_register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.admin_register'))
        
        # Create new admin user
        user = User(
            name=name,
            username=username,
            email=email,
            role='admin'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Admin registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/admin_register.html') 