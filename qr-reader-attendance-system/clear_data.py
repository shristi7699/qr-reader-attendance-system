from app import create_app, db
from app.models.user import User
from app.models.attendance import Attendance
import os
import shutil

def clear_all_data():
    app = create_app()
    with app.app_context():
        print("Clearing all data...")
        
        # Delete all attendance records
        Attendance.query.delete()
        print("✓ Deleted all attendance records")
        
        # Delete all users
        User.query.delete()
        print("✓ Deleted all users")
        
        # Commit the changes
        db.session.commit()
        print("✓ Committed changes to database")
        
        # Delete QR code images
        qr_dir = os.path.join('app', 'static', 'qrcodes')
        if os.path.exists(qr_dir):
            shutil.rmtree(qr_dir)
            os.makedirs(qr_dir, exist_ok=True)
            print("✓ Deleted all QR code images")
        
        # Delete report files
        report_files = ['attendance.csv', 'weekly_report.csv']
        for file in report_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"✓ Deleted {file}")
        
        print("\nAll data has been cleared successfully!")
        print("You can now register new users.")

if __name__ == "__main__":
    clear_all_data() 