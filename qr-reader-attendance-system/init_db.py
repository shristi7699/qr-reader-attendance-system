from app import create_app, db
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['QR_CODE_FOLDER'], exist_ok=True)
        
        print("Database initialized successfully!")
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"QR code folder: {app.config['QR_CODE_FOLDER']}")

if __name__ == '__main__':
    init_db() 