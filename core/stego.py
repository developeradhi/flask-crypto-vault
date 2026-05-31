import os
from stegano import lsb

def hide_in_image(image_path, text_data, output_path):
    """Hides text data inside a PNG image using LSB steganography."""
    try:
        secret_image = lsb.hide(image_path, text_data)
        secret_image.save(output_path)
        return True, "Data successfully hidden in image."
    except Exception as e:
        return False, str(e)

def extract_from_image(image_path):
    """Extracts hidden text data from a PNG image."""
    try:
        secret = lsb.reveal(image_path)
        if not secret:
            return False, "No hidden data found in this image."
        return True, secret
    except Exception as e:
        return False, f"Failed to extract data. Make sure it's a valid PNG image. Details: {str(e)}"
