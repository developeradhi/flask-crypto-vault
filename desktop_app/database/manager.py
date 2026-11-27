"""
Database Manager Module.
Handles SQLite operations, schema initialization, credentials management, history records, and system logs.
"""
import sqlite3
import os
import datetime
import contextlib
from pathlib import Path
from config.settings import DB_PATH

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        # Ensure target folder exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()

    @contextlib.contextmanager
    def _get_connection(self):
        """Returns a connection context manager to ensure safe closing."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables named access to columns
        try:
            yield conn
        finally:
            conn.close()

    def initialize_database(self):
        """Creates table schemas if they do not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # EncryptionHistory Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS EncryptionHistory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT CHECK(action_type IN ('ENCRYPT', 'DECRYPT')) NOT NULL,
                original_filename TEXT NOT NULL,
                processed_filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE SET NULL
            )
            """)
            
            # System Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT CHECK(level IN ('INFO', 'WARNING', 'ERROR')) NOT NULL,
                message TEXT NOT NULL,
                module TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            conn.commit()

    # ==========================================
    # USER OPERATIONS
    # ==========================================

    def register_user(self, username, password_hash, salt):
        """
        Registers a new local system user.
        Returns user ID on success, or raises sqlite3.IntegrityError if username exists.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username.lower().strip(), password_hash, salt)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            self.log_event("WARNING", f"Registration failed: User '{username}' already exists", "DatabaseManager")
            raise ValueError(f"User '{username}' is already registered.") from e
        except Exception as e:
            self.log_event("ERROR", f"Registration database error: {str(e)}", "DatabaseManager")
            raise

    def get_user(self, username):
        """
        Retrieves user credentials hash and salt details by username.
        Returns a dict/sqlite3.Row if found, otherwise None.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, salt, created_at FROM Users WHERE username = ?",
                (username.lower().strip(),)
            )
            return cursor.fetchone()

    def user_exists(self, username):
        """Quick check if a username exists."""
        return self.get_user(username) is not None

    # ==========================================
    # HISTORY OPERATIONS
    # ==========================================

    def add_history_entry(self, user_id, action_type, original_filename, processed_filename, file_size, file_hash):
        """Adds an entry tracking an encryption or decryption operation."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO EncryptionHistory 
                    (user_id, action_type, original_filename, processed_filename, file_size, file_hash) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, action_type, original_filename, processed_filename, file_size, file_hash)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.log_event("ERROR", f"Failed to record operation history: {str(e)}", "DatabaseManager")
            return None

    def get_user_history(self, user_id):
        """Returns all history items for a specific user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, action_type, original_filename, processed_filename, file_size, file_hash, timestamp "
                "FROM EncryptionHistory WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_all_history(self):
        """Retrieves global history linked with usernames."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT h.id, u.username, h.action_type, h.original_filename, h.processed_filename, "
                "h.file_size, h.file_hash, h.timestamp "
                "FROM EncryptionHistory h "
                "LEFT JOIN Users u ON h.user_id = u.id "
                "ORDER BY h.id DESC"
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==========================================
    # LOG OPERATIONS
    # ==========================================

    def log_event(self, level, message, module):
        """Saves a structured system audit log event in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Logs (level, message, module) VALUES (?, ?, ?)",
                    (level, message, module)
                )
                conn.commit()
        except Exception as e:
            # Fallback output in case SQLite logger is locked
            print(f"[Fallback DB Logger Error - {level}] [{module}] {message}. Error: {str(e)}")

    def get_logs(self, limit=100):
        """Retrieves system logs sorted by recent time."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, level, message, module, timestamp FROM Logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear_logs(self):
        """Purges all log entries in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Logs")
            conn.commit()
