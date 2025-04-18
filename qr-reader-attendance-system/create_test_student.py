from app import create_app, db
from app.models.user import User

def create_test_student():
    app = create_app()
    with app.app_context():
        # Create test student
        student = User(
            username='test_student',
            email='student@example.com',
            name='Test Student',
            role='student'
        )
        student.set_password('student123')
        
        # Add to database
        db.session.add(student)
        db.session.commit()
        print("Created test student account:")
        print("Username: test_student")
        print("Password: student123")

if __name__ == '__main__':
    create_test_student() 