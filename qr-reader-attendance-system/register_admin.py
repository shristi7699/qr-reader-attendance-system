from app import create_app, db
from app.models.user import User
import qrcode
import os
from datetime import datetime

def register_admin(username, email, password, name):
    app = create_app()
    with app.app_context():
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            print(f"Username {username} already exists!")
            return
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            print(f"Email {email} already registered!")
            return
        
        # Create admin user
        user = User(
            username=username,
            email=email,
            name=name,
            role='admin'  # Set role as admin
        )
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
        
        print("\nAdmin Registration Successful!")
        print("-" * 50)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Name: {name}")
        print(f"Role: Admin")
        print(f"QR Code saved as: {qr_filename}")
        print("\nYou can now login at http://localhost:8080/login")

if __name__ == '__main__':
    print("Admin Registration Form")
    print("-" * 50)
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    name = input("Enter full name: ")
    
    register_admin(username, email, password, name) 