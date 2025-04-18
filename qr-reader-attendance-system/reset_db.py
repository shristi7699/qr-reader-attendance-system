from app import create_app, db
import os
import time
import sqlite3

def reset_database():
    app = create_app()
    with app.app_context():
        # Delete the existing database file
        db_path = 'instance/attendance.db'
        
        # Try to close any existing connections
        try:
            conn = sqlite3.connect(db_path)
            conn.close()
        except:
            pass
            
        # Try to delete the file
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                print(f"Deleted existing database at {db_path}")
        except Exception as e:
            print(f"Could not delete existing database: {e}")
            print("Proceeding with table recreation...")
        
        # Create all tables
        db.create_all()
        print("Created new database with updated schema")
        
        # Create initial admin user
        from app.models.user import User
        
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created initial admin user (username: admin, password: admin123)")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    reset_database() 