import os
from cryptography.fernet import Fernet, InvalidToken

def generate_key():
    """Generates a new AES-256 key for a user."""
    return Fernet.generate_key().decode('utf-8')

def encrypt_file(file_path, key):
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    if file_path.endswith('.enc'):
        return False, f"File already encrypted: {file_path}"
    try:
        f = Fernet(key.encode('utf-8'))
        with open(file_path, "rb") as file:
            file_data = file.read()
        encrypted_data = f.encrypt(file_data)
        new_file_path = file_path + '.enc'
        with open(new_file_path, "wb") as file:
            file.write(encrypted_data)
        return True, f"Successfully encrypted to '{new_file_path}'"
    except Exception as e:
        return False, str(e)

def decrypt_file(file_path, key):
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    if not file_path.endswith('.enc'):
        return False, f"File does not end with .enc: {file_path}"
    try:
        f = Fernet(key.encode('utf-8'))
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        new_file_path = file_path[:-4]
        with open(new_file_path, "wb") as file:
            file.write(decrypted_data)
        return True, f"Successfully decrypted to '{new_file_path}'"
    except InvalidToken:
        return False, "Invalid token: Incorrect key or corrupted file."
    except Exception as e:
        return False, str(e)

def encrypt_text(text, key):
    try:
        f = Fernet(key.encode('utf-8'))
        return True, f.encrypt(text.encode('utf-8')).decode('utf-8')
    except Exception as e:
        return False, str(e)

def decrypt_text(encrypted_text, key):
    try:
        f = Fernet(key.encode('utf-8'))
        return True, f.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    except InvalidToken:
        return False, "Invalid token or incorrect key."
    except Exception as e:
        return False, str(e)
