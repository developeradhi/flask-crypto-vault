import hmac
import hashlib
import os

def generate_file_hmac(file_path, secret_key):
    """Generates an HMAC-SHA256 hash for a file using the user's AES key as the secret."""
    try:
        h = hmac.new(secret_key.encode('utf-8'), digestmod=hashlib.sha256)
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return True, h.hexdigest()
    except Exception as e:
        return False, str(e)

def verify_file_hmac(file_path, secret_key, expected_hmac):
    """Verifies that the file's HMAC matches the expected HMAC."""
    success, current_hmac = generate_file_hmac(file_path, secret_key)
    if not success:
        return False, current_hmac
    
    if hmac.compare_digest(current_hmac, expected_hmac):
        return True, "Integrity verified. File has NOT been tampered with."
    else:
        return False, "INTEGRITY COMPROMISED! File has been tampered with!"
