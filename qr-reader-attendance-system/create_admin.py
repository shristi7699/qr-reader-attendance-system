from app import create_app, db
from app.models.user import User

def create_admin_user(username, email, password, name):
    app = create_app()
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            # Update existing user to admin
            user.role = 'admin'
            db.session.commit()
            print(f"User {username} has been updated to admin role")
        else:
            # Create new admin user
            user = User(username=username, email=email, name=name, role='admin')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Admin user {username} has been created")

if __name__ == '__main__':
    # You can modify these values as needed
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    name = input("Enter admin name: ")
    
    create_admin_user(username, email, password, name) 