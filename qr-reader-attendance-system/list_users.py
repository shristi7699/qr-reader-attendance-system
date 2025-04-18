from app import create_app, db
from app.models.user import User

def list_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print("\nExisting Users:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            print(f"Role: {user.role}")
            print("-" * 50)

if __name__ == '__main__':
    list_users() 