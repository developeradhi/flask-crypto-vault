"""
Database Layer Integration Tests.
Validates table creation, constraints, user records, history operations, and audit logs.
"""
import unittest
import os
import sqlite3
from pathlib import Path
from database.manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        # Create a isolated SQLite file for testing
        self.test_db_path = Path(__file__).resolve().parent / "test_secure_vault.db"
        # Ensure clean state
        if self.test_db_path.exists():
            os.remove(self.test_db_path)
            
        self.db = DatabaseManager(db_path=str(self.test_db_path))

    def tearDown(self):
        # Delete test database
        if self.test_db_path.exists():
            os.remove(self.test_db_path)

    def test_database_initialization(self):
        """Asserts tables are initialized with correct column schemas."""
        conn = sqlite3.connect(str(self.test_db_path))
        try:
            cursor = conn.cursor()
            
            # Check tables existence
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            self.assertIn("Users", tables)
            self.assertIn("EncryptionHistory", tables)
            self.assertIn("Logs", tables)
        finally:
            conn.close()

    def test_user_registration_and_retrieval(self):
        """Asserts user inserts successfully and duplicate checks raise exceptions."""
        username = "testing_agent"
        pwd_hash = "f6f8f828a2a8a812838cf02d8"
        salt = "a9bc29d91f28b"
        
        # Register user
        user_id = self.db.register_user(username, pwd_hash, salt)
        self.assertIsNotNone(user_id)
        
        # Double check existence
        self.assertTrue(self.db.user_exists(username))
        
        # Retrieve user and match records
        user = self.db.get_user(username)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], username.lower())
        self.assertEqual(user['password_hash'], pwd_hash)
        self.assertEqual(user['salt'], salt)
        
        # Assert duplicate registrations throw ValueError
        with self.assertRaises(ValueError):
            self.db.register_user(username, pwd_hash, salt)

    def test_history_creation_and_query(self):
        """Asserts encryption history logging links to active user session records."""
        # 1. Create a dummy user session first
        user_id = self.db.register_user("history_user", "hash123", "salt123")
        
        # 2. Add History entries
        self.db.add_history_entry(
            user_id=user_id,
            action_type="ENCRYPT",
            original_filename="secret.docx",
            processed_filename="secret.docx.enc",
            file_size=1024500,
            file_hash="sha256checksumexample"
        )
        
        self.db.add_history_entry(
            user_id=user_id,
            action_type="DECRYPT",
            original_filename="secret.docx.enc",
            processed_filename="secret.docx",
            file_size=1024500,
            file_hash="sha256checksumexample"
        )
        
        # Retrieve history for the user
        history = self.db.get_user_history(user_id)
        self.assertEqual(len(history), 2)
        
        # Most recent entry must be DECRYPT due to sorting timestamps DESC
        self.assertEqual(history[0]['action_type'], "DECRYPT")
        self.assertEqual(history[0]['original_filename'], "secret.docx.enc")
        
        # Assert general history retrieval works
        global_history = self.db.get_all_history()
        self.assertEqual(len(global_history), 2)
        self.assertEqual(global_history[0]['username'], "history_user")

    def test_system_logs(self):
        """Asserts audit logs write to database and filter/purge correctly."""
        self.db.log_event("INFO", "Diagnostic system boot check.", "Diagnostics")
        self.db.log_event("WARNING", "Unrecognized packet signature.", "PacketHandler")
        self.db.log_event("ERROR", "Access control breach blocked.", "Acl")
        
        logs = self.db.get_logs(limit=10)
        self.assertEqual(len(logs), 3)
        
        # Sort is descending
        self.assertEqual(logs[0]['level'], "ERROR")
        self.assertEqual(logs[0]['module'], "Acl")
        
        # Clear log system
        self.db.clear_logs()
        logs_post_clear = self.db.get_logs(limit=10)
        self.assertEqual(len(logs_post_clear), 0)

if __name__ == "__main__":
    unittest.main()
