# QR Attendance System

A modern attendance tracking system using QR codes for schools, offices, and organizations. This system allows administrators to scan student QR codes to mark attendance and provides students with access to their attendance records.

![QR Attendance System](https://via.placeholder.com/800x400?text=QR+Attendance+System)

## Features

### Admin Features
- **Admin Portal**: Access to all administrative functions
- **QR Code Scanning**: Scan student QR codes to mark attendance
- **Attendance Reports**: Generate and view attendance reports
- **Statistics Dashboard**: Monitor attendance statistics
- **Student Management**: View and manage student records

### Student Features
- **Student Dashboard**: View personal attendance information
- **QR Code Display**: Access and download personal QR code
- **Attendance History**: View detailed attendance records
- **Attendance Statistics**: Track personal attendance statistics

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **QR Code**: OpenCV, pyzbar for scanning
- **Authentication**: Flask-Login

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/qr-reader-attendance-system.git
   cd qr-reader-attendance-system
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     .\.venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Initialize the database:
   ```
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

6. Create an admin user:
   ```
   python register_admin.py
   ```

## Usage

1. Start the application:
   ```
   python run.py
   ```

2. Access the application:
   - Open your browser and navigate to `http://localhost:8080`
   - Login as admin or student
   - For admin access, use the credentials created during setup

### Admin Workflow
1. Login to the admin portal
2. Use the QR scanner to scan student QR codes
3. View and generate attendance reports
4. Monitor attendance statistics

### Student Workflow
1. Register as a new student or login with existing credentials
2. View your QR code (show this to admin for attendance)
3. Check your attendance history and statistics

## Data Management

### Clearing All Data
To reset the system and delete all users and attendance records:
```
python clear_data.py
```

### Creating Admin Users
To create a new admin user:
```
python register_admin.py
```

## Security Features

- Role-based access control (Admin/Student)
- Password hashing for secure storage
- Protected routes with login requirements
- QR code-based attendance verification

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask web framework
- Bootstrap for UI components
- OpenCV and pyzbar for QR code processing
