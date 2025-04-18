from app import create_app
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['PYTHONUNBUFFERED'] = '1'

logger.info("Starting application initialization...")
app = create_app()
logger.info("Application initialized successfully")

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    print("Starting Flask application...")
    print("Server will be available at http://127.0.0.1:8000")
    print("Test the server at http://127.0.0.1:8000/test")
    app.run(port=8000, debug=True) 