import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont
import os
import json
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_qr_code(username, output_path, size=400, student_name=None):
    """
    Generate a QR code for a student with their username and additional information.
    
    Args:
        username (str): The student's username to encode in the QR code
        output_path (str): Path where the QR code image should be saved
        size (int): Size of the QR code image (default: 400)
        student_name (str): The student's full name (optional)
    """
    try:
        logger.info(f"Starting QR code generation for user: {username}")
        
        # Create QR code instance with high error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # Add the data with timestamp for additional security
        data = {
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'name': student_name
        }
        
        # Convert data to JSON string for better QR code compatibility
        json_data = json.dumps(data)
        logger.debug(f"QR code data: {json_data}")
        
        qr.add_data(json_data)
        qr.make(fit=True)
        
        # Create an image with white background
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Resize the QR code
        qr_image = qr_image.resize((size, size))
        
        # Create a new image with padding for text
        padding = 80  # Increased padding for more text
        final_size = (size, size + padding)
        final_image = Image.new('RGB', final_size, 'white')
        
        # Add a light gray background for the text area
        draw = ImageDraw.Draw(final_image)
        draw.rectangle([(0, size), (size, size + padding)], fill='#f8f9fa')
        
        # Paste the QR code
        final_image.paste(qr_image, (0, 0))
        
        # Try to use a nice font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            subtitle_font = ImageFont.truetype("arial.ttf", 16)
        except Exception as e:
            logger.warning(f"Could not load Arial font, using default. Error: {str(e)}")
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Add student name if provided
        if student_name:
            name_text = f"Name: {student_name}"
            name_bbox = draw.textbbox((0, 0), name_text, font=title_font)
            name_width = name_bbox[2] - name_bbox[0]
            name_position = ((size - name_width) // 2, size + 10)
            draw.text(name_position, name_text, fill="black", font=title_font)
        
        # Add username
        username_text = f"ID: {username}"
        username_bbox = draw.textbbox((0, 0), username_text, font=subtitle_font)
        username_width = username_bbox[2] - username_bbox[0]
        username_position = ((size - username_width) // 2, size + 40)
        draw.text(username_position, username_text, fill="#666666", font=subtitle_font)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the final image with high quality
        final_image.save(output_path, 'PNG', quality=95)
        logger.info(f"QR code successfully generated and saved to: {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating QR code for user {username}: {str(e)}")
        raise 