from app import create_app, db
from app.models.user import User

def update_admin_user(username, new_email=None, new_password=None, new_name=None):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"User {username} not found!")
            return
        
        if new_email:
            user.email = new_email
        if new_password:
            user.set_password(new_password)
        if new_name:
            user.name = new_name
            
        db.session.commit()
        print(f"Admin user {username} has been updated successfully!")

if __name__ == '__main__':
    username = input("Enter admin username to update: ")
    print("\nLeave blank if you don't want to update that field")
    new_email = input("Enter new email (or press Enter to skip): ")
    new_password = input("Enter new password (or press Enter to skip): ")
    new_name = input("Enter new name (or press Enter to skip): ")
    
    # Convert empty strings to None
    new_email = new_email if new_email else None
    new_password = new_password if new_password else None
    new_name = new_name if new_name else None
    
    update_admin_user(username, new_email, new_password, new_name) 