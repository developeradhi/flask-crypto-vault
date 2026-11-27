"""
Cryptography Unit Tests.
Asserts correctness of key derivation, password hashing, encryption integrity, and failure cases.
"""
import unittest
import os
import shutil
from pathlib import Path
from security.encryptor import SecureEncryptor

class TestSecureEncryptor(unittest.TestCase):
    def setUp(self):
        # Create a workspace directory for test files
        self.test_dir = Path(__file__).resolve().parent / "temp_workspace"
        self.test_dir.mkdir(exist_ok=True)
        
        self.plain_file = self.test_dir / "plain.txt"
        self.enc_file = self.test_dir / "plain.txt.enc"
        self.dec_file = self.test_dir / "plain_decrypted.txt"
        
        # Write dummy data
        self.secret_message = b"This is a high-security cryptographic testing sequence."
        with open(self.plain_file, "wb") as f:
            f.write(self.secret_message)
            
        self.test_pwd = "SuperSecretMasterPassword123"

    def tearDown(self):
        # Clean up temporary test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_password_hashing(self):
        """Asserts that password hashing produces consistent verification but distinct hashes with salts."""
        hash1, salt1 = SecureEncryptor.hash_password(self.test_pwd)
        hash2, salt2 = SecureEncryptor.hash_password(self.test_pwd)
        
        # Salting must ensure hashes are unique for the same inputs
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(salt1, salt2)
        
        # Verification must succeed with matching passwords
        self.assertTrue(SecureEncryptor.verify_password(self.test_pwd, hash1, salt1))
        self.assertTrue(SecureEncryptor.verify_password(self.test_pwd, hash2, salt2))
        
        # Verification must fail with incorrect passwords
        self.assertFalse(SecureEncryptor.verify_password("WrongPassword!", hash1, salt1))

    def test_file_encryption_decryption(self):
        """Asserts file encryption followed by decryption yields identical byte strings."""
        # 1. Encrypt
        out_path, orig_size, enc_hash, salt_hex = SecureEncryptor.encrypt_file(
            str(self.plain_file),
            self.test_pwd,
            str(self.enc_file)
        )
        
        self.assertTrue(os.path.exists(out_path))
        self.assertEqual(orig_size, len(self.secret_message))
        self.assertNotEqual(enc_hash, "")
        
        # 2. Decrypt
        dec_path, dec_size, dec_hash = SecureEncryptor.decrypt_file(
            str(self.enc_file),
            self.test_pwd,
            str(self.dec_file)
        )
        
        self.assertTrue(os.path.exists(dec_path))
        self.assertEqual(dec_size, orig_size)
        
        # 3. Read & Verify content integrity
        with open(dec_path, "rb") as f:
            decrypted_message = f.read()
            
        self.assertEqual(decrypted_message, self.secret_message)
        self.assertEqual(dec_hash, SecureEncryptor.get_file_sha256(str(self.plain_file)))

    def test_incorrect_password_decryption_failure(self):
        """Asserts decryption using an incorrect password raises ValueError (integrity checks block it)."""
        # Encrypt first
        SecureEncryptor.encrypt_file(
            str(self.plain_file),
            self.test_pwd,
            str(self.enc_file)
        )
        
        # Decrypt with wrong password should raise ValueError due to signature HMAC invalidation
        with self.assertRaises(ValueError):
            SecureEncryptor.decrypt_file(
                str(self.enc_file),
                "IncorrectDecryptionPassword",
                str(self.dec_file)
            )

    def test_corrupted_file_header_rejection(self):
        """Asserts that files missing a valid 16-byte salt header raise exceptions during decryption."""
        corrupt_file = self.test_dir / "corrupt.enc"
        # Write only 10 bytes (too short to contain the 16-byte salt)
        with open(corrupt_file, "wb") as f:
            f.write(b"TooShort!!")
            
        with self.assertRaises(ValueError):
            SecureEncryptor.decrypt_file(
                str(corrupt_file),
                self.test_pwd,
                str(self.dec_file)
            )

if __name__ == "__main__":
    unittest.main()
