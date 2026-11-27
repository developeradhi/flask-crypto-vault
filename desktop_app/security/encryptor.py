"""
Security and Cryptography Module.
Provides cryptographic services including key derivation (PBKDF2), file encryption/decryption (Fernet),
password hashing (SHA-256 with salt), and integrity checksums (SHA-256).
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from config.settings import PBKDF2_ITERATIONS, SALT_SIZE_BYTES, KEY_SIZE_BYTES

class SecureEncryptor:
    @staticmethod
    def generate_random_salt(size=SALT_SIZE_BYTES):
        """Generates cryptographically secure random bytes for salting."""
        return os.urandom(size)

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hashes a password with SHA-256 and a random salt.
        Returns a tuple of (hex_password_hash, hex_salt).
        """
        if not salt:
            # Generate a random 16-byte salt as hex
            salt_bytes = SecureEncryptor.generate_random_salt(SALT_SIZE_BYTES)
            salt = salt_bytes.hex()
        else:
            salt_bytes = bytes.fromhex(salt)

        # Concatenate salt and password and compute SHA-256
        hasher = hashlib.sha256()
        hasher.update(salt_bytes)
        hasher.update(password.encode('utf-8'))
        password_hash = hasher.hexdigest()

        return password_hash, salt

    @staticmethod
    def verify_password(password, stored_hash, salt):
        """
        Validates if the provided password matches the stored SHA-256 salted hash.
        """
        computed_hash, _ = SecureEncryptor.hash_password(password, salt)
        return computed_hash == stored_hash

    @staticmethod
    def derive_key(password, salt_bytes):
        """
        Derives a 32-byte key compliant with Fernet specifications from a password.
        Uses PBKDF2 with SHA-256 and 100,000 iterations.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE_BYTES,
            salt=salt_bytes,
            iterations=PBKDF2_ITERATIONS
        )
        derived = kdf.derive(password.encode('utf-8'))
        return base64.urlsafe_b64encode(derived)

    @staticmethod
    def get_file_sha256(file_path):
        """
        Calculates SHA-256 checksum of a file in standard 64KB blocks.
        Ensures low memory consumption for larger files.
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def encrypt_file(input_path, password, output_path=None):
        """
        Encrypts any input file with standard AES key generated via password PBKDF2.
        Saves: [16-byte salt] + [Fernet cipher envelope bytes].
        Returns: (output_path, original_file_size, output_file_hash, salt_hex)
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Source file not found at: {input_path}")

        # Determine default output path if not specified
        if not output_path:
            output_path = input_path + ".enc"

        # Generate a unique salt for this specific file operation
        salt = SecureEncryptor.generate_random_salt(SALT_SIZE_BYTES)
        
        # Derive the encryption key
        key = SecureEncryptor.derive_key(password, salt)
        fernet = Fernet(key)

        # Read target payload
        with open(input_path, "rb") as f:
            plain_data = f.read()

        original_size = len(plain_data)
        encrypted_data = fernet.encrypt(plain_data)

        # Write out derived salt followed by actual encrypted payload
        with open(output_path, "wb") as f:
            f.write(salt)
            f.write(encrypted_data)

        # Calculate final file hash of the *encrypted* output file
        encrypted_hash = SecureEncryptor.get_file_sha256(output_path)

        return output_path, original_size, encrypted_hash, salt.hex()

    @staticmethod
    def decrypt_file(encrypted_path, password, output_path=None):
        """
        Decrypts an encrypted file using the correct password.
        Reads salt from first 16 bytes, derives key, and decrypts.
        Returns: (output_path, decrypted_file_size, decrypted_file_hash)
        """
        if not os.path.exists(encrypted_path):
            raise FileNotFoundError(f"Encrypted file not found at: {encrypted_path}")

        # If no output path is given, strip the .enc suffix or append .dec
        if not output_path:
            if encrypted_path.endswith(".enc"):
                output_path = encrypted_path[:-4]
            else:
                output_path = encrypted_path + ".dec"

        # Read salt and payload
        with open(encrypted_path, "rb") as f:
            salt = f.read(SALT_SIZE_BYTES)
            encrypted_payload = f.read()

        if len(salt) < SALT_SIZE_BYTES:
            raise ValueError("Corrupt file: Encrypted file header is missing salt information.")

        # Derive key using extracted salt
        key = SecureEncryptor.derive_key(password, salt)
        fernet = Fernet(key)

        try:
            decrypted_data = fernet.decrypt(encrypted_payload)
        except InvalidToken as e:
            raise ValueError("Authentication error: Wrong decryption password or corrupted file.") from e

        # Write decrypted result
        with open(output_path, "wb") as f:
            f.write(decrypted_data)

        decrypted_size = len(decrypted_data)
        decrypted_hash = SecureEncryptor.get_file_sha256(output_path)

        return output_path, decrypted_size, decrypted_hash
